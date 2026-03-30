from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    query = text("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    """)
    results = db.session.execute(query).fetchall()
    for row in results:
        print(f"Schema: {row[0]}, Table: {row[1]}")
