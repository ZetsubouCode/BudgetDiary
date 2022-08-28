import os
from _env import ENV
from urllib.parse import quote_plus as urlquote
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(
    "mysql://{}:{}@{}/{}".format(
		ENV.DB_USER,
		ENV.DB_PASS,
		ENV.DB_HOST,
		ENV.DB_NAME
    ),
    pool_size=500,
    max_overflow=500,
    echo=False,
    pool_recycle=280
)


@contextmanager
def get_session():
    try:
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        Session = scoped_session(session_factory)

        session = Session()

        yield session
    except Exception as e:
        session.rollback()
        session.close()
        raise


DB_BASE = declarative_base()
