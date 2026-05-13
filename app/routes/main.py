from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.forms.forms import CitySearchForm
from app.services.weather_service import WeatherService
from app.models.user import SearchHistory
from app.forms.forms import MultiCitySearchForm
from app import db
from flask_login import current_user
from app.models.user import SearchHistory, FavoriteCity
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = CitySearchForm()
    weather = None
    forecast = None
    requested_at = None
    favorites = []

    if current_user.is_authenticated:
        favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        city = form.city.data.strip()
        service = WeatherService()
        weather = service.get_current_weather(city)
        requested_at = (datetime.utcnow() + timedelta(hours=4)).strftime('%H:%M')

        if weather and 'error' not in weather:
            forecast = service.get_forecast(city)
            if current_user.is_authenticated:
                history_entry = SearchHistory(user_id=current_user.id, city=weather['city'])
                db.session.add(history_entry)
                db.session.commit()
        elif weather:
            flash(weather['error'], 'danger')
            weather = None

    return render_template('index.html', form=form, weather=weather, forecast=forecast, favorites=favorites, requested_at=requested_at)

@main_bp.route('/weather/<city>')
def weather_page(city):
    service = WeatherService()
    weather = service.get_current_weather(city)
    requested_at = (datetime.utcnow() + timedelta(hours=4)).strftime('%H:%M')
    forecast = None
    favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all() if current_user.is_authenticated else []

    if weather and 'error' not in weather:
        forecast = service.get_forecast(city)
        if current_user.is_authenticated:
            history_entry = SearchHistory(user_id=current_user.id, city=weather['city'])
            db.session.add(history_entry)
            db.session.commit()
    else:
        flash(weather.get('error', 'Неизвестная ошибка'), 'danger')
        return redirect(url_for('main.index'))

    form = CitySearchForm()
    return render_template('index.html', form=form, weather=weather, forecast=forecast, favorites=favorites, requested_at=requested_at)


@main_bp.route('/compare', methods=['GET', 'POST'])
def compare():
    form = MultiCitySearchForm()
    results = []
    errors = []

    if form.validate_on_submit():
        cities = [c.strip() for c in form.cities.data.split(',') if c.strip()]
        cities = cities[:6]
        service = WeatherService()
        for city in cities:
            weather = service.get_current_weather(city)
            if weather and 'error' not in weather:
                if current_user.is_authenticated:
                    history_entry = SearchHistory(user_id=current_user.id, city=weather['city'])
                    db.session.add(history_entry)
                results.append(weather)
            else:
                errors.append(city)
        if current_user.is_authenticated:
            db.session.commit()
        if errors:
            flash(f'Не удалось получить погоду для: {", ".join(errors)}', 'warning')

    return render_template('compare.html', form=form, results=results)