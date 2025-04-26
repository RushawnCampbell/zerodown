import uuid
#import threading, keyring, getpass, requests
from  .. import db
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class ScheduledJob(db.Model):
    __tablename__ = 'scheduledjob'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), ForeignKey('backupjob.id'),nullable=False)
    frequency = db.Column(db.String(8), nullable=False)
    sch_datetime = Column(DateTime, nullable=False)
    next_sch_datetime = Column(DateTime, default=None, nullable=True)
    sch_day = db.Column(db.String(9), default=None, nullable=True)
    created = Column(DateTime, default=lambda: datetime.now())
    
   
    existing_job = relationship("BackupJob", backref="jobid")

    def __init__(self, job_id, frequency, sch_datetime, sch_day=None):
        self.job_id = job_id
        self.frequency = frequency
        self.sch_datetime =  sch_datetime


            
"""def Scheduled_Job_Watcher(mapper, connection, target, event_type):
    sch_job_id = getattr(target, 'id', target)
    if event_type == "insert":
        pass


def sch_job_watcher_in_thread(mapper, connection, target, event_type):
    thread = threading.Thread(target=Scheduled_Job_Watcher, args=(mapper, connection, target, event_type))
    thread.start()

@event.listens_for(ScheduledJob, 'after_insert')
def receive_after_insert(mapper, connection, target):
    sch_job_watcher_in_thread(mapper, connection, target, 'insert')"""


