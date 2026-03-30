import os
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    for table_name in ['users', 'resumes']:
        if inspector.has_table(table_name):
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  Column: {column['name']}, Type: {column['type']}, PK: {column.get('primary_key', False)}")
        else:
            print(f"\nTable {table_name} does not exist.")
