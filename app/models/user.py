from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # id = db.Column(db.Integer, primary_key=True)  # Removed in favor of email PK
    email = db.Column(db.String(120), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship to user's resumes
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def id(self):
        """Map id attribute to email for compatibility with Flask-Login and existing code."""
        return self.email

    def get_id(self):
        return str(self.email)

    def __repr__(self):
        return f'<User {self.email}>'

from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    # user_id is now the email string
    return User.query.get(user_id)
