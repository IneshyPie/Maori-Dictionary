# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application name      : Maori Dictionary
# Program name          : services.py
# Program description   : This module services the web module of the application.
# Author                : Inesh Bhanuka
# Date                  : 2022-05-30
# Project               : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
NO_IMAGE_FILENAME = "noimage.png"


app = Flask(__name__)  # Create application object
bcrypt = Bcrypt(app)  # Builds the password security platform
app.secret_key = "Duckyweu"  # The security key used


def is_logged_in():
    """
        This function is used to obtain whether the user has logged in.

    :return: A boolean representing whether the user has logged in
        True: When the user has logged in
        False: When the user has NOT logged in
    """
    if session.get('email') is None:
        return False
    else:
        return True


def allow_edit():
    """
        This function is used to obtain whether the user has rights to edit directory entries
    :calls (located in data_access.py module)
        get_allow_edit - Retrieve allow edit from database
    :return: A boolean representing whether the user has rights to edit directory entries
        True: When the user has rights to edit directory entries
        False: When the user has NO rights to edit directory entries
    """
    if not is_logged_in():
        return False
    email = session.get('email')
    allow = get_allow_edit(email)
    if allow is None:
        return False
    return allow


def do_search_by_form(search_form):
    """
        This function is used to search directory entries using the search criteria submitted
        via the search form
    :param search_form:
        type: request.form
        required: true
        description: The search from submitted with user search criteria
    :calls (located in data_access.py module)
        get_search_results - Retrieve search results from database
    :return: A list of search results
        When no search criteria entered straight away return empty list.
        Otherwise, return search results from database
    """
    maori, english, level, most_recent = get_search_form_data(search_form)
    if maori == "" and english == "" and level == "0" and most_recent == "0":
        return []
    return get_search_results(maori, english, level, most_recent)


def do_search_by_browse(letter):
    """
        This function is used to search directory entries using the browse character the user
        clicked in the search page header
    :param letter:
        type: string
        required: true
        description: The character used to browse the dictionary
    :calls (located in data_access.py module)
        get_browse_results - Retrieve search results from database
    :return: If letter is a valid for searching then return the search results from database
             otherwise return empty list.
    """
    search_results = []
    if letter.isalpha() and letter != "~" and len(letter) == 1:
        search_results = get_browse_results(letter)
    return search_results


def validate_add_word(word_form, category_id):
    """
        This function is used to validate and add a word to the dictionary under the specified
        category
     :param word_form:
        type: request.form
        required: true
        description: The word form submitted with word details
    :param category_id:
        type: int
        required: true
        description: The category id the user is attempting to add this word to
    :calls
        get_word_form_data - get the word data from the form
        add_word (in data_access.py module) - Add word to the database
    :return:
        is_valid: A boolean indicating success.
        return_url: Return URL with error message in case of add failure.
    """
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    success = add_word(maori, english, description, level, category_id, email)
    if not success:
        is_valid = False
        return_url = f"/category/{category_id}?error=The+word+'{maori}'+with+the+english+meaning+'{english}'+already" \
                     f"+exists "
    return is_valid, return_url


def validate_update_word(word_form, word_id, breadcrumb):
    """
        This function is used to validate and update the word identified by the word_id
     :param word_form:
        type: request.form
        required: true
        description: The word form submitted with word details
    :param word_id:
        type: int
        required: true
        description: The word id of the word needing update
    :param breadcrumb:
        type: string
        required: true
        description: The breadcrumb used to track return URL
    :calls
        get_word_form_data - get the word data from the form
        update_word (in data_access.py module) - Update word in the database
    :return:
        is_valid: A boolean indicating success.
        return_url: Return URL with error message in case update failure.
    """
    maori, english, description, level = get_word_form_data(word_form)
    email = session.get('email')
    is_valid = True
    return_url = ""
    success = update_word(maori, english, description, level, email, word_id)
    if not success:
        is_valid = False
        return_url = f"/word/{word_id}?breadcrumb={breadcrumb}&error=The+word+'{maori}'+with+the+english+meaning+" \
                     f"'{english}'+already+exists "
    return is_valid, return_url


def validate_add_category(category_form):
    """
        This function is used to validate and add a category
     :param category_form:
        type: request.form
        required: true
        description: The category form submitted with category details
    :calls
        add_category (in data_access.py module) - Add category to the database
    :return:
        is_valid: A boolean indicating success.
        return_url: Return URL with error message in case add failure.
    """
    category_name = category_form.get("category_name").strip().title()
    return_url = ""
    is_valid = True
    if category_name == "":
        is_valid = False
        return_url = '/add_category?error=Please+enter+category+name'
    else:
        success = add_category(category_name)
        if not success:
            is_valid = False
            return_url = '/add_category?error=Category+already+exists'
    return is_valid, return_url


def validate_signup_user(signup_form):
    """
        This function is used to validate and sign up user
     :param signup_form:
        type: request.form
        required: true
        description: The sign-up form submitted with sign up details
    :calls
        add_user (in data_access.py module) - Add user to the database
    :return:
        is_valid: A boolean indicating success.
        return_url: Return URL with error message in case add failure.
    """
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


def validate_and_login_user(login_form):
    """
        This function is used to validate and login user. The user email, names and type details
        are stored in the session if successful login
     :param login_form:
        type: request.form
        required: true
        description: The login form submitted with login details
    :calls
        get_user_details (in data_access.py module) - Gets the user details from database for validation
    :return: A boolean indicating success of login.
        True: Login success.
        False: Login failure.
    """
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
    """
        This function is used to trigger a deletion of a category in the database
    :param category_id:
        type: int
        required: true
        description: The category id of the category the user is attempting to delete
    :calls
        delete_category (in data_access.py module) - Deletes the category identified from the database
    :return: A boolean indicating success of delete.
        True: Login success.
        False: Login failure.
    """
    return delete_category(category_id)


def remove_word(word_id):
    """
        This function is used to trigger a deletion of a category in the database
    :param word_id:
        type: int
        required: true
        description: The word id of the word the user is attempting to delete
    :calls
        delete_word (in data_access.py module) - Deletes the word identified from the database
    :return: A boolean indicating success of delete.
        True: Login success.
        False: Login failure.
    """
    return delete_word(word_id)


def get_checked(level):
    """
        Gets a list with the value "checked" inserted into the location corresponding
        the value of level
    :param level:
        type: int
        required: true
        description: A value indicating the position of the list to have "checked" inserted
    :return: A list with the value "checked" inserted into the location corresponding
        the value of level.
    """
    checked = []
    for i in range(1, 11):
        if level == i:
            checked.append("checked")
        else:
            checked.append("")
    return checked


def get_selected(alphabetic_letter):
    """
        Gets a list with the value "selected" inserted into the location corresponding
        to the alphabetic letter position in the english alphabet
    :param alphabetic_letter:
        type: string of length 1
        required: true
        description: A value indicating the position of the list to have "selected"  to be inserted.
    :return: A list with the value "selected" inserted into the location corresponding
        to the alphabetic letter position in the english alphabet.
    """
    selected = []
    if alphabetic_letter.isalpha() and len(alphabetic_letter) == 1:
        for i in range(26):
            selected.append("")
        selected[string.ascii_lowercase.index(alphabetic_letter.lower())] = "selected"
    return selected


def get_categories():
    """
        This function returns all the categories in the database
    :calls
        get_category_list (in data_access.py module) - Retrieve all the categories from the database
    :return: A list of all the categories in the database or Error if any database level issue occurs.
    """
    return get_category_list()


def get_category_words(category_id):
    """
        This function returns all the words for the category specified from the database
    :param category_id:
        type: int
        required: true
        description: The category id of the category to retrieve the words
    :calls
        get_words (in data_access.py module) - Retrieve all the words for the given category id
        from the database
    :return: A list of all the words in the database for the given category or Error if any
             database level issue occurs.
    """
    return get_words(category_id)


def get_dictionary_word(word_id):
    """
        This function returns the word for the word id specified from the database
    :param word_id:
        type: int
        required: true
        description: The word id of the word to retrieve rom the database
    :calls
        get_word (in data_access.py module) - Retrieve all the words for the given category id
        from the database
    :return: A list with the word or the word id specified  if not found None or Error if any
             database level issue occurs.
    """
    return get_word(word_id)


def get_user():
    """
        This function constructs and returns user details and type in a string
    :return: Returns user details and type in a string.
    """
    first_name = session.get('first_name')
    if first_name is None:
        user_details = ""
    else:
        last_name = session.get('last_name')
        user_type = session.get('user_type').title()
        user_details = f"{first_name} {last_name} ({user_type})"
    return user_details


def get_image_filename(english_word):
    """
        Searches the images' directory for an image file with English word (regardless of extension)
        passed in, if a file is found return the filename with the extension immediately. If multiples
        were found will return the first one found.
        If no image file with the specified english word then return the default image file name
    :param english_word:
        type: string
        required: true
        description: The English word to search the image file for.
    :return: The corresponding image file or default image file if not found.
    """
    path_file = f"{IMAGE_PATH}{english_word}.*"
    listing = glob.glob(path_file)
    for filename in listing:
        return os.path.basename(filename)
    return NO_IMAGE_FILENAME


def get_image_filenames(words):
    """
        Constructs and returns a list of image file names corresponding to the list
        of words passed in to the function
    :param words:
        type: list of tuples
        required: true
        description: The English word should be in the 3 location in each tuple
    :calls
       get_image_filename - To retrieve the image filename for each english word
                            from the database
    :return: A list of image file names corresponding to the words list
        passed into the function.
    """
    image_names = []
    for word in words:
        image_names.append(get_image_filename(word[2]))
    return image_names


def get_form_data(form):
    """
        Retrieve and return the basic word details from the passed in request form
     :param form:
        type: request.form
        required: true
        description: A form to retrieve and return word details
    :return:
        maori - The maori word
        english - The english word
        level - The year level
    """
    maori = form.get("maori").strip()
    english = form.get("english").strip()
    level = form.get("level")
    return maori, english, level


def get_word_form_data(word_form):
    """
    Retrieve and return the basic word details and description from the passed in
    word form
     :param word_form:
        type: request.form
        required: true
        description: A word form to retrieve and return word details and description
    :calls
        get_form_data - Retrieve basic word details from the passed in request form
    :return:
        maori - The maori word
        english - The english word
        description - The description of the word
        level - The year level
    """
    maori, english, level = get_form_data(word_form)
    description = word_form.get("description").strip()
    return maori, english, description, level


def get_search_form_data(search_form):
    """
    Retrieve and return the basic word details and most_recent indicator from the passed in
    search form
     :param search_form:
        type: request.form
        required: true
        description: A search form to retrieve and return word details and most_recent indicator
    :calls
        get_form_data - Retrieve basic word details from the passed in request form
    :return:
        maori - The maori word
        english - The english word
        description - The description of the word
        most_recent - The most_recent indicator
    """
    maori, english, level = get_form_data(search_form)
    most_recent = search_form.get("Date-Added").strip()
    return maori, english, level, most_recent
