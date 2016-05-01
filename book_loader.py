import os
import requests
import urllib
from pyquery import PyQuery as pq

WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
WORLDCAT_FILTER_LANG_EN_EBOOKS_ONLY = "&fq=%20(%28x0%3Abook+x4%3Adigital%29)%20>%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"

HTTP_URL = "http:"

def get_crawl_results(keywords):
    """Provided user's search keywords, return list of search results, represented by
    a dictionary of general info and WorldCat url for each result."""

    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    worldcat_ready_url = WORLDCAT_SEARCH_URL + worldcat_ready_keywords + WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    list_of_search_results = search_for_print_books(worldcat_ready_url)

    return list_of_search_results


def search_for_print_books(url):
    """Given the url for a WorldCat search results page of English-language print books,
    returns a dictionary about the first 10 search results."""

    list_of_search_results = []

    # requests.get the search results page and
    results_page_xml = requests.get(url)

    # use pyquery to query the results_page_xml
    pq_results_page_xml = pq(results_page_xml.content)

    # Revised edition using pquery objects only
    # TODO - add documentation why we use .eq(3)
    content_xml = pq_results_page_xml('content').eq(3).text()
    pq_content = pq(content_xml)
    pq_results_list = pq_content('table.table-results tr.menuElem').items()

    for idx, pq_result in enumerate(pq_results_list):
        # TODO - consider moving contents of for loop into a function
        # TODO - so this looks like dict_for_result = _process_pq_result(pq_result)
        # TODO - once we pull this out into a function, we can write a test for it!
        # read the raw_rank from the TR directly
        raw_rank = pq_result('td.num').eq(1).text()
        # slice the raw_rank to remove the end "."
        rank = int(raw_rank[:-1])

        # result_id = "result-"+str(rank)

        # rank_of_result: get the rank of result
        rank_of_result = rank
        # book_title: get the book title
        book_title = pq_result('div.name strong').text()
        # author: get the book author(s) and slice to remove the "by " at the beginning
        author_string = pq_result('div.author').text()[3:]
        author_list = author_string.split(";")
        final_author_list = []
        for author in author_list:
            author = author.strip()
            final_author_list.append(author)

        # worldcat_url: find href result with id="result-1" and create the new url to store in the dict
        result_href_string = pq_result('div.name a').attr('href')
        new_url = WORLDCAT_STANDARD_URL + result_href_string

        # cover_url:
        cover_url = pq_result('td.coverart img').attr('src')
        final_cover_url = HTTP_URL + cover_url

        # assign key-value to dictionary for the specific result
        dict_for_result = dict()
        dict_for_result['rank'] = rank_of_result
        dict_for_result['title'] = book_title
        dict_for_result['author'] = final_author_list
        dict_for_result['worldcaturl'] = new_url
        dict_for_result['coverurl'] = final_cover_url

        # append the dict for the specific result to the final list of dicts
        list_of_search_results.append(dict_for_result)

    return list_of_search_results


def get_item_details(dict_of_item):
    """Provided one item's dictionary results from search_for_books(keywords),
    returns full book details for database for that item by the worldcat URL of its items details page."""

    # return list of only ISBN-13's for each url:
    # [ { '[url]': [#, #, #, ...] },
    #   ...
    # ]
    # >>> page = requests.get("http://www.worldcat.org/title/lean-in-women-work-and-the-will-to-lead/oclc/813526963&referer=brief_results")
    # >>> pq_details_page = pq(page.content)
    # ISBN
    # >>> isbn = pq_details_page('#details-standardno').eq(0).text()
    # >>> isbn
    # 'ISBN: 9780385349949 0385349947'
    # TITLE
    # >>> pq_details_page('h1.title').text()
    # 'Lean in : women, work, and the will to lead'
    # AUTHOR
    # >>> authors_string = pq_details_page('#bib-author-cell').text()
    # >>> [x.strip() for x in authors_string.split(';')]
    # ['Sheryl Sandberg', 'Nell Scovell']
    # COVER URL
    # http://covers.openlibrary.org/b/isbn/9780385533225-S.jpg
    # PUBLISHER
    # NUMBER OF PAGES
    # SUMMARY

    isbn_10_key = 'ISBN-10'
    isbn10_list = []
    isbn_13_key = 'ISBN-13'
    isbn13_list = []

    # initialize the empty dicts for this specific result
    book_details_dict = {}

    # get the url string from the dictionary passed into this function
    url = dict_of_item['worldcaturl']

    # requests.get the contents of the page and convert to pq object
    page = requests.get(url)

    # TODO - create a function that takes a string (page.content), this will make it easier to write a test
    pq_page = pq(page.content)

    # TITLE
    # >>> pq_details_page('h1.title').text()
    # 'Lean in : women, work, and the will to lead'
    title = pq_page('h1.title').text()

    # AUTHOR
    # >>> authors_string = pq_details_page('#bib-author-cell').text()
    # >>> [x.strip() for x in authors_string.split(';')]
    # ['Sheryl Sandberg', 'Nell Scovell']
    authors_string = pq_page('#bib-author-cell').text()
    author_list = [author.strip() for author in authors_string.split(';')]

    # PUBLISHER
    # >>> publisher = pq_details_page('#bib-publisher-cell').text()
    # 'New York : Alfred A. Knopf, 2013.' (pub_loc : pub, pub_year)
    publisher = pq_page('#bib-publisher-cell').text()

    # FORMAT
    format = pq_page('span.itemType').text()

    # NUMBER OF PAGES
    # >>> desc = pq_details_page('#details-description td').text()
    # "228 pages; 1 edition"
    # >>> page_num = []
    # >>> for char in desc[desc.find('pages')-1::-1]:
    # ...     if char != " " and not char.isdigit():
    # ...         break
    # ...     elif char == " " or char.isdigit():
    # ...         page_num.insert(0, char)
    # ...
    # ...
    # ...
    # >>> page_num
    # ['2', '2', '8', ' ']
    desc = pq_page('#details-description td').text()
    page_num = []

    # TODO - find more pages examples from worldcat and make sure we can cover more page formats
    for char in desc[desc.find('pages')-2::-1]:
        if not char.isdigit():
            break
        else:
            page_num.insert(0, char)

    num_of_pages = "".join(page_num)

    # SUMMARY
    # >>> summary = pq_details_page('div.abstracttxt').text()
    summary = pq_page('div.abstracttxt').text()

    # find the isbns on the page by their css selector and format them as a list
    isbn_string = pq_page('#details-standardno').eq(0).text()
    isbn_list = isbn_string.split(" ")

    # for any list item that is an ISBN of a particular length, assign the appropriate key and value
    for item in isbn_list:
        # TODO if item == ISBN:  continue
        if item != "ISBN:" and len(item) == 10:
            isbn10_list.append(str(item))
        elif item != "ISBN:" and len(item) == 13:
            isbn13_list.append(str(item))

    # TODO - consider promoting these to model.ISBN10 and model.ISBN13
    book_details_dict[isbn_10_key] = isbn10_list
    book_details_dict[isbn_13_key] = isbn13_list

    coverurl = dict_of_item['coverurl']

    # GOODREADS INFO
    # TODO - pull goodreads info out of this function so we can create model.GoodreadsInfo
    isbn_to_goodreads_list = [get_goodreads_info_by_isbn13(isbn13) for isbn13 in isbn13_list]

    # TODO - Simplify k.values()[0] issue and sorted[0].keys()[0]
    # sortedlist = list(sorted(isbn_to_goodreads_list, key=lambda k: int(k.values()[0]['goodreads_ratings_count'])))
    # lead_isbn13_by_ratings_count = sortedlist[0].keys()[0]

    # assign the type_of_isbn-isbn_no key-value pairs to the corresponding url's dictionary
    # TODO - consider promoting book_details_dict to model.Book
    book_details_dict['worldcaturl'] = url
    book_details_dict['title'] = title
    book_details_dict['author'] = author_list
    book_details_dict['publisher'] = publisher
    book_details_dict['page_count'] = num_of_pages
    book_details_dict['coverurl'] = coverurl
    book_details_dict['format'] = format
    book_details_dict['summary'] = summary
    book_details_dict['isbn_to_goodreads_list'] = isbn_to_goodreads_list
    # book_details_dict['isbn13_lead_by_goodreads_ratings_count'] = lead_isbn13_by_ratings_count

    return book_details_dict


def get_goodreads_info_by_isbn13(isbn13):
    """Provided an ISBN13, get ratings and review count info from goodreads."""

    goodreads_key = os.environ['GOODREADS_API_KEY']
    url = "https://www.goodreads.com/book/isbn"
    payload = dict(key=goodreads_key, isbn=isbn13)

    goodreads_page = requests.get(url, params=payload)
    pq_goodreads_page = pq(goodreads_page.content)

    pq_book = pq_goodreads_page('book').eq(0)

    pq_work = pq_goodreads_page('book').eq(0)('work').eq(0)

    final_dict = {}
    final_dict['goodreads_work_id'] = pq_work('id').text()
    final_dict['goodreads_rating'] = float(pq_book.children('average_rating').text() or 0.0)
    final_dict['goodreads_ratings_count'] = int(pq_work('ratings_count').text() or 0)
    final_dict['goodreads_review_count'] = int(pq_work('reviews_count').text() or 0)

    final_dict['isbn13'] = isbn13

    return final_dict