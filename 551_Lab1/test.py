import os
import flask
import psycopg2

from flask import Flask, render_template, request, url_for, session
from sqlalchemy import create_engine
from werkzeug.utils import redirect
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

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

# set session secret key
app.secret_key = 'ENGO551_Lab1'

# set up database connection **MAKE SURE ITS postgresql AND NOT postgres**
engine = create_engine('postgresql://auruxcdprcbthb:7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9'
                       '@ec2-3-222-127-58.compute-1.amazonaws.com:5432/da76or2kuol1r')
db = scoped_session(sessionmaker(bind=engine))

conn = psycopg2.connect(
    host="ec2-3-222-127-58.compute-1.amazonaws.com",
    database="da76or2kuol1r",
    user="auruxcdprcbthb",
    password="7ff31e2174704980e587ea5a91ef8b11a63b69ffe29b034a6b42a8c7318272e9")

cur = conn.cursor()

# already created users database
# cur.execute("CREATE TABLE users(username varchar(255) NOT NULL PRIMARY KEY, password varchar("
#            "255) NOT NULL);")


# routes
@app.route('/')
def index():
    return render_template('index_book_search.html')


@app.route('/user_login', methods=["GET", "POST"])
# make sure username and password are not misspelled (there's nothing coded for that)
def user_login():
    # clear session, in case someone has logged in already
    session.clear()

    # get username
    username = request.form.get("username")

    if request.method == "POST":

        # username/password not inputted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("error.html", message="Your username and/or password was empty.")

        # check database for username/password
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username})

        result = rows.fetchone()

        # remember user
        session["user_name"] = result[0]

        return render_template('user_profile.html')
    else:
        return render_template('user_login.html')


@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return render_template('index_book_search.html')


@app.route('/user_profile', methods=["GET", "POST"])
def user_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur.execute('INSERT INTO users (username,password) VALUES (%s, %s)',
                    (username, password))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('user_login'))

    return render_template('user_profile.html')


@app.route('/user_register', methods=["GET"])
def user_register():
    return render_template('user_register.html')


@app.route('/book_search', methods=["GET"])
def book_search():
    if not request.args.get("book"):
        return render_template("index_book_search.html")

    # syntax of search title
    # have '%%' to search in between titles
    # capitalise titles
    search = "'%" + request.args.get("book") + "%'"
    search = search.title()

    # look up item in database
    sql_query = "SELECT * FROM books_csv WHERE title LIKE " + search + " OR isbn LIKE " + search + \
                " OR isbn LIKE " + search + " OR author LIKE " + search + " OR author LIKE " + search
    rows = db.execute(sql_query)
    books = rows.fetchall()

    # if no results found
    if rows.rowcount == 0:
        return render_template('book_results.html', message="No results found", search_name=request.args.get("book"))

    return render_template('book_results.html', books=books, search_name=request.args.get("book"))


if __name__ == '__main__':
    app.run()
