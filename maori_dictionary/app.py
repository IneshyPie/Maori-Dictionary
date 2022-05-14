import string
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import glob
import os
from datetime import datetime
import smtplib
import ssl
from smtplib import SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "Duckyweu"
DATABASE = "database/dictionary.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
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


def get_image_filename(english_name):
    path_file = f"static\\images\\{english_name}.*"
    print(path_file)
    listing = glob.glob(path_file)
    for filename in listing:
        print(filename)
        return os.path.basename(filename)
    return "noimage.png"

def get_image_filenames(words):
    image_names = []
    for word in words:
        image_names.append(get_image_filename(word[2]))
    return image_names

@app.route('/')
def render_home():
    return render_template("home.html", category_list=render_category_list(), logged_in=is_logged_in(),
                           allow_edit=allow_edit())

#Example of the sql
#SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
#FROM dictionary d
#LEFT JOIN user_details u on d.user_id = u.id
#WHERE
#    maori LIKE '%'
#    AND
#    english LIKE '%'
#    AND
#    level = 5
#ORDER BY date_added DESC LIMIT 20
@app.route('/search/<letter>', methods=["POST", "GET"])
def render_search(letter):
    selected = []
    if request.method == "POST":
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        level = request.form.get("level").strip()
        most_recent = request.form.get("Date-Added").strip()
        print(f"form data: maori: {maori}, english: {english}, level: {level}, most_recent: {most_recent}")
        sql_maori = ""
        sql_english = ""
        sql_level = ""
        con = create_connection(DATABASE)
        cur = con.cursor()
        if maori != "" or english != "" or level != "0" and most_recent == "1":
            if maori != "" and english != "" and level == "0":
                sql_maori = f"{maori}%"
                sql_english = f"{english}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ? AND 
                         english LIKE ?
                         ORDER BY date_added DESC LIMIT 20
                         """
                print(f"case 1 parms: {sql_maori}, {sql_english}")
                try:
                    cur.execute(sql, (sql_maori, sql_english,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english == "" and level != "0":
                sql_maori = f"{maori}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ? AND 
                         level = ?
                         ORDER BY date_added DESC LIMIT 20
                         """
                print(f"case 2 parms: {sql_maori}, {sql_level}")
                try:
                    cur.execute(sql, (sql_maori, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english != "" and level != "0":
                sql_english = f"{english}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         english LIKE ? AND 
                         level = ?
                         ORDER BY date_added DESC LIMIT 20
                         """
                print(f"case 3 parms: {sql_english}, {sql_level}")
                try:
                    cur.execute(sql, (sql_english, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english == "" and level == "0":
                sql_maori = f"{maori}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ?
                         ORDER BY date_added DESC LIMIT 20 
                         """
                print(f"case 4 parms: {sql_maori}")
                try:
                    cur.execute(sql, (sql_maori,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english != "" and level == "0":
                sql_english = f"{english}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         english LIKE ?
                         ORDER BY date_added DESC LIMIT 20
                         """
                print(f"case 5 parms: {sql_english}")
                try:
                    cur.execute(sql, (sql_english,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english == "" and level != "0":
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         level = ?
                         ORDER BY date_added DESC LIMIT 20
                         """
                print(f"case 6 parms: {sql_level}")
                try:
                    cur.execute(sql, (sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english != "" and level != "0":
                sql_maori = f"{maori}%"
                sql_english = f"{english}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                                         FROM dictionary d
                                         LEFT JOIN user_details u on d.user_id = u.id
                                         WHERE 
                                         maori LIKE ? AND
                                         english LIKE ? AND
                                         level = ?
                                         ORDER BY date_added DESC LIMIT 20
                                         """
                print(f"case 7 parms: {sql_maori}, {sql_english}, {sql_level}")
                try:
                    cur.execute(sql, (sql_maori, sql_english, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
        elif maori != "" or english != "" or level != "0" and most_recent == "0":
            if maori != "" and english != "" and level == "0":
                sql_maori = f"{maori}%"
                sql_english = f"{english}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ? AND 
                         english LIKE ?
                         """
                print(f"case 1 parms: {sql_maori}, {sql_english}")
                try:
                    cur.execute(sql, (sql_maori, sql_english,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english == "" and level != "0":
                sql_maori = f"{maori}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ? AND 
                         level = ?
                         """
                print(f"case 2 parms: {sql_maori}, {sql_level}")
                try:
                    cur.execute(sql, (sql_maori, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english != "" and level != "0":
                sql_english = f"{english}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         english LIKE ? AND 
                         level = ?
                         """
                print(f"case 3 parms: {sql_english}, {sql_level}")
                try:
                    cur.execute(sql, (sql_english, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english == "" and level == "0":
                sql_maori = f"{maori}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         maori LIKE ? 
                         """
                print(f"case 4 parms: {sql_maori}")
                try:
                    cur.execute(sql, (sql_maori,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english != "" and level == "0":
                sql_english = f"{english}%"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         english LIKE ?
                         """
                print(f"case 5 parms: {sql_english}")
                try:
                    cur.execute(sql, (sql_english,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori == "" and english == "" and level != "0":
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                         FROM dictionary d
                         LEFT JOIN user_details u on d.user_id = u.id
                         WHERE 
                         level = ?
                         """
                print(f"case 6 parms: {sql_level}")
                try:
                    cur.execute(sql, (sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
            if maori != "" and english != "" and level != "0":
                sql_maori = f"{maori}%"
                sql_english = f"{english}%"
                sql_level = f"{level}"
                sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                                         FROM dictionary d
                                         LEFT JOIN user_details u on d.user_id = u.id
                                         WHERE 
                                         maori LIKE ? AND
                                         english LIKE ? AND
                                         level = ?
                                         """
                print(f"case 7 parms: {sql_maori}, {sql_english}, {sql_level}")
                try:
                    cur.execute(sql, (sql_maori, sql_english, sql_level,))
                except sqlite3.IntegrityError:
                    redirect('/?error=has+occurred')
        elif most_recent == "1":
            sql = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                                     FROM dictionary d
                                     LEFT JOIN user_details u on d.user_id = u.id
                                     ORDER BY date_added DESC LIMIT 20
                                     """
            try:
                cur.execute(sql)
            except sqlite3.IntegrityError:
                redirect('/?error=has+occurred')
            print(f"case 8 parms: {sql_maori}, {sql_english}, {sql_level}, {most_recent}")
        else:
            return render_template("search.html", search_results=[], logged_in=is_logged_in(),
                                   category_list=render_category_list(), selected=selected)

        search_results = cur.fetchall()
        print(f"Search results: {search_results}")
        con.commit()
        con.close()

    else:
        search_results = []
        print(f"line 82: {letter}")
        if letter != "~":
            maori_search = f"{letter}%"
            print(f"line 85: maori_search : {maori_search}")
            con = create_connection(DATABASE)
            cur = con.cursor()
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                               FROM dictionary d
                               LEFT JOIN user_details u on d.user_id = u.id
                               WHERE maori LIKE ?"""
            cur.execute(query, (maori_search,))
            print(f"line 93: Query = {query}")
            search_results = cur.fetchall()
            print(f"line 95: Dictionary list = {search_results}")
            con.close()
            selected = ["" for i in range(26)]
            print(string.ascii_lowercase.index(letter.lower()))
            selected[string.ascii_lowercase.index(letter.lower())] = "selected"
        print(f"line 234: Dictionary list Outside= {search_results}")
    return render_template("search.html", search_results=search_results, logged_in=is_logged_in(),
                               category_list=render_category_list(), selected=selected)


@app.route('/category/<id>', methods=["POST", "GET"])
def render_category(id):
    if request.method == "POST":
        print(request.form)
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        description = request.form.get("description").strip()
        level = request.form.get("level")
        email = session.get('email')

        con = create_connection(DATABASE)
        sql = """INSERT INTO dictionary (maori, english, description, level, category_id, date_added, user_id)
                   VALUES (?, ?, ?, ?, ?, date(), (SELECT id FROM user_details WHERE email = ?))"""
        cur = con.cursor()
        try:
            cur.execute(sql, (maori, english, description, level, id, email,))
        except sqlite3.IntegrityError:
            redirect('/?error=Email+is+already+used')
        con.commit()
        con.close()
        return redirect(f'/category/{id}')
    else:
        con = create_connection(DATABASE)
        cur = con.cursor()
        query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
                   FROM category c
                   LEFT JOIN dictionary d on c.id = d.category_id
                   WHERE c.id = ?"""
        cur.execute(query, (id,))
        category_words = cur.fetchall()
        print(category_words)
        con.close()

        if category_words[0][3] is None:
            category_words_parm = []
        category_words_parm = category_words
        image_names = get_image_filenames(category_words_parm)
        print (f"Line 381 : image_names = {image_names}")
        return render_template("category.html", category_words=category_words_parm, logged_in=is_logged_in(),
                               image_names=image_names,
                               category_list=render_category_list(), allow_edit=allow_edit())


@app.route('/word/<id>', methods=["POST", "GET"])
def render_word(id):
    if request.method == "POST":
        print(request.form)
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        description = request.form.get("description").strip()
        level = request.form.get("level")
        email = session.get('email')

        con = create_connection(DATABASE)
        sql = """UPDATE dictionary
                 SET maori = ?,
                    english = ?,
                    description = ?,
                    level = ?,
                    user_id = (SELECT id FROM user_details WHERE email = ?),
                    date_added = date()
                 WHERE id = ?
                 AND (
                        maori <> ? OR
                        english <> ? OR
                        description <> ? OR
                        level <> ?
                     )"""
        cur = con.cursor()
        try:
            cur.execute(sql, (maori, english, description, level, email, id, maori, english, description, level,))
            print(f"{maori},{english},{description},{level}")
        except sqlite3.IntegrityError:
            redirect('/?error=Update+failed+try+again+later')
        con.commit()
        con.close()
        return redirect(f'/word/{id}')


    con = create_connection(DATABASE)
    cur = con.cursor()
    query = """SELECT d.id, d.maori, d.english, d.description, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE d.id = ?"""
    cur.execute(query, (id,))
    word_details = cur.fetchall()
    checked = []
    for i in range(1, 11):
        print(i)
        if word_details[0][4] == i:
            checked.append("checked")
        else:
            checked.append("")
    print(checked)
    print(word_details)
    print(word_details[0][4])
    con.close()

    return render_template("word.html",
                           word_details=word_details,
                           logged_in=is_logged_in(),
                           image_name=get_image_filename(word_details[0][2]),
                           checked=checked,
                           category_list=render_category_list(),
                           allow_edit=allow_edit())


@app.route('/delete_category/<id>')
def render_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
                   FROM category c
                   LEFT JOIN dictionary d on c.id = d.category_id
                   WHERE c.id = ?"""
    cur.execute(query, (id,))
    category_words = cur.fetchall()
    print(category_words)
    con.close()
    if category_words[0][4] is None:
        category_words_parm = []
    category_words_parm = category_words
    image_names = get_image_filenames(category_words_parm)
    return render_template("delete_category.html", category_words=category_words_parm, logged_in=is_logged_in(),
                           image_names=image_names, category_list=render_category_list())


@app.route('/delete_word/<id>')
def render_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = """SELECT d.id, d.maori, d.english, d.description, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE d.id = ?"""
    cur.execute(query, (id,))
    word_list = cur.fetchall()
    print(word_list)
    con.close()
    return render_template("delete_word.html", word_list=word_list, logged_in=is_logged_in(),
                           image_name=get_image_filename(word_list[0][2]),
                           category_list=render_category_list())


@app.route('/action_delete_category/<id>', methods=["POST"])
def action_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')

    con = create_connection(DATABASE)
    query = "DELETE FROM category WHERE id = ?"
    cur = con.cursor()
    try:
        print(id)
        cur.execute(query, (id,))
    except sqlite3.IntegrityError:
        redirect('/?error=Unknown+error+occurred+during+delete+of+category')
    con.commit()
    con.close()
    return redirect('/')


@app.route('/action_delete_word/<id>', methods=["POST"])
def action_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')

    con = create_connection(DATABASE)
    query = "DELETE FROM dictionary WHERE id = ?"
    cur = con.cursor()
    try:
        print(id)
        cur.execute(query, (id,))
    except sqlite3.IntegrityError:
        redirect('/?error=Unknown+error+occurred+during+delete+of+category')
    con.commit()
    con.close()
    return redirect('/')


@app.route('/addcategory', methods=["POST", "GET"])
def render_add_category():
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    if request.method == "POST":
        print(request.form)
        category_name = request.form.get("category_name").strip().title()
        if category_name == "":
            return redirect('/addcategory?error=Please+enter+category+name')

        con = create_connection(DATABASE)
        cur = con.cursor()
        query = "SELECT id FROM category WHERE category_name = ?"
        cur.execute(query, (category_name,))
        category_ids = cur.fetchall()
        if len(category_ids) != 0:
            return redirect('/addcategory?error=Category+already+exists')
        else:
            sql = "INSERT INTO category (category_name) VALUES (?)"
        try:
            cur.execute(sql, (category_name,))
        except sqlite3.IntegrityError:
            return ('/addcategory?error=Could+not+add+category+try+again+later')
        con.commit()
        con.close()
        return redirect('/addcategory')
    error = request.args.get('error')

    if error == None:
        error = ""

    return render_template("add_category.html", logged_in=is_logged_in(), category_list=render_category_list())


def is_logged_in():
    if session.get('email') is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


def allow_edit():
    if not is_logged_in():
        return False
    email = session.get('email')
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = """SELECT allow_edit
               FROM user_type
               WHERE id = (SELECT user_type_id FROM user_details WHERE email = ?)"""
    cur.execute(query, (email,))
    edit_privileges = cur.fetchall()
    return edit_privileges[0][0]


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
        user_type = request.form.get("user_type")
        if password != password2:
            error = "Passwords don't match"
            return redirect('/signup?error=Passwords+dont+match')
        if len(password) < 8:
            error = "Passwords must be 8 characters or more"
            return redirect('/signup?error=Passwords+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)
        query = "INSERT INTO user_details (first_name, last_name, email, password, user_type_id) VALUES (?,?,?,?,(SELECT id from user_type WHERE user_type = ?))"
        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, user_type,))
        except sqlite3.IntegrityError:
            error = "Email is already in use"
            return redirect('/signup?error=Email+is+already+used')
        con.commit()
        con.close()
        return redirect('/login')
    error = request.args.get('error')



    return render_template("signup.html", error=error, logged_in=is_logged_in(), category_list=render_category_list())


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
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect('/login?error=Email+invalid+or+password+incorrect')

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + '?error=Email+invalid+or+Password+incorrect')

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        print(session)
        return redirect('/')

    return render_template("login.html", logged_in=is_logged_in(), category_list=render_category_list())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect(request.referrer + '?message=see+you+later')


if __name__ == '__main__':
    app.run()
