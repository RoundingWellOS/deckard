requirejs.config({
    shim: {
        'lib/underscore-1.8.2.min': ['lib/jquery-2.1.3.min'],
        'lib/bootstrap.min': ['lib/jquery-2.1.3.min'],
        'lib/bootstrap-table.min': ['lib/bootstrap.min']
    },
    paths: {
        "moment": "lib/moment"
    }
});
define(["lib/moment-timezone-with-data-2010-2020"], function (moment) {
require(["lib/jquery-2.1.3.min", "lib/underscore-1.8.2.min", "lib/bootstrap.min", "lib/bootstrap-table.min"], function() {
!(function(job_queue, $, _) {
    "use strict";

    var $jobs_table = $('table#jobs-table'),
        $jobs_table_refresh_btn = $('button#btn-jobs-table-refresh'),
        log_url_tmpl = _.template($('#log_url_tmpl').html().replace('99999', '<%= id %>')),
        git_ref_tmpl = _.template($('#git_ref_tmpl').html()),
        timestamp_tmpl = _.template($('#timestamp_tmpl').html());

    job_queue.log_url_formatter = function(value) {
        if (!value) {
            return value;
        }
        return log_url_tmpl({id: value});
    };

    job_queue.git_ref_formatter = function(value, row) {
        if (!value) {
            return value;
        }
        return git_ref_tmpl({row: row});
    };

    job_queue.timestamp_formatter = function(value) {
        if (!value) {
            return value;
        }
        var m = moment(value),
            datestamp = m.format('MMMM DD, YYYY').replace(/\ /g, '&nbsp;'),
            timestamp = m.format('h:mm A').replace(/\ /g, '&nbsp;');
        return timestamp_tmpl({datestamp: datestamp, timestamp: timestamp});
    };

    $jobs_table.bootstrapTable({
        formatLoadingMessage: function() {return "<span class=\"glyphicon glyphicon-refresh glyphicon-spin\"></span>"},
        url: "/ajax/queued_jobs",
        responseHandler: function(res) {
            return res.data.jobs;
        },
        rowStyle: function(row, index) {
            var className;
            if (row.status === "failed") {
                className = "danger";
            }
            else if (row.status === "pending") {
                className = "warning";
            }
            else if (row.status === "processing") {
                className = "success";
            }
            return {
                classes: className
            }
        },
        striped: true
    });

    $jobs_table_refresh_btn.on('click', function(e) {
        e.preventDefault();
        $jobs_table.bootstrapTable('refresh');
    });

    $(document).on('hidden.bs.modal', function (e) {
        $(e.target).removeData('bs.modal');
    });

})( window.job_queue = window.job_queue || {}, jQuery, _);
})
});