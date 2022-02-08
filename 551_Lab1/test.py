import os
import psycopg2

from flask import Flask, render_template, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# checking environment variables
print(os.environ['DATABASE_URL'])
print(os.environ['FLASK_APP'])

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://auruxcdprcbthb' \
                                        ':7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9@ec2-3-222' \
                                        '-127-58.compute-1.amazonaws.com:5432/da76or2kuol1r '
# set up database
engine = create_engine('postgresql://auruxcdprcbthb:7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9'
                       '@ec2-3-222-127-58.compute-1.amazonaws.com:5432/da76or2kuol1r, echo = False')
# db = scoped_session(sessionmaker(bind=engine))

db = SQLAlchemy(app)

conn = psycopg2.connect(
    host="ec2-3-222-127-58.compute-1.amazonaws.com",
    database="da76or2kuol1r",
    user="auruxcdprcbthb",
    password="7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9")

cur = conn.cursor()
# already created users database
# cur.execute("CREATE TABLE users(userID int NOT NULL PRIMARY KEY, username varchar(255) NOT NULL, password varchar("
#            "255) NOT NULL);")


@app.route('/')
def index():
    return render_template('index_book_search.html')


@app.route('/book_search', methods=["GET", "POST"])
def book_search():
    return render_template('index_book_search.html')


@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    return render_template('user_login.html')


@app.route('/user_profile', methods=["GET", "POST"])
def user_profile():
    return render_template('user_profile.html')


@app.route('/user_register', methods=["GET", "POST"])
def user_register():
    return render_template('user_register.html')


conn.commit()
conn.close()

if __name__ == '__main__':
    app.run()
