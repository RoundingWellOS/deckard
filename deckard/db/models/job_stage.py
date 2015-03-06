# -*- coding: utf-8 -*-
from deckard.db import Base, MutableList

from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import backref, relationship


class JobStage(Base):
    __tablename__ = 'job_stage'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    name = Column(UnicodeText, nullable=False)
    servers = Column(MutableList.as_mutable(ARRAY(UnicodeText)),
                     nullable=False)

    job = relationship('Job', backref=backref('_stages', uselist=True))
