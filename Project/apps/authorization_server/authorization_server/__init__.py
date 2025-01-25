from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from authorization_server import env, models

app = Flask(__name__, instance_path=env.INSTANCE_DIR)
app.secret_key = "1234"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///authorization.db"

db = SQLAlchemy(app, model_class=models.Base)

with app.app_context():
    db.create_all()
    models.initialize_database(db)


logger = logging.create_logger(app)

import authorization_server.routes
