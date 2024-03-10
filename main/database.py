from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def read_config():
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')

    return db_username, db_password, db_host, db_name

def create_db_engine():
    db_username, db_password, db_host, db_name = read_config()
    db_connection_string = f"postgresql://{db_username}:{db_password}@{db_host}/{db_name}"
    engine = create_engine(db_connection_string)
    print("Connected to the database.")
    return engine

def load_estate_from_db(engine): 
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM estate"))
            estate = result.fetchall()
        print("Query executed successfully.")
        return estate
    except UnicodeDecodeError as e:
        print("Error decoding data:", e)
        # Handle the error gracefully, e.g., log it or skip the problematic data.
        return None

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)