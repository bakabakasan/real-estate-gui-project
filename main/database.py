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
            
        print("Query executed successfully.")
        return rows
    except SQLAlchemyError as e:
        print("An error occurred while executing the query:", str(e))
        return None

# Usage
engine = create_db_engine()
estate = load_estate_from_db(engine)

def load_estateitem_from_db(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM estate WHERE id = :id"),
            {"id": id}
        )
        rows = result.fetchall()
        if len(rows) == 0:
            return None
        else:
            keys = result.keys()  # Get column names
            row_dict = dict(zip(keys, rows[0]))  # Create dictionary from tuple values
            return row_dict
        
def add_message_to_db(page_url, data):
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO messages(full_name, phone_number, email, message, page_url) 
                VALUES(:full_name, :phone_number, :email, :message, :page_url)""")
            if all(key in data for key in ['full_name', 'phone_number', 'email', 'message']):
                conn.execute(query, {
                    'full_name': data.get('full_name', ''),  
                    'phone_number': data.get('phone_number', ''),  
                    'email': data.get('email', ''),  
                    'message': data.get('message', ''),  
                    'page_url': page_url
                })
            else:
                print("Отсутствуют обязательные поля в данных.")
    except SQLAlchemyError as e:
        print("An error occurred while adding the message to the database:", str(e))
        raise

def register_form(name, email, password):
    try:
        with engine.connect() as conn:
            query = text("""
                         INSERT INTO users(name, email, password)
                         VALUES(:name, :email, :password)""")
            conn.execute(query, {
                    'name': name,  
                    'email': email,  
                    'password': password
                })
            print("User was added to the database successfully.")
    except SQLAlchemyError as e:
            print("An error occurred while adding the user to the database:", str(e)) 

def authenticate_user(email, password):
    try:
        with engine.connect() as conn:
            query = """
                    SELECT * FROM users
                    WHERE email = :email AND password = :password"""
            result = conn.execute(query, {
                'email': email,
                'password': password
            })
            user = result.fetchone()
            if user:
                # If user found in the database, return True
                return True
            else:
                # If user not found, return False
                return False
    except SQLAlchemyError as e:
        print("An error occurred while authenticating user:", str(e))
        return False     

