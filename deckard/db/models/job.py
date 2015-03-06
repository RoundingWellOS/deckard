# -*- coding: utf-8 -*-
from deckard.db import Base

from sqlalchemy import Boolean, Column, ForeignKey, Integer, UnicodeText
from sqlalchemy.orm import backref, column_property, relationship


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('job_type.id'), nullable=False)
    repo_name = Column(UnicodeText)
    repo_owner = Column(UnicodeText)
    include_forks = Column(Boolean, server_default='false', default=False)
    environment = Column(UnicodeText, nullable=False)

    repo_full_name = column_property(repo_owner + u'/' + repo_name)

    type = relationship('JobType', backref=backref('jobs', uselist=True))

    @property
    def name(self):
        return self.type.name

    @property
    def stages(self):
        return {s.name: s.servers for s in self._stages}

    @property
    def tasks(self):
        tasks = [dict(sort_num=t.sort_num, module=t.module)
                 for t in self._tasks]
        tasks.sort(cmp=lambda x, y: cmp(x['sort_num'], y['sort_num']))
        return tasks

    def serialize(self):
        return dict(id=self.id, type_id=self.type_id, name=self.name,
                    environment=self.environment,
                    stages=self.stages)
