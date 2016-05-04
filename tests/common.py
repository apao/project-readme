import os

def load_from_file(filename):
    """
    :param filename:
    :return:
    """

    filepath = os.path.abspath(os.path.dirname(__file__))
    full_filepath = filepath + '/' + filename

    with open(full_filepath, 'r') as f:
        data = f.read()
    return data
