var cur_course = 0;
var cur_prof = 0;

// ajax
function renderCourseRequest(all_course_request) {
    cur_course = all_course_request.length;
    $('#cnum').text(cur_course);
    $.each(all_course_request, function(i, request) {
        $('#tabCourse').append(
            '<tr data-request="course-request-' + request['id'] + '">' +
                '<td>' + (i + 1) + '</td>' +
                '<td>' + request['subject_id'] + '</td>' +
                '<td>' + request['course_number'] + '</td>' +
                '<td>' + request['course_name'] + '</td>' +
                '<td>' + request['department_id'] + '</td>' +
                '<td>' + request['term_id'] + '</td>' +
                '<td><button class="btn btn-success approve"><i class="fa fa-check"></i></button><button class="btn btn-danger decline"><i class="fa fa-trash"></i></button></td>' +
            '</tr>'
        );
    });
}

function renderProfRequest(all_prof_request) {
    cur_prof = all_prof_request.length;
    $('#pnum').text(cur_prof);
    $.each(all_prof_request, function(i, request) {
        $('#tabProf').append(
            '<tr data-request="prof-request-' + request['id'] + '">' +
                '<td>' + (i + 1) + '</td>' +
                '<td>' + request['name'] + '</td>' +
                '<td></td>' +
                '<td>' + request['department_id'] + '</td>' +
                '<td>' + request['course_id'] + '</td>' +
                '<td>' + request['term_id'] + '</td>' +
                '<td></td>' +
                '<td></td>' +
                '<td><button class="btn btn-success approve"><i class="fa fa-check"></i></button><button class="btn btn-danger decline"><i class="fa fa-trash"></i></button></td>' +
            '</tr>'
        );
    });
}

// add entry
$(".add").click(function() {
    if ($(this).parent().parent().attr('id') == "course_tab") {
        cur_course++;
        $('#tabCourse').append(
            '<tr>' +
                '<td>' + cur_course + '</td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><button class="btn btn-success submit">Submit</button></td>' +
            '</tr>'
        );

        $("#tabCourse .submit").click(function() {
            var index = $('#tabCourse tr').index($(this).parent().parent());
            $.post("/url/",
            {
                subject: $("#tabCourse tr:nth-child(" + (index + 1) + ") td:nth-child(2) input").val(),
                course_num: $("#tabCourse tr:nth-child(" + (index + 1) + ") td:nth-child(3) input").val(),
                course_name: $("#tabCourse tr:nth-child(" + (index + 1) + ") td:nth-child(4) input").val(),
                department: $("#tabCourse tr:nth-child(" + (index + 1) + ") td:nth-child(5) input").val(),
                semester: $("#tabCourse tr:nth-child(" + (index + 1) + ") td:nth-child(6) input").val(),
                decision: true
            });
        });
    } else {
        cur_prof++;
        $('#tabProf').append(
            '<tr>' +
                '<td>' + cur_prof + '</td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><input type="text" value=""></td>' +
                '<td><button class="btn btn-success submit">Submit</button></td>' +
            '</tr>'
        );

        $("#tabProf .submit").click(function() {
            var index = $('#tabProf tr').index($(this).parent().parent());
            $.post("/url/",
            {
                name: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(2) input").val(),
                uni: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(3) input").val(),
                department: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(4) input").val(),
                course: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(5) input").val(),
                semester: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(6) input").val(),
                avatar: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(7) input").val(),
                url: $("#tabProf tr:nth-child(" + (index + 1) + ") td:nth-child(8) input").val(),
                decision: true
            });
        });
    }
});

// data posting
$("#tabCourse button").click(function() {
    var index = $(this).parent().parent().attr("data-request");
    var decision = true;
    if ($(this).hasClass('decline')) {
        decision = false;
    }
    $.post("/url/",
    {
        request_id: $("tr[data-request=" + index + "] td:nth-child(1)").text(),
        subject: $("tr[data-request=" + index + "] td:nth-child(2)").text(),
        course_num: $("tr[data-request=" + index + "] td:nth-child(3)").text(),
        course_name: $("tr[data-request=" + index + "] td:nth-child(4)").text(),
        department: $("tr[data-request=" + index + "] td:nth-child(5)").text(),
        semester: $("tr[data-request=" + index + "] td:nth-child(6)").text(),
        decision: decision
    });
});

$("#tabProf button").click(function(){
    var index = $(this).parent().parent().attr("data-request");
    var decision = true;
    if ($(this).hasClass('decline')) {
        decision = false;
    }
    $.post("/url/",
    {
        request_id: $("tr[data-request=" + index + "] td:nth-child(1)").text(),
        name: $("tr[data-request=" + index + "] td:nth-child(2)").text(),
        uni: $("tr[data-request=" + index + "] td:nth-child(3)").text(),
        department: $("tr[data-request=" + index + "] td:nth-child(4)").text(),
        course: $("tr[data-request=" + index + "] td:nth-child(5)").text(),
        semester: $("tr[data-request=" + index + "] td:nth-child(6)").text(),
        avatar: $("tr[data-request=" + index + "] td:nth-child(7)").text(),
        url: $("tr[data-request=" + index + "] td:nth-child(8)").text(),
        decision: decision
    });
});

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


// editable table
// set multiple table editable
function EditTables() {
    for (var i=0;i<arguments.length;i++){
        SetTableCanEdit(arguments[i]);
    }
}

// set editable tables
function SetTableCanEdit(table) {
    for (var i=1; i<table.rows.length;i++) {
        SetRowCanEdit(table.rows[i]);
    }
}

function SetRowCanEdit(row) {
    for (var j=0;j<row.cells.length; j++) {
        // see if the current tab is set to be editable
        var editType = row.cells[j].getAttribute("EditType");
        if (!editType) {
            // if not, see whether the row has
            editType = row.parentNode.rows[0].cells[j].getAttribute("EditType");
        }
        if (editType) {
            row.cells[j].onclick = function (){
                EditCell(this);
            }
        }
    }
}    

// set current editable
function EditCell(element, editType) {
    var editType = element.getAttribute("EditType");
    if (!editType) {
        // if not, see whether the row has
        editType = element.parentNode.parentNode.rows[0].cells[element.cellIndex].getAttribute("EditType");
    }
    switch(editType) {
        case "TextBox":
            CreateTextBox(element, element.innerHTML);
            break;
        case "DropDownList":
            CreateDropDownList(element);
            break;
        default:
            break;
    }
}    

// set editable input box
function CreateTextBox(element, value) {
    // check editable status, if so, skip
    var editState = element.getAttribute("EditState");
    if (editState != "true") {
        // create input
        var textBox = document.createElement("INPUT");
        textBox.type = "text";
        textBox.className="EditCell_TextBox";
        if (!value) {
            value = element.getAttribute("Value");
        }
        textBox.value = value;

        // set lost focus event
        textBox.onblur = function() {
            CancelEditCell(this.parentNode, this.value);
        }

        // add text
        ClearChild(element);
        element.appendChild(textBox);
        textBox.focus();
        textBox.select();

        // change status
        element.setAttribute("EditState", "true");
        element.parentNode.parentNode.setAttribute("CurrentRow", element.parentNode.rowIndex);
    }
}

// cancel editable status
function CancelEditCell(element, value, text) {
    element.setAttribute("Value", value);
    if (text) {
        element.innerHTML = text;
    } else {
        element.innerHTML = value;
    }
    element.setAttribute("EditState", "false");
}    
    
// clear child
function ClearChild(element) {
    element.innerHTML = "";
}    


