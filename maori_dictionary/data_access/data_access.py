# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Program name      : Maori Dictionary
# Author            : Inesh Bhanuka
# Date              : 2021-05-12
# Project           : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~
# Program imports
# ~~~~~~~~~~~~~~~
import sqlite3
from sqlite3 import Error
import glob
import os

# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~
DATABASE = "database/dictionary.db"
IMAGE_PATH = "static\\images\\"


def get_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


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


def get_allow_edit(email):
    query = """SELECT allow_edit
               FROM user_type
               WHERE id = (SELECT user_type_id FROM user_details WHERE email = ?)"""
    query_results = execute_query(query, [email])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results[0][0]


def get_category_list():
    category_list = execute_query("SELECT * FROM category ORDER BY category_name")
    if issubclass(type(category_list), Error):
        return []
    return category_list


def get_search_results(maori, english, level, most_recent):
    query = ""
    args = []
    maori_search = f"{maori}%"
    english_search = f"{english}%"
    level_search = f"{level}"
    if (maori != "" or english != "" or level != "0") and most_recent == "1":
        if maori != "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     english LIKE ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20
                     """
            args = [maori_search, english_search]
        if maori != "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ? AND 
                     level = ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20
                     """
            args = [maori_search, level_search]
        if maori == "" and english != "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ? AND 
                     level = ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20
                     """
            args = [english_search, level_search]
        if maori != "" and english == "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     maori LIKE ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20 
                     """
            args = [maori_search]
        if maori == "" and english != "" and level == "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     english LIKE ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20
                     """
            args = [english_search]
        if maori == "" and english == "" and level != "0":
            query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
                     FROM dictionary d
                     LEFT JOIN user_details u on d.user_id = u.id
                     WHERE 
                     level = ?
                     ORDER BY date_added DESC, maori
                     LIMIT 20
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
                     ORDER BY date_added DESC, maori
                     LIMIT 20
                     """
            args = [maori_search, english_search, level_search]
    elif (maori != "" or english != "" or level != "0") and most_recent == "0":
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
                 ORDER BY date_added DESC, maori
                 LIMIT 20
                 """
    else:
        return []
    if len(args) == 0:
        query_results = execute_query(query)
    else:
        query_results = execute_query(query, args)
    if issubclass(type(query_results), Error):
        return None
    return query_results


def delete_category(category_id):
    response = execute_command("DELETE FROM category WHERE id = ?", [category_id])
    if issubclass(type(response), Error):
        return False
    return True


def delete_word(word_id):
    response = execute_command("DELETE FROM dictionary WHERE id = ?", [word_id])
    if issubclass(type(response), Error):
        return False
    return True


def get_browse_results(letter):
    query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE maori LIKE ?
               ORDER BY maori"""
    query_results = execute_query(query, [f"{letter}%"])
    if issubclass(type(query_results), Error):
        return None
    return query_results


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


def add_user(first_name, last_name, email, hashed_password, user_type):
    command = """INSERT INTO user_details 
                 (first_name, last_name, email, password, user_type_id) 
                 VALUES (?,?,?,?,(SELECT id from user_type WHERE user_type = ?))"""
    args = [first_name, last_name, email, hashed_password, user_type]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


def get_password(email):
    query_results = execute_query("SELECT password FROM user_details WHERE email = ?", [email])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results[0][0]
