var color_pool = ['success', 'primary', 'info', 'danger', 'warning'];

for (var i = 0; i < $('.tags a').length; i++) {
    var color = i%5;
    $('.tags a:nth-child('+(i+1)+')').addClass(color_pool[i]);
}

var rating = parseFloat(""+$('#rating_num').text());
var grade = parseFloat(""+$('#grade_num').text());
var workload = parseFloat(""+$('#workload_num').text());

if ($('#rating_num').text() != 'N/A') {
    $('#rating_progress_bar').css('width', rating / 5 * 100 + '%');
    $('#rating_progress_bar').addClass(rating_to_color(rating));
} else {
    $('#rating_progress_bar').css('width', 0);
}

if ($('#grade_num').text() != 'N/A') {
    $('#grade_progress_bar').css('width', grade / 4.33 * 100 + '%');
    $('#grade_progress_bar').addClass(gpa_to_color(grade));
} else {
    $('#grade_progress_bar').css('width', 0);
}

if ($('#workload_num').text() != 'N/A') {
    $('#workload_progress_bar').css('width', workload / 5 * 100 + '%');
    $('#workload_progress_bar').addClass(workload_to_color(workload));
} else {
    $('#workload_progress_bar').css('width', 0);
}

$(".card").each(function(index) {
    var ratingdiv = $(".cardcol .col-md-6:nth-child("+(index+1)+") div:nth-child(5)");
    var gradediv = $(".cardcol .col-md-6:nth-child("+(index+1)+") div:nth-child(6)");
    var workloaddiv = $(".cardcol .col-md-6:nth-child("+(index+1)+") div:nth-child(7)");

    var rating_num = ratingdiv.text().split(" ")[1];
    var grade_num = gradediv.text().split(" ")[1];
    var workload_num = workloaddiv.text().split(" ")[1];

    var rating = parseFloat(rating_num);
    ratingdiv.addClass(rating_to_color(rating));

    var grade = parseFloat(grade_num);
    gradediv.addClass(gpa_to_color(grade));

    var workload = parseFloat(workload_num);
    workloaddiv.addClass(workload_to_color(workload));

    var border_div = $(".cardcol .col-md-6:nth-child("+(index+1)+") .card .card-body");
    border_div.addClass('border-'+rating_to_color(rating));
});
