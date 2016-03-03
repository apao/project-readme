"""Project ReadMe."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import Book, Author, ISBN10, ISBN13, Query, QueryBook, connect_to_db, db, LibraryBranch, LibrarySystem

from tempmvp import get_crawl_results, get_item_details, get_sccl_availability, normalize_sccl_availability, normalize_smcl_availability, get_smcl_availability, normalize_sfpl_availability, get_sfpl_availability, avails_to_markers

from dbfunctions import get_db_results, add_new_book, add_new_query, get_db_book_details

import json


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


@app.route('/search')
def search_page():
    """Search page."""

    return render_template("search.html")


@app.route('/results', methods=['POST'])
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

    search_type = request.form["searchtype"]
    search_keywords = request.form.get("keywords")
    search_keywords = search_keywords.strip().lower()

    if search_type == "print":

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

    elif search_type == "ebooks":

        return render_template("base.html")

    else:

        return "Something is not working!"






@app.route('/details/<int:bookid>')
def item_details(bookid):
    """Show details about an item."""

    book_details = get_db_book_details(bookid)
    isbn13_list = book_details['ISBN-13']
    # marker_list = []

    for isbn13 in isbn13_list:
        norm_sccl_avail_dict = normalize_sccl_availability(get_sccl_availability(isbn13))
        norm_smcl_avail_dict = normalize_smcl_availability(get_smcl_availability(isbn13))
        norm_sfpl_avail_dict = normalize_sfpl_availability(get_sfpl_availability(isbn13))
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

        # key_list = norm_avail_dict.keys()
        # for branch in key_list:
        #     lib_branch_obj = LibraryBranch.query.filter_by(branch_name=branch).first()
        #     if lib_branch_obj:
        #         norm_avail_dict[branch]['branch_geo'] = lib_branch_obj.branch_geo
        #     norm_avail_dict[branch]['branch_name'] = branch

        agg_norm_avail_list = dict_to_evaluate.values()
        newlist = sorted(agg_norm_avail_list, key=lambda k: (k['sys_name'], k['branch_name']))
        returned_marker_list = avails_to_markers(agg_norm_avail_list)

        # for avail in norm_avail_list:
        #     branch = avail.get('branch_name')
        #     avail_copies = avail.get('avail_copies', 0)
        #     unavail_copies = avail.get('unavail_copies', 0)
        #     where_to_find = avail.get('sccl_where_to_find')
        #     url = avail.get('sccl_search_url')
        #     branch_geo = avail.get('branch_geo')
        #     branch_geo_list = branch_geo.split(',')
        #     branch_geo_long = float(branch_geo_list[0])
        #     branch_geo_lat = float(branch_geo_list[1])
        #     marker = {}
        #     marker["type"] = "Feature"
        #     marker["properties"] = {}
        #     marker["geometry"] = {}
        #     marker["geometry"]["type"] = "Point"
        #     marker["geometry"]["coordinates"] = [branch_geo_long, branch_geo_lat]
        #
        #     if avail_copies:
        #         marker_symbol = "library"
        #         marker["properties"]["description"] = "<div class=%s><strong>%s</strong></div><p>Copies Available: %s<br>Copies Unavailable: %s<br>Call Number: %s | %s</p><p><a href=%s target=\"_blank title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, avail_copies, unavail_copies, where_to_find[0][0], where_to_find[0][1], url)
        #         marker["properties"]["marker-symbol"] = marker_symbol
        #         marker_list.append(marker)
        #     elif avail_copies == 0:
        #         marker_symbol = "roadblock"
        #         marker["properties"]["description"] = "<div class=%s>%s</div><p>Copies Unavailable: %s</p><a href=%s target=\"_blank title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, unavail_copies, url)
        #         marker["properties"]["marker-symbol"] = marker_symbol
        #         marker_list.append(marker)
        #     else:
        #         continue

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




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()