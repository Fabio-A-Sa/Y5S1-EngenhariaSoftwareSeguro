from typing import Any
from cryptography.fernet import Fernet
from json import dumps, loads
from pydantic import BaseModel

from utils import base64
from utils.pydantic import model_cast

from authorization_server import logger

class Token(BaseModel):
    role_name: str
    
    def to_json(self):
        return self.model_dump()
    
    @classmethod
    def from_json(cls, json: Any):
        return model_cast(cls, json)

def create_token(role_name: str, key: str):
    fernet = Fernet(key)

    token = Token(role_name=role_name)
    serialized_token = base64.to_base64(dumps(token.to_json()))
    encrypted_token = base64.to_base64_as_str(fernet.encrypt(serialized_token))

    return encrypted_token


def read_token(encrypted_token: str, key: str):
    
    fernet = Fernet(key)
    
    logger.debug(f"Encrypted token: {encrypted_token}")

    serialized_token = fernet.decrypt(base64.from_base64(encrypted_token))
    logger.debug(f"Serialized token: {serialized_token}")
    token = Token.from_json(loads(base64.from_base64_as_str(serialized_token)))
    logger.debug(f"Token: {token}")
    return token
