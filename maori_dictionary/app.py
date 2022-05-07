from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from pathlib import Path
from datetime import datetime
import smtplib
import ssl
from smtplib import SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "Duckyweu"
DATABASE = "/Maori Dictionary/database/dictionary.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(Path.cwd())
        print(db_file)
        print(e)
    return None


def render_category_list():
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT * FROM category"
    cur.execute(query)

    category_list = cur.fetchall()
    con.close()
    return category_list


@app.route('/')
def render_home():
    return render_template("home.html", category_list=render_category_list(), logged_in=is_logged_in())


@app.route('/fulldict')
def render_dictionary():
    con = create_connection(DATABASE)
    query = "SELECT * FROM dictionary"
    cur = con.cursor()
    cur.execute(query)

    dictionary_list = cur.fetchall()
    con.close()
    return render_template("full_dictionary.html", dictionary_list=dictionary_list, logged_in=is_logged_in(),
                           category_list=render_category_list())


@app.route('/category/<id>')
def render_category(id):
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = """SELECT c.category_name, d.maori, d.english, d.image_name, d.id
               FROM dictionary d
               JOIN category c on c.id = d.category_id
               WHERE d.category_id = ?"""
    cur.execute(query, (id,))

    category_words = cur.fetchall()
    print(category_words)
    con.close()
    return render_template("category.html", category_words=category_words, logged_in=is_logged_in(),
                           category_list=render_category_list())


def is_logged_in():
    if session.get('email') is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


@app.route('/signup', methods=["POST", "GET"])
def render_signup():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        print(request.form)
        fname = request.form.get("fname").strip().title()
        lname = request.form.get("lname").strip().title()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        password2 = request.form.get("confirm_password")
        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')
        if len(password) < 8:
            return redirect('/signup?error=Passwords+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)
        query = "INSERT INTO user_details (first_name, last_name, email, password) VALUES (?,?,?,?)"
        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            redirect('/signup?error=Email+is+already+used')
        con.commit()
        con.close()
        return redirect('/login')
    error = request.args.get('error')

    if error == None:
        error = ""

    return render_template("signup.html", error=error, logged_in=is_logged_in())


@app.route('/login', methods=["POST", "GET"])
def render_login():
    if is_logged_in():
        print(is_logged_in())
        return redirect('/')
    if request.method == "POST":
        print(request.form)
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        query = """SELECT id, first_name, password FROM user_details WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()

        try:
            customer_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect('/login?error=Email+invalid+or+password+incorrect')

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + '?error=Email+invalid+or+Password+incorrect')

        session['email'] = email
        session['customer_id'] = customer_id
        session['first_name'] = first_name
        print(session)
        return redirect('/')

    return render_template("login.html", logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect(request.referrer + '?message=see+you+later')


if __name__ == '__main__':
    app.run()
