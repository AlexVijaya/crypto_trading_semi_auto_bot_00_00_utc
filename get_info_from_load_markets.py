from datetime import datetime

import pprint
import ccxt
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import time
import traceback
import re
import numpy as np
# from fetch_historical_USDT_pairs_for_1D_delete_first_primary_db_and_delete_low_volume_db import remove_values_from_list



from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
import streamlit as st
import plotly.graph_objects as go
# from huobi_client.generic import GenericClient
# from test_streamlit_app import plot_ohlcv

async def plot_ohlcv(entire_ohlcv_df):
    # entire_ohlcv_df["Timestamp"] = (entire_ohlcv_df.index)

    try:
        entire_ohlcv_df["open_time"] = entire_ohlcv_df["Timestamp"].apply(
            lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print("error_message")
        traceback.print_exc()

    entire_ohlcv_df['Timestamp'] = entire_ohlcv_df["Timestamp"] / 1000.0


    fig = go.Figure(go.Ohlc(x=entire_ohlcv_df["open_time"], open=entire_ohlcv_df['open'], high=entire_ohlcv_df['high'],
        low=entire_ohlcv_df['low'], close=entire_ohlcv_df['close'], increasing_line_color= 'green',
        decreasing_line_color='red'))
    st.plotly_chart(fig)

import ccxt.async_support as ccxt_async
async def async_fetch_entire_ohlcv_without_exchange_name(exchange_object,trading_pair, timeframe,limit_of_daily_candles):
    try:


        # limit_of_daily_candles = 200
        data = []
        header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
        data_df1 = pd.DataFrame(columns=header)
        data_df=pd.DataFrame()
        exchange_id=""

        # Fetch the most recent 100 days of data
        try:
            #exchange latoken has a specific limit of one request number of candles
            if isinstance(exchange_object, ccxt_async.latoken):
                print("exchange is latoken")
                limit_of_daily_candles = 100
        except:
            traceback.print_exc()

        # Fetch the most recent 200 days of data
        try:
            # exchange bybit has a specific limit of one request number of candles
            if isinstance(exchange_object, ccxt_async.bybit):
                print("exchange is bybit")
                limit_of_daily_candles = 200
        except:
            traceback.print_exc()

        # streamlit.write("exchange_object",exchange_object)
        # streamlit.write(type(exchange_object))
        # print("trading_pair1")
        # print(trading_pair)
        data += await exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
        first_timestamp_in_df=0
        first_timestamp_in_df_for_gateio=0

        # Fetch previous n days of data consecutively
        for i in range(1, 100):

            print("i=", i)
            print("data[0][0] - i * 86400000 * limit_of_daily_candles")
            # print(data[0][0] - i * 86400000 * limit_of_daily_candles)
            try:
                previous_data = await exchange_object.fetch_ohlcv(trading_pair,
                                                     timeframe,
                                                     limit=limit_of_daily_candles,
                                                     since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
                data = previous_data + data
            finally:

                data_df1 = pd.DataFrame(data, columns=header)
                if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df:
                    break
                first_timestamp_in_df = data_df1.iloc[0]['Timestamp']

        header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
        data_df = pd.DataFrame(data, columns=header)

        data_df.drop_duplicates(subset=["Timestamp"],keep="first",inplace=True)
        data_df.sort_values("Timestamp",inplace=True)

        try:
            data_df["open_time"] = data_df["Timestamp"].apply(
                lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print("error_message")
            traceback.print_exc()

        data_df['Timestamp'] = data_df["Timestamp"] / 1000.0

        data_df = data_df.set_index('Timestamp')
        try:
            exchange_id=exchange_object.id
            data_df["exchange"]=exchange_id
        except:
            traceback.print_exc()

        try:
            data_df["trading_pair"]=trading_pair
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by low
            data_df["volume*low"]=data_df["volume"]*data_df["low"]
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by close
            data_df["volume*close"]=data_df["volume"]*data_df["close"]
        except:
            traceback.print_exc()

        print(f"data_df on {exchange_id}")
        print(data_df)
        return data_df
    except:
        traceback.print_exc()
        data_df=pd.DataFrame()
        return data_df
    finally:
        await exchange_object.close()


async def async_fetch_entire_ohlcv_without_exchange_name_with_load_markets(exchange_object, trading_pair, timeframe,
                                                         limit_of_daily_candles):
    try:


        # limit_of_daily_candles = 200
        data = []
        header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
        data_df1 = pd.DataFrame(columns=header)
        data_df=pd.DataFrame()
        exchange_id = ""
        print("exchange_object")
        print(exchange_object)
        await exchange_object.load_markets()

        # Fetch the most recent 100 days of data
        try:
            # exchange latoken has a specific limit of one request number of candles
            if isinstance(exchange_object, ccxt_async.latoken):
                print("exchange is latoken")
                limit_of_daily_candles = 100
        except:
            traceback.print_exc()

        # Fetch the most recent 200 days of data
        try:
            # exchange bybit has a specific limit of one request number of candles
            if isinstance(exchange_object, ccxt_async.bybit):
                print("exchange is bybit")
                limit_of_daily_candles = 200
        except:
            traceback.print_exc()

        # streamlit.write("exchange_object",exchange_object)
        # streamlit.write(type(exchange_object))
        # print("trading_pair1")
        # print(trading_pair)
        data += await exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
        first_timestamp_in_df = 0
        first_timestamp_in_df_for_gateio = 0

        # Fetch previous n days of data consecutively
        for i in range(1, 100):

            print("i=", i)
            print("data[0][0] - i * 86400000 * limit_of_daily_candles")
            # print(data[0][0] - i * 86400000 * limit_of_daily_candles)
            try:
                previous_data = await exchange_object.fetch_ohlcv(trading_pair,
                                                                  timeframe,
                                                                  limit=limit_of_daily_candles,
                                                                  since=data[-1][
                                                                            0] - i * 86400000 * limit_of_daily_candles)
                data = previous_data + data
            finally:

                data_df1 = pd.DataFrame(data, columns=header)
                if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df:
                    break
                first_timestamp_in_df = data_df1.iloc[0]['Timestamp']

        header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
        data_df = pd.DataFrame(data, columns=header)

        data_df.drop_duplicates(subset=["Timestamp"], keep="first", inplace=True)
        data_df.sort_values("Timestamp", inplace=True)

        try:
            data_df["open_time"] = data_df["Timestamp"].apply(
                lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print("error_message")
            traceback.print_exc()

        data_df['Timestamp'] = data_df["Timestamp"] / 1000.0

        data_df = data_df.set_index('Timestamp')
        try:
            exchange_id = exchange_object.id
            data_df["exchange"] = exchange_id
        except:
            traceback.print_exc()

        try:
            data_df["trading_pair"] = trading_pair
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by low
            data_df["volume*low"] = data_df["volume"] * data_df["low"]
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by close
            data_df["volume*close"] = data_df["volume"] * data_df["close"]
        except:
            traceback.print_exc()

        print(f"data_df on {exchange_id}")
        print(data_df)
        return data_df
    except:
        traceback.print_exc()
        data_df = pd.DataFrame()
        return data_df
    finally:
        await exchange_object.close()


def get_exchange_object3(exchange_name):
    import ccxt.async_support as ccxt  # noqa: E402
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
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceus': ccxt.binanceus({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binancecoinm': ccxt.binancecoinm({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceusdm':ccxt.binanceusdm({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bit2c': ccxt.bit2c(),
        'bitbank': ccxt.bitbank(),
        'bitbay': ccxt.bitbay(),
        'bitbns': ccxt.bitbns(),
        'bitcoincom': ccxt.bitcoincom(),
        'bitfinex': ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitflyer': ccxt.bitflyer(),
        'bitforex': ccxt.bitforex({
        'rateLimit': 300,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitget': ccxt.bitget(),
        'bithumb': ccxt.bithumb(),
        # 'bitkk': ccxt.bitkk(),
        'bitmart': ccxt.bitmart({
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
        # 'bkex': ccxt.bkex(),
        'btcalpha': ccxt.btcalpha(),
        'btcbox': ccxt.btcbox(),
        'btcmarkets': ccxt.btcmarkets(),
        # 'btctradeim': ccxt.btctradeim(),
        'btcturk': ccxt.btcturk(),
        # 'btctradeua':ccxt.btctradeua(),
        # 'buda': ccxt.buda(),
        'bybit': ccxt.bybit({
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
        'coinex': ccxt.coinex(),
        # 'coinfalcon': ccxt.coinfalcon(),
        'coinsph':ccxt.coinsph(),
        # 'coinfloor': ccxt.coinfloor(),
        # 'coingi': ccxt.coingi(),
        # 'coinmarketcap': ccxt.coinmarketcap(),
        'cryptocom': ccxt.cryptocom(),
        'coinmate': ccxt.coinmate(),
        'coinone': ccxt.coinone(),
        'coinspot': ccxt.coinspot(),
        # 'crex24': ccxt.crex24(),
        'currencycom': ccxt.currencycom(),
        'delta': ccxt.delta(),
        'deribit': ccxt.deribit(),
        'digifinex': ccxt.digifinex(),
        # 'dsx': ccxt.dsx(),
        # 'dx': ccxt.dx(),
        # 'eqonex': ccxt.eqonex(),
        # 'eterbase': ccxt.eterbase(),
        'exmo': ccxt.exmo(),
        # 'exx': ccxt.exx(),
        # 'fcoin': ccxt.fcoin(),
        # 'fcoinjp': ccxt.fcoinjp(),
        # 'ftx': ccxt.ftx(),
        # 'flowbtc':ccxt.flowbtc(),
        'fmfwio': ccxt.fmfwio(),
        'gate':ccxt.gate(),
        'gateio': ccxt.gateio(),
        'gemini': ccxt.gemini(),
        # 'gopax': ccxt.gopax(),
        # 'hbtc': ccxt.hbtc(),
        'hitbtc': ccxt.hitbtc(),
        # 'hitbtc2': ccxt.hitbtc2(),
        # 'hkbitex': ccxt.hkbitex(),
        'hitbtc3': ccxt.hitbtc3(),
        'hollaex': ccxt.hollaex(),
        'huobijp': ccxt.huobijp(),
        'huobipro': ccxt.huobipro(),
        # 'ice3x': ccxt.ice3x(),
        'idex': ccxt.idex(),
        # 'idex2': ccxt.idex2(),
        'indodax': ccxt.indodax(),
        'independentreserve': ccxt.independentreserve(),

        # 'itbit': ccxt.itbit(),
        'kraken': ccxt.kraken(),
        'krakenfutures': ccxt.krakenfutures(),
        'kucoin': ccxt.kucoin(),
        'kuna': ccxt.kuna(),
        # 'lakebtc': ccxt.lakebtc(),
        'latoken': ccxt.latoken(),
        'lbank': ccxt.lbank(),
        # 'liquid': ccxt.liquid(),
        'luno': ccxt.luno(),
        'lykke': ccxt.lykke(),
        'mercado': ccxt.mercado(),
        'mexc':ccxt.mexc(),
        'mexc3' : ccxt.mexc3(),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        'okex': ccxt.okex(),
        'okex5':ccxt.okex5(),
        'okx':ccxt.okx(),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi(),
        'lbank2': ccxt.lbank2(),
        'blockchaincom': ccxt.blockchaincom(),
        # 'btcex': ccxt.btcex(),
        'kucoinfutures': ccxt.kucoinfutures(),
        # 'okex3': ccxt.okex3(),
        # 'p2pb2b': ccxt.p2pb2b(),
        # 'paribu': ccxt.paribu(),
        'phemex': ccxt.phemex(),
        'tokocrypto':ccxt.tokocrypto(),
        'poloniex': ccxt.poloniex(),
        'probit': ccxt.probit(),
        # 'qtrade': ccxt.qtrade(),
        # 'ripio': ccxt.ripio(),
        # 'southxchange': ccxt.southxchange(),
        # 'stex': ccxt.stex(),
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
        'wazirx':ccxt.wazirx({
        'rateLimit': 300,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'whitebit': ccxt.whitebit(),
        # 'xbtce': ccxt.xbtce(),
        # 'xt': ccxt.xt(),
        'yobit': ccxt.yobit(),
        'zaif': ccxt.zaif(),
        # 'zb': ccxt.zb(),
        'zonda':ccxt.zonda(),
        'bingx': ccxt.bingx()
    }
    exchange_object = exchange_objects.get(exchange_name)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    return exchange_object
def get_exchange_object6(exchange_name):
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
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceus': ccxt.binanceus({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binancecoinm': ccxt.binancecoinm({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'binanceusdm':ccxt.binanceusdm({
        'rateLimit': 50,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
        # 'options': {
        #     'defaultType': 'future',
        #     'adjustForTimeDifference': True
        #     # 'sandbox': True  # set_sandbox_mode is True
        # }
    }),
        'bit2c': ccxt.bit2c(),
        'bitbank': ccxt.bitbank(),
        'bitbay': ccxt.bitbay(),
        'bitbns': ccxt.bitbns(),
        'bitcoincom': ccxt.bitcoincom(),
        'bitfinex': ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitflyer': ccxt.bitflyer(),
        'bitforex': ccxt.bitforex({
        'rateLimit': 10000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitget': ccxt.bitget(),
        'bithumb': ccxt.bithumb(),
        # 'bitkk': ccxt.bitkk(),
        'bitmart': ccxt.bitmart({
        'rateLimit': 170,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        # 'bitmax': ccxt.bitmax(),
        'bitmex': ccxt.bitmex(),
        'bitpanda': ccxt.bitpanda(),
        'bitso': ccxt.bitso(),
        'bitstamp': ccxt.bitstamp(),
        # 'bitstamp1': ccxt.bitstamp1(),
        # 'bittrex': ccxt.bittrex(),
        'bitrue':ccxt.bitrue(),
        'bitvavo': ccxt.bitvavo(),
        # 'bitz': ccxt.bitz(),
        'bl3p': ccxt.bl3p(),
        # 'bleutrade': ccxt.bleutrade(),
        # 'braziliex': ccxt.braziliex(),
        #  'btcex': ccxt.btcex(),
        # 'bkex': ccxt.bkex(),
        'btcalpha': ccxt.btcalpha(),
        'btcbox': ccxt.btcbox(),
        'btcmarkets': ccxt.btcmarkets(),
        # 'btctradeim': ccxt.btctradeim(),
        'btcturk': ccxt.btcturk(),
        # 'btctradeua':ccxt.btctradeua(),
        # 'buda': ccxt.buda(),
        'bybit': ccxt.bybit({
        'rateLimit': 9,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        # 'bytetrade': ccxt.bytetrade(),
        # 'cdax': ccxt.cdax(),
        'cex': ccxt.cex(),
        # 'chilebit': ccxt.chilebit(),
        'coinbase': ccxt.coinbase(),
        # 'coinbaseprime': ccxt.coinbaseprime(),
        'coinbasepro': ccxt.coinbasepro(),
        'coincheck': ccxt.coincheck(),
        # 'coinegg': ccxt.coinegg(),
        'coinex': ccxt.coinex(),
        # 'coinfalcon': ccxt.coinfalcon(),
        'coinsph':ccxt.coinsph(),
        # 'coinfloor': ccxt.coinfloor(),
        # 'coingi': ccxt.coingi(),
        # 'coinmarketcap': ccxt.coinmarketcap(),
        'cryptocom': ccxt.cryptocom(),
        'coinmate': ccxt.coinmate(),
        'coinone': ccxt.coinone(),
        'coinspot': ccxt.coinspot(),
        # 'crex24': ccxt.crex24(),
        'currencycom': ccxt.currencycom(),
        'delta': ccxt.delta(),
        'deribit': ccxt.deribit(),
        'digifinex': ccxt.digifinex(),
        # 'dsx': ccxt.dsx(),
        # 'dx': ccxt.dx(),
        # 'eqonex': ccxt.eqonex(),
        # 'eterbase': ccxt.eterbase(),
        'exmo': ccxt.exmo(),
        # 'exx': ccxt.exx(),
        # 'fcoin': ccxt.fcoin(),
        # 'fcoinjp': ccxt.fcoinjp(),
        # 'ftx': ccxt.ftx(),
        # 'flowbtc':ccxt.flowbtc(),
        'fmfwio': ccxt.fmfwio(),
        'gate':ccxt.gate(),
        'gateio': ccxt.gateio(),
        'gemini': ccxt.gemini(),
        # 'gopax': ccxt.gopax(),
        # 'hbtc': ccxt.hbtc(),
        'hitbtc': ccxt.hitbtc(),
        # 'hitbtc2': ccxt.hitbtc2(),
        # 'hkbitex': ccxt.hkbitex(),
        'hitbtc3': ccxt.hitbtc3(),
        'hollaex': ccxt.hollaex(),
        'huobijp': ccxt.huobijp(),
        'huobipro': ccxt.huobi(),
        # 'huobipro': ccxt.huobipro(),
        # 'ice3x': ccxt.ice3x(),
        'idex': ccxt.idex(),
        # 'idex2': ccxt.idex2(),
        'indodax': ccxt.indodax(),
        'independentreserve': ccxt.independentreserve(),

        # 'itbit': ccxt.itbit(),
        'kraken': ccxt.kraken(),
        'krakenfutures': ccxt.krakenfutures(),
        'kucoin': ccxt.kucoin(),
        'kuna': ccxt.kuna(),
        # 'lakebtc': ccxt.lakebtc(),
        'latoken': ccxt.latoken(),
        'lbank': ccxt.lbank(),
        # 'liquid': ccxt.liquid(),
        'luno': ccxt.luno(),
        'lykke': ccxt.lykke(),
        'mercado': ccxt.mercado(),
        'mexc':ccxt.mexc(),
        # 'mexc3' : ccxt.mexc3(),
        'mexc3' : ccxt.mexc(),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        # 'okex': ccxt.okex(),
        # 'okex5':ccxt.okex5(),
        'okex5':ccxt.okx(),
        'okx':ccxt.okx(),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi(),
        # 'lbank2': ccxt.lbank2(),
        'lbank2': ccxt.lbank(),
        'blockchaincom': ccxt.blockchaincom(),
        # 'btcex': ccxt.btcex(),
        'kucoinfutures': ccxt.kucoinfutures(),
        # 'okex3': ccxt.okex3(),
        # 'p2pb2b': ccxt.p2pb2b(),
        # 'paribu': ccxt.paribu(),
        'phemex': ccxt.phemex(),
        'tokocrypto':ccxt.tokocrypto(),
        'poloniex': ccxt.poloniex(),
        'probit': ccxt.probit(),
        # 'qtrade': ccxt.qtrade(),
        # 'ripio': ccxt.ripio(),
        # 'southxchange': ccxt.southxchange(),
        # 'stex': ccxt.stex(),
        # 'stronghold': ccxt.stronghold(),
        # 'surbitcoin': ccxt.surbitcoin(),
        # 'therock': ccxt.therock(),
        # 'tidebit': ccxt.tidebit(),
        # 'tidex': ccxt.tidex(),
        'timex': ccxt.timex(),
        'upbit': ccxt.upbit(),
        # 'vcc': ccxt.vcc(),
        'wavesexchange': ccxt.wavesexchange(),
        'woo':ccxt.woo(),
        'wazirx':ccxt.wazirx({
        'rateLimit': 300,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'whitebit': ccxt.whitebit(),
        # 'xbtce': ccxt.xbtce(),
        # 'xena': ccxt.xena(),
        # 'xt' : ccxt.xt(),
        'yobit': ccxt.yobit(),
        'zaif': ccxt.zaif(),
        # 'zb': ccxt.zb(),
        'zonda':ccxt.zonda(),
        'bingx': ccxt.bingx()
    }
    exchange_object = exchange_objects.get(exchange_name)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    # exchange_object.set_sandbox_mode(True)
    return exchange_object


import ccxt.async_support as ccxt_async
async def async_get_exchange_object3(exchange_name):
      # noqa: E402
    exchange_objects = {
        # 'aax': ccxt_async.aax(),
        # 'aofex': ccxt_async.aofex(),
        'ace': ccxt_async.ace({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'alpaca': ccxt_async.alpaca({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'ascendex': ccxt_async.ascendex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bequant': ccxt_async.bequant({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bibox': ccxt_async.bibox(),
        'bigone': ccxt_async.bigone({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'binance': ccxt_async.binance({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'binanceus': ccxt_async.binanceus({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'binancecoinm': ccxt_async.binancecoinm({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'binanceusdm':ccxt_async.binanceusdm({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bit2c': ccxt_async.bit2c({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitbank': ccxt_async.bitbank({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitbay': ccxt_async.bitbay({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitbns': ccxt_async.bitbns({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitcoincom': ccxt_async.bitcoincom({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitfinex': ccxt_async.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt_async.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitflyer': ccxt_async.bitflyer({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitforex': ccxt_async.bitforex({
        'rateLimit': 10000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitget': ccxt_async.bitget({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bithumb': ccxt_async.bithumb({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bitkk': ccxt_async.bitkk(),
        'bitmart': ccxt_async.bitmart({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bitmax': ccxt_async.bitmax(),
        'bitmex': ccxt_async.bitmex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitpanda': ccxt_async.bitpanda({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitso': ccxt_async.bitso({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitstamp': ccxt_async.bitstamp({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitstamp1': ccxt_async.bitstamp1({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bittrex': ccxt_async.bittrex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitrue':ccxt_async.bitrue({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitvavo': ccxt_async.bitvavo({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bitz': ccxt_async.bitz(),
        'bl3p': ccxt_async.bl3p({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bleutrade': ccxt_async.bleutrade(),
        # 'braziliex': ccxt_async.braziliex(),
        'bkex': ccxt_async.bkex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),  # Set a custom timeout of 60000 ms (1 minute)}),
        'btcalpha': ccxt_async.btcalpha({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'btcbox': ccxt_async.btcbox({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'btcmarkets': ccxt_async.btcmarkets({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'btctradeim': ccxt_async.btctradeim(),
        'btcturk': ccxt_async.btcturk({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'btctradeua':ccxt_async.btctradeua({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'buda': ccxt_async.buda(),
        'bybit': ccxt_async.bybit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'bytetrade': ccxt_async.bytetrade(),
        # 'cdax': ccxt_async.cdax(),
        'cex': ccxt_async.cex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'chilebit': ccxt_async.chilebit(),
        'coinbase': ccxt_async.coinbase({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinbaseprime': ccxt_async.coinbaseprime({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinbasepro': ccxt_async.coinbasepro({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coincheck': ccxt_async.coincheck({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'coinegg': ccxt_async.coinegg(),
        'coinex': ccxt_async.coinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinfalcon': ccxt_async.coinfalcon({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinsph':ccxt_async.coinsph({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'coinfloor': ccxt_async.coinfloor(),
        # 'coingi': ccxt_async.coingi(),
        # 'coinmarketcap': ccxt_async.coinmarketcap(),
        'cryptocom': ccxt_async.cryptocom({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinmate': ccxt_async.coinmate({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinone': ccxt_async.coinone({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'coinspot': ccxt_async.coinspot({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'crex24': ccxt_async.crex24(),
        'currencycom': ccxt_async.currencycom({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'delta': ccxt_async.delta({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'deribit': ccxt_async.deribit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'digifinex': ccxt_async.digifinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'dsx': ccxt_async.dsx(),
        # 'dx': ccxt_async.dx(),
        # 'eqonex': ccxt_async.eqonex(),
        # 'eterbase': ccxt_async.eterbase(),
        'exmo': ccxt_async.exmo({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'exx': ccxt_async.exx(),
        # 'fcoin': ccxt_async.fcoin(),
        # 'fcoinjp': ccxt_async.fcoinjp(),
        # 'ftx': ccxt_async.ftx(),
        # 'flowbtc':ccxt_async.flowbtc(),
        'fmfwio': ccxt_async.fmfwio({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'gate':ccxt_async.gate({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'gateio': ccxt_async.gateio({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'gemini': ccxt_async.gemini({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'gopax': ccxt_async.gopax(),
        # 'hbtc': ccxt_async.hbtc(),
        'hitbtc': ccxt_async.hitbtc({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'hitbtc2': ccxt_async.hitbtc2(),
        # 'hkbitex': ccxt_async.hkbitex(),
        'hitbtc3': ccxt_async.hitbtc3({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'hollaex': ccxt_async.hollaex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'huobijp': ccxt_async.huobijp({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'huobipro': ccxt_async.huobipro({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'ice3x': ccxt_async.ice3x(),
        'idex': ccxt_async.idex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'idex2': ccxt_async.idex2(),
        'indodax': ccxt_async.indodax({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'independentreserve': ccxt_async.independentreserve({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),

        # 'itbit': ccxt_async.itbit(),
        'kraken': ccxt_async.kraken({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'krakenfutures': ccxt_async.krakenfutures({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'kucoin': ccxt_async.kucoin({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'kuna': ccxt_async.kuna({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'lakebtc': ccxt_async.lakebtc(),
        'latoken': ccxt_async.latoken({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'lbank': ccxt_async.lbank({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'liquid': ccxt_async.liquid(),
        'luno': ccxt_async.luno({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'lykke': ccxt_async.lykke({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'mercado': ccxt_async.mercado({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'mexc':ccxt_async.mexc({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'mexc3' : ccxt_async.mexc3({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'mixcoins': ccxt_async.mixcoins(),
        'paymium':ccxt_async.paymium({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'poloniexfutures':ccxt_async.poloniexfutures({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'ndax': ccxt_async.ndax({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'novadax': ccxt_async.novadax({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'oceanex': ccxt_async.oceanex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'okcoin': ccxt_async.okcoin({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'okex': ccxt_async.okex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'okex5':ccxt_async.okex5({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'okx':ccxt_async.okx({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'bitopro': ccxt_async.bitopro({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'huobi': ccxt_async.huobi({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'lbank2': ccxt_async.lbank2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'blockchaincom': ccxt_async.blockchaincom({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'btcex': ccxt_async.btcex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'kucoinfutures': ccxt_async.kucoinfutures({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'okex3': ccxt_async.okex3(),
        # 'p2pb2b': ccxt_async.p2pb2b(),
        # 'paribu': ccxt_async.paribu(),
        'phemex': ccxt_async.phemex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'tokocrypto':ccxt_async.tokocrypto({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'poloniex': ccxt_async.poloniex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'probit': ccxt_async.probit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),

        'xt': ccxt_async.xt({
            'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
            'enableRateLimit': True,  # Enable rate limiting
            'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),

        # 'qtrade': ccxt_async.qtrade(),
        # 'ripio': ccxt_async.ripio(),
        # 'southxchange': ccxt_async.southxchange(),
        'stex': ccxt_async.stex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'stronghold': ccxt_async.stronghold(),
        # 'surbitcoin': ccxt_async.surbitcoin(),
        # 'therock': ccxt_async.therock(),
        # 'tidebit': ccxt_async.tidebit(),
        'tidex': ccxt_async.tidex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'timex': ccxt_async.timex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'upbit': ccxt_async.upbit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'vcc': ccxt_async.vcc(),
        'wavesexchange': ccxt_async.wavesexchange({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'woo':ccxt_async.woo({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'wazirx':ccxt_async.wazirx({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'whitebit': ccxt_async.whitebit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'xbtce': ccxt_async.xbtce(),
        # 'xena': ccxt_async.xena(),
        'yobit': ccxt_async.yobit({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        'zaif': ccxt_async.zaif({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)
    }),
        # 'zb': ccxt_async.zb(),
        'zonda':ccxt_async.zonda({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True,  # Enable rate limiting
        'timeout': 60000  # Set a custom timeout of 60000 ms (1 minute)


    })
    }
    exchange_object = exchange_objects.get(exchange_name)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    return exchange_object

def ohlcVolume(x):
    if len(x):
        ohlc={ "open":x["open"][0],"high":max(x["high"]),"low":min(x["low"]),"close":x["close"][-1],"volume":sum(x["volume"])}
        return pd.Series(ohlc)
# Function to resample a dataframe for a day timeframe
def resample_dataframe_daily(df):
    # df: The dataframe to be resampled.

    # Convert the timestamp to be in 12h:
    # df.index = df.index /1000
    print("df.index")
    print(df.index)
    df.index =  pd.to_datetime(df.index,unit='ms')

    # Resample the dataframe based on the day timeframe:
    resampled_df = df.resample('D').apply(ohlcVolume)

    return resampled_df

def convert_index_to_unix_timestamp(df):
    # convert the index to datetime object
    df.index = pd.to_datetime(df.index)

    # convert the datetime object to Unix timestamp in milliseconds
    df.index = df.index.astype(int) // 10**6

    return df
def fetch_entire_ohlcv_without_exchange_name(exchange_object,trading_pair, timeframe,limit_of_daily_candles):
    # exchange_id = 'bybit'
    # exchange_class = getattr(ccxt, exchange_id)
    # exchange = exchange_class()

    print(f'list of available timeframes for {exchange_object.id}')
    print(exchange_object.timeframes)
    # limit_of_daily_candles = 200
    data = []
    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df1 = pd.DataFrame(columns=header)
    data_df=pd.DataFrame()

    # Fetch the most recent 100 days of data for latoken exchange
    try:
        #exchange latoken has a specific limit of one request number of candles
        if isinstance(exchange_object, ccxt.latoken):
            print("exchange is latoken")
            limit_of_daily_candles = 100
    except:
        traceback.print_exc()

    # Fetch the most recent 200 days of data bybit exchange
    try:
        # exchange bybit has a specific limit of one request number of candles
        if isinstance(exchange_object, ccxt.bybit):
            print("exchange is bybit")
            limit_of_daily_candles = 200
    except:
        traceback.print_exc()

    if exchange_object.id == "btcex":
        timeframe="12h"
        data += exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
    else:
        data += exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
    first_timestamp_in_df=0
    first_timestamp_in_df_for_gateio=0

    # Fetch previous n days of data consecutively
    for i in range(1, 100):

        print("i=", i)
        print("data[0][0] - i * 86400000 * limit_of_daily_candles")
        # print(data[0][0] - i * 86400000 * limit_of_daily_candles)
        try:
            if exchange_object.id=="btcex":
                timeframe="12h"
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * (86400000/2) * limit_of_daily_candles)
            else:
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                     timeframe,
                                                     limit=limit_of_daily_candles,
                                                     since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
            data = previous_data + data
        finally:

            data_df1 = pd.DataFrame(data, columns=header)
            if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df:
                break
            first_timestamp_in_df = data_df1.iloc[0]['Timestamp']


    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df = pd.DataFrame(data, columns=header)

    data_df.drop_duplicates(subset=["Timestamp"],keep="first",inplace=True)
    data_df.sort_values("Timestamp",inplace=True)
    data_df = data_df.set_index('Timestamp')

    if exchange_object.id=="btcex":
        data_df_for_btcex=resample_dataframe_daily(data_df)
        # print("data_df_for_btcex")
        # print(data_df_for_btcex.to_string())
        data_df_for_btcex=convert_index_to_unix_timestamp(data_df_for_btcex)
        print("data_df_for_btcex")
        print(data_df_for_btcex.to_string())
        return data_df_for_btcex
    else:
        return data_df
def connect_to_postgres_db_without_deleting_it_first(database):

    import db_config
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' , echo = True )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def connect_to_postgres_db_with_deleting_it_first(database):
    import db_config
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database
    connection = None

    engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}",
                           isolation_level='AUTOCOMMIT',
                           echo=False,
                           pool_pre_ping=True,
                           pool_size=20, max_overflow=0,
                           connect_args={'connect_timeout': 10})
    print(f"{engine} created successfully")

    # Create database if it does not exist.
    if not database_exists(engine.url):
        try:
            create_database(engine.url)
        except:
            traceback.print_exc()
        print(f'new database created for {engine}')
        try:
            connection = engine.connect()
        except:
            traceback.print_exc()
        print(f'Connection to {engine} established after creating new database')

    if database_exists(engine.url):
        print("database exists ok")

        try:
            engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}",
                                   isolation_level='AUTOCOMMIT', echo=False)
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';

                            ''')
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''DROP DATABASE {database};''')
        except:
            traceback.print_exc()

        try:
            engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}",
                                   isolation_level='AUTOCOMMIT', echo=False)
        except:
            traceback.print_exc()
        try:
            create_database(engine.url)
        except:
            traceback.print_exc()
        print(f'new database created for {engine}')

    try:
        connection = engine.connect()
    except:
        traceback.print_exc()

    print(f'Connection to {engine} established. Database already existed.'
          f' So no new db was created')
    return engine, connection
def get_spread(exchange_instance, symbol):
    # exchange = getattr(ccxt, exchange_id)()
    orderbook = exchange_instance.fetch_order_book(symbol)
    bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
    spread = ask - bid if (bid is not None and ask is not None) else None
    return spread
def get_perpetual_swap_url(exchange_id, trading_pair):

    trading_pair=trading_pair.split(":")[0]
    base=trading_pair.split("/")[0]
    quote = trading_pair.split("/")[1]

    print(f"base = {base}")
    print(f"quote = {quote}")

    if exchange_id == 'binance':
        return f"https://www.binance.com/en/futures/{trading_pair.replace('/','').upper()}"
    elif exchange_id == 'huobipro':
        return f"https://www.huobi.com/en-us/futures/linear_swap/exchange#contract_code={base}-{quote}&contract_type=swap&type=isolated"
    elif exchange_id == 'huobi':
        return f"https://www.huobi.com/en-us/futures/linear_swap/exchange#contract_code={base}-{quote}&contract_type=swap&type=isolated"
    elif exchange_id == 'bybit':
        return f"https://www.bybit.com/trade/{quote.lower()}/{trading_pair.replace('/','').upper()}"
    elif exchange_id == 'hitbtc3':
        return f"https://www.hitbtc.com/futures/{base.lower()}-to-{quote.lower()}"
    elif exchange_id == 'mexc' or exchange_id == 'mexc3':
        return f"https://futures.mexc.com/exchange/{trading_pair.replace('/','_').upper()}?type=linear_swap"
    elif exchange_id == 'bitfinex' or exchange_id == 'bitfinex2':
        # return f"https://trading.bitfinex.com/t/{trading_pair.replace('/','')+'F0:USDTF0'}"
        base=trading_pair.split('/')[0]
        quote=trading_pair.split('/')[1]
        if quote=='USDT':
            return f"https://trading.bitfinex.com/t/{base}F0:USTF0"
        if quote=='BTC':
            return f"https://trading.bitfinex.com/t/{base}F0:{quote}F0"
    elif exchange_id == 'gateio':
        return f"https://www.gate.io/en/futures_trade/{quote}/{trading_pair.replace('/','_').upper()}"
    elif exchange_id == 'gate':
        return f"https://www.gate.io/en/futures_trade/{quote}/{trading_pair.replace('/','_').upper()}"
    elif exchange_id == 'kucoin':
        return f"https://futures.kucoin.com/trade/{trading_pair.replace('/','-')}-SWAP"
    elif exchange_id == 'coinex':
        # return f"https://www.coinex.com/swap/{trading_pair.replace('/','').upper()}"
        return f"https://www.coinex.com/futures/{trading_pair.replace('/','-').upper()}"
    elif exchange_id == 'poloniex':
        return f"https://www.poloniex.com/futures/trade/{base.upper()}{quote.upper()}PERP"
    elif exchange_id == 'lbank2':
        return f"https://www.lbank.com/futures/{base.lower()}{quote.lower()}/"
    elif exchange_id == 'lbank':
        return f"https://www.lbank.com/futures/{base.lower()}{quote.lower()}/"
    elif exchange_id == 'bkex':
        return f"https://swap.bkex.com/contract/LIVE_{quote.upper()}/{base.lower()}_{quote.lower()}"
    elif exchange_id == 'bitmart':
        return f"https://derivatives.bitmart.com/en-US?symbol={base.upper()}{quote.upper()}&theme=dark"
    elif exchange_id == 'whitebit':
        return f"https://whitebit.com/ru/trade/{base.upper()}-PERP"
    elif exchange_id == 'bitget':
        return f"https://www.bitget.com/ru/mix/usdt/{base.upper()}{quote.upper()}_UMCBL/"
    elif exchange_id == 'cryptocom':
        return f"https://crypto.com/exchange/trade/{base.upper()}{quote.upper()}-PERP"
    elif exchange_id == 'delta':
        return f"https://www.delta.exchange/app/futures/trade/{base.upper()}/{base.upper()}{quote.upper()}"
    elif exchange_id == 'btcex':
        return f"https://www.btcex.com/en-us/perpetual/{base.upper()}-{quote.upper()}-PERPETUAL"
    elif exchange_id == 'ascendex':
        return f"https://ascendex.com/en/futures-perpetualcontract-trading/{base.lower()}-perp"
    elif exchange_id == 'bigone':
        return f"https://big.one/contract/trade/{base.upper()}{quote.upper()}"
    elif exchange_id == 'xt':
        return f"https://www.xt.com/en/futures/trade/{base.lower()}_{quote.lower()}"
    elif exchange_id == 'woo':
        return f"https://x.woo.org/en/trade/{base.upper()}_PERP"
    elif exchange_id == 'okex5':
        return f"https://www.okx.com/ru/trade-swap/{base.lower()}-{quote.lower()}-swap"
    elif exchange_id == 'okex':
        return f"https://www.okx.com/ru/trade-swap/{base.lower()}-{quote.lower()}-swap"
    elif exchange_id == 'okx':
        return f"https://www.okx.com/ru/trade-swap/{base.lower()}-{quote.lower()}-swap"
    elif exchange_id == 'poloniexfutures':
        return f"https://www.poloniex.com/futures/trade/{base.upper()}{quote.upper()}PERP"
    elif exchange_id == 'ascendex':
        return f"https://ascendex.com/en/margin-trading/{quote.lower()}/{base.lower()}"
    elif exchange_id == 'phemex':
        return f"https://phemex.com/trade/{base.upper()}{quote.upper()}"
    elif exchange_id == 'digifinex':
        return f"https://www.digifinex.com/en-ww/swap/{base.upper()}{quote.upper()}PERP"
    elif exchange_id == 'bingx':
        return f"https://swap.bingx.com/en-us/{base.upper()}-{quote.upper()}"
    elif exchange_id == 'bitforex':
        return f"https://www.bitforex.com/en/perpetual/{base.lower()}_{quote.lower()}"
    elif exchange_id == 'bitrue':
        return f"https://www.bitrue.com/futures/{base.upper()}"
    elif exchange_id == 'bitbns':
        return f"https://bitbns.com/trade/#/futures/{base.upper()}{quote.upper()}_Perpetual"
    elif exchange_id == 'fmfwio':
        return f"https://fmfw.io/futures/{base.lower()}-to-{quote.lower()}"
    else:
        return "Exchange not supported"

def is_scientific_notation(number_string):
    return bool(re.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', str(number_string)))
def scientific_to_decimal(number):
    """
    Converts a number in scientific notation to a decimal number.

    Args:
        number (str): A string representing a number in scientific notation.

    Returns:
        float: The decimal value of the input number.
    """
    num_float=float(number)
    num_str = '{:.{}f}'.format(num_float, abs(int(str(number).split('e')[1])))
    return float(num_str)

def scientific_to_decimal2(number):
    """
    Converts a number in scientific notation to a decimal number.

    Args:
        number (str): A string representing a number in scientific notation.

    Returns:
        float: The decimal value of the input number.
    """
    if 'e' in number:
        mantissa, exponent = number.split('e')
        return float(mantissa) * 10 ** int(exponent)
    else:
        return float(number)

def count_zeros_number_with_e_notaton_is_acceptable(number):

    number_str = str(number)  # convert the number to a string
    if is_scientific_notation(number_str):

        # print("number_str")
        # print(number_str)
        # print(bool('e' in number_str))
        # print(type(number_str))
        if 'e-' in number_str:
            mantissa, exponent = number_str.split('e-')
            # print("mantissa")
            # print(mantissa)
            # print("exponent")
            # print(int(float(exponent)))
            return int(float(exponent))

    count = 0
    for digit in number_str:
        if digit == '0':
            count += 1
        elif digit == '.':
            continue # stop counting zeros at the decimal point
        else:
            break # skip non-zero digits

    #remove the zero befor point
    if number_str.startswith("0"):
        count=count-1
    return count

def fetch_huobipro_ohlcv(symbol, exchange,timeframe='1d'):

    ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)

    return df
def get_huobipro_fees(trading_pair):
    exchange = ccxt.huobipro()
    symbol_info = exchange.load_markets()[trading_pair]
    # print("symbol_info")
    # print(symbol_info)
    maker_fee = symbol_info['maker']
    taker_fee = symbol_info['taker']
    return maker_fee, taker_fee

def get_fees(markets, trading_pair):
    market=markets[trading_pair]
    # pprint.pprint(market)
    return market['maker'], market['taker']
def get_asset_type(exchange_name, trading_pair):
    exchange = getattr(ccxt, exchange_name)()
    market = exchange.load_markets()[trading_pair]
    # print("market1")
    pprint.pprint(market)
    # market=markets[trading_pair]
    print("pprint.pprint(exchange.describe())")
    pprint.pprint(exchange.describe())


    return market['type']

def get_exchange_url(exchange_id, exchange_object,symbol):
    exchange = exchange_object
    print("exchange_object")
    print(exchange_object)
    market = exchange.market(symbol)

    if exchange_id == 'binance':
        return f"https://www.binance.com/en/trade/{market['base']}_{''.join(market['quote'].split('/'))}?layout=pro&type=spot"
    elif exchange_id == 'huobipro':
        return f"https://www.huobi.com/en-us/exchange/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'huobi':
        return f"https://www.huobi.com/en-us/exchange/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'bybit':
        return f"https://www.bybit.com/ru-RU/trade/spot/{market['base']}/{market['quote']}"
    elif exchange_id == 'hitbtc3':
        return f"https://hitbtc.com/{market['base']}-to-{market['quote']}"
    elif exchange_id == 'mexc' or exchange_id == 'mexc3':
        return f"https://www.mexc.com/exchange/{market['base']}_{market['quote']}"
    elif exchange_id == 'bitfinex' or exchange_id == 'bitfinex2':
        return f"https://trading.bitfinex.com/t/{market['base']}:UST?type=exchange"
    elif exchange_id == 'exmo':
        return f"https://exmo.me/en/trade/{market['base']}_{market['quote']}"
    elif exchange_id == 'gateio':
        return f"https://www.gate.io/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'gate':
        return f"https://www.gate.io/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'kucoin':
        return f"https://trade.kucoin.com/{market['base']}-{market['quote']}"
    elif exchange_id == 'coinex':
        return f"https://www.coinex.com/exchange/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'poloniex':
        return f"https://www.poloniex.com/trade/{market['base'].upper()}_{market['quote'].upper()}/?type=spot"
    elif exchange_id == 'lbank2':
        return f"https://www.lbank.com/trade/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'lbank':
        return f"https://www.lbank.com/trade/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'bitmart':
        return f"https://www.bitmart.com/trade/en-US?layout=basic&theme=dark&symbol={market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'bkex':
        return f"https://www.bkex.com/en/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'whitebit':
        return f"https://whitebit.com/ru/trade/{market['base'].upper()}-{market['quote'].upper()}?type=spot&tab=open-orders"
    elif exchange_id == 'bitget':
        return f"https://www.bitget.com/ru/spot/{market['base'].upper()}{market['quote'].upper()}_SPBL?type=spot"
    elif exchange_id == 'cryptocom':
        return f"https://crypto.com/exchange/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'currencycom':
        return f"https://currency.com/{market['base'].lower()}-to-{market['quote'].lower()}"
    elif exchange_id == 'btcex':
        return f"https://www.btcex.com/en-us/spot/{market['base'].upper()}-{market['quote'].upper()}-SPOT"
    elif exchange_id == 'tokocrypto':
        return f"https://www.tokocrypto.com/id/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'wazirx':
        return f"https://wazirx.com/exchange/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'coinbase':
        return f"https://exchange.coinbase.com/trade/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'coinbasepro':
        return f"https://exchange.coinbase.com/trade/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'coinbaseprime':
        return f"https://exchange.coinbase.com/trade/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'ascendex':
        return f"https://ascendex.com/en/cashtrade-spottrading/{market['quote'].lower()}/{market['base'].lower()}"
    elif exchange_id == 'bigone':
        return f"https://big.one/en/trade/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'xt':
        return f"https://www.xt.com/en/trade/{market['base'].lower()}_{market['quote'].lower()}"
    elif exchange_id == 'woo':
        return f"https://x.woo.org/en/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'okex5':
        return f"https://www.okx.com/ru/trade-spot/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'okex':
        return f"https://www.okx.com/ru/trade-spot/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'okx':
        return f"https://www.okx.com/ru/trade-spot/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'ascendex':
        return f"https://ascendex.com/en/cashtrade-spottrading/{market['quote'].lower()}/{market['base'].lower()}"
    elif exchange_id == 'probit':
        return f"https://www.probit.com/app/exchange/{market['base'].upper()}-{market['quote'].upper()}"
    elif exchange_id == 'oceanex':
        return f"https://oceanex.pro/en/trades/{market['base'].lower()}{market['quote'].lower()}"
    elif exchange_id == 'phemex':
        return f"https://phemex.com/margin/trade/{market['base'].upper()}{market['quote'].upper()}"
    elif exchange_id == 'digifinex':
        return f"https://www.digifinex.com/en-ww/trade/{market['quote'].upper()}/{market['base'].upper()}"
    elif exchange_id == 'bequant':
        return f"https://bequant.io/{market['base'].lower()}-to-{market['quote'].lower()}"
    elif exchange_id== 'bingx':
        return f"https://bingx.com/en-us/spot/{market['base'].upper()}{market['quote'].upper()}/"
    elif exchange_id == 'bitforex':
        return f"https://www.bitforex.com/en/spot/{market['base'].lower()}_{market['quote'].lower()}"
    elif exchange_id == 'bitrue':
        return f"https://www.bitrue.com/trade/{market['base'].lower()}_{market['quote'].lower()}"
    elif exchange_id == 'bitbns':
        return f"https://bitbns.com/trade/#/{market['base'].lower()}"
    elif exchange_id == 'fmfwio':
        return f"https://fmfw.io/{market['base'].lower()}-to-{market['quote'].lower()}"
    elif exchange_id == 'hollaex':
        return f"https://pro.hollaex.com/trade/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'upbit':
        return f"https://upbit.com/exchange?code=CRIX.UPBIT.{market['quote'].upper()}-{market['base'].upper()}"
    elif exchange_id == 'zonda':
        return f"https://app.zondacrypto.exchange/market/{market['base'].lower()}-{market['quote'].lower()}"
    else:
        return "Exchange not supported"

def get_asset_type2(markets, trading_pair):
    market = markets[trading_pair]
    return market['type']

def if_margin_true_for_an_asset(markets, trading_pair):
    market = markets[trading_pair]
    print(f" markets[{trading_pair}]")
    print(market)
    return market['margin']

# def get_asset_type(markets, trading_pair):
#     # exchange = getattr(ccxt, exchange_name)()
#     # market = exchange.load_markets()[trading_pair]
#     market=markets[trading_pair]
#     return market['type']

def get_taker_tiered_fees(exchange_object):
    trading_fees = exchange_object.describe()['fees']['linear']['trading']
    taker_fees = trading_fees['tiers']['taker']
    return taker_fees

def fetch_entire_ohlcv(exchange_object,exchange_name,trading_pair, timeframe,limit_of_daily_candles):
    # import ccxt
    # exchange_id = 'bybit'
    # exchange_class = getattr(ccxt, exchange_id)
    # exchange = exchange_class()

    # limit_of_daily_candles = 200
    data = []
    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df1 = pd.DataFrame(columns=header)
    data_df=pd.DataFrame()

    # Fetch the most recent 100 days of data for latoken exchange
    try:
        # exchange latoken has a specific limit of one request number of candles
        if isinstance(exchange_object, ccxt.latoken):
            print("exchange is latoken")
            limit_of_daily_candles = 1
    except:
        traceback.print_exc()

    # Fetch the most recent 200 days of data bybit exchange
    try:
        # exchange bybit has a specific limit of one request number of candles
        if isinstance(exchange_object, ccxt.bybit):
            print("exchange is bybit")
            limit_of_daily_candles = 200
    except:
        traceback.print_exc()

    try:
        # exchange bybit has a specific limit of one request number of candles
        if isinstance(exchange_object, ccxt.poloniex):
            print("exchange is poloniex")
            limit_of_daily_candles = 480
    except:
        traceback.print_exc()

    if exchange_object.id == "btcex":
        timeframe = "12h"
        data += exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
    else:
        data += exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)

    first_timestamp_in_df=0
    first_timestamp_in_df_for_gateio=0


    print(f"limit_of_daily_candles123 for {exchange_object}")
    print(limit_of_daily_candles)
    # Fetch previous 200 days of data consecutively
    for i in range(1, 100):

        print("i=", i)
        print("data[0][0] - i * 86400000 * limit_of_daily_candles")
        # print(data[0][0] - i * 86400000 * limit_of_daily_candles)
        try:
            if exchange_object.id == "btcex" :
                timeframe = "12h"
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * (
                                                                        86400000 / 2) * limit_of_daily_candles)
            elif exchange_object.id == "alpaca":
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
            elif exchange_object.id == "exmo":
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
            elif exchange_object.id == "bittrex":
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
            elif exchange_object.id == "bitmex":
                previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                            timeframe,
                                                            limit=limit_of_daily_candles,
                                                            since=data[-1][0] - i * 86400000 * limit_of_daily_candles)

            else:
                if i>1:
                    previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                                timeframe,
                                                                limit=limit_of_daily_candles,
                                                                since=data[-1][0] - i * 86400000 * limit_of_daily_candles,
                                                                params={'endTime': data[-1][0] - (i-1) * 86400000 * limit_of_daily_candles})
                else:
                    previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                                timeframe,
                                                                limit=limit_of_daily_candles,
                                                                since=data[-1][
                                                                          0] - i * 86400000 * limit_of_daily_candles)
            data = previous_data + data
        except:
            traceback.print_exc()
        finally:

            data_df1 = pd.DataFrame(data, columns=header)
            if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df:
                break
            first_timestamp_in_df = data_df1.iloc[0]['Timestamp']

    if exchange_object.id == "whitebit":
        data = exchange_object.fetch_ohlcv(trading_pair,
                                                timeframe)

    if exchange_object.id == "hitbtc3":
        data=exchange_object.fetch_ohlcv(trading_pair, timeframe, params={"paginate": True})


    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df = pd.DataFrame(data, columns=header)
    # try:
    #     data_df["open_time"] = data_df["Timestamp"].apply(
    #         lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
    # except Exception as e:
    #     print("error_message")
    #     traceback.print_exc()
    data_df.drop_duplicates(subset=["Timestamp"],keep="first",inplace=True)
    data_df.sort_values("Timestamp",inplace=True)
    data_df = data_df.set_index('Timestamp')


    if exchange_object.id=="btcex":
        data_df_for_btcex=resample_dataframe_daily(data_df)
        # print("data_df_for_btcex")
        # print(data_df_for_btcex.to_string())
        data_df_for_btcex=convert_index_to_unix_timestamp(data_df_for_btcex)
        # print("data_df_for_btcex")
        # print(data_df_for_btcex.to_string())

        try:
            # add volume multiplied by low
            data_df_for_btcex["volume*low"] = data_df_for_btcex["volume"] * data_df_for_btcex["low"]
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by close
            data_df_for_btcex["volume*close"] = data_df_for_btcex["volume"] * data_df_for_btcex["close"]
        except:
            traceback.print_exc()

        return data_df_for_btcex
    else:
        try:
            # add volume multiplied by low
            data_df["volume*low"] = data_df["volume"] * data_df["low"]
        except:
            traceback.print_exc()

        try:
            # add volume multiplied by close
            data_df["volume*close"] = data_df["volume"] * data_df["close"]
        except:
            traceback.print_exc()


        return data_df





def get_maker_taker_fees_for_huobi(exchange_object):
    fees = exchange_object.describe()['fees']['trading']
    maker_fee = fees['maker']
    taker_fee = fees['taker']
    return maker_fee, taker_fee
def get_maker_tiered_fees(exchange_object):
    print("exchange_object")
    print(exchange_object)

    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    trading_fees = exchange_object.describe()['fees']['linear']['trading']
    maker_fees = trading_fees['tiers']['maker']
    return maker_fees


def get_tuple_with_lists_taker_and_maker_fees(exchange_object):


    # retrieve fee structure from exchange
    fee_structure = exchange_object.describe()['fees']['trading']['taker']
    print("fee_structure")
    print(fee_structure)
    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    # calculate taker fees for each tier
    taker_fees = []
    for tier in fee_structure:
        fee = tier[1]
        if tier[0] == 0:
            taker_fees.append((0, fee))
        else:
            prev_tier = taker_fees[-1]
            taker_fees.append((prev_tier[1], fee))

    # calculate maker fees for each tier
    maker_fees = []
    for tier in fee_structure:
        fee = tier[2]
        if tier[0] == 0:
            maker_fees.append((0, fee))
        else:
            prev_tier = maker_fees[-1]
            maker_fees.append((prev_tier[1], fee))

    return (taker_fees, maker_fees)
def get_dict_taker_and_maker_fees(exchange_object):


    # retrieve fee structure from exchange
    fee_structure = exchange_object.describe()['fees']['trading']['taker']
    print("fee_structure")
    print(fee_structure)
    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    # calculate taker fees for each tier
    taker_fees = {}
    for tier in fee_structure:
        fee = tier[1]
        if tier[0] == 0:
            taker_fees['0'] = fee
        else:
            prev_tier_fee = taker_fees[str(tier[0] - 1)]
            taker_fees[str(tier[0])] = fee if fee != prev_tier_fee else None

    # calculate maker fees for each tier
    maker_fees = {}
    for tier in fee_structure:
        fee = tier[2]
        if tier[0] == 0:
            maker_fees['0'] = fee
        else:
            prev_tier_fee = maker_fees[str(tier[0] - 1)]
            maker_fees[str(tier[0])] = fee if fee != prev_tier_fee else None

    return {'taker_fees': taker_fees, 'maker_fees': maker_fees}

def get_huobi_margin_pairs():
    huobi = ccxt.huobipro()


    # Check if Huobi supports margin trading
    if 'margin' in huobi.load_markets():
        # Get list of assets available for margin trading
        margin_symbols = huobi.load_markets(True)['margin']
        # Filter margin symbols to get only those with USDT as the quote currency
        margin_pairs = [symbol for symbol in margin_symbols if symbol.endswith('/USDT')]
        return margin_pairs
    else:
        print('Huobi does not support margin trading')
        return []

def get_shortable_assets_for_gateio():
    # Create a Gate.io exchange object
    exchange = ccxt.gateio()
    # print("exchange.load_markets()")
    # pprint.pprint(exchange.load_markets())

    # Load the exchange markets
    markets = exchange.load_markets()

    # Get the list of shortable assets
    shortable_assets = []
    for symbol, market in markets.items():
        if 'info' in market and 'shortable' in market['info'] and market['info']['shortable']:
            shortable_assets.append(symbol)

    return shortable_assets

def get_shortable_assets_for_binance():
    # create a Binance exchange instance
    exchange = ccxt.binance()

    # retrieve the exchange info
    exchange_info = exchange.load_markets()

    # retrieve the symbols that are shortable
    shortable_assets = []
    for symbol in exchange_info:
        market_info = exchange_info[symbol]
        if market_info.get('info', {}).get('isMarginTradingAllowed') == True:
            shortable_assets.append(symbol)

    return shortable_assets

def get_active_trading_pairs_from_huobipro():
    exchange = ccxt.huobipro()
    pairs = exchange.load_markets()
    active_pairs = []
    for pair in pairs.values():
        if pair['active']:
            active_pairs.append(pair['symbol'])
    return active_pairs
def get_exchange_object_and_limit_of_daily_candles(exchange_name):
    exchange_object = None
    limit = None

    # if exchange_name == 'binance':
    #     exchange_object = ccxt.binance()
    #     limit = 2000
    # elif exchange_name == 'huobipro':
    #     exchange_object = ccxt.huobipro()
    #     limit = 2000
    # elif exchange_name == 'bybit':
    #     exchange_object = ccxt.bybit()
    #     limit = 200
    # elif exchange_name == 'hitbtc3':
    #     exchange_object = ccxt.hitbtc3()
    #     limit = 1000
    # elif exchange_name == 'mexc':
    #     exchange_object = ccxt.mexc()
    #     limit = 2000
    # elif exchange_name == 'mexc3':
    #     exchange_object = ccxt.mexc3()
    #     limit = 2000
    # elif exchange_name == 'bitfinex':
    #     exchange_object = ccxt.bitfinex()
    #     limit = 1000
    # elif exchange_name == 'bitfinex2':
    #     exchange_object = ccxt.bitfinex2()
    #     limit = 1000
    # elif exchange_name == 'exmo':
    #     exchange_object = ccxt.exmo()
    #     limit = 2000
    # elif exchange_name == 'gateio':
    #     exchange_object = ccxt.gateio()
    #     limit = 2000
    # elif exchange_name == 'kucoin':
    #     exchange_object = ccxt.kucoin()
    #     limit = 2000
    # elif exchange_name == 'coinex':
    #     exchange_object = ccxt.coinex()
    #     limit = 2000
    # return exchange_object, limit



    if exchange_name == 'binance':
        exchange_object = ccxt.binance()
        limit = 2000
    elif exchange_name == 'huobipro':
        exchange_object = ccxt.huobipro()
        limit = 1000
    elif exchange_name == 'bybit':
        exchange_object = ccxt.bybit()
        limit = 20000
    elif exchange_name == 'hitbtc3':
        exchange_object = ccxt.hitbtc3()
        limit = 10000
    elif exchange_name == 'mexc':
        exchange_object = ccxt.mexc()
        limit = 2000
    elif exchange_name == 'mexc3':
        exchange_object = ccxt.mexc3()
        limit = 2000
    elif exchange_name == 'bitfinex':
        exchange_object = ccxt.bitfinex()
        limit = 1000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2()
        limit = 1000
    elif exchange_name == 'exmo':
        exchange_object = ccxt.exmo()
        limit = 3000
    elif exchange_name == 'gateio':
        exchange_object = ccxt.gateio()
        limit = 20000
    elif exchange_name == 'kucoin':
        exchange_object = ccxt.kucoin()
        limit = 20000

    elif exchange_name == 'coinex':
        exchange_object = ccxt.coinex()
        limit = 20000
    return exchange_object, limit

def get_limit_of_daily_candles_original_limits(exchange_name):
    exchange_object = None
    limit = None

    if exchange_name == 'binance':
        exchange_object = ccxt.binance()
        limit = 1000
    elif exchange_name == 'bingx':
        exchange_object = ccxt.bingx()
        limit = 1000

    elif exchange_name == 'ace':
        exchange_object = ccxt.ace()
        limit = 1000
    elif exchange_name == 'alpaca':
        exchange_object = ccxt.alpaca()
        limit = 1000
    elif exchange_name == 'ascendex':
        exchange_object = ccxt.ascendex()
        limit = 1000
    elif exchange_name == 'bequant':
        exchange_object = ccxt.bequant()
        limit = 1000
    elif exchange_name == 'digifinex':
        exchange_object = ccxt.digifinex()
        limit = 1000
    elif exchange_name == 'fmfwio':
        exchange_object = ccxt.fmfwio()
        limit = 1000

    elif exchange_name == 'independentreserve':
        exchange_object = ccxt.independentreserve()
        limit = 1000
    elif exchange_name == 'fmfwio':
        exchange_object = ccxt.fmfwio()
        limit = 1000
    elif exchange_name == 'yobit':
        exchange_object = ccxt.yobit()
        limit = 1000
    elif exchange_name == 'zaif':
        exchange_object = ccxt.zaif()
        limit = 1000
    elif exchange_name == 'zonda':
        exchange_object = ccxt.zonda()
        limit = 1000
    elif exchange_name == 'bitflyer':
        exchange_object = ccxt.bitflyer()
        limit = 1000
    elif exchange_name == 'bithumb':
        exchange_object = ccxt.bithumb()
        limit = 1000
    elif exchange_name == 'bitmex':
        exchange_object = ccxt.bitmex()
        limit = 1000
    elif exchange_name == 'bitopro':
        exchange_object = ccxt.bitopro()
        limit = 1000
    elif exchange_name == 'bitpanda':
        exchange_object = ccxt.bitpanda()
        limit = 1000
    elif exchange_name == 'bitrue':
        exchange_object = ccxt.bitrue()
        limit = 1000
    elif exchange_name == 'bitso':
        exchange_object = ccxt.bitso()
        limit = 1000
    elif exchange_name == 'bitstamp':
        exchange_object = ccxt.bitstamp()
        limit = 1000
    elif exchange_name == 'bitstamp1':
        exchange_object = ccxt.bitstamp1()
        limit = 1000
    elif exchange_name == 'bittrex':
        exchange_object = ccxt.bittrex()
        limit = 1000
    elif exchange_name == 'bl3p':
        exchange_object = ccxt.bl3p()
        limit = 1000
    elif exchange_name == 'blockchaincom':
        exchange_object = ccxt.blockchaincom()
        limit = 1000
    elif exchange_name == 'btcbox':
        exchange_object = ccxt.btcbox()
        limit = 1000
    elif exchange_name == 'btcmarkets':
        exchange_object = ccxt.btcmarkets()
        limit = 1000
    elif exchange_name == 'btctradeua':
        exchange_object = ccxt.btctradeua()
        limit = 1000
    elif exchange_name == 'btcturk':
        exchange_object = ccxt.btcturk()
        limit = 1000
    elif exchange_name == 'cex':
        exchange_object = ccxt.cex()
        limit = 1000
    elif exchange_name == 'coinbase':
        exchange_object = ccxt.coinbase()
        limit = 1000
    elif exchange_name == 'coinbase':
        exchange_object = ccxt.coinbase()
        limit = 1000
    elif exchange_name == 'coinbaseprime':
        exchange_object = ccxt.coinbaseprime()
        limit = 1000
    elif exchange_name == 'coinbasepro':
        exchange_object = ccxt.coinbasepro()
        limit = 1000
    elif exchange_name == 'coincheck':
        exchange_object = ccxt.coincheck()
        limit = 1000
    elif exchange_name == 'coinfalcon':
        exchange_object = ccxt.coinfalcon()
        limit = 1000
    elif exchange_name == 'coinmate':
        exchange_object = ccxt.coinmate()
        limit = 1000
    elif exchange_name == 'coinone':
        exchange_object = ccxt.coinone()
        limit = 1000
    elif exchange_name == 'coinsph':
        exchange_object = ccxt.coinsph()
        limit = 1000
    elif exchange_name == 'coinspot':
        exchange_object = ccxt.coinspot()
        limit = 1000
    elif exchange_name == 'deribit':
        exchange_object = ccxt.deribit()
        limit = 1000



    elif exchange_name == 'bitbank':
        exchange_object = ccxt.bitbank()
        limit = 1000
    elif exchange_name == 'bitbay':
        exchange_object = ccxt.bitbay()
        limit = 1000
    elif exchange_name == 'bitbns':
        exchange_object = ccxt.bitbns()
        limit = 1000
    elif exchange_name == 'gemini':
        exchange_object = ccxt.gemini()
        limit = 1000
    elif exchange_name == 'idex':
        exchange_object = ccxt.idex()
        limit = 1000
    elif exchange_name == 'indodax':
        exchange_object = ccxt.indodax()
        limit = 1000
    elif exchange_name == 'kraken':
        exchange_object = ccxt.kraken()
        limit = 1000
    elif exchange_name == 'krakenfutures':
        exchange_object = ccxt.krakenfutures()
        limit = 1000
    elif exchange_name == 'wazirx':
        exchange_object = ccxt.wazirx()
        limit = 1000

    elif exchange_name == 'kuna':
        exchange_object = ccxt.kuna()
        limit = 1000
    elif exchange_name == 'luno':
        exchange_object = ccxt.luno()
        limit = 1000
    elif exchange_name == 'lykke':
        exchange_object = ccxt.lykke()
        limit = 1000
    elif exchange_name == 'mercado':
        exchange_object = ccxt.mercado()
        limit = 1000
    elif exchange_name == 'wavesexchange':
        exchange_object = ccxt.wavesexchange()
        limit = 1000
    elif exchange_name == 'woo':
        exchange_object = ccxt.woo()
        limit = 1000



    elif exchange_name == 'bitcoincom':
        exchange_object = ccxt.bitcoincom()
        limit = 1000
    elif exchange_name == 'bit2c':
        exchange_object = ccxt.bit2c()
        limit = 1000
    elif exchange_name == 'huobipro':
        exchange_object = ccxt.huobipro()
        limit = 1000
    elif exchange_name == 'hollaex':
        exchange_object = ccxt.hollaex()
        limit = 1000
    elif exchange_name == 'huobijp':
        exchange_object = ccxt.huobijp()
        limit = 1000
    elif exchange_name == 'upbit':
        exchange_object = ccxt.upbit()
        limit = 1000
    elif exchange_name == 'huobi':
        exchange_object = ccxt.huobi()
        limit = 1000
    elif exchange_name == 'bybit':
        exchange_object = ccxt.bybit()
        limit = 200
    elif exchange_name == 'hitbtc3':
        exchange_object = ccxt.hitbtc3()
        limit = 500
    elif exchange_name == 'mexc':
        exchange_object = ccxt.mexc()
        limit = 1000
    elif exchange_name == 'mexc3':
        exchange_object = ccxt.mexc3()
        limit = 1000
    elif exchange_name == 'bitfinex':
        exchange_object = ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 1000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 1000
    elif exchange_name == 'bitvavo':
        exchange_object = ccxt.bitvavo()
        limit = 100
    elif exchange_name == 'ndax':
        exchange_object = ccxt.ndax()
        limit = 100
    elif exchange_name == 'oceanex':
        exchange_object = ccxt.oceanex()
        limit = 100
    elif exchange_name == 'okcoin':
        exchange_object = ccxt.okcoin()
        limit = 100
    elif exchange_name == 'okex5':
        exchange_object = ccxt.okex5()
        limit = 100
    elif exchange_name == 'okex':
        exchange_object = ccxt.okex()
        limit = 100
    elif exchange_name == 'okx':
        exchange_object = ccxt.okx()
        limit = 100
    elif exchange_name == 'paymium':
        exchange_object = ccxt.paymium()
        limit = 100
    elif exchange_name == 'phemex':
        exchange_object = ccxt.phemex()
        limit = 100
    elif exchange_name == 'poloniex':
        exchange_object = ccxt.poloniex({
        'rateLimit': 2000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 480
    elif exchange_name == 'poloniexfutures':
        exchange_object = ccxt.poloniexfutures()
        limit = 100
    elif exchange_name == 'probit':
        exchange_object = ccxt.probit()
        limit = 100
    # elif exchange_name == 'stex':
    #     exchange_object = ccxt.stex()
    #     limit = 100
    elif exchange_name == 'tidex':
        exchange_object = ccxt.tidex()
        limit = 100
    elif exchange_name == 'timex':
        exchange_object = ccxt.timex()
        limit = 100
    elif exchange_name == 'tokocrypto':
        exchange_object = ccxt.tokocrypto()
        limit = 100
    # elif exchange_name == 'upbit':
    #     exchange_object = ccxt.upbit()
    #     limit = 100

    elif exchange_name == 'novadax':
        exchange_object = ccxt.novadax()
        limit = 100
    elif exchange_name == 'exmo':
        exchange_object = ccxt.exmo()
        limit = 2000
    elif exchange_name == 'gateio':
        exchange_object = ccxt.gateio()
        limit = 1000
    elif exchange_name == 'gate':
        exchange_object = ccxt.gate()
        limit = 1000
    elif exchange_name == 'kucoin':
        exchange_object = ccxt.kucoin()
        limit = 2000
    elif exchange_name == 'coinex':
        exchange_object = ccxt.coinex()
        limit = 500
    elif exchange_name == 'poloniex':
        exchange_object = ccxt.poloniex()
        limit = 500
    elif exchange_name == 'lbank2':
        exchange_object = ccxt.lbank2()
        limit = 1000
    elif exchange_name == 'lbank':
        exchange_object = ccxt.lbank()
        limit = 1000

    elif exchange_name == 'zb':
        # exchange_object = ccxt.zb()
        limit = 1000
    # elif exchange_name == 'tokocrypto':
    #     exchange_object = ccxt.tokocrypto()
    #     limit = 1000
    elif exchange_name == 'currencycom':
        exchange_object = ccxt.currencycom()
        limit = 1000
    elif exchange_name == 'cryptocom':
        exchange_object = ccxt.cryptocom()
        limit = 300
    elif exchange_name == 'delta':
        exchange_object = ccxt.delta()
        limit = 1000
    elif exchange_name == 'bitmart':
        exchange_object = ccxt.bitmart()
        limit = 1000
    # elif exchange_name == 'probit':
    #     exchange_object = ccxt.probit()
    #     limit = 1000
    elif exchange_name == 'whitebit':
        exchange_object = ccxt.whitebit()
        limit = 30
    elif exchange_name == 'latoken':
        exchange_object = ccxt.latoken()
        limit = 100
    elif exchange_name == 'phemex':
        exchange_object = ccxt.phemex()
        limit = 1000
    # elif exchange_name == 'bkex':
    #     exchange_object = ccxt.bkex()
    #     limit = 1000
    elif exchange_name == 'bigone':
        exchange_object = ccxt.bigone()
        limit = 500
    elif exchange_name == 'bitget':
        exchange_object = ccxt.bitget()
        limit = 300


    return exchange_object, limit

def get_all_exchanges():
    exchanges = ccxt.exchanges

    exclusion_list = ["lbank", "huobi", "okex", "okx", "hitbtc", "mexc", "gate", "binanceusdm",
        "binanceus", "bitfinex", "binancecoinm", "huobijp"]
    exchanges=[value for value in exchanges if value not in exclusion_list]
    return exchanges

    # if exchange_name == 'binance':
    #     exchange_object = ccxt.binance()
    #     limit = 10000
    # elif exchange_name == 'huobipro':
    #     exchange_object = ccxt.huobipro()
    #     limit = 1000
    # elif exchange_name == 'bybit':
    #     exchange_object = ccxt.bybit()
    #     limit = 20000
    # elif exchange_name == 'hitbtc3':
    #     exchange_object = ccxt.hitbtc3()
    #     limit = 10000
    # elif exchange_name == 'mexc':
    #     exchange_object = ccxt.mexc()
    #     limit = 2000
    # elif exchange_name == 'mexc3':
    #     exchange_object = ccxt.mexc3()
    #     limit = 2000
    # elif exchange_name == 'bitfinex':
    #     exchange_object = ccxt.bitfinex()
    #     limit = 10000
    # elif exchange_name == 'bitfinex2':
    #     exchange_object = ccxt.bitfinex2()
    #     limit = 10000
    # elif exchange_name == 'exmo':
    #     exchange_object = ccxt.exmo()
    #     limit = 3000
    # elif exchange_name == 'gateio':
    #     exchange_object = ccxt.gateio()
    #     limit = 20000
    # elif exchange_name == 'kucoin':
    #     exchange_object = ccxt.kucoin()
    #     limit = 20000
    # elif exchange_name == 'coinex':
    #     exchange_object = ccxt.coinex()
    #     limit = 20000
    # return exchange_object, limit

def get_active_trading_pairs_from_exchange(exchange_object):

    pairs = exchange_object.load_markets()
    active_pairs = []
    for pair in pairs.values():
        if pair['active']:
            active_pairs.append(pair['symbol'])
    return active_pairs

def get_ohlcv_kucoin(pair):
    exchange = ccxt.kucoin()
    exchange.load_markets()
    symbol = exchange.market(pair)['symbol']
    timeframe = '1d'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    return ohlcv

def get_ohlcv_okex(pair):
    exchange = ccxt.okex()
    exchange.load_markets()
    symbol = exchange.market(pair)['symbol']
    timeframe = '1d'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    return ohlcv
def get_trading_pairs(exchange_object):

    markets = exchange_object.load_markets()
    trading_pairs = list(markets.keys())
    return trading_pairs
def get_exchange_object2(exchange_name):
    exchange_objects = {
        # 'aax': ccxt.aax(),
        # 'aofex': ccxt.aofex(),
        'ace': ccxt.ace(),
        'alpaca': ccxt.alpaca(),
        'ascendex': ccxt.ascendex(),
        'bequant': ccxt.bequant(),
        # 'bibox': ccxt.bibox(),
        'bigone': ccxt.bigone(),
        'binance': ccxt.binance(),
        'binanceus': ccxt.binanceus(),
        'binancecoinm': ccxt.binancecoinm(),
        'binanceusdm':ccxt.binanceusdm(),
        'bit2c': ccxt.bit2c(),
        'bitbank': ccxt.bitbank(),
        'bitbay': ccxt.bitbay(),
        'bitbns': ccxt.bitbns(),
        'bitcoincom': ccxt.bitcoincom(),
        'bitfinex': ccxt.bitfinex(),
        'bitfinex2': ccxt.bitfinex2(),
        'bitflyer': ccxt.bitflyer(),
        'bitforex': ccxt.bitforex(),
        'bitget': ccxt.bitget(),
        'bithumb': ccxt.bithumb(),
        # 'bitkk': ccxt.bitkk(),
        'bitmart': ccxt.bitmart(),
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
        # 'bkex': ccxt.bkex(),
        'btcalpha': ccxt.btcalpha(),
        'btcbox': ccxt.btcbox(),
        'btcmarkets': ccxt.btcmarkets(),
        # 'btctradeim': ccxt.btctradeim(),
        'btcturk': ccxt.btcturk(),
        # 'btctradeua':ccxt.btctradeua(),
        # 'buda': ccxt.buda(),
        'bybit': ccxt.bybit(),
        # 'bytetrade': ccxt.bytetrade(),
        # 'cdax': ccxt.cdax(),
        'cex': ccxt.cex(),
        # 'chilebit': ccxt.chilebit(),
        'coinbase': ccxt.coinbase(),
        'coinbaseprime': ccxt.coinbaseprime(),
        'coinbasepro': ccxt.coinbasepro(),
        'coincheck': ccxt.coincheck(),
        # 'coinegg': ccxt.coinegg(),
        'coinex': ccxt.coinex(),
        # 'coinfalcon': ccxt.coinfalcon(),
        'coinsph':ccxt.coinsph(),
        # 'coinfloor': ccxt.coinfloor(),
        # 'coingi': ccxt.coingi(),
        # 'coinmarketcap': ccxt.coinmarketcap(),
        'cryptocom': ccxt.cryptocom(),
        'coinmate': ccxt.coinmate(),
        'coinone': ccxt.coinone(),
        'coinspot': ccxt.coinspot(),
        # 'crex24': ccxt.crex24(),
        'currencycom': ccxt.currencycom(),
        'delta': ccxt.delta(),
        'deribit': ccxt.deribit(),
        'digifinex': ccxt.digifinex(),
        # 'dsx': ccxt.dsx(),
        # 'dx': ccxt.dx(),
        # 'eqonex': ccxt.eqonex(),
        # 'eterbase': ccxt.eterbase(),
        'exmo': ccxt.exmo(),
        # 'exx': ccxt.exx(),
        # 'fcoin': ccxt.fcoin(),
        # 'fcoinjp': ccxt.fcoinjp(),
        # 'ftx': ccxt.ftx(),
        # 'flowbtc':ccxt.flowbtc(),
        'fmfwio': ccxt.fmfwio(),
        'gate':ccxt.gate(),
        'gateio': ccxt.gateio(),
        'gemini': ccxt.gemini(),
        # 'gopax': ccxt.gopax(),
        # 'hbtc': ccxt.hbtc(),
        'hitbtc': ccxt.hitbtc(),
        # 'hitbtc2': ccxt.hitbtc2(),
        # 'hkbitex': ccxt.hkbitex(),
        'hitbtc3': ccxt.hitbtc3(),
        'hollaex': ccxt.hollaex(),
        'huobijp': ccxt.huobijp(),
        'huobipro': ccxt.huobipro(),
        # 'ice3x': ccxt.ice3x(),
        'idex': ccxt.idex(),
        # 'idex2': ccxt.idex2(),
        'indodax': ccxt.indodax(),
        'independentreserve': ccxt.independentreserve(),

        # 'itbit': ccxt.itbit(),
        'kraken': ccxt.kraken(),
        'krakenfutures': ccxt.krakenfutures(),
        'kucoin': ccxt.kucoin(),
        'kuna': ccxt.kuna(),
        # 'lakebtc': ccxt.lakebtc(),
        'latoken': ccxt.latoken(),
        'lbank': ccxt.lbank(),
        # 'liquid': ccxt.liquid(),
        'luno': ccxt.luno(),
        'lykke': ccxt.lykke(),
        'mercado': ccxt.mercado(),
        'mexc':ccxt.mexc(),
        'mexc3' : ccxt.mexc3(),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        'okex': ccxt.okex(),
        'okex5':ccxt.okex5(),
        'okx':ccxt.okx(),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi(),
        'lbank2': ccxt.lbank2(),
        'blockchaincom': ccxt.blockchaincom(),
        # 'btcex': ccxt.btcex(),
        'kucoinfutures': ccxt.kucoinfutures(),
        # 'okex3': ccxt.okex3(),
        # 'p2pb2b': ccxt.p2pb2b(),
        # 'paribu': ccxt.paribu(),
        'phemex': ccxt.phemex(),
        'tokocrypto':ccxt.tokocrypto(),
        'poloniex': ccxt.poloniex(),
        'probit': ccxt.probit(),
        # 'qtrade': ccxt.qtrade(),
        # 'ripio': ccxt.ripio(),
        # 'southxchange': ccxt.southxchange(),
        # 'stex': ccxt.stex(),
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
        'wazirx':ccxt.wazirx({
        'rateLimit': 300,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'whitebit': ccxt.whitebit(),
        # 'xbtce': ccxt.xbtce(),
        # 'xena': ccxt.xena(),
        'yobit': ccxt.yobit(),
        'zaif': ccxt.zaif(),
        # 'zb': ccxt.zb(),
        'zonda':ccxt.zonda(),
        'bingx': ccxt.bingx()
        # 'xt': ccxt.xt()

    }
    exchange_object = exchange_objects.get(exchange_name)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    return exchange_object
def get_exchange_object(exchange_name):
    exchange_objects = {
        'binance': ccxt.binance(),
        'huobipro': ccxt.huobipro(),
        'bybit': ccxt.bybit(),
        'hitbtc3': ccxt.hitbtc3(),
        'mexc': ccxt.mexc(),
        'mexc3': ccxt.mexc3(),
        'bitfinex': ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'exmo': ccxt.exmo(),
        'gateio': ccxt.gateio(),
        'kucoin': ccxt.kucoin(),
        'coinex': ccxt.coinex(),
        'bitstamp': ccxt.bitstamp()}
    return exchange_objects.get(exchange_name)


def get_exchange_object_for_binance_via_vpn():
    exchange = ccxt.binance({
        'apiKey': 'your-api-key',
        'secret': 'your-api-secret',
        'timeout': 30000,
        'enableRateLimit': True,
        'proxy': 'https://your-vpn-server.com:port',
        'proxyCredentials': {
            'username': 'your-username',
            'password': 'your-password'
        }
    })
def get_ohlcv_from_huobi_pro():
    # create a new instance of the CCXT Huobi Pro exchange
    exchange = ccxt.huobipro()

    # retrieve a list of all symbols on the Huobi Pro exchange
    symbols = exchange.load_markets()

    # loop through each symbol and retrieve its OHLCV data
    for symbol in symbols:
        candles = exchange.fetch_ohlcv(symbol, '1d')
        df = pd.DataFrame(candles, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)

        # print the OHLCV data for the symbol
        print(f"Symbol: {symbol}")
        for candle in candles:
            print(
                f"Time: {candle[0]}, Open: {candle[1]}, High: {candle[2]}, Low: {candle[3]}, Close: {candle[4]}, Volume: {candle[5]}")

# def get_huobi_ohlcv():
#     # create a new instance of the Huobi API client
#     # create a new instance of the Huobi API client
#     # client = GenericClient(api_key='your_api_key', secret_key='your_secret_key')
#
#     # retrieve a list of all symbols on the Huobi Pro exchange
#     symbols = client.get_symbols()
#
#     # create an empty DataFrame to store the OHLCV data
#     df = pd.DataFrame()
#
#     # loop through each symbol and retrieve its OHLCV data
#     for symbol in symbols:
#         # retrieve the OHLCV data for the symbol
#         candles = client.get_candles(symbol['symbol'], '1day')
#
#         # create a DataFrame for the OHLCV data
#         candles_df = pd.DataFrame(candles, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
#         candles_df['Timestamp'] = pd.to_datetime(candles_df['Timestamp'], unit='s')
#         candles_df.set_index('Timestamp', inplace=True)
#         candles_df.columns = [f"{symbol['symbol']}_{col}" for col in candles_df.columns]
#
#         # merge the OHLCV data for the symbol into the main DataFrame
#         df = pd.concat([df, candles_df], axis=1, sort=True)
#
#     return df
def check_if_stable_coin_is_the_first_part_of_ticker(trading_pair):
    trading_pair_has_stable_coin_name_as_its_first_part=False
    stablecoin_tickers = [
        "USDT/", "USDC/", "BUSD/", "DAI/", "FRAX/", "TUSD/", "USDP/", "USDD/",
        "GUSD/", "XAUT/", "USTC/", "EURT/", "LUSD/", "ALUSD/", "EURS/", "USDX/",
        "MIM/", "sEUR/", "WBTC/", "sGBP/", "sJPY/", "sKRW/", "sAUD/", "GEM/",
        "sXAG/", "sXAU/", "sXDR/", "sBTC/", "sETH/", "sCNH/", "sCNY/", "sHKD/",
        "sSGD/", "sCHF/", "sCAD/", "sNZD/", "sLTC/", "sBCH/", "sBNB/", "sXRP/",
        "sADA/", "sLINK/", "sXTZ/", "sDOT/", "sFIL/", "sYFI/", "sCOMP/", "sAAVE/",
        "sSNX/", "sMKR/", "sUNI/", "sBAL/", "sCRV/", "sLEND/", "sNEXO/", "sUMA/",
        "sMUST/", "sSTORJ/", "sREN/", "sBSV/", "sDASH/", "sZEC/", "sEOS/", "sXTZ/",
        "sATOM/", "sVET/", "sTRX/", "sADA/", "sDOGE/", "sDGB/","UUSD"
    ]

    for first_part_in_trading_pair in stablecoin_tickers:
        if first_part_in_trading_pair in trading_pair:
            trading_pair_has_stable_coin_name_as_its_first_part=True
            break
        else:
            continue
    return trading_pair_has_stable_coin_name_as_its_first_part
def return_list_of_all_stablecoin_bases_with_slash():
    stablecoin_bases_with_slash_list = [
        "USDT/", "USDC/", "BUSD/", "DAI/", "FRAX/", "TUSD/", "USDP/", "USDD/",
        "GUSD/", "XAUT/", "USTC/", "EURT/", "LUSD/", "ALUSD/", "EURS/", "USDX/",
        "MIM/", "sEUR/", "WBTC/", "sGBP/", "sJPY/", "sKRW/", "sAUD/", "GEM/",
        "sXAG/", "sXAU/", "sXDR/", "sBTC/", "sETH/", "sCNH/", "sCNY/", "sHKD/",
        "sSGD/", "sCHF/", "sCAD/", "sNZD/", "sLTC/", "sBCH/", "sBNB/", "sXRP/",
        "sADA/", "sLINK/", "sXTZ/", "sDOT/", "sFIL/", "sYFI/", "sCOMP/", "sAAVE/",
        "sSNX/", "sMKR/", "sUNI/", "sBAL/", "sCRV/", "sLEND/", "sNEXO/", "sUMA/",
        "sMUST/", "sSTORJ/", "sREN/", "sBSV/", "sDASH/", "sZEC/", "sEOS/", "sXTZ/",
        "sATOM/", "sVET/", "sTRX/", "sADA/", "sDOGE/", "sDGB/","UUSD"
    ]
    return stablecoin_bases_with_slash_list

def get_exchanges_for_trading_pair(df, trading_pair):
    exchanges = []
    for col in df.columns:
        if trading_pair in df[col].values:
            exchanges.append(col)
    return exchanges
def remove_leveraged_pairs(filtered_pairs):
    levereged_tokens_string_list=["3S", "3L", "2S", "2L", "4S", "4L", "5S", "5L","6S", "6L"]
    for token in levereged_tokens_string_list:
        filtered_pairs = [pair for pair in filtered_pairs if token not in pair]
    return filtered_pairs

def remove_futures_with_expiration_and_options(filtered_pairs):
    futures_with_expiration_and_options_ends_with_this_string=["-P", "-C", "-M",":P", ":C", ":M"]
    for ending in futures_with_expiration_and_options_ends_with_this_string:
        filtered_pairs = [pair for pair in filtered_pairs if ending not in pair]
    return filtered_pairs


def add_exchange_count(df,exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names


    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df = result_df.append({'trading_pair': trading_pair, 'exchange_count': exchange_count},
                                     ignore_index=True)

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df

def add_exchange_count_without_append_to_df(df, exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names

    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df.loc[trading_pair] = [trading_pair, exchange_count]

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df
def get_exchanges_for_trading_pairs(df):
    # Create a set of all unique trading pairs in the DataFrame
    trading_pairs = set(df.values.flatten())

    # Create a dictionary to store the exchanges where each trading pair is traded
    trading_pair_exchanges = {}
    for pair in trading_pairs:
        print(pair)
        exchanges = [col for col in df.columns if pair in df[col].values]
        trading_pair_exchanges[pair] = '_'.join(exchanges)

    # Create a new DataFrame from the trading_pair_exchanges dictionary
    new_df = pd.DataFrame.from_dict(trading_pair_exchanges, orient='index', columns=['exchanges_where_pair_is_traded'])
    new_df.index.name = 'trading_pair'

    return new_df
def extract_unique_exchanges(row):
    exchanges = row['exchanges_where_pair_is_traded'].split('_')
    unique_exchanges = []
    for exchange in exchanges:
        is_unique = True
        for e in unique_exchanges:
            print("inside for loop")
            if exchange != e and e.startswith(exchange):
                is_unique = False
                break
        if is_unique:
            unique_exchanges.append(exchange)
        print("unique_exchanges")
        print(unique_exchanges)
    return '_'.join(unique_exchanges)
def get_exchange_map_from_exchange_id_to_exchange_name(exchange_ids):
    exchange_map = {}
    for exchange_id in exchange_ids:
        exchange_object=get_exchange_object2(exchange_id)
        exchange_name = exchange_object.name
        exchange_map[exchange_id] = exchange_name
    return exchange_map

def add_exchange_count2(df, exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names

    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df.loc[len(result_df)] = [trading_pair, exchange_count]

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df
def remove_trading_pairs_which_contain_stablecoin_as_base(filtered_pairs,stablecoin_bases_with_slash_list):
    filtered_pairs = [pair for pair in filtered_pairs if
                      not any(pair.startswith(ticker) for ticker in stablecoin_bases_with_slash_list)]
    return filtered_pairs
if __name__=="__main__":

    exchanges_list=ccxt.exchanges

    exclusion_list = ["lbank", "huobi", "okex", "okx", "hitbtc", "mexc", "gate", "binanceusdm",
        "binanceus", "bitfinex", "binancecoinm", "huobijp"]
    exchanges_list=[value for value in exchanges_list if value not in exclusion_list]
    print("exchanges_list")
    print(exchanges_list)
    for exchange_name in exchanges_list:
        try:
            print(f"fethcing info for {exchange_name}")
            trading_pair="BTC/USDT"
            # timeframe="1d"
            # limit_of_daily_candles=1200
            exchange_object=get_exchange_object6(exchange_name)
            # ohlcv_df=fetch_entire_ohlcv(exchange_object,
            #                                exchange_name,
            #                                trading_pair,
            #                                timeframe,limit_of_daily_candles)

            markets = np.nan
            try:
                markets = exchange_object.load_markets()
            except:
                traceback.print_exc()
            trading_pair_can_be_traded_with_margin=if_margin_true_for_an_asset(markets, trading_pair)

            # print("ohlcv_df.head(10).to_string()")
            # print(ohlcv_df.head(10).to_string())
            #
            # print("len(ohlcv_df)")
            # print(len(ohlcv_df))

            print(f"trading_pair_can_be_traded_with_margin on {exchange_object}")
            print(trading_pair_can_be_traded_with_margin)
        except:
            traceback.print_exc()

    # list_of_shortable_assets_for_binance=get_shortable_assets_for_binance()
    # print("list_of_shortable_assets_for_binance")
    # print(list_of_shortable_assets_for_binance)
    #
    # list_of_shortable_assets_for_huobipro = get_huobi_margin_pairs()
    # print("list_of_shortable_assets_for_huobipro")
    # print(list_of_shortable_assets_for_huobipro)
    #
    # list_of_shortable_assets_for_gateio = get_shortable_assets_for_gateio()
    # print("list_of_shortable_assets_for_gateio")
    # print(list_of_shortable_assets_for_gateio)


    # print("get_market_type('huobipro', 'BTC/USDT')")
    # for exchange_name in ['binance','huobipro','bybit','poloniex',
    #                         'mexc3',
    #                         'bitfinex2','exmo','gateio','kucoin','coinex']:
        # if exchange_name!="hitbtc3":
        #     continue
        # try:
    #         print("exchange_name")
    #         print (exchange_name)
    #         # print(get_asset_type(exchange_name, 'BTC/USDT'))
    #         exchange_object=get_exchange_object(exchange_name)
    #         markets=exchange_object.load_markets()
    #         trading_pair='BTC/USDT'
    #         timeframe='1d'
    #         exchange_object1,limit_of_daily_candles=get_limit_of_daily_candles_original_limits(exchange_name)
    #         print(f"limit_of_daily_candles_for{exchange_name}")
    #         print(limit_of_daily_candles)
    #         # maker_tiered_fees,taker_tiered_fees=get_maker_taker_fees_for_huobi(exchange_object)
    #         # # taker_tiered_fees = get_t(exchange_object)
    #         # print(f"maker_tiered_fees for {exchange_name}")
    #         # print(maker_tiered_fees)
    #         # print(f"taker_tiered_fees for {exchange_name}")
    #         # print(taker_tiered_fees)
    #         list_of_all_symbols_from_exchange = exchange_object.symbols
    # #
    #         for trading_pair in  list_of_all_symbols_from_exchange:
    #             # print("trading_pair")
    #             # print(trading_pair)
    #             if trading_pair!='BTC/USDT':
    #                 continue
    #             # ohlcv_df=\
    #             #     fetch_entire_ohlcv(exchange_object,
    #             #                        exchange_name,
    #             #                        trading_pair,
    #             #                        timeframe,limit_of_daily_candles)
    #             # print("final_ohlcv_df")
    #             # print(ohlcv_df)
    #             asset_type=get_asset_type2(markets,trading_pair)
    #             if asset_type=="spot":
    #
    #                 url=get_exchange_url(exchange_name,exchange_object,trading_pair)
    #                 print(f"url_for_swap for {exchange_name}")
    #                 print(url)
    #     except:
    #         traceback.print_exc()

    # trading_pair="BTC/USDT"
    # timeframe="1d"
    # ohlcv_df=fetch_bybit_ohlcv(trading_pair, timeframe)
    # print("ohlcv_df")
    # print(ohlcv_df)

    #
    # print("get_market_type('huobipro', 'BTC/USDT')")
    # for exchange_name in ['binance', 'huobipro', 'bybit',
    #                       'hitbtc3', 'mexc', 'mexc3', 'bitfinex',
    #                       'bitfinex2', 'exmo', 'gateio', 'kucoin', 'coinex']:
    #
    #     exchange = getattr(ccxt, exchange_name)()
    #     markets=exchange.load_markets()
    #     print(get_asset_type2(markets, 'BTC/USDT'))
    #     print(get_fees(markets, 'BTC/USDT'))
    # maker_fee, taker_fee=get_huobipro_fees("1INCH/USDT:USDT")

    # print(maker_fee)
    # print(taker_fee)
    # ohlcv_df=get_ohlcv_kucoin("1INCH/USDT")
    # print("ohlcv_df")
    # print(ohlcv_df)
    # exchange = ccxt.gateio()
    # ohlcv_data = exchange.fetch_ohlcv('ANKR/USDT', timeframe='1d')
    # print("ohlcv_data for ANKR/USDT")
    # print(ohlcv_data)
    #
    # time.sleep(50000)
    # for exchange_name in ['binance','huobipro','bybit',
    #                         'hitbtc3','mexc','mexc3','bitfinex',
    #                         'bitfinex2','exmo','gateio','kucoin','coinex']:
    #     exchange_object, limit=get_exchange_object_and_limit_of_daily_candles(exchange_name)
    #     exchange_object.load_markets()
    #     # symbol = exchange_object.market(pair)['symbol']
    #     timeframe = '1d'
    #     ohlcv = exchange_object.fetch_ohlcv("BSV/USDT", timeframe)
    #     # ohlcv = get_ohlcv_okex("BTC/USDT")
    #     print(f"ohlcv for {exchange_name}")
    #     print(ohlcv)

    # active_trading_pairs_list=get_active_trading_pairs_from_huobipro()
    # print("active_trading_pairs_list")
    # print(active_trading_pairs_list)
    # for symbol in active_trading_pairs_list:
    #     exchange = ccxt.huobipro()
    #     ohlcv_df=fetch_huobipro_ohlcv(symbol, exchange, timeframe='1d')
    #     trading_pair = symbol.replace("/", "_")
    #
    #     ohlcv_df['ticker'] = symbol
    #     ohlcv_df['exchange'] = "huobipro"
    #
    #     print("ohlcv_df")
    #     print(ohlcv_df)
    # zeros_in_number=count_zeros_number_with_e_notaton_is_acceptable(9.701e-05)
    # print("zeros_in_number")
    # print(zeros_in_number)
    # get_ohlcv_from_huobi_pro()
    # ohlcv_df=get_huobi_ohlcv()
    # print("ohlcv_df")
    # print(ohlcv_df)
    # db_with_trading_pair_statistics="db_with_trading_pair_statistics"
    # table_name_where_exchanges_will_be_with_all_available_trading_pairs="available_trading_pairs_for_each_exchange"
    # # table_with_strings_where_each_pair_is_traded="exchanges_where_each_pair_is_traded"
    # engine_for_db_with_trading_pair_statistics, connection_to_db_with_trading_pair_statistics=\
    #     connect_to_postgres_db_with_deleting_it_first(db_with_trading_pair_statistics)
    # list_of_all_exchanges=get_all_exchanges()
    # data_dict={}
    # # exchange_map=get_exchange_map_from_exchange_id_to_exchange_name(list_of_all_exchanges)
    # # print("exchange_map")
    # # print(exchange_map)
    # for exchange_name in list_of_all_exchanges:
    #     try:
    #         exchange_object=get_exchange_object2(exchange_name)
    #         list_of_trading_pairs_for_one_exchange=get_trading_pairs(exchange_object)
    #
    #         print(f"list_of_trading_pairs_for_one_exchange for {exchange_name}" )
    #         print(list_of_trading_pairs_for_one_exchange)
    #         print(f"number of all pairs for {exchange_name} is  {len(list_of_trading_pairs_for_one_exchange)}")
    #
    #         filtered_pairs = [pair for pair in list_of_trading_pairs_for_one_exchange if "/USDT" in pair]
    #         print(f"filtered_pairs for {exchange_name}")
    #         print(filtered_pairs)
    #         print(f"number of all usdt pairs for {exchange_name} is  {len(filtered_pairs)}")
    #         stablecoin_bases_with_slash_list=return_list_of_all_stablecoin_bases_with_slash()
    #         filtered_pairs =\
    #             remove_trading_pairs_which_contain_stablecoin_as_base(
    #                 filtered_pairs,
    #                 stablecoin_bases_with_slash_list)
    #         print(filtered_pairs)
    #         filtered_pairs=remove_leveraged_pairs(filtered_pairs)
    #         filtered_pairs=remove_futures_with_expiration_and_options(filtered_pairs)
    #         print(f"number of all usdt pairs without stablecoin base and without levereged tokens "
    #               f"for {exchange_name} is  {len(filtered_pairs)}")
    #         data_dict[exchange_name] = filtered_pairs
    #
    #     except:
    #         traceback.print_exc()
    # df_with_trading_pairs_for_each_exchange = pd.DataFrame.from_dict(data_dict, orient='index')
    # df_with_trading_pairs_for_each_exchange = df_with_trading_pairs_for_each_exchange.transpose()
    # print("df_with_trading_pairs")
    # print(df_with_trading_pairs_for_each_exchange.head(200).to_string())
    # trading_pair="PIAS/USDT"
    # exchanges_for_trading_pair_list=get_exchanges_for_trading_pair(df_with_trading_pairs_for_each_exchange)
    # print("exchanges_for_"trading_pair_list")
    # print(exchanges_for_tra"ding_pair_list)


    # df_with_strings_where_each_pair_is_traded=get_exchanges_for_trading_pairs(df_with_trading_pairs_for_each_exchange)

    # df_with_strings_where_each_pair_is_traded_plus_exchange_count=\
    #     add_exchange_count2(df_with_strings_where_each_pair_is_traded, exchange_map)

    # apply the function to each row and create the new column
    # df_with_strings_where_each_pair_is_traded['unique_exchanges_where_pair_is_traded'] =\
    #     df_with_strings_where_each_pair_is_traded.apply(extract_unique_exchanges, axis=1)

    # df_with_trading_pairs_for_each_exchange.to_sql(table_name_where_exchanges_will_be_with_all_available_trading_pairs,
    #                engine_for_db_with_trading_pair_statistics,
    #                if_exists='replace')
    # df_with_strings_where_each_pair_is_traded.to_sql(table_with_strings_where_each_pair_is_traded,
    #                                                engine_for_db_with_trading_pair_statistics,
    #                                                if_exists='replace')