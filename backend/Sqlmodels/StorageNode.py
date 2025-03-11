from  .. import db
from datetime import datetime, timezone
import uuid, ipaddress
from .ZeroCryptor import ZeroCryptor

class StorageNode(db.Model):
    __tablename__ = 'storagenode'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    ip = db.Column(db.Text,nullable=False)
    username = db.Column(db.String(255),nullable=False)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pub_key = db.Column(db.Text,nullable=False)

    def __init__(self, ip, name, username, pub_key):
        try:
            ipaddress.ip_address(ip)
            self.ip = ZeroCryptor._encrypt_data(data=ip, type="STORAGE")
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip}")
        self.name = name
        self.username = username
        self.pub_key = ZeroCryptor._encrypt_data(data=pub_key, type="STORAGE")


