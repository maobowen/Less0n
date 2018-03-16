//navbarshow&hide

    $('#sort-alphabetical').show();
    $('#alphabetical-card').show();
    $('#sort-school').hide();
    $('#school-card').hide();   



$('#sort').click(function(){
    $('#sort-alphabetical').show();
    $('#alphabetical-card').show();
    $('#sort-school').hide();
    $('#school-card').hide();
});


$('#school').click(function(){
    $('#sort-alphabetical').hide();
    $('#alphabetical-card').hide();
    $('#sort-school').show();
    $('#school-card').show();
});