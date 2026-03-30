import os
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    table_names = inspector.get_table_names()
    for table_name in table_names:
        if table_name == 'alembic_version':
            continue
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pks = pk_constraint.get('constrained_columns', [])
        
        for column in columns:
            is_pk = column['name'] in pks
            print(f"  Column: {column['name']}, Type: {column['type']}, PK: {is_pk}")
        
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            print(f"  FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        else:
            print(f"\nTable {table_name} does not exist.")
