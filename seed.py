"""Utility file to seed database with library system and branch data."""

from model import LibrarySystem
from model import LibraryBranch

from model import connect_to_db, db
from server import app


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

    with open("data/libdata.txt") as libdatafile:
        for line in libdatafile:
            line = line.rstrip()
            sys_id, branch_name, branch_zipcode, branch_public_access, branch_card_policy, branch_overdrive_status, branch_address, branch_geo, branch_phone = line.split("|")

            librarybranch = LibraryBranch(sys_id=int(sys_id),
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


if __name__ == "__main__":
    connect_to_db(app)

    # Creates all models associated with app
    db.create_all()

    # Import different types of data
    load_librarysystems()
    load_librarybranches()
    print "Load complete."