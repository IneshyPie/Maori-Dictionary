# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Application name      : Maori Dictionary
# Program name          : create_initial_load_scripts.py
#                         NOTE: This is just a one off data load script creation module only
#                               and not a part of the application.
# Author                : Inesh Bhanuka
# Date                  : 2022-05-30
# Project               : 91902 (NCEA L3 Internal)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import csv


# ~~~~~~~~~~~~~~~~~
# Declare constants
# ~~~~~~~~~~~~~~~~~
SCRIPT_DIR = "scripts"
DATA_DIR = "data"
DATABASE = "database/dictionary.db"
DATA_FILE = "Vocab_List.csv"
CATEGORY_TABLE_SCRIPT = "1_category_initial_load.sql"
DICTIONARY_TABLE_SCRIPT = "2_dictionary_initial_load.sql"


category_list = []
image_list = []


def sql_encode(input_string):
    return input_string.replace("'", "''")


def find_category_id(category_name):
    last_category_id = 0
    for category in category_list:
        last_category_id = category[0]
        if category[1] == category_name:
            return category[0]
    category_list.append([last_category_id + 1, category_name])
    return last_category_id + 1


def dictionary_initial_load():
    with open(f'{SCRIPT_DIR}/{DICTIONARY_TABLE_SCRIPT}', 'w') as f:
        f.write(f"DELETE FROM dictionary;\n")
        f.write(f"DELETE FROM sqlite_sequence WHERE name = 'dictionary';\n\n")
        with open(f'{DATA_DIR}/{DATA_FILE}') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                else:
                    print(f'Maori:{row[0]}, English:{row[1]}, Category:{row[2]} Definition:{row[3]} Level:{row[4]}')
                    data_row = f"INSERT INTO " \
                               f"dictionary(maori, english, description, level, category_id, user_id, date_added) " \
                               f"VALUES('{row[0]}'," \
                               f"'{row[1]}', " \
                               f"'{sql_encode(row[3])}', " \
                               f"'{row[4]}', " \
                               f"'{find_category_id(row[2].title())}', " \
                               f"null, " \
                               f"date());\n"
                    f.write(data_row)
                line_count += 1
            print(f'Dictionary table data : Processed {line_count} lines.\n')


def category_initial_load():
    with open(f'{SCRIPT_DIR}/{CATEGORY_TABLE_SCRIPT}', 'w') as f:
        f.write(f"DELETE FROM category;\n")
        f.write(f"DELETE FROM sqlite_sequence WHERE name = 'category';\n\n")
        category_count = 0
        for category in category_list:
            print(f'Category_id:{category[0]}, Category_name:{category[1]}')
            data_row = f"INSERT INTO " \
                       f"category(id, category_name) " \
                       f"VALUES({category[0]}," \
                       f"'{category[1]}');\n"
            f.write(data_row)
            category_count += 1
        print(f'Category table data : Processed {category_count} lines.')


dictionary_initial_load()
category_initial_load()
