import json
from sqlalchemy import create_engine, text
import os

def read_config():
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')
    return db_username, db_password, db_host, db_name

def create_db_engine():
    db_username, db_password, db_host, db_name = read_config()
    db_connection_string = f"mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
    engine = create_engine(db_connection_string)
    print("Connected to the database.")
    return engine

def load_estate_from_db(engine): 
    with engine.connect() as conn:
        result = conn.execute(text("select * from estate"))
        estate = result.fetchall()
    print("Query executed successfully.")
    return estate

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)
