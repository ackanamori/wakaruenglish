import re
from flask import Flask, render_template, redirect, request, session
from flask.templating import render_template
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "sunabaco"  #loging

@app.route('/wordlist')
def wordlist():
   #データベースに接続

    conn = sqlite3.connect('wakaen.db')
    c = conn.cursor()  #データベースに接続して処理を開始しますという意味
    c.execute("select word_id,past,voice_past FROM words")
    #select文でとってきた内容を配列に渡す
    wordlist = []
    for row in c.fetchall():  #row は変数名にc.fetchallを入れていく
        wordlist.append({"word_id": row[0], "past": row[1],"voice_past": row[2]})  #辞書型で入れていく後から使いやすい
    #dbとの接続を終了   
    c.close()
    print(wordlist)
    return render_template('miki_test.html',html_wordlist=wordlist)

#404画面
@app.errorhandler(404)
def errorhandler(error):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)