"""Models and database functions for project readme."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    birth_month = db.Column(db.Integer, nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)
    preferred_library_sys = db.Column(db.Integer, db.ForeignKey('librarysystems.sys_id'), nullable=True)
    preferred_library_sys_username = db.Column(db.String(30), nullable=True)
    preferred_library_sys_password = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        """Represents user object."""
        return "<User ID: %s, username: %s>" % (self.user_id, self.username)

    @classmethod
    def get_user_by_id(cls, user_id):

        user = User.query.filter_by(user_id=user_id).first()

        return user


class Book(db.Model):
    """Book searched on website."""

    __tablename__ = "books"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    worldcaturl = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    publisher = db.Column(db.String(500), nullable=False)
    page_count = db.Column(db.String(10), nullable=True)
    summary = db.Column(db.String(10000), nullable=True)
    coverurl = db.Column(db.String(500), nullable=False)
   
    def __repr__(self):
        """Represents book object"""
        return "<Book ID: %s, Title: %s>" % (self.book_id, self.title)

    @classmethod
    def get_book_by_id(cls, book_id):

        book = Book.query.filter_by(book_id=book_id).first()

        return book


class ISBN10(db.Model):
    """ISBN-10 number for item on website."""

    __tablename__ = "isbn10s"

    isbn10_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    isbn10 = db.Column(db.String(20), nullable=False)

    book = db.relationship('Book', backref=db.backref('isbn10s', order_by=isbn10_id))


class ISBN13(db.Model):
    """ISBN-13 number for item on website."""

    __tablename__ = "isbn13s"

    isbn13_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    isbn13 = db.Column(db.String(20), nullable=False)
    lead_isbn13_by_gr_ratings_count = db.Column(db.Boolean, nullable=True, default=False)

    book = db.relationship('Book', backref=db.backref('isbn13s', order_by=isbn13_id))


class Author(db.Model):
    """Author for item on website."""

    __tablename__ = "authors"

    author_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_name = db.Column(db.String(50), nullable=False)


class BookAuthors(db.Model):
    """Association table for books and authors on website."""

    __tablename__ = "bookauthors"

    bookauthor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)

    author = db.relationship('Author', backref=db.backref('books', order_by=book_id))
    book = db.relationship('Book', backref=db.backref('authors', order_by=book_id)) 


class Format(db.Model):
    """Format for item on website."""

    __tablename__ = "formats"

    format_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    format_type = db.Column(db.String(50), nullable=False)


class BookFormat(db.Model):
    """Association table for books and formats on website."""

    __tablename__ = "bookformats"

    bookformat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    format_id = db.Column(db.Integer, db.ForeignKey('formats.format_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)

    format = db.relationship('Format', backref=db.backref('books', order_by=format_id))
    book = db.relationship('Book', backref=db.backref('bookformats', order_by=book_id)) 


class AmazonInfo(db.Model):
    """Amazon Info for book on website."""

    __tablename__ = "amazoninfo"

    amazoninfo_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    amazon_ASIN = db.Column(db.String(50), nullable=False)
    amazon_rating = db.Column(db.Float, nullable=True)
    amazon_review_count = db.Column(db.Integer, nullable=True)
    amazon_review_text = db.Column(db.String(10000), nullable=True)

    book = db.relationship('Book', backref=db.backref('amazoninfo', order_by=amazoninfo_id))


class GoodreadsInfo(db.Model):
    """Goodreads Info for book on website."""

    __tablename__ = "goodreadsinfo"

    goodreadsinfo_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    isbn13_id = db.Column(db.Integer, db.ForeignKey('isbn13s.isbn13_id'), nullable=False)
    goodreads_work_id = db.Column(db.String(50), nullable=False)
    goodreads_rating = db.Column(db.Float, nullable=True)
    goodreads_ratings_count = db.Column(db.Integer, nullable=True)
    goodreads_review_count = db.Column(db.Integer, nullable=True)
    goodreads_review_text = db.Column(db.String(10000), nullable=True)

    isbn13 = db.relationship('ISBN13', backref=db.backref('goodreadsinfo', order_by=goodreadsinfo_id))


class LibrarySystem(db.Model):
    """Library system on website."""

    __tablename__ = "librarysystems"

    sys_id = db.Column(db.Integer, primary_key=True)
    sys_name = db.Column(db.String(50), nullable=False)


class LibraryBranch(db.Model):
    """Library branch on website."""

    __tablename__ = "librarybranches"

    branch_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sys_id = db.Column(db.Integer, db.ForeignKey('librarysystems.sys_id'), nullable=False)
    branch_name = db.Column(db.String(100), nullable=False)
    branch_zipcode = db.Column(db.String(15), nullable=False)
    branch_public_access = db.Column(db.String(100), nullable=False)
    branch_card_policy = db.Column(db.String(1000), nullable=False)
    branch_overdrive_status = db.Column(db.String(50), nullable=True)
    branch_address = db.Column(db.String(100), nullable=False)
    branch_geo = db.Column(db.String(500), nullable=False)
    branch_phone = db.Column(db.String(50), nullable=True)

    library_system = db.relationship('LibrarySystem', backref=db.backref('librarybranches', order_by=branch_id))


class Genre(db.Model):
    """Genre on website."""

    __tablename__ = "genres"

    genre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)
    genre_desc = db.Column(db.String(1000), nullable=True)


class BookGenre(db.Model):
    """Association table for books and genres on website."""

    __tablename__ = "bookgenres"

    bookgenre_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)

    book = db.relationship('Book', backref=db.backref('genres', order_by=genre_id))


class Query(db.Model):
    """User query on website."""

    __tablename__ = "queries"

    query_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    query_keywords = db.Column(db.String(100), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)

    @classmethod
    def get_query_id_by_keywords(cls, keywords):

        query_id = Query.query.filter_by(query_keywords=keywords).first().query_id

        return query_id


class QueryBook(db.Model):
    """Association table for query and book on website."""

    __tablename__ = "querybooks"

    querybook_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('queries.query_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    rank_of_result = db.Column(db.Integer, nullable=False)

    book = db.relationship('Book', backref=db.backref('queries', order_by=querybook_id))

    @classmethod
    def get_results_by_query_id(cls, query_id):

        results = QueryBook.query.filter_by(query_id=query_id).all()

        return results


def add_new_query(keywords):
    """Given search keywords, add a new query to the db."""

    current_time = datetime.utcnow()
    new_query = Query(query_keywords=keywords, last_updated=current_time)
    db.session.add(new_query)
    db.session.commit()

    return new_query.query_id


def add_new_book(queryid, newdict, rank):
    """Given a dict about a book, add the book details to the db."""

    # TODO - push model.Book creation upstream
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

    # TODO - consider letting SQLAlchemy handle this by setting up Relationships
    # TODO - so you can do Book.authors = [Author(), Author()]
    # TODO - work on caching behavior
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

    # TODO - consider letting SQLAlchemy handle this by setting up Relationships
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

    # TODO - consider letting SQLAlchemy handle this by setting up Relationships
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

    # TODO - consider letting SQLAlchemy handle this by setting up Relationships
    # FORMAT & BOOKFORMAT
    format = newdict['format']
    new_format = Format(format_type=format)
    db.session.add(new_format)
    db.session.flush()

    new_book_format = BookFormat(book_id=new_book.book_id, format_id=new_format.format_id)
    db.session.add(new_book_format)
    db.session.flush()

    # TODO - consider letting SQLAlchemy handle this by setting up Relationships
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
    if sorted_goodreadsinfo:
        leading_goodreadsinfo_match = sorted_goodreadsinfo[0]
    else:
        leading_goodreadsinfo_match = []
    result_dict['goodreads_info'] = leading_goodreadsinfo_match

    return result_dict


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///projectreadme'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."