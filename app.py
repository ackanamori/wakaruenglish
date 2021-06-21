import re
from flask import Flask, render_template, redirect, request, session
from flask.templating import render_template
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "sunabaco"  #loging


@app.route('/')
def hello_world():
    return 'Hello_world'


@app.route('/hello/<text>')
def hello(text):
    return text + "さんこんにちは"


@app.route('/yoho')
def yoho():
    return 'yoho'


@app.route('/top')
def top():
    return render_template('index.html')


@app.route('/index')
def index():
    name = "KAI"
    age = 17
    address = "New York"
    return render_template('temptest.html',
                           html_name=name,
                           html_age=age,
                           html_address=address)


@app.route('/weather')
def weather():

    weather_list = ['☀', '☁', '☂']
    today_weather = weather_list[random.randint(0, 2)]
    print(today_weather)
    return render_template('weather.html', html_weather=today_weather)


#404画面
@app.errorhandler(404)
def errorhandler(error):
    return render_template('404.html')


@app.route('/dbtest')
def dbtest():
    #データベースに接続

    conn = sqlite3.connect('flask.db')
    c = conn.cursor()  #データベースに接続して処理を開始しますという意味
    c.execute("select name,age,address FROM staff WHERE  id=2")
    #select文でとってきた内容を配列に渡す
    userinfo = c.fetchone()
    #dbとの接続を終了
    c.close()
    print(userinfo)
    return render_template('dbtest.html', html_staffinfo=userinfo)


#タスク追加画面
@app.route('/add')  #method="GETが省略されている")
def add():
    if "member_id" in session:
        return render_template('add.html')  #セッションがあれば処理
    else:
        return redirect("/login")  #セッションがなければログイン画面にリダイレクト


#タスク追加処理
@app.route('/add', methods=["POST"])
def addPost():
    member_id = session["member_id"][0]
    task = request.form.get("task")
    conn = sqlite3.connect('task.db')
    c = conn.cursor()
    c.execute("INSERT INTO task VALUES(null,?,?)", (task,member_id))
    conn.commit()
    c.close()
    return redirect('/list')


#タスク一覧表示
@app.route('/list')
def list():
    if "member_id" in session:
        member_id =session["member_id"][0]
        task = request.form.get("task")
        conn = sqlite3.connect('task.db')
        c = conn.cursor()
        c.execute("select id,task FROM task WHERE member_id = ?",(member_id,))
        task_list = []

        #select文でとってきた内容を配列に渡す
        task_list = []  #task_listという変数を配列指定
        for row in c.fetchall():  #row は変数名にc.fetchallを入れていく
            task_list.append({"id": row[0], "task": row[1]})  #辞書型で入れていく後から使いやすい
        c.close()
        return render_template('task_list.html', html_tasklist=task_list)
    else:
        return redirect("/login")  #セッションがなければログイン画面にリダイレクト


#タスク修正　一件画面処理
@app.route('/edit/<int:id>')
def edit(id):
    if "member_id" in session:
        conn = sqlite3.connect('task.db')
        c = conn.cursor()
        c.execute("SELECT task FROM task WHERE id = ?",
              (id, ))  #まだわからないものは？でおいておいて、（変数,）タプル型
        task = c.fetchone()
        c.close()
        #存在しないIDが入力されたときの対策　なければlist画面を表示
        if task is None:
            return redirect('/list')
        else:
            # item = {"id":id,"task":task}  この書き方だとタプル型になるので
            item = {"id": id, "task": task[0]}
            return render_template('edit.html', html_task=item)
    else:
        return redirect("/login")  #セッションがなければログイン画面にリダイレクト


#タスク修正　リスト一覧画面処理
@app.route('/edit', methods=["POST"])
def editPost():
    id = request.form.get("id")
    print(type(id))
    task = request.form.get("task")
    conn = sqlite3.connect('task.db')
    c = conn.cursor()
    c.execute("UPDATE task SET task = ? WHERE id = ?", (task, id))
    conn.commit()
    c.close()
    return redirect("/list")


#タスクリスト削除
@app.route('/delete/<int:id>')
def delete(id):
    if "member_id" in session:

        conn = sqlite3.connect('task.db')
        c = conn.cursor()
        c.execute("DELETE FROM task WHERE id = ?", (id, ))
        conn.commit()
        c.close()
        return redirect("/list")
    else:
        return redirect("/login")  #セッションがなければログイン画面にリダイレクト


#登録画面
@app.route('/regist')
def regist():
    return render_template('regist.html')


#登録処理
@app.route('/regist', methods=["POST"])
def addregist():
    name = request.form.get("member_name")
    password = request.form.get("member_password")
    conn = sqlite3.connect('task.db')
    c = conn.cursor()
    c.execute("INSERT INTO member VALUES(null,?,?)", (name, password))
    conn.commit()
    c.close()
    return "登録完了"
    # return redirect('/regist')


#ログイン画面
@app.route('/login')
def login():
    return render_template('login.html')


#ログイン処理
@app.route('/login', methods=["POST"])
def login_post():
    name = request.form.get("member_name")
    password = request.form.get("member_password")
    conn = sqlite3.connect('task.db')
    c = conn.cursor()
    c.execute("select id FROM member WHERE name = ? AND password = ?",
              (name, password))
    member_id = c.fetchone()
    c.close()
    if member_id is None:
        return render_template("login.html")
    else:
        session["member_id"] = member_id
        return redirect('/list')

@app.route('/logout')
def logout():
    session.pop("member_id",None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)