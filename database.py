import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']

global cursor

def create_table():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tbl_user (UserID int);")
    print('table created...')