from flask import Flask, render_template, jsonify, request, redirect, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import os
from dotenv import load_dotenv
from flask_admin import Admin, AdminIndexView, form
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required

load_dotenv() 
app = Flask(__name__)

db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_password = os.environ.get('DB_PASSWORD')
db_username = os.environ.get('DB_USERNAME')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}"
app.config["SECRET_KEY"] = "mysecret"

db = SQLAlchemy(app)
app.app_context().push()
admin = Admin(app)
login = LoginManager(app) 
login.init_app(app)

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
    photo = db.Column(db.Text())

    def __init__(self, type, location, cost=0.0, currency='USD', bedrooms=None, area=None, floor=None, description=None, additional_information=None, photo=None):
        self.type = type
        self.location = location
        self.cost = cost
        self.currency = currency
        self.bedrooms = bedrooms
        self.area = area
        self.floor = floor
        self.description = description
        self.additional_information = additional_information
        self.photo = photo

class FilesModelView(ModelView):
    form_overrides = {
        'photo': form.FileUploadField
    }
    form_args = {
        'photo': {
            'label': 'Photo',
            'base_path': '/static/photos',
            'allow_overwrite': False
        }
    }

admin.add_view(FilesModelView(Estate, db.session, endpoint='files_model_view_estate'))
               
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
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(30))
    password = db.Column(db.String(128))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

        def __self__(self):
            return self.name
        
@login.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    else:
        return None

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Message, db.session))

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

@app.route("/login")
def login():
    return render_template('login.html')
 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return 'Вы вышли из аккаунта!'

@app.route("/home")
@login_required
def home():
    return 'Администратор - ' + current_user.email

@app.route("/") 
def hello_dreamhouse(): 
    try:
        estate = Estate.query.all()
        return render_template('home.html', estate=estate) 
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

def load_estate_from_db(): 
    try:
        with current_app.app_context():
            result = db.session.execute(text("SELECT * FROM estate"))
            rows = result.fetchall()
            db.session.close()
            print("Query executed successfully.")
            return rows
    except SQLAlchemyError as e:
        print("An error occurred while executing the query:", str(e))
        return None

@app.route("/api/estate")
def list_estate():
    try:
        estates = Estate.query.all()
        return jsonify(estate=estates)
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/estateitem/<id>")
def show_estate(id):
    estate_item = Estate.query.get(id)
    if not estate_item:
        return "Not Found", 404
    return render_template('estatepage.html', estate=estate_item)

def load_estateitem_from_db(id):
    try:
        estate_item = Estate.query.get(id=id).first()
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
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
