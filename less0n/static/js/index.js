// Show and hide navigation bar

$('#welcome').show();
$('#main-page').hide();

$('#start-btn').click(function(){
    $('#main-page').show();
    $('#welcome').hide();
});
