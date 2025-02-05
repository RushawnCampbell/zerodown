import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env if it exists.

class Config(object):
    """Base Config Object"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY','')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER','')
    SQLALCHEMY_DATABASE_URI = os.environ.get('D_URL', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_RECORD_QUERIES = True