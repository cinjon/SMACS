$('#buyOrder').click(function() {
    $('#orderType').html("Buy");
    adjustEnterQuantity();
});

$('#sellOrder').click(function() {
    $('#orderType').html("Sell");
    adjustEnterQuantity();
});

$('#btcCurrency').click(function() {
    $('#currency').html("BTC");
    adjustEnterQuantity();
});

$('#usdCurrency').click(function() {
    $('#currency').html("USD");
    adjustEnterQuantity();
});

function adjustEnterQuantity() {
    var currency = $('#currency').html();
    var orderType = $('#orderType').html();
    var instructions = $('#enterInstructions');
    instructions.html("Enter Quantity of " + currency + " to " + orderType);
}

function updateResults(value, commission, orderType, currency, quantity) {
    $('#results').html("To " + orderType + " " + quantity + " of " + currency + " , the exchange rate will be " + Number(value).toFixed(2) + " dollar per coin" + " after the commission of " + Number(commission).toFixed(2) + " dollars.");
}

$('#submit').click(function() {
    var orderType = $('#orderType').html();
    var currency = $('#currency').html();
    var quantity = $('#quantity').val();
    if(isNaN(quantity)) {
        $('#validNumberWarning').show();
        return;
    } else {
        $('#validNumberWarning').hide();
        $.getJSON($(this).attr("url"), {
            orderType:orderType,
            currency:currency,
            quantity:quantity
        }, function(data) {
            if (data.success) {
                updateResults(data.value, data.commission, orderType, currency, quantity);
            }
        });
    }
});

