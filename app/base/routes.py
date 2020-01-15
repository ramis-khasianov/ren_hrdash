from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from app.base.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.base.models import User
from app.extensions import db

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)


@blueprint.route('/')
def route_default():
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    status = ''
    try:
        current_app.logger.debug(form.email.data.lower().replace(' ', ''))
    except:
        pass
    current_app.logger.debug('form not validated')
    email_entered = form.email.data
    password_entered = form.password.data
    current_app.logger.debug(f'user entered {email_entered} and {password_entered} form not validated')
    current_app.logger.debug('form not validated')
    if form.validate_on_submit():
        try:
            current_app.logger.debug(form.email.data.lower().replace(' ', ''))
        except:
            pass
        current_app.logger.debug('form validated')
        user = User.query.filter_by(email=form.email.data.lower().replace(' ', ''), active=1).first()
        if user is not None:
            current_app.logger.debug(f'found user {user}')
            if user.check_password(form.password.data):
                current_app.logger.debug(f'user {user} entered correct password')
                login_user(user)
                next_url = request.args.get('next')
                current_app.logger.debug(f'{user} signed in')
                if next_url is None or not next_url[0] == '/':
                    next_url = url_for('home_blueprint.index')

                return redirect(next_url)
            else:
                status = 'Неверный пароль'
        else:
            status = 'Пользователя с такой почтой нет'

    return render_template('login/login.html', form=form, status=status)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))

    form = RegistrationForm(request.form)
    status = ''
    current_app.logger.debug('registration form not validated')
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=request.form['email'].replace(' ', '').lower()).first()
        current_app.logger.debug(f'registration form validated, entered {form.email.data} and {form.username.data} with {form.password.data} and {form.pass_confirm.data}')
        if existing_user is None:
            user = User(email=form.email.data.lower().replace(' ', ''),
                        username=form.username.data,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
            current_app.logger.debug('new_user_registered')
            return redirect(url_for('base_blueprint.login'))
        elif not existing_user.active:
            existing_user.password_hash = generate_password_hash(form.password.data)
            existing_user.username = form.username.data
            existing_user.active = True
            db.session.commit()
            return redirect(url_for('base_blueprint.login'))
        else:
            status = 'Пользователь с такой почтой уже зарегестрирован'

    return render_template('login/register.html', form=form, status=status)


@blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():

    form = ChangePasswordForm()
    status = ''
    if form.validate_on_submit():
        user = User.query.filter_by(user_id=current_user.user_id).first()
        if user.check_password(request.form['current_password']):
            if request.form['new_password'] == request.form['pass_confirm']:
                user.password_hash = generate_password_hash(request.form['new_password'])
                db.session.commit()
                logout_user()
                return redirect(url_for('base_blueprint.login'))
            else:
                status = 'Пароли не совпадают'
        else:
            status = 'Проверьте текущий пароль'

    return render_template('login/change_password.html', form=form, status=status)
