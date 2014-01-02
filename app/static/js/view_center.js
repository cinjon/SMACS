document.addEventListener('DOMContentLoaded', function() {
});

$('input.inputBoxAvailable').keyup(function (e) {
    if (e.keyCode == 13) {
        var value = $(this).val();
        if (checkInteger(value)) {
            console.log('value: ' + value);
            console.log($(this).parent().attr("id"));
            var id = $(this).parent().attr("id");
            $('#' + id.slice(0,15)).html('<strong>' + value + '</strong>')
        }
        return false;
    }
});

function checkInteger(val) {
    var intRegex = /^\d+$/;
    if(intRegex.test(val)) {
        return true;
    } else {
        return false;
    }
}

$('div.token_view').click(function() {
    var viewID = $(this).attr("id");
    var tokenID = viewID.slice(4);
    $(".show_token").hide();
    $("#show" + tokenID).show();
});

$('div.token_view').css('cursor','pointer');