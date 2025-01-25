import abc
from typing import Literal, Union, cast
from logging import Logger
import requests

from resource_server import secure_requests

ResourceOperation = Literal["PUT", "GET", "DELETE"]


def as_resource_operation(method: str) -> Union[ResourceOperation, None]:
    return (
        cast(ResourceOperation, method) if method in ["PUT", "GET", "DELETE"] else None
    )


class TokenValidator:
    @abc.abstractmethod
    async def validate(
        self, method: ResourceOperation, resource: str, token: str
    ) -> bool:
        pass


class AlwaysValidTokenValidator(TokenValidator):
    async def validate(
        self, method: ResourceOperation, resource: str, token: str
    ) -> bool:
        return True


class AuthorizationServerValidator(TokenValidator):
    def __init__(self, logger: Logger, authorization_server_url: str) -> None:
        super().__init__()
        self.logger = logger
        self.authorization_server_url = authorization_server_url

    async def validate(self, method: ResourceOperation, resource: str, token: str):
        with secure_requests.new_secure_session() as r:
            res = r.post(
                f"{self.authorization_server_url}/tokens/validate",
                json={"method": method, "resource": resource, "token": token},
                timeout=10,
            )
            
            if res.status_code == 200:
                return True
            elif res.status_code == 403:
                return False
            else:
                self.logger.error("Authorization server returned an unexpected response")
                self.logger.error({"method": method, "resource": resource, "token": token})
                return False
