import traceback

import ccxt  # noqa: E402
from api_config import api_dict_for_all_exchanges

def get_exchange_object_with_api_key(exchange_name,public_api_key,api_secret,trading_password):
    import ccxt  # noqa: E402
    exchange_objects = {
        # 'aax': ccxt.aax(),
        # 'aofex': ccxt.aofex(),
        'ace': ccxt.ace(),
        'alpaca': ccxt.alpaca(),
        'ascendex': ccxt.ascendex(),
        'bequant': ccxt.bequant(),
        # 'bibox': ccxt.bibox(),
        'bigone': ccxt.bigone(),
        'binance': ccxt.binance({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceus': ccxt.binanceus({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binancecoinm': ccxt.binancecoinm({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceusdm':ccxt.binanceusdm({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting

    }),
        'bit2c': ccxt.bit2c(),
        'bitbank': ccxt.bitbank(),
        'bitbay': ccxt.bitbay(),
        'bitbns': ccxt.bitbns(),
        'bitcoincom': ccxt.bitcoincom(),
        'bitfinex': ccxt.bitfinex({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt.bitfinex2({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitflyer': ccxt.bitflyer(),
        'bitforex': ccxt.bitforex({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 10000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitget': ccxt.bitget(),
        'bithumb': ccxt.bithumb(),
        # 'bitkk': ccxt.bitkk(),
        'bitmart': ccxt.bitmart({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 170,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        # 'bitmax': ccxt.bitmax(),
        'bitmex': ccxt.bitmex(),
        'bitpanda': ccxt.bitpanda(),
        'bitso': ccxt.bitso(),
        'bitstamp': ccxt.bitstamp(),
        'bitstamp1': ccxt.bitstamp1(),
        'bittrex': ccxt.bittrex(),
        'bitrue':ccxt.bitrue(),
        'bitvavo': ccxt.bitvavo(),
        # 'bitz': ccxt.bitz(),
        'bl3p': ccxt.bl3p(),
        # 'bleutrade': ccxt.bleutrade(),
        # 'braziliex': ccxt.braziliex(),
        'bkex': ccxt.bkex(),
        'btcalpha': ccxt.btcalpha(),
        'btcbox': ccxt.btcbox(),
        'btcmarkets': ccxt.btcmarkets(),
        # 'btctradeim': ccxt.btctradeim(),
        'btcturk': ccxt.btcturk(),
        'btctradeua':ccxt.btctradeua(),
        # 'buda': ccxt.buda(),
        'bybit': ccxt.bybit({
        'apiKey': public_api_key ,
        'secret': api_secret ,
        'rateLimit': 9,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        # 'bytetrade': ccxt.bytetrade(),
        # 'cdax': ccxt.cdax(),
        'cex': ccxt.cex(),
        # 'chilebit': ccxt.chilebit(),
        'coinbase': ccxt.coinbase(),
        'coinbaseprime': ccxt.coinbaseprime(),
        'coinbasepro': ccxt.coinbasepro(),
        'coincheck': ccxt.coincheck(),
        # 'coinegg': ccxt.coinegg(),
        'coinex': ccxt.coinex({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'coinfalcon': ccxt.coinfalcon(),
        'coinsph':ccxt.coinsph(),
        # 'coinfloor': ccxt.coinfloor(),
        # 'coingi': ccxt.coingi(),
        # 'coinmarketcap': ccxt.coinmarketcap(),
        'cryptocom': ccxt.cryptocom({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'coinmate': ccxt.coinmate(),
        'coinone': ccxt.coinone(),
        'coinspot': ccxt.coinspot(),
        # 'crex24': ccxt.crex24(),
        'currencycom': ccxt.currencycom({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'delta': ccxt.delta({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'deribit': ccxt.deribit({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'digifinex': ccxt.digifinex({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'dsx': ccxt.dsx(),
        # 'dx': ccxt.dx(),
        # 'eqonex': ccxt.eqonex(),
        # 'eterbase': ccxt.eterbase(),
        'exmo': ccxt.exmo({'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'exx': ccxt.exx(),
        # 'fcoin': ccxt.fcoin(),
        # 'fcoinjp': ccxt.fcoinjp(),
        # 'ftx': ccxt.ftx(),
        # 'flowbtc':ccxt.flowbtc(),
        'fmfwio': ccxt.fmfwio(),
        'gate':ccxt.gate({'apiKey': public_api_key ,
        'secret': api_secret }),
        'gateio': ccxt.gateio({'apiKey': public_api_key ,
        'secret': api_secret }),
        'gemini': ccxt.gemini(),
        # 'gopax': ccxt.gopax(),
        # 'hbtc': ccxt.hbtc(),
        'hitbtc': ccxt.hitbtc({'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'hitbtc2': ccxt.hitbtc2(),
        # 'hkbitex': ccxt.hkbitex(),
        'hitbtc3': ccxt.hitbtc3({'apiKey': public_api_key ,
        'secret': api_secret }),
        'hollaex': ccxt.hollaex(),
        'huobijp': ccxt.huobijp(),
        'huobipro': ccxt.huobipro({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'ice3x': ccxt.ice3x(),
        'idex': ccxt.idex(),
        # 'idex2': ccxt.idex2(),
        'indodax': ccxt.indodax(),
        'independentreserve': ccxt.independentreserve(),

        # 'itbit': ccxt.itbit(),
        'kraken': ccxt.kraken(),
        'krakenfutures': ccxt.krakenfutures(),
        'kucoin': ccxt.kucoin({
        'apiKey': public_api_key ,
        'secret': api_secret,
        'password': trading_password}),
        'kuna': ccxt.kuna(),
        # 'lakebtc': ccxt.lakebtc(),
        'latoken': ccxt.latoken({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'lbank': ccxt.lbank({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'liquid': ccxt.liquid(),
        'luno': ccxt.luno(),
        'lykke': ccxt.lykke(),
        'mercado': ccxt.mercado(),
        'mexc':ccxt.mexc({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'mexc3' : ccxt.mexc3({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        'okex': ccxt.okex({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'okex5':ccxt.okex5({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'okx':ccxt.okx({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'lbank2': ccxt.lbank2({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'blockchaincom': ccxt.blockchaincom(),
        'btcex': ccxt.btcex({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'kucoinfutures': ccxt.kucoinfutures({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'okex3': ccxt.okex3(),
        # 'p2pb2b': ccxt.p2pb2b(),
        # 'paribu': ccxt.paribu(),
        'phemex': ccxt.phemex(),
        'tokocrypto':ccxt.tokocrypto({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'poloniex': ccxt.poloniex({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        'probit': ccxt.probit({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'qtrade': ccxt.qtrade(),
        # 'ripio': ccxt.ripio(),
        # 'southxchange': ccxt.southxchange(),
        'stex': ccxt.stex(),
        # 'stronghold': ccxt.stronghold(),
        # 'surbitcoin': ccxt.surbitcoin(),
        # 'therock': ccxt.therock(),
        # 'tidebit': ccxt.tidebit(),
        'tidex': ccxt.tidex(),
        'timex': ccxt.timex(),
        'upbit': ccxt.upbit(),
        # 'vcc': ccxt.vcc(),
        'wavesexchange': ccxt.wavesexchange(),
        'woo':ccxt.woo(),
        'wazirx':ccxt.wazirx(),
        'whitebit': ccxt.whitebit({
        'apiKey': public_api_key ,
        'secret': api_secret }),
        # 'xbtce': ccxt.xbtce(),
        # 'xena': ccxt.xena(),
        'yobit': ccxt.yobit(),
        'zaif': ccxt.zaif(),
        # 'zb': ccxt.zb(),
        'zonda':ccxt.zonda()
    }
    exchange_object = exchange_objects.get(exchange_name)
    exchange_object.set_sandbox_mode(True)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    return exchange_object

def get_public_api_private_api_and_trading_password(exchange_id):
    public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    trading_password = None
    try:
        trading_password = api_dict_for_all_exchanges[exchange_id]['trading_password']
    except:
        traceback.print_exc()

    return public_api_key,api_secret,trading_password
def create_order(exchange_id,trading_pair,type,side,amount,price,params):

    public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    trading_password=None
    try:
        trading_password=api_dict_for_all_exchanges[exchange_id]['trading_password']
    except:
        traceback.print_exc()

    exchange_object=\
        get_exchange_object_with_api_key(exchange_name=exchange_id,
                                         public_api_key=public_api_key
                                         ,api_secret=api_secret,
                                         trading_password=trading_password)



    # print(f"public_api_key for {exchange_id}")
    # print(public_api_key)
    # print(f"api_secret for {exchange_id}")
    # print(api_secret)
    print(f"exchange_object_with_api_key for {exchange_id}")
    print(exchange_object)
    order=""
    if type=='market':
        if exchange_object.has['createMarketOrder']:
            order=exchange_object.create_order(trading_pair,type,side,amount,price,params)
            print(f"1market order has been placed on {exchange_id}")
        else:
            print(f"{exchange_id} does not have market order")
    else:
        order=exchange_object.create_order(trading_pair, type, side, amount, price,params)
        print(f"2limit order has been placed on {exchange_id}")

    return order

def create_market_buy_order(exchange_id,trading_pair,amount,price,params):
    type = 'market'
    side = 'buy'

    order=create_order(exchange_id, trading_pair, type, side, amount, price,params)
    return order

def create_market_sell_order(exchange_id,trading_pair,amount,price,params):
    type = 'market'
    side = 'sell'

    order=create_order(exchange_id, trading_pair, type, side, amount, price,params)
    return order
def create_limit_sell_order(exchange_id,trading_pair,amount,price,params):
    type = 'limit'
    side = 'sell'
    order=create_order(exchange_id, trading_pair, type, side, amount, price,params)
    return order
def create_limit_buy_order(exchange_id,trading_pair,amount,price,params):
    type = 'limit'
    side = 'buy'
    order=create_order(exchange_id, trading_pair, type, side, amount, price,params)
    return order

if __name__=="__main__":
    exchange_id='binance'
    trading_pair = 'BTC/USDT'
    params={}

    amount = 0.0005
    price = 25000
    create_limit_buy_order(exchange_id,trading_pair,amount,price,params)