var professor_list = ["../static/img/cu.jpg", "../static/img/el.jpg", "../static/img/c-logo.jpg"];
var cur = 0;

$(document).ready(function() {
    $('#left i').click(function() {
        if (cur == -1) {
            cur = professor_list.length-1;
        }
        $('#prof-pic').attr("src", professor_list[cur]);
        cur --;
    });

    $('#right i').click(function() {
        if (cur == professor_list.length) {
            cur = 0;
        }
        $('#prof-pic').attr("src", professor_list[cur]);
        cur ++;
    });
});