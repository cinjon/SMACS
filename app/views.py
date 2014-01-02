import app
from flask import render_template, request, jsonify
# from flask.ext.login import logout_user, login_required, login_user

@app.flask_app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.flask_app.route('/order_book', methods=['GET'])
def order_book():
    book = app.order_book
    ty = request.args.get('orderType')
    currency = request.args.get('currency')
    quantity = float(request.args.get('quantity'))
    commission = app.models.get_commission(quantity)
    quantity -= commission

    if ty == 'Sell' and currency == 'BTC':
        value = app.models.usd_buy(quantity, book)
    elif ty == 'Sell' and currency == 'USD':
        value = app.models.btc_buy(quantity, book)
    elif ty == 'Buy' and currency == 'BTC':
        value = app.models.usd_sell(quantity, book)
    elif ty == 'Buy' and currency == 'USD':
        value = app.models.btc_sell(quantity, book)

    if currency == 'BTC':
        commission = value * commission

    return jsonify({'success':True, 'value':value, 'commission':commission})
