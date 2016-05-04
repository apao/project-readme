"""Project ReadMe."""
import requests
from jinja2 import StrictUndefined

from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db
from model import get_book_related_details

from book_loader import get_crawl_results_with_cache_check
from availability_search import get_availability_dicts_for_isbn13

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

 * cache in the database WorldCat.org's top 10 matching results, including:
 ** WorldCat.org's rank of the result for the specific keyword search
 ** Title
 ** Author
 ** WorldCat.org's book details page URL
 ** WorldCat.org's book cover image URL

 * crawl each of the top 10 WorldCat.org book details pages and extract the following additional information:
 ** ISBNs (both ISBN-10s and ISBN-13s)
 ** Publisher
 ** Page Count
 ** Book Format (all print books currently, as limited by search categorization)
 ** Summary

 * in addition, for each result's ISBNs, we read from the Goodreads API
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
** Library System-specific URL for the book (BROKEN AND CURRENTLY ON MAP ONLY)

"""


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# With this line, it raises an error instead.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("home.html")


@app.route('/thankyou')
def thanks_page():
    """Thanks page for those signing up for private beta."""

    return render_template("thanks.html")


@app.route('/search')
def search_page():
    """Search page."""

    return render_template("search.html")


@app.route('/results', methods=['POST'])
def get_search_results():
    search_keywords = request.form.get("keywords")
    search_keywords = search_keywords.strip().lower()

    all_books = get_crawl_results_with_cache_check(search_keywords)

    return render_template("searchresults.html", list=all_books)


@app.route('/details/<int:bookid>')
def item_details(bookid):
    """Show details about an item."""

    book_detail_dict = get_book_related_details(bookid)

    isbn13_list = book_detail_dict['isbn13s']

    for isbn13_obj in isbn13_list:
        current_isbn13 = isbn13_obj.isbn13
        result_dicts = get_availability_dicts_for_isbn13(current_isbn13)
        agg_norm_avail_list, newlist, final_marker_list = result_dicts

        if agg_norm_avail_list:
            return render_template("bookdetails.html",
                                   dictionary=book_detail_dict,
                                   avail_list=newlist,
                                   marker_list=final_marker_list,
                                   **book_detail_dict)
        else:
            continue

    # NOTE - we would only get here if there are no matches on ISBNs
    return render_template("bookdetails.html", dictionary=book_detail_dict, avail_list=[], marker_list=0)


@app.route('/about')
def about_page():
    """About page."""

    return render_template("about.html")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # http://stackoverflow.com/questions/12369295/flask-sqlalchemy-display-queries-for-debug
    app.config['SQLALCHEMY_ECHO'] = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run()