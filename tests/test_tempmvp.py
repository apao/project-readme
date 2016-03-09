from readme import tempmvp


def _validate_result(current_result):
    assert type(current_result) is dict
    assert type(current_result['author']) is list

    assert current_result['coverurl'] is not None
    assert type(current_result['rank']) is int

    assert current_result['title'] is not None

    worldcat_url = current_result['worldcaturl']
    assert worldcat_url.startswith('http://www.worldcat.org/title/')


def test_search_for_print_books():
    """ Check if tempmvp.search_for_print_books(url) returns the correct number of results.
    """
    url = "http://www.worldcat.org/search?q=lean+in&fq=%20(%28x0%3Abook+x4%3Aprintbook%29)%20%3E%20ln%3Aeng&se=&sd=&qt=facet_fm_checkbox&refinesearch=true&refreshFormat=undefined"
    results = tempmvp.search_for_print_books(url)
    # I expect this to give a list of dicts with properties....

    assert len(results) == 10

    assert type(results) is list
    for current_result in results:
        _validate_result(current_result)
