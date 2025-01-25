from logging import Logger
import functools

from requests import Session, adapters
from flask import Flask, request, abort, logging

from secure_endpoints.worker import COMMON_NAME_HEADER
from secure_endpoints.adapter import DowngradeHTTPSAdapter, EnforceHTTPSAdapter

class SecureEndpoints:

    def __init__(self, app: Flask, bypass: bool = False):
        self.app = app
        self.bypass = bypass

    def authenticated(self, allowed_common_names: list[str]):
        def decorator(func):
            sync_func = self.app.ensure_sync(func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self.bypass:
                    return sync_func(*args, **kwargs)
                
                common_name = request.headers.get(COMMON_NAME_HEADER, None)
                
                if common_name is None:
                    return abort(401)

                if common_name not in allowed_common_names:
                    return abort(403)

                return sync_func(*args, **kwargs)
            return wrapper
        return decorator

class SecureRequests:
    def __init__(
        self,
        communications_ca_certificate_path: str,
        client_certificate_path: str,
        client_key_path: str,
        bypass: bool = False,
    ):
        self.communications_ca_certificate_path = communications_ca_certificate_path
        self.client_certificate_path = client_certificate_path
        self.client_key_path = client_key_path
        self.bypass = bypass
        
    def new_secure_session(self):
        session = Session()
        self.make_session_secure(session)
        
        return session
        
    def make_session_secure(self, session: Session):
        def create_adapter():
            return EnforceHTTPSAdapter(
                DowngradeHTTPSAdapter(
                    adapters.HTTPAdapter(),
                    active=self.bypass,
                ),
                active=True,
            )
        
        session.mount("https://", create_adapter())
        session.mount("http://", create_adapter())
        
        if not self.bypass:
            session.verify = self.communications_ca_certificate_path
            session.cert = (self.client_certificate_path, self.client_key_path)

        return session
