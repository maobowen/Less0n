// data posting
$("#course_tab .approve").click(function(){
    var index = $("#course_tab .approve").index(this);
    $.post("/url/",
    {
        request_id: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(1))").text(),
        course_id: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(2))").text(),
        course_name: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(3))").text(),
        department: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(4))").text(),
        subject: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(5))").text(),
        decision: true
    });
});

$("#course_tab .decline").click(function(){
    var index = $("#course_tab .decline").index(this);
    $.post("/url/",
    {
        request_id: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(1))").text(),
        course_id: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(2))").text(),
        course_name: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(3))").text(),
        department: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(4))").text(),
        subject: $("#course_tab tr:nth-child(" + (index + 1) + " td:nth-child(5))").text(),
        decision: false
    });
});

$("#professor_tab .approve").click(function(){
    var index = $("#professor_tab .approve").index(this);
    $.post("/url/",
    {
        request_id: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(1))").text(),
        name: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(2))").text(),
        uni: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(3))").text(),
        department: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(4))").text(),
        avatar: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(5))").text(),
        url: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(6))").text(),
        decision: true
    });
});

$("#professor_tab .decline").click(function(){
    var index = $("#professor_tab .decline").index(this);
    $.post("/url/",
    {
        request_id: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(1))").text(),
        name: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(2))").text(),
        uni: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(3))").text(),
        department: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(4))").text(),
        avatar: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(5))").text(),
        url: $("#professor_tab tr:nth-child(" + (index + 1) + " td:nth-child(6))").text(),
        decision: false
    });
});

// tab switching
function openCity(evt, tab) {
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


// set editable
var tabCourse = document.getElementById("tabCourse");
EditTables(tabCourse);

var tabProf = document.getElementById("tabProf");
EditTables(tabProf);