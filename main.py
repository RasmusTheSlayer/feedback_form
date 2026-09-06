import os
from flask import (
    Flask,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    session
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, Optional, Length
from flask_babel import Babel
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
babel = Babel(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ---------- Форма (WTForms) ----------
class Form(FlaskForm):
    name = StringField(
        validators=[
            DataRequired(message="Имя обязательно"),
            Length(min=2, max=30,
                   message="Имя должно быть от 2 до 30 символов")
        ]
    )
    email = EmailField(
        validators=[DataRequired(message="Email обязателен")]
    )
    tg_user = StringField(
        validators=[Optional()]
    )


# ---------- Модель базы данных ----------
class FormBack(db.Model):
    __tablename__ = 'form'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    tg_user = db.Column(db.String(50), nullable=True)

    @classmethod
    def create(cls, name, email, tg_user):
        form = cls(name=name, email=email, tg_user=tg_user)
        db.session.add(form)
        db.session.commit()
        return form

    def update(self, name, email, tg_user):
        self.name = name
        self.email = email
        self.tg_user = tg_user
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# ---------- Вспомогательные функции для админки ----------
def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ---------- Маршруты для входа/выхода ----------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        valid_username = os.getenv('ADMIN_USERNAME', 'admin')
        valid_password = os.getenv('ADMIN_PASSWORD', 'supersecret')
        if username == valid_username and password == valid_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_index'))
        else:
            error = 'Неверный логин или пароль'
    return render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index_view'))


# ---------- Админские маршруты ----------
@app.route('/admin')
@admin_required
def admin_index():
    # Получаем все записи
    records = FormBack.query.all()
    return render_template('admin/index.html', records=records)


@app.route('/admin/add', methods=['GET', 'POST'])
@admin_required
def admin_add():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        tg_user = request.form.get('tg_user')
        if name and email:
            FormBack.create(name, email, tg_user)
            flash('Запись добавлена', 'success')
            return redirect(url_for('admin_index'))
        else:
            flash('Имя и email обязательны', 'danger')
    return render_template('admin/add_edit.html', action='Добавить',
                           record=None)


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit(id):
    record = FormBack.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        tg_user = request.form.get('tg_user')
        if name and email:
            record.update(name, email, tg_user)
            flash('Запись обновлена', 'success')
            return redirect(url_for('admin_index'))
        else:
            flash('Имя и email обязательны', 'danger')
    return render_template('admin/add_edit.html', action='Редактировать',
                           record=record)


@app.route('/admin/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete(id):
    record = FormBack.query.get_or_404(id)
    record.delete()
    flash('Запись удалена', 'success')
    return redirect(url_for('admin_index'))


# ---------- Главная страница ----------
@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = Form()
    if form.validate_on_submit():
        FormBack.create(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            tg_user=form.tg_user.data.strip() if form.tg_user.data else None
        )
        flash('Спасибо! Анкета отправлена 🎉', 'success')
        return redirect(url_for('index_view'))
    return render_template('index.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='192.168.0.107', port=5000, debug=True)
