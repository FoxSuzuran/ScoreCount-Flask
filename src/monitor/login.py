import json

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired


# 定义班长登录表单
class ClassMonitorLoginForm(FlaskForm):
    admin_name = StringField('用户名', validators=[InputRequired()])
    password = PasswordField('密码', validators=[InputRequired()])
    submit = SubmitField('登录')


def validate_admin(admin_name, password):
    try:
        with open("config/config.json", 'r') as file:
            data = json.load(file)
            if data.get("admin_name") == admin_name and data.get("password") == password:
                return True
    except FileNotFoundError:
        pass
    return False
