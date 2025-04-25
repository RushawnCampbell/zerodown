import uuid, threading
from  .. import db
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, DateTime, event
from sqlalchemy.orm import relationship
from Sqlmodels.ScheduledJob import ScheduledJob

class ScheduledJob(db.Model):
    __tablename__ = 'scheduledjob'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), ForeignKey('backupjob.id'),nullable=False)
    frequency = db.Column(db.String(8), nullable=False)
    sch_datetime = Column(DateTime, nullable=False)
    next_sch_datetime = Column(DateTime, default=None, nullable=True)
    sch_day = db.Column(db.String(9), default=None, nullable=True)
    created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
   
    existing_job = relationship("BackupJob", backref="jobid")

    def __init__(self, job_id, frequency, sch_datetime, sch_day=None):
        self.job_id = job_id
        self.frequency = frequency
        self.sch_datetime =  sch_datetime

job_initiation_dict = {}
def Scheduled_Job_Watcher(mapper, connection, target, event_type):
    print(f"Thread started for {event_type} event in table: {mapper.class_.__name__}")
    print(f"Affected record ID: {getattr(target, 'id', target)}")
    sch_job_id = getattr(target, 'id', target)

    if event_type == "insert":
        job_initiation_dict[sch_job_id] = sch_job_id

    if event_type == "delete":
        del job_initiation_dict[sch_job_id]


def sch_job_watcher_in_thread(mapper, connection, target, event_type):
    thread = threading.Thread(target=Scheduled_Job_Watcher, args=(mapper, connection, target, event_type))
    thread.start()

@event.listens_for(ScheduledJob, 'after_insert')
def receive_after_insert(mapper, connection, target):
    sch_job_watcher_in_thread(mapper, connection, target, 'insert')

@event.listens_for(ScheduledJob, 'after_delete')
def receive_after_delete(mapper, connection, target):
    sch_job_watcher_in_thread(mapper, connection, target, 'delete')