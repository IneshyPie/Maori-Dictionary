# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application name      : Maori Dictionary
# Program name          : app.py
# Program description   : This is the web module of the application.
# Author                : Inesh Bhanuka
# Date                  : 2022-05-30
# Project               : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from services import *
from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt


app = Flask(__name__)  # Create application object
bcrypt = Bcrypt(app)  # Builds the password security platform
app.secret_key = "Duckyweu"  # The security key used


@app.route('/search/<letter>', methods=["POST", "GET"])
def render_search(letter):
    """
        This end point renders the application's popular search page
    :methods
        GET:/search/<letter>
        POST:/search/<letter>
    :param letter:
        type: string
        required: true
        description: The character used to browse the dictionary
    :calls (located in services.py module)
        do_search_by_form - When searching by submitting the search form (POST requests)
        do_search_by_browse - When browsing by clicking a letter in top of page (GET requests)
    :return: renders the search.html
        description: Renders the search.html template processed with following:
            search_results: Actual search results
            logged_in: A boolean describing whether the user is logged in or not
            letter: The letter parameter that was passed in
            category_list: List of categories to be displayed on the sidebar
            selected: Marks a CSS class against the browsing letter in the UI
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            error: Error message for the UI and URL query string
            current_user: Current username and type to be displayed in the top right in the UI
    """
    error = ""
    if request.method == "POST":
        search_letter = ""
        search_results = do_search_by_form(request.form)
    else:
        search_results = []
        search_letter = letter
        error = request.args.get('error')
        if error is None:
            error = ""
            search_results = do_search_by_browse(letter)
    if search_results is None:
        return redirect(f'/search/~?error=Unexpected+error+has+occurred+during+search+please+try+again+later')
    return render_template('search.html',
                           search_results=search_results,
                           logged_in=is_logged_in(),
                           letter=letter,
                           category_list=get_categories(),
                           selected=get_selected(search_letter),
                           allow_edit=allow_edit(),
                           error=error,
                           current_user=get_user())


@app.route('/delete_word/<word_id>')
def render_delete_word(word_id):
    """
        This end point renders delete word page
    :methods
        GET:/delete_word/<word_id>
    :param word_id:
        type: int
        required: true
        description: The id of the word in the dictionary table
    :calls (located in services.py module)
        get_dictionary_word - To get the corresponding word details (GET requests)
    :return: renders the delete_word.html
        description: Renders the delete_word.html template processed with following:
            word_list: The dictionary word identified by the word_id
            logged_in: A boolean describing whether the user is logged in or not
            image_name: Tne image file name corresponding to the word
            category_list: List of categories to be displayed on the sidebar
            breadcrumb: The breadcrumb from query string for tracking where it is coming from
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    word = get_dictionary_word(word_id)
    if word is None:
        return redirect('/?error=Word+does+not+exist+or+unexpected+error')
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('delete_word.html',
                           word_list=word,
                           logged_in=is_logged_in(),
                           image_name=get_image_filename(word[0][2]),
                           category_list=get_categories(),
                           breadcrumb=breadcrumb,
                           allow_edit=allow_edit(),
                           current_user=get_user())


@app.route('/action_delete_word/<word_id>', methods=["POST"])
def action_delete_word(word_id):
    """
        NOTE: This POST only method is for internal use only.
              It is used in the confirm delete mini form to POST and action deleting a word
    :methods
        POST:/action_delete_word/<word_id>
    :calls (located in services.py module)
        remove_word - To remove the corresponding word (POST requests)
    :param word_id:
       type: int
       required: true
       description: The id of the word in the dictionary table
    :return: redirect
        description: Returns a redirect using the breadcrumb passed in the query.
                     Or in case of an unexpected error return to home page with an error message.
    """
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    success = remove_word(word_id)
    if not success:
        redirect('/?error=Unexpected+error+occurred+during+delete+of+word+please+try+again+later')
    breadcrumb = request.args.get("breadcrumb")
    return redirect(f'{breadcrumb}')


@app.route('/word/<word_id>', methods=["POST", "GET"])
def render_word(word_id):
    """
        This end point renders the word page.
    :methods
        GET:/word/<word_id>
        POST:/word/<word_id>
    :calls (located in services.py module)
        validate_update_word - To validate request and update the word (POST requests)
        get_dictionary_word - To get the corresponding word (GET requests)
    :param word_id:
        type: int
        required: true
        description: The id of the word in the dictionary table
    :return: renders the word.html
        description: Renders the word.html template processed with following:
            word_details: The dictionary word details identified by the word_id
            logged_in: A boolean describing whether the user is logged in or not
            error: Error message for the UI and URL query string
            image_name: Tne image file name corresponding to the word
            checked: Used to add HTML 'checked' against for Year Level element to show selected year level radio button
            category_list: List of categories to be displayed on the sidebar
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            breadcrumb: The breadcrumb from query string for tracking where it is coming from
            current_user: Current username and type to be displayed in the top right in the UI
    """
    breadcrumb = request.args.get("breadcrumb")
    if request.method == "POST":
        is_valid, return_url = validate_update_word(request.form, word_id, breadcrumb)
        if not is_valid:
            return redirect(return_url)
        return redirect(f'/word/{word_id}?breadcrumb={breadcrumb}')
    word = get_dictionary_word(word_id)
    if word is None:
        return redirect('/?error=Word+could+not+be+retrieved+unexpected+error')
    error = request.args.get('error')
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('word.html',
                           word_details=word,
                           logged_in=is_logged_in(),
                           error=error,
                           image_name=get_image_filename(word[0][2]),
                           checked=get_checked(word[0][4]),
                           category_list=get_categories(),
                           allow_edit=allow_edit(),
                           breadcrumb=breadcrumb,
                           current_user=get_user())


@app.route('/delete_category/<category_id>')
def render_delete_category(category_id):
    """
        This end point renders delete category page
    :methods
        GET:/delete_category/<category_id>
    :param category_id:
        type: int
        required: true
        description: The id of the category in the category table
    :calls (located in services.py module)
        get_category_words - To validate request and update the word (GET requests)
    :return: renders the delete_category.html
        description: Renders the delete_category.html template processed with following:
            category_words: The words corresponding to the category_id passed in
            logged_in: A boolean describing whether the user is logged in or not
            image_name: Tne image file name corresponding to the word
            category_list: List of categories to be displayed on the sidebar
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    category_words = get_category_words(category_id)
    if category_words is None:
        return redirect('/?error=Unexpected+error')
    return render_template('delete_category.html',
                           category_words=category_words,
                           logged_in=is_logged_in(),
                           image_names=get_image_filenames(category_words),
                           category_list=get_categories(),
                           allow_edit=allow_edit(),
                           current_user=get_user())


@app.route('/action_delete_category/<category_id>', methods=["POST"])
def action_delete_category(category_id):
    """
        NOTE: This POST only method is for internal use only.
              It is used in the confirm delete mini form to POST and action deleting a category
    :methods
        POST:/action_delete_category/<category_id>
    :calls (located in services.py module)
        remove_category - To remove category identified by category_id (POST requests)
    :param category_id:
        type: int
        required: true
        description: The id of the category in the category table
    :return: redirect
        description: Returns a redirect home page.
                     Or in case of an unexpected error return to home page with an error message.
    """
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    success = remove_category(category_id)
    if not success:
        redirect('/?error=Unexpected+error+occurred+during+delete+of+category+please+try+again+later')
    return redirect('/')


@app.route('/add_category', methods=["POST", "GET"])
def render_add_category():
    """
        This end point renders the add category page
    :methods
        GET:/add_category
        POST:/add_category
    :calls (located in services.py module)
        validate_add_category - To validate request and add the category (POST requests)
    :return: renders the add_category.html
        description: Renders the add_category.html template processed with following:
            logged_in: A boolean describing whether the user is logged in or not
            category_list: List of categories to be displayed on the sidebar
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            error: Error message for the UI and URL query string
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    if request.method == "POST":
        is_valid, return_url = validate_add_category(request.form)
        if not is_valid:
            return redirect(return_url)
        return redirect('/add_category')
    error = request.args.get('error')
    return render_template('add_category.html',
                           logged_in=is_logged_in(),
                           category_list=get_categories(),
                           allow_edit=allow_edit(),
                           error=error,
                           current_user=get_user())


@app.route('/category/<category_id>', methods=["POST", "GET"])
def render_category(category_id):
    """
        This end point renders the category page
    :methods
        GET:/category/<category_id>
        POST:/category/<category_id>
    :calls (located in services.py module)
        validate_add_word - To validate request and add the word (POST requests)
        get_category_words - To get all the corresponding words for the specified category id (GET requests)
    :param category_id:
        type: int
        required: true
        description: The id of the category in the category table
    :return: renders the category.html
        description: Renders the category.html template processed with following:
            category_words: All the corresponding words for the specified category id
            logged_in: A boolean describing whether the user is logged in or not
            image_name: Tne image file name corresponding to the word
            error: Error message for the UI and URL query string
            category_list: List of categories to be displayed on the sidebar
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if request.method == "POST":
        is_valid, return_url = validate_add_word(request.form, category_id)
        if not is_valid:
            return redirect(return_url)
        return redirect(f'/category/{category_id}')
    words = get_category_words(category_id)
    if words is None:
        return redirect('/?error=Category+could+not+be+retrieved+unexpected+error')
    error = request.args.get('error')
    return render_template('category.html',
                           category_words=words,
                           logged_in=is_logged_in(),
                           image_names=get_image_filenames(words),
                           error=error,
                           category_list=get_categories(),
                           allow_edit=allow_edit(),
                           current_user=get_user())


@app.route('/signup', methods=["POST", "GET"])
def render_signup():
    """
        This end point renders the signup page
    :methods
        GET:/signup
        POST:/signup
    :calls (located in services.py module)
        validate_signup_user - To validate request and signup the user (POST requests)
    :return: renders the signup.html
        description: Renders the signup.html template processed with following:
            logged_in: A boolean describing whether the user is logged in or not
            category_list: List of categories to be displayed on the sidebar
            error: Error message for the UI and URL query string
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        is_valid, return_url = validate_signup_user(request.form)
        if not is_valid:
            return redirect(return_url)
        return redirect('/login')
    error = request.args.get('error')
    return render_template('signup.html',
                           logged_in=is_logged_in(),
                           category_list=get_categories(),
                           error=error,
                           current_user=get_user())


@app.route('/logout')
def logout():
    """
        This end point logs the user out by removing his credentials from session
        and returns the user back to the home page
    :methods
        GET:/logout
    :return: redirect
        description: Returns redirect to home page
    """
    [session.pop(key) for key in list(session.keys())]
    return redirect('/')


@app.route('/login', methods=["POST", "GET"])
def render_login():
    """
        This end point renders the login page
    :methods
        GET:/login
        POST:/login
    :calls (located in services.py module)
        validate_and_login_user - To validate request and log the user in (POST requests)
    :return: renders the login.html
        description: Renders the login.html template processed with following:
            logged_in: A boolean describing whether the user is logged in or not
            category_list: List of categories to be displayed on the sidebar
            error: Error message for the UI and URL query string
            current_user: Current username and type to be displayed in the top right in the UI
    """
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        if not validate_and_login_user(request.form):
            return redirect('/login?error=Email+invalid+or+password+incorrect')
        return redirect('/')
    error = request.args.get('error')
    return render_template('login.html',
                           logged_in=is_logged_in(),
                           category_list=get_categories(),
                           error=error,
                           current_user=get_user())


@app.route('/')
def render_home():
    """
        This end point renders the home page
    :methods
        GET:/
    :return: renders the home.html
        description: Renders the home.html template processed with following:
            logged_in: A boolean describing whether the user is logged in or not
            allow_edit: A boolean describing whether the user is allowed to edit dictionary data
            category_list: List of categories to be displayed on the sidebar
            current_user: Current username and type to be displayed in the top right in the UI
    """
    return render_template('home.html',
                           logged_in=is_logged_in(),
                           allow_edit=allow_edit(),
                           category_list=get_categories(),
                           current_user=get_user())


if __name__ == '__main__':
    app.run()
