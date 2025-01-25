from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import (
    Name, NameAttribute, CertificateBuilder,
    NameOID, random_serial_number, 
    load_pem_x509_certificate, Certificate as X509Certificate
)
from cryptography.hazmat.backends import default_backend
import datetime

COUNTRY_NAME = "PT"
STATE_OR_PROVINCE_NAME = "Porto"
LOCALITY_NAME = "Porto"
ORGANIZATION_NAME = "FEUP"
COMMON_NAME = "ESS"
CA_TIMEOUT = 365
CERT_TIMEOUT = 1

class Certificate:

    def __init__(self, cert: X509Certificate):
        self.cert = cert
    
    def get_common_name(self):
        return self.cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    
    def verify_signature(self, public_key: rsa.RSAPublicKey):
        try:
            public_key.verify(
                self.cert.signature,
                self.cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                self.cert.signature_hash_algorithm or hashes.SHA256(),
            )
            return True
        
        except Exception:
            return False
        
    def verify_issuer(self, issuer: "Certificate"):
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            if not (self.cert.not_valid_before_utc <= now <= self.cert.not_valid_after_utc):
                raise ValueError("Certificate is not valid at the current time")
            
            self.cert.verify_directly_issued_by(issuer.cert)
            
            return True
        except Exception as exception:
            return False
        
    def to_pem(self):
        return self.cert.public_bytes(serialization.Encoding.PEM)

class Key:

    def __init__(self, key: rsa.RSAPrivateKey):
        self.key = key

    def sign(self, data: bytes, hash_algorithm=hashes.SHA256()):
        return self.key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hash_algorithm),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_algorithm
        )

class CA:

    def __init__(self, certificate: Certificate, key: Key):
        self.cert = certificate.cert
        self.key = key.key

    def create_certificate(
        self, subject_name: str, validity: datetime.timedelta
    ):
        user_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        subject = Name([
            NameAttribute(NameOID.COUNTRY_NAME, COUNTRY_NAME),
            NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, STATE_OR_PROVINCE_NAME),
            NameAttribute(NameOID.LOCALITY_NAME, LOCALITY_NAME),
            NameAttribute(NameOID.ORGANIZATION_NAME, ORGANIZATION_NAME),
            NameAttribute(NameOID.COMMON_NAME, subject_name),
        ])
        
        now = datetime.datetime.now(datetime.timezone.utc)

        user_cert = (
            CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.cert.subject)
            .public_key(user_key.public_key())
            .serial_number(random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + validity)
            .sign(self.key, hashes.SHA256(), default_backend())
        )

        return Certificate(user_cert), Key(user_key)
        # with open(output_cert_path, "wb") as cert_file:
        #     cert_file.write(user_cert.public_bytes(serialization.Encoding.PEM))
        #     cert_file.close()

        # with open(output_key_path, "wb") as key_file:
        #     key_file.write(
        #         user_key.private_bytes(
        #             encoding=serialization.Encoding.PEM,
        #             format=serialization.PrivateFormat.TraditionalOpenSSL,
        #             encryption_algorithm=serialization.NoEncryption(),
        #         )
        #     )
        #     key_file.close()

class CertManager:

    def __init__(self):
        pass

    def certificate(self, cert_path: str) -> Certificate:
        with open(cert_path, "rb") as f:
            return self.certificate_from_bytes(f.read())
        
    def certificate_from_bytes(self, cert_data: bytes) -> Certificate:
        return Certificate(load_pem_x509_certificate(cert_data, default_backend()))

    def key(self, key_path: str) -> Key:
        with open(key_path, "rb") as f:
            key = serialization.load_pem_private_key(f.read(), None, default_backend())
            f.close()
            
            if not isinstance(key, rsa.RSAPrivateKey):
                raise ValueError("The key is not an RSA private key")
            
            return Key(key)
    
    def ca(self, cert_path: str, key_path: str) -> CA:
        return CA(self.certificate(cert_path), self.key(key_path))
