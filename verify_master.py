from app import create_app, db
from app.models.user import User
from app.models.resume import Resume
import json
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        test_email = "sagnikruproy11@gmail.com"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            print(f"User {test_email} not found!")
        else:
            # Create a test resume for this user
            resume = Resume(
                user_id=user.email,
                title="Master User Live Test",
                data=json.dumps({"name": "Sagnik Master"}),
                template_id="template1"
            )
            db.session.add(resume)
            db.session.commit()
            print(f"SUCCESS: Resume saved for {test_email}")
            
            # Verify count query
            count = Resume.query.filter_by(user_id=test_email).count()
            print(f"Resumes for {test_email} in DB: {count}")
            
            # Clean up test resume (leave user)
            db.session.delete(resume)
            db.session.commit()
            print("Cleanup (resume) successful.")
            
    except Exception as e:
        print(f"LIVE TEST FAILED: {e}")
        db.session.rollback()
