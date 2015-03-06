# -*- coding: utf-8 -*-
from deckard.config import settings

from .mutable_list import MutableList

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(settings.DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


def drop_db():
    Base.metadata.drop_all(bind=engine)

__all__ = ['Base', 'db_session', 'drop_db', 'init_db', 'MutableList']

# Make DB
# create role deckard nosuperuser createdb createrole inherit login;
# create database deckard owner deckard encoding = 'UTF8' lc_ctype = 'en_US.UTF-8' lc_collate = 'en_US.UTF-8' template template0;
