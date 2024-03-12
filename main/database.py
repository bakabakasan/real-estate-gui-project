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
    db_connection_string = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}?client_encoding=utf8"
    engine = create_engine(db_connection_string)
    print("Connected to the database.")
    return engine
    
def load_estate_from_db(engine): 
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM estate"))
            # Указываем кодировку символов
            estates = result.fetchall()
        print("Query executed successfully.")
        # Декодируем данные после извлечения
        return estates

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)

def load_estateitem_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM ESTATE WHERE id = :id"),
            {"id": id}
        )
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        else:
            keys = result.keys()  # Получаем имена столбцов
            row_dict = dict(zip(keys, rows[0]))  # Создаем словарь из кортежа значений
            return row_dict
    