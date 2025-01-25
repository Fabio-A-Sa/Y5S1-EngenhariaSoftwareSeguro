from flask import Flask, logging
from secure_endpoints import SecureEndpoints, SecureRequests

from web_server import env

app = Flask(__name__, instance_path=env.INSTANCE_DIR)
app.secret_key = "qualquercoisa19189"

logger = logging.create_logger(app)

secure_endpoints = SecureEndpoints(
    app,
    bypass=env.DEVELOPMENT,
)

secure_requests = SecureRequests(
    f"{env.DATA_DIR}/communications_ca/certificate.pem",
    f"{env.DATA_DIR}/own_dns_certificate/certificate.pem",
    f"{env.DATA_DIR}/own_dns_certificate/key.pem",
    bypass=env.DEVELOPMENT,
)

import web_server.routes
