from flask import Flask, render_template, jsonify, request, redirect, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)

db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_password = os.environ.get('DB_PASSWORD')
db_username = os.environ.get('DB_USERNAME')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}"

db = SQLAlchemy()
app.app_context().push()
db.init_app(app)

try:
        db.session.execute(text("SELECT 1"))
        print("Соединение с базой данных успешно установлено.")
        db.create_all()
        print("Таблицы успешно созданы.")
except SQLAlchemyError as e:
    print("Ошибка при соединении с базой данных:", str(e))

class Estate(db.Model):
    __tablename__ = 'estate'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    cost = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    bedrooms = db.Column(db.String(10))
    area = db.Column(db.String(20))
    floor = db.Column(db.String(20))
    description = db.Column(db.Text())
    additional_information = db.Column(db.Text())

    def __init__(self, type, location, cost=0.0, currency='USD', bedrooms=None, area=None, floor=None, description=None, additional_information=None):
        self.type = type
        self.location = location
        self.cost = cost
        self.currency = currency
        self.bedrooms = bedrooms
        self.area = area
        self.floor = floor
        self.description = description
        self.additional_information = additional_information

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(60))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(30))
    message = db.Column(db.Text())
    page_url = db.Column(db.String(200))

    def __init__(self, full_name, phone_number, email, message, page_url):
        self.full_name = full_name
        self.phone_number = phone_number
        self.email = email
        self.message = message
        self.page_url = page_url

    def save_to_database(self):
        pass
    
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(30))
    password = db.Column(db.String(10))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

@app.route("/") 
def hello_dreamhouse(): 
    try:
        estate = load_estate_from_db()
        return render_template('home.html', estate=estate) 
    except Exception as e:
        return render_template('error.html', error=str(e)), 500


def load_estate_from_db(): 
    try:
        with current_app.app_context():
            result = db.session.execute(text("SELECT * FROM estate"))
            rows = result.fetchall()
            db.session.close()
            print("Fetched rows from the database:", rows)  # Debug output 
            print("Query executed successfully.")
            return rows
    except SQLAlchemyError as e:
        print("An error occurred while executing the query:", str(e))
        return None

@app.route("/api/estate")
def list_estate():
    try:
        estates = load_estate_from_db()
        return jsonify(estate=estates)
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/estateitem/<id>")
def show_estate(id):
    estate_item = load_estateitem_from_db(id)
    if not estate_item:
        return "Not Found", 404
    return render_template('estatepage.html', estate=estate_item)

def load_estateitem_from_db(id):
    try:
        estate_item = Estate.query.filter_by(id=id).first()
        if estate_item:
            return {
               "id": estate_item.id, 
               "type": estate_item.type,
                "location": estate_item.location,
                "cost": estate_item.cost,
                "currency": estate_item.currency,
                "bedrooms": estate_item.bedrooms,
                "area": estate_item.area,
                "floor": estate_item.floor,
                "description": estate_item.description,
                "additional_information": estate_item.additional_information
            }
        else:
            return None
    except SQLAlchemyError as e:
        print("An error occurred while loading estate item from the database:", str(e))
        return None

@app.route("/sent-message", methods=['POST'])
def fill_in_the_form():
    try:
        data = request.form
        print("Form Data:", data)  # Для отладки: проверяем данные формы
        add_message_to_db(data)
        return render_template('sent_message.html', data=data)
    except SQLAlchemyError as e:
        return render_template('error.html', error=str(e)), 500

def add_message_to_db(data):
    try:
        if all(key in data for key in ['full_name', 'phone_number', 'email', 'message', 'page_url']):
            message = Message(
                full_name=data.get('full_name', ''),
                phone_number=data.get('phone_number', ''),
                email=data.get('email', ''),
                message=data.get('message', ''),
                page_url=data.get('page_url', '')
            )
            db.session.add(message)
            db.session.commit()
        else:
            print("Отсутствуют обязательные поля в данных.")
    except SQLAlchemyError as e:
        print("An error occurred while adding the message to the database:", str(e))
        db.session.rollback()
        raise

@app.route("/contacts") 
def contact_details(): 
    return render_template('contacts.html')

@app.route("/about-us") 
def about_company(): 
    return render_template('aboutus.html')

@app.route("/register", methods=['GET', 'POST']) 
def register(): 
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not name or not email or not password:
                return render_template('error.html', error='Please fill out all fields'), 400
            
            register_form(name, email, password)
        
        return render_template('register.html') 
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

def register_form(name, email, password):
    try:
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        print("User was added to the database successfully.")
    except SQLAlchemyError as e:
        print("An error occurred while adding the user to the database:", str(e))
        db.session.rollback()
        return None
    
@app.route("/login", methods=['GET', 'POST']) 
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Проверяем аутентификацию пользователя
            if authenticate_user(email, password):
                # Если аутентификация успешна, устанавливаем сессию для пользователя
                return redirect('/')
            else:
                # Если аутентификация не удалась, возвращаем сообщение об ошибке на страницу входа
                return render_template('login.html', error='Invalid email or password')

        return render_template('login.html')
    except Exception as e:
        return render_template('error.html', error=str(e)), 500  

def authenticate_user(email, password):
    try:
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return True
        else:
            return False
    except SQLAlchemyError as e:
        print("An error occurred while authenticating user:", str(e))
        return None
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
