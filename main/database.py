import json
from sqlalchemy import create_engine, text

def read_config(filename):
    with open(filename, 'r') as file:
        config_data = json.load(file)
    db_username = config_data['DB_USERNAME']
    db_password = config_data['DB_PASSWORD']
    db_host = config_data['DB_HOST']
    db_name = config_data['DB_NAME']
    return db_username, db_password, db_host, db_name

def create_db_engine(config_filename):
    db_username, db_password, db_host, db_name = read_config(config_filename)
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
config_filename = 'config.json'
engine = create_db_engine(config_filename)
estate = load_estate_from_db(engine)
