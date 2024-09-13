from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import os
import stat
import datetime
from common.paths import cert_dir

# Set up logging
from common.log import get_logger
logger = get_logger(__name__)

def set_file_permissions(file_path):
    if os.name == 'posix':
        # Unix-based systems
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    elif os.name == 'nt':
        # Windows
        os.system(f'icacls "{file_path}" /inheritance:r /grant:r %username%:F')

def check_cert(key_passphrase: str | None = None):
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    cert_path = cert_dir / "cert.pem"
    key_path = cert_dir / "key.pem"
    
    if not cert_path.exists() or not key_path.exists():
        try:
            # Generate key
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"pAI-OS Local Installation"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                # Certificate is valid for 1 year
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost")
                ]),
                critical=False,
            ).sign(key, hashes.SHA256())
            
            # Write key to file with encryption if passphrase is set
            encryption_algorithm = serialization.BestAvailableEncryption(key_passphrase.encode()) if key_passphrase else serialization.NoEncryption()
            with open(key_path, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=encryption_algorithm,
                ))
            
            # Set restrictive permissions on the key file
            set_file_permissions(key_path)
            
            # Write certificate to file
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            logger.info(f"Generated new certificate and key at {cert_dir}")
        except Exception as e:
            logger.error(f"Error generating certificate and key: {e}")
    else:
        logger.info(f"Using existing certificate and key.")

# Example usage
if __name__ == "__main__":
    check_cert()
