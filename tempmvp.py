import os
import requests
import urllib
from pyquery import PyQuery as pq
import re
import json
import pprint

WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
WORLDCAT_FILTER_LANG_EN_EBOOKS_ONLY = "&fq=%20(%28x0%3Abook+x4%3Adigital%29)%20>%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"

SCCL_SEARCH_URL_BEG = "https://sccl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q="
SCCL_SEARCH_URL_END = "&commit=Search&searchOpt=catalogue"
SCCL_AVAILABILITY_URL_BEG = "https://sccl.bibliocommons.com"
SCCL_AVAILABILITY_URL_JSONEND = ".json"

SFPL_SEARCH_URL_BEG = "https://sfpl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q="
SFPL_SEARCH_URL_END = "&commit=Search"
SFPL_AVAILABILITY_URL_BEG = "https://sfpl.bibliocommons.com"
SFPL_AVAILABILITY_URL_END = ".json?search_scope=CAL-SFPL"

SMPLIBRARY_SEARCH_URL_BEG = "https://smplibrary.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q="
SMPLIBRARY_SEARCH_URL_END = "&commit=Search"
SMPLIBRARY_AVAILABILITY_URL_BEG = "https://smplibrary.bibliocommons.com"

SMCL_SEARCH_URL_BEG = "https://smcl.bibliocommons.com/search?locale=en-US&t=smart&q="
SMCL_AVAILABILITY_URL_BEG = "https://smcl.bibliocommons.com"

OPEN_LIBRARY_COVER_URL = "http://covers.openlibrary.org/b/isbn/"
OPEN_LIBRARY_SMALL_IMG_END = "-S.jpg"
OPEN_LIBRARY_MED_IMG_END = "-M.jpg"
OPEN_LIBRARY_LRG_IMG_END = "-L.jpg"
HTTP_URL = "http:"

# =============================================
# PRINT BOOK SEARCH ON WORLDCAT 
# =============================================


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


def get_urls_by_search_keywords(user_search_keywords):
    """Provided user's search keywords, return list of search results, represented by
    a dictionary of general info and WorldCat url for each result."""

    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    # TODO - either use {} format or add spaces around +'s for readability
    worldcat_ready_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    list_of_search_results = search_for_print_books(worldcat_ready_url)

    return list_of_search_results


# =============================================
# EBOOK SEARCH ON WORLDCAT 
# =============================================


def search_for_ebooks(url):
    """Given the url for a WorldCat search results page of English-language ebooks, 
    returns a dictionary about the first 10 search results."""

    list_of_search_results = []

    results_page_xml = requests.get(url)

    # use pyquery to query the results_page_xml
    pq_results_page_xml = pq(results_page_xml.content)

    # Revised edition using pquery objects only
    content_xml = pq_results_page_xml('content').eq(3).text()
    pq_content = pq(content_xml)
    pq_results_list = pq_content('table.table-results tr.menuElem').items()

    for idx, pq_result in enumerate(pq_results_list):
        # read the raw_rank from the TR directly
        raw_rank = pq_result('td.num').eq(1).text()
        # slice the raw_rank to remove the end "."
        rank = int(raw_rank[:-1])

        dict_for_result = {}
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

        # assign key-value to dictionary for the specific result
        dict_for_result['rank'] = rank_of_result
        dict_for_result['title'] = book_title
        dict_for_result['author'] = final_author_list
        dict_for_result['worldcaturl'] = new_url

        # append the dict for the specific result to the final list of dicts
        list_of_search_results.append(dict_for_result)

    return list_of_search_results


def get_ebook_results_by_search_keywords(user_search_keywords):
    """Provided user's search keywords, return list of only ebook search results, represented by
    a dictionary of general info and WorldCat url for each result."""

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Adigital%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    
    ebook_search_results = []
    worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)
    worldcat_ready_search_ebooks_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_EBOOKS_ONLY
    ebook_search_results = search_for_ebooks(worldcat_ready_search_ebooks_url)

    return ebook_search_results


# =============================================
# GETTING ISBNs FROM WORLDCAT ITEM DETAILS PAGE 
# =============================================


def get_isbn_by_url(dict_of_item):
    """Provided one item's dictionary results from search_for_books(keywords),
    returns list of ISBN-10 and ISBN-13 numbers for that item by the worldcat URL of its items details page."""

    # return list of only ISBN-13's for each url:
    # [ { '[url]': [#, #, #, ...] },
    #   ...
    # ]
    # >>> page = requests.get("http://www.worldcat.org/title/lean-in-women-work-and-the-will-to-lead/oclc/813526963&referer=brief_results")
    # >>> pq_details_page = pq(page.content)
    # >>> isbn = pq_details_page('#details-standardno').eq(0).text()
    # >>> isbn
    # 'ISBN: 9780385349949 0385349947'

    # returns [{'http://www.worldcat.org/title/catch-22-a-novel/oclc/271160&referer=brief_results': {'ISBN-10': '0671128051', 'ISBN-13': '978067112
    # 8050'}}, {'http://www.worldcat.org/title/catch-as-catch-can-the-collected-stories-and-other-writings/oclc/51095413&referer=brief_resu
    # lts': {'ISBN-10': '0743243749', 'ISBN-13': '9780743243742'}}, {'http://www.worldcat.org/title/conversations-with-joseph-heller/oclc/2
    # 7186451&referer=brief_results': {'ISBN-10': '0878056351', 'ISBN-13': '9780878056354'}}, {'http://www.worldcat.org/title/closing-time-
    # a-novel/oclc/30544119&referer=brief_results': {'ISBN-10': '0684804506', 'ISBN-13': '9780684804507'}}, {'http://www.worldcat.org/title
    # /joseph-heller/oclc/14166525&referer=brief_results': {'ISBN-10': '0805774920', 'ISBN-13': '9780805774924'}}, {'http://www.worldcat.or
    # g/title/joseph-hellers-catch-22/oclc/719518&referer=brief_results': {}}, {'http://www.worldcat.org/title/catch-22-joseph-heller/oclc/
    # 753253992&referer=brief_results': {'ISBN-10': '1411407180', 'ISBN-13': '9781411407183'}}, {'http://www.worldcat.org/title/yossarian-s
    # lept-here-when-joseph-heller-was-dad-the-apthorp-was-home-and-life-was-a-catch-22/oclc/687664279&referer=brief_results': {'ISBN-10': 
    # '1439197695', 'ISBN-13': '9781439197691'}}, {'http://www.worldcat.org/title/catch-22-joseph-heller/oclc/54036951&referer=brief_result
    # s': {'ISBN-10': '1586633813', 'ISBN-13': '9781586633813'}}, {'http://www.worldcat.org/title/just-one-catch-a-biography-of-joseph-hell
    # er/oclc/704383812&referer=brief_results': {'ISBN-10': '0312596855', 'ISBN-13': '9780312596859'}}]

    isbn_10_key = 'ISBN-10'
    isbn10_list = []
    isbn_13_key = 'ISBN-13'
    isbn13_list = []

    # initialize the empty dicts for this specific result
    dict_for_url = {}
    dict_of_isbns_with_url_key = {}

    # get the url string from the dictionary passed into this function
    url = dict_of_item['worldcaturl']
    
    # requests.get the contents of the page and convert to pq object
    page = requests.get(url)
    pq_page = pq(page.content)
    
    # find the isbns on the page by their css selector and format them as a list
    isbn_string = pq_page('#details-standardno').eq(0).text()
    isbn_list = isbn_string.split(" ")
    
    # for any list item that is an ISBN of a particular length, assign the appropriate key and value
    for item in isbn_list:
        if item != "ISBN:" and len(item) == 10:
            isbn10_list.append(str(item))
        elif item != "ISBN:" and len(item) == 13:
            isbn13_list.append(str(item))
    
    dict_for_url[isbn_10_key] = isbn10_list
    dict_for_url[isbn_13_key] = isbn13_list

    # assign the type_of_isbn-isbn_no key-value pairs to the corresponding url's dictionary
    dict_of_isbns_with_url_key[url] = dict_for_url

    return dict_of_isbns_with_url_key


def get_goodreads_info_by_isbn13(isbn13):
    """Provided an ISBN13, get ratings and review count info from goodreads."""

    goodreads_key = os.environ['GOODREADS_API_KEY']
    url = "https://www.goodreads.com/book/isbn"
    payload = dict(key=goodreads_key, isbn=isbn13)
    print isbn13
    
    goodreads_page = requests.get(url, params=payload)
    pq_goodreads_page = pq(goodreads_page.content)

    pq_book = pq_goodreads_page('book').eq(0)
    
    pq_work = pq_goodreads_page('book').eq(0)('work').eq(0)

    inner_dict = {}
    # final_dict = {}
    inner_dict['goodreads_work_id'] = pq_work('id').text()
    inner_dict['goodreads_rating'] = float(pq_book.children('average_rating').text() or 0.0)
    inner_dict['goodreads_ratings_count'] = int(pq_work('ratings_count').text() or 0)
    inner_dict['goodreads_review_count'] = int(pq_work('reviews_count').text() or 0)

    inner_dict['isbn13'] = isbn13
    final_dict = inner_dict

    # goodreads_avg_rating = pq_book.children('average_rating').text()
    # goodreads_ratings_count = pq_work('ratings_count').text()
    # goodreads_work_id = pq_work('id').text()
    # goodreads_review_count = pq_work('reviews_count').text()

    # final_dict = dict(isbn13=isbn13, 
    #                   goodreads_work_id=goodreads_work_id, 
    #                   goodreads_rating=goodreads_avg_rating,
    #                   goodreads_ratings_count=goodreads_ratings_count,
    #                   goodreads_review_count=goodreads_review_count)

    return final_dict


def get_book_details_by_url(dict_of_item):
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


def get_isbns_from_urls_list(list_of_dicts):
    """Given the returned list of item dictionaries from get_urls_by_search_keywords(keywords), 
    returns the respective list of dictionaries with item url as key and isbn(s) as pair."""

    # SAMPLE RETURNED RESPONSE FROM BPYTHON TESTING:
    # returns [{'http://www.worldcat.org/title/brain-rules-12-principles-for-surviving-and-thriving-at-work-home-and-school/oclc/184871778&referer=
    # brief_results': {'ISBN-10': '0979777747', 'ISBN-13': '9780979777745'}}, {'http://www.worldcat.org/title/brain-rules-for-baby-how-to-r
    # aise-a-smart-and-happy-child-from-zero-to-five/oclc/505420609&referer=brief_results': {'ISBN-10': '0983263302', 'ISBN-13': '978098326
    # 3302'}}, {'http://www.worldcat.org/title/think-like-a-freak-the-authors-of-freakonomics-offer-to-retrain-your-brain/oclc/870699040&re
    # ferer=brief_results': {'ISBN-10': '0606369414', 'ISBN-13': '9780606369411'}}, {'http://www.worldcat.org/title/kennedys-brain/oclc/154
    # 309109&referer=brief_results': {'ISBN-10': '1595581847', 'ISBN-13': '9781595581846'}}, {'http://www.worldcat.org/title/grain-brain-th
    # e-surprising-truth-about-wheat-carbs-and-sugar-your-brains-silent-killers/oclc/827082643&referer=brief_results': {'ISBN-10': '0316239
    # 836', 'ISBN-13': '9780316239837'}}, {'http://www.worldcat.org/title/words-and-rules-the-ingredients-of-language/oclc/42290964&referer
    # =brief_results': {'ISBN-10': '0965437469', 'ISBN-13': '9780965437462'}}, {'http://www.worldcat.org/title/subliminal-how-your-unconsci
    # ous-mind-rules-your-behavior/oclc/753624823&referer=brief_results': {'ISBN-10': '0307378217', 'ISBN-13': '9780307378217'}}, {'http://
    # www.worldcat.org/title/gods-brain/oclc/465330631&referer=brief_results': {'ISBN-10': '1616141646', 'ISBN-13': '9781616141646'}}, {'ht
    # tp://www.worldcat.org/title/paradoxical-brain/oclc/688679738&referer=brief_results': {'ISBN-10': '0521115574', 'ISBN-13': '9780521115
    # 575'}}, {'http://www.worldcat.org/title/new-complete-hoyle-the-authoritative-guide-to-the-official-rules-of-all-popular-games-of-skil
    # l-and-chance/oclc/21197036&referer=brief_results': {'ISBN-10': '0385402708', 'ISBN-13': '9780385402705'}}]

    list_of_dicts_with_isbns = []

    for dict_for_item in list_of_dicts:
        dict_of_isbns_with_url_key = get_isbn_by_url(dict_for_item)
        # append the dictionary to the list in order of original search results rank
        list_of_dicts_with_isbns.append(dict_of_isbns_with_url_key)

    return list_of_dicts_with_isbns


# ===================================
# PRINT SEARCH FOR LIBRARY AVAILABILITY
# ===================================

class BaseBibliocommonsAvailabilitySearch(object):
    """Abstract class for availability search in a library catalogue powered by Bibliocommons."""

    availability_url_beg = None

    def load_availability(self, isbn):

        full_list_of_branch_avails = []

        # TODO - ADD BIBLIOCOMMONS SEARCH URL INTO EACH DICT IN THE LIST
        # requests.get the bibliocommons search page using isbn
        bibliocommons_search_url = self.create_search_url(isbn) # search_url_beg + str(isbn) + search_url_end

        # requests.get the contents of the page and convert to pq object
        page = requests.get(bibliocommons_search_url)

        avail_url = self.get_avail_url_from_serp(page.content)
        if not avail_url:
            return full_list_of_branch_avails

        avail_page = requests.get(avail_url)
        json_avail_page = json.loads(avail_page.text)
        html_section_only = json_avail_page["html"]

        self.populate_availability_by_avail_url(html_section_only, full_list_of_branch_avails)

        # for current_branch_avails in full_list_of_branch_avails:
        #     current_branch_avails['bibliocommons_search_url'] = bibliocommons_search_url

        return full_list_of_branch_avails

    def get_avail_url_from_serp(self, page_html):
        pq_page = pq(page_html)
        # find the availability href for the isbn on the page by css selector
        availability_string = pq_page('a.circInfo.value.underlined').attr('href')

        if not availability_string:
            return None

        availability_string = availability_string.replace('?', '.json?')
        avail_url = self.create_avail_url(availability_string)
        return avail_url

    def populate_availability_by_avail_url(self, html_section_only, full_list_of_branch_avails):
        """Given availability URL, get dictionary of branch availabilities.
        """
        pq_html_section = pq(html_section_only)

        pq_ths = pq_html_section('thead').eq(0).find('th')
        headers = [pq_th.text() for pq_th in pq_ths.items()]

        non_thead_tr_list = pq_html_section.find('tr').filter(lambda i, this: not pq(this).parents('thead')).items()

        for pq_tr in non_thead_tr_list:
            status_details = self.status_details_from_tr_list(headers, pq_tr)
            full_list_of_branch_avails.append(status_details)

        return full_list_of_branch_avails

    def status_details_from_tr_list(self, headers, pq_tr):
        """Given pq object of status rows, create branch copy status details as dicts and add them to the full list."""

        list_of_status_details = []
        dict_of_status_details = {}

        for pq_td in pq_tr.find('td').items():
            list_of_status_details.append(pq_td.text())

        library_status_details = dict(zip(headers, list_of_status_details))

        branch_name_and_copies = library_status_details['Location'].split('(')  # 0-index item is branch name and num of copies

        if len(branch_name_and_copies) == 1:
            branch_name_and_copies.append('1')  # Add a num of copies for those without multiple
        else:
            branch_name_and_copies[1] = branch_name_and_copies[1][:-1] # Num of copies without parens

        dict_of_status_details['branch_name'] = branch_name_and_copies[0].rstrip()
        dict_of_status_details['num_of_copies'] = int(branch_name_and_copies[1])
        dict_of_status_details['branch_section'] = library_status_details['Collection']
        dict_of_status_details['call_no'] = library_status_details['Call No']
        dict_of_status_details['status'] = library_status_details['Status']

        return dict_of_status_details

    def create_search_url(self, isbn):
        """With ISBN, creates ISBN-specific library search url to be passed to requests."""

        raise NotImplementedError

    def create_avail_url(self, availability_string):
        """With availability string, creates library availability search url."""

        raise NotImplementedError

    def normalize_availability(self, dictlist):
        """With list of availability dicts, create normalized set of individual dicts by copy."""

        raise NotImplementedError


class SCCLAvailabilitySearch(BaseBibliocommonsAvailabilitySearch):
    """With ISBN, creates ISBN-specific SCCL library search url to be passed to requests."""

    availability_url_beg = "https://sccl.bibliocommons.com"

    def create_search_url(self, isbn):
        search_url = SCCL_SEARCH_URL_BEG + str(isbn) + SCCL_SEARCH_URL_END
        return search_url

    def create_avail_url(self, availability_string):
        avail_url = self.availability_url_beg + availability_string
        return avail_url

    def normalize_availability(self, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = avail.get('sccl_search_url')
            branch_dict[current_branch] = branch_dict.get(current_branch, {})
            branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
            branch_dict[current_branch]['search_url'] = current_url
            if avail.get('status') == 'Available':
                branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
                branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
            elif "Due" in avail.get('status') or "Holdshelf" in avail.get('status'):
                branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
            else:
                continue

        return branch_dict


class SMCLAvailabilitySearch(BaseBibliocommonsAvailabilitySearch):
    """With ISBN, creates ISBN-specific SMCL library search url to be passed to requests."""

    availability_url_beg = "https://smcl.bibliocommons.com"

    def create_search_url(self, isbn):
        search_url = SMCL_SEARCH_URL_BEG + str(isbn)
        return search_url

    def create_avail_url(self, availability_string):
        avail_url = self.availability_url_beg + availability_string
        return avail_url

    def normalize_availability(self, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = avail.get('smcl_search_url')
            branch_dict[current_branch] = branch_dict.get(current_branch, {})
            branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
            branch_dict[current_branch]['search_url'] = current_url
            if avail.get('status') == 'CHECK SHELF':
                branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
                branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
            elif "Due" in avail.get('status') or "HOLD" in avail.get('status'):
                branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
            else:
                continue

        return branch_dict


class SFPLAvailabilitySearch(BaseBibliocommonsAvailabilitySearch):
    """With ISBN, creates ISBN-specific SFPL library search url to be passed to requests."""

    availability_url_beg = "https://sfpl.bibliocommons.com"

    def create_search_url(self, isbn):
        search_url = SFPL_SEARCH_URL_BEG + str(isbn) + SFPL_SEARCH_URL_END
        return search_url

    def create_avail_url(self, availability_string):
        avail_url = self.availability_url_beg + availability_string
        return avail_url

    def normalize_availability(self, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = avail.get('sfpl_search_url')
            branch_dict[current_branch] = branch_dict.get(current_branch, {})
            branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
            branch_dict[current_branch]['search_url'] = current_url
            if avail.get('status') == 'CHECK SHELF':
                branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
                branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
            elif "Due" in avail.get('status') or "HOLD" in avail.get('status'):
                branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
            else:
                continue

        return branch_dict



def get_isbn13_from_dict(dict_for_item):
    """Given a returned dict, get the list of ISBN-13 numbers of the item."""

    isbn_13_key = 'ISBN-13'

    key = dict_for_item.keys()[0]
    isbn_dict = dict_for_item.get(key)
    isbn_13_list = isbn_dict.get(isbn_13_key)

    return isbn_13_list


def get_availabilities_for_list_of_books(list_of_dicts):
    """Given the returned list of dicts from get_isbns_from_urls_list(list_of_dicts),
    return a respective dict of sccl availabilities for each item in the list."""

    list_of_dicts_with_availabilities = []

    for dict_for_item in list_of_dicts:
        list_of_availability = get_sccl_avail_for_item(dict_for_item)
        # append the dictionary to the list in order of original search results rank
        list_of_dicts_with_availabilities.append(list_of_availability)

    return list_of_dicts_with_availabilities


def get_sccl_avail_for_item(dict_of_item):
    """Returns the full list of SCCL availability for one item returned by get_isbn_by_url on
    one result from get_urls_by_search_keywords."""

    # >>> get_sccl_avail_for_item(get_isbn_by_url(get_urls_by_search_keywords("brain rules")[0]))

    isbn13_list = get_isbn13_from_dict(dict_of_item)
    list_of_dicts_with_availabilities = []

    for isbn13 in isbn13_list:
        dict_of_isbn_availability = get_sccl_availability(isbn13)
        # append the dictionary to the list for the item
        list_of_dicts_with_availabilities.append(dict_of_isbn_availability)

    return list_of_dicts_with_availabilities


# =============================================
# EBOOK SEARCH FOR SCCL AVAILABILITY
# =============================================


# =============================================
# FUNCTIONS TO BE USED IN SERVER.PY
# =============================================

def get_crawl_results(keywords):
    # TODO - collapse functions together?
    results = get_urls_by_search_keywords(keywords)
    return results


def get_item_details(item_dict):
    # TODO - collapse functions together?
    details = get_book_details_by_url(item_dict)
    return details


# =============================================
# FUNCTIONS FOR FUTURE GEOCODING AND GEOLOCATION
# =============================================

# https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY

def get_smcl_branches_hours(url):
    """Given the SMCL hours and locations page, grab the information."""

    pass

# =============================================
# FUNCTIONS TO NORMALIZE EACH LIBRARY'S ITEM AVAILABILITY
# =============================================

def normalize_sccl_availability(dictlist):
    """Return normalized availability to pass to javascript for map rendering."""

    branch_dict = {}

    for avail in dictlist:
        current_branch = avail.get('branch_name')
        current_call_num = avail.get('call_no')
        current_branch_section = avail.get('branch_section')
        current_num_of_copies = avail.get('num_of_copies')
        current_url = avail.get('sccl_search_url')
        branch_dict[current_branch] = branch_dict.get(current_branch, {})
        branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
        branch_dict[current_branch]['search_url'] = current_url
        if avail.get('status') == 'Available':
            branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
            branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
        elif "Due" in avail.get('status') or "Holdshelf" in avail.get('status'):
            branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
        else:
            continue

    return branch_dict

# normalize_sccl_availability(get_sccl_availability("9780439136358"))

def normalize_smcl_availability(dictlist):
    """Return normalized availability to pass to javascript for map rendering."""

    branch_dict = {}

    for avail in dictlist:
        current_branch = avail.get('branch_name')
        current_call_num = avail.get('call_no')
        current_branch_section = avail.get('branch_section')
        current_num_of_copies = avail.get('num_of_copies')
        current_url = avail.get('smcl_search_url')
        branch_dict[current_branch] = branch_dict.get(current_branch, {})
        branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
        branch_dict[current_branch]['search_url'] = current_url
        if avail.get('status') == 'CHECK SHELF':
            branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
            branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
        elif "Due" in avail.get('status') or "HOLD" in avail.get('status'):
            branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
        else:
            continue

    return branch_dict


def normalize_sfpl_availability(dictlist):
    """Return normalized availability to pass to javascript for map rendering."""

    branch_dict = {}

    for avail in dictlist:
        current_branch = avail.get('branch_name')
        current_call_num = avail.get('call_no')
        current_branch_section = avail.get('branch_section')
        current_num_of_copies = avail.get('num_of_copies')
        current_url = avail.get('sfpl_search_url')
        branch_dict[current_branch] = branch_dict.get(current_branch, {})
        branch_dict[current_branch]['where_to_find'] = branch_dict.get(current_branch).get('where_to_find', [])
        branch_dict[current_branch]['search_url'] = current_url
        if avail.get('status') == 'CHECK SHELF':
            branch_dict[current_branch]['avail_copies'] = branch_dict.get(current_branch).get('avail_copies', 0) + current_num_of_copies
            branch_dict.get(current_branch).get('where_to_find').append(tuple([current_branch_section, current_call_num]))
        elif "Due" in avail.get('status') or "HOLD" in avail.get('status'):
            branch_dict[current_branch]['unavail_copies'] = branch_dict.get(current_branch).get('unavail_copies', 0) + current_num_of_copies
        else:
            continue

    return branch_dict


def avails_to_markers(list_of_avails):
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


# =======================================================
# FUNCTIONS TO GET EACH LIBRARY'S EBOOK ITEM AVAILABILITY
# =======================================================

def get_sccl_eresources_by_keyword(keyword):
    """Given search keywords, provides availability for eresources in the Santa Clara County Library System."""

    sccl_eresource_search_url = SCCL_SEARCH_URL_BEG + urllib.quote_plus(keyword) + SCCL_SEARCH_URL_END

    return sccl_eresource_search_url


def get_sfpl_ebooks_by_keyword(keyword):
    """Given search keywords, provides availability for ebooks in the San Francisco Public Library System."""

    sfpl_ebook_id_list = []
    list_of_final_items = []
    # https://sfpl.bibliocommons.com/search?t=smart&search_category=keyword&commit=Search&q=lean%20in&formats=EBOOK
    SFPL_BASE_URL = "https://sfpl.bibliocommons.com"
    SFPL_SEARCH_EBOOKS_URL_BEG = "https://sfpl.bibliocommons.com/search?t=smart&search_category=keyword&commit=Search&q="
    SFPL_SEARCH_EBOOKS_URL_END = "&formats=EBOOK"
    search_keywords = urllib.quote(keyword)

    sfpl_search_ebooks_url = SFPL_SEARCH_EBOOKS_URL_BEG + search_keywords + SFPL_SEARCH_EBOOKS_URL_END

    # requests.get the contents of the search page and convert to pq object
    page = requests.get(sfpl_search_ebooks_url)
    pq_page = pq(page.content)

    # find the href with sfpl id no. on the page by css selector
    # ebook_id_objects = pq_page('img.jacketCover.bib_detail').attr('id')
    # ebook_id_pq_objects = pq_page.find('img.jacketCover.bib_detail')
    # for i in range(len(ebook_id_pq_objects)):
    #     sfpl_ebook_id_list.append(ebook_id_pq_objects.eq(i).attr('id'))
    #
    # title_lst = [i.text() for i in pq_page.items('span.title')]
    # author_lst = [i.text() for i in pq_page.items('span.author')]

    title_results_lst = [i.find('span.title').text() for i in pq_page.items('div.list_item_outer')]
    author_results_lst = [i.find('span.author').text() for i in pq_page.items('div.list_item_outer')]
    item_href_lst = [i.find('a.jacketCoverLink').attr('href') for i in pq_page.items('div.pull-left.visible-xs.visible-sm')]
    ebook_format_provider_lst = [i.find('span.value.callNumber').text() for i in pq_page.items('div.row.circ_info.list_item_section')]
    coverurl_lst = [i.find('img.jacketCover').attr('src') for i in pq_page.items('div.pull-left.visible-xs.visible-sm')]
    item_avail_href_lst = [i.find('a.click_n_sub').attr('href') for i in pq_page.items('div.availability_block')]
    item_request_href_lst = [i.find('a.digital_request').attr('href') for i in pq_page.items('span.hold_button')]

    item_details_full_url_lst = []
    for href in item_href_lst:
        item_full_details_url = SFPL_BASE_URL + href
        item_details_full_url_lst.append(item_full_details_url)

    for i in range(len(title_results_lst)):
        if item_avail_href_lst[i] and item_request_href_lst[i]:
            item_dict = dict(title=title_results_lst[i],
                             author=author_results_lst[i],
                             item_details_url=item_details_full_url_lst[i],
                             ebook_format_provider=ebook_format_provider_lst[i],
                             coverurl=coverurl_lst[i],
                             item_avail_url=SFPL_BASE_URL + item_avail_href_lst[i],
                             item_request_url=SFPL_BASE_URL + item_request_href_lst[i])
            final_item_dict = get_sfpl_ebook_details(item_dict, item_dict.get('item_details_url'))
        else:
            item_dict = dict(title=title_results_lst[i],
                             author=author_results_lst[i],
                             item_details_url=item_details_full_url_lst[i],
                             ebook_format_provider=ebook_format_provider_lst[i],
                             coverurl=coverurl_lst[i],
                             item_avail_url="",
                             item_request_url="")
            final_item_dict = get_sfpl_ebook_details(item_dict, item_dict.get('item_details_url'))
        list_of_final_items.append(final_item_dict)

    return list_of_final_items


def get_sfpl_ebook_details(itemdict, sfplurl):
    """Given an SFPL item url, provide details about the ebook."""

    # item_libid_lst = []
    # isbns_full_lst = []
    # other_details_lst = []
    # summary_lst = []
    # publisher_lst = []
    # item_characteristics_lst = []
    # goodreads_info_lst = []

    item_page = requests.get(sfplurl)
    pq_item_page = pq(item_page.content)
    item_libid_str = pq_item_page('div.content.itemDetail').attr('id')
    itemdict['sfpl_libid'] = item_libid_str
    # item_libid_lst.append(item_libid_str)
    item_isbns_str = pq_item_page('div.content.itemDetail').attr('data-isbns')
    item_isbns_lst = item_isbns_str.split(',')
    # isbns_full_lst.append(item_isbns_lst)
    for isbn in item_isbns_lst:
        if len(isbn) == 13:
            itemdict['isbn13'] = isbn
            goodreads_info = get_goodreads_info_by_isbn13(isbn)
            itemdict['isbn_to_goodreads_list'] = goodreads_info
            break
            # goodreads_info_lst.append(goodreads_info)
    item_pub_and_other_lst = [i.find('span.value').text() for i in pq_item_page.items('div.dataPair.clearfix')]
    itemdict['publisher_and_page_count'] = item_pub_and_other_lst
    # if len(item_pub_and_other_lst) == 5:
    #     item_pub, item_edition, item_isbns, item_characteristics, item_other_contributors = item_pub_and_other_lst
    # else:
    #     item_pub, item_edition, item_isbns, item_characteristics = item_pub_and_other_lst
    # publisher_lst.append(item_pub)
    # item_characteristics_lst.append(item_characteristics)
    # other_details_lst.append(item_pub_and_other_lst)
    summary = pq_item_page('div.bib_description').text()
    itemdict['summary'] = summary
    # summary_lst.append(summary)

    return itemdict












# if __name__ == '__main__':
#     # VERSION FOR TESTING ONLY LOOKING AT ONE RESULT - 4.5 seconds of processing
#     # urls = get_urls_by_search_keywords("brain rules")
#     # isbns = get_isbn_by_url(urls[0])
#     # avails = get_sccl_avail_for_item(isbns)
#     # pprint.pprint(avails)
#
#     # VERSION FOR TESTING ON FULL LIST OF 10 RESULTS - more than 18 seconds of processing
#     # >>> get_availabilities_for_list_of_books(get_isbns_from_urls_list(get_urls_by_search_keywords("brain rules")))
#     urls = get_urls_by_search_keywords("lean in")
#     isbns = get_isbns_from_urls_list(urls)
#     avails = get_availabilities_for_list_of_books(isbns)
#     pprint.pprint(avails)


