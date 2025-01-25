from flask import request, jsonify
from sqlalchemy import select
import datetime
from cryptography.fernet import Fernet
from authorization_server import app, db, validation
from authorization_server.models import User, Role, Operation
from cert_manager import CertManager
import base64
from json import dumps
from authorization_server import env
from flask_pydantic import validate
from authorization_server.token import read_token, create_token

from authorization_server.logic import can_role_perform_operation

import authorization_server.routes.admin

PRIVATE_KEY = base64.b64decode(env.TOKEN_KEY)

manager = CertManager()
identity_ca_certificate = manager.certificate(f"{env.DATA_DIR}/identity_ca/certificate.pem")


@app.route("/")
def index():
    return "Hello World from the authorization server!"


@app.route("/authorize", methods=['POST'])
def authorize():
    certificate_base64 = request.json.get("user_cert")
    certificate_bytes = base64.b64decode(certificate_base64)
    
    cert = manager.certificate_from_bytes(certificate_bytes)

    if cert.verify_issuer(identity_ca_certificate):
        user_name = cert.get_common_name()
        user = db.session.scalar(select(User).where(User.username == user_name))

        if user:
            
            token = create_token(user.role.name, env.TOKEN_KEY)
            return jsonify({"token": token, "name": user.username}), 200
        
        return jsonify({"error": "User not found"}), 403

    return jsonify({"error": "Certificate  not valid"}), 403


@app.post("/tokens/validate")
@validate()
def check_authorization(body: validation.ValidateTokenPayload):
    token = read_token(body.token, env.TOKEN_KEY)
    if not token:
            return jsonify({'authorized': False, 'error': 'Invalid token'}), 403

    if can_role_perform_operation(token.role_name, body.resource):
        return jsonify({'message': 'Access allowed'}), 200
    
    return jsonify({'error': 'Access not allowed'}), 419


################# Managing Users #########################################


@app.route("/api/users", methods=["GET"])
def get_users():
    users = db.session.scalars(select(User))

    return jsonify(
        [
            {
                "id": user.id,
                "name": user.username,
                "role": user.role.name if user.role else None,
            }
            for user in users
        ]
    )


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.scalar(select(User).where(User.id == user_id))

    return jsonify(
        [
            {
                "id": user.id,
                "name": user.username,
                "role": user.role.name if user.role else None,
            }
        ]
    )


@app.route("/api/users", methods=["POST"])
def add_user():

    try:
        data = validation.CreateUserPayload(**request.json)
    
        role = db.session.query(Role).get(data.role_id)

        new_user = User(username=data.username, role=role)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User created successfully"}), 201
    except validation.ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error adding user: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):

    try:
        user = db.session.query(User).get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error deleting user: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["POST"])
def edit_user(user_id):
    data = request.json

    new_name = data.get("name")
    new_role_id = data.get("role_id")

    if not user_id or not new_name or not new_role_id:
        return jsonify({"error": "Missing required fields"}), 400

    user = db.session.query(User).get(user_id)
    role = db.session.query(Role).get(new_role_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not role:
        return jsonify({"error": "Role not found"}), 404

    user.username = new_name
    user.role = role
    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200


################## Managing Roles #########################################3


@app.route("/api/roles", methods=["POST"])
def add_role():

    try:
        data = request.json
        role = data["role"]

        operation = data["operation"]

        # operations_ids = data["operations_ids"]

        # ops_ids = [int(op_id) for op_id in operations_ids]

        # stmt = select(Operation).where(Operation.id.in_(ops_ids))
        # operations = db.session.execute(stmt).scalars().all()

        new_operation = Operation(name=operation)
        db.session.add(new_operation)

        new_role = Role(name=role)
        db.session.add(new_role)

        new_role.operations.extend(new_operation)
        db.session.commit()

        return jsonify({"message": "Role created successfully"}), 201

    except Exception as e:
        app.logger.error(f"Error adding role: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/roles", methods=["GET"])
def get_roles():

    roles = db.session.scalars(select(Role))

    return jsonify(
        [
            {
                "id": role.id,
                "name": role.name,
                "operations": [
                    {"id": op.id, "name": op.resource} for op in role.operations
                ],
            }
            for role in roles
        ]
    )


@app.route("/api/roles/<int:role_id>", methods=["DELETE"])
def delete_role(role_id):

    try:
        role = db.session.query(Role).get(role_id)

        if not role:
            return jsonify({"error": "Role not found"}), 404

        db.session.delete(role)
        db.session.commit()

        return jsonify({"message": "Role deleted successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error deleting ~role: {e}")
        return jsonify({"error": str(e)}), 500


##################### Managing Operations ####################################


@app.route("/api/operations", methods=["GET"])
def get_operations():

    ops = db.session.scalars(select(Operation))
    return jsonify([{"id": op.id, "name": op.name} for op in ops])


@app.route("/api/operations", methods=["POST"])
def add_operation():

    try:
        data = request.json
        operation = data["operation"]

        if not operation:
            return jsonify({"error": "Operation name is required"}), 400

        new_operation = Operation(name=operation)
        db.session.add(new_operation)
        db.session.commit()

        return jsonify({"message": "Operation created successfully"}), 201

    except Exception as e:
        app.logger.error(f"Error adding operation: {e}")
        return jsonify({"error": str(e)}), 500


################# Managing Resources #######################################


# @app.route("/api/resources", methods=["POST"])
# def add_resources():

#     try:
#         data = request.json
#         name = data["resource"]

#         if not name:
#             return jsonify({"error": "Resource is required"}), 400

#         operations_ids = data["operations_ids"]
#         ops_ids = [int(op_id) for op_id in operations_ids]

#         stmt = select(Operation).where(Operation.id.in_(ops_ids))
#         operations = db.session.execute(stmt).scalars().all()

#         new_resource = Resource(name=name)
#         db.session.add(new_resource)

#         new_resource.operations.extend(operations)
#         db.session.commit()

#         return jsonify({"message": "Resource created successfully"}), 201

#     except Exception as e:
#         app.logger.error(f"Error adding resource: {e}")
#         return jsonify({"error": str(e)}), 500


# @app.route("/api/resources", methods=["GET"])
# def get_resources():

#     resources = db.session.scalars(select(Resource))
#     return jsonify(
#         [
#             {
#                 "id": resource.id,
#                 "name": resource.name,
#                 "operations": [
#                     {"id": op.id, "name": op.name} for op in resource.operations
#                 ],
#             }
#             for resource in resources
#         ]
#     )


# @app.route("/api/resources/<int:resource_id>", methods=["DELETE"])
# def delete_resource(resource_id):

#     try:
#         resource = db.session.query(Resource).get(resource_id)

#         if not resource:
#             return jsonify({"error": "Resource not found"}), 404

#         db.session.delete(resource)
#         db.session.commit()

#         return jsonify({"message": "Resource deleted successfully"}), 200

#     except Exception as e:
#         app.logger.error(f"Error deleting resource: {e}")
#         return jsonify({"error": str(e)}), 500
