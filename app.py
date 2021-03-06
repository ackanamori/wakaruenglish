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
@app.route('/')
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
        c.execute("select user_name from persons where user_name = ?" ,(name,))
        user_name_ok = c.fetchone()
        # print(user_name_ok)
        # print(allname)
        if user_name_ok is None:
            # conn = sqlite3.connect('wakaen.db')
            # c = conn.cursor()
            c.execute("INSERT into persons values(null, ?,?)",(name, password))
            conn.commit()

            c.execute("SELECT user_id from persons WHERE  user_name = ?" ,(name,))
            user_id_tap = c.fetchone()
            user_id=user_id_tap[0]
            mkrecord_result_ck_tap = make_user_record(user_id)
            # print('mkrecord_result_ck_tap')
            mkrecord_result_ck = mkrecord_result_ck_tap
            c.close()
            if mkrecord_result_ck == 1:
                # 登録したことを知らせる
                # login_message = "登録が完了しました！"
                return render_template("jump.html")
            else:
                return redirect('/')
        else:
            entry_ER = "このIDは使用できません"
            # print("sasa")
            # 登録失敗すると、登録画面に戻す
            return render_template("entry.html",html_entry_ER = entry_ER)
                  

        #dbに入力
        # c.execute("insert into persons("name", "password") select user_name,password from persons where not exists(select user_name from persons where user_name = "name" )")
        # c.execute("INSERT into persons values(null, ?,?)",(name, password))
        
def make_user_record(user_id): 
    #セッションのユーザーidの値を、変数user_idに代入
    mkrecord_user_id = user_id
    conn = sqlite3.connect('wakaen.db')
    c = conn.cursor()
    #１user_id が一致するレコードがあればresults_idの数を数える
    c.execute("SELECT COUNT(results_id) FROM results WHERE user_id = ?", (mkrecord_user_id,))
    result_record_tap = c.fetchall()

    #result_record_tap はタプル型の配列 [(0,)]となるため、数字だけにしてresult_recordに入れる
    result_record = result_record_tap[0][0]
       
    #２もしレコードがなければ作る
    level_no = 7
    if result_record == 0:
        for word_no in range(1, 79):
            # print(word_no)
            c.execute("INSERT INTO results VALUES(null, ?,?,?,?,?)",(mkrecord_user_id, level_no,word_no,"notyet.png",0))
            conn.commit()
        mkrecord_result=1
        return(mkrecord_result)
    #もしあれば処理なし
    else:
        mkrecord_result=0    
        return(mkrecord_result)        
        

# -------------------ログイン----------------------
@app.route("/login")
def login():
    login_ER=""
    return render_template('login.html',html_login_ER=login_ER)

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
            login_ER = "IDかパスワードが間違っています"
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html",html_login_ER=login_ER)
        else:
            session['user_id'] = user_id[0]
            return redirect("/mypage")      


@app.route("/mypage")
def mypage():
    #セッションにユーザーidがあるかを確認
    if "user_id" in session:
        #セッションのユーザーidの値を、変数user_idに代入
        user_id = session['user_id']
        # print("mypage/user_id:",user_id)
        #dbに接続する
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        #personsテーブルからuser_idの人のuser_nameを取得し、変数user_nameに代入
        c.execute("SELECT user_name FROM persons WHERE user_id = ?",(user_id, ))  
        user_name=c.fetchone()
        c.close()  
        
        # #user_idから、wordsとresultsを外部結合したリスト抽出
        # wordlist = user_word_results(user_id)

        ###削除
        # #wordsテーブルにresultsテーブルを外部結合。resultsはresults_id、wordsはword_idをキー。単語一覧と結果を取得し変数配列wordlistに代入
        # c.execute("SELECT id,voice_past,past,result_ok,result_ng FROM words LEFT OUTER JOIN results ON  results.word_no = words.word_id") 
        # # wordlist = []
        # # for row in c.fetchall():  #row は変数名にc.fetchallを入れていく
        # #     wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3], "result_ng": row[4]}) 
        # # # print(wordlist)
        ###削除

        #正解数をカウント   
        user_ok_num = count_correct(user_id)
  
        return render_template('mypage.html', html_user_name = user_name, html_user_ok_num=user_ok_num)
    else:
        return redirect("/") 

def user_word_results(user_id):
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        #wordsテーブルにresultsテーブルを外部結合。resultsはresults_id、wordsはword_idをキー。単語一覧と結果を取得し変数配列wordlistに代入
        c.execute("SELECT id,voice_past,past,result_ok,result_ng,present,jp,past_participle FROM words LEFT OUTER JOIN results ON  results.word_no = words.word_id and results.user_id=?",(user_id,)) 
        wordlist = []
        for row in c.fetchall(): 
            wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3], "result_ng": row[4], "present": row[5], "jp": row[6], "past_participle": row[7]}) 
        c.close()  
        # print("user_word_results/wordlist:",wordlist)  
        return(wordlist)

@app.route("/wordlist")
def wordlist():
    if "user_id" in session:
        user_id= session['user_id']
        # conn = sqlite3.connect('wakaen.db')
        # c = conn.cursor()

        #正解数をカウント   
        user_ok_num = count_correct(user_id)
        #user_idから、wordsとresultsを外部結合したリスト抽出
        wordlist = user_word_results(user_id)
        # print(wordlist)
        # #wordsテーブルにresultsテーブルを外部結合。resultsはresults_id、wordsはword_idをキー。単語一覧と結果を取得し変数配列wordlistに代入
        # c.execute("SELECT id,voice_past,past,result_ok,result_ng,present,jp FROM words LEFT OUTER JOIN results ON  results.word_no = words.word_id and results.user_id=?",(user_id,)) 
        # wordlist = []
        # for row in c.fetchall(): 
        #     wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3], "result_ng": row[4], "present": row[5], "jp": row[6]}) 


        # c.close()    
        return render_template('wordlist.html',html_wordlist=wordlist,html_user_ok_num=user_ok_num)
    else:
        return redirect("/login") 

#正解数をカウント
def count_correct(user_id):  
        result_ok = "correctanswer.png"
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        c.execute("SELECT count(result_ok) FROM results WHERE user_id = ? and result_ok=?",(user_id,result_ok))  
        user_ok_num_tap=c.fetchall()
        user_ok_num=user_ok_num_tap[0][0]
        c.close()
        # print("count_correct/user_ok_num:",user_ok_num)
        return(user_ok_num)


#ユーザーの正解していない番号一覧取得
def notclear_exam_no(user_id):
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        result_ok= "correctanswer.png"

        #resultsテーブルから、user_id一致、result_okがnullの場合と正解でない場合を取得
        c.execute("SELECT word_no FROM results WHERE user_id = ? and (result_ok = ?)",(user_id,result_ok)) 
        #正解しているword番号をすべてremain_exam_noにリストで入れる
        clear_exam_no = []
        for row in c.fetchall(): 
            clear_exam_no.append(row[0]) 
        #すべてのWord番号をall_exam_noに入れ、残っているword番号を notclear_exam_noに入れる
        all_exam_no = list(range(1, 79))
        # print("notclear_exam_no/all_exam_no:",all_exam_no)

        notclear_exam_no = set(all_exam_no) - set(clear_exam_no) 
        # print("notclear_exam_no/notclear_exam_no:",notclear_exam_no)

        c.close() 
  
        return notclear_exam_no

def word_no_record(exam_word_no,user_id):
        # conn = sqlite3.connect('wakaen.db')
        # c = conn.cursor()
        # #word一覧を取得
        # c.execute("SELECT id,voice_past,past,result_ok,result_ng,jp,present,past_participle FROM words LEFT OUTER JOIN results ON  results.word_no = words.word_id") 
        # wordlist = []
        # for row in c.fetchall(): 
        #     wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3],"result_ng": row[4], "jp": row[5],  "present": row[6], "past_participle": row[7]}) 
        # print("word_no_record/exam_word_no:",exam_word_no)
        wordlist=user_word_results(user_id)
        exam_word_no_index = exam_word_no -1
        exam_word = wordlist[exam_word_no_index]
        # print("word_no_record/exam_word:",exam_word)
        return exam_word

#テストページ
@app.route("/exam")
def exam():
    if "user_id" in session:
        user_id= session['user_id']
        
        user_ok_num = count_correct(user_id)
        if user_ok_num ==78:
            return render_template('examcomplete.html')
        else:
            pass
        
        #ユーザーが正解していないリストを取得
        notclear_exam_no_list = notclear_exam_no(user_id)
        #ランダムで1件選ぶ
        exam_word_no_list = random.sample(notclear_exam_no_list,1)
        exam_word_no = exam_word_no_list[0]
        # print("exam/exam_word_no:",exam_word_no)
        #実施するword番号から、wordすべて取得        
        exam_word = word_no_record(exam_word_no,user_id)
        #正解数をカウント   
        user_ok_num = count_correct(user_id)
        return render_template('exam.html',html_user_ok_num=user_ok_num,html_exam_word = exam_word)
    else:
        return redirect("/login") 

#結果判定ページ
@app.route("/result",methods=["POST"])
def result():
   
    user_id = session['user_id']
    word_no = int(request.form.get("word_id"))
    # print("ゲットしたWord_no",word_no)
    level_no = 7

    conn = sqlite3.connect('wakaen.db')
    c = conn.cursor()
    # #１user_id word_idが一致するレコードがあればresults_idの数を数える
    # c.execute("SELECT COUNT(results_id) FROM results WHERE user_id = ? and word_no = ?", (user_id, word_no))
    # result_record_tap = c.fetchall()
    # #result_record_tap はタプル型の配列 [(0,)]となるため、数字だけにしてresult_recordに入れる
    # result_record = result_record_tap[0][0]

    # #２もしレコードがなければ作る
    # if result_record == 0:
    #     c.execute("INSERT INTO results VALUES(null, ?,?,?,?,?)",(user_id, level_no,word_no,"notyet.png",0))
    #     conn.commit()
    # #もしあれば処理なし
    # else:
    #      pass
    
    #３上記２で作ったもしくは存在しているレコードの主キーであるresults_idを取得。結果書き込みの際に使用する
    c.execute("SELECT results_id FROM results WHERE user_id = ? and word_no = ?", (user_id, word_no) )
    target_result_tap = c.fetchone()
    target_result = target_result_tap[0]

    #４ユーザのインプットした値を取得
    input_answer = request.form.get("input_answer")
    #５答えのユニットを取得

    exam_word = word_no_record(word_no,user_id)
    # print(exam_word)

    # print("input_answer=",input_answer)
    #６答えを比較
    answer_word = exam_word['past']
    # print("answer_word=",answer_word)


    #７上記３で取得したresults_idのレコードで、間違い回数を取得
    c.execute("SELECT result_ng FROM results WHERE user_id = ? and word_no = ?", (user_id, word_no) )
    result_ng_tap = c.fetchone()
    result_ng = result_ng_tap[0]

    #正解の場合
    if input_answer == answer_word:
        result_ok = "correctanswer.png"
        # print("OK",result_ok,target_result)
        c.execute("UPDATE results SET result_ok = ?  WHERE results_id = ? ", (result_ok,target_result))
        conn.commit()
        result_text ="正解"
        user_ok_num = count_correct(user_id)
        if user_ok_num ==78:
            return render_template('examcomplete.html')
        else:
            pass
        
    #間違っている場合
    else:
        result_ng = result_ng + 1
        result_ok = "incorrectanswer.png"
        # print("NG",result_ok,result_ng,target_result)
        c.execute("UPDATE results SET result_ok = ?,result_ng = ?  WHERE results_id = ?", (result_ok,result_ng,target_result))
        conn.commit()
        result_text ="不正解"

    exam_word=word_no_record(word_no,user_id)

    c.execute("SELECT id,voice_past,past,result_ok,result_ng,jp,present,past_participle FROM words LEFT OUTER JOIN results ON  results.word_no = words.word_id") 
    wordlist = []
    for row in c.fetchall(): 
        wordlist.append({"word_id": row[0], "voice_past": row[1], "past": row[2], "result_ok": row[3],"result_ng": row[4], "jp": row[5],  "present": row[6], "past_participle": row[7]}) 
      
    c.close()  
    #正解数をカウント   
    user_ok_num = count_correct(user_id)
    # print(exam_word)
    return render_template('result.html',html_user_ok_num=user_ok_num,html_exam_word=exam_word,html_result_text=result_text,html_input_answer=input_answer)

@app.route("/reset")
def reset():
    if "user_id" in session:
        user_id= session['user_id']  
        result_ok = "notyet.png"
        result_ng = 0
        conn = sqlite3.connect('wakaen.db')
        c = conn.cursor()
        c.execute("UPDATE results SET result_ok = ?,result_ng = ?  WHERE user_id = ?", (result_ok,result_ng,user_id))
        conn.commit()
      
        #personsテーブルからuser_idの人のuser_nameを取得し、変数user_nameに代入
        c.execute("SELECT user_name FROM persons WHERE user_id = ?",(user_id, ))  
        user_name=c.fetchone()

        #正解数をカウント   
        user_ok_num = count_correct(user_id)
        c.close()   
        return render_template('mypage.html',html_user_name = user_name, html_user_ok_num=user_ok_num)
    else:
        return redirect('login')

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect('login')

#404画面
@app.errorhandler(404)
def errorhandler(error):
    return render_template('404.html')

if __name__ == "__main__":
    app.run()