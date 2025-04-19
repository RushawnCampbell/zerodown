import uuid
from  .. import db
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey,  Text, DateTime
from sqlalchemy.orm import relationship

class BackupJob(db.Model):
    __tablename__ = 'backupjob'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    esnpair = db.Column(db.String(36), ForeignKey('esnpair.id'),nullable=False)
    name = db.Column(db.String(255), nullable=False, unique=True)
    target= db.Column(Text, nullable=True, default='{}')
    destination= db.Column(Text, nullable=True, default='{}')
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_backup =  Column(DateTime, nullable=True)
   
    esn_pair = relationship("ESNPair", backref="esnpairing")

    def __init__(self, esnpair, name, target, destination, id= str(uuid.uuid4())):
        self.id=id
        self.esnpair = esnpair
        self.name = name
        self.target = target
        self.destination = destination