from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from authorization_server import app, db, models

admin = Admin(app, "Authorization Server")

admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Role, db.session))
admin.add_view(ModelView(models.Operation, db.session))
