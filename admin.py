from flask import session
from models import Estate, User, Message, Administrator, db
from flask_admin.base import expose
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField
from wtforms.validators import InputRequired, Email, EqualTo, Length, Regexp
from wtforms import PasswordField, EmailField
from werkzeug.security import generate_password_hash

admin = Admin(name="DreamHouse", template_mode="bootstrap4")

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return 'admin_logged_in' in session and session['admin_logged_in']
    
    @expose('/')
    def index(self):
        admin_id = session.get('admin_id')
        admin = Administrator.query.get(admin_id)
        return self.render('admin/index.html', admin=admin)

class UserAdminView(ModelView):
    def is_accessible(self):
        return 'admin_logged_in' in session and session['admin_logged_in']

    column_display_pk = True
    column_labels = {
        'id': 'ID',
        'name': 'Имя',
        'email': 'Email'
    }
    column_list = ['id', 'name', 'email']
    form_extra_fields = {
        'password': PasswordField('Пароль', validators=[
            InputRequired(),
            Length(min=8, max=20, message='Пароль должен быть от 8 до 20 символов'),
            Regexp('^[a-zA-Z0-9]*$', message='Пароль должен содержать только латинские буквы и цифры')
        ]),
        'confirm_password': PasswordField('Повторите пароль', validators=[
            InputRequired(),
            EqualTo('password', message='Пароли должны совпадать')
        ]),
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    create_modal = True
    edit_modal = True

    column_searchable_list = ['id', 'email', 'name']
    column_filters = ['email', 'name']
    column_editable_list = ['email', 'name']

    can_delete = True
    can_create = True
    can_edit = True
    can_export = True

    export_max_rows = 500
    export_types = ['csv']

class AdministratorAdminView(ModelView):
    column_display_pk = True
    column_labels = {
        'id': 'ID',
        'full_name': 'Имя',
        'email': 'Email'
    }
    column_list = ['id', 'full_name', 'email']
    form_extra_fields = {
        'password': PasswordField('Пароль', validators=[
            InputRequired(),
            Length(min=8, max=20, message='Пароль должен быть от 8 до 20 символов'),
            Regexp('^[a-zA-Z0-9]*$', message='Пароль должен содержать только латинские буквы и цифры')
        ]),
        'confirm_password': PasswordField('Повторите пароль', validators=[
            InputRequired(),
            EqualTo('password', message='Пароли должны совпадать')
        ]),
        'email': EmailField('Email', validators=[InputRequired(), Email()])
    }

    column_descriptions = dict(
        full_name='Фамилия и имя'
    )

    column_searchable_list = ['id', 'email', 'full_name']
    column_filters = ['email', 'full_name']
    column_editable_list = ['email', 'full_name']
    
    create_modal = True
    edit_modal = True

    can_delete = False
    can_create = True
    can_edit = True
    can_export = True
    export_max_rows = 500
    export_types = ['csv']

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = generate_password_hash(form.password.data)
        return super(AdministratorAdminView, self).on_model_change(form, model, is_created)
    
    def is_accessible(self):
        return 'admin_logged_in' in session and session['admin_logged_in']

class EstateAdminView(ModelView):
    def is_accessible(self):
        return 'admin_logged_in' in session and session['admin_logged_in']

    column_display_pk = True
    column_labels = {
        'id': 'ID',
        'type': 'Тип',
        'location': 'Местоположение',
        'cost': 'Стоимость',
        'currency': 'Валюта',
        'bedrooms': 'Комнаты',
        'area': 'Площадь',
        'floor': 'Этажность',
        'description': 'Описание',
        'additional_information': 'Дополнительная информация',
        'photo': 'Фото',
        'user_id': 'ID Пользователя',
        'admin_id': 'ID Админа'
    }
    column_list = ['id', 'type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'user_id', 'admin_id']
    form_columns = ['type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']
    column_sortable_list = ['id', 'type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'user_id', 'admin_id']

    form_extra_fields = {
        'photo': FileUploadField('Photos', base_path='static/uploads/')
    }

    AVAILABLE_ESTATE_TYPES = [
        (u'Дом', u'Дом'),
        (u'Квартира', u'Квартира'),
    ]

    AVAILABLE_CURRENCY_TYPES = [
        (u'USD', u'USD'),
        (u'BYN', u'BYN'),
    ]
    
    AVAILABLE_BEDROOMS_TYPES = [
        (u'1', u'1'),
        (u'2', u'2'),
        (u'3', u'3'),
        (u'4', u'4'),
        (u'5', u'5'),
        (u'Студия', u'Студия'),
    ]
    form_choices = {
        'type': AVAILABLE_ESTATE_TYPES,
        'currency': AVAILABLE_CURRENCY_TYPES,
        'bedrooms': AVAILABLE_BEDROOMS_TYPES
    }
    
    column_descriptions = dict(
        user_id='Если зарегестрирован',
        admin_id='Опубликовавший Админ'
    )

    column_searchable_list = ['type', 'location', 'bedrooms']
    column_filters = ['type', 'location', 'cost', 'bedrooms']
    column_editable_list = ['type', 'location', 'cost', 'currency', 'bedrooms', 'area', 'floor', 'description', 'additional_information', 'photo', 'user_id', 'admin_id']

    create_modal = True
    edit_modal = True

    can_delete = True
    can_create = True
    can_edit = True
    can_export = True
    export_max_rows = 500
    export_types = ['csv']

class MessageAdminView(ModelView):
    def is_accessible(self):
        return 'admin_logged_in' in session and session['admin_logged_in']

    column_display_pk = True
    column_labels = {
        'id': 'ID',
        'full_name': 'Имя',
        'email': 'Email',
        'phone_number': 'Номер телефона',
        'message': 'Запрос',
        'page_url': 'Со страницы',
        'admin_id': 'ID Админа',
    }

    column_list = ['id', 'full_name', 'email', 'phone_number', 'message', 'page_url', 'admin_id']
    column_sortable_list = ['id', 'full_name', 'email', 'phone_number', 'admin_id']
    form_columns = ['full_name', 'email', 'phone_number', 'message', 'page_url', 'admin_id'] 
    
    column_descriptions = dict(
        admin_id='Ответственный Админ'
    )

    column_searchable_list = ['full_name', 'email', 'phone_number']
    column_filters = ['email', 'full_name']
    column_editable_list = ['admin_id']

    create_modal = False
    edit_modal = True

    can_delete = False
    can_create = False
    can_edit = True
    can_export = True
    export_max_rows = 500
    export_types = ['csv']

admin = Admin(name="DreamHouse", template_mode="bootstrap4", index_view=MyAdminIndexView())
admin.add_view(EstateAdminView(Estate, db.session, name='Недвижимость'))
admin.add_view(MessageAdminView(Message, db.session, name='Заявки'))
admin.add_view(AdministratorAdminView(Administrator, db.session, name='Администраторы'))
admin.add_view(UserAdminView(User, db.session, name='Пользователи'))
