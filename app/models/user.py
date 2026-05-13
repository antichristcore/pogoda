from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    theme = db.Column(db.String(10), nullable=False, default='light')

    avatar = db.Column(db.String(256), nullable=True, default='default.png')
    search_history = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    favorite_cities = db.relationship('FavoriteCity', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SearchHistory {self.city} by user {self.user_id}>'


class FavoriteCity(db.Model):
    __tablename__ = 'favorite_cities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<FavoriteCity {self.city} by user {self.user_id}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
