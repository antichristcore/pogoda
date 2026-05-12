import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///weather_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    YANDEX_GEOCODER_KEY = os.getenv('YANDEX_GEOCODER_KEY', '')
    YANDEX_WEATHER_API_KEY = os.getenv('YANDEX_WEATHER_API_KEY', '')
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
