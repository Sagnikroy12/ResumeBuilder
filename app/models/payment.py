from app.extensions import db
from datetime import datetime
import pytz

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    razorpay_order_id = db.Column(db.String(255), unique=True, nullable=False)
    razorpay_payment_id = db.Column(db.String(255), unique=True, nullable=True)
    amount = db.Column(db.Integer, nullable=False)  # Amount in paisa
    currency = db.Column(db.String(3), default='INR', nullable=False)
    status = db.Column(db.String(20), default='created', nullable=False)  # created, paid, failed
    payment_type = db.Column(db.String(20), nullable=False)  # 'single_download' or 'premium_subscription'
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)  # For single downloads
    premium_expiry = db.Column(db.DateTime, nullable=True)  # For premium subscriptions
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relationships
    user = db.relationship('User', backref='payments')
    resume = db.relationship('Resume', backref='payments')

    def __repr__(self):
        return f'<Payment {self.razorpay_order_id} - {self.status}>'