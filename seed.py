"""Utility file to seed database with library system and branch data."""

from model import LibrarySystem
from model import LibraryBranch

from model import connect_to_db, db
from server import app


# {
#     'branch_name': 'Campbell',
#     'branch_zipcode': '',
#     'branch_public_access': '',
#     'branch_card_policy': '',
#     'branch_overdrive_status': '',
#     'branch_address': '',
#     'branch_geo': ''
# }


def load_librarysystems():
    """Load library systems to the db."""

    print "Loading Library Systems!"

    LibrarySystem.query.delete()

    libsys_list = ['Santa Clara County Library System', 'San Mateo County Library System', 'San Francisco Public Library System']

    for idx, libsys in enumerate(libsys_list):
        libsys_id = idx + 1
        new_librarysys = LibrarySystem(sys_id=libsys_id, sys_name=libsys)
        db.session.add(new_librarysys)

    db.session.commit()


def load_librarybranches():
    """Load library branches to the db."""

    print "Loading Library Branches!"

    LibraryBranch.query.delete()

    for row in open("data/libdata.txt"):
        row = row.rstrip()
        sys_id, branch_name, branch_zipcode, branch_public_access, \
        branch_card_policy, branch_overdrive_status, branch_address, \
        branch_geo, branch_phone = row.split("|")

        librarybranch = LibraryBranch(sys_id=sys_id,
                                      branch_name=branch_name,
                                      branch_zipcode=branch_zipcode,
                                      branch_public_access=branch_public_access,
                                      branch_card_policy=branch_card_policy,
                                      branch_overdrive_status=branch_overdrive_status,
                                      branch_address=branch_address,
                                      branch_geo=branch_geo,
                                      branch_phone=branch_phone)

        db.session.add(librarybranch)

    db.session.commit()


# def load_users():
#     """Load users from u.user into database."""
#
#     print "Users"
#
#     # Delete all rows in table, so if we need to run this a second time,
#     # we won't be trying to add duplicate users
#     User.query.delete()
#
#     # Read u.user file and insert data
#     for row in open("seed_data/u.user"):
#         row = row.rstrip()
#         user_id, age, gender, occupation, zipcode = row.split("|")
#
#         user = User(user_id=user_id,
#                     age=age,
#                     zipcode=zipcode)
#
#         # We need to add to the session or it won't ever be stored
#         db.session.add(user)
#
#     # Once we're done, we should commit our work
#     db.session.commit()
#
#
# def load_movies():
#     """Load movies from u.item into database."""
#
#     print "Movies"
#
#     Movie.query.delete()
#
#     # Read u.item file and insert data
#     for row in open("seed_data/u.item"):
#         row = row.rstrip()
#         movie_id, title, release_date, video_release_date, imdb_url, \
#         unknown, action, adventure, animation, children, comedy, crime, \
#         documentary, drama, fantasy, film_noir, horror, musical, mystery, \
#         romance, sci_fi, thriller, war, western  = row.split("|")
#
#         # Remove (YYYY) from title in u.item
#         title = title[:-7]
#
#         # Update release_date into datetime format
#         if release_date:
#             released_at = datetime.strptime(release_date, '%d-%b-%Y')
#         else:
#             released_at = None
#
#
#
#         movie = Movie(movie_id=movie_id,
#                     title=title,
#                     released_at=released_at,
#                     imdb_url=imdb_url)
#
#         # We need to add to the session or it won't ever be stored
#         db.session.add(movie)
#
#     # Once we're done, we should commit our work
#     db.session.commit()
#
#
# def load_ratings():
#     """Load ratings from u.data into database."""
#
#     print "Ratings"
#
#     # Delete all rows in table, so if we need to run this a second time,
#     # we won't be trying to add duplicate users
#     Rating.query.delete()
#
#     # Read u.data file and insert data
#     for row in open("seed_data/u.data"):
#         row = row.rstrip()
#         user_id, movie_id, score, timestamp = row.split("\t")
#
#         rating = Rating(user_id=user_id,
#                     movie_id=movie_id,
#                     score=score)
#
#         # We need to add to the session or it won't ever be stored
#         db.session.add(rating)
#
#     # Once we're done, we should commit our work
#     db.session.commit()


# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""
#
#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])
#
#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


# if __name__ == "__main__":
#     connect_to_db(app)
#
#     # Import different types of data
#     load_librarysystems()
#     load_librarybranches()
#     print "Load complete."