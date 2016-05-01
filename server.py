"""Project ReadMe."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import Book, Author, ISBN10, ISBN13, Query, QueryBook, connect_to_db, db, LibraryBranch, LibrarySystem

from tempmvp import get_crawl_results, get_item_details, normalize_sccl_availability, normalize_smcl_availability, normalize_sfpl_availability, avails_to_markers
from tempmvp import SCCLAvailabilitySearch, SMCLAvailabilitySearch, SFPLAvailabilitySearch

from dbfunctions import get_db_results, add_new_book, add_new_query, get_db_book_details

import json
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
    """Get, store and render results based on user keyword search."""

    search_keywords = request.form.get("keywords")
    search_keywords = search_keywords.strip().lower()

    matching_query = Query.query.filter_by(query_keywords=search_keywords).first()

    if matching_query:
        print "Matching query found!"
        final_results = get_db_results(matching_query.query_id)
    else:
        initial_results = get_crawl_results(search_keywords)
        new_query_id = add_new_query(search_keywords)
        print "New query added!"

        final_results = []

        # TODO - document what initial results are, they are a list of parsed worldcat search results
        for item in initial_results:

            new_dict = get_item_details(item)
            rank = item['rank']
            new_dict['rank'] = rank

            # TODO - if get_item_details returns a bunch of model.Book/model.ISBN*/model.GoodreadsInfo
            # TODO - update add_new_book
            new_book_id = add_new_book(new_query_id, new_dict, rank)
            new_dict['bookid'] = new_book_id
            final_results.append(new_dict)

    return render_template("searchresults.html", list=final_results)


@app.route('/details/<int:bookid>')
def item_details(bookid):
    """Show details about an item."""

    # TODO - remove get_db_book_details entirely and rely on objects getting returned
    # TODO - update template code to expect model.Book
    book_details = get_db_book_details(bookid)
    isbn13_list = book_details['ISBN-13']

    # TODO - Convert this to a list of [SCCLAvailabilitySearch, SMCLAvailabilitySearch, SFPLAvailabilitySearch]
    sccl_searcher = SCCLAvailabilitySearch()
    smcl_searcher = SMCLAvailabilitySearch()
    sfpl_searcher = SFPLAvailabilitySearch()

    for isbn13 in isbn13_list:
        # TODO - move contents of for loop to its own function so we have availability_for_isbn(isbn13)

        # TODO - convert this to iterate over list of searchers
        # TODO - move normalize_*_availability onto their respective search classes
        norm_sccl_avail_dict = normalize_sccl_availability(sccl_searcher.load_availability(isbn13))
        norm_smcl_avail_dict = normalize_smcl_availability(smcl_searcher.load_availability(isbn13))
        norm_sfpl_avail_dict = normalize_sfpl_availability(sfpl_searcher.load_availability(isbn13))

        # TODO - add documentation as to what this is doing
        # TODO - Write a test for dict_to_evaluate?
        dict_to_evaluate = norm_sccl_avail_dict.copy()
        dict_to_evaluate.update(norm_smcl_avail_dict)
        dict_to_evaluate.update(norm_sfpl_avail_dict)
        if not dict_to_evaluate:
            continue

        key_list = dict_to_evaluate.keys()
        for branch in key_list:
            lib_branch_obj = LibraryBranch.query.filter_by(branch_name=branch).first()
            if lib_branch_obj:
                dict_to_evaluate[branch]['branch_geo'] = lib_branch_obj.branch_geo
                dict_to_evaluate[branch]['sys_name'] = lib_branch_obj.library_system.sys_name
            dict_to_evaluate[branch]['branch_name'] = branch

        # TODO - move marker list creation to a separate function called marker_list(dict_to_evaluate)
        # Filtering out branches for which the database does not have a correlated library system name
        agg_norm_avail_list = [branch_dict for branch_dict in dict_to_evaluate.values() if branch_dict.get('sys_name')]
        newlist = sorted(agg_norm_avail_list, key=lambda k: (k['sys_name'], k['branch_name']))
        returned_marker_list = avails_to_markers(agg_norm_avail_list)

        final_marker_list = {
            "type": "FeatureCollection",
            "features": returned_marker_list
        }

        # TODO -
        if agg_norm_avail_list:
            return render_template("bookdetails.html", dictionary=book_details, avail_list=newlist, marker_list=final_marker_list)
        else:
            continue

    # NOTE - we would only get here if there are no matches on ISBNs
    return render_template("bookdetails.html", dictionary=book_details, avail_list=[], marker_list=0)


@app.route('/availability.geojson')
def check_availability(bookid):
    """Check library availability for an item."""

    pass


@app.route('/about')
def about_page():
    """About page."""

    return render_template("about.html")


# @app.route('/bookrecs')
# def connect_to_bookrecs():
#     """Book Recommendations page - connect to Emma's app."""
#
#     return render_template("bookrecs.html")


# @app.route('/contact')
# def contact_page():
#     """Contact Us page."""
#
#     return render_template("contact.html")
#
#
# @app.route('/register')
# def registration_page():
#     """User registration page."""
#
#     return render_template("register.html")
#
#
# @app.route('/login')
# def login_page():
#     """Log In page."""
#
#     return render_template("login.html")




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()