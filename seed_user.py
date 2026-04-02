from app import create_app, db, bcrypt
from app.models.user import User

app = create_app()

with app.app_context():
    email = "sagnikruproy11@gmail.com"
    username = "sagnik_master"
    password = "MasterUser" # Updated per user request
    
    # Check if user already exists
    existing = User.query.filter_by(email=email).first()
    
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if existing:
        print(f"User {email} already exists. Updating password to: {password}")
        existing.password_hash = hashed_pw
        db.session.commit()
        print(f"User {email} updated successfully!")
    else:
        print(f"Creating new user {email}...")
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            is_premium=True # Setting as master user / premium
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"User {email} created successfully with password: {password}")
