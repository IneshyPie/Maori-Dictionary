# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Program name      : Maori Dictionary
# Author            : Inesh Bhanuka
# Date              : 2021-05-12
# Project           : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~
# Program imports
# ~~~~~~~~~~~~~~~
from data_access import *
from flask import Flask, session
from flask_bcrypt import Bcrypt
import string
import glob
import os


# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~
IMAGE_PATH = "static\\images\\"

app = Flask(__name__)  # Create application object
bcrypt = Bcrypt(app)  # Builds the password security platform
app.secret_key = "Duckyweu"  # The security key used


def is_logged_in():
    if session.get('email') is None:
        return False
    else:
        return True


def allow_edit():
    if not is_logged_in():
        return False
    email = session.get('email')
    allow = get_allow_edit(email)
    if allow is None:
        return False
    return allow


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


def get_form_data(form):
    maori = form.get("maori").strip()
    english = form.get("english").strip()
    level = form.get("level")
    return maori, english, level


def get_word_form_data(word_form):
    maori, english, level = get_form_data(word_form)
    description = word_form.get("description").strip()
    return maori, english, description, level


def get_search_form_data(search_form):
    maori, english, level = get_form_data(search_form)
    most_recent = search_form.get("Date-Added").strip()
    return maori, english, level, most_recent


def do_search_by_form(search_form):
    maori, english, level, most_recent = get_search_form_data(search_form)
    if maori == "" and english == "" and level == "0" and most_recent == "0":
        return []
    return get_search_results(maori, english, level, most_recent)


def do_search_by_browse(letter):
    search_results = []
    if letter.isalpha() and letter != "~" and len(letter) == 1:
        search_results = get_browse_results(letter)
    return search_results


def get_selected(alphabetic_letter):
    selected = []
    if alphabetic_letter.isalpha() and len(alphabetic_letter) == 1:
        for i in range(26):
            selected.append("")
        selected[string.ascii_lowercase.index(alphabetic_letter.lower())] = "selected"
    return selected


def validate_add_word(word_form, category_id):
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    success = insert_word(maori, english, description, level, category_id, email)
    if not success:
        is_valid = False
        return_url = f"/category/{category_id}?error=The+word+'{maori}'+with+the+english+meaning+'{english}'+already" \
                     f"+exists "
    return is_valid, return_url


def validate_update_word(word_form, word_id):
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    success = update_word(maori, english, description, level, email, word_id)
    if not success:
        is_valid = False
        return_url = f"/word/{word_id}?error=The+word+'{maori}'+with+the+english+meaning+'{english}'+already+exists"
    return is_valid, return_url


def get_checked(level):
    checked = []
    for i in range(1, 11):
        if level == i:
            checked.append("checked")
        else:
            checked.append("")
    return checked


def validate_add_category(category_form):
    category_name = category_form.get("category_name").strip().title()
    return_url = ""
    is_valid = True
    if category_name == "":
        is_valid = False
        return_url = '/addcategory?error=Please+enter+category+name'
    else:
        success = add_category(category_name)
        if not success:
            is_valid = False
            return_url = '/addcategory?error=Category+already+exists'
    return is_valid, return_url


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


def validate_login(login_form):
    email = login_form["email"].strip().lower()
    password = login_form["password"].strip()
    user_details = get_user_details(email)
    if user_details is None or not bcrypt.check_password_hash(user_details[0][2], password):
        return False
    session['email'] = email
    session['first_name'] = user_details[0][0]
    session['last_name'] = user_details[0][1]
    session['user_type'] = user_details[0][3]
    return True


def remove_category(category_id):
    return delete_category(category_id)


def remove_word(word_id):
    return delete_word(word_id)


def get_categories():
    return get_category_list()


def get_dictionary_word(word_id):
    return get_word(word_id)


def get_category_words(category_id):
    return get_words(category_id)


def get_user():
    first_name = session.get('first_name')
    if first_name is None:
        user_details = ""
    else:
        last_name = session.get('last_name')
        user_type = session.get('user_type').title()
        user_details = f"{first_name} {last_name} ({user_type})"
    return user_details
