# Project 1

ENGO 551

Requirements:
_______________________________________________________________________________________________
1. Registration

user_register.html
input username and password, which saves it into a database called "users"

_______________________________________________________________________________________________
2. Login

user_login.html
input username and password, which looks it up in the "users" database
if user found, take to user_profile.html
if user not found, flash error and go back to login page

_______________________________________________________________________________________________
3. Logout

session is cleared
go back to index_book_search.html
_______________________________________________________________________________________________
4. Import

import.py
connect to database using psycopg2
use .to_sql function from sqlalchemy
table columns are index, isbn, title, author, and year
_______________________________________________________________________________________________
5. Search

if no results are found, message says "No results found"
if results found, there are multiple cards that show the title, author, isbn, date, and cover
image
users can find results even if part of query was inputted due to 'LIKE' query in SQL
_______________________________________________________________________________________________
6. Book page

book_details.html
you can see title, author, date, isbn, reviews user has writte, reviews other users have written
user can also look up other books at the bottom of the page
_______________________________________________________________________________________________
7. Review submission

if user has not submitted review on book page, there will be a link where user can dubmit reviews
reviews are stored in a database called reviews where the columns are review_id, username, rating,
review_title, review, and book_isbn
if user has already submitted a review, an error saying "no duplicate reviews" pops up
_______________________________________________________________________________________________
8. Google Books review data

review data from Google Books API gotten using the following:
goo_revs = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": isbn})
    response = goo_revs.json()
    rating = (response['items'][0]['volumeInfo']['averageRating'])
    no_rating = (response['items'][0]['volumeInfo']['ratingsCount'])
_______________________________________________________________________________________________
9. API access

if users want a JSON response, they need to go to the book page and click the JSON link
ex.

This is your JSON response:

{

 "title": "The Dark Is Rising",

 "author": "Susan Cooper",

 "publishedDate": "1973",

 "ISBN_10": "1416949658",

 "ISBN_13": "9781416949653",

 "reviewCount": 1,

 "averageRating": 5.0

}

