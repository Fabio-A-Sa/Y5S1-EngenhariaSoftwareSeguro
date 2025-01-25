from typing import Callable
from flask import request, abort

from . import validation


def authorize_resource_operation(validator: validation.TokenValidator):
    def decorator(route: Callable):
        async def wrapper(resource: str, *args, **kwargs):
            method = validation.as_resource_operation(request.method)
            if not method:
                abort(405)

            token = request.headers.get("X-Authorization-Token")
            if not token or not await validator.validate(method, resource, token):
                abort(401)

            return await route(resource=resource, *args, **kwargs)

        wrapper.__name__ = route.__name__
        return wrapper

    return decorator
