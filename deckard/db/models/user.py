# -*- coding: utf-8 -*-
from deckard.db import Base

import github3

import itertools

from sqlalchemy import Column, ForeignKey, Index, Integer, Table, UnicodeText
from sqlalchemy.orm import backref, relationship


job_user = Table(
    'job_user',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('job.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    extend_existing=True
)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('user_github_login_idx', 'github_login', unique=True),
    )

    _github_client = None

    id = Column(Integer, primary_key=True)
    github_login = Column(UnicodeText, nullable=False)
    github_name = Column(UnicodeText)
    github_access_token = Column(UnicodeText, nullable=False, default=u'')
    github_avatar = Column(UnicodeText)

    _jobs = relationship('Job', secondary=job_user, uselist=True,
                         backref=backref('users', uselist=True))

    @property
    def github_client(self):
        if not self._github_client:
            self._github_client = github3.GitHub(
                self.github_login, token=self.github_access_token)
        return self._github_client

    @property
    def jobs(self):
        return {k: [g for g in group]
                for k, group in itertools.groupby(
                    [j.serialize() for j in self._jobs], lambda j: j['name'])}

    def serialize(self):
        return dict(id=self.id, github_login=self.github_login,
                    github_name=self.github_name,
                    github_avatar=self.github_avatar, jobs=self.jobs)
