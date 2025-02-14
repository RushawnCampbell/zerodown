from  .. import db
from werkzeug.security import generate_password_hash
from datetime import datetime


class User(db.Model):

    __tablename__ = 'user'

    user_id = db.Column(db.Integer(), primary_key=True, autoincrement= True)
    first_name= db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email= db.Column(db.String(255), unique= True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255), unique=True)
    date_joined = db.Column(db.DateTime)
    
    def __init__(self,first_name="/NA",last_name="/NA",email="/NA", username="/NA", password="/NA", date_joined= datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = generate_password_hash(password,method='pbkdf2:sha256')
        self.date_joined = date_joined

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)  # python 3 support
    
    def __repr__(self):
        return '<User %r>' % (self.username)


