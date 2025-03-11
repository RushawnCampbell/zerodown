from  .. import db
from datetime import datetime, timezone
import uuid,ipaddress
from .ZeroCryptor import ZeroCryptor

class Endpoint(db.Model):
    __tablename__ = 'endpoint'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255),nullable=False, unique=True)
    ip = db.Column(db.Text,nullable=False) #using text for encrypted ip digest
    username = db.Column(db.String(255),nullable=False)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    #pub_key = db.Column(db.Text)

    def __init__(self, ip, name, username):
        try:
            ipaddress.ip_address(ip)
            zcryptobj= ZeroCryptor()
            self.ip = zcryptobj._encrypt_data(data=ip, type="ENDPOINT")
        except ValueError:
            raise ValueError(f"Invalid IP address")
        self.name = name
        self.username = username
        #self.pub_key = pub_key