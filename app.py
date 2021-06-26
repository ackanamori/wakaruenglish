import re
from flask import Flask, render_template, redirect, request, session
from flask.templating import render_template
import random
import sqlite3
app = Flask(__name__)

# Flask では標準で Flask.secret_key を設定すると、sessionを使うことができます。この時、Flask では session の内容を署名付きで Cookie に保存します。
app.secret_key = 'wakaen'


# -----------------トップ-----------------------
@app.route('/index')
def index():
    return render_template('index.html')

# ------------------登録----------------------
# GET  /register => 登録画面を表示
# POST /register => 登録処理をする

@app.route('/entry')
def entry():
    return render_template('entry.html')

@app.route('/entry',methods=["POST"])
def entry_post():
    #  登録ページを表示させる

        # 登録ページで登録ボタンを押した時に走る処理
        name = request.form.get("name")
        password = request.form.get("password")
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        # 課題4の答えはここ
        c.execute("insert into persons values(null, ?,?)",(name, password))
        conn.commit()
        conn.close()
        return redirect('/login')

# -------------------ログイン----------------------
@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login_post():
        name = request.form.get("member_name")
        password = request.form.get("member_password")

        # ブラウザから送られてきた name ,password を userテーブルに一致するレコードが
        # 存在するかを判定する。レコードが存在するとuser_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        c.execute("select user_id from persons where user_name = ? and password = ?", (name, password) )
        user_id = c.fetchone()
        conn.close()
        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html")
        else:
            session['user_id'] = user_id[0]
            print('user_id[0]')
            user_id=user_id[0]
            print('user_id')
            return redirect("/mypage")      


@app.route("/mypage")
def mypage():
    if "user_id" in session:
        user_id= session['user_id']
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        c.execute("SELECT user_name FROM persons WHERE user_id = ?",(user_id, ))  
        user_name=c.fetchone()
        print('user_name',user_name)


        c.execute("SELECT word_no,result_ok,result_ng FROM results WHERE user_id = ?",(user_id, ))  
        user_results = c.fetchall()
        print('user_results',user_results)

        result_ok=1
        c.execute("SELECT count(result_ok) from results WHERE user_id = ? and result_ok=?",(user_id,result_ok))  
        user_ok_num= c.fetchall()

        print('user_results',user_ok_num)
        
        c.close()    
        return render_template('mypage.html',html_user_ok_num=user_ok_num, html_user_name = user_name)
    

@app.route("/wordlist")
def wordlist():
   
    return render_template('wordlist.html')

@app.route("/exam")
def exam():
   
    return render_template('exam.html')

@app.route("/result")
def result():
   
    return render_template('result.html')

if __name__ == "__main__":
    app.run(debug=True)