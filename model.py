"""Models and database functions for project readme."""

from flask_sqlalchemy import SQLAlchemy

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
    worldcaturl = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    publisher = db.Column(db.String(128), nullable=False)
    page_count = db.Column(db.String(10), nullable=True)
    summary = db.Column(db.String(5000), nullable=True)
    coverurl = db.Column(db.String(256), nullable=False)
   
    def __repr__(self):
        """Represents book object"""
        return "<Book ID: %s, Title: %s>" % (self.book_id, self.title)

    @classmethod
    def get_book_by_id(cls, book_id):

        book = Book.query.filter_by(book_id=book_id).first()

        return book


# class CoverUrl(db.Model):
#     """Cover URL for item on website."""

#     __tablename__ = "coverurls"

#     coverurl_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
#     coverurl = db.Column(db.String(100), nullable=False)

#     book = db.relationship('Book', backref=db.backref('coverurls', order_by=coverurl_id))


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
    branch_card_policy = db.Column(db.String(500), nullable=False)
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

    import tempmvp
    avail_list = tempmvp.get_sfpl_availability("9780062349026")