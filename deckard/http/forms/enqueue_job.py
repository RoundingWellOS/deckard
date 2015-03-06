# -*- coding: utf-8 -*-
from deckard.db.models import Job

from flask import g
from wtforms import Form, IntegerField, TextField, validators


class EnqueueJobForm(Form):
    GIT_REF_TYPE_BRANCH = 'branch'
    GIT_REF_TYPE_TAG = 'tag'

    _is_deploy_job = False

    def __init__(self, *args, **kwargs):
        if 'deploy_job' in kwargs:
            self._is_deploy_job = kwargs.pop('deploy_job')
        super(EnqueueJobForm, self).__init__(*args, **kwargs)

    job_id = IntegerField(validators=[validators.Required()])
    user_id = IntegerField()

    git_fork = TextField()
    git_ref = TextField()
    git_ref_type = TextField()
    git_sha1 = TextField()

    def validate_user_id(form, field):
        field.data = g.user.id

    def validate_git_fork(form, field):
        if form._is_deploy_job and not field.data:
            raise ValueError(u'This field is required')
        if field.data:
            job = Job.query.get(form.job_id.data)
            if not job.include_forks and field.data != job.repo_full_name:
                raise ValueError(u'Only the upstream fork is allowed '
                                 'for this job')

    def validate_git_ref(form, field):
        if form._is_deploy_job:
            if field.data:
                git_ref_type, git_sha1, git_ref = field.data.split('|')
                field.data = git_ref
                form.git_ref_type.data = git_ref_type
                form.git_sha1.data = git_sha1
            else:
                raise ValueError(u'This field is required')

    def validate_git_ref_type(form, field):
        if form._is_deploy_job and not field.data:
            raise ValueError(u'This field is required')

    def validate_git_sha1(form, field):
        if form._is_deploy_job and not field.data:
            raise ValueError(u'This field is required')
