"""Project ReadMe."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import Book, Author, ISBN10, ISBN13, Query, QueryBook, connect_to_db, db, LibraryBranch, LibrarySystem

from tempmvp import get_crawl_results, get_item_details, normalize_sccl_availability, normalize_smcl_availability, normalize_sfpl_availability, avails_to_markers
from tempmvp import SCCLAvailabilitySearch, SMCLAvailabilitySearch, SFPLAvailabilitySearch

from dbfunctions import get_db_results, add_new_book, add_new_query, get_db_book_details

import json


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

        for item in initial_results:

            new_dict = get_item_details(item)
            rank = item['rank']
            new_dict['rank'] = rank
            new_book_id = add_new_book(new_query_id, new_dict, rank)
            new_dict['bookid'] = new_book_id
            final_results.append(new_dict)

    return render_template("searchresults.html", list=final_results)


@app.route('/details/<int:bookid>')
def item_details(bookid):
    """Show details about an item."""

    book_details = get_db_book_details(bookid)
    isbn13_list = book_details['ISBN-13']
    sccl_searcher = SCCLAvailabilitySearch()
    smcl_searcher = SMCLAvailabilitySearch()
    sfpl_searcher = SFPLAvailabilitySearch()

    for isbn13 in isbn13_list:
        norm_sccl_avail_dict = normalize_sccl_availability(sccl_searcher.load_availability(isbn13))
        norm_smcl_avail_dict = normalize_smcl_availability(smcl_searcher.load_availability(isbn13))
        norm_sfpl_avail_dict = normalize_sfpl_availability(sfpl_searcher.load_availability(isbn13))
        dict_to_evaluate = norm_sccl_avail_dict.copy()
        dict_to_evaluate.update(norm_smcl_avail_dict)
        dict_to_evaluate.update(norm_sfpl_avail_dict)
        if dict_to_evaluate:
            key_list = dict_to_evaluate.keys()
            for branch in key_list:
                lib_branch_obj = LibraryBranch.query.filter_by(branch_name=branch).first()
                if lib_branch_obj:
                    dict_to_evaluate[branch]['branch_geo'] = lib_branch_obj.branch_geo
                    dict_to_evaluate[branch]['sys_name'] = lib_branch_obj.library_system.sys_name
                dict_to_evaluate[branch]['branch_name'] = branch
        else:
            continue

        # Filtering out branches for which the database does not have a correlated library system name
        agg_norm_avail_list = [branch_dict for branch_dict in dict_to_evaluate.values() if branch_dict.get('sys_name')]
        newlist = sorted(agg_norm_avail_list, key=lambda k: (k['sys_name'], k['branch_name']))
        returned_marker_list = avails_to_markers(agg_norm_avail_list)

        final_marker_list = {
            "type": "FeatureCollection",
            "features": returned_marker_list
        }

        if agg_norm_avail_list:
            return render_template("bookdetails.html", dictionary=book_details, avail_list=newlist, marker_list=final_marker_list)
        else:
            continue

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