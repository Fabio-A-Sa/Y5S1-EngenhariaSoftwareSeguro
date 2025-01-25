from typing import cast
import ssl

from gunicorn.workers.sync import SyncWorker
from gunicorn.sock import TCPSocket
from gunicorn.http.message import Request

PCTRTT = tuple[tuple[str, str], ...]
PCTRTTT = tuple[PCTRTT, ...]

COMMON_NAME_HEADER = "X-CERTIFICATE-COMMON-NAME"

class ClientCertificateSyncWorker(SyncWorker):
    def handle_request(self, listener: TCPSocket, req: Request, client: ssl.SSLSocket, addr: tuple):
        headers = dict(req.headers)
        
        # Ensure that clients connecting without a certificate can't bypass the authentication
        # by sending the common name in the request headers
        if COMMON_NAME_HEADER in headers:
            del headers[COMMON_NAME_HEADER]

        cert = client.getpeercert()
        
        if cert is not None:
            pctrttt_subject = cast(PCTRTTT, cert.get("subject"))
            subjects = [dict(record) for record in zip(*pctrttt_subject)]
            
            if len(subjects) > 0:
                subject = subjects[0]
                
                common_name = subject.get("commonName", None)
                if common_name is not None:
                    
                    headers = dict(req.headers)
                    headers[COMMON_NAME_HEADER] = common_name
                    
        req.headers = list(headers.items())
        super().handle_request(listener, req, client, addr)
