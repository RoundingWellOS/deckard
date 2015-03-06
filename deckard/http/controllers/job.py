# -*- coding: utf-8 -*-
from deckard.db import db_session
from deckard.db.models import Job, QueuedJob
from deckard.http.app import app
from deckard.http.forms import EnqueueJobForm
from deckard.http.util.decorators import login_required

from flask import jsonify, render_template, g, request


@app.route('/job/enqueue')
@login_required
def job_enqueue():
    job_types = [dict(name=type_name, id=jobs[0]['type_id'])
                 for type_name, jobs in g.user.jobs.items()]
    return render_template(u'job_enqueue.html', job_types=job_types)


@app.route('/ajax/job/enqueue', methods=['POST'])
@login_required
def job_enqueue_post():
    form = EnqueueJobForm(request.form, deploy_job=True)
    if not form.validate():
        return jsonify(dict(data=form.errors, _status=False)), 400

    job = QueuedJob()
    form.populate_obj(job)
    db_session.add(job)
    db_session.commit()

    return jsonify(dict(data=True, _status=True))


@app.route('/job_queue')
@login_required
def job_queue():
    return render_template(u'job_queue.html')


@app.route('/ajax/queued_jobs')
@login_required
def ajax_queued_jobs():
    jobs = QueuedJob.query.order_by(QueuedJob.created_ts.desc()).limit(20)
    return jsonify(data=dict(jobs=[j.serialize() for j in jobs]), _status=True)


@app.route('/queued_job/<int:queued_job_id>/log')
@login_required
def job_queue_log(queued_job_id):
    job = QueuedJob.query.get(queued_job_id)
    return render_template(u'job_queue_log.html', log=list(job.log))


@app.route('/ajax/job/type/<int:type_id>/environments')
@login_required
def job_type_envs(type_id):
    jobs = Job.query.filter_by(type_id=type_id).join(
        Job.users, aliased=True).filter_by(id=g.user.id).order_by(
        Job.environment.asc()).all()
    environments = [dict(job_id=j.id, environment=j.environment) for j in jobs]
    return jsonify(data=environments)


@app.route('/ajax/job/<int:job_id>/forks')
@login_required
def job_forks(job_id):
    job = Job.query.get(job_id)

    if job.include_forks:
        repo = g.user.github_client.repository(job.repo_owner, job.repo_name)
        forks = [f.full_name for f in repo.iter_forks()]
        forks.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
        forks.insert(0, job.repo_full_name)
    else:
        forks = [job.repo_full_name]

    return jsonify(data=forks)


@app.route('/ajax/fork/<repo_owner>/<repo_name>/refs')
@login_required
def repo_refs(repo_owner, repo_name):
    repo = g.user.github_client.repository(repo_owner, repo_name)
    branches = [dict(name=b.name, sha=b.commit.sha)
                for b in repo.iter_branches()]
    tags = [dict(name=t.name, sha=t.commit['sha'])
            for t in repo.iter_tags()]
    return jsonify(data=dict(branches=branches, tags=tags))
