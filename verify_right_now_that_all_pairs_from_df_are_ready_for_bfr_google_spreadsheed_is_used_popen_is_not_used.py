from statistics import mean
# from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_ath_breakout
# from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_atl_breakout
import pandas as pd
# from shitcoins_with_different_models import pd.read_sql_query
import sys
# from pytz import timezone
from datetime import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# import streamlit as st
from subprocess import Popen, PIPE
import subprocess
from get_info_from_load_markets import get_exchange_object6
import ccxt
import streamlit as st
# from current_search_for_tickers_with_rebound_situations_off_atl import check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level
# from current_search_for_tickers_with_rebound_situations_off_atl import check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level
# from current_search_for_tickers_with_rebound_situations_off_ath import check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level
# from current_search_for_tickers_with_rebound_situations_off_ath import check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level
# from current_search_for_tickers_with_rebound_situations_off_atl import get_timestamp_of_bpu2
# from current_search_for_tickers_with_fast_breakout_of_atl import calculate_atr_without_paranormal_bars_from_numpy_array
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import os
# from current_search_for_tickers_with_rebound_situations_off_atl import get_timestamp_of_bpu2
# from current_search_for_tickers_with_rebound_situations_off_atl import get_ohlc_of_bpu2
# from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
# from current_search_for_tickers_with_fast_breakout_of_atl import get_date_with_and_without_time_from_timestamp
import time
import traceback
# from current_search_for_tickers_with_rebound_situations_off_atl import get_volume_of_bpu2
# from current_search_for_tickers_with_rebound_situations_off_atl import calculate_advanced_atr
# from before_entry_current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_current_price_of_asset
# from sqlalchemy_utils import create_database, database_exists
# import db_config
# from sqlalchemy import inspect
# from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
# from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import get_list_of_tables_in_db
import datetime
# from build_entire_df_of_assets_which_will_be_used_for_position_entry import build_entire_df_of_assets_which_will_be_used_for_position_entry
import numpy as np
# from current_search_for_tickers_with_rebound_situations_off_atl import get_last_close_price_of_asset
# from fetch_historical_ohlcv_data_for_one_USDT_pair_for_1D_without_inserting_into_db import fetch_one_ohlcv_table
# from update_todays_USDT_pairs_where_models_have_formed_for_1D_next_bar_print_utc_time_00 import get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table
import math
list_of_inactive_pairs=[]
list_of_newly_added_trading_pairs=[]

def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
def add_time_of_next_candle_print_to_df(data_df):
    try:
        # Set the timezone for Moscow
        # moscow_tz = timezone('Europe/Moscow')
        # almaty_tz = timezone('Asia/Almaty')
        data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
        data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
        # Convert the "open_time" column from UTC to Moscow time
        data_df['open_time_msk'] =\
            data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert('Europe/Moscow')

        data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')

        # Convert the "open_time_datatime_format" column from UTC to Almaty time
        data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')

        # Create a new column called "open_time_almaty_time" that contains the time in string format
        data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
    except:
        traceback.print_exc()

def check_volume(trading_pair,
                 min_volume_over_these_many_last_days,
                 data_df,
                 min_volume_in_bitcoin,
                 last_bitcoin_price):
    """
    Checks if the trading pair has enough volume over the specified number of days
    and if the volume is not less than n prices of bitcoin for USD pairs or the minimum volume for BTC pairs.

    Args:
        trading_pair (str): The trading pair to check for volume.
        min_volume_over_these_many_last_days (int): The number of days to look back for volume.
        data_df (pandas.DataFrame): The DataFrame containing the trading data.
        min_volume_in_bitcoin (float): The minimum volume in bitcoin to be considered sufficient.
        last_bitcoin_price (float): The last price of bitcoin.

    Returns:
        asset_has_enough_volume (bool): True if the trading pair has enough volume, False otherwise.
    """

    data_df_n_days_slice = data_df.iloc[:-1].tail(min_volume_over_these_many_last_days).copy()
    data_df_n_days_slice["volume_by_close"] = data_df_n_days_slice["volume"] * data_df_n_days_slice["close"]

    min_volume_over_last_n_days_for_usd_pairs = min(data_df_n_days_slice["volume_by_close"])
    min_volume_over_last_n_days_for_btc_pairs = min(data_df_n_days_slice["volume_by_close"])

    asset_has_enough_volume = True

    if "_BTC" not in trading_pair:
        if min_volume_over_last_n_days_for_usd_pairs < min_volume_in_bitcoin * last_bitcoin_price:
            print(f"{trading_pair} discarded due to low volume")
            asset_has_enough_volume = False
    else:
        if min_volume_over_last_n_days_for_btc_pairs < min_volume_in_bitcoin:
            print(f"{trading_pair} discarded due to low volume")
            asset_has_enough_volume = False

    return asset_has_enough_volume
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
def if_margin_true_for_an_asset(markets, trading_pair):
    market = markets[trading_pair]
    print(f" markets[{trading_pair}]")
    print(market)
    return market['margin']
def convert_index_to_unix_timestamp(df):
    # convert the index to datetime object
    df.index = pd.to_datetime(df.index)

    # convert the datetime object to Unix timestamp in milliseconds
    df.index = df.index.astype(int) // 10**6
def ohlcVolume(x):
    if len(x):
        ohlc={ "open":x["open"][0],"high":max(x["high"]),"low":min(x["low"]),"close":x["close"][-1],"volume":sum(x["volume"])}
        return pd.Series(ohlc)
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
def get_maker_taker_fees_for_huobi(exchange_object):
    fees = exchange_object.describe()['fees']['trading']
    maker_fee = fees['maker']
    taker_fee = fees['taker']
    return maker_fee, taker_fee
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


def check_exchange_object_is_none(exchange_object):
    if exchange_object is None:
        return True
    else:
        return False

def get_asset_type2(markets, trading_pair):
    market = markets[trading_pair]
    return market['type']
def get_fees(markets, trading_pair):
    market=markets[trading_pair]
    # pprint.pprint(market)
    return market['maker'], market['taker']
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
        'bitstamp1': ccxt.bitstamp(),
        # 'bittrex': ccxt.bittrex(),
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
        'mexc3' : ccxt.mexc(),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        'okex': ccxt.okx(),
        'okex5':ccxt.okx(),
        'okx':ccxt.okx(),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi(),
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
        exchange_object = ccxt.bitstamp()
        limit = 1000
    elif exchange_name == 'bittrex':
        # exchange_object = ccxt.bittrex()
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
        # exchange_object = ccxt.btctradeua()
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
        # exchange_object = ccxt.coinbaseprime()
        limit = 1000
    elif exchange_name == 'coinbasepro':
        exchange_object = ccxt.coinbasepro()
        limit = 1000
    elif exchange_name == 'coincheck':
        exchange_object = ccxt.coincheck()
        limit = 1000
    elif exchange_name == 'coinfalcon':
        # exchange_object = ccxt.coinfalcon()
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
        exchange_object = ccxt.huobi()
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
        exchange_object = ccxt.mexc({
        'rateLimit': 501,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 1000
    elif exchange_name == 'mexc3':
        exchange_object = ccxt.mexc()
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
        exchange_object = ccxt.okx()
        limit = 100
    elif exchange_name == 'okex':
        # exchange_object = ccxt.okex()
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
        # exchange_object = ccxt.tidex()
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
        exchange_object = ccxt.lbank()
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

def insert_into_df_whether_swap_contract_is_also_available_for_swap(data_df,exchange_object,markets,trading_pair_base_slash_underscore_without_exchange):
    spot_asset_also_available_as_swap_contract_on_the_same_exchange=False
    try:
        probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too = trading_pair_base_slash_underscore_without_exchange.replace("_",
                                                                                                                   "/") + ":USDT"
        print("probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too")
        print(probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too)
        if probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too in exchange_object.symbols:
            print(
                f"{probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too} in exchange_object.symbols")

            if get_asset_type2(markets,
                               probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too) == "swap":
                spot_asset_also_available_as_swap_contract_on_the_same_exchange=True
                print(f'{trading_pair_base_slash_underscore_without_exchange.replace("_", "/")} has also a '
                      f'swap contract called {probable_swap_contract_name_of_symbol_which_might_be_in_symbols_of_the_exchange_too} on {exchange_object}')
        else:
            spot_asset_also_available_as_swap_contract_on_the_same_exchange = False
    except:
        traceback.print_exc()

    return spot_asset_also_available_as_swap_contract_on_the_same_exchange

def fetch_one_ohlcv_table(ticker,timeframe,last_bitcoin_price):

    exchange=ticker.split("_on_")[1]
    base_underscore_quote=ticker.split("_on_")[0]
    trading_pair=base_underscore_quote.replace("_","/")

    # print("exchange=",exchange)

    exchange_object=False
    limit_of_daily_candles=np.nan
    data_df=pd.DataFrame()

    # active_trading_pairs_list_from_huobipro=[]
    try:
        # active_trading_pairs_list_from_huobipro=[]
        # if exchange in ["huobipro"]:
        #     active_trading_pairs_list_from_huobipro = get_active_trading_pairs_from_huobipro()
        exchange_object, limit_of_daily_candles=\
            get_limit_of_daily_candles_original_limits(exchange)




        try:
            if check_exchange_object_is_none(exchange_object):
                exchange_object=get_exchange_object2(exchange)
                limit_of_daily_candles=1000
        except:
            print(f"2problem with {exchange}")
            traceback.print_exc()

        # exchange_object = getattr ( ccxt , exchange ) ()
        exchange_object.enableRateLimit = True

    except:
        traceback.print_exc()


    try:
        markets=exchange_object.load_markets ()

        asset_type=''
        if_margin_true_for_an_asset_bool=''
        try:
            asset_type=get_asset_type2(markets, trading_pair.replace("_", "/"))
            try:
                if_margin_true_for_an_asset_bool=if_margin_true_for_an_asset(markets, trading_pair.replace("_", "/"))
            except:
                traceback.print_exc()
            print(f"asset_type for {trading_pair} on {exchange}")


        except:
            traceback.print_exc()

        # Fetch the most recent 100 days of data for latoken exchange
        try:
            # exchange latoken has a specific limit of one request number of candles
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

        try:
            data_df=fetch_entire_ohlcv(exchange_object,exchange,trading_pair,timeframe,limit_of_daily_candles)
        except:
            traceback.print_exc()


        print ( "=" * 80 )
        print ( f'ohlcv for {trading_pair} on exchange {exchange}\n' )
        print ( data_df )





        trading_pair=trading_pair.replace("/","_")

        data_df['ticker'] = trading_pair
        data_df['exchange'] = exchange
        # print("markets[trading_pair]")

        # print(markets[trading_pair])


        #if trading pair is traded with margin
        try:
            data_df['trading_pair_is_traded_with_margin'] = if_margin_true_for_an_asset_bool
        except:
            data_df['trading_pair_is_traded_with_margin'] = np.nan

        # add asset type to df
        try:
            data_df['asset_type'] = asset_type
        except:
            data_df['asset_type'] = np.nan
            traceback.print_exc()

        # add maker and taker fees
        try:
            if exchange!='huobipro':
                maker_fee, taker_fee=get_fees(markets, trading_pair.replace("_","/"))
                data_df['maker_fee'] = maker_fee
                data_df['taker_fee'] = taker_fee

        except:
            data_df['maker_fee'] = np.nan
            data_df['taker_fee'] = np.nan
            traceback.print_exc()

        try:
            if exchange == "huobipro":
                maker_fee, taker_fee = get_maker_taker_fees_for_huobi(exchange_object)
                data_df['maker_fee'] = maker_fee
                data_df['taker_fee'] = taker_fee
                print("fees for huobi pro")
                print("maker_fee for huobi")
                print(maker_fee)
                print("taker_fee for huobi")
                print(taker_fee)
        except:
            data_df['maker_fee'] = np.nan
            data_df['taker_fee'] = np.nan
            traceback.print_exc()



        # add url of trading pair to df
        try:
            # market = markets[trading_pair.replace("_", "/")]
            # market_id = market['id']
            url_of_trading_pair =\
                get_exchange_url(exchange, exchange_object, trading_pair.replace("_", "/"))
            data_df['url_of_trading_pair'] = url_of_trading_pair
        except:
            data_df['url_of_trading_pair'] = np.nan
            traceback.print_exc()

        spot_asset_is_also_available_as_swap_contract_on_the_same_exchange=False
        if asset_type == "spot":
            try:
                # from fetch_additional_historical_USDT_pairs_for_1D_without_deleting_primary_db_and_without_deleting_db_with_low_volume import \
                #     insert_into_df_whether_swap_contract_is_also_available_for_swap
                spot_asset_is_also_available_as_swap_contract_on_the_same_exchange = insert_into_df_whether_swap_contract_is_also_available_for_swap(
                    data_df,
                    exchange_object,
                    markets,
                    trading_pair)
            except:
                traceback.print_exc()

        try:
            data_df[
                'spot_asset_also_available_as_swap_contract_on_same_exchange'] = spot_asset_is_also_available_as_swap_contract_on_the_same_exchange
        except:
            data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = np.nan
            traceback.print_exc()

        try:
            if spot_asset_is_also_available_as_swap_contract_on_the_same_exchange:
                data_df["url_of_swap_contract_if_it_exists"] = get_perpetual_swap_url(exchange,
                                                                                      trading_pair.replace("_", "/"))
                print("url_swap_added")
            else:
                data_df["url_of_swap_contract_if_it_exists"] = "swap_of_spot_asset_does_not_exist"
        except:
            traceback.print_exc()

        # add url of trading pair to df
        if asset_type=='swap':
            try:

                url_of_trading_pair = \
                    get_perpetual_swap_url(exchange, trading_pair.replace("_", "/"))
                data_df['url_of_trading_pair'] = url_of_trading_pair
                data_df['trading_pair_is_traded_with_margin'] = True
            except:
                data_df['url_of_trading_pair'] = np.nan
                traceback.print_exc()

        try:
            data_df[
                'spot_asset_also_available_as_swap_contract_on_same_exchange'] = spot_asset_is_also_available_as_swap_contract_on_the_same_exchange
        except:
            data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = np.nan
            traceback.print_exc()

        try:
            if spot_asset_is_also_available_as_swap_contract_on_the_same_exchange:
                data_df["url_of_swap_contract_if_it_exists"] = get_perpetual_swap_url(exchange,
                                                                                      trading_pair.replace("_", "/"))
                print("url_swap_added")
            else:
                data_df["url_of_swap_contract_if_it_exists"] = "swap_of_spot_asset_does_not_exist"
        except:
            traceback.print_exc()



        current_timestamp=time.time()
        last_timestamp_in_df=data_df.tail(1).index.item()/1000.0
        print("current_timestamp=",current_timestamp)
        print("data_df.tail(1).index.item()=",data_df.tail(1).index.item()/1000.0)


        #-----------------------------------------
        #-------------------------------------------
        # #проверить, что объем за последние n дней не меньше, чем 4 цены биткойна
        min_volume_over_these_many_last_days = 7
        min_volume_in_bitcoin = 3


        asset_has_enough_volume = check_volume(trading_pair,
                                               min_volume_over_these_many_last_days,
                                               data_df,
                                               min_volume_in_bitcoin,
                                               last_bitcoin_price)
        if not asset_has_enough_volume:
            asset_has_enough_volume=False

        data_df["Timestamp"] = (data_df.index)

        try:
            data_df["open_time"] = data_df["Timestamp"].apply(lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print("error_message")
            traceback.print_exc()

        data_df['Timestamp'] = data_df["Timestamp"] / 1000.0

        data_df.index = range(0, len(data_df))


        data_df["exchange"] = exchange


        data_df.set_index("open_time")

        add_time_of_next_candle_print_to_df(data_df)
        print("2program got here")



        print(f"{trading_pair} was added to df")
        list_of_newly_added_trading_pairs.append(f"{trading_pair}_on_{exchange}")

        print("data_df.index")
        print(data_df.index)

        if asset_has_enough_volume==True:

            return data_df
        else:

            return data_df
    except:
        traceback.print_exc()


def get_date_with_and_without_time_from_timestamp(timestamp):

    try:
        open_time = \
            datetime.datetime.fromtimestamp ( timestamp  )
        # last_timestamp = historical_data_for_crypto_ticker_df["Timestamp"].iloc[-1]
        # last_date_with_time = historical_data_for_crypto_ticker_df["open_time"].iloc[-1]
        # print ( "type(last_date_with_time)\n" , type ( last_date_with_time ) )
        # print ( "last_date_with_time\n" , last_date_with_time )
        date_with_time = open_time.strftime ( "%Y/%m/%d %H:%M:%S" )
        date_without_time = date_with_time.split ( " " )
        print ( "date_with_time\n" , date_without_time[0] )
        date_without_time = date_without_time[0]
        print ( "date_without_time\n" , date_without_time )
        # date_without_time = date_without_time.replace ( "/" , "_" )
        # date_with_time = date_with_time.replace ( "/" , "_" )
        # date_with_time = date_with_time.replace ( " " , "__" )
        # date_with_time = date_with_time.replace ( ":" , "_" )
        return date_with_time,date_without_time
    except:
        return timestamp,timestamp
def get_last_close_price_of_asset(ohlcv_table_df):
    last_close_price=ohlcv_table_df["close"].iat[-1]
    return last_close_price
def calculate_advanced_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):
    # calcualte atr over 5 days before bpu2. bpu2 is not included

    list_of_true_ranges = []
    for row_number_for_atr_calculation_backwards in range ( 0 , atr_over_this_period ):
        try:
            if (row_number_of_bpu1 - row_number_for_atr_calculation_backwards) < 0:
                continue
            # if truncated_high_and_low_table_with_ohlcv_data_df.loc[
            #     row_number_of_bpu1 + 1 , "high"]:
            #     high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
            #         row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "high"]
            #     low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
            #         row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "low"]
            #     true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            # else:
            high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "high"]
            low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "low"]
            true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            # print("true_range")
            # print(true_range)

            list_of_true_ranges.append ( true_range )

        except:
            traceback.print_exc ()
    percentile_20=np.percentile(list_of_true_ranges,20)
    percentile_80 = np.percentile ( list_of_true_ranges , 80 )
    print ( "list_of_true_ranges" )
    print ( list_of_true_ranges )
    print ( "percentile_20" )
    print ( percentile_20 )
    print ( "percentile_80" )
    print ( percentile_80 )
    list_of_non_rejected_true_ranges=[]
    for true_range_in_list in list_of_true_ranges:
        if true_range_in_list>=percentile_20 and true_range_in_list<=percentile_80:
            list_of_non_rejected_true_ranges.append(true_range_in_list)
    atr = np.nan
    try:
        if len(list_of_true_ranges) <= 2:
            atr = mean(list_of_true_ranges)
        else:
            atr = mean(list_of_non_rejected_true_ranges)
    except:
        traceback.print_exc()

    return atr

def get_volume_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get high of bpu2
    volume_bpu2=False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            volume_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "volume"]
            # print ( "high_of_bpu2" )
            # print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return volume_bpu2

def get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get ohlcv of bpu2
    low_of_bpu2=False
    high_of_bpu2 = False
    open_of_bpu2 = False
    close_of_bpu2 = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            low_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "low"]
            open_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "open"]
            close_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "close"]
            high_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "high"]
            print ( "high_of_bpu2_inside_function" )
            print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return open_of_bpu2,high_of_bpu2,low_of_bpu2,close_of_bpu2
def get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get high of bpu2
    timestamp_bpu2=False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            timestamp_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "Timestamp"]
            # print ( "high_of_bpu2" )
            # print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return timestamp_bpu2

def calculate_atr_without_paranormal_bars_from_numpy_array(atr_over_this_period,
                  numpy_array_slice,
                  row_number_last_bar):
    list_of_true_ranges = []
    advanced_atr=False
    percentile_20=False
    percentile_80=False
    number_of_rows_in_numpy_array=len(numpy_array_slice)
    array_of_true_ranges=False
    try:
        if (row_number_last_bar+1 - number_of_rows_in_numpy_array) < 0:
            array_of_true_ranges=numpy_array_slice[:,2]-numpy_array_slice[:,3]
            percentile_20 = np.percentile ( array_of_true_ranges , 20 )
            percentile_80 = np.percentile ( array_of_true_ranges , 80 )
        else:
            array_of_true_ranges=numpy_array_slice[-atr_over_this_period-1:,2]-\
                                 numpy_array_slice[-atr_over_this_period-1:,3]

            percentile_20 = np.percentile ( array_of_true_ranges , 20 )
            percentile_80 = np.percentile ( array_of_true_ranges , 80 )
            # print("percentile_80")
            # print ( percentile_80 )
            # print ( "percentile_20" )
            # print ( percentile_20 )



    except:
        traceback.print_exc()

    list_of_non_rejected_true_ranges = []
    for true_range_in_array in array_of_true_ranges:

        if true_range_in_array >= percentile_20 and true_range_in_array <= percentile_80:
            list_of_non_rejected_true_ranges.append ( true_range_in_array )
    # print("list_of_non_rejected_true_ranges")
    # print ( list_of_non_rejected_true_ranges )
    advanced_atr = mean ( list_of_non_rejected_true_ranges )

    return advanced_atr
def check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level(
        acceptable_backlash , atr , open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
        low_of_bsu , low_of_bpu1 , low_of_bpu2):
    three_bars_do_not_open_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(high_of_bsu-open_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(high_of_bpu1-open_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(high_of_bpu2-open_of_bpu2) >= luft_for_bpu2:
        # print ( "luft_for_bpu2" )
        # print ( luft_for_bpu2 )
        # print ( "high_of_bpu2 - open_of_bpu2" )
        # print ( high_of_bpu2 - open_of_bpu2 )
        bpu2_ok = True
        # print ( "bpu2_ok" )
        # print ( bpu2_ok )
    else:
        # print ( "luft_for_bpu2" )
        # print ( luft_for_bpu2 )
        # print ( "high_of_bpu2" )
        # print ( high_of_bpu2 )
        # print ( "open_of_bpu2" )
        # print ( open_of_bpu2 )
        # print ( "high_of_bpu2 - open_of_bpu2" )
        # print ( high_of_bpu2 - open_of_bpu2 )
        bpu2_ok = False
        # print ( "bpu2_ok" )
        # print ( bpu2_ok )

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_open_into_level = True
    else:
        three_bars_do_not_open_into_level = False

    return three_bars_do_not_open_into_level


def check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level(acceptable_backlash , atr , close_of_bsu , close_of_bpu1 ,
                                                       close_of_bpu2 ,
                                                       high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                       low_of_bsu , low_of_bpu1 , low_of_bpu2):
    three_bars_do_not_close_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(high_of_bsu - close_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(high_of_bpu1 - close_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(high_of_bpu2 - close_of_bpu2) >= luft_for_bpu2:

        bpu2_ok = True
    else:
        bpu2_ok = False

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_close_into_level = True
    else:
        three_bars_do_not_close_into_level = False

    return three_bars_do_not_close_into_level
def check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level (
        acceptable_backlash,atr,open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
        low_of_bsu , low_of_bpu1 , low_of_bpu2 ):
    three_bars_do_not_open_into_level=False

    luft_for_bsu=(high_of_bsu-low_of_bsu)*acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(open_of_bsu-low_of_bsu)>=luft_for_bsu:
        bsu_ok=True
    else:
        bsu_ok=False

    if abs(open_of_bpu1-low_of_bpu1)>=luft_for_bpu1:
        bpu1_ok=True
    else:
        bpu1_ok=False

    if abs(open_of_bpu2-low_of_bpu2)>=luft_for_bpu2:
        bpu2_ok=True
    else:
        bpu2_ok=False

    if all([bsu_ok,bpu1_ok,bpu2_ok]):
        three_bars_do_not_open_into_level=True
    else:
        three_bars_do_not_open_into_level = False

    return three_bars_do_not_open_into_level

def check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level ( acceptable_backlash,atr,close_of_bsu , close_of_bpu1 , close_of_bpu2 ,
                                                                    high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                                    low_of_bsu , low_of_bpu1 , low_of_bpu2 ):
    three_bars_do_not_close_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(close_of_bsu - low_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(close_of_bpu1 - low_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(close_of_bpu2 - low_of_bpu2) >= luft_for_bpu2:
        bpu2_ok = True
    else:
        bpu2_ok = False

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_close_into_level = True
    else:
        three_bars_do_not_close_into_level = False

    return three_bars_do_not_close_into_level

def check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_atl_was_not_broken,
                       atl,
                       row_of_last_atl):
    if np.isnan(row_of_last_atl):
        return True
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_atl - number_of_days_where_atl_was_not_broken)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_atl + 1]

    # Determine if the low was broken during the selected period
    atl_is_not_broken_for_a_long_time = True
    min_low_over_given_period = np.min(selected_rows[:, 3])
    if min_low_over_given_period < atl:
        atl_is_not_broken_for_a_long_time = False

    return atl_is_not_broken_for_a_long_time

def check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_ath_was_not_broken,
                       ath,
                       row_of_last_ath):

    if np.isnan(row_of_last_ath):
        return True

    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_ath - number_of_days_where_ath_was_not_broken)
    # print("start_row_index")
    # print(start_row_index)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_ath + 1]
    # print("selected_rows")
    # print(selected_rows)

    # Determine if the high was broken during the selected period
    ath_is_not_broken_for_a_long_time = True
    max_high_over_given_perion = np.max(selected_rows[:, 2])
    # print("max_high_over_given_perion_when_true")
    # print(max_high_over_given_perion)
    if max_high_over_given_perion > ath:
        # print("max_high_over_given_perion_when_false")
        # print(max_high_over_given_perion)
        ath_is_not_broken_for_a_long_time = False

    return ath_is_not_broken_for_a_long_time


def return_args_for_placing_limit_or_stop_order(row_df):
    # trading_pair = base_slash_quote
    # price_of_sl = 0
    # price_of_tp = 0

    amount_of_asset_for_entry_in_quote_currency = row_df.loc[row_index, "position_size"]
    # position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
    # amount_of_asset_for_entry = position_size_in_shares_of_asset
    # price_of_limit_order = row_df.loc[row_index, "buy_order"]
    # amount_of_sl = position_size_in_shares_of_asset
    # amount_of_tp = position_size_in_shares_of_asset
    # stop_loss_is_calculated = row_df.loc[row_index, "stop_loss_is_calculated"]
    # stop_loss_is_technical = row_df.loc[row_index, "stop_loss_is_technical"]
    type_of_sl = row_df.loc[row_index, "market_or_limit_stop_loss"]
    type_of_tp = row_df.loc[row_index, "market_or_limit_take_profit"]
    price_of_tp = row_df.loc[row_index, "final_take_profit_price"]
    price_of_sl = row_df.loc[row_index, "final_stop_loss_price"]
    price_of_limit_or_stop_order = row_df.loc[row_index, "final_position_entry_price"]

    # market_or_limit_take_profit = row_df.loc[row_index, "market_or_limit_take_profit"]
    # take_profit_x_to_one = row_df.loc[row_index, "take_profit_x_to_one"]
    # take_profit_when_sl_is_technical_3_to_1 = row_df.loc[
    #     row_index, "take_profit_when_sl_is_technical_3_to_1"]
    # take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[
    #     row_index, "take_profit_when_sl_is_calculated_3_to_1"]

    spot_cross_or_isolated_margin = ""

    spot_without_margin_bool = row_df.loc[row_index, "spot_without_margin"]
    print("row_df")
    print(row_df.to_string())
    print("index12")
    print(row_index)
    # spot_without_margin_bool=bool(spot_without_margin_bool)
    print("spot_without_margin_bool")
    print(spot_without_margin_bool)
    print("type(spot_without_margin_bool)")
    print(type(spot_without_margin_bool))
    cross_margin_bool = row_df.loc[row_index, "cross_margin"]
    isolated_margin_bool = row_df.loc[row_index, "isolated_margin"]

    if spot_without_margin_bool == True:
        spot_cross_or_isolated_margin = "spot"
    elif cross_margin_bool == True:
        spot_cross_or_isolated_margin = "cross"
    elif isolated_margin_bool == True:
        spot_cross_or_isolated_margin = "isolated"
    else:
        print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated1")

    # take_profit_3_1 = np.nan
    # if "take_profit_3_1" in row_df.columns:
    #     take_profit_3_1 = row_df.loc[row_index, "take_profit_3_1"]
    # if is_not_nan(take_profit_3_1):
    #     price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0
    #
    # if stop_loss_is_technical:
    #     price_of_sl = row_df.loc[row_index, "technical_stop_loss"]
    #     if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
    #         price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
    # if stop_loss_is_calculated:
    #     price_of_sl = row_df.loc[row_index, "calculated_stop_loss"]
    #     if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
    #         price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

    # if market_or_limit_stop_loss == 'market':
    #     type_of_sl = 'market'
    # if market_or_limit_stop_loss == 'limit':
    #     type_of_sl = 'limit'
    # 
    # if market_or_limit_take_profit == 'market':
    #     type_of_tp = 'market'
    # if market_or_limit_take_profit == 'limit':
    #     type_of_tp = 'limit'

    side_of_limit_or_stop_order = row_df.loc[row_index, "side"]
    post_only_for_limit_tp_bool = False

    # args = [exchange_id,
    #         trading_pair,
    #         price_of_sl,
    #         type_of_sl,
    #         amount_of_sl,
    #         price_of_tp,
    #         type_of_tp,
    #         amount_of_tp,
    #         post_only_for_limit_tp_bool,
    #         price_of_limit_order,
    #         amount_of_asset_for_entry,
    #         side_of_limit_order,
    #         spot_cross_or_isolated_margin]

    return price_of_sl,\
        type_of_sl,\
        price_of_tp,\
        type_of_tp,\
        side_of_limit_or_stop_order,\
        price_of_limit_or_stop_order,\
        spot_cross_or_isolated_margin,\
        amount_of_asset_for_entry_in_quote_currency
def convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,price_of_entry_order):
    amount_of_asset_for_entry_in_base_currency = float(amount_of_asset_for_entry_in_quote_currency) / float(
        price_of_entry_order)
    return amount_of_asset_for_entry_in_base_currency
def run_separate_file_that_enters_position(row_df,index,current_price_of_asset,exchange_id,base_slash_quote):
    sell_order_price = row_df.loc[index, "sell_order"]
    if current_price_of_asset < sell_order_price:
        # run file that places sell limit order
        trading_pair = base_slash_quote
        price_of_sl = 0
        price_of_tp = 0
        type_of_sl = None
        type_of_tp = None
        position_size_in_usd = row_df.loc[index, "position_size"]
        position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
        amount_of_asset_for_entry = position_size_in_shares_of_asset
        price_of_limit_order = row_df.loc[index, "sell_order"]
        amount_of_sl = position_size_in_shares_of_asset
        amount_of_tp = position_size_in_shares_of_asset
        stop_loss_is_calculated = row_df.loc[index, "stop_loss_is_calculated"]
        stop_loss_is_technical = row_df.loc[index, "stop_loss_is_technical"]
        market_or_limit_stop_loss = row_df.loc[index, "market_or_limit_stop_loss"]

        market_or_limit_take_profit = row_df.loc[index, "market_or_limit_take_profit"]
        take_profit_x_to_one = row_df.loc[index, "take_profit_x_to_one"]
        take_profit_when_sl_is_technical_3_to_1 = row_df.loc[index, "take_profit_when_sl_is_technical_3_to_1"]
        take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[index, "take_profit_when_sl_is_calculated_3_to_1"]

        take_profit_3_1 = np.nan
        if "take_profit_3_1" in row_df.columns:
            take_profit_3_1 = row_df.loc[index, "take_profit_3_1"]
        if is_not_nan(take_profit_3_1):
            price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0

        if stop_loss_is_technical:
            price_of_sl = row_df.loc[index, "technical_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
                price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
        if stop_loss_is_calculated:
            price_of_sl = row_df.loc[index, "calculated_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
                price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

        if market_or_limit_stop_loss == 'market':
            type_of_sl = 'market'
        if market_or_limit_stop_loss == 'limit':
            type_of_sl = 'limit'

        if market_or_limit_take_profit == 'market':
            type_of_tp = 'market'
        if market_or_limit_take_profit == 'limit':
            type_of_tp = 'limit'

        side_of_limit_order = row_df.loc[index, "side"]
        post_only_for_limit_tp_bool = False

        spot_cross_or_isolated_margin = ""

        spot_without_margin_bool = row_df.loc[index, "spot_without_margin"]
        cross_margin_bool = row_df.loc[index, "cross_margin"]
        isolated_margin_bool = row_df.loc[index, "isolated_margin"]

        if spot_without_margin_bool == True:
            spot_cross_or_isolated_margin = "spot"
        elif cross_margin_bool == True:
            spot_cross_or_isolated_margin = "cross"
        elif isolated_margin_bool == True:
            spot_cross_or_isolated_margin = "isolated"
        else:
            print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated")

        args = [exchange_id,
                trading_pair,
                price_of_sl,
                type_of_sl,
                amount_of_sl,
                price_of_tp,
                type_of_tp,
                amount_of_tp,
                post_only_for_limit_tp_bool,
                price_of_limit_order,
                amount_of_asset_for_entry,
                side_of_limit_order,
                                  spot_cross_or_isolated_margin]

        # convert all elements in the args list into string because this is how popen works
        args = convert_list_elements_to_string(args)

        # command_args = [sys.executable, 'place_limit_order_on_exchange_with_sl_and_tp.py'] + args
        # print("executing place_place_limit_order_on_exchange_with_sl_and_tp.py as popen ")

        command_args = [sys.executable, 'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
        print("executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")


        print("command_args")
        print(command_args)
        # Run the command using subprocess Popen

        process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    else:
        # run file that places sell stop market order

        trading_pair = base_slash_quote
        price_of_sl = 0
        price_of_tp = 0
        type_of_sl = None
        type_of_tp = None
        position_size_in_usd = row_df.loc[index, "position_size"]
        position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
        amount_of_asset_for_entry = position_size_in_shares_of_asset
        price_of_buy_or_sell_market_stop_order = row_df.loc[index, "sell_order"]
        amount_of_sl = position_size_in_shares_of_asset
        amount_of_tp = position_size_in_shares_of_asset
        stop_loss_is_calculated = row_df.loc[index, "stop_loss_is_calculated"]
        stop_loss_is_technical = row_df.loc[index, "stop_loss_is_technical"]
        market_or_limit_stop_loss = row_df.loc[index, "market_or_limit_stop_loss"]

        market_or_limit_take_profit = row_df.loc[index, "market_or_limit_take_profit"]
        take_profit_x_to_one = row_df.loc[index, "take_profit_x_to_one"]
        take_profit_when_sl_is_technical_3_to_1 = row_df.loc[
            index, "take_profit_when_sl_is_technical_3_to_1"]
        take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[
            index, "take_profit_when_sl_is_calculated_3_to_1"]

        spot_cross_or_isolated_margin = ""

        spot_without_margin_bool = row_df.loc[index, "spot_without_margin"]
        cross_margin_bool = row_df.loc[index, "cross_margin"]
        isolated_margin_bool = row_df.loc[index, "isolated_margin"]

        if spot_without_margin_bool == True:
            spot_cross_or_isolated_margin = "spot"
        elif cross_margin_bool == True:
            spot_cross_or_isolated_margin = "cross"
        elif isolated_margin_bool == True:
            spot_cross_or_isolated_margin = "isolated"
        else:
            print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated")

        take_profit_3_1 = np.nan
        if "take_profit_3_1" in row_df.columns:
            take_profit_3_1 = row_df.loc[index, "take_profit_3_1"]
        if is_not_nan(take_profit_3_1):
            price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0

        if stop_loss_is_technical:
            price_of_sl = row_df.loc[index, "technical_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
                price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
        if stop_loss_is_calculated:
            price_of_sl = row_df.loc[index, "calculated_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
                price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

        if market_or_limit_stop_loss == 'market':
            type_of_sl = 'market'
        if market_or_limit_stop_loss == 'limit':
            type_of_sl = 'limit'

        if market_or_limit_take_profit == 'market':
            type_of_tp = 'market'
        if market_or_limit_take_profit == 'limit':
            type_of_tp = 'limit'

        side_of_buy_or_sell_market_stop_order = row_df.loc[index, "side"]
        post_only_for_limit_tp_bool = False

        args = [exchange_id,
                trading_pair,
                stop_loss_is_calculated,
                stop_loss_is_technical,
                price_of_sl,
                type_of_sl,
                amount_of_sl,
                price_of_tp,
                type_of_tp,
                amount_of_tp,
                post_only_for_limit_tp_bool,
                price_of_buy_or_sell_market_stop_order,
                amount_of_asset_for_entry,
                side_of_buy_or_sell_market_stop_order,
                spot_cross_or_isolated_margin]

        # convert all elements in the args list into string because this is how popen works
        args = convert_list_elements_to_string(args)
        print("args")
        print(args)
        # command_args3 = [sys.executable, 'place_buy_or_sell_stop_order_with_sl_and_tp.py'] + args
        # #
        # print("4executing place_buy_or_sell_stop_order_with_sl_and_tp.py as popen ")

        command_args3 = [sys.executable,
                         'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
        print(
            "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

        print("command_args3")
        print(command_args3)

        # # #delete this when debug is finished
        # phrase_to_print="what is your name"
        # command_args2=[sys.executable, "test.py"]+[phrase_to_print]
        # print("command_args2")
        # print(command_args2)
        process = Popen(command_args3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def convert_to_necessary_types_values_from_bfr_dataframe(stop_loss_is_calculated,
                                                         stop_loss_is_technical,
                                                         price_of_sl,
                                                         amount_of_sl,
                                                         post_only_for_limit_tp_bool,
                                                         price_of_buy_or_sell_market_stop_order,
                                                         amount_of_asset_for_entry):
    stop_loss_is_calculated=bool(stop_loss_is_calculated)
    stop_loss_is_technical=bool(stop_loss_is_technical)
    price_of_sl=float(price_of_sl)
    amount_of_sl=float(amount_of_sl)
    post_only_for_limit_tp_bool=bool(post_only_for_limit_tp_bool)
    price_of_buy_or_sell_market_stop_order=float(price_of_buy_or_sell_market_stop_order)
    amount_of_asset_for_entry=float(amount_of_asset_for_entry)
    return stop_loss_is_calculated,stop_loss_is_technical,price_of_sl,\
        amount_of_sl,post_only_for_limit_tp_bool,\
        price_of_buy_or_sell_market_stop_order,amount_of_asset_for_entry

def convert_column_to_boolean(df, column_name):
    """
    Converts a specified column of a DataFrame from string type to boolean.
    Returns the modified DataFrame.
    """
    df[column_name] = df[column_name].astype(bool)
    print(f"{column_name} converted to bool")

    return df
def convert_list_elements_to_string(lst):
    """
    Converts all elements in a list to strings.
    """
    return [str(elem) for elem in lst]
def is_not_nan(value):
    return not math.isnan(value)
def delete_last_row(df):
    # Make a copy of the dataframe without the last row
    modified_df = df.iloc[:-1].copy()

    # Return the modified DataFrame
    return modified_df
def check_if_utc_midnight_has_arrived():
    current_time = datetime.datetime.utcnow().time()
    target_time = datetime.time(hour=0, minute=0, second=1)
    # Format the time object to exclude the decimal part
    current_time_str = current_time.strftime('%H:%M:%S')
    target_time_str = target_time.strftime('%H:%M:%S')
    print("current_time_str")
    print(current_time_str)
    print("target_time_str")
    print(target_time_str)


    if current_time_str == target_time_str:
        print("It's 00:00:01 UTC!")
        return True
    else:
        print("Not yet 00:00:01 UTC.")
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_ath(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period,
                                                                                      acceptable_backlash):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []
    list_with_tickers_ready_for_rebound_off_ath=[]
    list_with_tickers_ready_for_rebound_off_atl=[]

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                table_with_ohlcv_data_df = table_with_ohlcv_data_df.iloc[:-1]

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
                        table_with_ohlcv_data_df)

                if asset_type == 'spot':
                    continue
            except:
                traceback.print_exc()

            # truncated_high_and_low_table_with_ohlcv_data_df[["high","low"]]=table_with_ohlcv_data_df[["high","low"]].round(decimals=2)
            # print("truncated_high_and_low_table_with_ohlcv_data_df")
            # print ( truncated_high_and_low_table_with_ohlcv_data_df)
            # print ( "before_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df.head(10).to_string() )

            # truncate high and low to two decimal number

            table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()

            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            print('table_with_ohlcv_data_df.loc[0,"close"]')
            print(table_with_ohlcv_data_df.loc[0, "close"])

            last_close_price = get_last_close_price_of_asset(table_with_ohlcv_data_df)
            number_of_zeroes_in_price = count_zeros_number_with_e_notaton_is_acceptable(last_close_price)

            # round high and low to two decimal number
            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(number_of_zeroes_in_price + 3,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(number_of_zeroes_in_price + 3,))

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            number_of_all_rows_in_df = len(truncated_high_and_low_table_with_ohlcv_data_df)
            list_of_periods = list(range(20, number_of_all_rows_in_df, 20))
            list_of_periods.append(len(truncated_high_and_low_table_with_ohlcv_data_df))
            # print ( "number_of_all_rows_in_df" )
            # print ( number_of_all_rows_in_df )
            # print ( "list_of_periods" )
            # print ( list_of_periods )

            # for last_row_in_slice in list_of_periods:
            # print ( "last_row_in_slice" )
            # print ( last_row_in_slice )
            truncated_high_and_low_table_with_ohlcv_data_df_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df.tail(365 * 2)
            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            table_with_ohlcv_data_df_slice = initial_table_with_ohlcv_data_df.tail(365 * 2).copy()

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head(10).to_string() )
            #

            # print ( "truncated_high_and_low_table_with_ohlcv_data_df_slice" )
            # print ( truncated_high_and_low_table_with_ohlcv_data_df_slice.tail(10).to_string())

            all_time_high = truncated_high_and_low_table_with_ohlcv_data_df_slice["high"].max()
            all_time_low = truncated_high_and_low_table_with_ohlcv_data_df_slice["low"].min()

            # print("all_time_high")
            # print(all_time_high)
            # print("all_time_low")
            # print(all_time_low)
            ohlcv_df_with_low_equal_to_atl_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["low"] == all_time_low]
            ohlcv_df_with_high_equal_to_ath_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["high"] == all_time_high]

            ######################################################

            ###############################################

            # find rebound from ath
            if len(ohlcv_df_with_high_equal_to_ath_slice) > 1:

                print("ohlcv_df_with_high_equal_to_ath_slice")
                print(ohlcv_df_with_high_equal_to_ath_slice.to_string())
                # print ( "list_with_tickers_ready_for_rebound_off_ath" )
                # print ( list_with_tickers_ready_for_rebound_off_ath )
                ohlcv_df_with_high_equal_to_ath_slice = \
                    ohlcv_df_with_high_equal_to_ath_slice.rename(columns={"index": "index_column"})
                # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )

                print("1output")

                row_number_of_bpu1 = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[1]
                row_number_of_bsu = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[0]
                row_number_of_bpu2 = row_number_of_bpu1 + 1

                # check if the found ath is legit and no broken for the last 2 years
                ath_is_not_broken_for_a_long_time = True
                try:
                    number_of_days_where_ath_was_not_broken = 366 * 2
                    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                    ath_is_not_broken_for_a_long_time = check_ath_breakout(
                        table_with_ohlcv_data_df_slice_numpy_array,
                        number_of_days_where_ath_was_not_broken,
                        all_time_high,
                        row_number_of_bsu)
                    print(f"ath={all_time_high}")
                    print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

                except:
                    traceback.print_exc()

                if ath_is_not_broken_for_a_long_time == False:
                    continue

                # # check if the found atl is legit and no broken for the last 2 years
                # atl_is_not_broken_for_a_long_time = True
                # try:
                #     number_of_days_where_atl_was_not_broken = 366 * 2
                #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                #                                                            number_of_days_where_atl_was_not_broken,
                #                                                            all_time_low,
                #                                                            last_all_time_low_row_number)
                #     print(f"atl={all_time_low}")
                #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
                #
                # except:
                #     pass
                #
                # if atl_is_not_broken_for_a_long_time == False:
                #     continue

                #############################################

                # print("row_number_of_bsu")
                # print(row_number_of_bsu)
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                print("row_number_of_bpu2")
                print(row_number_of_bpu2)
                print("len(truncated_high_and_low_table_with_ohlcv_data_df)-1")
                print(len(truncated_high_and_low_table_with_ohlcv_data_df) - 1)

                print("2output")
                if row_number_of_bpu2 != len(truncated_high_and_low_table_with_ohlcv_data_df) - 1:
                    continue
                print("3output")
                # print ( "row_number_of_bsu" )
                # print ( row_number_of_bsu )
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                # print("row_number_of_bpu2")
                # print(row_number_of_bpu2)

                # get ohlcv of tvx with high and low truncated
                # open_of_tvx,high_of_tvx,low_of_tvx,close_of_tvx=\
                #     get_ohlc_of_tvx(truncated_high_and_low_table_with_ohlcv_data_df,
                #                      row_number_of_bpu1)
                # get ohlcv of bpu2 with high and low truncated
                open_of_bpu2, high_of_bpu2, low_of_bpu2, close_of_bpu2 = \
                    get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # atr = calculate_atr(atr_over_this_period,
                #                     table_with_ohlcv_data_df,
                #                     row_number_of_bpu1)
                advanced_atr = calculate_advanced_atr(advanced_atr_over_this_period,
                                                      table_with_ohlcv_data_df,
                                                      row_number_of_bpu1)
                # atr = round(atr, 20)
                # advanced_atr = round(advanced_atr, 20)

                low_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "open"]
                close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "close"]
                close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "close"]
                high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "high"]

                # get ohlcv of bsu, bpu1,bpu2, tvx
                # get ohlcv of bpu2
                # print ("table_with_ohlcv_data_df_2")
                # print (table_with_ohlcv_data_df.head(10).to_string())
                true_open_of_bpu2, true_high_of_bpu2, true_low_of_bpu2, true_close_of_bpu2 = \
                    get_ohlc_of_bpu2(table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # get ohlcv of tvx
                # open_of_bpu2 = high_of_bpu2 = low_of_bpu2 = close_of_bpu2 = volume_of_bpu2 = timestamp_of_bpu2 = False
                open_of_tvx = high_of_tvx = low_of_tvx = close_of_tvx = volume_of_tvx = timestamp_of_tvx = False
                # try:
                #     true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                #         get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                # except:
                #     pass
                # get ohlc of bsu, bpu1
                true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                # true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                # true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "high"]
                #
                # print("table_with_ohlcv_data_df_slice_in_ath")
                # print(table_with_ohlcv_data_df_slice.head(10).to_string())
                true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "open"]
                true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bsu, "close"]
                true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "close"]
                true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "high"]

                volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu, "volume"]
                volume_of_bpu1 = table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1, "volume"]
                volume_of_bpu2 = get_volume_of_bpu2(table_with_ohlcv_data_df,
                                                    row_number_of_bpu1)

                print("4output")

                # if all_time_high <= 1:
                #     if volume_of_bpu1 < 1000 or volume_of_bsu < 1000 or volume_of_bpu2 < 1000:
                #         continue
                # print("5output")
                # if volume_of_bpu1 < 750 or volume_of_bsu < 750 or volume_of_bpu2 < 750:
                #     continue
                print("6output")
                # if open_of_tvx>=close_of_bpu2:
                #     continue

                # if true_high_of_tvx<all_time_high-0.5*atr:
                #     continue

                timestamp_of_bpu2 = get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                                          row_number_of_bpu1)
                timestamp_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1, "Timestamp"]
                timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu, "Timestamp"]

                timestamp_of_bpu2_with_time, timestamp_of_bpu2_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu2)
                timestamp_of_bpu1_with_time, timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu1)
                timestamp_of_bsu_with_time, timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bsu)

                # print ( "high_of_bpu2" )
                # print ( high_of_bpu2 )

                # calcualte atr over 5 days before bpu2. bpu2 is not included
                # atr_over_this_period = 30

                asset_not_open_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level(acceptable_backlash, advanced_atr, open_of_bsu,
                                                                      open_of_bpu1, open_of_bpu2,
                                                                      high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                      low_of_bsu, low_of_bpu1, low_of_bpu2)
                asset_not_close_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level(acceptable_backlash, advanced_atr, close_of_bsu,
                                                                       close_of_bpu1, close_of_bpu2,
                                                                       high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                       low_of_bsu, low_of_bpu1, low_of_bpu2)

                # print("asset_not_open_into_level_bool")
                # print(asset_not_open_into_level_bool)
                # print("asset_not_close_into_level_bool")
                # print(asset_not_close_into_level_bool)

                print("7output")
                if not asset_not_open_into_level_bool:
                    continue
                print("8output")
                if not asset_not_close_into_level_bool:
                    continue

                if advanced_atr > 0:
                    backlash = abs(all_time_high - true_high_of_bpu2)
                    if (backlash <= advanced_atr * acceptable_backlash) and (all_time_high - high_of_bpu2) >= 0:
                        list_with_tickers_ready_for_rebound_off_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_with_tickers_ready_for_rebound_off_atl:
        return True
    elif stock_name in list_with_tickers_ready_for_rebound_off_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_atl(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period,
                                                                                      acceptable_backlash):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []
    list_with_tickers_ready_for_rebound_off_atl=[]
    list_with_tickers_ready_for_rebound_off_ath=[]

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                table_with_ohlcv_data_df = table_with_ohlcv_data_df.iloc[:-1]

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue



            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']



            print("exchange")
            print(exchange)
            # print("short_name")
            # print(short_name)

            # truncated_high_and_low_table_with_ohlcv_data_df[["high","low"]]=table_with_ohlcv_data_df[["high","low"]].round(decimals=2)
            # print("truncated_high_and_low_table_with_ohlcv_data_df")
            # print ( truncated_high_and_low_table_with_ohlcv_data_df)
            # print ( "before_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df.head(10).to_string() )

            # truncate high and low to two decimal number

            table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()

            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            # print('table_with_ohlcv_data_df.loc[0,"close"]')
            # print ( table_with_ohlcv_data_df.loc[0 , "close"] )

            last_close_price = get_last_close_price_of_asset(table_with_ohlcv_data_df)
            number_of_zeroes_in_price = count_zeros_number_with_e_notaton_is_acceptable(last_close_price)

            # round high and low to two decimal number
            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(number_of_zeroes_in_price + 3,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(number_of_zeroes_in_price + 3,))

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            # number_of_all_rows_in_df=len(truncated_high_and_low_table_with_ohlcv_data_df)
            # list_of_periods=list(range(20,number_of_all_rows_in_df,20))
            # list_of_periods.append(len(truncated_high_and_low_table_with_ohlcv_data_df))
            # print ( "number_of_all_rows_in_df" )
            # print ( number_of_all_rows_in_df )
            # print ( "list_of_periods" )
            # print ( list_of_periods )

            # for last_row_in_slice in list_of_periods:
            # print ( "last_row_in_slice" )
            # print ( last_row_in_slice )
            truncated_high_and_low_table_with_ohlcv_data_df_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df.tail(365 * 2)
            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            table_with_ohlcv_data_df_slice = initial_table_with_ohlcv_data_df.tail(365 * 2).copy()

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head(10).to_string() )
            #

            # print ( "truncated_high_and_low_table_with_ohlcv_data_df_slice" )
            # print ( truncated_high_and_low_table_with_ohlcv_data_df_slice )

            all_time_high = truncated_high_and_low_table_with_ohlcv_data_df_slice["high"].max()
            all_time_low = truncated_high_and_low_table_with_ohlcv_data_df_slice["low"].min()

            # print("all_time_high")
            # print(all_time_high)
            # print("all_time_low")
            # print(all_time_low)
            ohlcv_df_with_low_equal_to_atl_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["low"] == all_time_low]
            ohlcv_df_with_high_equal_to_ath_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["high"] == all_time_high]

            ######################################################

            # find rebound from atl
            if len(ohlcv_df_with_low_equal_to_atl_slice) > 1:
                # list_with_tickers_ready_for_rebound_off_atl.append(stock_name)
                # print ( "ohlcv_df_with_low_equal_to_atl_slice" )
                # print ( ohlcv_df_with_low_equal_to_atl_slice )
                # print ( "list_with_tickers_ready_for_rebound_off_atl" )
                # print ( list_with_tickers_ready_for_rebound_off_atl )
                ohlcv_df_with_low_equal_to_atl_slice = \
                    ohlcv_df_with_low_equal_to_atl_slice.rename(columns={"index": "index_column"})
                # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )
                row_number_of_bpu1 = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[1]
                row_number_of_bsu = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[0]
                row_number_of_bpu2 = row_number_of_bpu1 + 1

                # check if the found atl is legit and no broken for the last 2 years
                last_all_time_low_row_number = row_number_of_bsu
                atl_is_not_broken_for_a_long_time = True
                try:
                    number_of_days_where_atl_was_not_broken = 366 * 2
                    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                    atl_is_not_broken_for_a_long_time = check_atl_breakout(
                        table_with_ohlcv_data_df_slice_numpy_array,
                        number_of_days_where_atl_was_not_broken,
                        all_time_low,
                        last_all_time_low_row_number)
                    print(f"atl={all_time_low}")
                    print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

                except:
                    traceback.print_exc()

                if atl_is_not_broken_for_a_long_time == False:
                    continue

                # print("row_number_of_bsu")
                # print(row_number_of_bsu)
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                # print("row_number_of_bpu2")
                # print(row_number_of_bpu2)
                # print("len(truncated_high_and_low_table_with_ohlcv_data_df)-1")
                # print(len(truncated_high_and_low_table_with_ohlcv_data_df)-1)
                # print("len(truncated_high_and_low_table_with_ohlcv_data_df_slice)-1")
                # print(len(truncated_high_and_low_table_with_ohlcv_data_df_slice) - 1)

                if row_number_of_bpu2 != len(truncated_high_and_low_table_with_ohlcv_data_df) - 1:
                    continue
                # print ( "row_number_of_bpu1" )
                # print ( row_number_of_bpu1 )

                # get ohlcv of bsu, bpu1,bpu2, tvx from truncated high and low df
                # get ohlcv of bpu2 from NOT truncated high and low df
                open_of_bpu2 = high_of_bpu2 = low_of_bpu2 = close_of_bpu2 = False
                open_of_tvx = high_of_tvx = low_of_tvx = close_of_tvx = False
                try:
                    open_of_bpu2, high_of_bpu2, low_of_bpu2, close_of_bpu2 = \
                        get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1)
                except:
                    traceback.print_exc()

                # # get ohlcv of tvx from NOT truncated high and low df
                # try:
                #     open_of_tvx , high_of_tvx , low_of_tvx , close_of_tvx = \
                #         get_ohlc_of_tvx ( truncated_high_and_low_table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                # except:
                #     pass

                # if open_of_tvx==False:
                #
                #     print ( "row_number_of_bpu1" )
                #     print ( row_number_of_bpu1 )
                #     print ( "table_with_ohlcv_data_df" )
                #     print ( table_with_ohlcv_data_df.iloc[row_number_of_bpu1-5:row_number_of_bpu1+5,:].to_string () )
                #     #time.sleep(10000)

                # get ohlc of bsu, bpu1 from truncated high and low df
                low_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "open"]
                close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "close"]
                close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "close"]
                high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "high"]

                # get ohlcv of bsu, bpu1,bpu2, tvx
                # get ohlcv of bpu2
                true_open_of_bpu2, true_high_of_bpu2, true_low_of_bpu2, true_close_of_bpu2 = \
                    get_ohlc_of_bpu2(table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # get ohlcv of tvx
                # true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                #     get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                #                       row_number_of_bpu1 )
                # get ohlc of bsu, bpu1
                true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "open"]
                true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bsu, "close"]
                true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "close"]
                true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "high"]

                volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu, "volume"]
                volume_of_bpu1 = table_with_ohlcv_data_df.loc[row_number_of_bpu1, "volume"]
                volume_of_bpu2 = get_volume_of_bpu2(table_with_ohlcv_data_df, row_number_of_bpu1)

                # atr = calculate_atr ( atr_over_this_period ,
                #                       table_with_ohlcv_data_df ,
                #                       row_number_of_bpu1 )
                advanced_atr = calculate_advanced_atr(advanced_atr_over_this_period,
                                                      table_with_ohlcv_data_df,
                                                      row_number_of_bpu1)

                # atr = round ( atr ,20)
                # advanced_atr = round ( advanced_atr ,20)

                # print("true_low_of_bsu")
                # print(true_low_of_bsu)
                # print ( "true_low_of_bpu1" )
                # print ( true_low_of_bpu1 )
                # print ( "true_low_of_bpu2" )
                # print ( true_low_of_bpu2 )

                # if all_time_low<=1:
                #     if volume_of_bpu1 < 1000 or volume_of_bsu < 1000 or volume_of_bpu2 < 1000:
                #         continue
                #
                # if volume_of_bpu1<750 or volume_of_bsu<750 or volume_of_bpu2<750:
                #     continue

                # if open_of_tvx<=close_of_bpu2:
                #     continue
                #
                # if true_low_of_tvx > all_time_low + 0.5 * atr:
                #     continue

                timestamp_of_bpu2 = get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                                          row_number_of_bpu1)
                timestamp_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1, "Timestamp"]
                timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu, "Timestamp"]

                timestamp_of_bpu2_with_time, timestamp_of_bpu2_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu2)
                timestamp_of_bpu1_with_time, timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu1)
                timestamp_of_bsu_with_time, timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bsu)

                # print ( "low_of_bpu2" )
                # print ( low_of_bpu2 )

                # calcualte atr over 5 days before bpu2. bpu2 is not included
                # atr_over_this_period = 30

                asset_not_open_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level(acceptable_backlash, advanced_atr, open_of_bsu,
                                                                      open_of_bpu1, open_of_bpu2,
                                                                      high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                      low_of_bsu, low_of_bpu1, low_of_bpu2)
                asset_not_close_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level(acceptable_backlash, advanced_atr, close_of_bsu,
                                                                       close_of_bpu1, close_of_bpu2,
                                                                       high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                       low_of_bsu, low_of_bpu1, low_of_bpu2)

                if not asset_not_open_into_level_bool:
                    continue

                if not asset_not_close_into_level_bool:
                    continue

                if advanced_atr > 0:
                    backlash = abs(true_low_of_bpu2 - all_time_low)
                    if (backlash <= advanced_atr * acceptable_backlash) and (low_of_bpu2 - all_time_low) >= 0:
                        stop_loss = all_time_low - (advanced_atr * 0.05)
                        calculated_backlash_from_advanced_atr = advanced_atr * 0.05
                        buy_order = all_time_low + (advanced_atr * 0.5)
                        take_profit_3_to_1 = buy_order + (advanced_atr * 0.5) * 3
                        take_profit_4_to_1 = buy_order + (advanced_atr * 0.5) * 4

                        # stop_loss = round(stop_loss, 3)
                        # calculated_backlash_from_advanced_atr = round(calculated_backlash_from_advanced_atr, 3)
                        # buy_order = round(buy_order, 3)
                        # take_profit_3_to_1 = round(take_profit_3_to_1, 3)
                        # take_profit_4_to_1 = round(take_profit_4_to_1, 3)

                        # advanced_atr = round(advanced_atr, 3)
                        # low_of_bsu = round(low_of_bsu, 3)
                        # low_of_bpu1 = round(low_of_bpu1, 3)
                        # low_of_bpu2 = round(low_of_bpu2, 3)
                        # close_of_bpu2 = round(close_of_bpu2, 3)

                        list_with_tickers_ready_for_rebound_off_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_with_tickers_ready_for_rebound_off_atl:
        return True
    elif stock_name in list_with_tickers_ready_for_rebound_off_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_one_bar(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]
            # print("last_two_years_of_data_but_one_last_day")
            # print(last_two_years_of_data_but_one_last_day.to_string())

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_one_last_day['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years

            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_atl_was_not_broken,
                    all_time_low,
                    last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            print(f"false_breakout_bar_row_number={false_breakout_bar_row_number}")
            print(f"last_all_time_low_row_number={last_all_time_low_row_number}")
            if false_breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            print(f"low_of_false_breakout_bar={low_of_false_breakout_bar}")
            print(f"all_time_low={all_time_low}")
            if low_of_false_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar <= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_false_breakout_bar <= open_of_false_breakout_bar:
                continue

            print(f"7found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_false_breakout_bar_row_number)

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            distance_between_current_atl_and_false_breakout_bar_open = \
                open_of_false_breakout_bar - all_time_low
            distance_between_current_atl_and_false_breakout_bar_close = \
                all_time_low - close_of_false_breakout_bar
            if distance_between_current_atl_and_false_breakout_bar_open == 0:
                continue

            if not (distance_between_current_atl_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)

            buy_order = all_time_low + (advanced_atr * 0.5)
            technical_stop_loss = low_of_false_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss
            take_profit_when_stop_loss_is_technical_3_to_1 = buy_order + (buy_order - technical_stop_loss) * 3
            take_profit_when_stop_loss_is_technical_4_to_1 = buy_order + (buy_order - technical_stop_loss) * 4
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # buy_order = round(buy_order, 3)
            # technical_stop_loss = round(technical_stop_loss, 3)
            # take_profit_when_stop_loss_is_technical_3_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_3_to_1, 3)
            # take_profit_when_stop_loss_is_technical_4_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_4_to_1, 3)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr, 3)

            # open_of_bar_next_day_after_false_breakout_bar = \
            #     round(open_of_bar_next_day_after_false_breakout_bar,20)
            # advanced_atr = \
            #     round(advanced_atr, 3)

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_one_bar(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_one_last_day['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_ath_was_not_broken,
                    all_time_high,
                    last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            #############################################

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if false_breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_false_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar >= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_false_breakout_bar >= open_of_false_breakout_bar:
                continue

            print(f"7found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)

            # if suppression_flag_for_lows==False:
            #     continue

            # print(f"last_n_lows_for_{stock_name}")
            # print(last_n_lows)
            #
            # print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_false_breakout_bar_row_number)

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            distance_between_current_ath_and_false_breakout_bar_open = \
                all_time_high - open_of_false_breakout_bar
            distance_between_current_ath_and_false_breakout_bar_close = \
                close_of_false_breakout_bar - all_time_high
            if distance_between_current_ath_and_false_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_two_bars(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after false_breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate false_breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate false_breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate false_breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate false_breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate false_breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate false_breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-false_breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-false_breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-false_breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-false_breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-false_breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-false_breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_two_last_days['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years

            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_atl_was_not_broken,
                    all_time_low,
                    last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический минимум был не ближе, чем 3 дня до пробоя
            if false_breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_false_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar >= all_time_low:
                continue
            print(f"5.5found_stock={stock_name}", f"atl={all_time_low}",
                  f"open_of_next_day_bar_after_break_out_bar={open_of_next_day_bar_after_break_out_bar}  ")
            if open_of_next_day_bar_after_break_out_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_next_day_bar_after_break_out_bar <= all_time_low:
                continue

            print(f"7found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"8found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_false_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar < close_of_false_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar < open_of_false_breakout_bar or \
                    high_of_next_day_bar_after_break_out_bar < high_of_false_breakout_bar:
                continue

            print(f"9found_stock={stock_name}")

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            # check that second false breakout bar does not open and close into level
            distance_between_current_atl_and_false_breakout_bar_open = \
                open_of_false_breakout_bar - all_time_low
            distance_between_current_atl_and_false_breakout_bar_close = \
                all_time_low - close_of_false_breakout_bar
            if distance_between_current_atl_and_false_breakout_bar_open == 0:
                continue

            print(f"10found_stock={stock_name}")

            if not (distance_between_current_atl_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            print(f"11found_stock={stock_name}")

            # check that second false breakout bar does not open and close into level
            distance_between_current_atl_and_next_day_bar_after_break_out_bar_open = \
                open_of_next_day_bar_after_break_out_bar - all_time_low
            distance_between_current_atl_and_next_day_bar_after_break_out_bar_close = \
                all_time_low - close_of_next_day_bar_after_break_out_bar
            if distance_between_current_atl_and_next_day_bar_after_break_out_bar_open == 0:
                continue

            print(f"12found_stock={stock_name}")

            if not (distance_between_current_atl_and_next_day_bar_after_break_out_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_next_day_bar_after_break_out_bar_close > advanced_atr * 0.05):
                continue

            print(f"13found_stock={stock_name}")

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            print(f"14found_stock={stock_name}")

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_two_bars(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_two_last_days
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_two_last_days
            pre_false_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after false_breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate false_breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate false_breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate false_breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate false_breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate false_breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate false_breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-false_breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-false_breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-false_breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-false_breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-false_breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-false_breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_ath_was_not_broken,
                    all_time_high,
                    last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            #############################################

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический максимум был не ближе, чем 3 дня до пробоя
            if false_breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_false_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar <= all_time_high:
                continue

            if open_of_next_day_bar_after_break_out_bar <= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_next_day_bar_after_break_out_bar >= all_time_high:
                continue

            print(f"7found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)
            print(f"8found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_false_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar > close_of_false_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar > open_of_false_breakout_bar or \
                    low_of_next_day_bar_after_break_out_bar > low_of_false_breakout_bar:
                continue

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            # check that first false breakout bar does not open and close into level
            distance_between_current_ath_and_false_breakout_bar_open = \
                all_time_high - open_of_false_breakout_bar
            distance_between_current_ath_and_false_breakout_bar_close = \
                close_of_false_breakout_bar - all_time_high
            if distance_between_current_ath_and_false_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            # check that second false breakout bar does not open and close into level
            distance_between_current_ath_and_next_day_bar_after_break_out_bar_open = \
                all_time_high - open_of_next_day_bar_after_break_out_bar
            distance_between_current_ath_and_next_day_bar_after_break_out_bar_close = \
                close_of_next_day_bar_after_break_out_bar - all_time_high
            if distance_between_current_ath_and_next_day_bar_after_break_out_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_next_day_bar_after_break_out_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_next_day_bar_after_break_out_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            sell_order = all_time_high - (advanced_atr * 0.5)
            technical_stop_loss = max(high_of_false_breakout_bar, high_of_next_day_bar_after_break_out_bar) + (
                    0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_sell_order = technical_stop_loss - sell_order
            take_profit_when_stop_loss_is_technical_3_to_1 = sell_order - (technical_stop_loss - sell_order) * 3
            take_profit_when_stop_loss_is_technical_4_to_1 = sell_order - (technical_stop_loss - sell_order) * 4
            distance_between_technical_stop_loss_and_sell_order_in_atr = \
                distance_between_technical_stop_loss_and_sell_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss,20)
            # take_profit_when_stop_loss_is_technical_3_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_3_to_1,20)
            # take_profit_when_stop_loss_is_technical_4_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_4_to_1,20)

            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_sell_order_in_atr,20)
            # sell_order = round(sell_order,20)
            # advanced_atr = round(advanced_atr,20)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False


def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_day_two(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            print("include_last_day_in_bfr_model_assessment")
            print(include_last_day_in_bfr_model_assessment)
            print("type(include_last_day_in_bfr_model_assessment)")
            print(type(include_last_day_in_bfr_model_assessment))
            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_two_last_days
            pre_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_two_last_days
            pre_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_ath_was_not_broken,
                                                                       all_time_high,
                                                                       last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический максимум был не ближе, чем 3 дня до пробоя
            if breakout_bar_row_number - last_all_time_high_row_number < 3:
                print("breakout_bar_row_number - last_all_time_high_row_number < 3")
                print(f"breakout_bar_row_number={breakout_bar_row_number}")
                print(f"last_all_time_high_row_number={last_all_time_high_row_number}")
                print(f"high_of_last_all_time_high={high_of_last_all_time_high}")
                print(f"high_of_breakout_bar={high_of_breakout_bar}")
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                print('''last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high''')
                continue

            print(f"3found_stock={stock_name}")

            if high_of_breakout_bar <= all_time_high:
                print('''high_of_breakout_bar <= all_time_high''')
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar >= all_time_high:
                print('''open_of_breakout_bar >= all_time_high''')
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar <= all_time_high:
                print('''close_of_breakout_bar <= all_time_high''')
                continue

            print(f"6found_stock={stock_name}")

            # #cмотрим поджатие
            # number_of_bars_when_we_check_suppression_by_lows=3
            # last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            # suppression_flag = True
            # for i in range(len(last_n_lows) - 1):
            #     if last_n_lows[i + 1] < last_n_lows[i]:
            #         suppression_flag = False
            #         break
            # if suppression_flag==False:
            #     continue

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] < last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_closes_for_{stock_name}")
            print(last_n_closes)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar < close_of_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar < close_of_breakout_bar:
                continue

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_ath_and_breakout_bar_open = \
                all_time_high - open_of_breakout_bar
            distance_between_current_ath_and_breakout_bar_close = \
                close_of_breakout_bar - all_time_high
            if distance_between_current_ath_and_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            calculated_stop_loss = all_time_high - (advanced_atr * 0.05)
            buy_order = all_time_high + (advanced_atr * 0.5)
            take_profit_when_sl_is_calculated_3_to_1 = (buy_order - calculated_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_calculated_4_to_1 = (buy_order - calculated_stop_loss) * 4 + buy_order

            # round decimals for ease of looking at
            # buy_order = round(buy_order,20)
            # calculated_stop_loss = round(calculated_stop_loss,20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1,20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1,20)

            # plot all lines with advanced atr (stop loss is technical)
            technical_stop_loss = low_of_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss
            take_profit_when_sl_is_technical_3_to_1 = (buy_order - technical_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_technical_4_to_1 = (buy_order - technical_stop_loss) * 4 + buy_order
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss,20)
            # take_profit_when_sl_is_technical_3_to_1 = \
            #     round(take_profit_when_sl_is_technical_3_to_1,20)
            # take_profit_when_sl_is_technical_4_to_1 = \
            #     round(take_profit_when_sl_is_technical_4_to_1,20)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr,20)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:


            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue


            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']



            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue

            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_two_last_days['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years
            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_atl_was_not_broken,
                                                                       all_time_low,
                                                                       last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический минимум был не ближе, чем 3 дня до пробоя
            if breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar > close_of_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar > close_of_breakout_bar:
                continue

            print(f"8found_stock={stock_name}")

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_atl_and_breakout_bar_open = \
                open_of_breakout_bar - all_time_low
            distance_between_current_atl_and_breakout_bar_close = \
                all_time_low - close_of_breakout_bar
            if distance_between_current_atl_and_breakout_bar_open == 0:
                continue

            print(f"9found_stock={stock_name}")

            if not (distance_between_current_atl_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            print(f"10found_stock={stock_name}")

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            print(f"11found_stock={stock_name}")
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            print(f"12found_stock={stock_name}")
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            print(f"13found_stock={stock_name}")
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)
            print(f"14found_stock={stock_name}")

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()

    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False


def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_the_next_day(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # counter = counter + 1
            # print(f'{stock_name} is'
            #       f' number {counter} out of {len(list_of_tables_in_ohlcv_db)}\n')

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            # print("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
            #             table_with_ohlcv_data_df)
            #
            #     # do not short unshortable assets
            #     # if asset_type == 'spot':
            # #                    continue
            #
            # except:
            #     traceback.print_exc()

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")
            #
            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_one_last_day['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_ath_was_not_broken,
                                                                       all_time_high,
                                                                       last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar <= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True
            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_breakout_bar_row_number)

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_ath_and_breakout_bar_open = \
                all_time_high - open_of_breakout_bar
            distance_between_current_ath_and_breakout_bar_close = \
                close_of_breakout_bar - all_time_high
            if distance_between_current_ath_and_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)

            calculated_stop_loss = all_time_high - (advanced_atr * 0.05)
            buy_order = all_time_high + (advanced_atr * 0.5)
            take_profit_when_sl_is_calculated_3_to_1 = (buy_order - calculated_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_calculated_4_to_1 = (buy_order - calculated_stop_loss) * 4 + buy_order

            # round decimals for ease of looking at
            # buy_order = round(buy_order, 20)
            # calculated_stop_loss = round(calculated_stop_loss, 20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1, 20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1, 20)

            # plot all lines with advanced atr (stop loss is technical)
            technical_stop_loss = low_of_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss

            take_profit_when_sl_is_technical_3_to_1 = (buy_order - technical_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_technical_4_to_1 = (buy_order - technical_stop_loss) * 4 + buy_order
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss, 20)
            # take_profit_when_sl_is_technical_3_to_1 = \
            #     round(take_profit_when_sl_is_technical_3_to_1, 20)
            # take_profit_when_sl_is_technical_4_to_1 = \
            #     round(take_profit_when_sl_is_technical_4_to_1, 20)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr, 20)

            list_of_stocks_which_broke_ath.append(stock_name)
            print("list_of_stocks_which_broke_ath")
            print(list_of_stocks_which_broke_ath)
        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_the_next_day(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db=[stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # counter = counter + 1
            # print(f'{stock_name} is'
            #       f' number {counter} out of {len(list_of_tables_in_ohlcv_db)}\n')

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df=fetch_one_ohlcv_table(stock_name,timeframe,last_bitcoin_price)


            # ##########################
            # #delete this in the future in production
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################





            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue



            if table_with_ohlcv_data_df.empty:
                continue

            # print("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
            #             table_with_ohlcv_data_df)
            #
            #     # do not short unshortable assets
            #     # if asset_type == 'spot':
            # #                    continue
            #
            # except:
            #     traceback.print_exc()

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Round ohlc and adjclose to 6 decimal places
            # last_two_years_of_data = last_two_years_of_data.round(
            #               {'open': 6, 'high': 6, 'low': 6, 'close': 6, 'adjclose': 6})

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_one_last_day['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years
            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_atl_was_not_broken,
                                                                       all_time_low,
                                                                       last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(
                last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_breakout_bar_row_number)

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_atl_and_breakout_bar_open = \
                open_of_breakout_bar - all_time_low
            distance_between_current_atl_and_breakout_bar_close = \
                all_time_low - close_of_breakout_bar
            if distance_between_current_atl_and_breakout_bar_open == 0:
                continue

            if not (distance_between_current_atl_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)

            list_of_stocks_which_broke_atl.append(stock_name)
            print("list_of_stocks_which_broke_atl")
            print(list_of_stocks_which_broke_atl)

            # calculated_stop_loss = all_time_low + (advanced_atr * 0.05)
            # sell_order = all_time_low - (advanced_atr * 0.5)
            # take_profit_when_sl_is_calculated_3_to_1 = sell_order - (calculated_stop_loss - sell_order) * 3
            # take_profit_when_sl_is_calculated_4_to_1 = sell_order - (calculated_stop_loss - sell_order) * 4
            # # round decimals for ease of looking at
            # sell_order = round(sell_order, 20)
            # calculated_stop_loss = round(calculated_stop_loss, 20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1, 20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1, 20)
            #
            # # plot all lines with advanced atr (stop loss is technical)
            # technical_stop_loss = high_of_breakout_bar + (0.05 * advanced_atr)
            # distance_between_technical_stop_loss_and_sell_order = technical_stop_loss - sell_order
            # take_profit_when_sl_is_technical_3_to_1 = sell_order - (technical_stop_loss - sell_order) * 3
            # take_profit_when_sl_is_technical_4_to_1 = sell_order - (technical_stop_loss - sell_order) * 4
            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     distance_between_technical_stop_loss_and_sell_order / advanced_atr
            # # round technical stop loss and take profit for ease of looking at
            # # technical_stop_loss = round(technical_stop_loss,20)
            # # take_profit_when_sl_is_technical_3_to_1 = \
            # #     round(take_profit_when_sl_is_technical_3_to_1, 3)
            # # take_profit_when_sl_is_technical_4_to_1 = \
            # #     round(take_profit_when_sl_is_technical_4_to_1, 3)
            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_sell_order_in_atr, 20)
            #
            # df_with_level_atr_bpu_bsu_etc = pd.DataFrame()
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker"] = stock_name
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "exchange"] = exchange
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "model"] = "ПРОБОЙ_ATL_с_подтверждением_вход_на_следующий_день"
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "atl"] = all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "advanced_atr"] = advanced_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "advanced_atr_over_this_period"] = \
            #     advanced_atr_over_this_period
            # # df_with_level_atr_bpu_bsu_etc.loc[
            # #     0, "low_of_bsu"] = all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_bsu"] = open_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_bsu"] = high_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_bsu"] = low_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_bsu"] = close_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_bsu"] = volume_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "timestamp_of_bsu"] = timestamp_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_bsu"] = date_of_last_ath
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "timestamp_of_pre_breakout_bar"] = timestamp_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_pre_breakout_bar"] = date_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_pre_breakout_bar"] = open_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_pre_breakout_bar"] = high_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_pre_breakout_bar"] = low_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_pre_breakout_bar"] = close_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_pre_breakout_bar"] = volume_of_pre_breakout_bar
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_breakout_bar"] = date_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_breakout_bar"] = open_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_breakout_bar"] = high_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_breakout_bar"] = low_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_breakout_bar"] = close_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_breakout_bar"] = volume_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_breakout_bar"] = timestamp_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_breakout_bar"] = date_of_breakout_bar
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "min_volume_over_last_n_days"] = last_two_years_of_data['volume'].tail(
            #     count_min_volume_over_this_many_days).min()
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "count_min_volume_over_this_many_days"] = count_min_volume_over_this_many_days
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "sell_order"] = sell_order
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "calculated_stop_loss"] = calculated_stop_loss
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_calculated_3_to_1"] = take_profit_when_sl_is_calculated_3_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_calculated_4_to_1"] = take_profit_when_sl_is_calculated_4_to_1
            #
            # distance_between_calculated_stop_loss_and_sell_order = calculated_stop_loss - sell_order
            # distance_between_calculated_stop_loss_and_sell_order_in_atr = \
            #     distance_between_calculated_stop_loss_and_sell_order / advanced_atr
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "distance_between_calculated_stop_loss_and_sell_order_in_atr"] = \
            #     distance_between_calculated_stop_loss_and_sell_order_in_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "technical_stop_loss"] = technical_stop_loss
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_technical_3_to_1"] = take_profit_when_sl_is_technical_3_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_technical_4_to_1"] = take_profit_when_sl_is_technical_4_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "distance_between_technical_sl_and_sell_order_in_atr"] = distance_between_technical_stop_loss_and_sell_order_in_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "suppression_by_highs"] = suppression_flag_for_highs
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "number_of_bars_when_we_check_suppression_by_highs"] = number_of_bars_when_we_check_suppression_by_highs
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "suppression_by_closes"] = suppression_flag_for_closes
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "number_of_bars_when_we_check_suppression_by_closes"] = number_of_bars_when_we_check_suppression_by_closes
            #
            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)
            #
            #     df_with_level_atr_bpu_bsu_etc.at[0, "asset_type"] = asset_type
            #     df_with_level_atr_bpu_bsu_etc.at[0, "maker_fee"] = maker_fee
            #     df_with_level_atr_bpu_bsu_etc.at[0, "taker_fee"] = taker_fee
            #     df_with_level_atr_bpu_bsu_etc.at[0, "url_of_trading_pair"] = url_of_trading_pair
            #     df_with_level_atr_bpu_bsu_etc.at[0, "number_of_available_bars"] = number_of_available_days
            #     try:
            #         df_with_level_atr_bpu_bsu_etc.at[0, "trading_pair_is_traded_with_margin"] = \
            #             get_bool_if_asset_is_traded_with_margin(table_with_ohlcv_data_df)
            #     except:
            #         traceback.print_exc()
            # except:
            #     traceback.print_exc()
            #
            # # try:
            # #     #############################################
            # #     # add info to dataframe about whether level was broken on other exchanges
            # #     df_with_level_atr_bpu_bsu_etc = fill_df_with_info_if_atl_was_broken_on_other_exchanges(stock_name,
            # #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_0000,
            # #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_1600,
            # #                                                                                            table_with_ohlcv_data_df,
            # #                                                                                            engine_for_ohlcv_data_for_stocks_0000,
            # #                                                                                            engine_for_ohlcv_data_for_stocks_1600,
            # #                                                                                            all_time_low,
            # #                                                                                            list_of_tables_in_ohlcv_db_1600,
            # #                                                                                            df_with_level_atr_bpu_bsu_etc,
            # #                                                                                            0)
            # # except:
            # #     traceback.print_exc()
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker_last_column"] = stock_name
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker_will_be_traced_and_position_entered"] = False
            #
            # side = "sell"
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "side"] = side
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "stop_loss_is_technical"] = False
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "stop_loss_is_calculated"] = False
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "market_or_limit_stop_loss"] = 'market'
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "market_or_limit_take_profit"] = 'limit'
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "position_size"] = 0
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_x_to_one"] = 3
            #
            # # df_with_level_atr_bpu_bsu_etc.to_sql(
            # #     table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be,
            # #     engine_for_db_where_ticker_which_may_have_breakout_situations,
            # #     if_exists='append')
            # # print_df_to_file(df_with_level_atr_bpu_bsu_etc,
            # #                  'current_rebound_breakout_and_false_breakout')

        except:
            traceback.print_exc()

    # string_for_output = f"Список инструментов, которые сформировали модель ПРОБОЙ исторического минимума (с подтверждением)." \
    #                     f"Вход на следующий день после пробоя:\n" \
    #                     f"{list_of_stocks_which_broke_atl}\n\n"
    # # Use the function to create a text file with the text
    # # in the subdirectory "current_rebound_breakout_and_false_breakout"
    # create_text_file_and_writ_text_to_it(string_for_output,
    #                                      'current_rebound_breakout_and_false_breakout')


    print("list_of_stocks_which_broke_ath")
    print(list_of_stocks_which_broke_ath)
    print("list_of_stocks_which_broke_atl")
    print(list_of_stocks_which_broke_atl)

    #check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def get_base_slash_quote_from_stock_name_with_underscore_between_base_and_quote_and_exchange(
        stock_name_with_underscore_between_base_and_quote_and_exchange):
    base_underscore_quote=\
        stock_name_with_underscore_between_base_and_quote_and_exchange.split("_on_")[0]
    base_slash_quote=base_underscore_quote.replace("_","/")
    return base_slash_quote

def update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,column_name,cell_value):

    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
    print("column_number_of_trade_status")
    print(column_number_of_trade_status)
    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
def update_one_cell_in_google_spreadsheet(row_index,column_number_of_trade_status,cell_value):
    json_file_name = 'aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # path_to_dir_where_json_file_is = os.path.join(os.getcwd(),
    #                                               '/home/alex/PycharmProjects/crypto_trading_semi_auto_bot_00_00_utc/datasets/',
    #                                               'json_key_for_google')
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Define the path to the JSON file relative to the script's directory
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')

    path_to_json = os.path.join(path_to_dir_where_json_file_is, json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, scope)
    gc = gspread.authorize(credentials)
    print("authorize ok!7")

    # Open the spreadsheet by its title
    spread_sheet_title="streamlit_app_google_sheet"
    spreadsheet = gc.open(spread_sheet_title)

    # Check if the worksheet exists
    # date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_models"
    worksheet = None
    for ws in spreadsheet.worksheets():
        if ws.title == worksheet_title:
            worksheet = ws
            print(f'Worksheet "{worksheet_title}" found!')
            break

    # You can also directly get the values as a list of lists
    worksheet.update_cell(row_index,column_number_of_trade_status,cell_value)
    print("cell_updated")

    # values_list = worksheet.get_all_values()
    #
    # for cell in values_list:
    #     print("cell1")
    #     print(cell)
    #     if cell.row == row_index and cell.col == column_name:  # Replace <column_number_of_trade_status> with the actual column number of "trade_status"
    #         cell.value = cell_value
    #
    # # Update the worksheet with the new value
    # worksheet.update_cells(values_list)

def fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed(spread_sheet_title):
    df_with_bfr = fetch_dataframe_from_google_spreadsheet(spread_sheet_title)

    # if columns in the bfr dataframe are str we convert them to bool
    column_name_list_which_must_be_converted_from_str_to_bool = \
        ["stop_loss_is_technical", "stop_loss_is_calculated", "spot_without_margin", "margin",
         "cross_margin", "isolated_margin", "include_last_day_in_bfr_model_assessment",
         "trading_pair_is_traded_with_margin", "spot_asset_also_available_as_swap_contract_on_same_exchange",
         "suppression_by_closes", "suppression_by_lows"]
    for column_name in column_name_list_which_must_be_converted_from_str_to_bool:
        try:
            df_with_bfr = convert_column_to_boolean(df_with_bfr, column_name)
        except:
            traceback.print_exc()
    return df_with_bfr
def fetch_dataframe_from_google_spreadsheet(spread_sheet_title):
    json_file_name = 'aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # path_to_dir_where_json_file_is = os.path.join(os.getcwd(),
    #                                               '/home/alex/PycharmProjects/crypto_trading_semi_auto_bot_00_00_utc/datasets/',
    #                                               'json_key_for_google')
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Define the path to the JSON file relative to the script's directory
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')
    path_to_json = os.path.join(path_to_dir_where_json_file_is, json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, scope)
    gc = gspread.authorize(credentials)
    print("authorize ok!8")

    print("spread_sheet_title")
    print(spread_sheet_title)
    print("going to sleep for 10 sec")
    time.sleep(10)
    # Open the spreadsheet by its title
    # spread_sheet_title="copy_of_streamlit_app_google_sheet"
    spreadsheet = gc.open(spread_sheet_title)

    # Check if the worksheet exists
    # date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_models"
    worksheet = None
    for ws in spreadsheet.worksheets():
        if ws.title == worksheet_title:
            worksheet = ws
            print(f'Worksheet "{worksheet_title}" found!')
            break

    # Convert the data in the worksheet to a DataFrame
    data = worksheet.get_all_values()
    # Assuming 'data' is the list of lists obtained from the worksheet
    df_from_sheet = pd.DataFrame(data[1:], columns=data[0])
    df_from_sheet = convert_commas_to_points(df_from_sheet)
    df_from_sheet = convert_string_boolean(df_from_sheet)

    print("df_from_sheet1")
    print(df_from_sheet)

    return df_from_sheet

def convert_commas_to_points(df):
    # Define a function to handle conversion
    def convert_value(value):
        if isinstance(value, str) and ',' in value:
            try:
                return float(value.replace(',', '.'))
            except ValueError:
                return value  # Return the original value if the conversion fails
        else:
            return value  # Return the original value if it's not a string with a comma

    # Apply the conversion to the entire DataFrame using applymap
    return df.map(convert_value)

def convert_string_boolean(df):
    # Replace string values with boolean values
    df.replace({'TRUE': True, 'FALSE': False}, inplace=True)
    return df
if __name__=="__main__":
    # stock_name='BTC_USDT_on_binance'

    # database_name = "levels_formed_by_highs_and_lows_for_cryptos_0000"
    # df_with_bfr=\
    #     build_entire_df_of_assets_which_will_be_used_for_position_entry(database_name)

    spread_sheet_title = 'streamlit_app_google_sheet'
    df_with_bfr = fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed(
        spread_sheet_title)
    last_df_with_bfr_was_fetched_at = datetime.datetime.now()
    # interpreter = sys.executable

    while True:


        current_timestamp = datetime.datetime.now()
        # difference_between_current_timestamp_and_when_df_was_last_fetched = current_timestamp - last_df_with_bfr_was_fetched_at
        # print("difference_between_current_timestamp_and_when_df_was_last_fetched")
        # print(difference_between_current_timestamp_and_when_df_was_last_fetched)
        # if difference_between_current_timestamp_and_when_df_was_last_fetched.total_seconds() >= 10:
        spread_sheet_title = 'streamlit_app_google_sheet'
        df_with_bfr = fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed(
            spread_sheet_title)
            # last_df_with_bfr_was_fetched_at = datetime.datetime.now()

        # utc_position_entry_time_list = list(df_with_bfr["utc_position_entry_time"])
        # Remove seconds and keep only hours and minutes
        # utc_position_entry_time_list_without_seconds = [time_str.rsplit(':', 1)[0] for time_str in
        #                                                 utc_position_entry_time_list]
        # print("utc_position_entry_time_list")
        # print(utc_position_entry_time_list)

        # Assuming your DataFrame is named df_with_bfr

        # current_utc_time = datetime.datetime.now(timezone.utc).strftime('%H:%M')
        # current_utc_time_without_leading_zero = datetime.datetime.now(timezone.utc).strftime('%-H:%M')
        # print("current_utc_time")
        # print(current_utc_time)
        # print("utc_position_entry_time_list_without_seconds")
        # print(utc_position_entry_time_list_without_seconds)
        #delete "not" when in production
        # if current_utc_time in utc_position_entry_time_list_without_seconds or\
        #         current_utc_time_without_leading_zero in utc_position_entry_time_list_without_seconds:
            #next bar print time has arrived
            # print("desired time is now")
            # iterate over each row in df_with_bfr and verify that pair still satisfies the desired
            # criteria for bfr
        for row_index, row in df_with_bfr.iterrows():
            # print("row1")
            # print(pd.DataFrame(row).T.to_string())
            row_df=pd.DataFrame(row).T
            model_type=row_df.loc[row_index,"model"]




            stock_name_with_underscore_between_base_and_quote_and_exchange = \
                row_df.loc[row_index, "ticker"]
            print("stock_name_with_underscore_between_base_and_quote_and_exchange")
            print(stock_name_with_underscore_between_base_and_quote_and_exchange)
            base_slash_quote=\
                get_base_slash_quote_from_stock_name_with_underscore_between_base_and_quote_and_exchange(
                stock_name_with_underscore_between_base_and_quote_and_exchange)

            exchange_id=row_df.loc[row_index, "exchange"]

            include_last_day_in_bfr_model_assessment=False
            include_last_day_in_bfr_model_assessment=row_df.loc[row_index, "include_last_day_in_bfr_model_assessment"]

            trade_status=row_df.loc[row_index, "trade_status"]
            utc_position_entry_time_in_df=row_df.loc[row_index,"utc_position_entry_time"]
            if trade_status!="must_verify_if_bfr_conditions_are_fulfilled":
                print("non of trade_status is equal to must_verify_if_bfr_conditions_are_fulfilled")
                continue
            # if utc_position_entry_time_in_df!=current_utc_time or utc_position_entry_time_in_df!=current_utc_time_without_leading_zero:
            #     continue




            exchange_object = get_exchange_object6(exchange_id)
            advanced_atr_over_this_period = 30
            acceptable_backlash = 0.05
            timeframe = "1d"
            last_bitcoin_price = 30000
            count_min_volume_over_this_many_days = 7
            if model_type == "ПРОБОЙ_ATL_с_подтверждением_вход_на_следующий_день":
                trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day = \
                    verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_the_next_day(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)
                print("trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day")
                print(trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day)

                if trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day:
                    trade_status="bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status="bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)




            elif model_type == "ПРОБОЙ_ATH_с_подтверждением_вход_на_следующий_день":
                trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day = \
                    verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_the_next_day(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)
                print("trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day")
                print(trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day)

                if trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)


            elif model_type == "ПРОБОЙ_ATL_с_подтверждением_вход_на_2й_день":
                trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two = \
                    verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)
                print("trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two")
                print(trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two)

                if trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)

                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)


            elif model_type == "ПРОБОЙ_ATH_с_подтверждением_вход_на_2й_день":
                trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two = \
                    verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_day_two(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)
                print("trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two")
                print(trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two)

                if trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index+2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)

            elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATL_1Б":
                trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar = \
                    verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_one_bar(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)


                if trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)

            elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATH_1Б":
                trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar = \
                    verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_one_bar(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)

                print("trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar")
                print(trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar)

                if trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)


            elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATL_2Б":
                trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars = \
                    verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_two_bars(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)



                if trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)

            elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATH_2Б":
                trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars = \
                    verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_two_bars(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period)

                print("trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars")
                print(trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars)

                if trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)


            elif model_type == "ОТБОЙ_от_ATL":
                trading_pair_is_ready_for_rebound_situations_off_atl = \
                    verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_atl(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period, acceptable_backlash)

                print("trading_pair_is_ready_for_rebound_situations_off_atl")
                print(trading_pair_is_ready_for_rebound_situations_off_atl)

                if trading_pair_is_ready_for_rebound_situations_off_atl:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)

            elif model_type == "ОТБОЙ_от_ATH":
                trading_pair_is_ready_for_rebound_situations_off_ath = \
                    verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_ath(
                        include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                        last_bitcoin_price, advanced_atr_over_this_period, acceptable_backlash)
                print("trading_pair_is_ready_for_rebound_situations_off_ath")
                print(trading_pair_is_ready_for_rebound_situations_off_ath)

                if trading_pair_is_ready_for_rebound_situations_off_ath:
                    trade_status = "bfr_conditions_are_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)
                else:
                    trade_status = "bfr_conditions_are_not_met"
                    cell_value = trade_status
                    column_name = "trade_status"
                    column_number_of_trade_status = df_with_bfr.columns.get_loc(column_name) + 1
                    print("column_number_of_trade_status")
                    print(column_number_of_trade_status)
                    update_one_cell_in_google_spreadsheet(row_index + 2, column_number_of_trade_status, cell_value)


            else:
                print("no_bfr_model_yet")

            df_with_bfr["trade_status"].iat[row_index]=trade_status
            print("df_with_bfr1")
            print(df_with_bfr.to_string())
            # time.sleep(100000)



            # time.sleep(20)
            # print("i am sleeping for 20 sec")

    # verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(stock_name)