import os

from flask import Flask, request, render_template, jsonify
import xlrd

from datetime import datetime

app = Flask(__name__, template_folder='./templates')

import sqlite3


port =input('输入服务端口：')


def remove_extension(filepath):
    filename = os.path.basename(filepath)  # 获取文件名
    base, ext = os.path.splitext(filename)  # 分离文件名和扩展名
    if ext == '.db':  # 如果扩展名是 .db
        return base  # 返回没有扩展名的文件名
    else:
        return filepath  # 如果不是 .db 扩展名，返回原路径


def get_scores(student_id):
    try:
        # 连接到数据库文件
        conn = sqlite3.connect('scores.db')
        cursor = conn.cursor()

        # 执行查询语句，获取指定学生的所有成绩
        cursor.execute(f"SELECT 语文, 数学, 英语, 政治, 历史, 物理, 化学, 生物, 地理 FROM 学生成绩 WHERE 学生ID = ?",
                       (student_id,))
        scores = cursor.fetchone()

        # 关闭数据库连接
        conn.close()

        return scores
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

    # 示例：获取学生ID为12345的所有成绩


'''
student_id = 12345
scores = get_scores(student_id)
if scores:
    for i, score in enumerate(scores, start=1):
        print(f"{i}. {score}")  # 这里假设成绩字段是数值类型，直接打印出来。如果成绩字段是文本类型，你可能需要修改打印语句。    
else:
    print("没有找到该学生的成绩。")


'''


# 创建 SQLite 数据库连接

def create_db_connection(dbName):
    return sqlite3.connect(dbName + '.db')


# 创建 log 表  
def create_log_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS log    
             (ip TEXT, method TEXT, path TEXT, time TEXT)''')
    conn.commit()


def create_scores_table(conn):
    conn.execute('''CREATE TABLE 学生成绩 (  
    学生ID INT PRIMARY KEY,  
    语文 INT,  
    数学 INT,  
    英语 INT,  
    政治 INT,  
    历史 INT,  
    物理 INT,  
    化学 INT,  
    生物 INT,  
    地理 INT  
);''')
    conn.commit()


@app.before_request
def log_request():
    # 获取请求的 IP 地址、方法、路径和时间戳  
    ip = request.remote_addr
    method = request.method
    path = request.path
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with create_db_connection('log') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS log    
                      (ip TEXT, method TEXT, path TEXT, time TEXT)''')
        conn.execute("INSERT INTO log (ip, method, path, time) VALUES (?, ?, ?, ?)", (ip, method, path, time))
        conn.commit()


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/search')
def search():
    return render_template('search.html')




@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/api/excel')
def process_excel():
    name = request.args.get('name')
    try:
        workbook = xlrd.open_workbook(name)
    except Exception:
        return 'excel err ' + name, 400
    return name, 200


@app.route('/upload')
def up_load():
    return render_template('upload.html')



@app.route('/api/upload', methods=['POST'])
def upload_file():
    # 获取上传的文件
    try:

        from flask import request
        file = request.files['file']

    # 获取表单提交的参数
        grade = request.form.get('grade')
        academic_year = request.form.get('academic_year')
        session = request.form.get('session')
        fileName = request.form.get('fileName')

        # 创建保存路径
        save_path = f"Data/Excel/{academic_year}/{grade}/{session}"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

            # 保存文件到指定路径
        try:
            file.save(os.path.join(save_path, f"{fileName}.xlsx"))
        except:return '文件保存错误'
        ###




        import pandas as pd
        # 创建SQLite3数据库和表

        # 定义路径
        path = "Data/DB/{}/{}".format(academic_year, grade)

        # 创建路径
        print(academic_year, grade, session)
        save_path = f"Data/DB/{academic_year}/{grade}/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        try:
            conn_c = sqlite3.connect("Data/DB/{}/{}/{}.db".format(academic_year, grade, session))
        except:return '数据表错误'
        c = conn_c.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scores (
                name VARCHAR(255) NOT NULL,
                student_id VARCHAR(255) NOT NULL PRIMARY KEY,
                gender VARCHAR(255) NOT NULL,
                class_level VARCHAR(255) NOT NULL,
                chinese FLOAT,
                math FLOAT,
                english FLOAT,
                politics FLOAT,
                history FLOAT,
                biology FLOAT,
                geography FLOAT,
                chemistry FLOAT,
                physics FLOAT,
                music FLOAT,
                information_tech FLOAT,
                art FLOAT,
                sports FLOAT,
                total_score FLOAT)''')
        conn_c.commit()
        conn_c.close()
        print('sql done')
        # 读取Excel数据并插入到SQLite3数据库中
        try:
            df = pd.read_excel(f"Data/Excel/{academic_year}/{grade}/{session}/{fileName}.xlsx")
        except:return 'excel错误'
        count = 0

        for index, row in df.iterrows():
            name = row['姓名']
            gender = row['性别']
            class_level = row['班别']# 根据实际字段名替换“性别”
            exam_id = row['考生号']
            chinese = row['语文']
            math = row['数学']
            english = row['英语']
            politics = row['政治']
            history = row['历史']
            physics = row['物理']
            chemistry = row['化学']
            biology = row['生物']
            geography = row['地理']
            music = row['音乐']
            information_tech = row['信息技术']
            art = row['美术']
            sports = row['体育']
            total_score = row['总分']


            conn = sqlite3.connect("Data/DB/{}/{}/{}.db".format(academic_year, grade, session, ))
            c = conn.cursor()
            c.execute("INSERT INTO scores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?, ?, ?)",
                      (name, exam_id, gender, class_level, chinese, math, english, politics, history, biology, geography,
                       chemistry, physics, music, information_tech, art, sports, total_score))
            conn.commit()
            count += 1

            print(f"Inserted {count} rows...")  # 更新进度信息，这里仅用于示例，实际中可以更详细地处理并发和错误等。
            conn.close()
        return '成功'
    except:
        os.remove(f"Data/Excel/{academic_year}/{grade}/{session}/{fileName}.xlsx")
        os.remove("Data/DB/{}/{}/{}.db".format(academic_year, grade, session))

        return '错误'



@app.route('/api/getAcademic_year')
def getAcademic_year():
    os.listdir('./Data/DB/')
    print(os.listdir('./Data/DB/'))
    return os.listdir('./Data/DB/')

@app.route('/api/getGrade')
def getGrade():
    academic_year=request.args.get('academic_year')
    return os.listdir(f'./Data/DB/{academic_year}')


import os


def remove_extension_from_all(file_paths):
    result = []
    for filepath in file_paths:
        filename = os.path.basename(filepath)  # 获取文件名
        base, ext = os.path.splitext(filename)  # 分离文件名和扩展名
        print(base)
        if ext == '.db':  # 如果扩展名是 .db
            print(result)

            result.append(base)  # 将没有扩展名的文件名添加到结果列表中
            print(result)

    print(result)
    return result


@app.route('/api/getSession')
def getSession():
    academic_year = request.args.get('academic_year')
    grade=request.args.get('grade')

    filepath = os.listdir(f'./Data/DB/{academic_year}/{grade}')
    filepath = remove_extension_from_all(filepath)
    return filepath


@app.route('/api/search')
def get_scores_api():
    academic_year = request.args.get('academic_year')
    grade = request.args.get('grade')
    session = request.args.get('session')
    studentID = str( request.args.get('chineseid'))
    print(academic_year, grade, session,studentID)

    conn = sqlite3.connect("Data/DB/{}/{}/{}.db".format(academic_year, grade, session))
    c=conn.cursor()
    c.execute("SELECT * FROM scores WHERE exam_id={}".format(studentID))
    print(c.execute("SELECT * FROM scores WHERE exam_id={}".format(studentID)))
    return c.fetchall()





@app.route('/api/add_scores', )
def add_scores_api():
    academic_year = request.form.get('academic_year')
    grade = request.form.get('grade')
    session = request.form.get('session')
    studentID = request.args.get('studentID')
    chinese = request.args.get('chinese')
    math = request.args.get('math')
    english = request.args.get('english')
    politics = request.args.get('politics')
    history = request.args.get('history')
    physics = request.args.get('physics')
    chemistry = request.args.get('chemistry')
    biology = request.args.get('biology')
    geography = request.args.get('geography')


@app.route('/scores_list')
def scores_list():
    try:

        academic_year = request.args.get('academic_year')
        grade = request.args.get('grade')
        session = request.args.get('session')
        studentID = str(request.args.get('examid'))
        print(academic_year, grade, session, studentID)
    except:return  render_template('search.html')

    try:
        conn = sqlite3.connect("Data/DB/{}/{}/{}.db".format(academic_year, grade, session))
        c = conn.cursor()
        query = "SELECT * FROM scores WHERE student_id=?;"
        c.execute(query, (studentID,))
        results = c.fetchall()
        print(results)  # 打印整个查询结果
        c.close()
        conn.close()


        try:
            return render_template('scoreslist.html', results=results[0]), 200  # 返回查询结果，可能需要进行进一步处理或格式化
        except: return render_template('search.html')


    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "查找错误", 500  # 返回一个错误响应和状态码500




if __name__ == '__main__':
    app.run(debug=True ,port=port)
