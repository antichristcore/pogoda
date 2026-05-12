from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Войдите в аккаунт для доступа к этой странице.'
login_manager.login_message_category = 'warning'

def format_time(value):
    try:
        return value[11:16]
    except (TypeError, IndexError):
        return '--:--'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        app.jinja_env.filters['format_date'] = format_date
        app.jinja_env.filters['format_time'] = format_time

    return app

def format_date(value):
    months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн',
              'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    try:
        dt = datetime.strptime(value, '%Y-%m-%d')
        today = datetime.today().date()
        if dt.date() == today:
            return 'Сегодня'
        if (dt.date() - today).days == 1:
            return 'Завтра'
        return f'{days[dt.weekday()]} {dt.day} {months[dt.month - 1]}'
    except (ValueError, AttributeError):
        return value
