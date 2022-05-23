# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Program name      : Maori Dictionary
# Author            : Inesh Bhanuka
# Date              : 2021-05-12
# Project           : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~
# Program imports
# ~~~~~~~~~~~~~~~
from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import glob
import os
import sqlite3
from sqlite3 import Error
import string

# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~
DATABASE = "database/dictionary.db"

app = Flask(__name__)        # Create application object
bcrypt = Bcrypt(app)         # Builds the password security platform
app.secret_key = "Duckyweu"  # The security key used


def get_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


def get_image_filename(english_name):
    path_file = f"static\\images\\{english_name}.*"
    listing = glob.glob(path_file)
    for filename in listing:
        return os.path.basename(filename)
    return "noimage.png"


def get_image_filenames(words):
    image_names = []
    for word in words:
        image_names.append(get_image_filename(word[2]))
    return image_names


def get_search_results(maori, english, level, most_recent):
    query = ""
    args = []
    maori_search = f"{maori}%"
    english_search = f"{english}%"
    level_search = f"{level}"
    if maori != "" or english != "" or level != "0" and most_recent == "1":
        if maori != "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     english LIKE ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [maori_search, english_search]
        if maori != "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     level = ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [maori_search, level_search]
        if maori == "" and english != "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ? AND 
                     level = ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [english_search, level_search]
        if maori != "" and english == "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ?
                     ORDER BY date_added DESC, maori  LIMIT 20 
                     """
            args = [maori_search]
        if maori == "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [english_search]
        if maori == "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     level = ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [level_search]
        if maori != "" and english != "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND
                     english LIKE ? AND
                     level = ?
                     ORDER BY date_added DESC, maori  LIMIT 20
                     """
            args = [maori_search, english_search, level_search]
    elif maori != "" or english != "" or level != "0" and most_recent == "0":
        if maori != "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     english LIKE ?
                     ORDER BY maori
                     """
            args = [maori_search, english_search]
        if maori != "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     level = ?
                     ORDER BY maori
                     """
            args = [maori_search, level_search]
        if maori == "" and english != "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ? AND 
                     level = ?
                     ORDER BY maori
                     """
            args = [english_search, level_search]
        if maori != "" and english == "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ?
                     ORDER BY maori 
                     """
            args = [maori_search]
        if maori == "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ?
                     ORDER BY maori
                     """
            args = [english_search]
        if maori == "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     level = ?
                     ORDER BY maori
                     """
            args = [level_search]
        if maori != "" and english != "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND
                     english LIKE ? AND
                     level = ?
                     ORDER BY maori
                     """
            args = [maori_search, english_search, level_search]
    elif most_recent == "1":
        query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                 FROM dictionary d
                 LEFT JOIN user_details u on d.user_id = u.id
                 ORDER BY date_added DESC, maori  LIMIT 20
                 """
    if len(args) == 0:
        query_results = execute_query(query)
    else:
        query_results = execute_query(query, args)
    if issubclass(type(query_results), Error):
        redirect('/?error=has+occurred')
    return query_results


@app.route('/search/<letter>', methods=["POST", "GET"])
def render_search(letter):
    selected = []
    if request.method == "POST":
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        level = request.form.get("level").strip()
        most_recent = request.form.get("Date-Added").strip()
        if maori == "" and english == "" and level == "0" and most_recent == "0":
            return render_template('search.html'
                                   , search_results=[]
                                   , logged_in=is_logged_in()
                                   , category_list=get_category_list()
                                   , selected=selected)
        search_results = get_search_results(maori, english, level, most_recent)
    else:
        search_results = []
        if letter != "~":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                       FROM dictionary d
                       LEFT JOIN user_details u on d.user_id = u.id
                       WHERE maori LIKE ?
                       ORDER BY maori"""
            search_results = execute_query(query, [f"{letter}%"])
            if issubclass(type(search_results), Error):
                return redirect('/?error=Unknown+error')
            selected = ["" for i in range(26)]
            selected[string.ascii_lowercase.index(letter.lower())] = "selected"
    return render_template("search.html", search_results=search_results, logged_in=is_logged_in(), letter=letter,
                           category_list=get_category_list(), selected=selected, allow_edit=allow_edit())


@app.route('/category/<id>', methods=["POST", "GET"])
def render_category(id):
    if request.method == "POST":
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        description = request.form.get("description").strip()
        level = request.form.get("level")
        email = session.get('email')
        query_results = execute_query("SELECT id FROM dictionary WHERE maori = ?", [maori])
        if issubclass(type(query_results), Error) or len(query_results) != 0:
            return redirect(f"/category/{id}?error=The+word+{maori}+already+exists")
        else:
            command = """INSERT INTO dictionary (maori, english, description, level, category_id, date_added, user_id)
                           VALUES (?, ?, ?, ?, ?, date(), (SELECT id FROM user_details WHERE email = ?))"""
            args = [maori, english, description, level, id, email]
            response = execute_command(command, args)
            if issubclass(type(response), Error):
                redirect(f"/category/{id}?error=The+word+{maori}+already+exists")
            return redirect(f'/category/{id}')
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
               FROM category c
               LEFT JOIN dictionary d on c.id = d.category_id
               WHERE c.id = ?
               ORDER BY maori"""
    query_results = execute_query(query, [id])
    if issubclass(type(query_results), Error):
        return redirect('/?error=Category+could+not+be+retrieved+unknown+error')
    image_names = get_image_filenames(query_results)
    error = request.args.get('error')
    if error is None:
        error = ""
    return render_template('category.html'
                           , category_words=query_results
                           , logged_in=is_logged_in()
                           , image_names=image_names
                           , error=error
                           , category_list=get_category_list()
                           , allow_edit=allow_edit())


@app.route('/word/<id>', methods=["POST", "GET"])
def render_word(id):
    if request.method == "POST":
        maori = request.form.get("maori").strip()
        english = request.form.get("english").strip()
        description = request.form.get("description").strip()
        level = request.form.get("level")
        email = session.get('email')
        query_results = execute_query("SELECT id FROM dictionary WHERE maori = ? AND id <> ?", [maori, id])
        if issubclass(type(query_results), Error) or len(query_results) != 0:
            return redirect(f"/word/{id}?error=The+word+'{maori}'+already+exists")
        else:
            command = """UPDATE dictionary
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
            args = [maori, english, description, level, email, id, maori, english, description, level]
            response = execute_command(command, args)
            if issubclass(type(response), Error):
                redirect('/?error=Update+failed+try+again+later')
            breadcrumb = request.args.get("breadcrumb")
            return redirect(f'/word/{id}?breadcrumb={breadcrumb}')
    query = """SELECT d.id, d.maori, d.english, d.description, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE d.id = ?"""
    query_results = execute_query(query, [id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return redirect('/?error=Word+could+not+be+retrieved+unknown+error')
    checked = []
    for i in range(1, 11):
        print(i)
        if query_results[0][4] == i:
            checked.append("checked")
        else:
            checked.append("")
    error = request.args.get('error')
    if error is None:
        error = ""
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('word.html'
                           , word_details=query_results
                           , logged_in=is_logged_in()
                           , error=error
                           , image_name=get_image_filename(query_results[0][2])
                           , checked=checked
                           , category_list=get_category_list()
                           , allow_edit=allow_edit()
                           , breadcrumb=breadcrumb)


@app.route('/delete_category/<id>')
def render_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
               FROM category c
               LEFT JOIN dictionary d on c.id = d.category_id
               WHERE c.id = ?
               ORDER BY maori"""
    query_results = execute_query(query, [id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return redirect('/?error=Unknown+error')
    image_names = get_image_filenames(query_results)
    return render_template('delete_category.html'
                           , category_words=query_results
                           , logged_in=is_logged_in()
                           , image_names=image_names
                           , category_list=get_category_list()
                           , allow_edit=allow_edit())


@app.route('/delete_word/<id>')
def render_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    query = """SELECT d.id
               , d.maori
               , d.english
               , d.description
               , d.level
               , d.date_added
               , ifnull(u.first_name, '')
               , ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE d.id = ?"""
    query_results = execute_query(query, [id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return redirect('/?error=Word+does+not+exist+or+unknown+error')
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('delete_word.html'
                           , word_list=query_results
                           , logged_in=is_logged_in()
                           , image_name=get_image_filename(query_results[0][2])
                           , category_list=get_category_list()
                           , breadcrumb=breadcrumb)


@app.route('/action_delete_category/<id>', methods=["POST"])
def action_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    response = execute_command("DELETE FROM category WHERE id = ?", [id])
    if issubclass(type(response), Error):
        redirect('/?error=Unknown+error+occurred+during+delete+of+category')
    return redirect('/')


@app.route('/action_delete_word/<id>', methods=["POST"])
def action_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    response = execute_command("DELETE FROM dictionary WHERE id = ?", [id])
    print(f"line 557: response: {response}")
    print(f"line 557: id: {id}")
    if issubclass(type(response), Error):
        redirect('/?error=Unknown+error+occurred+during+delete+of+word')
    breadcrumb = request.args.get("breadcrumb")
    return redirect(f'{breadcrumb}')


@app.route('/addcategory', methods=["POST", "GET"])
def render_add_category():
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    if request.method == "POST":
        category_name = request.form.get("category_name").strip().title()
        if category_name == "":
            return redirect('/addcategory?error=Please+enter+category+name')
        category_id = execute_query("SELECT id FROM category WHERE category_name = ?", [category_name])
        print(f"line 574 category_id: {category_id}")
        if issubclass(type(category_id), Error) or len(category_id) != 0:
            return redirect('/addcategory?error=Category+already+exists')
        else:
            response = execute_command("INSERT INTO category (category_name) VALUES (?)", [category_name])
            if issubclass(type(response), Error):
                return redirect('/addcategory?error=Could+not+add+category+try+again+later')
        return redirect('/addcategory')
    error = request.args.get('error')
    if error is None:
        error = ""
    return render_template('add_category.html'
                           , logged_in=is_logged_in()
                           , category_list=get_category_list()
                           , allow_edit=allow_edit()
                           , error=error)


@app.route('/signup', methods=["POST", "GET"])
def render_signup():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        first_name = request.form.get("first_name").strip().title()
        last_name = request.form.get("last_name").strip().title()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type")
        if first_name.isdigit():
            error = "First name should only contain alphabetic characters"
            return redirect('/signup?error=First+name+should+only+contain+alphabetic+characters')
        if last_name.isdigit():
            error = "Last name should only contain alphabetic characters"
            return redirect('/signup?error=Last+name+should+only+contain+alphabetic+characters')
        if password != confirm_password:
            error = "Passwords don't match"
            return redirect('/signup?error=Passwords+dont+match')
        if len(password) < 8:
            error = "Passwords must be 8 characters or more"
            return redirect('/signup?error=Passwords+must+be+8+characters+or+more')
        hashed_password = bcrypt.generate_password_hash(password)
        command = """INSERT INTO user_details 
                   (first_name, last_name, email, password, user_type_id) 
                   VALUES (?,?,?,?,(SELECT id from user_type WHERE user_type = ?))"""
        args = [first_name, last_name, email, hashed_password, user_type]
        response = execute_command(command, args)
        if issubclass(type(response), Error):
            error = "Email is already in use"
            return redirect('/signup?error=Email+is+already+used')
        return redirect('/login')
    error = request.args.get('error')
    return render_template('signup.html'
                           , logged_in=is_logged_in()
                           , category_list=get_category_list()
                           , error = error)


def get_category_list():
    category_list = execute_query("SELECT * FROM category ORDER BY category_name")
    if issubclass(type(category_list), Error):
        return []
    return category_list


def allow_edit():
    if not is_logged_in():
        return False
    query = """SELECT allow_edit
               FROM user_type
               WHERE id = (SELECT user_type_id FROM user_details WHERE email = ?)"""
    args = [session.get('email')]
    query_results = execute_query(query, args)
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return False
    return query_results[0][0]


def is_logged_in():
    if session.get('email') is None:
        return False
    else:
        return True


@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    return redirect('/')


def execute_query(query, args=None):
    connection = get_connection(DATABASE)
    cursor = connection.cursor()
    try:
        if args is None:
            cursor.execute(query)
        else:
            cursor.execute(query, args)
        query_results = cursor.fetchall()
    except sqlite3.Error as e:
        return e
    finally:
        if connection is not None:
            connection.close()
    return query_results


def execute_command(command, args=None):
    connection = get_connection(DATABASE)
    cursor = connection.cursor()
    sql = f"""{command}"""
    try:
        if args is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)
        connection.commit()
    except sqlite3.Error as e:
        return e
    finally:
        if connection is not None:
            connection.close()
    return


@app.route('/login', methods=["POST", "GET"])
def render_login():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()
        query_results = execute_query("SELECT password FROM user_details WHERE email = ?", [email])
        if issubclass(type(query_results), Error)\
            or len(query_results) == 0\
                or not bcrypt.check_password_hash(query_results[0][0], password):
            return redirect('/login?error=Email+invalid+or+password+incorrect')
        session['email'] = email
        return redirect('/')
    error = request.args.get('error')
    if error is None:
        error = ""
    return render_template('login.html'
                           , logged_in=is_logged_in()
                           , category_list=get_category_list()
                           , error=error)


@app.route('/')
def render_home():
    return render_template('home.html'
                           , logged_in=is_logged_in()
                           , allow_edit=allow_edit()
                           , category_list=get_category_list())


if __name__ == '__main__':
    app.run()
