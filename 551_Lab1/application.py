import os

import flask
from flask import Flask, session, redirect, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# from flask_login import *
# from flask_wtf import FlaskForm
# from sqlalchemy.sql.functions import user
# from wtforms import StringField, PasswordField, SubmitField

app = Flask(__name__)

# setting up wtform
# class LoginForm(FlaskForm):
#    username = StringField('Username')
#    password = PasswordField('Password')
#    submit = SubmitField('Submit')

# checking environment variables
print(os.environ['DATABASE_URL'])
print(os.environ['FLASK_APP'])

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# set up flask-login
# login_manager = LoginManager()
# login_manager.init_app(app)

# # create routes

# initial route
@app.route('/')
def index():
    return render_template("index_book_search.html")


# route to log into review site
@app.route('/login', methods=['GET', 'POST'])
def login():
    #    form = LoginForm()
    #    if form.validate_on_submit():
    #        login_user(user)
    #
    #        # if user logs in successfully:
    #        flask.flash('Logged in successfully!')
    #
    #        next = flask.request.args.get('next')
    #
    #        # function is_safe_url not working
    #        # if not is_safe_url(next):
    #        #    return flask.abort(400)

    #        return flask.redirect(next or flask.url_for('index'))
    #    return flask.render_template('user_login.html', form=form)
    return render_template('user_login.html')


# if user logs out
@app.route('/logout')
def logout():
#    """ Log user out """

    # Forget any user ID
#    session.clear()

    # Redirect user to login form
    return redirect("/")


# @app.route('/user_profile', methods=['GET', 'POST'])
# def user_profile():
#    if current_user.is_authenticated:
#        return render_template("user_profile.html")
#    else:
#        return render_template("user_login.html")


if __name__ == '__main__':
    app.run()
