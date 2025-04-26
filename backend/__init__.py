from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session

from .config import Config
from flask_compress import Compress
from flask_caching import Cache
from flask_apscheduler import APScheduler

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT':3600})
cache.init_app(app)
app.config.from_object(Config)

app.config['SESSION_TYPE'] = 'sqlalchemy'
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
app.config['SESSION_SQLALCHEMY'] = db
sess= Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

Compress(app)

from flask_migrate import Migrate
migrate =  Migrate(app,db)
from .Sqlmodels import Endpoint, ESNPair, StorageNode, BackupJob, ScheduledJob, Schedule, User
from . import Zeroapi