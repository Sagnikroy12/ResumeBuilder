from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import razorpay

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

# Initialize Razorpay client
razorpay_client = None

def init_razorpay(app):
    global razorpay_client
    razorpay_client = razorpay.Client(
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET'])
    )
    return razorpay_client

# Set up login views
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
