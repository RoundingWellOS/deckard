requirejs.config({
    shim: {
        'lib/underscore-1.8.2.min': ['lib/jquery-2.1.3.min'],
        'lib/bootstrap.min': ['lib/jquery-2.1.3.min']
    }
});
require(["lib/jquery-2.1.3.min", "lib/underscore-1.8.2.min", "lib/bootstrap.min"], function() {
(function(job_enqueue, $, _) {
    "use strict";

    var JOB_TYPE = 'job-type',
        ENVIRONMENT = 'environment',
        FORK = 'git-fork',
        GIT_REF = 'git-ref',
        sections = [JOB_TYPE, ENVIRONMENT, FORK, GIT_REF],
        $panels = {},
        $selects = {},
        $submit_btn = $('#job-enqueue-submit-btn > button'),
        $job_enqueue_form = $('form#job-enqueue-form'),
        csrftoken = $('meta[name=csrf-token]').attr('content'),
        env_options_tmpl = _.template($('#env_options_tmpl').html()),
        fork_options_tmpl = _.template($('#git_fork_options_tmpl').html()),
        git_ref_options_tmpl = _.template($('#git_ref_options_tmpl').html());

    sections.forEach(function(section) {
        $panels[section] = $('#' + section + '-panel');
        $selects[section] = $panels[section].find('select');
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function _section_status(sections, good) {
        sections.forEach(function(section) {
            $panels[section].toggleClass('panel-danger', !good). toggleClass('panel-success', good);
        });
    }

    function _select_status(sections, on) {
        sections.forEach(function(section) {
            $selects[section].attr('disabled', !on);
        });
    }

    function _submit_status(on) {
        $submit_btn.toggleClass('disabled', !on);
    }

    function select_reset() {
        var sections = Array.prototype.slice.call(arguments);
        select_disable.apply(null, sections);
        sections.forEach(function(section) {
            $selects[section].val('');;
        });
    }

    function section_bad() {
        _section_status(Array.prototype.slice.call(arguments), false);
        submit_disable();
    }

    function section_good() {
        _section_status(Array.prototype.slice.call(arguments), true);
    }

    function select_enable() {
        _select_status(Array.prototype.slice.call(arguments), true);
    }

    function select_disable() {
        _select_status(Array.prototype.slice.call(arguments), false);
    }

    function submit_enable() {
        _submit_status(true);
    }

    function submit_disable() {
        _submit_status(false);
    }

    $selects[JOB_TYPE].change(function(e) {
        var type_id = e.currentTarget.value;

        section_bad(JOB_TYPE, ENVIRONMENT, FORK, GIT_REF);
        select_disable(ENVIRONMENT, FORK, GIT_REF);
        select_reset(ENVIRONMENT, FORK, GIT_REF);

        if (!_.isEmpty(type_id)) {
            section_good(JOB_TYPE);
            $.getJSON('/ajax/job/type/' + type_id + '/environments', function(res) {
                $selects[ENVIRONMENT].html(env_options_tmpl({options: res.data}));
                select_enable(ENVIRONMENT);
            });
        }

    });

    $selects[ENVIRONMENT].change(function(e) {
        var job_id = e.currentTarget.value;

        section_bad(ENVIRONMENT, FORK, GIT_REF);
        select_disable(FORK, GIT_REF);
        select_reset(FORK, GIT_REF);

        if (!_.isEmpty(job_id)) {
            section_good(ENVIRONMENT);
            $.getJSON('/ajax/job/' + job_id + '/forks', function(res) {
                $selects[FORK].html(fork_options_tmpl({forks: res.data}));
                select_enable(FORK);
            });
        }

    });

    $selects[FORK].change(function(e) {
        var fork = e.currentTarget.value;

        section_bad(FORK, GIT_REF);
        select_disable(GIT_REF);
        select_reset(GIT_REF);

        if (!_.isEmpty(fork)) {
            section_good(FORK);
            $.getJSON('/ajax/fork/' + fork + '/refs', function(res) {
                $selects[GIT_REF].html(git_ref_options_tmpl({branches: res.data.branches, tags: res.data.tags}));
                select_enable(GIT_REF);
            });
        }

    });

    $selects[GIT_REF].change(function(e) {
        var git_ref = e.currentTarget.value;

        section_bad(GIT_REF);

        if (!_.isEmpty(git_ref)) {
            section_good(GIT_REF);
            submit_enable();
        }

    });

    $job_enqueue_form.submit(function(e) {
        e.preventDefault();
        var xhr = $.post('/ajax/job/enqueue', $job_enqueue_form.serialize());

        xhr.done(function(data) {
            location.href = '/job_queue';
        });

        xhr.fail(function(xhr) {
            var errors, msg;
            if (xhr.status === 400) {
                errors = xhr.responseJSON.data;
                msg = _.reduce(_.keys(errors), function(memo, field){
                    return memo + field + ": " + errors[field].join(', ') + '\n';
                }, '');
                alert(msg);
            }
            else {
                alert(xhr.responseJSON.data);
            }
        });
        
    });

    $(function() {
        $selects[JOB_TYPE].change();
    });

})( window.job_enqueue = window.job_enqueue || {}, jQuery, _);
});