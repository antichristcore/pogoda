import requests
from flask import current_app
import time
USE_MOCK = False

MOCK_WEATHER = {
    'city': '{city}',
    'country': 'RU',
    'temperature': 18,
    'feels_like': 16,
    'humidity': 65,
    'wind_speed': 4.2,
    'description': 'Переменная облачность',
    'icon': '/static/img/weather/cloudy.svg',
    'pressure': 759,
    'visibility': 10,
    'sunrise': '06:00',
    'sunset': '20:00',
    'uv': 3,
}

MOCK_FORECAST = [
    {'date': '2025-01-20', 'temp_min': 12, 'temp_max': 19, 'description': 'Ясно', 'icon': '/static/img/weather/day.svg', 'humidity': 55, 'wind_speed': 3.1, 'pop': 0},
    {'date': '2025-01-21', 'temp_min': 10, 'temp_max': 17, 'description': 'Облачно', 'icon': '/static/img/weather/cloudy.svg', 'humidity': 70, 'wind_speed': 5.0, 'pop': 20},
    {'date': '2025-01-22', 'temp_min': 8, 'temp_max': 14, 'description': 'Дождь', 'icon': '/static/img/weather/rainy-1.svg', 'humidity': 85, 'wind_speed': 6.5, 'pop': 80},
    {'date': '2025-01-23', 'temp_min': 11, 'temp_max': 16, 'description': 'Гроза', 'icon': '/static/img/weather/thunder.svg', 'humidity': 90, 'wind_speed': 8.0, 'pop': 90},
    {'date': '2025-01-24', 'temp_min': 14, 'temp_max': 21, 'description': 'Ясно', 'icon': '/static/img/weather/day.svg', 'humidity': 50, 'wind_speed': 2.5, 'pop': 0},
]

YANDEX_ICONS = {
    'CLEAR': 'day.svg',
    'PARTLY_CLOUDY': 'cloudy-day-1.svg',
    'CLOUDY': 'cloudy-day-2.svg',
    'OVERCAST': 'cloudy.svg',
    'DRIZZLE': 'rainy-4.svg',
    'LIGHT_RAIN': 'rainy-1.svg',
    'RAIN': 'rainy-2.svg',
    'MODERATE_RAIN': 'rainy-3.svg',
    'HEAVY_RAIN': 'rainy-5.svg',
    'CONTINUOUS_HEAVY_RAIN': 'rainy-6.svg',
    'SHOWERS': 'rainy-7.svg',
    'WET_SNOW': 'snowy-4.svg',
    'LIGHT_SNOW': 'snowy-1.svg',
    'SNOW': 'snowy-2.svg',
    'SNOW_SHOWERS': 'snowy-3.svg',
    'HAIL': 'snowy-6.svg',
    'THUNDERSTORM': 'thunder.svg',
    'THUNDERSTORM_WITH_RAIN': 'thunder.svg',
    'THUNDERSTORM_WITH_HAIL': 'thunder.svg',
}

YANDEX_CONDITIONS = {
    'CLEAR': 'Ясно',
    'PARTLY_CLOUDY': 'Малооблачно',
    'CLOUDY': 'Облачно с прояснениями',
    'OVERCAST': 'Пасмурно',
    'DRIZZLE': 'Морось',
    'LIGHT_RAIN': 'Небольшой дождь',
    'RAIN': 'Дождь',
    'MODERATE_RAIN': 'Умеренный дождь',
    'HEAVY_RAIN': 'Сильный дождь',
    'CONTINUOUS_HEAVY_RAIN': 'Длительный сильный дождь',
    'SHOWERS': 'Ливень',
    'WET_SNOW': 'Дождь со снегом',
    'LIGHT_SNOW': 'Небольшой снег',
    'SNOW': 'Снег',
    'SNOW_SHOWERS': 'Снегопад',
    'HAIL': 'Град',
    'THUNDERSTORM': 'Гроза',
    'THUNDERSTORM_WITH_RAIN': 'Дождь с грозой',
    'THUNDERSTORM_WITH_HAIL': 'Гроза с градом',
}
WIND_DIRECTIONS = {
    'CALM': 'Штиль',
    'N': 'С',
    'NNE': 'ССВ',
    'NE': 'СВ',
    'ENE': 'ВСВ',
    'E': 'В',
    'ESE': 'ВЮВ',
    'SE': 'ЮВ',
    'SSE': 'ЮЮВ',
    'S': 'Ю',
    'SSW': 'ЮЮЗ',
    'SW': 'ЮЗ',
    'WSW': 'ЗЮЗ',
    'W': 'З',
    'WNW': 'ЗСЗ',
    'NW': 'СЗ',
    'NNW': 'ССЗ',
}

class WeatherService:

    def __init__(self):
        if not USE_MOCK:
            self.yandex_key = current_app.config['YANDEX_WEATHER_API_KEY']
            self.geocoder_key = current_app.config['YANDEX_GEOCODER_KEY']

    def geocode(self, city):
        for attempt in range(3):
            try:
                r = requests.get(
                    'https://geocode-maps.yandex.ru/1.x/',
                    params={
                        'apikey': self.geocoder_key,
                        'geocode': city,
                        'format': 'json',
                        'results': 1,
                        'lang': 'ru_RU'
                    },
                    timeout=10
                )
                r.raise_for_status()
                data = r.json()
                members = data['response']['GeoObjectCollection']['featureMember']
                if not members:
                    return None
                obj = members[0]['GeoObject']
                lon, lat = map(float, obj['Point']['pos'].split())
                components = obj['metaDataProperty']['GeocoderMetaData']['Address']['Components']
                name = next((c['name'] for c in components if c['kind'] == 'locality'), obj['name'])
                country = next((c['name'] for c in components if c['kind'] == 'country'), '')
                return lat, lon, name, country
            except Exception as e:
                print(f"Ошибка геокодера: {e}")
                print(f"Геокодер попытка {attempt + 1}: {e}")
                time.sleep(1)
        return None

    def yandex_query(self, lat, lon):
        # НЕ ТРОГАТЬ, если код не работает, то достать из utils.txt
        query = f"""
        {{
          weatherByPoint(request: {{ lat: {lat}, lon: {lon} }}) {{
            now {{
              temperature
              feelsLike
              humidity
              pressure
              windSpeed
              condition
              visibility
              precProbability
              uvIndex
              windGust
            }}
            forecast {{
              days(limit: 5) {{
                sunriseTime
                sunsetTime
                parts {{
                  day {{
                    temperature
                    humidity
                    windSpeed
                    condition
                    precProbability
                  }}
                  night {{
                    temperature
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        for attempt in range(3):
            try:
                r = requests.post(
                    'https://api.weather.yandex.ru/graphql/query',
                    headers={'X-Yandex-Weather-Key': self.yandex_key},
                    json={'query': query},
                    timeout=10
                )
                r.raise_for_status()
                return r.json()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка Яндекс погоды: {e}")
                print(f"Яндекс погода попытка {attempt + 1}: {e}")
                time.sleep(1)
        return None

    def get_current_weather(self, city: str) -> dict | None:
        if USE_MOCK:
            data = MOCK_WEATHER.copy()
            data['city'] = city.capitalize()
            return data

        geo = self.geocode(city)
        if not geo:
            return {'error': 'Город не найден'}

        lat, lon, city_name, country = geo
        data = self.yandex_query(lat, lon)

        if not data or 'errors' in data:
            return {'error': 'Ошибка API погоды'}

        now = data['data']['weatherByPoint']['now']
        days = data['data']['weatherByPoint']['forecast']['days']
        condition = now.get('condition', 'CLEAR')

        sunrise = days[0].get('sunriseTime', '--:--') if days else '--:--'
        sunset = days[0].get('sunsetTime', '--:--') if days else '--:--'
        print(now.get('precProbability'))
        return {
            'city': city_name,
            'country': country,
            'temperature': now['temperature'],
            'feels_like': now['feelsLike'],
            'humidity': now['humidity'],
            'wind_speed': round(now['windSpeed'], 1),
            'description': YANDEX_CONDITIONS.get(condition, condition).capitalize(),
            'icon': f"/static/img/weather/{YANDEX_ICONS.get(condition, 'cloudy.svg')}",
            'pressure': round(now['pressure'] * 0.750064),
            'visibility': round(now.get('visibility', 0) / 1000, 1),
            'sunrise': sunrise,
            'sunset': sunset,
            'uv': now.get('uvIndex') or now.get('uv') or 0,
            'wind_gust': round(now.get('windGust', 0), 1),
            'wind_direction': WIND_DIRECTIONS.get(now.get('windDirection', ''), '—'),
            'cloudiness': now.get('cloudiness', '—'),
            'prec_probability': round(now.get('precProbability', 0) * 100),
        }

    def get_forecast(self, city):
        if USE_MOCK:
            return MOCK_FORECAST

        geo = self.geocode(city)
        if not geo:
            return None

        lat, lon, _, _ = geo
        data = self.yandex_query(lat, lon)

        if not data or 'errors' in data:
            return None

        days = data['data']['weatherByPoint']['forecast']['days']
        result = []
        for day in days:
            day_part = day['parts']['day']
            night_part = day['parts']['night']
            condition = day_part.get('condition', 'CLEAR')
            result.append({
                'date': day.get('sunriseTime', '')[:10],
                'temp_min': night_part.get('temperature', 0),
                'temp_max': day_part.get('temperature', 0),
                'description': YANDEX_CONDITIONS.get(condition, condition).capitalize(),
                'icon': f"/static/img/weather/{YANDEX_ICONS.get(condition, 'cloudy.svg')}",
                'humidity': day_part.get('humidity', 0),
                'wind_speed': round(day_part.get('windSpeed', 0), 1),
                'pop': round(day_part.get('precProbability', 0) * 100),
            })

        return result

    def search_cities(self, query):
        if USE_MOCK:
            mock_cities = ['Москва', 'Берлин', 'Лондон', 'Париж', 'Токио']
            return [c for c in mock_cities if c.lower().startswith(query.lower())]
        try:
            r = requests.get(
                'https://geocode-maps.yandex.ru/1.x/',
                params={
                    'apikey': self.geocoder_key,
                    'geocode': query,
                    'format': 'json',
                    'results': 5,
                    'lang': 'ru_RU'
                },
                timeout=5
            )
            r.raise_for_status()
            data = r.json()
            members = data['response']['GeoObjectCollection']['featureMember']
            result = []
            for m in members:
                components = m['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['Components']
                name = next((c['name'] for c in components if c['kind'] == 'locality'), None)
                if name:
                    result.append(name)
            return result
        except Exception:
            return []