import os

from sqlalchemy import create_engine

from app.config import DB_PATH
from app.models import Base


def init_db():
    """ Initializes the database if it does not already exist. """

    if not os.path.exists(DB_PATH):
        print("Database does not exist. Creating now...")

        engine = create_engine(f'sqlite:///{DB_PATH}')
        Base.metadata.create_all(engine)

        print("Database created successfully.")
    else:
        print("Database already exists. Skipping initialization.")


if __name__ == "__main__":
    init_db()
