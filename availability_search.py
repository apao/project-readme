import requests
from pyquery import PyQuery as pq
import json

from model import LibraryBranch, get_book_isbn13s

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

    def normalize_availability(self, isbn13, dictlist):
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

    def normalize_availability(self, isbn13, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = self.create_search_url(isbn13)
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

    def normalize_availability(self, isbn13, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = self.create_search_url(isbn13)
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

    def normalize_availability(self, isbn13, dictlist):
        """Return normalized availability to pass to javascript for map rendering."""

        branch_dict = {}

        for avail in dictlist:
            current_branch = avail.get('branch_name')
            current_call_num = avail.get('call_no')
            current_branch_section = avail.get('branch_section')
            current_num_of_copies = avail.get('num_of_copies')
            current_url = self.create_search_url(isbn13)
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


def get_table_and_map_availability(bookid):
    """
    :param bookid:
    :return:
    """

    final_dict = {
        'avail_list': [],
        'marker_list': 0
    }

    isbn13_list = get_book_isbn13s(bookid)

    for isbn13_obj in isbn13_list:
        current_isbn13 = isbn13_obj.isbn13
        result_dicts = get_availability_dicts_for_isbn13(current_isbn13)
        agg_norm_avail_list, newlist, final_marker_list = result_dicts
        final_dict = {
            'avail_list': newlist,
            'marker_list': final_marker_list
        }

        if agg_norm_avail_list:
            return final_dict
        else:
            continue

    # NOTE - we would only get here if there are no matches on ISBNs
    return final_dict


def get_availability_dicts_for_isbn13(isbn13):
    """
    :param isbn13:
    :return:
    """

    sccl_searcher = SCCLAvailabilitySearch()
    smcl_searcher = SMCLAvailabilitySearch()
    sfpl_searcher = SFPLAvailabilitySearch()
    lib_sys_searcher_list = [sccl_searcher, smcl_searcher, sfpl_searcher]

    # NOTE - initializing defaults values as empty lists to provide consistent return values for short-circuited conditions
    agg_norm_avail_list = list()
    newlist = list()
    final_marker_list = list()

    if not lib_sys_searcher_list:
        return agg_norm_avail_list, newlist, final_marker_list

    dict_to_evaluate = dict()
    for current_searcher in lib_sys_searcher_list:
        raw_availability = current_searcher.load_availability(isbn13)
        normalized_availability = current_searcher.normalize_availability(isbn13, raw_availability)
        dict_to_evaluate.update(normalized_availability)

    if not dict_to_evaluate:
        return agg_norm_avail_list, newlist, final_marker_list

    key_list = dict_to_evaluate.keys()
    for branch in key_list:
        lib_branch_obj = LibraryBranch.query.filter_by(branch_name=branch).first()
        if lib_branch_obj:
            dict_to_evaluate[branch]['branch_geo'] = lib_branch_obj.branch_geo
            dict_to_evaluate[branch]['sys_name'] = lib_branch_obj.library_system.sys_name
            dict_to_evaluate[branch]['branch_address'] = lib_branch_obj.branch_address
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

    return agg_norm_avail_list, newlist, final_marker_list


def _avails_to_markers(list_of_avails):
    """Return marker geojson based on list of availabilities."""

    marker_list = []

    for avail in list_of_avails:
        branch = avail.get('branch_name')
        avail_copies = avail.get('avail_copies', 0)
        unavail_copies = avail.get('unavail_copies', 0)
        where_to_find = avail.get('where_to_find')
        url = avail.get('search_url')
        branch_address = avail.get('branch_address')
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
            marker["properties"]["description"] = u"<div class='%s'><strong>%s</strong><br>Address: %s</div><p>Copies Available: %s<br>Copies Unavailable: %s<br>Call Number: %s | %s</p><p><a href='%s' target=\"_blank\" title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, branch_address ,avail_copies, unavail_copies, where_to_find[0][0], where_to_find[0][1], url)
            marker["properties"]["marker-symbol"] = marker_symbol
            # marker["properties"]["marker-color"] = "blue"
            # marker["properties"]["marker-size"] = "large"
            marker_list.append(marker)
        elif avail_copies == 0 or avail_copies == '0':
            marker_symbol = "harbor"
            marker["properties"]["description"] = u"<div class='%s'><strong>%s</strong><br>Address: %s</div><p>Copies Unavailable: %s</p><p><a href='%s' target=\"_blank\" title=\"Opens in a new window\">Go to library website to learn more.</a></p>" % (branch, branch, branch_address, unavail_copies, url)
            marker["properties"]["marker-symbol"] = marker_symbol
            # marker["properties"]["marker-color"] = "red"
            marker_list.append(marker)
        else:
            continue

    return marker_list
