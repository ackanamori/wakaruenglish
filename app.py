import re
from flask import Flask, render_template, redirect, request, session
from flask.templating import render_template
import random
import sqlite3

# ――――――――――――――――――――――――――――桜奈―――――――――――――――――――――――――
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
@app.route('/entry',methods=["GET", "POST"])
def register():
    #  登録ページを表示させる
    if request.method == "GET":
        if 'user_id' in session :
            return redirect ('/mypage')
        else:
            return render_template("entry.html")

    # ここからPOSTの処理
    else:
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
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session :
            return redirect("/mypage")    
        else:
            return render_template("login.html")
    else:
        # ブラウザから送られてきたデータを受け取る
        name = request.form.get("member_name")
        password = request.form.get("member_password")

        # ブラウザから送られてきた name ,password を userテーブルに一致するレコードが
        # 存在するかを判定する。レコードが存在するとuser_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        c.execute("select user_id from persons where user_name = ? and password = ?", (name, password) )
        user_id = c.fetchone()
        conn.close()
        # DBから取得してきたuser_id、ここの時点ではタプル型
        print(type(user_id))
        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html")
        else:
            session['user_id'] = user_id[0]
            return redirect("/mypage")        

@app.route("/mypage")
def mypage():
   
    return render_template('mypage.html' )
    

# ―――――――――――――――――――――ここまで―――――――――――――――――――――――――――

if __name__ == "__main__":
    app.run(debug=True)