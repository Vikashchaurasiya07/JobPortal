from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    role = db.Column(db.String(20), nullable=False)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50))
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    employer = db.relationship('User', backref='jobs')


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', ondelete='CASCADE'), nullable=False)  # Added ondelete='CASCADE'
    name = db.Column(db.String(80), nullable=False)  # Name of the applicant
    email = db.Column(db.String(120), nullable=False)  # Email of the applicant
    phone = db.Column(db.String(20))
    cover_letter = db.Column(db.Text, nullable=False)
    resume_link = db.Column(db.String(255), nullable=True)  # Store Google Drive link
    status = db.Column(db.String(50), default='Pending')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    job = db.relationship('Job', backref='applications', cascade="all, delete")  # Ensures deletion of related applications

