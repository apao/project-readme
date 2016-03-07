from readme import server

test_client = None

def setup_module(module):
    """ setup any state specific to the execution of the given module."""

    global test_client
    test_client = server.app.test_client()
    server.app.config['TESTING'] = True


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """

    global test_client
    test_client = None


def test_homepage():
    """ confirm homepage contains expected text and returns appropriate status code.
    """

    result = test_client.get('/')
    assert result.status_code == 200
    assert 'Find books you want to read for free in the libraries closest to you.' in result.data


def test_searchpage():
    """ confirm search page contains expected text and returns appropriate status code.
    """

    result = test_client.get('/search')
    assert result.status_code == 200
    assert '<form action="/results" method="POST">' in result.data
    assert '<input type="text" class="form-control" id="keywords" name="keywords" placeholder="Search by Title / Author / ISBN">' in result.data
    assert '<button type="submit" id="submitsearch" class="btn btn-primary btn-lg">' in result.data


def test_searchresultspage():

    pass




