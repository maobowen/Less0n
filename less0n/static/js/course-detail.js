$(document).ready(function() {

    var professor_list = [{
        "name": "All",
        "pic": "../static/img/cu.jpg",
        "rating": "40%",
        "grade": "90%",
        "workload": "20%",
        "tag": ["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10"],
    }, {
        "name": "Ewan Lowe",
        "pic": "../static/img/el.jpg",
        "rating": "50%",
        "grade": "70%",
        "workload": "80%",
        "tag": ["g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9", "g10"],
    }, {
        "name": "Big White",
        "pic": "../static/img/c-logo.jpg",
        "rating": "30%",
        "grade": "20%",
        "workload": "50%",
        "tag": ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10"],
    }];

    var cur = 0;

    $('#left i').click(function() {
        if (cur == -1) {
            cur = professor_list.length-1;
        }
        changeProf(cur);
        cur --;
    });

    $('#right i').click(function() {
        if (cur == professor_list.length) {
            cur = 0;
        }
        changeProf(cur);
        cur ++;
    });

    function changeProf(index) {
        $('#prof-pic').attr("src", professor_list[index]["pic"]);
        $('#faculty_choice h4').text(professor_list[index]["name"]);
        for (var i=1; i<11; i++) {
            $('#tag_list .tags a:nth-child('+i+')').text(professor_list[index]["tag"][i-1]);
        }
        $('#rating_progress_bar').css("width", professor_list[index]["rating"]);
        $('#grade_progress_bar').css("width", professor_list[index]["grade"]);
        $('#workload_progress_bar').css("width", professor_list[index]["workload"]);
    }
});