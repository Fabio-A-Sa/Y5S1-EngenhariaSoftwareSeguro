from flask import Flask, logging
from secure_endpoints import SecureEndpoints

from authentication_server import env, models

app = Flask(__name__, instance_path=env.INSTANCE_DIR)
app.secret_key = "1234"

secure_endpoints = SecureEndpoints(app, bypass=env.DEVELOPMENT)

logger = logging.create_logger(app)

with app.app_context():
    models.init_db()

import authentication_server.routes
