"""Project ReadMe."""
import requests
from jinja2 import StrictUndefined

from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension

from model import db, connect_to_db, LibraryBranch
from model import get_db_book_details

from book_loader import get_crawl_results, create_book_from_worldcat_id
from availability_search import SCCLAvailabilitySearch, SMCLAvailabilitySearch, SFPLAvailabilitySearch, normalize_sccl_availability, normalize_smcl_availability, normalize_sfpl_availability

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

    oclc_id_results_list = get_crawl_results(search_keywords)

    # TODO - Add caching code as proposed by mentor
    # [] = book_loader.load_books_by_oclc_ids(oclc_id_results_list)
    all_books = []
    for oclc_id in oclc_id_results_list:
        current_book = create_book_from_worldcat_id(oclc_id)
        all_books.append(current_book)
        db.session.add(current_book)
        db.session.flush()

        print '%s - %s' % (oclc_id, current_book.title)

    db.session.commit()
    return render_template("searchresults.html", list=all_books)


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
        returned_marker_list = _avails_to_markers(agg_norm_avail_list)

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


@app.route('/about')
def about_page():
    """About page."""

    return render_template("about.html")


def _avails_to_markers(list_of_avails):
    """Return marker geojson based on list of availabilities."""

    marker_list = []

    for avail in list_of_avails:
        branch = avail.get('branch_name')
        avail_copies = avail.get('avail_copies', 0)
        unavail_copies = avail.get('unavail_copies', 0)
        where_to_find = avail.get('where_to_find')
        url = avail.get('search_url')
        branch_geo = avail.get('branch_geo')
        branch_geo_list = branch_geo.split(',')
        branch_geo_long = float(branch_geo_list[0])
        branch_geo_lat = float(branch_geo_list[1])
        marker = {}
        marker["type"] = "Feature"
        marker["properties"] = {}
        marker["geometry"] = {}
        marker["geometry"]["type"] = "Point"
        marker["geometry"]["coordinates"] = [branch_geo_long, branch_geo_lat]

        if avail_copies:
            marker_symbol = "library"
            # branch = branch.decode('utf-8')
            marker["properties"]["description"] = u"<div class='%s'><strong>%s</strong></div><p>Copies Available: %s<br>Copies Unavailable: %s<br>Call Number: %s | %s</p><p><a href='%s' target=\"_blank\" title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, avail_copies, unavail_copies, where_to_find[0][0], where_to_find[0][1], url)
            marker["properties"]["marker-symbol"] = marker_symbol
            # marker["properties"]["marker-color"] = "blue"
            # marker["properties"]["marker-size"] = "large"
            marker_list.append(marker)
        elif avail_copies == 0 or avail_copies == '0':
            marker_symbol = "harbor"
            marker["properties"]["description"] = u"<div class='%s'><strong>%s</strong></div><p>Copies Unavailable: %s</p><p><a href='%s' target=\"_blank\" title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, unavail_copies, url)
            marker["properties"]["marker-symbol"] = marker_symbol
            # marker["properties"]["marker-color"] = "red"
            marker_list.append(marker)
        else:
            continue

    return marker_list


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # http://stackoverflow.com/questions/12369295/flask-sqlalchemy-display-queries-for-debug
    app.config['SQLALCHEMY_ECHO'] = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()