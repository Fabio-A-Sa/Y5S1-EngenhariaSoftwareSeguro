from typing import cast, List

from flask import request, jsonify, redirect, url_for, render_template, session, abort, make_response
import jwt
import requests

from web_server import app, env, middleware, secure_endpoints, secure_requests, logger

# Add admin routes
import web_server.routes.admin

TIMEOUT = 5


def request_get(url: str):
    with secure_requests.new_secure_session() as r:
        return r.get(url, timeout=TIMEOUT)
    
def request_resource(resource: str, token: str):
    with secure_requests.new_secure_session() as r:
        return r.get(f"{env.RESOURCE_SERVER_URL}/resources/{resource}", headers={"X-Authorization-Token": token}, timeout=TIMEOUT)

def request_post(url: str, json):
    with secure_requests.new_secure_session() as r:
        return r.post(url, json=json, timeout=TIMEOUT)        

def request_resources():
    return request_get(f"{env.RESOURCE_SERVER_URL}/resources")


@app.get("/")
def index():
    resources = cast(List[str], request_resources().json())
    return render_template("index.html", resources=resources)


@app.get("/resources/<path:resource>")
@middleware.require_authorization_certificate(app)
def download_resource(resource: str):
    
    certificate = request.args.get("certificate")

    url_validate = f"{env.AUTHORIZATION_SERVER_URL}/authorize"

    response = request_post(url_validate, json={"user_cert": certificate})

    if response.status_code == 200:
        autz_token_encoded = response.json().get("token")
        session['user'] = response.json().get("username")

        token_res = request_resource(resource, autz_token_encoded)
        logger.info(f"token RES: {token_res.status_code}")
        if token_res.status_code == 200:
            logger.error(f"token RES: {token_res.headers}")

            return make_response(token_res.content, token_res.status_code, token_res.headers)
            # token = token_res.json()
        else:
            logger.error(f"token RES: {token_res.status_code}")
            return abort(403)
    
    if response.status_code == 403:
        return f"Message: {response.json().get("error")}"
        
    logger.error("status code %d", response.status_code)
    return abort(500)


# @app.route("/resources")
# def list_resources():

#     url = f"{env.AUTHORIZATION_SERVER_URL}/api/resources"
#     response = request_resources_get(url)

#     if response.status_code == 200:
#         resources = response.json()
#         return render_template("view-resources.html", resources=resources)
#     else:
#         return "Error fetching resources", response.status_code


# @app.route("/admin/add-operation", methods=["GET", "POST"])
# def add_operation():

#     if session["user"] == "admin":
#         if request.method == "POST":
#             operation = request.form.get("operation")
#             url = f"{env.AUTHORIZATION_SERVER_URL}/api/operations"
#             response = requests.post(url, json={"operation": operation})

#             if response.status_code == 201:
#                 return redirect(url_for("index"))

#             return "Error adding operation", response.status_code

#         else:
#             return render_template("add-operation.html")

#     return "Access to this page not allowed"

