from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def read_config():
    db_url = os.environ.get('DB_URL')

    print("DB_URL:", db_url)

    return db_url

def create_db_engine():
    db_url = read_config()
    engine = create_engine(db_url)
    print("Connected to the database.")
    return engine

def load_estate_from_db(engine): 
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM estate"))
        estate = result.fetchall()
    print("Query executed successfully.")
    return estate

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)

