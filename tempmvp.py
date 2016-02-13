import os
import requests
import urllib
from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
from lxml import etree
import re

WORLDCAT_STANDARD_URL = "http://www.worldcat.org"
WORLDCAT_SEARCH_URL = "http://www.worldcat.org/search?q="
WORLDCAT_FILTER_LANG_EN_PRINT_ONLY = "&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
SCCL_SEARCH_URL_BEG = "https://sccl.bibliocommons.com/search?utf8=%E2%9C%93&t=smart&search_category=keyword&q="
SCCL_SEARCH_URL_END = "&commit=Search&searchOpt=catalogue"
SCCL_AVAILABILITY_URL_BEG = "https://sccl.bibliocommons.com/item/show_circulation/"
SCCL_AVAILABILITY_URL_JSONEND = ".json"




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

    list_of_search_results = []

    # take a user's search keywords
    # convert string to match the format for the WorldCat search results page
    worldcat_ready_keywords = urllib.quote_plus(user_search_keywords)

    # http://www.worldcat.org/search?q=[ USER KEYWORDS ]&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined
    worldcat_ready_url = WORLDCAT_SEARCH_URL+worldcat_ready_keywords+WORLDCAT_FILTER_LANG_EN_PRINT_ONLY

    # requests.get the search results page and
    results_page_xml = requests.get(worldcat_ready_url)

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


def get_worldcat_book_details(list_of_dicts):
    # return list of only ISBN-13's for each url:
    # [ { '[url]': [#, #, #, ...] },
    #   ...
    # ]
    # >>> page = requests.get("http://www.worldcat.org/title/lean-in-women-work-and-the-will-to-lead/oclc/813526963&referer=brief_results")
    # >>> pq_details_page = pq(page.content)
    # >>> isbn = pq_details_page('#details-standardno').eq(0).text()
    # >>> isbn
    # 'ISBN: 9780385349949 0385349947'

    isbn_10_key = 'ISBN-10'
    isbn_13_key = 'ISBN-13'
    list_of_dicts_with_isbns = []

    for dict_of_result in list_of_dicts:
        # initialize the empty dicts for this specific result
        dict_for_url = {}
        dict_of_isbns_with_url_key = {}

        # get the url string from the dictionary passed into this function
        url = dict_of_result['worldcaturl']
        
        # requests.get the contents of the page and convert to pq object
        page = requests.get(url)
        pq_page = pq(page.content)
        
        # find the isbns on the page by their css selector and format them as a list
        isbn_string = pq_page('#details-standardno').eq(0).text()
        isbn_list = isbn_string.split(" ")
        
        # for any list item that is an ISBN of a particular length, assign the appropriate key and value
        for item in isbn_list:
            if item != "ISBN:" and len(item) == 10:
                dict_for_url[isbn_10_key] = item
            elif item != "ISBN:" and len(item) == 13:
                dict_for_url[isbn_13_key] = item
        
        # assign the type_of_isbn-isbn_no key-value pairs to the corresponding url's dictionary
        dict_of_isbns_with_url_key[url] = dict_for_url
        
        # append the dictionary to the list in order of original search results rank
        list_of_dicts_with_isbns.append(dict_of_isbns_with_url_key)

    return list_of_dicts_with_isbns


def get_sccl_availability(isbn):
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

    pass
    
    # requests.get the sccl search page using isbn
    sccl_search_url = SCCL_SEARCH_URL_BEG + isbn + SCCL_SEARCH_URL_END

    # requests.get the contents of the page and convert to pq object
    page = requests.get(sccl_search_url)
    pq_page = pq(page.content)

    # find the sccl id no for the isbn on the page by css selector
    availability_string = pq_page('a.circInfo.value.underlined').attr('href')
    if availability_string:
        regex_search_result = re.search('/(\w*)\?', availability_string)
        sccl_id_num = regex_search_result[1:-1] # slices off the leading / and trailing ?
    else:
        return "Item Unavailable"

    # with the sccl_id_num, get the sccl availability json
    sccl_avail_url = SCCL_AVAILABILITY_URL_BEG + sccl_id_num + SCCL_AVAILABILITY_URL_JSONEND













# if __name__ == '__main__':
#     search_for_books('lean in')
