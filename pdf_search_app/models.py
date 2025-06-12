from flask_sqlalchemy import SQLAlchemy

# This db object is what your app and routes will share
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
    preview = db.Column(db.Text, nullable=True)

