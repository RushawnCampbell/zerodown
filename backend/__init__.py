from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session

#from flask_cors import CORS
from .config import Config
from flask_compress import Compress

app = Flask(__name__, static_folder='../dist/assets')

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

from backend import zeroapi