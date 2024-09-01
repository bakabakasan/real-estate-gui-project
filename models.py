from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    estates = relationship("Estate", back_populates="user")

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Administrator(db.Model):
    __tablename__ = 'administrators'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    estates = relationship("Estate", back_populates="admin")
    messages = relationship("Message", back_populates="admin")

    def check_password(self, password):
        return check_password_hash(self.password, password)

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

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    page_url = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20))
    admin_id = db.Column(db.Integer, db.ForeignKey('administrators.id'), nullable=True)
    admin = relationship("Administrator", back_populates="messages")

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    estate_id = db.Column(db.Integer, db.ForeignKey('estate.id'), nullable=False)
    user = relationship("User", back_populates="favorites")
    estate = relationship("Estate")

class ViewHistory(db.Model):
    __tablename__ = 'view_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    estate_id = db.Column(db.Integer, db.ForeignKey('estate.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user = relationship("User", back_populates="view_history")
    estate = relationship("Estate")

User.favorites = relationship("Favorite", back_populates="user")
User.view_history = relationship("ViewHistory", back_populates="user")
