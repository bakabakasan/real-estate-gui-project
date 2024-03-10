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
            # Указываем кодировку символов
            estate = result.fetchall()
        print("Запрос выполнен успешно.")

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)

def load_estates_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM ESTATE WHERE id = :val"),
            val=id
        )
        rows = result.all()
        if len(rows) == 0:
            return None
        else:
            return dict(rows[0])