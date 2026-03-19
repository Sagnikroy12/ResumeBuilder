from app.extensions import db
from datetime import datetime
import pytz

def get_ist_now():
    """Helper to ensure we track daily limits in IST timezone consistently"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

class Download(db.Model):
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=get_ist_now)

    # Relationships
    user = db.relationship('User', backref=db.backref('downloads', lazy=True))
    resume = db.relationship('Resume', backref=db.backref('downloads', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Download {self.resume_id} by User {self.user_id}>'
