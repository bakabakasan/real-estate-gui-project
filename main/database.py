from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

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
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM estate"))
            rows = result.fetchall()
            print("Fetched rows from the database:", rows)  # Debug output
            
            # Convert rows to dictionaries
            estates = []
            for row in rows:
                estate_dict = {}
                for column, value in zip(result.keys(), row):
                    estate_dict[column] = value
                estates.append(estate_dict)
                
        print("Query executed successfully.")
        return estates
    except SQLAlchemyError as e:
        print("An error occurred while executing the query:", str(e))
        return None
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
        
def add_message_to_db(page_url, data):
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO messages(full_name, phone_number, email, message, page_url) 
                VALUES(:full_name, :phone_number, :email, :message, :page_url)
            """)
            conn.execute(query, {
                'full_name': data['full_name'], 
                'phone_number': data['phone_number'], 
                'email': data['email'], 
                'message': data['message'], 
                'page_url': page_url
            })
        print("Message added to the database successfully.")
    except SQLAlchemyError as e:
        print("An error occurred while adding the message to the database:", str(e))
