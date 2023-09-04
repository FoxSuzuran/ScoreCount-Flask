from openpyxl import Workbook


def generate_xlsx_file(file_path, form_data, students, student_key):
    # 创建工作簿和工作表
    wb = Workbook()
    ws = wb.active
    ws.title = 'Scores'

    # 写入表头
    headers = ['学号', '姓名', '思想道德素质分', '身心素质分', '审美与人文素养分', '劳动素养分']
    ws.append(headers)

    # 写入表格数据
    for student_id, student_name in students.items():
        if student_id == student_key:
            continue  # 跳过当前用户的数据

        row_data = [student_id, student_name]
        for i in range(1, 5):
            key = f'score_{student_id}_{i}'
            score = form_data.get(key)
            row_data.append(score)
        ws.append(row_data)

    # 保存工作簿为 XLSX 文件
    wb.save(file_path)
    wb.close()
