from typing import Literal
from pydantic import BaseModel, ValidationError as _ValidationError

ValidationError = _ValidationError

class CreateUserPayload(BaseModel):
    username: str
    role_id: int

class ValidateTokenPayload(BaseModel):
    method: Literal["GET", "PUT", "DELETE"]
    resource: str
    token: str