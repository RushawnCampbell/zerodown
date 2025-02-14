from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session

from .config import Config
from flask_compress import Compress

app = Flask(__name__)

app.config.from_object(Config)

app.config['SESSION_TYPE'] = 'sqlalchemy'
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
sess= Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

Compress(app)

from flask_migrate import Migrate
migrate =  Migrate(app,db)
from .Sqlmodels import Endpoint, ESNPair, StorageNode, Schedule, User
from . import Zeroapi