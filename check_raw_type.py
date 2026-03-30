from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    query = text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'resumes' AND column_name = 'user_id';
    """)
    result = db.session.execute(query).fetchone()
    if result:
        print(f"resumes.user_id type: {result[1]}")
    else:
        print("resumes.user_id not found")
