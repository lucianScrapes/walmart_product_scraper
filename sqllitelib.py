import sqlite3
from sqlite3 import Error
import os.path
from os import path

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    sql_create_products_table = """ CREATE TABLE IF NOT EXISTS products (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        price text
                                    ); """
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql_create_products_table)
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")
    return conn


def insertProduct(db_connection,prod_id,prod_name,prod_price):
    cur = db_connection.cursor()
    try:
        cur.execute("INSERT INTO products VALUES (?, ?, ?);", (prod_id, prod_name, prod_price))
    except sqlite3.IntegrityError:
        print("product id already exists")
    db_connection.commit()
