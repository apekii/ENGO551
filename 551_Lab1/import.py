import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# read csv file
books = pd.read_csv('books.csv')

# connect to database
engine = create_engine('postgresql://auruxcdprcbthb:7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9'
                       '@ec2-3-222-127-58.compute-1.amazonaws.com:5432/da76or2kuol1r')

conn = psycopg2.connect(
    host="ec2-3-222-127-58.compute-1.amazonaws.com",
    database="da76or2kuol1r",
    user="auruxcdprcbthb",
    password="7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9")

# create object that can execute SQL commands
cur = conn.cursor()

# create table, ensuring the database has same columns as csv
# cur.execute("""
#    CREATE TABLE books(
#    isbn integer PRIMARY KEY,
#    title text,
#    author text,
#    year integer)
# """)

# commit changes to table
# conn.commit()

# import books to table
books.to_sql('books_csv', engine)

# close connections
cur.close()
conn.close()
