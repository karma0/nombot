import ccxt
import time

exchange = ccxt.poloniex()
exchange.load_markets()
delay_seconds = exchange.rateLimit / 1000

symbols = dict()

iteration = 0
while True:

    # https://github.com/ccxt-dev/ccxt/wiki/Manual#market-price
    for symbol in exchange.markets:

        start_time = time.clock()
        orderbook = exchange.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        market_price = {
            'bid': bid,
            'ask': ask,
            'spread': spread
        }
        print(exchange.id, symbol, 'market price:\n', market_price)

        if iteration > 0:
            difference = {
                'bid': bid - symbols[symbol]['bid'],
                'ask': ask - symbols[symbol]['ask'],
                'spread': spread - symbols[symbol]['spread']
            }
            print(difference)

        symbols[symbol] = market_price

        time.sleep(delay_seconds - (time.clock() - start_time))
    iteration += 1