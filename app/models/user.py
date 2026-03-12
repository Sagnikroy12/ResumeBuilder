from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship to user's resumes
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
