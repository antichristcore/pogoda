import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from app.models.user import SearchHistory, FavoriteCity
from werkzeug.utils import secure_filename
from app import db
from app.forms.forms import ChangePasswordForm

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/')
@login_required
def index():
    history = (SearchHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(SearchHistory.created_at.desc())
               .limit(20)
               .all())
    favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all()
    return render_template('profile/index.html', history=history, favorites=favorites)


@profile_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    city = request.form.get('city', '').strip()
    if not city:
        flash('Город не указан.', 'warning')
        return redirect(url_for('main.index'))

    existing = FavoriteCity.query.filter_by(user_id=current_user.id, city=city).first()
    if not existing:
        fav = FavoriteCity(user_id=current_user.id, city=city)
        db.session.add(fav)
        db.session.commit()

    return redirect(url_for('main.weather_page', city=city))


@profile_bp.route('/favorites/remove/<int:fav_id>', methods=['POST'])
@login_required
def remove_favorite(fav_id):
    fav = FavoriteCity.query.filter_by(id=fav_id, user_id=current_user.id).first_or_404()
    db.session.delete(fav)
    db.session.commit()
    flash(f'{fav.city} удалён из избранного.', 'info')
    return redirect(url_for('profile.index'))


@profile_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    SearchHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('История поиска очищена.', 'info')
    return redirect(url_for('profile.index'))

@profile_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('Файл не выбран.', 'warning')
        return redirect(url_for('profile.index'))

    if not allowed_file(file.filename):
        flash('Допустимые форматы: png, jpg, jpeg, gif, webp.', 'danger')
        return redirect(url_for('profile.index'))

    filename = secure_filename(f'user_{current_user.id}_{file.filename}')
    upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))

    current_user.avatar = filename
    db.session.commit()
    flash('Аватар обновлён.', 'success')
    return redirect(url_for('profile.index'))

@profile_bp.route('/avatar/delete', methods=['POST'])
@login_required
def delete_avatar():
    if current_user.avatar and current_user.avatar != 'default.png':
        path = os.path.join(current_app.root_path, 'static', 'img', 'avatars', current_user.avatar)
        if os.path.exists(path):
            os.remove(path)
        current_user.avatar = 'default.png'
        db.session.commit()
        flash('Фото удалено.', 'info')
    return redirect(url_for('profile.index'))

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Неверный текущий пароль.', 'danger')
            return redirect(url_for('profile.change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Пароль успешно изменён.', 'success')
        return redirect(url_for('profile.index'))
    return render_template('profile/change_password.html', form=form)

@profile_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Аккаунт удалён.', 'info')
    return redirect(url_for('main.index'))

@profile_bp.route('/favorites/remove-by-city', methods=['POST'])
@login_required
def remove_favorite_by_city():
    city = request.form.get('city', '').strip()
    fav = FavoriteCity.query.filter_by(user_id=current_user.id, city=city).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect(url_for('main.weather_page', city=city))