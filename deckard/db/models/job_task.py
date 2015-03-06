# -*- coding: utf-8 -*-
from deckard.db import Base

from sqlalchemy import Column, ForeignKey, Integer, UnicodeText,\
    UniqueConstraint
from sqlalchemy.orm import backref, relationship


class JobTask(Base):
    __tablename__ = 'job_task'
    __table_args__ = (
        UniqueConstraint('job_id', 'sort_num'),
    )

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    module = Column(UnicodeText, nullable=False)
    sort_num = Column(Integer, nullable=False)

    job = relationship('Job', backref=backref('_tasks'))
