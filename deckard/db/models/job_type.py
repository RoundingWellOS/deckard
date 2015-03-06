# -*- coding: utf-8 -*-
from deckard.db import Base

from sqlalchemy import Column, Integer, UnicodeText, UniqueConstraint


class JobType(Base):
    __tablename__ = 'job_type'
    __table_args__ = (
        UniqueConstraint('name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)

    def serialize(self):
        return dict(id=self.id, name=self.name,
                    jobs=[j.serialize() for j in self.jobs])
