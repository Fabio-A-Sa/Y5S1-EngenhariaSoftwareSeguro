import os

from flask import request, abort, send_file
from secure_endpoints import SecureEndpoints
from sqlalchemy import select
from ulid import ULID

from resource_server import env, middleware, app, db, logger
from resource_server.models import File

secure_endpoints = SecureEndpoints(app, bypass=env.DEVELOPMENT)
only_web_server = secure_endpoints.authenticated(["web-server.local"])

token_validator = middleware.validation.AuthorizationServerValidator(
    logger, env.AUTHORIZATION_SERVER_URL
)

# token_validator = middleware.validation.AlwaysValidTokenValidator()

def ensure_files_directory():
    os.makedirs(f"{env.DATA_DIR}/files", exist_ok=True)


@app.route("/")
def index():
    return "Hello World from the resource server!"


@app.get("/resources")
@only_web_server
def get_resources():
    resources = db.session.execute(select(File.resource)).scalars().all()
    return list(resources)


@app.put("/resources/<path:resource>")
@only_web_server
@middleware.authorize_resource_operation(token_validator)
async def put_resource(resource: str):
    uploaded_file = request.files["file"]
    if not uploaded_file:
        abort(400)

    current_file = db.session.execute(
        select(File).where(File.resource == resource)
    ).scalar_one_or_none()

    ulid = ULID()
    new_file_path = f"{env.DATA_DIR}/files/{ulid}"

    old_file_path: str | None = None
    if current_file:
        old_file_path = current_file.file_path
        current_file.file_path = new_file_path
    else:
        current_file = File(resource=resource, file_path=new_file_path)

    db.session.bulk_save_objects([current_file])
    db.session.flush()

    try:
        ensure_files_directory()

        if old_file_path:
            os.remove(old_file_path)

        uploaded_file.save(new_file_path)

        db.session.commit()
    except Exception as err:
        logger.error(
            "An error occured while saving updating the filesystem state",
            extra={"error": err},
            exc_info=True,
        )
        db.session.rollback()

    return {
        "id": current_file.id,
        "resource": current_file.resource,
        "file_path": current_file.file_path,
    }


@app.get("/resources/<path:resource>")
@only_web_server
@middleware.authorize_resource_operation(token_validator)
async def get_resource(resource: str):
    current_file = db.session.execute(
        select(File).where(File.resource == resource)
    ).scalar_one_or_none()

    if not current_file:
        abort(404)

    return send_file(current_file.file_path, download_name="file")


@app.delete("/resources/<path:resource>")
@only_web_server
@middleware.authorize_resource_operation(token_validator)
async def delete_resource(resource: str):
    current_file = db.session.execute(
        select(File).where(File.resource == resource)
    ).scalar_one_or_none()

    try:
        if current_file:
            ensure_files_directory()
            os.remove(current_file.file_path)

            db.session.delete(current_file)
            db.session.commit()

        return None, 204
    except Exception as err:
        logger.error(
            "An error occured while saving updating the filesystem state",
            extra={"error": err},
        )
        db.session.rollback()
