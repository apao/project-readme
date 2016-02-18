"""Project ReadMe."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import Book, Author, ISBN10, ISBN13, Query, QueryBook, connect_to_db, db

import tempmvp


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("home.html")


@app.route('/results', methods=['GET'])
def get_search_results():
    """Get, store and render results based on user keyword search."""

    # CACHING - using your DB as a cache

    # query db to see if string has been searched for
    
    # if queried and if NOT queried should return the same result
    ### This could be a populated model, a dict, or something else, TBD by you
    ### In this case, you should get used to passing around models...
    # if NOT queried, do crawl
    ### Populate a model "book = Book()""
    ### book.name = 'hi there'

    # IF queried, do NOT crawl, and return results

    search_keywords = request.form.get('keywords').strip()

    matching_keywords = Query.query.filter_by(query_keywords=search_keywords).first()

    if matching_keywords:
        # get matching book_ids and info
        # db_results = get_db_results()
        # add results here
        results = get_db_results(matching_keywords)

    else:

        results = get_crawl_results(search_keywords)

    for item in results:

        item_details = get_item_details(item)

        # write code to add book_details to database for:
        # class Book
        # class Author
        # class ISBN10
        # class ISBN13
        # class Query
        # class QueryBook

    return render_template("searchresults.html", list=item_details)


@app.route('/about')
def about_page():
    """About page."""

    return render_template("about.html")


@app.route('/bookrecs')
def connect_to_bookrecs():
    """Book Recommendations page - connect to Emma's app."""

    return render_template("bookrecs.html")


@app.route('/contact')
def contact_page():
    """Contact Us page."""

    return render_template("contact.html")


@app.route('/register')
def registration_page():
    """User registration page."""

    return render_template("register.html")


@app.route('/login')
def login_page():
    """Log In page."""

    return render_template("login.html")


def get_db_results(keywords):

    pass


def get_crawl_results(keywords):

    results = tempmvp.get_urls_by_search_keywords(keywords)
    return results


def get_item_details(item_dict):

    details = tempmvp.get_book_details_by_url(item_dict)
    return details



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()