import requests
from pyquery import PyQuery as pq
import json

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


#
# # =======================================================
# # FUNCTIONS TO GET EACH LIBRARY'S EBOOK ITEM AVAILABILITY
# # =======================================================
#
# def get_sccl_eresources_by_keyword(keyword):
#     """Given search keywords, provides availability for eresources in the Santa Clara County Library System."""
#
#     sccl_eresource_search_url = SCCL_SEARCH_URL_BEG + urllib.quote_plus(keyword) + SCCL_SEARCH_URL_END
#
#     return sccl_eresource_search_url
#
#
# def get_sfpl_ebooks_by_keyword(keyword):
#     """Given search keywords, provides availability for ebooks in the San Francisco Public Library System."""
#
#     sfpl_ebook_id_list = []
#     list_of_final_items = []
#     # https://sfpl.bibliocommons.com/search?t=smart&search_category=keyword&commit=Search&q=lean%20in&formats=EBOOK
#     SFPL_BASE_URL = "https://sfpl.bibliocommons.com"
#     SFPL_SEARCH_EBOOKS_URL_BEG = "https://sfpl.bibliocommons.com/search?t=smart&search_category=keyword&commit=Search&q="
#     SFPL_SEARCH_EBOOKS_URL_END = "&formats=EBOOK"
#     search_keywords = urllib.quote(keyword)
#
#     sfpl_search_ebooks_url = SFPL_SEARCH_EBOOKS_URL_BEG + search_keywords + SFPL_SEARCH_EBOOKS_URL_END
#
#     # requests.get the contents of the search page and convert to pq object
#     page = requests.get(sfpl_search_ebooks_url)
#     pq_page = pq(page.content)
#
#     # find the href with sfpl id no. on the page by css selector
#     # ebook_id_objects = pq_page('img.jacketCover.bib_detail').attr('id')
#     # ebook_id_pq_objects = pq_page.find('img.jacketCover.bib_detail')
#     # for i in range(len(ebook_id_pq_objects)):
#     #     sfpl_ebook_id_list.append(ebook_id_pq_objects.eq(i).attr('id'))
#     #
#     # title_lst = [i.text() for i in pq_page.items('span.title')]
#     # author_lst = [i.text() for i in pq_page.items('span.author')]
#
#     title_results_lst = [i.find('span.title').text() for i in pq_page.items('div.list_item_outer')]
#     author_results_lst = [i.find('span.author').text() for i in pq_page.items('div.list_item_outer')]
#     item_href_lst = [i.find('a.jacketCoverLink').attr('href') for i in pq_page.items('div.pull-left.visible-xs.visible-sm')]
#     ebook_format_provider_lst = [i.find('span.value.callNumber').text() for i in pq_page.items('div.row.circ_info.list_item_section')]
#     coverurl_lst = [i.find('img.jacketCover').attr('src') for i in pq_page.items('div.pull-left.visible-xs.visible-sm')]
#     item_avail_href_lst = [i.find('a.click_n_sub').attr('href') for i in pq_page.items('div.availability_block')]
#     item_request_href_lst = [i.find('a.digital_request').attr('href') for i in pq_page.items('span.hold_button')]
#
#     item_details_full_url_lst = []
#     for href in item_href_lst:
#         item_full_details_url = SFPL_BASE_URL + href
#         item_details_full_url_lst.append(item_full_details_url)
#
#     for i in range(len(title_results_lst)):
#         if item_avail_href_lst[i] and item_request_href_lst[i]:
#             item_dict = dict(title=title_results_lst[i],
#                              author=author_results_lst[i],
#                              item_details_url=item_details_full_url_lst[i],
#                              ebook_format_provider=ebook_format_provider_lst[i],
#                              coverurl=coverurl_lst[i],
#                              item_avail_url=SFPL_BASE_URL + item_avail_href_lst[i],
#                              item_request_url=SFPL_BASE_URL + item_request_href_lst[i])
#             final_item_dict = get_sfpl_ebook_details(item_dict, item_dict.get('item_details_url'))
#         else:
#             item_dict = dict(title=title_results_lst[i],
#                              author=author_results_lst[i],
#                              item_details_url=item_details_full_url_lst[i],
#                              ebook_format_provider=ebook_format_provider_lst[i],
#                              coverurl=coverurl_lst[i],
#                              item_avail_url="",
#                              item_request_url="")
#             final_item_dict = get_sfpl_ebook_details(item_dict, item_dict.get('item_details_url'))
#         list_of_final_items.append(final_item_dict)
#
#     return list_of_final_items
#
#
# def get_sfpl_ebook_details(itemdict, sfplurl):
#     """Given an SFPL item url, provide details about the ebook."""
#
#     # item_libid_lst = []
#     # isbns_full_lst = []
#     # other_details_lst = []
#     # summary_lst = []
#     # publisher_lst = []
#     # item_characteristics_lst = []
#     # goodreads_info_lst = []
#
#     item_page = requests.get(sfplurl)
#     pq_item_page = pq(item_page.content)
#     item_libid_str = pq_item_page('div.content.itemDetail').attr('id')
#     itemdict['sfpl_libid'] = item_libid_str
#     # item_libid_lst.append(item_libid_str)
#     item_isbns_str = pq_item_page('div.content.itemDetail').attr('data-isbns')
#     item_isbns_lst = item_isbns_str.split(',')
#     # isbns_full_lst.append(item_isbns_lst)
#     for isbn in item_isbns_lst:
#         if len(isbn) == 13:
#             itemdict['isbn13'] = isbn
#             goodreads_info = get_goodreads_info_by_isbn13(isbn)
#             itemdict['isbn_to_goodreads_list'] = goodreads_info
#             break
#             # goodreads_info_lst.append(goodreads_info)
#     item_pub_and_other_lst = [i.find('span.value').text() for i in pq_item_page.items('div.dataPair.clearfix')]
#     itemdict['publisher_and_page_count'] = item_pub_and_other_lst
#     # if len(item_pub_and_other_lst) == 5:
#     #     item_pub, item_edition, item_isbns, item_characteristics, item_other_contributors = item_pub_and_other_lst
#     # else:
#     #     item_pub, item_edition, item_isbns, item_characteristics = item_pub_and_other_lst
#     # publisher_lst.append(item_pub)
#     # item_characteristics_lst.append(item_characteristics)
#     # other_details_lst.append(item_pub_and_other_lst)
#     summary = pq_item_page('div.bib_description').text()
#     itemdict['summary'] = summary
#     # summary_lst.append(summary)
#
#     return itemdict
#
