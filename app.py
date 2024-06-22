from flask import Flask, render_template, jsonify, request, redirect, current_app, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import os
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField, EmailField
from flask_admin.form.upload import FileUploadField
from wtforms.validators import InputRequired, Email
from flask_migrate import Migrate
from sqlalchemy.orm import relationship

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
migrate = Migrate(app, db)

try:
    db.session.execute(text("SELECT 1"))
    print("Соединение с базой данных успешно установлено.")
    db.create_all()
    print("Таблицы успешно созданы.")
except SQLAlchemyError as e:
    print("Ошибка при соединении с базой данных:", str(e))

admin = Admin(app, name="DreamHouse", template_mode="bootstrap3")

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    estates = relationship("Estate", back_populates="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def check_password(self, password):
        return self.password == password

class Administrator(db.Model):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    estates = relationship("Estate", back_populates="admin")
    messages = relationship("Message", back_populates="admin")

    def __init__(self, full_name, email, password):
        self.full_name = full_name
        self.email = email
        self.password = password

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id'))
    user = relationship("User", back_populates="estates")
    admin = relationship("Administrator", back_populates="estates")

    def __init__(self, type, location, cost=0.0, currency='USD', bedrooms=None, area=None, floor=None, description=None, additional_information=None, photo=None, user_id=None, admin_id=None):
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
        self.user_id = user_id
        self.admin_id = admin_id

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    page_url = db.Column(db.String(200), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id'))
    admin = relationship("Administrator", back_populates="messages")

    def __init__(self, full_name, email, password, message, page_url, admin_id=None):
        self.full_name = full_name
        self.email = email
        self.password = password
        self.message = message
        self.page_url = page_url
        self.admin_id = admin_id

class UserAdminView(ModelView):
    column_list = ['id', 'name', 'email', 'password']  
    form_extra_fields = {
        'password': PasswordField('Password', validators=[InputRequired()]), 
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)

class AdministratorAdminView(ModelView):
    column_list = ['id', 'full_name', 'email', 'password']  
    form_extra_fields = {
        'password': PasswordField('Password', validators=[InputRequired()]), 
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)

class EstateAdminView(ModelView):
    column_list = ['id', 'type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']
    form_columns = ['type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']
    form_extra_fields = {
        'photo': FileUploadField('Photos', base_path='static/uploads/')
    }

class MessageAdminView(ModelView):
    column_list = ['id', 'full_name', 'email', 'password', 'message', 'page_url', 'admin_id']
    form_columns = ['full_name', 'email', 'password', 'message', 'page_url', 'admin_id']

admin.add_view(UserAdminView(User, db.session, name='Пользователь'))
admin.add_view(AdministratorAdminView(Administrator, db.session, name='Администратор'))
admin.add_view(EstateAdminView(Estate, db.session, name='Недвижимость'))
admin.add_view(MessageAdminView(Message, db.session, name='Заявки'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):  
            session['logged_in'] = True
            return redirect("/admin") 
        else:
            return redirect("/login?failed=True")  
    else:
        return render_template("admin/login.html")  

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/") 
def hello_dreamhouse(): 
    try:
        estate = Estate.query.all()
        page = request.args.get('page', 1, type=int)
        per_page = 10
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (len(estate) + per_page - 1) // per_page

        estates_on_page = estate[start:end]

        return render_template('home.html', estate=estate, estates_on_page=estates_on_page, total_pages=total_pages) 
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
    
@app.route("/estateitem/<int:id>")
def show_estate(id):
    estate_item = Estate.query.get(id)
    if not estate_item:
        return "Not Found", 404
    return render_template('estatepage.html', estate=estate_item)

def load_estateitem_from_db(id):
    try:
        estate_item = Estate.query.get(id)
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
                "additional_information": estate_item.additional_information,
                "photo": estate_item.photo  
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

@app.route('/search', methods=['GET'])
def search():
    bedrooms = request.args.get('bedrooms')
    estate_type = request.args.get('type')
    price_range = request.args.get('price_range')
    results = perform_search(price_range, bedrooms, estate_type)
    return render_template('search_results.html', results=results)

def perform_search(price_range, bedroom, estate_type):
    query = db.session.query(Estate)
    if bedroom:
        query = query.filter_by(bedrooms=bedroom)
    if estate_type:
        query = query.filter_by(type=estate_type)
    if price_range:
        if price_range == '200000-more':
            query = query.filter(Estate.cost >= 200000)
        else:
            min_price, max_price = map(int, price_range.split('-'))
            query = query.filter(Estate.cost.between(min_price, max_price))
    return query.all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
