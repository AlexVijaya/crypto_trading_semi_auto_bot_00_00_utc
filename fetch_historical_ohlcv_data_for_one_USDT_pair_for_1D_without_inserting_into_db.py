# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
import asyncio
import os
import sys
import time
import traceback
import db_config
import sqlalchemy
import psycopg2
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# import talib
import datetime
import ccxt
# import ccxt.async_support as ccxt  # noqa: E402
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from pytz import timezone
import pprint
from verify_that_asset_has_enough_volume import check_volume
from get_info_from_load_markets import get_asset_type2
from get_info_from_load_markets import if_margin_true_for_an_asset
from get_info_from_load_markets import get_fees
from get_info_from_load_markets import fetch_huobipro_ohlcv
from get_info_from_load_markets import get_active_trading_pairs_from_huobipro
from get_info_from_load_markets import get_exchange_object_and_limit_of_daily_candles
from get_info_from_load_markets import get_exchange_object
from get_info_from_load_markets import get_exchange_url
from get_info_from_load_markets import get_maker_taker_fees_for_huobi
from get_info_from_load_markets import get_limit_of_daily_candles_original_limits
from get_info_from_load_markets import fetch_entire_ohlcv
from get_info_from_load_markets import get_perpetual_swap_url
from  current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import get_list_of_tables_in_db
from update_historical_USDT_pairs_for_1D_next_bar_print_utc_time_00 import connect_to_postgres_db_without_deleting_it_first
from get_info_from_load_markets import get_exchange_object2

def get_maker_and_taker_fees_and_is_shortable(exchange, trading_pair):

    maker_fee=np.nan
    taker_fee=np.nan
    is_shortable=np.nan

    # Get the symbol for the specified trading pair
    symbol = exchange.markets[trading_pair]['symbol']

    # Check if API keys are required for the exchange
    if exchange.apiKey is None or exchange.secret is None:
        return maker_fee, taker_fee, is_shortable
    
    # Retrieve the exchange info for the specified symbol
    exchange_info = exchange.load_trading_limits(symbol)
    print(f"exchange_info_for_{symbol}")
    pprint.pprint(exchange_info)
    #
    # print("exchange.markets[symbol]")
    # pprint.pprint(exchange.markets[symbol])

    # Extract the maker and taker fees
    maker_fee = exchange_info['maker']
    taker_fee = exchange_info['taker']



    # Check if the symbol is shortable
    is_shortable = exchange.markets[symbol].get('short', False)


    # Return the results as a tuple
    return maker_fee, taker_fee, is_shortable

def connect_to_postgres_db_with_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database
    connection=None

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )
        try:
            connection=engine.connect ()
        except:
            traceback.print_exc()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )

    try:
        connection = engine.connect ()
    except:
        traceback.print_exc()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def add_time_of_next_candle_print_to_df(data_df):
    try:
        # Set the timezone for Moscow
        moscow_tz = timezone('Europe/Moscow')
        almaty_tz = timezone('Asia/Almaty')
        data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
        data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
        # Convert the "open_time" column from UTC to Moscow time
        data_df['open_time_msk'] =\
            data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)

        data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')

        # Convert the "open_time_datatime_format" column from UTC to Almaty time
        data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')

        # Create a new column called "open_time_almaty_time" that contains the time in string format
        data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
    except:
        traceback.print_exc()

def connect_to_postres_db_and_delete_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        create_database ( engine.url )
        print ( f'new database created for {engine}' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def check_if_stable_coin_is_the_first_part_of_ticker(trading_pair):
    trading_pair_has_stable_coin_name_as_its_first_part=False
    stablecoin_tickers = [
    "USDT_","USDC_","BUSD_","DAI_","FRAX_","TUSD_","USDP_","USDD_",
    "GUSD_","XAUT_","USTC_","EURT_","LUSD_","ALUSD_","EURS_","USDX_",
    "MIM_","sEUR_","WBTC_","sGBP_","sJPY_","sKRW_","sAUD_","GEM_",
    "sXAG_","sXAU_","sXDR_","sBTC_","sETH_","sCNH_","sCNY_","sHKD_",
    "sSGD_","sCHF_","sCAD_","sNZD_","sLTC_","sBCH_","sBNB_","sXRP_",
    "sADA_","sLINK_","sXTZ_","sDOT_","sFIL_","sYFI_","sCOMP_","sAAVE_",
    "sSNX_","sMKR_","sUNI_","sBAL_","sCRV_","sLEND_","sNEXO_","sUMA_",
    "sMUST_","sSTORJ_","sREN_","sBSV_","sDASH_","sZEC_","sEOS_","sXTZ_",
    "sATOM_","sVET_","sTRX_","sADA_","sDOGE_","sDGB_"
]

    for first_part_in_trading_pair in stablecoin_tickers:
        if first_part_in_trading_pair in trading_pair:
            trading_pair_has_stable_coin_name_as_its_first_part=True
            break
        else:
            continue
    return trading_pair_has_stable_coin_name_as_its_first_part




new_counter=0
not_active_pair_counter = 0
list_of_inactive_pairs=[]
list_of_newly_added_trading_pairs=[]
def check_exchange_object_is_none_use_isnone(exchange_object):
    if np.isnan(exchange_object):
        return True
    else:
        return False

def check_exchange_object_is_none(exchange_object):
    if exchange_object is None:
        return True
    else:
        return False
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



def convert_string_timeframe_into_seconds(timeframe):
    timeframe_in_seconds=0
    if timeframe=='1d':
        timeframe_in_seconds=86400
    if timeframe == '12h':
        timeframe_in_seconds = 86400/2
    if timeframe == '6h':
        timeframe_in_seconds = 86400/4
    if timeframe == '4h':
        timeframe_in_seconds = 86400/6
    if timeframe == '8h':
        timeframe_in_seconds = 86400/3
    return timeframe_in_seconds

def get_real_time_bitcoin_price():
    binance = ccxt.binance()
    btc_ticker = binance.fetch_ticker('BTC/USDT')
    last_bitcoin_price=btc_ticker['close']
    return last_bitcoin_price


if __name__=="__main__":
    timeframe='1d'

    last_bitcoin_price=30000
    # last_bitcoin_price=get_real_time_bitcoin_price()
    print("last_bitcoin_price")
    print(last_bitcoin_price)
    # database_name="ohlcv_1d_data_for_usdt_pairs_0000"
    # database_name_for_low_volume_pairs = "ohlcv_1d_data_for_low_volume_usdt_pairs_0000"
    ticker="BTC/USDT_on_binance"
    data_df=fetch_one_ohlcv_table(ticker,timeframe,last_bitcoin_price)

    print("final_data_df")
    print(data_df.to_string())
#asyncio.run(get_hisorical_data_from_exchange_for_many_symbols_and_exchanges())
