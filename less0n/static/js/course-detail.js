var cur = 0;
var all_profs = null;
var color_pool = ['success', 'primary', 'info', 'danger', 'warning'];

function changeProf(index, all_profs) {
    var current_prof = all_profs[index];
    $('#prof-pic').attr('src', current_prof['avatar']);
    $('#faculty_choice h4').text(current_prof['name']);

    $('#tag_list .tags').empty();
    for (var i = 0; i < current_prof['tags'].length; i++) {
        var color = i%5;
        $('#tag_list .tags').append('<a class="' + color_pool[color] + '">' + current_prof['tags'][i] + '</a>');
    }

    $('#rating_progress_bar').css('width', current_prof['rating'] / 5 * 100 + '%');
    $('#rating_progress_bar').removeClass();
    $('#rating_progress_bar').addClass('progress_bar');
    $('#rating_progress_bar').addClass(rating_to_color(current_prof['rating']));
    $('#rating_numerical').text(current_prof['rating']);
    $('#grade_progress_bar').css('width', current_prof['grade'] / 4.33 * 100 + '%');
    $('#grade_progress_bar').removeClass();
    $('#grade_progress_bar').addClass('progress_bar');
    $('#grade_progress_bar').addClass(gpa_to_color(current_prof['grade']))
    $('#grade_numerical').text(current_prof['grade']);
    $('#workload_progress_bar').css('width', current_prof['workload'] / 5 * 100 + '%');
    $('#workload_progress_bar').removeClass();
    $('#workload_progress_bar').addClass('progress_bar');
    $('#workload_progress_bar').addClass(workload_to_color(current_prof['workload']));
    $('#workload_numerical').text(current_prof['workload']);

    // Load comments
    $('.container.card-columns').empty();
    for (var i = 0; i < current_prof['comments'].length; i++) {
        var current_comment = current_prof['comments'][i];

        var rating_html = '';
        var workload_html = '';
        for (var j = 0; j < current_comment['rating']; j++)
            rating_html += '<i class="fa fa-star"></i>';
        for (var j = 0; j < current_comment['workload']; j++)
            workload_html += '<i class="fa fa-pencil"></i>';

        $('.container.card-columns').append(
            '<div class="card">' +
                '<div class="card-body ' + rating_to_color(current_comment['rating']) + '">' +
                    '<h5 class="card-title">' + current_comment['title'] + '</h5>' +
                    '<p class="card-text">' + current_comment['content'] + '</p>' +
                    '<a class="btn btn-light" data-toggle="collapse" href="#c' + i + '" role="button" aria-expanded="false" aria-controls="c' + i + '">Show Details <i class="fa fa-caret-down"></i></a>' +
                    '<div class="collapse" id="c' + i + '">' +
                        '<ul class="list-group">' +
                            '<li class="list-group-item">Term: ' + current_comment['term'] + '</li>' +
                            '<li class="list-group-item">Instructor: ' + current_prof['name'] + '</li>' +
                            '<li class="list-group-item">Rating: ' + rating_html + '</li>' +
                            '<li class="list-group-item">Workload: ' + workload_html + '</li>' +
                            '<li class="list-group-item">Grade: '  + current_comment['grade'] +  '</li>' +
                            '<li class="list-group-item">'  + current_comment['timestamp'] +  '</li>' +
                        '</ul>' +
                    '</div>' +
                '</div>' +
            '</div>');
    }
}

$('#left i').click(function() {
    cur--;
    if (cur < 0)
        cur = all_profs.length - 1;
    changeProf(cur, all_profs);
});

$('#right i').click(function() {
    cur++;
    if (cur >= all_profs.length)
        cur = 0;
    changeProf(cur, all_profs);
});
