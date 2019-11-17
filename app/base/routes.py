from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.base.forms import LoginForm, RegistrationForm
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
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None:
            if user.check_password(form.password.data):

                login_user(user)
                next_url = request.args.get('next')

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
        return redirect(url_for('home_blueprint.home'))

    form = RegistrationForm(request.form)
    status = ''
    print(form.validate_on_submit())
    if form.validate_on_submit():
        email = User.query.filter_by(email=request.form['email'].lower()).first()
        if email is None:
            user = User(email=form.email.data.lower(),
                        username=form.username.data,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('base_blueprint.login'))
        else:
            status = 'Пользователь с такой почтой уже зарегестрирован'

    return render_template('login/register.html', form=form, status=status)
