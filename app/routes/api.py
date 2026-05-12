from flask import Blueprint, jsonify
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
        'icon_url': weather['icon_url'],
        'pressure': weather['pressure'],
        'visibility_km': weather['visibility'],
    })


@api_bp.route('/forecast/<city>', methods=['GET'])
def get_forecast(city):

    service = WeatherService()
    forecast = service.get_forecast(city)

    if forecast is None:
        return jsonify({'error': 'Не удалось получить прогноз'}), 500

    return jsonify({'city': city, 'forecast': forecast})

@api_bp.route('/cities')
def cities():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    service = WeatherService()
    results = service.search_cities(q)
    return jsonify(results)

#TODO def cities()