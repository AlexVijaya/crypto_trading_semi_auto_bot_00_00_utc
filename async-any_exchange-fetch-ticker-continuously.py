# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from get_info_from_load_markets import get_exchange_object3
import ccxt.async_support as ccxt  # noqa: E402
async def fetch_ticker_forever(symbol, exchange_object):
    # you can set enableRateLimit = True to enable the built-in rate limiter
    # this way you request rate will never hit the limit of an exchange
    # the library will throttle your requests to avoid that

    exchange = exchange_object
    while True:
        print('--------------------------------------------------------------')
        print(exchange.iso8601(exchange.milliseconds()), 'fetching', symbol, 'ticker from', exchange.name)
        # this can be any call instead of fetch_ticker, really
        try:
            ticker = await exchange.fetch_ticker(symbol)
            print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)
            print(ticker)
        except ccxt.RequestTimeout as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            # will retry
        except ccxt.DDoSProtection as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            # will retry
        except ccxt.ExchangeNotAvailable as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            # will retry
        except ccxt.ExchangeError as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            break  # won't retry

if __name__=="__main__":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(root + '/python')


    async def main2():

        exchange_objects = [get_exchange_object3('binance'),
                            get_exchange_object3('gateio'),
                            get_exchange_object3('bitfinex')]

        tasks = [
            asyncio.create_task(fetch_ticker_forever('BTC/USDT', exchange))
            for exchange in exchange_objects
        ]

        result = await asyncio.gather(*tasks)  # this will wait until all tasks are done
        print(result)  # this will print the results of all the tasks


    asyncio.run(main2())