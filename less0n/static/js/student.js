var color_pool = ['success', 'primary', 'info', 'danger', 'warning'];

function renderStatus(code) {
    if (code == 0 ) {
        return '<div class="btn btn-warning">Pending</div>';
    } else if (code == 1) {
        return '<div class="btn btn-success">Approved</div>';
    } else {
        return '<div class="btn btn-danger">Declined</div>';
    }
}

function renderTag(tags) {
    tags_html = '';
    for (var i = 0; i < tags.length; i++) {
        var color = i%5;
        tags_html += '<a class="bg-' + color_pool[color] + '">' + tags[i] + '</a>';
    }
    return tags_html;
}

// render ajax
function renderCourseRequest(all_course_request) {
    $('#cnum').text(all_course_request.length);
    $.each(all_course_request, function(i, request) {
        $('#tabCourse').append(
            '<tr data-request="course-request-' + request['id'] + '">' +
                '<td>' + (i + 1) + '</td>' +
                '<td>' + request['subject_id'] + '</td>' +
                '<td>' + request['course_number'] + '</td>' +
                '<td>' + request['course_name'] + '</td>' +
                '<td>' + request['department_id'] + '</td>' +
                '<td>' + request['term_id'] + '</td>' +
                '<td>' + renderStatus(request['approved']) + '</td>' +
            '</tr>'
        );
    });
}

function renderProfRequest(all_prof_request) {
    $('#pnum').text(all_prof_request.length);
    $.each(all_prof_request, function(i, request) {
        $('#tabProf').append(
            '<tr data-request="prof-request-' + request['id'] + '">' +
                '<td>' + (i + 1) + '</td>' +
                '<td>' + request['name'] + '</td>' +
                '<td>' + request['department_id'] + '</td>' +
                '<td>' + request['course_id'] + '</td>' +
                '<td>' + request['term_id'] + '</td>' +
                '<td>' + renderStatus(request['approved']) + '</td>' +
            '</tr>'
        );
    });
}

function renderComment(all_comment) {
    $.each(all_comment, function(i, current_comment) {
        var rating_html = '';
        var workload_html = '';
        for (var j = 0; j < current_comment['rating']; j++)
            rating_html += '<i class="fa fa-star"></i>';
        for (var j = 0; j < current_comment['workload']; j++)
            workload_html += '<i class="fa fa-pencil"></i>';

        $('.container.card-columns').append(
            '<div class="card">' +
                '<div class="card-body ' + rating_to_color(current_comment['rating']) + '">' +
                    '<button class="btn btn-danger delete"><i class="fa fa-trash"></i></button>' +
                    '<button class="btn btn-warning edit" data-toggle="modal" data-target="#commentModal"><i class="fa fa-edit"></i></button>' +
                    '<h5 class="card-title">' + current_comment['title'] + '</h5>' +
                    '<p class="card-text">' + current_comment['content'] + '</p>' +
                    '<a class="btn btn-light" data-toggle="collapse" href="#c' + i + '" role="button" aria-expanded="false" aria-controls="c' + i + '">Show Details <i class="fa fa-caret-down"></i></a>' +
                    '<div class="collapse" id="c' + i + '">' +
                        '<ul class="list-group">' +
                            '<li class="list-group-item">Course: ' + current_comment['subject_id'] + current_comment['course_number'] + '</li>' +
                            '<li class="list-group-item">Instructor: ' + current_comment['professor_name'] + '</li>' +
                            '<li class="list-group-item">Term: ' + current_comment['term_id'] + '</li>' +
                            '<li class="list-group-item">Rating: ' + rating_html + '</li>' +
                            '<li class="list-group-item">Workload: ' + workload_html + '</li>' +
                            '<li class="list-group-item">Grade: ' + current_comment['grade'] + '</li>' +
                            '<li class="list-group-item">Tags: ' + renderTag(current_comment['tags']) + '</li>' +
                        '</ul>' +
                    '</div>' +
                '</div>' +
            '</div>');

        $('.edit').on('click', function() {
            var index = $('.container.card-columns .card').index($(this).parent().parent());
            var cur_course = $('#c' + index + ' ul li:nth-child(1)').text().split(' ')[1];
            var cur_prof = $('#c' + index + ' ul li:nth-child(2)').text();

            $('.cmt_course').text(cur_course);
            $('#cmt_prof').text(cur_prof);
        });
    });
}

// tab switching
function switchTab(evt, tab) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tab).style.display = "block";
    evt.currentTarget.className += " active";
}

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

