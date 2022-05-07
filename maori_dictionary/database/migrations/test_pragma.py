from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        return connection
    except Error as e:
        print(e)
    return None


con = create_connection("..\dictionary.db")
sql = "DELETE FROM category WHERE id=3"
cur = con.cursor()
try:
    cur.execute(sql)
except sqlite3.IntegrityError:
    print("error")
con.commit()
con.close()
        

