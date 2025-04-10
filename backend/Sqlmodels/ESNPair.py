import uuid
from  .. import db
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .ZeroCryptor import ZeroCryptor

class ESNPair(db.Model):
    __tablename__ = 'esnpair'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    storage_node_id = Column(String(36), ForeignKey('storagenode.id'), nullable=False, unique=True)
    endpoint_id = Column(String(36), ForeignKey('endpoint.id'), nullable=False, unique=True)
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    storage_node = relationship("StorageNode", backref="pairings")
    endpoint = relationship("Endpoint", backref="pairings")

    def __init__(self, storage_node_id, endpoint_id):
        self.storage_node_id = storage_node_id
        self.endpoint_id = endpoint_id