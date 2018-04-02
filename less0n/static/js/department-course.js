$(".card").each(function(index) {
    var ratingdiv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(4)");
    var gradediv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(5)");
    var workloaddiv = $(".row .col-md-6:nth-child("+(index+1)+") div:nth-child(6)");

    var rating = ratingdiv.attr("data-stat-value");
    var grade = gradediv.attr("data-stat-value");
    var workload = workloaddiv.attr("data-stat-value");

    ratingdiv.addClass(rating_to_color(rating));
    gradediv.addClass(gpa_to_color(grade));
    workloaddiv.addClass(workload_to_color(workload));

    var borderdiv = $(".row .col-md-6:nth-child("+(index+1)+") .card .card-body");
    borderdiv.addClass('border-'+rating_to_color(rating));
});
