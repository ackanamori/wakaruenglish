import re
from flask import Flask, render_template, redirect, request, session
from flask.templating import render_template
import random
import sqlite3

from werkzeug.datastructures import Range
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
        c.execute("INSERT into persons values(null, ?,?)",(name, password))
        conn.commit()
        c.close()
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
        c.execute("SELECT user_id FROM persons where user_name = ? and password = ?", (name, password) )
        user_id = c.fetchone()
        c.close()
        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html")
        else:
            session['user_id'] = user_id[0]
            return redirect("/mypage")      


@app.route("/mypage")
def mypage():
    #セッションにユーザーidがあるかを確認
    if "user_id" in session:
        #セッションのユーザーidの値を、変数user_idに代入
        user_id = session['user_id']
        print(user_id)

        #dbに接続する
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()

        #personsテーブルからuser_idの人のuser_nameを取得し、変数user_nameに代入
        c.execute("SELECT user_name FROM persons WHERE user_id = ?",(user_id, ))  
        user_name=c.fetchone()

        #wordsテーブルにresultsテーブルを外部結合。resultsはresults_id、wordsはword_idをキー。単語一覧と結果を取得し変数配列wordlistに代入
        c.execute("SELECT id,voice_past,past,result_ok,result_ng FROM words LEFT OUTER JOIN results ON  results.results_id = words.word_id") 
        wordlist = []
        for row in c.fetchall():  #row は変数名にc.fetchallを入れていく
            wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3], "result_ng": row[4]}) 
        print(wordlist)

        #正解数をカウント        
        result_ok = "correctanswer.png"
        c.execute("SELECT count(result_ok) FROM results WHERE user_id = ? and result_ok=?",(user_id,result_ok))  
        user_ok_num= c.fetchall()

        c.close()    
        return render_template('mypage.html', html_user_name = user_name, html_user_ok_num=user_ok_num[0],html_wordlist=wordlist)
    else:
        return redirect("/login") 

@app.route("/wordlist")
def wordlist():
    if "user_id" in session:
        user_id= session['user_id']
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()

        #wordsテーブルにresultsテーブルを外部結合。resultsはresults_id、wordsはword_idをキー。単語一覧と結果を取得し変数配列wordlistに代入
        c.execute("SELECT id,voice_past,past,result_ok,result_ng FROM words LEFT OUTER JOIN results ON  results.results_id = words.word_id") 
        wordlist = []
        for row in c.fetchall(): 
            wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3], "result_ng": row[4]}) 
        c.close()    
        return render_template('wordlist.html',html_wordlist=wordlist)
    else:
        return redirect("/login") 

@app.route("/exam")
def exam():
    if "user_id" in session:
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        user_id= session['user_id']
        result_ok= "correctanswer.png"

        #resultsテーブルから、user_id一致、result_okがnullの場合と正解でない場合を取得
        c.execute("SELECT user_id,word_no,result_ok,result_ng FROM results WHERE user_id = ? and (result_ok <> ? or result_ok is NULL)",(user_id,result_ok)) 

        remain_exam = []
        for row in c.fetchall(): 
            remain_exam.append(row[1]) 

        

        expect_exam =random.sample(remain_exam,2)
        c.close()
  
  
        # for do_exam_no in expect_exam():
        #     c.execute("SELECT word_no,voice_past,past, FROM word WHERE id = ?" ,(do_exam_no,)) 
        #     do_exam = c.fetchone()
        #     print(do_exam)
        
        # result_not_ok=[0,1,2,3,4]
        # exam_word=rsult_not_ok[random.randint(0,2)]
        print("remain_exam",remain_exam)
        print("expect_exam",expect_exam)

  
        return render_template('exam.html')
    else:
        return redirect("/login") 




@app.route("/result")
def result():
   
    return render_template('result.html')

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect('login')

if __name__ == "__main__":
    app.run(debug=True)