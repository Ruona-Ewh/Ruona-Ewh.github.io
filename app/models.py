from . import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    confirm_password = db.Column(db.Boolean, default=False)
    short_urls = db.relationship("Url", backref="user", lazy=True)


    def __repr__(self):
        return f"User('{self.email}"
    
class Url(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(), nullable=False)
    short_url = db.Column(db.String(20), unique=True)
    custom_url = db.Column(db.String(20), unique=True, default=None)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'Url: <{self.short_url}>'
    
    

