import json, openpyxl

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import InputRequired


# 定义班长登录表单
class StudentLoginForm(FlaskForm):
    student_id = StringField('学号', validators=[InputRequired()])
    student_name = StringField('姓名', validators=[InputRequired()])
    submit = SubmitField('登录')


def read_student_data() -> dict:
    file_path = "config/data.xlsx"
    data_dict = {}
    try:
        # 打开Excel文件
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        # 遍历每一行，从第二行开始（第一行是标题）
        for row in sheet.iter_rows(min_row=2, values_only=True):
            student_id, student_name = row[:2]  # 假设学号在第一列，姓名在第二列
            if student_id is not None:
                data_dict[str(student_id)] = str(student_name)
        wb.close()
    except Exception as e:
        # 处理异常
        print(f"读取数据失败: {str(e)}")

    return data_dict
