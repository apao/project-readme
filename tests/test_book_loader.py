import pickle
import os

from readme import book_loader
from common import load_from_file
from mock import MagicMock, patch

def _validate_result(current_result):
    assert type(str(current_result)) is str
    assert type(current_result) is int


def test_search_for_print_books():
    """ Check if book_loader.search_for_print_books(xml_content) returns the correct number of validated results.
    """
    url = "http://www.worldcat.org/search?q=lean+in&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
    xml_content = load_from_file('data/worldcatxml.html')

    int_results = book_loader.search_for_print_books(xml_content)

    # Expect list of 10 results total, with each result as a string that can also be converted into an int
    assert len(int_results) == 10
    assert type(int_results) is list
    for current_result in int_results:
        _validate_result(current_result)


def _stable_key(args=None, kwargs=None):
    args = args or tuple()
    kwargs = kwargs or dict()
    return pickle.dumps(dict(args=args, kwargs=kwargs))

class TestCreateBookFromWorldcat(object):
    # TODO - pull all html_content for worldcat to a class-level attribute
    worldcat_html = load_from_file('data/worldcat.html')

    goodreads_html = load_from_file('data/goodreads.html')

    test_api_key = 'test-test-test'
    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        os.environ['GOODREADS_API_KEY'] = cls.test_api_key

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        os.environ.pop('GOODREADS_API_KEY')

    def _fake_requests_response(self, content):
        mock_resp = MagicMock()
        mock_resp.content = content
        return mock_resp

    def test_create_book_from_worldcat_id(self):
        """
        :return:
        """
        oclc_id = 813526963

        values = {
            _stable_key(args=('http://www.worldcat.org/oclc/813526963',)):
                self._fake_requests_response(self.worldcat_html),
            _stable_key(args=('https://www.goodreads.com/book/isbn',), kwargs=dict(params=dict(key=self.test_api_key, isbn='9780385349949'))):
                self._fake_requests_response(self.goodreads_html),
        }

        def requests_get_side_effect(*args, **kwargs):
            key = _stable_key(args=args, kwargs=kwargs)
            return values[key]

        mock_get = MagicMock()
        mock_get.side_effect = requests_get_side_effect

        with patch('requests.get', new=mock_get):
            current_book = book_loader.create_book_from_worldcat_id(oclc_id)

        assert current_book.book_id == 813526963


    def test_load_book_from_worldcat_details_page(self):
        """
        :return:
        """
        worldcat_details_page_url = "http://www.worldcat.org/oclc/813526963"
        oclc_id = 813526963

        book = book_loader._load_book_from_worldcat_details_page(self.worldcat_html, worldcat_details_page_url, oclc_id)

        # Expect the book object to have all the expected attributes
        assert book.book_id == 813526963
        assert book.title == 'Lean in : women, work, and the will to lead'
        assert book.publisher == 'New York : Alfred A. Knopf, 2013.'
        assert book.worldcaturl == 'http://www.worldcat.org/oclc/813526963'
        assert book.page_count == '228'
        assert 'United States' in book.summary
        assert 'TEDTalk' in book.summary
        assert book.coverurl == 'http://coverart.oclc.org/ImageWebSvc/oclc/+-+814170863_140.jpg?SearchOrder=+-+OT,OS,TN,GO,FA'


    def test_load_title_from_worldcat_details_page(self):
        """
        :return:
        """

        pass


    def test_load_authors_from_worldcat_details_page(self):
        """
        :return:
        """

        worldcat_details_page_url = "http://www.worldcat.org/oclc/813526963"
        oclc_id = 813526963

        author_list = book_loader._load_authors_from_worldcat_details_page(self.worldcat_html)

        assert type(author_list) is list
        assert len(author_list) == 2

        for author_obj in author_list:
            assert ("Sheryl" in author_obj.author_name or "Nell" in author_obj.author_name)


    def test_load_isbns_from_worldcat_details_page(self):
        """
        :return:
        """

        isbn10_list, isbn13_list = book_loader._load_isbns_from_worldcat_details_page(self.worldcat_html)

        for current_isbn in isbn10_list:
            assert (len(current_isbn.isbn10) == 10 and current_isbn.isbn10 == '0385349947')

        for current_isbn in isbn13_list:
            assert (len(current_isbn.isbn13) == 13 and current_isbn.isbn13 == '9780385349949')


    def test_load_goodreads_info_from_goodreads_api(self):
        """
        :return:
        """

        isbn13 = '9780385349949'

        goodreads_info_obj = book_loader._load_goodreads_info_from_goodreads_api(self.goodreads_html)

        assert (goodreads_info_obj.goodreads_ratings_count >= 100000)
        assert (goodreads_info_obj.goodreads_rating >= 3.50)
        assert (goodreads_info_obj.goodreads_work_id == '21865596')
        assert (goodreads_info_obj.goodreads_review_count >= 220000)







