import os
import requests
import psycopg2

from flask import Flask, flash, render_template, request, url_for, session
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

        flash('You have been logged in!')

        return render_template('user_profile.html')
    else:
        flash('Please try again.')
        return render_template('user_login.html')


@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    flash('You have been logged out!')
    return render_template('index_book_search.html')


@app.route('/user_profile', methods=["GET", "POST"])
def user_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur.execute('INSERT INTO users (username,password) VALUES (%s, %s)',
                    (username, password))

        flash('You have successfully registered!')

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


@app.route("/user_book_review", methods=["GET"])
def user_book_review():
    return render_template('user_book_review.html')


@app.route("/user_write_review/<isbn>", methods=["GET", "POST"])
def user_write_review(isbn):
    sql_query = "SELECT isbn, title, author, year FROM books_csv WHERE isbn = '" + isbn + "'"
    val = db.execute(sql_query).fetchall()

    # put (title) by (author) into string for html page
    review_for = val[0][1] + " by " + val[0][2]

    if request.method == "POST":

        # save/get info
        user = session["user_name"]
        rating = request.form.get("rating")
        user_review_title = request.form.get("user_review_title")
        user_review = request.form.get("user_review")

        # look for previous submissions
        sql_dupli_rev = "SELECT * FROM reviews WHERE username = '" + user + "' AND book_isbn = '" + isbn + "'"
        revs = db.execute(sql_dupli_rev)

        if revs.rowcount >= 1:
            return render_template('error.html', message="You cannot make duplicate reviews!")

        # insert review into database
        sql_insert_rev = "INSERT INTO reviews (username, rating, review_title, review, book_isbn) VALUES ('" + user + \
                         "', '" + rating + "', '" + user_review_title + "', '" + user_review + "', '" + isbn + "')"
        db.execute(sql_insert_rev)
        db.commit()

        flash('Review submitted!')

        return render_template('index_book_search.html')
    else:
        return render_template('user_write_review.html', review_for=review_for, book=val)


@app.route("/book_details/<isbn>", methods=["GET", "POST"])
def book_details(isbn):
    sql_query = "SELECT * FROM books_csv WHERE isbn = '" + isbn + "'"
    book_val = db.execute(sql_query)
    books = book_val.fetchall()
    count = 0

    # get all reviews
    sql_all = "SELECT username, rating, review_title, review, book_isbn FROM reviews WHERE book_isbn = '" + isbn + "'"
    all_rev_val = db.execute(sql_all)
    curr_all_review = all_rev_val.fetchall()

    # api for Google Books ratings
    goo_revs = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": isbn})
    response = goo_revs.json()
    rating = (response['items'][0]['volumeInfo']['averageRating'])
    no_rating = (response['items'][0]['volumeInfo']['ratingsCount'])

    # check if there are reviews for the current book
    count_all = all_rev_val.rowcount

    # put (title) by (author) into string for html page
    details_for = books[0][2] + " by " + books[0][3]
    if session.get('user_name'):
        user = session["user_name"]
        sql_review = "SELECT username, rating, review_title, review, book_isbn FROM reviews WHERE username = '" + user + \
                     "' AND book_isbn = '" + isbn + "'"
        rev_val = db.execute(sql_review)
        curr_user_review = rev_val.fetchall()

        # check if there are reviews for the current book
        count = rev_val.rowcount

        return render_template("book_details.html", book=books, t_by_a=details_for, review=curr_user_review,
                               all_review=curr_all_review, count=count, count_all=count_all, rating=rating,
                               no_rating=no_rating)
    else:
        none_book_review = books
        return render_template("book_details.html", book=books, t_by_a=details_for, review=none_book_review,
                               all_review=curr_all_review, count=count, count_all=count_all, rating=rating,
                               no_rating=no_rating)


@app.route("/api/<isbn>", methods=["GET"])
def api_acess(isbn):
    # get vals of book from isbn
    sql_api = "SELECT title, author, year, isbn FROM books_csv WHERE isbn = '" + isbn + "'"
    val_api = db.execute(sql_api)
    curr_val_api = val_api.fetchall()
    print(curr_val_api[0][0])
    # get review states of book
    sql_rev = "SELECT rating FROM reviews WHERE book_isbn = '" + isbn + "'"
    val_rev = db.execute(sql_rev)
    curr_val_rev = val_rev.fetchall()

    title = curr_val_api[0][0]
    author = curr_val_api[0][1]
    date = curr_val_api[0][2]

    # calculate isbn_13 from isbn_10
    # see how many digits are in isbn
    if len(str(isbn)) == 7:
        isbn_10 = "0" + "0" + "0" + str(isbn)
    if len(str(isbn)) == 8:
        isbn_10 = "0" + "0" + str(isbn)
    if len(str(isbn)) == 9:
        isbn_10 = "0" + str(isbn)
    else:
        isbn_10 = str(isbn)

    isbn_13_pre = "9" + "7" + "8" + isbn_10[:-1]
    isbn_13_add = 0
    print(10 % 5)

    for i in range(0,len(isbn_13_pre),2):
        isbn_13_add = isbn_13_add + int(isbn_13_pre[i]) * 1
        isbn_13_add = isbn_13_add + int(isbn_13_pre[i+1]) * 3

    isbn_13 = isbn_13_pre + str(isbn_13_add % 10)

    review_count = val_rev.rowcount
    average_rating = 0

    if review_count == 0:
        average_rating = None
    else:
        for i in range(0,review_count):
            average_rating = average_rating+ curr_val_rev[i][0]
        average_rating = average_rating / review_count

    # set JSON vals into json_val
    json_val = [title, author, date, isbn_10, isbn_13, review_count, average_rating]

    return render_template("api_return.html", json_val=json_val)


if __name__ == '__main__':
    app.run()
