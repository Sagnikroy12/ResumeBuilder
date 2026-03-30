from app import create_app, db
from sqlalchemy import text
from datetime import datetime

app = create_app()
with app.app_context():
    try:
        user_email = 'sagnikruproy11@gmail.com'
        query = text("""
            SELECT count(*) FROM resumes 
            WHERE user_id = :user_id AND created_at >= :created_at
        """)
        count = db.session.execute(query, {'user_id': user_email, 'created_at': datetime(2026, 3, 30)}).scalar()
        print(f"Count: {count}")
    except Exception as e:
        print(f"Error: {e}")
