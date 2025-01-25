import requests
from flask import request, render_template, redirect, url_for, session, logging

from web_server import app, env, secure_endpoints, secure_requests

TIMEOUT=10

def request_get(url):
    with secure_requests.new_secure_session() as r:
        return r.get(url, timeout=TIMEOUT)

def request_post(url, json):
    with secure_requests.new_secure_session() as r:
        return r.post(url, json=json, timeout=TIMEOUT)

def request_delete(url):
    with secure_requests.new_secure_session() as r:
        return r.delete(url, timeout=TIMEOUT)        

# def request_resources():
#     with secure_requests.new_secure_session() as r:
#         return r.get(f"{env.RESOURCE_SERVER_URL}/resources", timeout=TIMEOUT)

# def request_resource_post(url, json):
#     with secure_requests.new_secure_session() as r:
#         return r.post(url, json=json, timeout=TIMEOUT)

# def request_resource_delete(url):
#     with secure_requests.new_secure_session() as r:
#         return r.delete(url, timeout=TIMEOUT)        

# def request_users_get(url):
#     with secure_requests.new_secure_session() as r:
#         return r.get(url, timeout=TIMEOUT)

# def request_users_post(url, json):
#     with secure_requests.new_secure_session() as r:
#         return r.post(url, json=json, timeout=TIMEOUT)

# def request_users_delete(url):
#     with secure_requests.new_secure_session() as r:
#         return r.delete(url, timeout=TIMEOUT)

# def request_roles_get(url):
#     with secure_requests.new_secure_session() as r:
#         return r.get(url, timeout=TIMEOUT)

# def request_roles_post(url, json):
#     with secure_requests.new_secure_session() as r:
#         return r.post(url, json=json, timeout=TIMEOUT)

# def request_roles_delete(url):
#     with secure_requests.new_secure_session() as r:
#         return r.delete(url, timeout=TIMEOUT)

# def request_operations_get(url):
#     with secure_requests.new_secure_session() as r:
#         return r.get(url, timeout=TIMEOUT)

# def request_operation_post(url, json):        
#     with secure_requests.new_secure_session() as r:
#         return r.post(url, json=json, timeout=TIMEOUT)

# @app.get("/")
# def index():
#     resources = cast(List[str], request_resources().json())
#     return render_template("index.html", resources=resources)

@app.route("/admin/add-user", methods=["GET", "POST"])
def add_user():
    # if session["user"] == "admin":
    if request.method == "POST":
        username = request.form.get("username")
        role = request.form.get("role")
        url_users = f"{env.AUTHORIZATION_SERVER_URL}/api/users"
        response = request_post(
            url_users, json={"username": username, "role_id": role}
        )

        if response.status_code == 201:
            return redirect(url_for("list_users"))
        else:
            return response.json()

    url_roles = f"{env.AUTHORIZATION_SERVER_URL}/api/roles"
    response = request_get(url_roles)
    if response.status_code == 200:
        roles = response.json()
        return render_template("add-user.html", roles=roles)
    else:
        return "Error fetching roles", response.status_code

    # return "Acess to this page not allowed"


@app.route("/admin/users")
def list_users():

    # if session["user"] == "admin":
    url_users = f"{env.AUTHORIZATION_SERVER_URL}/api/users"
    response = request_get(url_users)

    if response.status_code == 200:
        users = response.json()
        return render_template("view-users.html", users=users)
    else:
        return "Error fetching users", response.status_code

    # return "Access to this page not allowed"


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    #if session["user"] == "admin":
    try:
        if request.form.get("method") == "DELETE":
            url_user = f"{env.AUTHORIZATION_SERVER_URL}/api/users/{user_id}"

            response = request_delete(url_user)
            if response.status_code == 200:
                return redirect(url_for("list_users"))

            else:
                error_message = response.json().get("error", "Unknown error")
                return (
                    f"Failed to delete user: {error_message}",
                    response.status_code,
                )

        return "Invalid", 400

    except Exception as e:
        app.logger.error(f"Error handling user deletion: {e}")
        return "Internal Server Error", 500

    #return "Access to this page not allowed"


@app.route("/admin/edit-user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if request.method == "POST":

        new_name = request.form["name"]
        new_role_id = request.form["role"]

        url = f"{env.AUTHORIZATION_SERVER_URL}/api/users/{user_id}"

        try:
            response = request_post(
                url, json={"user_id": user_id, "name": new_name, "role_id": new_role_id}
            )
            response_data = response.json()

            if response.status_code == 200:
                return redirect(url_for("list_users"))
            else:
                return f"Error updating user: {response_data.get('error', 'Unknown error')}"

        except requests.RequestException as e:
            return (
                f"Failed to communicate with the authorization server: {str(e)}",
                "danger",
            )

    url_user = f"{env.AUTHORIZATION_SERVER_URL}/api/users/{user_id}"
    url_roles = f"{env.AUTHORIZATION_SERVER_URL}/api/roles"
    user = request_get(url_user)
    roles = request_get(url_roles)

    return render_template("edit-user.html", user=user.json()[0], roles=roles.json())


@app.route("/admin/roles")
def list_roles():

    # if session["user"] == "admin":
    url_roles = f"{env.AUTHORIZATION_SERVER_URL}/api/roles"
    response = request_get(url_roles)

    if response.status_code == 200:
        roles = response.json()
        return render_template("view-roles.html", roles=roles)
    else:
        return "Error fetching users", response.status_code

    # return "Access to this page not allowed"


@app.route("/admin/add-role", methods=["GET", "POST"])
def add_role():

    #if session["user"] == "admin":
    if request.method == "POST":
        url_roles = f"{env.AUTHORIZATION_SERVER_URL}/api/roles"
        role = request.form.get("role")
        operation = request.form.get("operation")

        #operations_ids = [int(op_id) for op_id in operations]
        response = request_post(
            url_roles, json={"role": role, "operation": operation}
        )

        if response.status_code == 201:
            return redirect(url_for("list_users"))

        return "Error adding roles", response.status_code

    else:
        #url_operation = f"{env.AUTHORIZATION_SERVER_URL}/api/operations"
        #response = request_get(url_operation)
        #operations = response.json()
        return render_template("add-role.html")

    #return "Access to this page not allowed"


@app.route("/admin/delete-role/<int:role_id>", methods=["POST"])
def delete_role(role_id):
    if session["user"] == "admin":
        try:
            if request.form.get("method") == "DELETE":
                url = f"{env.AUTHORIZATION_SERVER_URL}/api/roles/{role_id}"

                response = request_delete(url)
                if response.status_code == 200:
                    return redirect(url_for("list_roles"))

                else:
                    error_message = response.json().get("error", "Unknown error")
                    return (
                        f"Failed to delete role: {error_message}",
                        response.status_code,
                    )

            return "Invalid", 400

        except Exception as e:
            admin_blueprint.logger.error(f"Error handling role deletion: {e}")
            return "Internal Server Error", 500

    return "Access to this page not allowed"


@app.route("/admin/add-resource", methods=["GET", "POST"])
def add_resource():

    if request.method == "POST":
        resource = request.form.get("resource")
        operations = request.form.getlist("operation")

        operations_ids = [int(op_id) for op_id in operations]
        url_resources = f"{env.AUTHORIZATION_SERVER_URL}/api/resources"
        response = request_post(
            url_resources, json={"resource": resource, "operations_ids": operations_ids}
        )

        if response.status_code == 201:
            return redirect(url_for("list_resources"))

        return "Error adding resources", response.status_code

    else:
        url_operation = f"{env.AUTHORIZATION_SERVER_URL}/api/operations"
        response = request_get(url_operation)
        operations = response.json()
        return render_template("add-resource.html", operations=operations)


@app.route("/admin/delete-resource/<int:resource_id>", methods=["POST"])
def delete_resource(resource_id):

    if session["user"] == "admin":
        try:
            if request.form.get("method") == "DELETE":
                url = f"{env.AUTHORIZATION_SERVER_URL}/api/resources/{resource_id}"

                response = request_delete(url)
                if response.status_code == 200:
                    return redirect(url_for("list_resources"))

                else:
                    error_message = response.json().get("error", "Unknown error")
                    return (
                        f"Failed to delete resource: {error_message}",
                        response.status_code,
                    )

            return "Invalid", 400

        except Exception as e:
            app.logger.error(f"Error handling resource deletion: {e}")
            return "Internal Server Error", 500

    return "Access to this page not allowed"        
