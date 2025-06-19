from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



db = SQLAlchemy()

class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    artist_name = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    keywords = db.Column(db.String, nullable=True)
    status = db.Column(db.String(120))  # Add this line
    affiliation = db.Column(db.String(200), nullable=True) 
    category = db.Column(db.String, default='Uncategorized')
    summary = db.Column(db.Text, nullable=True)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    action = db.Column(db.String(255), nullable=False)        
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=True)
    details = db.Column(db.Text)  # optional: store extra details like filename, fields edited
    user = db.relationship('User', backref='logs')
    contract = db.relationship('Contract', backref='logs')
