import smtplib
import random
import sqlite3
import bcrypt
import base64
from typing import cast
from nonce import create_nonce
import requests
from urllib.parse import urlencode
from flask import request, jsonify, render_template, redirect, url_for, session
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import hashlib
from secure_endpoints import SecureEndpoints
from authentication_server import app, env, secure_endpoints, logger
from cert_manager import CertManager


TIMEOUT = 10
WEB_SERVER_URL = "https://web-server.local:8084"

#ESTA CENA É A BIBLIO DO FABIO!!!!
cert_manager = CertManager()
ca = cert_manager.ca(cert_path=f"{env.DATA_DIR}/identity_ca/certificate.pem", key_path=f"{env.DATA_DIR}/identity_ca/key.pem")


# Database setup
DATABASE = f"{env.INSTANCE_DIR}/users.db"
SECRET_KEY = ""
AUTH_SERVER_PUBLIC_KEY = ""
admin_pass = "d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1"


def b64bytes(s: str):
    return base64.b64decode(s)

def b64str(b: bytes):
    return base64.b64encode(b).decode("utf-8")

def create_hash(password: str):
    salt_bytes = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password.encode("utf-8"), salt_bytes)
    return b64str(hash_bytes)

def verify_hash(password: str, hashed_password: str):
    hash_bytes = b64bytes(hashed_password)
    return bcrypt.checkpw(password.encode("utf-8"), hash_bytes)


# SMTP configuration
SMTP_SERVER = "mailpit"  # Change to your SMTP server
SMTP_PORT = 1025
EMAIL_ADDRESS = "test@example.com"  # Replace with your email
EMAIL_PASSWORD = ""  # Replace with your email password


def send_email(to_email, nonce):
    msg = MIMEText(f"Your verification code is: {nonce}")
    msg["Subject"] = "Your Authentication Code"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
            logger.debug("Email sent!")
    except Exception as e:
        logger.error("Error sending email", exc_info=e)


# Route to serve the HTML form for registration
@app.get("/register")
def show_register_form():
    return render_template("register.html")


# Route to handle registration form submissions
@app.post("/register")
def register():
    username = request.form.get("username")
    password = cast(str, request.form.get("password"))
    email = request.form.get("email")
    
    hashed_password = create_hash(password)

    # FIXME: major security flaw
    nonce = create_nonce()
    expiry = datetime.now() + timedelta(minutes=5)

    send_email(email, nonce)


    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, email, verified) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, 0),
            )
            conn.commit()
            
            cursor.execute(
                "INSERT INTO nonces (username, nonce, expiry) VALUES (?, ?, ?)",
                (username, nonce, expiry),
            )
            conn.commit()

            return redirect(url_for("two_factor"))

        except sqlite3.IntegrityError as e:
            logger.error("Integrity error while registering user", exc_info=e)
            return render_template("register_existing_username.html"), 400

@app.get("/2fa")
def two_factor():
    return render_template("2fa.html", title="Verify New User", action="/register_verification")

@app.post('/register_verification')
def verify_reg_nonce():
    username = request.form.get("username")
    nonce = request.form.get("nonce")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nonces.expiry
            FROM nonces 
            WHERE nonces.username = ? AND nonces.nonce = ?""",
            (username, nonce,),
        )
        result = cursor.fetchone()

        if result:
            expiry,  = result
            
            if datetime.now() <= datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S.%f"):
                cursor.execute("DELETE FROM nonces WHERE username = ?", (username,))
                cursor.execute("UPDATE users SET verified = 1 WHERE username = ?", (username,))
                conn.commit()

                return render_template("register_sucessful.html", redirect_uri=request.args.get('redirect_uri', '/')), 200
            else:
                cursor.execute("DELETE FROM nonces WHERE username = ?", (username,))
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                
                return render_template("nonce_expired.html"), 401
        else:
            return render_template("invalid_nonce_or_email.html"), 401

@app.get("/login")
def login_page():
    redirect_uri = request.args.get("redirect", "/")
    session["redirect_uri"] = redirect_uri
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user is not None and password is not None:
            email, stored_password = user

            if not verify_hash(password, stored_password):
                return render_template("login_failed.html"), 401

            nonce = create_nonce()
            expiry = datetime.now() + timedelta(minutes=5)

            cursor.execute(
                "INSERT INTO nonces (username, nonce, expiry) VALUES (?, ?, ?)",
                (username, nonce, expiry),
            )
            conn.commit()

            send_email(email, nonce)  # Send nonce via email
            
            return render_template("nonce_sent.html"), 200
        else:
            return render_template("invalid_email_or_password.html"), 401


@app.route("/verify", methods=["GET"])
def verify_page():
    return render_template("2fa.html", title="Verify Nonce", action="/verify")

@app.route("/verify", methods=["POST"])
def verify_nonce():
    username = request.form.get("username")
    nonce = request.form.get("nonce")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT users.verified, nonces.expiry
            FROM nonces
            JOIN users ON nonces.username = users.username
            WHERE nonces.username = ? AND nonces.nonce = ?""",
            (username, nonce),
        )
        result = cursor.fetchone()

        if result:
            verified, expiry, = result
            if datetime.now() <= datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S.%f") and verified:
                cursor.execute("DELETE FROM nonces WHERE username = ?", (username,))
                conn.commit()

                validity = timedelta(minutes=1)

                # Generate a User Certificate
                cert, _ = ca.create_certificate(
                    subject_name=username,
                    validity=validity,
                )
                
                cert_base64 = b64str(cert.to_pem())
                redirect_uri = session.get("redirect_uri", "/")
                return redirect(f"{redirect_uri}{'&' if '?' in redirect_uri else '?'}{urlencode({'certificate': cert_base64})}")  
            
        return render_template("invalid_email_or_password.html"), 401


@app.route("/admin", methods=["GET"])
def admin_page():
    return render_template("admin_menu.html")


@app.route("/admin", methods=["POST"])
def admin():
    action = request.form.get("action")
    admin_password = request.form.get("admin_password")
    user_name = request.form.get("user_name")

    print(admin_password)
    print(hash_simple(admin_password, 1234))

    if hash_simple(admin_password, 1234) == admin_pass:  # Check for admin password
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if action == "remove_user":
            cursor.execute("DELETE FROM users WHERE username = ?", (user_name,))
            conn.commit()
            conn.close()
            return #admin_remove_suc.html
        elif action == "modify_user":
            return render_template("admin_modify_user_menu.html"), 401
    else:
        return render_template("invalid_admin.html"), 401


@app.route("/admin/modify_user", methods=["POST"])
def modify_user():
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    salt = bcrypt.gensalt()
    hashed_password = hash_simple(password, salt)  # Hash the new password

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET username = ?, password = ?, salt = ?, email = ? WHERE id = ?",
        (username, hashed_password, email, salt, user_id),
    )
    conn.commit()
    conn.close()

    return render_template("modify_user.html")


@app.route("/")
def index():
    return "Hello World from the authentication server!"
