import csv
from pathlib import Path

category_list = []
image_list = []

def load_image_filenames():
    for path in Path('..\..\static\images').iterdir():
        #print(path.name)
        image_list.append(path.name)
        

def sql_encode(input_string):
    return input_string.replace("'","''")


def find_category_id(category_name):
    last_category_id = 0
    for category in category_list:
        last_category_id = category[0]
        if category[1] == category_name:
            return category[0]
    category_list.append([last_category_id + 1, category_name])
    return last_category_id + 1
    

def find_image_filename(english_name):
    for image_filename in image_list:
        if image_filename == english_name + ".jpg":
            return image_filename
    return "noimage.png"


def dictionary_initial_load():
    with open('2_dictionary_initial_load.sql', 'w') as f:
        f.write(f"DELETE FROM dictionary;\n")
        f.write(f"DELETE FROM sqlite_sequence WHERE name = 'dictionary';\n\n")
        with open('Vocab_List.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    print(f'Maori: {row[0]}, English: {row[1]}, Category: {row[2]} Definition: {row[3]} Level: {row[4]}')
                    data_row = f"INSERT INTO dictionary(maori, english, description, level, category_id, image_name, user_id, date_added) VALUES('{row[0]}','{row[1]}', '{sql_encode(row[3])}', '{row[4]}', '{find_category_id(row[2].title())}', '{find_image_filename(row[1])}', null, date());\n"
                    f.write(data_row)
                    line_count += 1
            print(f'Processed {line_count} lines.')


def category_initial_load():
    with open('1_category_initial_load.sql', 'w') as f:
        f.write(f"DELETE FROM category;\n")
        f.write(f"DELETE FROM sqlite_sequence WHERE name = 'category';\n\n")
        category_count = 0
        for category in category_list:
            print(f'Category_id: {category[0]}, Category_name: {category[1]}')
            data_row = f"INSERT INTO category(id, category_name) VALUES({category[0]},'{category[1]}');\n"
            f.write(data_row)
            category_count += 1
        print(f'Processed {category_count} lines.')


load_image_filenames()
dictionary_initial_load()
category_initial_load()

