import os
import requests
import urllib
from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
from lxml import etree
import re
import json
import pprint

WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
SCCL_SEARCH_URL_BEG = "https://sccl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q="
SCCL_SEARCH_URL_END = "&commit=Search&searchOpt=catalogue"
SCCL_AVAILABILITY_URL_BEG = "https://sccl.bibliocommons.com/item/show_circulation/"
SCCL_AVAILABILITY_URL_JSONEND = ".json"


def search_for_books(url):
    """Searching user keywords in the WorldCat, returns a dictionary about the search results."""

    # WHAT WORKED FROM BPYTHON TESTING:
    # >>> from bs4 import BeautifulSoup as bs
    # >>> from pyquery import PyQuery as pq
    # >>> from lxml import etree
    # >>> import requests
    # >>> r = requests.get('http://www.worldcat.org/search?q=lean+in&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined')
    # >>> d = pq(etree.fromstring(r.content))
    # >>> root = d("content")
    # >>> child = root[3]
    # >>> html = child.text
    # >>> soup = bs(html, "lxml")
    # >>> result_href_string = soup.findAll(id="result-1", href=True)[0]['href']
    # '/title/lean-in-women-work-and-the-will-to-lead/oclc/813526963&referer=brief_results'
    # >>> new_url = "http://www.worldcat.org"+result_href_string
    # >>> list_of_authors = soup.findAll("div", { "class" : "author" })

    # BPYTHON PROOF THAT THE FUNCTION WORKS!!!!! :P
    # >>> search_for_books("lean in")
    # {'result-4': {'worldcaturl': 'http://www.worldcat.org/title/lean-in/oclc/869793004&referer=brief_results', 'a
    # uthor': u'Sheryl Sandberg', 'rank': 4, 'title': u'Lean in'}, 'result-5': {'worldcaturl': 'http://www.worldcat
    # .org/title/lean-in-women-work-and-the-will-to-lead/oclc/830326446&referer=brief_results', 'author': u'Sheryl 
    # Sandberg; Nell Scovell', 'rank': 5, 'title': u'Lean in : women, work, and the will to lead'}, 'result-6': {'w
    # orldcaturl': 'http://www.worldcat.org/title/lean-thinking-banish-waste-and-create-wealth-in-your-corporation/
    # oclc/34798036&referer=brief_results', 'author': u'James P Womack; Daniel T Jones', 'rank': 6, 'title': u'Lean
    #  thinking : banish waste and create wealth in your corporation'}, 'result-7': {'worldcaturl': 'http://www.wor
    # ldcat.org/title/applying-lean-in-healthcare-a-collection-of-international-case-studies/oclc/435419204&referer
    # =brief_results', 'author': u'Joe Aherne; John Whelton;', 'rank': 7, 'title': u'Applying lean in healthcare : 
    # a collection of international case studies'}, 'result-1': {'worldcaturl': 'http://www.worldcat.org/title/lean
    # -in-women-work-and-the-will-to-lead/oclc/813526963&referer=brief_results', 'author': u'Sheryl Sandberg; Nell 
    # Scovell', 'rank': 1, 'title': u'Lean in : women, work, and the will to lead'}, 'result-2': {'worldcaturl': 'h
    # ttp://www.worldcat.org/title/lean-mean-thirteen/oclc/122896800&referer=brief_results', 'author': u'Janet Evan
    # ovich', 'rank': 2, 'title': u'Lean mean thirteen'}, 'result-3': {'worldcaturl': 'http://www.worldcat.org/titl
    # e/in-search-of-excellence-lessons-from-americas-best-run-companies/oclc/8493620&referer=brief_results', 'auth
    # or': u'Thomas J Peters; Robert H Waterman', 'rank': 3, 'title': u"In search of excellence : lessons from Amer
    # ica's best-run companies"}, 'result-8': {'worldcaturl': 'http://www.worldcat.org/title/lean-years-politics-in
    # -the-age-of-scarcity/oclc/5799910&referer=brief_results', 'author': u'Richard J Barnet', 'rank': 8, 'title': 
    # u'The lean years : politics in the age of scarcity'}, 'result-9': {'worldcaturl': 'http://www.worldcat.org/ti
    # tle/clark-howards-living-large-in-lean-times-250-ways-to-buy-smarter-spend-smarter-and-save-money/oclc/693810
    # 714&referer=brief_results', 'author': u'Clark Howard; Mark Meltzer; Theo Thimou', 'rank': 9, 'title': u"Clark
    #  Howard's living large in lean times : 250+ ways to buy smarter, spend smarter, and save money"}, 'result-10'
    # : {'worldcaturl': 'http://www.worldcat.org/title/leveraging-lean-in-healthcare-transforming-your-enterprise-i
    # nto-a-high-quality-patient-care-delivery-system/oclc/669122292&referer=brief_results', 'author': u'Charles Pr
    # otzman; George Mayzell; Joyce Kerpchar', 'rank': 10, 'title': u'Leveraging lean in healthcare : transforming 
    # your enterprise into a high quality patient care delivery system'}}

    list_of_search_results = []

    # # take a user's search keywords
    # # convert string to match the format for the WorldCat search results page
    # worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    # worldcat_ready_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    # requests.get the search results page and
    results_page_xml = requests.get(url)

    # use pyquery to query the results_page_xml
    pq_results_page_xml = pq(results_page_xml.content)

    # find the full text from the appropriate element <content>
    # list_of_content_elements = results_page_pq("content")
    # fourth_content_element = list_of_content_elements[3]
    # text_of_fourth_content_element = fourth_content_element.text
    # soup_of_text = bs(text_of_fourth_content_element, "lxml")

    # for rank in range(1, 11):

    #     dict_for_result = {}
    #     result_id = "result-"+str(rank)
    #     pos_of_author = rank - 1
    #     # rank_of_result: get the rank of result
    #     rank_of_result = rank
    #     # book_title: get the book title
    #     book_title = soup_of_text.find(id=result_id).text
    #     # author: get the book author(s)
    #     list_of_authors = soup_of_text.findAll("div", {"class": "author"})
    #     author = list_of_authors[pos_of_author].text[3:]
    #     # worldcat_url: find href result with id="result-1" and create the new url to store in the dict
    #     result_href_string = soup_of_text.find(id=result_id, href=True)['href']
    #     new_url = WORLDCAT_STANDARD_URL+result_href_string

    #     # assign key-value to dictionary for the specific result
    #     dict_for_result['rank'] = rank_of_result
    #     dict_for_result['title'] = book_title
    #     dict_for_result['author'] = author
    #     dict_for_result['worldcaturl'] = new_url

    #     # assign the dict for the specific result to the final dict of dicts
    #     dict_of_search_results[result_id] = dict_for_result


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


def get_urls_by_search_keywords(user_search_keywords):
    """Provided user's search keywords, return list of search results, represented by
    a dictionary of general info and WorldCat url for each result."""

    list_of_search_results = []

    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    worldcat_ready_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    list_of_search_results = search_for_books(worldcat_ready_url)

    return list_of_search_results


def get_isbn_by_url(dict_of_item):
    """Provided one item's dictionary results from search_for_books(keywords),
    returns ISBN numbers for that item by the worldcat URL of its items details page."""

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
    isbn_13_key = 'ISBN-13'

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
            dict_for_url[isbn_10_key] = str(item)
        elif item != "ISBN:" and len(item) == 13:
            dict_for_url[isbn_13_key] = str(item)
    
    # assign the type_of_isbn-isbn_no key-value pairs to the corresponding url's dictionary
    dict_of_isbns_with_url_key[url] = dict_for_url

    return dict_of_isbns_with_url_key


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


def get_sccl_availability(isbn):
    """Given an ISBN, provides availability for an item in the Santa Clara County Library System."""

    # for each isbn, return list of dictionaries:
    # [ { 'isbn': { 'branch_name': ____,
    #               'status': ____,
    #               'number_of_copies': ____,
    #               'collection_name': ____,
    #               'call_no': ____}
    #   }
    # ]
    # for items not found in sccl, page html will have <div class="mainContent">
    # for items found in sccl, search for sccl id number:
    # https://sccl.bibliocommons.com/item/show_circulation/1402794103.json
    # >>> sccl_results = pq(requests.get("https://sccl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q=9780312349493&commit=Search&searchOpt=catalogue").content)
    # >>> sccl_results('a.circInfo.value.underlined').attr('href')
    # >>> re.search('/(\w*)\?', '/item/show_circulation/1214096103?search_scope=CAL-SCCL').group(0)
    # '/1214096103?'
    # >>> '/1214096103?'[1:-1]
    # '1214096103'
    # >>> page = requests.get("https://sccl.bibliocommons.com/item/show_circulation/1402794103.json")
    # >>> import json
    # >>> data = json.loads(page.text)
    # >>> html = data['html']
    # >>> pq_avail = pq(html)
    # >>> pq_avail('tr')
    # >>> for tr in pq_html_section.find('tr').filter(lambda i: not pq(this).parents('thead')).items():
    # ...     for td in tr.find('td').items():
    # ...         print td.text()
    # ...     print "=================="

    # RESULTS FROM BPYTHON TESTING:
    # https://sccl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q=9780385349949&commit=Search&searchOpt=catalogue
    # /item/show_circulation/1402794103?search_scope=CAL-SCCL
    # https://sccl.bibliocommons.com/item/show_circulation/1402794103.json
    # {9780385349949: [{'status': 'Available', 'branch_name': 'Campbell', 'branch_section': 'Campbell Adult - Nonfiction Section', 'num_of_
    # copies': '(4)', 'call_no': '658.4092 SANDBER'}, {'status': 'Available', 'branch_name': 'Cupertino', 'branch_section': 'Cupertino Adul
    # t - Nonfiction Section', 'num_of_copies': '(6)', 'call_no': '658.4092 SANDBER'}, {'status': 'Available', 'branch_name': 'Gilroy', 'br
    # anch_section': 'Gilroy Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'Available', 'br
    # anch_name': 'Los', 'branch_section': 'Los Altos Adult - Nonfiction Section', 'num_of_copies': 'Altos', 'call_no': '658.4092 SANDBER'}
    # , {'status': 'Available', 'branch_name': 'Milpitas', 'branch_section': 'Milpitas Adult - Nonfiction Section', 'num_of_copies': '(4)',
    #  'call_no': '658.4092 SANDBER'}, {'status': 'Available', 'branch_name': 'Morgan', 'branch_section': 'Morgan Hill Adult - Nonfiction S
    # ection', 'num_of_copies': 'Hill', 'call_no': '658.4092 SANDBER'}, {'status': 'Available', 'branch_name': 'Saratoga', 'branch_section'
    # : 'Saratoga Adult - Nonfiction Section', 'num_of_copies': '(5)', 'call_no': '658.4092 SANDBER'}, {'status': 'Due 02-20-16', 'branch_n
    # ame': 'Campbell', 'branch_section': 'Campbell Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'st
    # atus': 'Due 02-13-16', 'branch_name': 'Cupertino', 'branch_section': 'Cupertino Adult - Nonfiction Section', 'num_of_copies': '1', 'c
    # all_no': '658.4092 SANDBER'}, {'status': 'Due 11-23-15', 'branch_name': 'Cupertino', 'branch_section': 'Cupertino Adult - Nonfiction 
    # Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'Due 02-26-16', 'branch_name': 'Cupertino', 'branch_sectio
    # n': 'Cupertino Adult - Nonfiction Section', 'num_of_copies': '(2)', 'call_no': '658.4092 SANDBER'}, {'status': 'On Holdshelf', 'branc
    # h_name': 'Cupertino', 'branch_section': 'Cupertino Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'},
    #  {'status': 'In storage', 'branch_name': 'Gilroy', 'branch_section': 'Gilroy Adult - Nonfiction Section', 'num_of_copies': '(2)', 'ca
    # ll_no': '658.4092 SANDBER'}, {'status': 'Due 02-24-16', 'branch_name': 'Gilroy', 'branch_section': 'Gilroy Adult - Nonfiction Section
    # ', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'On Holdshelf', 'branch_name': 'Milpitas', 'branch_section': 'Mil
    # pitas Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'Due 02-29-16', 'branch_name': 'M
    # ilpitas', 'branch_section': 'Milpitas Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': '
    # Due 02-13-16', 'branch_name': 'Morgan', 'branch_section': 'Morgan Hill Adult - Nonfiction Section', 'num_of_copies': 'Hill', 'call_no
    # ': '658.4092 SANDBER'}, {'status': 'Due 02-22-16', 'branch_name': 'Saratoga', 'branch_section': 'Saratoga Adult - Nonfiction Section'
    # , 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'Due 02-16-16', 'branch_name': 'Saratoga', 'branch_section': 'Sara
    # toga Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}, {'status': 'Due 02-22-16', 'branch_name': 'Wo
    # odland', 'branch_section': 'Woodland Adult - Nonfiction Section', 'num_of_copies': '1', 'call_no': '658.4092 SANDBER'}]}
    
    availabilities_for_isbn = {}  # key: isbn, value: dict of dicts
    full_list_of_branch_avails = []

    # requests.get the sccl search page using isbn
    # turn SCCl into a templated string, {}
    sccl_search_url = SCCL_SEARCH_URL_BEG + str(isbn) + SCCL_SEARCH_URL_END

    # requests.get the contents of the page and convert to pq object
    page = requests.get(sccl_search_url)
    pq_page = pq(page.content)

    # find the sccl id no for the isbn on the page by css selector
    availability_string = pq_page('a.circInfo.value.underlined').attr('href')

    if availability_string:
        regex_search_result = re.search('/(\w*)\?', availability_string)
        if regex_search_result:
            if regex_search_result.group(1):
                regex_match = regex_search_result.group(1)               
        sccl_id_num = regex_match  # slices off the leading / and trailing ?
    else:
        availabilities_for_isbn[isbn] = "Item Not Found"
        return availabilities_for_isbn

    # with the sccl_id_num, get the sccl availability json
    sccl_avail_url = SCCL_AVAILABILITY_URL_BEG + sccl_id_num + SCCL_AVAILABILITY_URL_JSONEND

    avail_page = requests.get(sccl_avail_url)
    json_avail_page = json.loads(avail_page.text)
    html_section_only = json_avail_page["html"]
    
    pq_html_section = pq(html_section_only)

    # find table rows that are not under <thead> tags
    non_thead_tr_list = pq_html_section.find('tr').filter(lambda i: not pq(this).parents('thead')).items()

    for tr in non_thead_tr_list:
        list_of_status_details = []
        dict_of_status_details = {}
        for td in tr.find('td').items():
            list_of_status_details.append(td.text())
        branch_name_and_copies = list_of_status_details[0].split('(')  # 0-index item is branch name and num of copies
        if len(branch_name_and_copies) == 1:
            branch_name_and_copies.append('1')  # Add a num of copies for those without multiple
        else:
            branch_name_and_copies[1] = branch_name_and_copies[1][:-1] # Num of copies without parens
        
        dict_of_status_details['branch_name'] = branch_name_and_copies[0]
        dict_of_status_details['num_of_copies'] = int(branch_name_and_copies[1]) 
        dict_of_status_details['branch_section'] = list_of_status_details[1]
        dict_of_status_details['call_no'] = list_of_status_details[2]
        dict_of_status_details['status'] = list_of_status_details[3]
        full_list_of_branch_avails.append(dict_of_status_details)

    availabilities_for_isbn[isbn] = full_list_of_branch_avails

    return availabilities_for_isbn


def get_isbn13_from_dict(dict_for_item):
    """Given a returned dict, get the ISBN-13 of the item."""

    isbn_13_key = 'ISBN-13'

    key = dict_for_item.keys()[0]
    isbn_dict = dict_for_item.get(key)
    isbn_13 = isbn_dict.get(isbn_13_key)

    return isbn_13


def get_availabilities_for_list_of_books(list_of_dicts):
    """Given the returned list of dicts from get_isbns_from_urls_list(list_of_dicts),
    return a respective dict of sccl availabilities for each item in the list."""

    list_of_dicts_with_availabilities = []

    for dict_for_item in list_of_dicts:
        # key_for_dict = dict_for_item.keys()[0]
        # isbn_dict_for_item = dict_for_item.get(key_for_dict)
        # isbn_10_for_item = isbn_dict_for_item.get(isbn_10_key)
        # isbn_13_for_item = isbn_dict_for_item.get(isbn_13_key)
        isbn_13_for_item = get_isbn13_from_dict(dict_for_item)
        dict_of_item_availability = get_sccl_availability(isbn_13_for_item)
        # append the dictionary to the list in order of original search results rank
        list_of_dicts_with_availabilities.append(dict_of_item_availability)

    return list_of_dicts_with_availabilities





















if __name__ == '__main__':
    # VERSION FOR TESTING ONLY LOOKING AT ONE RESULT - 4.5 seconds of processing
    # urls = get_urls_by_search_keywords("brain rules")
    # isbns = get_isbn_by_url(urls[0])
    # isbn_13_test = get_isbn13_from_dict(isbns)
    # avails = get_sccl_availability(isbn_13_test)
    # pprint.pprint(avails)

    # VERSION FOR TESTING ON FULL LIST OF 10 RESULTS - 18 seconds of processing
    urls = get_urls_by_search_keywords("lean in")
    isbns = get_isbns_from_urls_list(urls)
    avails = get_availabilities_for_list_of_books(isbns)
    pprint.pprint(avails)


