from datetime import datetime
from app.extensions import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default="My Resume")
    data = db.Column(db.Text, nullable=False) # Store resume JSON data
    template_id = db.Column(db.String(50), nullable=False, default="template1")
    used_ai = db.Column(db.Boolean, default=False)
    file_path = db.Column(db.String(255), nullable=True) # Path if physical file generated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Resume {self.title} (User ID: {self.user_id})>'
