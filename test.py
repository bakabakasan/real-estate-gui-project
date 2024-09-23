import unittest
from unittest.mock import patch, MagicMock
from app import app, db
from models import User, Estate, Favorite, ViewHistory, Message, Administrator
from werkzeug.security import generate_password_hash
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "mysecret"

app.config.from_object(Config)

def generate_unique_email():
    return f"testuser{int(time.time())}{random.randint(1, 1000)}@example.com"

def create_admin_if_not_exists(full_name, email, password):
    existing_admin = Administrator.query.filter_by(email=email).first()
    if not existing_admin:
        admin = Administrator(full_name=full_name, email=email, password=generate_password_hash(password))
        db.session.add(admin)
        db.session.commit()
        return admin
    return existing_admin

class FlaskTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            db.create_all()
            unique_email = generate_unique_email()  # Генерация уникального email для администратора
            cls.admin = create_admin_if_not_exists('Test Admin', unique_email, 'admin123')
            cls.user = User(name='Test User', email=generate_unique_email(), password=generate_password_hash('password123'))
            db.session.add(cls.user)
            db.session.commit()
            print("Фикстуры установлены")
    
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()
            print("Таблицы удалены")

    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_hello_dreamhouse(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

    @patch('models.User.query.filter_by')
    @patch('models.db.session.commit')
    @patch('models.db.session.add')
    def test_register_user(self, mock_add, mock_commit, mock_filter_by):
        # Заглушка для метода фильтрации
        mock_filter_by.return_value.first.return_value = None  # Пользователь не существует
        
        # Генерация уникального email
        unique_email = generate_unique_email()
        
        # Выполнение запроса на регистрацию
        response = self.client.post('/register', data=dict(
            name='Test User',
            email=unique_email,
            password='password123',
            confirm_password='password123'
        ))
        
        # Проверка, что пользователь добавлен в сессию
        mock_add.assert_called()
        mock_commit.assert_called()
        self.assertEqual(response.status_code, 302)

    @patch('models.User.query.filter_by')
    def test_login_user(self, mock_filter_by):
        # Мокируем объект пользователя
        mock_user = MagicMock()
        mock_user.password = generate_password_hash('password123')
        mock_filter_by.return_value.first.return_value = mock_user
        
        response = self.client.post('/login', data=dict(
            email='testuser@example.com',
            password='password123'
        ))
        
        self.assertEqual(response.status_code, 302)  # Redirect to home

        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('user_logged_in'))

    def test_login_admin(self):
        response = self.client.post('/login', data=dict(
            email=self.admin.email,
            password='admin123',
            remember_me='y'
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/admin')

        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('admin_logged_in'))

    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/login')
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('user_logged_in'))

    @patch('models.User.query.filter_by')
    @patch('models.db.session.commit')
    def test_user_profile(self, mock_commit, mock_filter_by):
        mock_user = MagicMock()
        mock_user.id = self.user.id
        mock_user.name = self.user.name
        mock_user.email = self.user.email
        mock_filter_by.return_value.first.return_value = mock_user
        
        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id
            sess['user_name'] = self.user.name
            sess['user_email'] = self.user.email
        
        response = self.client.get('/user/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)

    @patch('models.Estate.query.get')
    def test_show_estate(self, mock_get_estate):
        mock_estate = MagicMock()
        mock_estate.id = 1
        mock_estate.type = 'Apartment'
        mock_estate.location = 'Test Location'
        mock_estate.cost = 50000
        mock_get_estate.return_value = mock_estate
        
        response = self.client.get(f'/estateitem/{mock_estate.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Location', response.data)

    def test_add_to_favorites(self):
        estate = Estate(name="Sample Estate", cost=50000)
        db.session.add(estate)
        db.session.commit()
        
        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id

        response = self.client.post(f'/add_to_favorites/{estate.id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.query.filter_by(user_id=self.user.id, estate_id=estate.id).count(), 1)

    def test_remove_from_favorites(self):
        estate = Estate(name="Sample Estate", cost=50000)
        db.session.add(estate)
        db.session.commit()

        favorite = Favorite(user_id=self.user.id, estate_id=estate.id)
        db.session.add(favorite)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id

        response = self.client.post(f'/remove_from_favorites/{estate.id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.query.filter_by(user_id=self.user.id, estate_id=estate.id).count(), 0)

    def test_fill_in_the_form(self):
        response = self.client.post('/sent-message', data=dict(
            full_name='Test Sender',
            phone_number='1234567890',
            email='sender@example.com',
            message='Test message',
            page_url='/'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test message', response.data)

    @patch('models.Estate.query.filter_by')
    def test_search(self, mock_filter_by):
        mock_estate = MagicMock()
        mock_estate.location = 'Test Location'
        mock_estate.type = 'Apartment'
        mock_filter_by.return_value.all.return_value = [mock_estate]
        
        response = self.client.get('/search', query_string=dict(
            type='Apartment'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Location', response.data)

    def test_view_history(self):
        view_history = ViewHistory(user_id=self.user.id, estate_id=1)
        db.session.add(view_history)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id

        response = self.client.get('/user/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View History', response.data)

    def test_clear_history(self):
        view_history = ViewHistory(user_id=self.user.id, estate_id=1)
        db.session.add(view_history)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id

        response = self.client.post('/user/clear_history')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ViewHistory.query.filter_by(user_id=self.user.id).count(), 0)

    def test_delete_account(self):
        with self.client.session_transaction() as sess:
            sess['user_logged_in'] = True
            sess['user_id'] = self.user.id

        response = self.client.post('/user/delete_account')
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(User.query.get(self.user.id))

if __name__ == '__main__':
    unittest.main()
