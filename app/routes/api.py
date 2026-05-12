from flask import Blueprint, jsonify, request
from app.services.weather_service import WeatherService

api_bp = Blueprint('api', __name__)


@api_bp.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    service = WeatherService()
    weather = service.get_current_weather(city)

    if not weather:
        return jsonify({'error': 'Не удалось получить данные о погоде'}), 500

    if 'error' in weather:
        return jsonify({'error': weather['error']}), 404

    return jsonify({
        'city': weather['city'],
        'country': weather['country'],
        'temperature': weather['temperature'],
        'feels_like': weather['feels_like'],
        'humidity': weather['humidity'],
        'wind_speed': weather['wind_speed'],
        'description': weather['description'],
        'pressure': weather['pressure'],
        'visibility_km': weather['visibility'],
        'sunrise': weather['sunrise'],
        'sunset': weather['sunset'],
        'prec_probability': weather['prec_probability'],
    })


@api_bp.route('/forecast/<city>', methods=['GET'])
def get_forecast(city):
    service = WeatherService()
    forecast = service.get_forecast(city)

    if forecast is None:
        return jsonify({'error': 'Не удалось получить прогноз'}), 500

    return jsonify({'city': city, 'forecast': forecast})