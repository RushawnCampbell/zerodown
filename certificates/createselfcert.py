import os
import datetime
import ipaddress
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

def create_self_signed_certificate(
    certificate_path, private_key_path, ip_address_str, common_name="My Server", days=365
):
    """Creates a self-signed certificate.
    Args:
        certificate_path: Path to save the certificate (.crt or .pem).
        private_key_path: Path to save the private key (.key or .pem).
        ip_address_str: The IP address as a string (e.g., "127.0.0.1").
        common_name: The Common Name (CN) for the certificate.
        days: Validity period of the certificate in days.
    """

    try:
        ip_address = ipaddress.ip_address(ip_address_str)  # Convert string to ipaddress object
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip_address_str}")

    # Generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )

    # Create the certificate builder
    builder = x509.CertificateBuilder()

    # Set the subject (who the certificate is for)
    builder = builder.subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
    )

    # Set the issuer (who issued the certificate - in this case, ourselves)
    builder = builder.issuer_name(
        x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
    )

    # Set the validity period
    not_valid_before = datetime.datetime.utcnow()
    not_valid_after = not_valid_before + datetime.timedelta(days=days)
    builder = builder.not_valid_before(not_valid_before).not_valid_after(not_valid_after)

    # Set the serial number
    builder = builder.serial_number(x509.random_serial_number())

    # Set the public key
    builder = builder.public_key(private_key.public_key())

    # Add the Subject Alternative Name (SAN) for the IP address
    builder = builder.add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ip_address),  # Use the ipaddress object here
        ]),
        critical=False,  # Not critical because older clients might not support it
    )

    # Self-sign the certificate
    certificate = builder.sign(
        private_key, hashes.SHA256()
    )

    # Write the private key to a file
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # Or use a password: serialization.BestAvailableEncryption(b"your_password")
        ))

    # Write the certificate to a file
    with open(certificate_path, "wb") as f:
        f.write(certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        ))

    print(f"Certificate saved to: {certificate_path}")
    print(f"Private key saved to: {private_key_path}")


# Example usage:
certificate_path = "zerodown.crt"  # or server.pem
private_key_path = "zerodown.key"  # or server.pem
ip_address_str = "209.51.183.162"  # Replace with your server's IP as a string!
create_self_signed_certificate(certificate_path, private_key_path, ip_address_str)




"""import ssl
import hashlib

def connect_to_server(hostname, port, expected_fingerprint):
    context = ssl.create_default_context()

    try:
        with ssl.create_connection((hostname, port), context=context) as sock:
            server_cert = sock.getpeercert(binary_form=True)
            fingerprint = hashlib.sha256(server_cert).hexdigest()

            if fingerprint != expected_fingerprint:
                raise Exception("Certificate fingerprint mismatch!")

            # ... proceed with communication ...

    except Exception as e:
        print(f"Connection error: {e}")

# Example usage (replace with your values):
hostname = "your_server_ip"
port = 443
expected_fingerprint = "the_sha256_fingerprint_of_your_certificate"  # Get this using openssl or similar

connect_to_server(hostname, port, expected_fingerprint)



# Assuming the client certificate is in a file named client.crt (or you can pipe it)
openssl x509 -in client.crt -noout -fingerprint -sha256

# Or, if your server is an HTTPS server and you want to get the fingerprint during a connection (more complex)
# This requires some scripting or programming to intercept the client certificate during the TLS handshake.
# The exact method depends on your server software (e.g., Apache, Nginx).

# Example (Conceptual using Python's ssl library - server-side):
import ssl
import hashlib

def handle_client_connection(client_socket):
    # ... (Your code to establish the TLS connection) ...
    client_cert = client_socket.getpeercert(binary_form=True) # Get the client certificate
    fingerprint = hashlib.sha256(client_cert).hexdigest()
    print(f"Client Certificate Fingerprint: {fingerprint}")
    # ... (Rest of your server logic) ...



    import ssl
import hashlib

def get_client_cert_fingerprint(conn): # conn is the SSL connection object
    #Gets the SHA-256 fingerprint of the client certificate.
    try:
        client_cert = conn.getpeercert(binary_form=True) # Get the client cert in binary format
        fingerprint = hashlib.sha256(client_cert).hexdigest()
        return fingerprint
    except AttributeError: # Happens when client doesn't provide a cert
      return None

# ... In your server code where you handle the SSL connection ...
conn = ssl.wrap_socket(...)  # Your SSL socket creation
fingerprint = get_client_cert_fingerprint(conn)
if fingerprint:
  print(f"Client certificate fingerprint: {fingerprint}")
else:
  print("No client certificate provided")



"""