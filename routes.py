from flask import Blueprint, render_template, request, redirect, session, abort, jsonify, url_for, flash
from models import Estate, User, Message, Administrator, ViewHistory, Favorite, db
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField, EmailField, StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Email, DataRequired, EqualTo, ValidationError, Length, Regexp
from flask_wtf import FlaskForm
import re
from flask_admin.form.upload import FileUploadField
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from datetime import timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
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

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        admin = Administrator.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            session['logged_in'] = True
            session['is_admin'] = True
            session['user_id'] = admin.id
            if remember_me:
                session.permanent = True
                main_bp.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
            return redirect("/admin")
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['is_admin'] = False
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            if remember_me:
                session.permanent = True
                main_bp.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
            return redirect('/')
        
        return redirect("/login?failed=True")
    else:
        return render_template("admin/login.html")

@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@main_bp.route("/contacts")
def contact_details():
    return render_template('contacts.html')

@main_bp.route("/about-us")
def about_company():
    return render_template('aboutus.html')

@main_bp.route("/place_ad")
def place_ad():
    return render_template('place_ad.html')

@main_bp.route("/api/estate")
def list_estate():
    try:
        estates = Estate.query.all()
        return jsonify(estate=estates)
    except Exception as e:
        return jsonify(error=str(e)), 500

@main_bp.route("/estateitem/<int:id>")
def show_estate(id):
    estate_item = Estate.query.get(id)
    if not estate_item:
        return "Not Found", 404

    is_favorite = False
    if session.get('logged_in') and not session.get('is_admin'):
        user_id = session.get('user_id')
        if user_id:  
            # Проверяем, есть ли недвижимость в избранном для текущего пользователя
            favorite = Favorite.query.filter_by(user_id=user_id, estate_id=estate_item.id).first()
            if favorite:
                is_favorite = True

    
    # Автоматическое добавление в историю просмотров
    if session.get('logged_in') and not session.get('is_admin'):
        user_id = session.get('user_id')
        if user_id:  
            history = ViewHistory(user_id=user_id, estate_id=id)
            db.session.add(history)
            db.session.commit()
        else:
            print("User ID is missing in session. Unable to add to view history.")

    return render_template('estatepage.html', estate=estate_item, is_favorite=is_favorite)

@main_bp.route("/sent-message", methods=['POST'])
def fill_in_the_form():
    try:
        data = request.form
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
                page_url=data.get('page_url', '')  # Если page_url получается автоматически, он будет взят из данных формы
            )
            db.session.add(message)
            db.session.commit()
            print("Сообщение успешно добавлено в базу данных.")
        else:
            print("Отсутствуют обязательные поля в данных.")
    except SQLAlchemyError as e:
        print("Произошла ошибка при добавлении сообщения в базу данных:", str(e))
        db.session.rollback()
        raise

@main_bp.route('/search', methods=['GET'])
def search():
    bedrooms = request.args.get('bedrooms')
    estate_type = request.args.get('type')
    price_range = request.args.get('price_range')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    results_query = perform_search(price_range, bedrooms, estate_type)
    total_results = results_query.count()
    results = results_query.paginate(page=page, per_page=per_page, error_out=False).items

    total_pages = (total_results + per_page - 1) // per_page

    return render_template('search_results.html', results=results, total_pages=total_pages, current_page=page)

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
    return query

@main_bp.route('/user/profile')
def profile():
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/user/profile')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    user = {
        'name': session.get('user_name'),
        'email': session.get('user_email')
    }
    return render_template('user/profile.html', user=user)

@main_bp.route('/user/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/user/profile')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    form = EditProfileForm(obj=user)
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('Изменения успешно сохранены', 'success')
        return redirect('/user/profile')
    
    return render_template('user/edit_profile.html', form=form)

@main_bp.route('/user/favorites')
def favorites():
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    favorites = Favorite.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/favorites.html', favorites=favorites)

@main_bp.route('/user/history')
def view_history():
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/')
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    history = ViewHistory.query.filter_by(user_id=user_id).order_by(ViewHistory.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/history.html', history=history)

@main_bp.route('/add_to_favorites/<int:estate_id>', methods=['POST'])
def add_to_favorites(estate_id):
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/')
    
    user_id = session.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, estate_id=estate_id).first()
    
    if favorite:
        flash('Эта недвижимость уже в вашем списке избранного.')
    else:
        favorite = Favorite(user_id=user_id, estate_id=estate_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Недвижимость добавлена в ваш список избранного.')

    return redirect(url_for('main.show_estate', id=estate_id))

@main_bp.route('/remove_from_favorites/<int:estate_id>', methods=['POST'])
def remove_from_favorites(estate_id):
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/')
    
    user_id = session.get('user_id')
    favorite = Favorite.query.filter_by(user_id=user_id, estate_id=estate_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash('Недвижимость удалена из вашего списка избранного.')
    else:
        flash('Эта недвижимость не была в вашем списке избранного.')

    return redirect(url_for('main.show_estate', id=estate_id))

@main_bp.route('/user/clear_history', methods=['POST'])
def clear_history():
    if not session.get('logged_in') or session.get('is_admin'):
        return redirect('/')

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Очистка истории просмотров пользователя
    ViewHistory.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    flash('История просмотров очищена', 'success')
    return redirect('/user/history')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Этот email уже используется, пожалуйста, выберите другой.', 'danger')
            return redirect(url_for('main.register'))
        
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрированы!', 'success')
        
        session['logged_in'] = True
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_email'] = new_user.email
        
        if form.remember_me.data:
            session.permanent = True
            main_bp.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
        
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

admin = Admin(name="DreamHouse", template_mode="bootstrap3")

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if "logged_in" in session and session.get('is_admin'):
            return True
        abort(403)

class UserAdminView(ModelView):
    column_list = ['id', 'name', 'email', 'password']
    form_extra_fields = {
        'password': PasswordField('Password', validators=[InputRequired()]),
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    def is_accessible(self):
        if "logged_in" in session and session.get('is_admin'):
            return True
        abort(403)

class AdministratorAdminView(ModelView):
    column_list = ['id', 'full_name', 'email', 'password']
    form_extra_fields = {
        'password': PasswordField('Password', validators=[InputRequired()]),
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    def is_accessible(self):
        if "logged_in" in session and session.get('is_admin'):
            return True
        abort(403)

class EstateAdminView(ModelView):
    column_list = ['id', 'type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']
    form_columns = ['type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']
    form_extra_fields = {
        'photo': FileUploadField('Photos', base_path='static/uploads/')
    }

    def is_accessible(self):
        if "logged_in" in session and session.get('is_admin'):
            return True
        abort(403)

class MessageAdminView(ModelView):
    column_list = ['id', 'full_name', 'email', 'phone_number', 'message', 'page_url', 'admin_id']
    form_columns = ['full_name', 'email', 'phone_number', 'message', 'page_url', 'admin_id'] 

    def is_accessible(self):
        if "logged_in" in session and session.get('is_admin'):
            return True
        abort(403)

class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Этот email уже используется, пожалуйста, выберите другой.')

    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8, max=20, message='Пароль должен быть от 8 до 20 символов'),
        Regexp('^[a-zA-Z0-9]*$', message='Пароль должен содержать только латинские буквы и цифры')
    ])
    confirm_password = PasswordField('Повторите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    remember_me = BooleanField('Запомнить меня')  # Добавлено поле для "Запомнить меня"
    submit = SubmitField('Зарегистрироваться')

class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message='Имя обязательно')])
    email = EmailField('Email', validators=[DataRequired(message='Email обязателен'), Email()])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=8, max=20, message='Пароль должен быть от 8 до 20 символов'),
        Regexp('^[a-zA-Z0-9]*$', message='Пароль должен содержать только латинские буквы и цифры')
    ])
    confirm_password = PasswordField('Повторите новый пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Сохранить изменения')

admin = Admin(name="DreamHouse", template_mode="bootstrap3", index_view=MyAdminIndexView())
admin.add_view(EstateAdminView(Estate, db.session, name='Недвижимость'))
admin.add_view(MessageAdminView(Message, db.session, name='Заявки'))
admin.add_view(AdministratorAdminView(Administrator, db.session, name='Администраторы'))
admin.add_view(UserAdminView(User, db.session, name='Пользователи'))
