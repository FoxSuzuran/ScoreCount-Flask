from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

import loguru, os

from src import generate_xlsx_file
from src.utils import check_file, find_max_min, calculate_data, create_xlsx
from src.monitor import ClassMonitorLoginForm, validate_admin
from src.student import StudentLoginForm, read_student_data

# 添加你的检查逻辑，如果不通过，就退出应用
if not check_file():
    loguru.logger.info("请填写config文件下的配置文件后重新启动")
    exit(1)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'none_here'  # 请更改为实际的密钥


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = ClassMonitorLoginForm()
    if form.validate_on_submit():
        admin_name = form.admin_name.data
        password = form.password.data

        # 在这里进行班长登录验证，比对用户名和密码是否匹配
        # 您可以根据实际需求编写验证逻辑
        if validate_admin(admin_name, password):
            flash('登录成功！')
            session["admin_check"] = 1
            return redirect(url_for('management'))
        else:
            flash('用户名或密码错误，请重试。')

    return render_template('admin_login.html', form=form)


# 路由：管理界面
@app.route('/management')
def management():
    # 检查 session 中的 admin_check 变量
    admin_check = session.get('admin_check')
    if admin_check != 1:
        return '<script> alert("只有管理员用户可以访问");window.open("/login");</script>'

    # 获取总人数和已提交人数，这里仅作示例
    total_students = len(read_student_data().keys())
    submitted_students = len(os.listdir('data'))

    # 获取未提交学号列表
    unsubmitted_students = []
    for student_id in read_student_data().keys():
        student_filename = f"data/{student_id}.xlsx"
        if not os.path.exists(student_filename):
            unsubmitted_students.append(f"学号 {student_id}")

    # 判断按钮是否可点击
    button_disabled = submitted_students != total_students

    return render_template('management.html', total_students=total_students, submitted_students=submitted_students,
                           unsubmitted_students=unsubmitted_students, button_disabled=button_disabled)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = StudentLoginForm()
    # 构建学号-姓名格式的选项列表
    student_data = [f"{student_id}-{student_name}" for student_id, student_name in
                    read_student_data().items()]
    form.student.choices = student_data
    if form.validate_on_submit():
        session["student"] = form.student.data.split("-")[0]
        return redirect(url_for('score_form'))
    return render_template('student_login.html', form=form)


@app.route('/score-form', methods=['GET', 'POST'])
def score_form():
    score_min, score_max = find_max_min()
    return render_template('score_form.html', students=read_student_data(), min=score_min, max=score_max)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    score_min, score_max = find_max_min()
    students = read_student_data()
    if request.method == 'POST':
        form_data = request.form
        student_key = session.get('student')  # 获取当前用户的学号

        for student_id, student_name in students.items():
            if student_id == student_key:
                continue  # 跳过当前用户的分数检查

            for i in range(1, 5):  # 四个分数列
                key = f'score_{student_id}_{i}'
                score = form_data.get(key)

                if not score:
                    flash(f"{student_name}（学号：{student_id}）的分数不能为空。", 'error')
                elif not (score_min <= int(score) <= score_max):
                    flash(f"{student_name}（学号：{student_id}）的分数不在允许范围内（{score_min} 到 {score_max}）。",
                          'error')
        else:
            # 保存数据到文件
            file_name = f'{student_key}.xlsx'
            try:
                generate_xlsx_file("data/" + file_name, form_data, students, student_key)
            except Exception as e:
                flash('保存文件出错', 'error')
                loguru.logger.error(e)
            flash('表格数据已成功提交并保存在服务器上。', 'success')

            return redirect(url_for('score_form'))


# 首页
@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/login')


@app.route('/calculate', methods=['POST'])
def calculate():
    success = True
    try:
        student_scores = calculate_data()
        # 调用函数，分别生成四个文件
        create_xlsx(student_scores, '思想道德素质分')
        create_xlsx(student_scores, '身心素质分')
        create_xlsx(student_scores, '审美与人文素养分')
        create_xlsx(student_scores, '劳动素养分')
    except Exception as e:
        success = False
        loguru.logger.error(e)
        print(e)
    if success:
        return jsonify({'message': '计算成功！'})
    else:
        return jsonify({'message': '计算失败，请检查报错并重试。'})


if __name__ == '__main__':
    app.run(debug=True)
