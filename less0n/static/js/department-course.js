$(".card").each(function(index) {
    var ratingdiv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(4)");
    var gradediv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(5)");
    var workloaddiv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(6)");

    var rating = ratingdiv.attr("data-stat-value");
    var grade = gradediv.attr("data-stat-value");
    var workload = workloaddiv.attr("data-stat-value");

    ratingdiv.removeClass();
    ratingdiv.addClass('btn');
    ratingdiv.addClass(rating_to_color(rating));

    gradediv.removeClass();
    gradediv.addClass('btn');
    gradediv.addClass(gpa_to_color(grade));

    workloaddiv.removeClass();
    workloaddiv.addClass('btn');
    workloaddiv.addClass(workload_to_color(workload));
});