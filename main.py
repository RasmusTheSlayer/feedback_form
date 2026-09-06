import os
from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, Optional, Length
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
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
        validators=[
            DataRequired(message="Email обязателен")
        ]
    )
    tg_user = StringField(
        validators=[
            Optional()
        ]
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


# ---------- Маршрут ----------
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
    app.run()
