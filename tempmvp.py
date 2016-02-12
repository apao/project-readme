import os
import requests
import urllib
from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
from lxml import etree


def search_for_books(user_search_keywords):
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

    dict_of_search_results = {}

    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)
    WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
    WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
    WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    worldcat_ready_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    # requests.get the search results page and
    results_page_xml = requests.get(worldcat_ready_url)

    # use pyquery to query the results_page_xml
    results_page_pq = pq(etree.fromstring(results_page_xml.content))

    # find the full text from the appropriate element <content>
    list_of_content_elements = results_page_pq("content")
    fourth_content_element = list_of_content_elements[3]
    text_of_fourth_content_element = fourth_content_element.text
    soup_of_text = bs(text_of_fourth_content_element, "lxml")

    for rank in range(1, 11):

        dict_for_result = {}
        result_id = "result-"+str(rank)
        pos_of_author = rank - 1
        # rank_of_result: get the rank of result
        rank_of_result = rank
        # book_title: get the book title
        book_title = soup_of_text.find(id=result_id).text
        # author: get the book author(s)
        list_of_authors = soup_of_text.findAll("div", {"class": "author"})
        author = list_of_authors[pos_of_author].text[3:]
        # worldcat_url: find href result with id="result-1" and create the new url to store in the dict
        result_href_string = soup_of_text.find(id=result_id, href=True)['href']
        new_url = WORLDCAT_STANDARD_URL+result_href_string

        # assign key-value to dictionary for the specific result
        dict_for_result['rank'] = rank_of_result
        dict_for_result['title'] = book_title
        dict_for_result['author'] = author
        dict_for_result['worldcaturl'] = new_url

        # assign the dict for the specific result to the final dict of dicts
        dict_of_search_results[result_id] = dict_for_result

    return dict_of_search_results



def get_worldcat_book_details(currentdict):
    # return list of only ISBN-13's for each url:
    # [ { '[url]': [#, #, #, ...] },
    #   ...
    # ]

    for rank in range(1, 11):
        current_dict = {}
        result_id = "result-"+str(rank)
        


def get_sccl_availability(isbn):
    # for each isbn, return list of dictionaries:
    # [ { 'isbn': { 'branch_name': ____,
    #               'status': ____,
    #               'number_of_copies': ____,
    #               'collection_name': ____,
    #               'call_no': ____}
    #   }
    # ]

    pass


