import requests
from flask import current_app

USE_MOCK = True

MOCK_WEATHER = {
    'city': '{city}',
    'country': 'RU',
    'temperature': 18,
    'feels_like': 16,
    'humidity': 65,
    'wind_speed': 4.2,
    'description': 'Переменная облачность',
    'icon': '02d',
    'icon_url': 'https://openweathermap.org/img/wn/02d@2x.png',
    'pressure': 1013,
    'visibility': 10,
}

MOCK_FORECAST = [
    {'date': '2025-01-20', 'temp_min': 12, 'temp_max': 19, 'description': 'Ясно', 'icon': '01d', 'icon_url': 'https://openweathermap.org/img/wn/01d@2x.png', 'humidity': 55, 'wind_speed': 3.1},
    {'date': '2025-01-21', 'temp_min': 10, 'temp_max': 17, 'description': 'Облачно', 'icon': '03d', 'icon_url': 'https://openweathermap.org/img/wn/03d@2x.png', 'humidity': 70, 'wind_speed': 5.0},
    {'date': '2025-01-22', 'temp_min': 8,  'temp_max': 14, 'description': 'Дождь', 'icon': '10d', 'icon_url': 'https://openweathermap.org/img/wn/10d@2x.png', 'humidity': 85, 'wind_speed': 6.5},
    {'date': '2025-01-23', 'temp_min': 11, 'temp_max': 16, 'description': 'Гроза', 'icon': '11d', 'icon_url': 'https://openweathermap.org/img/wn/11d@2x.png', 'humidity': 90, 'wind_speed': 8.0},
    {'date': '2025-01-24', 'temp_min': 14, 'temp_max': 21, 'description': 'Ясно', 'icon': '01d', 'icon_url': 'https://openweathermap.org/img/wn/01d@2x.png', 'humidity': 50, 'wind_speed': 2.5},
]


class WeatherService:

    def __init__(self):
        self.api_key = current_app.config['OPENWEATHER_API_KEY']
        self.base_url = current_app.config['OPENWEATHER_BASE_URL']

    def get_current_weather(self, city: str) -> dict | None:
        if USE_MOCK:
            data = MOCK_WEATHER.copy()
            data['city'] = city.capitalize()
            return data

        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        try:
            response = requests.get(f'{self.base_url}/weather', params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_current(data)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {'error': 'Город не найден'}
            return {'error': 'Ошибка API погоды'}
        except requests.exceptions.RequestException:
            return {'error': 'Не удалось подключиться к сервису погоды'}

    def get_forecast(self, city: str) -> dict | None:
        if USE_MOCK:
            return MOCK_FORECAST

        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru',
            'cnt': 40
        }
        try:
            response = requests.get(f'{self.base_url}/forecast', params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_forecast(data)
        except requests.exceptions.RequestException:
            return None

    def _parse_current(self, data: dict) -> dict:
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'], 1),
            'description': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon'],
            'icon_url': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            'pressure': data['main']['pressure'],
            'visibility': data.get('visibility', 0) // 1000,
        }

    def _parse_forecast(self, data: dict) -> list:
        daily = {}
        for item in data['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in daily:
                daily[date] = {
                    'date': date,
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'description': item['weather'][0]['description'].capitalize(),
                    'icon': item['weather'][0]['icon'],
                    'icon_url': f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                    'humidity': item['main']['humidity'],
                    'wind_speed': round(item['wind']['speed'], 1),
                }
            else:
                daily[date]['temp_min'] = min(daily[date]['temp_min'], item['main']['temp_min'])
                daily[date]['temp_max'] = max(daily[date]['temp_max'], item['main']['temp_max'])

        for d in daily.values():
            d['temp_min'] = round(d['temp_min'])
            d['temp_max'] = round(d['temp_max'])

        return list(daily.values())[:5]
