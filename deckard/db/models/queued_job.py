# -*- coding: utf-8 -*-
from deckard.db import Base, db_session, MutableList

from sqlalchemy import func, Column, DateTime, ForeignKey, Integer, UnicodeText
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship


class QueuedJob(Base):
    __tablename__ = 'queued_job'

    _working_directory = None

    PENDING = u'pending'
    PROCESSING = u'processing'
    COMPLETED = u'completed'
    FAILED = u'failed'

    id = Column(Integer, primary_key=True)

    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    status = Column(UnicodeText, server_default=PENDING, default=PENDING)

    created_ts = Column(DateTime(timezone=True),
                        server_default=func.now(), default=func.now())
    completed_ts = Column(DateTime(timezone=True))
    failed_ts = Column(DateTime(timezone=True))

    git_fork = Column(UnicodeText)
    git_ref = Column(UnicodeText)
    git_ref_type = Column(UnicodeText)
    git_sha1 = Column(UnicodeText)

    log = Column(MutableList.as_mutable(ARRAY(UnicodeText)),
                 server_default='{}', default=[])

    tasks = Column(JSON(none_as_null=True))
    stages = Column(JSON(none_as_null=True))

    job = relationship('Job')
    user = relationship('User')

    def serialize(self):
        return dict(id=self.id, job_id=self.job_id, user_id=self.user_id,
                    username=self.user.github_login,
                    status=self.status, created_ts=self.created_ts,
                    completed_ts=self.completed_ts, failed_ts=self.failed_ts,
                    finished_ts=self.completed_ts or self.failed_ts,
                    environment=self.job.environment, job_type=self.job.name,
                    git_fork=self.git_fork, git_ref=self.git_ref,
                    git_ref_type=self.git_ref_type, git_sha1=self.git_sha1)

    def mark_successful(self):
        self.status = self.COMPLETED
        self.completed_ts = func.now()
        db_session.commit()

    def mark_failed(self):
        self.status = self.FAILED
        self.failed_ts = func.now()
        db_session.commit()
