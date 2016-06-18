"""Project ReadMe."""
import requests
import os
from jinja2 import StrictUndefined

from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension

import sys
import logging

from model import connect_to_db
from model import get_book_related_details

from book_loader import get_crawl_results_with_cache_check
from availability_search import get_table_and_map_availability

"""
SUMMARY
# STEP ZERO:
To initialize Project ReadMe, Developer must complete the following:
* In seed.py, create and assign a list of Library System names. Iterate through the list of Library System names to populate the Library System database. (See seed.py for hard-coded example.)

* To populate the Library Branch database, first, create libdata.txt which is a pipe-delimited file with the following information:
** # TODO - flesh out fields for libdata.txt

* To complete the population of the Library Branch database, in seed.py, add the appropriate filepath to the libdata.txt file in the load_librarybranches() function.

* With PostgreSQL running, on the command line (such as Terminal), do the following:
** `virtualenv env`
** `source env/bin/activate`

* Once the env is confirmed to be activated, with PostgreSQL running, do the following:
** `createdb projectreadme`
** `python seed.py`

* If the seeding process is successful, you should see the "Load Complete." message. Once you see that message, you can spin up the local server by running:
** `python server.py`

* Get Goodreads API Secret and Key (http://www.goodreads.com/api), and set the following environment variables:
** `GOODREADS_API_SECRET=[Insert your Goodreads Secret here.]`
** `GOODREADS_API_KEY=[Insert your Goodreads Key here.]`

* With the local server and database running, visit localhost:5000/search in your browser to use the app.

# STEP ONE:
User visits search page (/search).

# STEP TWO:
User executes a text keyword search which triggers app to...
 * crawl WorldCat.org for English-language print books

 * crawl each of the top 10 WorldCat.org book details pages and extract and cache the following information:
 ** WorldCat.org's rank of the result for the specific keyword search
 ** Title
 ** Author
 ** WorldCat.org's book details page URL
 ** WorldCat.org's book cover image URL
 ** ISBNs (both ISBN-10s and ISBN-13s)
 ** Publisher
 ** Page Count
 ** Book Format (all print books currently, as limited by search categorization)
 ** Summary

 * in addition, for each result's ISBNs, we read from the Goodreads API:
 ** Goodreads Rating
 ** Goodreads Ratings Count

 * after all this, we render the results on the page (/results), displaying only the following:
 ** Cover Image
 ** Title
 ** Author
 ** Publisher
 ** Book Format
 ** Page Count

# STEP THREE:
User clicks on one of the results...which leads to the app loading book availability / rendering a book details page with the following info:

* From the WorldCat.org database cache:
** Cover Image
** Title
** Publisher
** Page Count
** Summary

* From Goodreads database cache:
** Goodreads Rating
** Goodreads Ratings Count

* For each Library System supported by Project ReadMe, the app executes an availability search using the ISBN of the book, which waits for all supported library systems to return before rendering:

* Both a Map and a Table with the following information:
** Library System Name
** Library Branch Name
** Number of Available Copies (if any)
** Where to Find the Copy (by section and/or call number)
** Library System-specific URL for the book

"""

DEBUG = 'NO_DEBUG' not in os.environ

app = Flask(__name__)

# Required to print errors to heroku logs
# Per http://stackoverflow.com/questions/27882479/flask-projects-on-heroku-returns-500-internal-server-error
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ABC")

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# With this line, it raises an error instead.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("home.html")


@app.route('/thankyou')
def thanks_page():
    """Thanks page for private beta sign-up."""

    return render_template("thanks.html")


@app.route('/search')
def search_page():
    """Search page."""

    return render_template("search.html")


@app.route('/results')
def show_search_results():
    """Search results page."""

    search_keywords = request.args.get("keywords")

    return render_template("searchresultspage.html", keywords=search_keywords)


@app.route('/results/ajax')
def search_results_ajax():

    keywords = request.args.get("keywords")
    keywords_lowered = keywords.strip().lower()

    all_books = get_crawl_results_with_cache_check(keywords_lowered)

    return render_template("searchresultsonly.html", list=all_books)


@app.route('/details/<int:bookid>')
def item_details(bookid):
    """Show details about an item."""

    book_detail_dict = get_book_related_details(bookid)

    return render_template("bookdetails.html", **book_detail_dict)


@app.route('/details/<int:bookid>/availability')
def item_availability(bookid):
    """Return availability details for an item."""

    results_dict = get_table_and_map_availability(bookid)
    avail_list = results_dict['avail_list']
    marker_list = results_dict['marker_list']

    return render_template('bookavailability.html', avail_list=avail_list, marker_list=marker_list)


@app.route('/about')
def about_page():
    """About page."""

    return render_template("about.html")


if __name__ == "__main__":

    PORT = int(os.environ.get("PORT", 5000))

    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    # app.debug = True

    # http://stackoverflow.com/questions/12369295/flask-sqlalchemy-display-queries-for-debug
    app.config['SQLALCHEMY_ECHO'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)