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
IMAGE_PATH = "static\\images\\"

app = Flask(__name__)  # Create application object
bcrypt = Bcrypt(app)  # Builds the password security platform
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
    path_file = f"{IMAGE_PATH}{english_name}.*"
    listing = glob.glob(path_file)
    for filename in listing:
        return os.path.basename(filename)
    return "noimage.png"


def get_image_filenames(words):
    image_names = []
    for word in words:
        image_names.append(get_image_filename(word[2]))
    return image_names


def is_logged_in():
    if session.get('email') is None:
        return False
    else:
        return True


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


def get_word_form_data(word_form):
    maori = word_form.get("maori").strip()
    english = word_form.get("english").strip()
    description = word_form.get("description").strip()
    level = word_form.get("level")
    return maori, english, description, level


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
        is_valid, return_url = validate_add_word(request.form, id)
        if not is_valid:
            return redirect(return_url)
        return redirect(f'/category/{id}')
    words = get_words(id)
    if words is None:
        return redirect('/?error=Category+could+not+be+retrieved+unknown+error')
    image_names = get_image_filenames(words)
    error = request.args.get('error')
    if error is None:
        error = ""
    return render_template('category.html'
                           , category_words=words
                           , logged_in=is_logged_in()
                           , image_names=image_names
                           , error=error
                           , category_list=get_category_list()
                           , allow_edit=allow_edit())


def validate_add_word(word_form, category_id):
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    if word_already_exists(maori):
        is_valid = False
        return_url = f"/category/{category_id}?error=The+word+{maori}+already+exists"
    else:
        success = insert_word(maori, english, description, level, category_id, email)
        if not success:
            is_valid = False
            return_url = f"/category/{category_id}?error=The+word+{maori}+already+exists"
    return is_valid, return_url


def word_already_exists(maori):
    query_results = execute_query("SELECT id FROM dictionary WHERE maori = ?", [maori])
    if issubclass(type(query_results), Error) or len(query_results) != 0:
        return True
    return False


def insert_word(maori, english, description, level, category_id, email):
    command = """INSERT INTO dictionary (maori, english, description, level, category_id, date_added, user_id)
                 VALUES (?, ?, ?, ?, ?, date(), (SELECT id FROM user_details WHERE email = ?))"""
    args = [maori, english, description, level, category_id, email]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


def get_words(category_id):
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
               FROM category c
               LEFT JOIN dictionary d on c.id = d.category_id
               WHERE c.id = ?
               ORDER BY maori"""
    query_results = execute_query(query, [category_id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results


@app.route('/word/<id>', methods=["POST", "GET"])
def render_word(id):
    if request.method == "POST":
        is_valid, return_url = validate_update_word(request.form, id)
        if not is_valid:
            return redirect(return_url)
        breadcrumb = request.args.get("breadcrumb")
        return redirect(f'/word/{id}?breadcrumb={breadcrumb}')
    word = get_word(id)
    if word is None:
        return redirect('/?error=Word+could+not+be+retrieved+unknown+error')
    error = request.args.get('error')
    if error is None:
        error = ""
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('word.html'
                           , word_details=word
                           , logged_in=is_logged_in()
                           , error=error
                           , image_name=get_image_filename(word[0][2])
                           , checked=get_checked(word[0][4])
                           , category_list=get_category_list()
                           , allow_edit=allow_edit()
                           , breadcrumb=breadcrumb)


def validate_update_word(word_form, word_id):
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    if word_already_exists_in_dictionary(maori, word_id):
        is_valid = False
        return_url = f"/word/{word_id}?error=The+word+'{maori}'+already+exists+in+dictionary"
    else:
        success = update_word(maori, english, description, level, email, word_id)
        if not success:
            is_valid = False
            return_url = '/?error=Update+failed+try+again+later'
    return is_valid, return_url


def word_already_exists_in_dictionary(maori, word_id):
    query_results = execute_query("SELECT id FROM dictionary WHERE maori = ? AND id <> ?", [maori, word_id])
    if issubclass(type(query_results), Error) or len(query_results) != 0:
        return True
    return False


def update_word(maori, english, description, level, email, word_id):
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
    args = [maori, english, description, level, email, word_id, maori, english, description, level]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


def get_checked(level):
    checked = []
    for i in range(1, 11):
        if level == i:
            checked.append("checked")
        else:
            checked.append("")
    return checked


@app.route('/delete_category/<id>')
def render_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    category_words = get_category_words(id)
    if category_words is None:
        return redirect('/?error=Unknown+error')
    image_names = get_image_filenames(category_words)
    return render_template('delete_category.html',
                           category_words=category_words,
                           logged_in=is_logged_in(),
                           image_names=image_names,
                           category_list=get_category_list(),
                           allow_edit=allow_edit())


def get_category_words(category_id):
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
               FROM category c
               LEFT JOIN dictionary d on c.id = d.category_id
               WHERE c.id = ?
               ORDER BY maori"""
    query_results = execute_query(query, [category_id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results


@app.route('/delete_word/<id>')
def render_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    word = get_word(id)
    if word is None:
        return redirect('/?error=Word+does+not+exist+or+unknown+error')
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('delete_word.html'
                           , word_list=word
                           , logged_in=is_logged_in()
                           , image_name=get_image_filename(word[0][2])
                           , category_list=get_category_list()
                           , breadcrumb=breadcrumb)


def get_word(word_id):
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
    query_results = execute_query(query, [word_id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results


def validate_add_category(category_form):
    category_name = category_form.get("category_name").strip().title()
    return_url = ""
    is_valid = True
    if category_name == "":
        is_valid = False
        return_url = '/addcategory?error=Please+enter+category+name'
    if category_already_exists(category_name):
        is_valid = False
        return_url = '/addcategory?error=Category+already+exists'
    else:
        success = add_category(category_name)
        if not success:
            is_valid = False
            return_url = '/addcategory?error=Could+not+add+category+try+again+later'
    return is_valid, return_url


def category_already_exists(category_name):
    category_ids = execute_query("SELECT id FROM category WHERE category_name = ?", [category_name])
    if issubclass(type(category_ids), Error) or len(category_ids) != 0:
        return True
    return False


def add_category(category_name):
    response = execute_command("INSERT INTO category (category_name) VALUES (?)", [category_name])
    if issubclass(type(response), Error):
        return False
    return True


@app.route('/addcategory', methods=["POST", "GET"])
def render_add_category():
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    if request.method == "POST":
        is_valid, return_url = validate_add_category(request.form)
        if not is_valid:
            return redirect(return_url)
        return redirect('/addcategory')
    error = request.args.get('error')
    if error is None:
        error = ""
    return render_template('add_category.html'
                           , logged_in=is_logged_in()
                           , category_list=get_category_list()
                           , allow_edit=allow_edit()
                           , error=error)


def validate_signup_user(signup_form):
    first_name = signup_form.get("first_name").strip().title()
    last_name = signup_form.get("last_name").strip().title()
    email = signup_form.get("email").strip().lower()
    password = signup_form.get("password")
    confirm_password = signup_form.get("confirm_password")
    user_type = signup_form.get("user_type")
    return_url = ""
    is_valid = True
    if any(c.isdigit() for c in first_name):
        is_valid = False
        return_url = '/signup?error=First+name+should+only+contain+alphabetic+characters'
    if any(c.isdigit() for c in last_name):
        is_valid = False
        return_url = '/signup?error=Last+name+should+only+contain+alphabetic+characters'
    if password != confirm_password:
        is_valid = False
        return_url = '/signup?error=Passwords+dont+match'
    if len(password) < 8:
        is_valid = False
        return_url = '/signup?error=Passwords+must+be+8+characters+or+more'
    if is_valid:
        hashed_password = bcrypt.generate_password_hash(password)
        success = add_user(first_name, last_name, email, hashed_password, user_type)
        if not success:
            is_valid = False
            return_url = '/signup?error=Email+is+already+used'
    return is_valid, return_url


def add_user(first_name, last_name, email, hashed_password, user_type):
    command = """INSERT INTO user_details 
                 (first_name, last_name, email, password, user_type_id) 
                 VALUES (?,?,?,?,(SELECT id from user_type WHERE user_type = ?))"""
    args = [first_name, last_name, email, hashed_password, user_type]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


@app.route('/signup', methods=["POST", "GET"])
def render_signup():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        is_valid, return_url = validate_signup_user(request.form)
        if not is_valid:
            return redirect(return_url)
        return redirect('/login')
    error = request.args.get('error')
    return render_template('signup.html'
                           , logged_in=is_logged_in()
                           , category_list=get_category_list()
                           , error=error)


@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    return redirect('/')


def validate_login(login_form):
    email = login_form["email"].strip().lower()
    password = login_form["password"].strip()
    stored_password = get_password(email)
    if stored_password is None or not bcrypt.check_password_hash(stored_password, password):
        return False
    session['email'] = email  # Successful login store email
    return True


def get_password(email):
    query_results = execute_query("SELECT password FROM user_details WHERE email = ?", [email])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results[0][0]


@app.route('/login', methods=["POST", "GET"])
def render_login():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        if not validate_login(request.form):
            return redirect('/login?error=Email+invalid+or+password+incorrect')
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
