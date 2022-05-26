from flask import Flask, render_template, redirect, request,session
from flask_login import UserMixin,LoginManager, login_required , login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from datetime import timedelta
from sqlalchemy import false
from werkzeug.security import check_password_hash, generate_password_hash

import os


#appの作成
app = Flask(__name__)
#データベースの作成
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todo.db"
#session情報の暗号化
app.config["SECRET_KEY"]=os.urandom(24)

#flask_bootstrapのインスタンス化
bootstrap = Bootstrap(app)

#dbの作成
db = SQLAlchemy(app)

#ログインマネージャーとappの紐づけ
login_manager = LoginManager()
login_manager.init_app(app)

#認証ユーザーの呼び出し方を定義する
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    username = db.Column(db.String(20),nullable = False)
    password = db.Column(db.String(20), nullable =False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    title = db.Column(db.String(20), nullable = False)
    body = db.Column(db.String(20), nullable = False)
    duedate = db.Column(db.String(20), nullable = False)
    ownerid = db.Column(db.Integer, nullable = False)


@app.route("/", methods = ["GET"])
def index():
    # ログイン状態だったら
    if current_user.is_authenticated:
        return redirect("/top")

    else:
        return redirect("/login")



@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #userインスタンスの作成。パスワードは"sha256"メソッドでハッシュ化
        user = User(username = username, password = generate_password_hash(password, method="sha256"))
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    else:
        return render_template("signup.html")


@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username = username).first()
    
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

@app.route("/logout")
def logout():
    logout_user()

    return redirect("/")


@login_required
@app.route("/top")
def top():
    todos = Todo.query.filter_by(ownerid = current_user.get_id())

    if todos != []:
        return render_template("top.html", todos = todos)

    else:
        return render_template("top.html")


@login_required
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        title = request.form.get("title")
        body = request.form.get("body")
        duedate = request.form.get("duedate")

        todo = Todo(title = title, body = body, duedate = duedate, ownerid = current_user.get_id())
     
        db.session.add(todo)
        db.session.commit()

        return redirect("/top")







