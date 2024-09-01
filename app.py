import os
from dotenv import load_dotenv
from flask import Flask, g, session
from models import User
from models import db
from routes import main_bp
from admin import admin
from flask_migrate import Migrate
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask_babel import Babel

load_dotenv()
app = Flask(__name__)

db_host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')
db_password = os.environ.get('DB_PASSWORD')
db_username = os.environ.get('DB_USERNAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "mysecret"
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'

db.init_app(app)
migrate = Migrate(app, db)
babel = Babel(app)
app.app_context().push()
app.register_blueprint(main_bp)
admin.init_app(app)

try:
    db.session.execute(text("SELECT 1"))
    print("Соединение с базой данных успешно установлено.")
    db.create_all()
    print("Таблицы успешно созданы.")
except SQLAlchemyError as e:
    print("Ошибка при соединении с базой данных:", str(e))

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.context_processor
def inject_user():
    return dict(current_user=g.user)


if __name__ == "__main__":

    # Запуск приложения Flask
    app.run(host="0.0.0.0", debug=True)
