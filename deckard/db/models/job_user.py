# -*- coding: utf-8 -*-
from deckard.db import Base

from sqlalchemy import Column, ForeignKey, Integer


class JobUser(Base):
    __tablename__ = 'job_user'

    job_id = Column(Integer, ForeignKey('job.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
