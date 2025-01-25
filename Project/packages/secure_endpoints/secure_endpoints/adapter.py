from typing import Mapping
from logging import Logger

from requests import PreparedRequest, Response, adapters

class EnforceHTTPSAdapter(adapters.BaseAdapter):
    def __init__(
        self,
        inner: adapters.BaseAdapter,
        active: bool = False,
    ):
        super().__init__()
        self.inner = inner
        self.active = active
       
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: None | float | tuple[float, float] | tuple[float, None] = None,
        verify: bool | str = True,
        cert: None | bytes | str | tuple[bytes | str, bytes | str] = None,
        proxies: Mapping[str, str] | None = None
    ) -> Response:
        
        if self.active:
            url = request.url
            if url is None or not url.startswith("https://"):
                raise ValueError("Cannot enforce HTTPS on non-HTTPS URL " + str(url))
        

        return self.inner.send(request, stream, timeout, verify, cert, proxies)
    
    def close(self) -> None:
        return self.inner.close()
    
class DowngradeHTTPSAdapter(adapters.HTTPAdapter):
    def __init__(
        self,
        inner: adapters.BaseAdapter,
        active: bool = False,
    ):
        super().__init__()
        self.inner = inner
        self.active = active
        
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: None | float | tuple[float, float] | tuple[float, None] = None,
        verify: bool | str = True,
        cert: None | bytes | str | tuple[bytes | str, bytes | str] = None,
        proxies: Mapping[str, str] | None = None
    ) -> adapters.Response:
        
        if self.active:
            url = request.url
            if url is not None and url.startswith("https://"):
                url = url.replace("https://", "http://", 1)
            
            request.url = url
            
        return self.inner.send(request, stream, timeout, verify, cert, proxies)

    def close(self):
        return self.inner.close()

class LoggingAdapter(adapters.HTTPAdapter):
    def __init__(
        self,
        inner: adapters.BaseAdapter,
        logger: Logger | None = None,
    ):
        super().__init__()
        self.inner = inner
        self.logger = logger
        
    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: None | float | tuple[float, float] | tuple[float, None] = None,
        verify: bool | str = True,
        cert: None | bytes | str | tuple[bytes | str, bytes | str] = None,
        proxies: Mapping[str, str] | None = None
    ) -> adapters.Response:
        
        if self.logger is not None:
            self.logger.debug("LoggingHTTPSAdapter - Sending %s to %s", request.method, request.url)
            
        return self.inner.send(request, stream, timeout, verify, cert, proxies)

    def close(self):
        return self.inner.close()
