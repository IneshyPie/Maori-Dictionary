# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Program name      : Maori Dictionary
# Author            : Inesh Bhanuka
# Date              : 2021-05-12
# Project           : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~
# Program imports
# ~~~~~~~~~~~~~~~
from services import *
from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt


# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~

app = Flask(__name__)  # Create application object
bcrypt = Bcrypt(app)  # Builds the password security platform
app.secret_key = "Duckyweu"  # The security key used


@app.route('/action_delete_category/<id>', methods=["POST"])
def action_delete_category(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    success = remove_category(id)
    if not success:
        redirect('/?error=Unknown+error+occurred+during+delete+of+category+please+try+again+later')
    return redirect('/')


@app.route('/action_delete_word/<id>', methods=["POST"])
def action_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    success = remove_word(id)
    if not success:
        redirect('/?error=Unknown+error+occurred+during+delete+of+word+please+try+again+later')
    breadcrumb = request.args.get("breadcrumb")
    return redirect(f'{breadcrumb}')


@app.route('/search/<letter>', methods=["POST", "GET"])
def render_search(letter):
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
        return redirect(f'/search/~?error=Unknown+error+has+occurred+during+search+please+try+again+later')
    return render_template('search.html',
                           search_results=search_results,
                           logged_in=is_logged_in(),
                           letter=letter,
                           category_list=get_categories(),
                           selected=get_selected(search_letter),
                           allow_edit=allow_edit(),
                           error=error,
                           current_user=get_user())


@app.route('/category/<id>', methods=["POST", "GET"])
def render_category(id):
    if request.method == "POST":
        is_valid, return_url = validate_add_word(request.form, id)
        if not is_valid:
            return redirect(return_url)
        return redirect(f'/category/{id}')
    words = get_category_words(id)
    if words is None:
        return redirect('/?error=Category+could+not+be+retrieved+unknown+error')
    image_names = get_image_filenames(words)
    error = request.args.get('error')
    return render_template('category.html'
                           , category_words=words
                           , logged_in=is_logged_in()
                           , image_names=image_names
                           , error=error
                           , category_list=get_categories()
                           , allow_edit=allow_edit()
                           , current_user=get_user())


@app.route('/word/<id>', methods=["POST", "GET"])
def render_word(id):
    if request.method == "POST":
        is_valid, return_url = validate_update_word(request.form, id)
        if not is_valid:
            return redirect(return_url)
        breadcrumb = request.args.get("breadcrumb")
        return redirect(f'/word/{id}?breadcrumb={breadcrumb}')
    word = get_dictionary_word(id)
    if word is None:
        return redirect('/?error=Word+could+not+be+retrieved+unknown+error')
    error = request.args.get('error')
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('word.html'
                           , word_details=word
                           , logged_in=is_logged_in()
                           , error=error
                           , image_name=get_image_filename(word[0][2])
                           , checked=get_checked(word[0][4])
                           , category_list=get_categories()
                           , allow_edit=allow_edit()
                           , breadcrumb=breadcrumb
                           , current_user=get_user())


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
                           category_list=get_categories(),
                           allow_edit=allow_edit(),
                           current_user=get_user())


@app.route('/delete_word/<id>')
def render_delete_word(id):
    if not is_logged_in() or not allow_edit():
        return redirect('/')
    word = get_dictionary_word(id)
    if word is None:
        return redirect('/?error=Word+does+not+exist+or+unknown+error')
    breadcrumb = request.args.get("breadcrumb")
    if breadcrumb is None:
        breadcrumb = "/"
    return render_template('delete_word.html'
                           , word_list=word
                           , logged_in=is_logged_in()
                           , image_name=get_image_filename(word[0][2])
                           , category_list=get_categories()
                           , breadcrumb=breadcrumb,
                           allow_edit=allow_edit()
                           , current_user=get_user())


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
    return render_template('add_category.html'
                           , logged_in=is_logged_in()
                           , category_list=get_categories()
                           , allow_edit=allow_edit()
                           , error=error
                           , current_user=get_user())


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
                           , category_list=get_categories()
                           , error=error
                           , current_user=get_user())


@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    return redirect('/')


@app.route('/login', methods=["POST", "GET"])
def render_login():
    if is_logged_in():
        return redirect('/')
    if request.method == "POST":
        if not validate_login(request.form):
            return redirect('/login?error=Email+invalid+or+password+incorrect')
        return redirect('/')
    error = request.args.get('error')
    return render_template('login.html'
                           , logged_in=is_logged_in()
                           , category_list=get_categories()
                           , error=error
                           , current_user=get_user())


@app.route('/')
def render_home():
    return render_template('home.html'
                           , logged_in=is_logged_in()
                           , allow_edit=allow_edit()
                           , category_list=get_categories()
                           , current_user=get_user())


if __name__ == '__main__':
    app.run()
