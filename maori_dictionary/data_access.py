# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application name      : Maori Dictionary
# Program name          : data_access.py
# Program description   : This module provides all database functions required for the web services.
# Author                : Inesh Bhanuka
# Date                  : 2022-05-30
# Project               : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sqlite3
from sqlite3 import Error


# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~
DATABASE = "database/dictionary.db"


def get_connection(db_file):
    """
        This function is used to get a connection to the specified database. If a connection
        could not be obtained the error details will be printed on the console.

    :param db_file:
        type: database file
        required: true
        description: The database file
    :return: A connection to the database.
    """
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


def execute_query(query, args=None):
    """
        This is a generic function used to run a SQL SELECT against the database.
        The function may be called with arguments or without arguments
    :param query:
        type: SQL query
        required: true
        description: The query to be executed on the database
    :param args:
        type: arguments list
        required: false
        description: The optional arguments for query
    :calls
        get_connection - To retrieves a connection to the database
    :return: A list of tuples consisting of query results or Error if
        an error occurred during execution of the statement.
    """
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
    """
        This is a generic function used to run a SQL command (e.g. INSERT, UPDATE etc.)
        against the database. The function may be called with arguments or without
        arguments
    :param command:
        type: SQL statement
        required: true
        description: The sql statement to be executed on the database
    :param args:
        type: arguments list
        required: false
        description: The optional arguments for the command
    :calls
        get_connection - To retrieves a connection to the database
    :return: An Error only if an error occurred during execution
             of the statement.
    """
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


def get_allow_edit(email):
    """
        This function checks if the user is allowed to edit dictionary entries
    :param email:
        type: string
        required: true
        description: The email address of the user
    :calls
        execute_query - Executes a query on the database
    :return: A boolean value
        True - If user is allowed to edit dictionary entries
        False - If user is NOT allowed to edit dictionary entries
    """
    query = """SELECT allow_edit
               FROM user_type
               WHERE id = (SELECT user_type_id FROM user_details WHERE email = ?)"""
    query_results = execute_query(query, [email])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results[0][0]


def get_category_list():
    """
        This function retrieves all tuples of the category table
    :calls
        execute_query - Executes a query on the database
    :return: A list of category table tuples
    """
    category_list = execute_query("SELECT * FROM category ORDER BY category_name")
    if issubclass(type(category_list), Error):
        return []
    return category_list


def get_browse_results(letter):
    """
        This function retrieves all tuples of the dictionary table that has a maori word
        starting with the letter supplied. It also combines it with last updated
        user's first and last names if available
    :calls
        execute_query - Executes a query on the database
    :return: A list of tuples or None in case of an unexpected error
    """
    query = """SELECT d.id, d.maori, d.english, d.level, d.date_added, ifnull(u.first_name, ''), ifnull(u.last_name, '')
               FROM dictionary d
               LEFT JOIN user_details u on d.user_id = u.id
               WHERE maori LIKE ?
               ORDER BY maori, english"""
    query_results = execute_query(query, [f"{letter}%"])
    if issubclass(type(query_results), Error):
        return None
    return query_results


def get_search_results(maori, english, level, most_recent):
    """
        This function provides a feature search functionality.
        It constructs an SQL SELECT query based on the search criteria passed in
        to as arguments to this function.
        Results are always ordered by maori and then english however, if the most_recent = "1"
        then it is first ordered in the descending order of the date_added column and then within
        that they are further ordered in maori and then english.
        If the most_recent = "1" then the results are also limited to 20 tuples
    :param maori:
        type: string
        required: true (but can be an empty string)
        description: The maori search phrase ready for a LIKE match. e.g "hei%"
    :param english:
        type: string
        required: true (but can be an empty string)
        description: The english search phrase ready for a LIKE match. e.g "chick%"
    :param level:
        type: string
        required: true
        description: Must be =>
                        "0" = Don't search on level
                        "1", "2" ... "10" = for specific year level search
    :param most_recent:
        type: string
        required: true
        description: Must be =>
                     "0" = Don't use in search
                     "1" = Sort by date_added in descending order and limit to the top 20 tuples
    :calls
        execute_query - Executes a query on the database
    :return: A list of tuples consisting of search results, an empty list when nothing is found
            or Error if an unexpected error occurred during execution of the statement.
    """
    query = ""
    args = []
    maori_search = f"{maori}%"
    english_search = f"{english}%"
    level_search = f"{level}"
    if (maori != "" or english != "" or level != "0") and most_recent == "1":
        if maori != "" and english != "" and level == "0":
            # Scenario 1 : Searching by maori and english and get most_recent
            query = """SELECT d.id,
                    d.maori,
                    d.english,
                    d.level,
                    d.date_added,
                    ifnull(u.first_name, ''),
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND english LIKE ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20
                    """
            args = [maori_search, english_search]
        if maori != "" and english == "" and level != "0":
            # Scenario 2 : Searching by maori and level and get most_recent
            query = """SELECT d.id, 
                    d.maori,
                    d.english,
                    d.level,
                    d.date_added,
                    ifnull(u.first_name, ''),
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND level = ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20
                    """
            args = [maori_search, level_search]
        if maori == "" and english != "" and level != "0":
            # Scenario 3 : Searching by english and level and get most_recent
            query = """SELECT d.id,
                    d.maori, d.english,
                    d.level,
                    d.date_added,
                    ifnull(u.first_name, ''),
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE english LIKE ?
                        AND level = ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20
                    """
            args = [english_search, level_search]
        if maori != "" and english == "" and level == "0":
            # Scenario 4 : Searching by maori and get most_recent
            query = """SELECT d.id,
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20 
                    """
            args = [maori_search]
        if maori == "" and english != "" and level == "0":
            # Scenario 5 : Searching by english and get most_recent
            query = """SELECT d.id,
                    d.maori,
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE english LIKE ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20
                    """
            args = [english_search]
        if maori == "" and english == "" and level != "0":
            # Scenario 6 : Searching by level and get most_recent
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level,
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE level = ?
                    ORDER BY date_added DESC, maori, english
                    LIMIT 20
                    """
            args = [level_search]
        if maori != "" and english != "" and level != "0":
            # Scenario 7 : Searching by maori and english and level and get most_recent
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND english LIKE ?
                        AND level = ?
                     ORDER BY date_added DESC, maori, english
                     LIMIT 20
                     """
            args = [maori_search, english_search, level_search]
    elif (maori != "" or english != "" or level != "0") and most_recent == "0":
        if maori != "" and english != "" and level == "0":
            # Scenario 8 : Searching by maori and english
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND english LIKE ?
                    ORDER BY maori, english
                    """
            args = [maori_search, english_search]
        if maori != "" and english == "" and level != "0":
            # Scenario 9 : Searching by maori and level
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND level = ?
                    ORDER BY maori, english
                    """
            args = [maori_search, level_search]
        if maori == "" and english != "" and level != "0":
            # Scenario 10 : Searching by english and level
            query = """SELECT d.id,
                    d.maori,
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE english LIKE ? 
                        AND level = ?
                    ORDER BY maori, english
                    """
            args = [english_search, level_search]
        if maori != "" and english == "" and level == "0":
            # Scenario 11 : Searching by maori
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                    ORDER BY maori, english 
                    """
            args = [maori_search]
        if maori == "" and english != "" and level == "0":
            # Scenario 12 : Searching by english and level
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE english LIKE ?
                    ORDER BY maori, english
                    """
            args = [english_search]
        if maori == "" and english == "" and level != "0":
            # Scenario 13 : Searching by level
            query = """SELECT d.id, 
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE level = ?
                    ORDER BY maori, english
                    """
            args = [level_search]
        if maori != "" and english != "" and level != "0":
            # Scenario 14 : Searching by maori and english and level
            query = """SELECT d.id,
                    d.maori, 
                    d.english, 
                    d.level, 
                    d.date_added, 
                    ifnull(u.first_name, ''), 
                    ifnull(u.last_name, '')
                    FROM dictionary d
                    LEFT JOIN user_details u on d.user_id = u.id
                    WHERE maori LIKE ?
                        AND english LIKE ? 
                        AND level = ?
                    ORDER BY maori, english
                    """
            args = [maori_search, english_search, level_search]
    elif most_recent == "1":
        # Scenario 15 : Searching just for the most_recent
        query = """SELECT d.id, 
                d.maori, 
                d.english, 
                d.level, 
                d.date_added, 
                ifnull(u.first_name, ''), 
                ifnull(u.last_name, '')
                FROM dictionary d
                LEFT JOIN user_details u on d.user_id = u.id
                ORDER BY date_added DESC, maori, english
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


def get_word(word_id):
    """
        This function gets the word details from the database for the supplied word id
        supplemented with the last updated user details
    :param word_id:
        type: int
        required: true
        description: The id of the word
    :calls
        execute_query - Executes a query on the database
    :return: A list containing one tuple from query results or None when nothing is found
            or if an unexpected error occurred during execution of the statement.
    """
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


def get_words(category_id):
    """
        This function gets the words details from the database for the supplied category id
        ordered in the maori and then english order
    :param category_id:
        type: int
        required: true
        description: The id of the category
    :calls
        execute_query - Executes a query on the database
    :return: A list of tuples consisting of the query results or None when nothing is found
            or if an unexpected error occurred during execution of the statement.
    """
    query = """SELECT c.category_name, d.maori, d.english, d.id, c.id
               FROM category c
               LEFT JOIN dictionary d on c.id = d.category_id
               WHERE c.id = ?
               ORDER BY maori, english"""
    query_results = execute_query(query, [category_id])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results


def get_user_details(email):
    """
        This function gets the username and type details from the database corresponding
        to the email address supplied
    :param email:
        type: string
        required: true
        description: The email address
    :calls
        execute_query - Executes a query on the database
    :return: A list containing one tuple from query results or None when nothing is found
            or if an unexpected error occurred during execution of the statement.
    """
    query = """SELECT ud.first_name, ud.last_name, ud.password, ut.user_type 
               FROM user_details ud
               JOIN user_type ut on ud.user_type_id = ut.id 
               WHERE ud.email = ?"""
    query_results = execute_query(query, [email])
    if issubclass(type(query_results), Error) or len(query_results) == 0:
        return None
    return query_results


def add_word(maori, english, description, level, category_id, email):
    """
        This function inserts a new word to the dictionary table.
        The user id of the user adding the word is also retrieved based on the email
        supplied and is included in the dictionary record
    :param maori:
        type: string
        required: true
        description: The maori word
    :param english:
        type: string
        required: true
        description: The english word
    :param description:
        type: string
        required: true
        description: The description of the dictionary entry
    :param level:
        type: int
        required: true
        description: The year level
    :param category_id:
        type: int
        required: true
        description: The category id of the category the word belongs to
    :param email:
        type: string
        required: true
        description: The email address
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the insert
    """
    command = """INSERT INTO dictionary (maori, english, description, level, category_id, date_added, user_id)
                 VALUES (?, ?, ?, ?, ?, date(), (SELECT id FROM user_details WHERE email = ?))"""
    args = [maori, english, description, level, category_id, email]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


def add_category(category_name):
    """
        This function inserts a new category to the category table
    :param category_name:
        type: string
        required: true
        description: The category name
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the insert
    """
    response = execute_command("INSERT INTO category (category_name) VALUES (?)", [category_name])
    if issubclass(type(response), Error):
        return False
    return True


def add_user(first_name, last_name, email, hashed_password, user_type):
    """
        This function inserts a new user to the user_details table.
        The user_type id of the user is also retrieved based on the user_type
        supplied and is included in the user_details record
    :param first_name:
        type: string
        required: true
        description: The first name of the user
    :param last_name:
        type: string
        required: true
        description: The last name of the user
    :param email:
        type: string
        required: true
        description: The email address of the user
    :param hashed_password:
        type: string
        required: true
        description: The hashed_password of the user
    :param user_type:
        type: string
        required: true
        description: The user_type e.g. Teacher
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the insert
    """
    command = """INSERT INTO user_details 
                 (first_name, last_name, email, password, user_type_id) 
                 VALUES (?,?,?,?,(SELECT id from user_type WHERE user_type = ?))"""
    args = [first_name, last_name, email, hashed_password, user_type]
    response = execute_command(command, args)
    if issubclass(type(response), Error):
        return False
    return True


def update_word(maori, english, description, level, email, word_id):
    """
        This function updates the word in the dictionary table identified by the word_id.
        The user id of the user adding the word is also retrieved based on the email
        supplied and is updated in the dictionary record.
        The date_added column will also be updated with the current date
        The statement also checked if any data supplied is actually changing, if so only
        the record is updated
    :param maori:
        type: string
        required: true
        description: The maori word
    :param english:
        type: string
        required: true
        description: The english word
    :param description:
        type: string
        required: true
        description: The description of the dictionary entry
    :param level:
        type: int
        required: true
        description: The year level
    :param email:
        type: string
        required: true
        description: The email address
    :param word_id:
        type: int
        required: true
        description: The word id of the directory word to be updated
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the update
    """
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


def delete_category(category_id):
    """
        This function deletes the category record from category table identified by
        the category id supplied
    :param category_id:
        type: int
        required: true
        description: The category id of the category record to be deleted
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the delete action
    """
    response = execute_command("DELETE FROM category WHERE id = ?", [category_id])
    if issubclass(type(response), Error):
        return False
    return True


def delete_word(word_id):
    """
        This function deletes the word from category table identified by
        the word id supplied
    :param word_id:
        type: int
        required: true
        description: The word id of the dictionary entry to be deleted
    :calls
        execute_command - Executes a command on the database
    :return: Returns True of False indicating the success of the delete action
    """
    response = execute_command("DELETE FROM dictionary WHERE id = ?", [word_id])
    if issubclass(type(response), Error):
        return False
    return True
