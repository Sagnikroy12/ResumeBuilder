from app import create_app, db
from app.models.user import User
from app.models.resume import Resume
import json
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        # 1. Create a user
        test_email = "test_fix@example.com"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            user = User(
                username="test_fix",
                email=test_email,
                password_hash="dummy"
            )
            db.session.add(user)
            db.session.commit()
            print(f"User {test_email} created.")
        
        # 2. Create a resume (this is where it failed)
        resume = Resume(
            user_id=user.email, # Use email string
            title="Test Fix Resume",
            data=json.dumps({"name": "Test"}),
            template_id="template1"
        )
        db.session.add(resume)
        db.session.commit()
        print(f"Resume created successfully for {user.email}!")
        
        # 3. Test the count query (check_daily_limit)
        count = Resume.query.filter(
            Resume.user_id == user.email,
            Resume.created_at >= datetime(2026, 3, 30)
        ).count()
        print(f"Daily generates count for {user.email}: {count}")
        
        # Clean up
        db.session.delete(resume)
        db.session.delete(user)
        db.session.commit()
        print("Cleanup successful.")
        
    except Exception as e:
        print(f"TEST FAILED: {e}")
        db.session.rollback()
