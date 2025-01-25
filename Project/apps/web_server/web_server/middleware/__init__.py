from typing import Callable
from urllib.parse import urlencode
import functools

from flask import request, redirect, abort, Flask

from web_server import env


def require_authorization_certificate(app: Flask):
    """
    Decorator to check if the user has a valid authorization certificate.
    If not, it redirects the user to the authentication server to login.
    """

    def decorator(route: Callable):
        sync_route = app.ensure_sync(route)

        @functools.wraps(route)
        def wrapper(*args, **kwargs):

            cert = request.args.get("certificate")
            if cert is None:
                if request.method == "GET":
                    return redirect(
                        f"{env.PUBLIC_AUTHENTICATION_SERVER_URL}/login?{urlencode({'redirect': request.url})}"
                    )

                return abort(401)
            return sync_route(*args, **kwargs)

        return wrapper

    return decorator
