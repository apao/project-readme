import os
import requests
import urllib
from pyquery import PyQuery as pq
from model import db, Book, Author, ISBN10, ISBN13, GoodreadsInfo
WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
WORLDCAT_FILTER_LANG_EN_EBOOKS_ONLY = "&fq=%20(%28x0%3Abook+x4%3Adigital%29)%20>%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"

HTTP_URL = "http:"

def get_crawl_results_with_cache_check(keywords):
    """
    :param keywords:
    :return:
    """
    final_dict = dict()
    # list_of_oclc_ids_as_strings, list_of_oclc_ids_as_ints = get_crawl_results(keywords)
    list_of_oclc_ids = get_crawl_results(keywords)

    books_in_db = Book.query.filter(Book.book_id.in_(list_of_oclc_ids)).all()

    for current_book_in_db in books_in_db:
        final_dict[current_book_in_db.book_id] = current_book_in_db

    for current_id in list_of_oclc_ids:
        # check to see if current_id is in db already
        if current_id in final_dict:
            continue

        # create a new book
        current_book = create_book_from_worldcat_id(current_id)
        # add new book to db
        db.session.add(current_book)
        db.session.flush()
        # add new book to final_dict
        final_dict[current_id] = current_book
        print '%s - %s' % (current_id, current_book.title)

    db.session.commit()

    # Iterate through list of final_dict
    all_books = [final_dict[current_id] for current_id in list_of_oclc_ids]

    return all_books


def get_crawl_results(keywords):
    """Provided user's search keywords, return list of search results, represented by
    a list of OCLC IDs (also our own book IDs)."""

    # TODO - consider renaming function to worldcat_ids_from_search_results_page
    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    worldcat_ready_url = WORLDCAT_SEARCH_URL + worldcat_ready_keywords + WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    # requests.get the search results page and
    results_page_xml = requests.get(worldcat_ready_url)

    list_of_oclc_ids = search_for_print_books(results_page_xml.content)

    return list_of_oclc_ids


def search_for_print_books(xml_content):
    """Given the url for a WorldCat search results page of English-language print books,
    returns a dictionary about the first 10 search results."""

    # use pyquery to query the results_page_xml
    pq_results_page_xml = pq(xml_content)

    # For each WorldCat search results page, there are four sets of content tags.
    # For our purposes, we only care about the HTML text within the last set of content tags.
    content_xml = pq_results_page_xml('content').eq(3).text()
    pq_content = pq(content_xml)

    # oclc_id_as_strings_results_list = [i.text() for i in pq_content('div.oclc_number').items()]
    oclc_id_as_ints_results_list = [int(i.text()) for i in pq_content('div.oclc_number').items()]

    # return (oclc_id_as_strings_results_list, oclc_id_as_ints_results_list)
    return oclc_id_as_ints_results_list

def create_book_from_worldcat_id(oclc_id):
    """
    :param oclc_id:
    :return:
    """
    worldcat_url_with_oclc_id = "http://www.worldcat.org/oclc/%d" % oclc_id
    details_page = requests.get(worldcat_url_with_oclc_id)
    html_string = details_page.content

    return _create_book_from_worldcat_details(html_string, worldcat_url_with_oclc_id, oclc_id)


def _create_book_from_worldcat_details(html_string, worldcat_url_with_oclc_id, oclc_id):

    book = _load_book_from_worldcat_details_page(html_string, worldcat_url_with_oclc_id, oclc_id)

    for current_isbn13 in book.isbn13s:
        current_isbn13.goodreadsinfo = get_goodreads_info_by_isbn13(current_isbn13.isbn13)

    return book


def _load_book_from_worldcat_details_page(html_content, details_page_url, oclc_id):
    """Given the HTML content of the details page, create a new Book object with all the necessary details."""

    current_book = Book()
    pq_page = pq(html_content)

    current_book.book_id = oclc_id

    current_book.title = _load_title_from_worldcat_details_page(pq_page)  # TITLE (e.g. 'Lean in : women, work, and the will to lead')
    current_book.publisher = _load_publisher_from_worldcat_details_page(pq_page)  # PUBLISHER (e.g. 'New York : Alfred A. Knopf, 2013.')
    current_book.worldcaturl = details_page_url
    current_book.page_count = _load_page_count_from_worldcat_details_page(pq_page)
    current_book.summary = _load_summary_from_worldcat_details_page(pq_page)
    current_book.coverurl = _load_cover_url_from_worldcat_details_page(pq_page)

    # TODO - check if author_name is unique before insertion
    current_book.authors = _load_authors_from_worldcat_details_page(html_content)

    isbn10_list, isbn13_list = _load_isbns_from_worldcat_details_page(html_content)
    current_book.isbn10s = isbn10_list
    current_book.isbn13s = isbn13_list

    return current_book


def _load_title_from_worldcat_details_page(pq_html_content):
    """
    :param pq_html_content:
    :return:
    """

    return pq_html_content('h1.title').text()


def _load_publisher_from_worldcat_details_page(pq_html_content):
    """
    :param pq_html_content:
    :return:
    """

    return pq_html_content('#bib-publisher-cell').text()


def _load_page_count_from_worldcat_details_page(pq_html_content):
    """
    :param pq_html_content:
    :return:
    """

    description_string = pq_html_content('#details-description td').text()
    page_num_list = []

    # TODO - find more pages examples from worldcat and make sure we can cover more page formats
    digits_found = False
    for char in description_string[description_string.find('pages')::-1]:
        if char.isdigit():
            digits_found = True
            page_num_list.insert(0, char)
        elif not char.isdigit() and digits_found:
            break
        else:
            continue

    num_of_pages = "".join(page_num_list)

    return num_of_pages


def _load_summary_from_worldcat_details_page(pq_html_content):
    """
    :param pq_html_content:
    :return:
    """

    return pq_html_content('div.abstracttxt').text()


def _load_cover_url_from_worldcat_details_page(pq_html_content):
    """
    :param pq_html_content:
    :return:
    """

    cover_url = pq_html_content('div#cover img.cover').attr('src')
    final_cover_url = HTTP_URL + cover_url

    return final_cover_url


def _load_authors_from_worldcat_details_page(html_content):
    """
    :param pq_html_content:
    :return:
    """

    pq_page = pq(html_content)
    authors_string = pq_page('#bib-author-cell').text()
    author_list = [author.strip() for author in authors_string.split(';')]
    final_author_list = []
    for author in author_list:
        current_author = Author()
        current_author.author_id = None
        current_author.author_name = author.strip()
        final_author_list.append(current_author)

    return final_author_list


def _load_isbns_from_worldcat_details_page(html_content):
    """
    :param pq_html_content:
    :return:
    """

    pq_page = pq(html_content)
    isbn_string = pq_page('#details-standardno').eq(0).text()
    isbn_list = isbn_string.split(" ")
    isbn10_list = []
    isbn13_list = []
    for current_isbn in isbn_list:
        if len(current_isbn) == 10:
            isbn10_obj = ISBN10()
            isbn10_obj.isbn10 = current_isbn
            isbn10_list.append(isbn10_obj)
        elif len(current_isbn) == 13:
            isbn13_obj = ISBN13()
            isbn13_obj.isbn13 = current_isbn
            isbn13_list.append(isbn13_obj)

    return [isbn10_list, isbn13_list]


def get_goodreads_info_by_isbn13(isbn13):
    """Provided an ISBN13, get ratings and review count info from goodreads."""

    goodreads_key = os.environ['GOODREADS_API_KEY']
    url = "https://www.goodreads.com/book/isbn"
    payload = dict(key=goodreads_key, isbn=isbn13)

    goodreads_page = requests.get(url, params=payload)

    html_string = goodreads_page.content

    goodreads_info_obj = _load_goodreads_info_from_goodreads_api(html_string)

    return goodreads_info_obj


def _load_goodreads_info_from_goodreads_api(html_content):
    """
    :param html_content:
    :return:
    """

    # TODO - promote this part to a separate function so we can write tests again test_html
    pq_goodreads_page = pq(html_content)

    pq_book = pq_goodreads_page('book').eq(0)

    pq_work = pq_goodreads_page('book').eq(0)('work').eq(0)

    # TODO - Return GoodreadsInfo()
    goodreads_info = GoodreadsInfo()
    goodreads_info.goodreads_work_id = pq_work('id').text()
    goodreads_info.goodreads_rating = float(pq_book.children('average_rating').text() or 0.0)
    goodreads_info.goodreads_ratings_count = int(pq_work('ratings_count').text() or 0)
    goodreads_info.goodreads_review_count = int(pq_work('reviews_count').text() or 0)
    goodreads_info.goodreads_review_text = None

    return goodreads_info