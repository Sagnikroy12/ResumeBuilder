from app import create_app, db, bcrypt
from app.models.user import User

app = create_app()

with app.app_context():
    email = "sagnikruproy11@gmail.com"
    username = "sagnik_master"
    password = "password123" # Temporary password
    
    # Check if user already exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"User {email} already exists.")
    else:
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            is_premium=True # Setting as master user / premium
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"User {email} recreated successfully with temporary password: {password}")
