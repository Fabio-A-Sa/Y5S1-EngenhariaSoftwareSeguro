from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from secure_endpoints import SecureRequests, SecureEndpoints

from resource_server import env, models

app = Flask(__name__, instance_path=env.INSTANCE_DIR)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///files.db"

db = SQLAlchemy(app, model_class=models.Base)
with app.app_context():
    db.create_all()

logger = logging.create_logger(app)

secure_endpoints = SecureEndpoints(app, bypass=env.DEVELOPMENT)

secure_requests = SecureRequests(
    f"{env.AUTHORIZATION_SERVER_URL}/communications_ca/certificate.pem",
    f"{env.AUTHORIZATION_SERVER_URL}/own_dns_certificate/certificate.pem",
    f"{env.AUTHORIZATION_SERVER_URL}/own_dns_certificate/key.pem",
    bypass=env.DEVELOPMENT,
)

import resource_server.routes
