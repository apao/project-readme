"""Utility file to add info to project readme database."""

from sqlalchemy import func
# from sqlalchemy.orm import subqueryload
from model import Book
from model import Author
from model import BookAuthors
from model import ISBN10
from model import ISBN13
from model import GoodreadsInfo
from model import Format
from model import BookFormat
from model import Query
from model import QueryBook
from model import LibrarySystem
from model import LibraryBranch

from model import db
# from server import app
from datetime import datetime



def add_new_query(keywords):
    """Given search keywords, add a new query to the db."""

    current_time = datetime.utcnow()
    new_query = Query(query_keywords=keywords, last_updated=current_time)
    db.session.add(new_query)
    db.session.commit()

    return new_query.query_id


def add_new_book(queryid, newdict, rank):
    """Given a dict about a book, add the book details to the db."""

    new_book = Book(
                    worldcaturl=newdict['worldcaturl'], 
                    title=newdict['title'], 
                    publisher=newdict['publisher'], 
                    page_count=newdict['page_count'], 
                    coverurl=newdict['coverurl'], 
                    summary=newdict['summary']
                   )

    db.session.add(new_book)
    db.session.flush()

    # AUTHOR(S)
    author_list = newdict['author']

    for author in author_list:
        # CONSIDER ADDING CONDITIONAL TO MAKE SURE AUTHORS DO NOT REPEAT IN THE AUTHOR TABLE
        # Adds an author to the author table
        new_author = Author(author_name=author)
        db.session.add(new_author)
        db.session.flush()
        # Correlates each author to the book in the BookAuthors table
        new_book_author = BookAuthors(book_id=new_book.book_id, author_id=new_author.author_id)
        db.session.add(new_book_author)
        db.session.flush()

    # ISBN-10's
    isbn10_list = newdict['ISBN-10']

    for isbn in isbn10_list:
        new_isbn10 = ISBN10(book_id=new_book.book_id, isbn10=isbn)
        db.session.add(new_isbn10)
        db.session.flush()

    # ISBN-13's
    isbn13_list = newdict['ISBN-13']

    for isbn in isbn13_list:
        new_isbn13 = ISBN13(book_id=new_book.book_id, isbn13=isbn)
        db.session.add(new_isbn13)
        db.session.flush()

    # GOODREADS INFO
    isbn_to_goodreads_list = newdict['isbn_to_goodreads_list']

    for goodreads_map in isbn_to_goodreads_list:
        isbn13 = goodreads_map['isbn13']

        isbn13_id_for_item = ISBN13.query.filter_by(isbn13=isbn13).first().isbn13_id
        new_goodreadsinfo = GoodreadsInfo(isbn13_id=isbn13_id_for_item,
                                          goodreads_work_id=goodreads_map['goodreads_work_id'],
                                          goodreads_rating=goodreads_map['goodreads_rating'],
                                          goodreads_ratings_count=goodreads_map['goodreads_ratings_count'],
                                          goodreads_review_count=goodreads_map['goodreads_review_count'])
        db.session.add(new_goodreadsinfo)
        db.session.flush()

    # FORMAT & BOOKFORMAT
    format = newdict['format']
    new_format = Format(format_type=format)
    db.session.add(new_format)
    db.session.flush()

    new_book_format = BookFormat(book_id=new_book.book_id, format_id=new_format.format_id)
    db.session.add(new_book_format)
    db.session.flush()

    # QUERY & QUERYBOOK
    new_query_book = QueryBook(query_id=queryid, book_id=new_book.book_id, rank_of_result=rank)
    db.session.add(new_query_book)
    db.session.flush()

    db.session.commit()

    print "New book added!"

    return new_book.book_id


def get_db_results(queryid):
    """Return a list of dictionary results from the database by searching for queryid."""

    db_results_list = []
    querybook_list = QueryBook.query.filter_by(query_id=queryid).order_by("book_id").all()

    for querybook in querybook_list:

        result_dict = {}
        current_book = querybook.book

        result_dict['bookid'] = current_book.book_id
        result_dict['worldcaturl'] = current_book.worldcaturl
        result_dict['title'] = current_book.title
        result_dict['publisher'] = current_book.publisher
        result_dict['page_count'] = current_book.page_count
        result_dict['coverurl'] = current_book.coverurl
        result_dict['summary'] = current_book.summary
        result_dict['format'] = current_book.bookformats[0].format.format_type

        # CONSIDER USING SQLALCHEMY RELATIONSHIP LOADING
        # http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html
        # author_list = BookAuthors.query.filter_by(book_id=bookid).all()
        author_list_for_dict = [a.author.author_name for a in current_book.authors]
        result_dict['author'] = author_list_for_dict

        # isbn10_list = ISBN10.query.filter_by(book_id=bookid).all()
        isbn10_list_for_dict = [num.isbn10 for num in current_book.isbn10s]
        result_dict['ISBN-10'] = isbn10_list_for_dict

        # isbn13_list = ISBN13.query.filter_by(book_id=bookid).all()
        isbn13_list_for_dict = [num.isbn13 for num in current_book.isbn13s]
        result_dict['ISBN-13'] = isbn13_list_for_dict

        db_results_list.append(result_dict)

    return db_results_list


def get_db_book_details(bookid):
    """Return a dictionary for a book from the database by searching for bookid."""

    current_book = Book.get_book_by_id(bookid)

    result_dict = {}

    result_dict['bookid'] = current_book.book_id
    result_dict['worldcaturl'] = current_book.worldcaturl
    result_dict['title'] = current_book.title
    result_dict['publisher'] = current_book.publisher
    result_dict['page_count'] = current_book.page_count
    result_dict['coverurl'] = current_book.coverurl
    result_dict['summary'] = current_book.summary
    result_dict['format'] = current_book.bookformats[0].format.format_type

    # CONSIDER USING SQLALCHEMY RELATIONSHIP LOADING
    # http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html
    # author_list = BookAuthors.query.filter_by(book_id=bookid).all()
    author_list_for_dict = [a.author.author_name for a in current_book.authors]
    result_dict['author'] = author_list_for_dict

    # isbn10_list = ISBN10.query.filter_by(book_id=bookid).all()
    isbn10_list_for_dict = [num.isbn10 for num in current_book.isbn10s]
    result_dict['ISBN-10'] = isbn10_list_for_dict

    # isbn13_list = ISBN13.query.filter_by(book_id=bookid).all()
    isbn13_list_for_dict = [num.isbn13 for num in current_book.isbn13s]
    result_dict['ISBN-13'] = isbn13_list_for_dict

    isbn13_id_list = [num.isbn13_id for num in current_book.isbn13s]
    
    goodreadsinfo_matches = GoodreadsInfo.query.filter(GoodreadsInfo.isbn13_id.in_(isbn13_id_list)).all()
    sorted_goodreadsinfo = list(sorted(goodreadsinfo_matches, key=lambda k: int(k.goodreads_ratings_count)))
    leading_goodreadsinfo_match = sorted_goodreadsinfo[0]
    result_dict['goodreads_info'] = leading_goodreadsinfo_match

    return result_dict


























# def add_new_author(newdict):
#     """Given a dict about a book, add the author details to the db."""

#     author_list = newdict['author']

#     for author in author_list:
#         new_author = Author(author_name=author)
#         db.session.add(new_author)
#         db.session.flush()


# def correlate_book_author(newdict):
#     """Given a dict about a book, 









# if __name__ == "__main__":
#     connect_to_db(app)

#     # In case tables haven't been created, create them
#     db.create_all()

#     # Import different types of data
#     load_users()
#     load_movies()
#     load_ratings()
#     set_val_user_id()
#     print "Load complete."