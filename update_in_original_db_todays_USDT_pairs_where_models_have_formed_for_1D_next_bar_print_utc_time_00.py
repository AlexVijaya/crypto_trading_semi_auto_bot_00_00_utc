# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
from sqlalchemy import inspect
import asyncio
import os
import sys
import time
import traceback
import db_config
from sqlalchemy import text
import sqlalchemy
import psycopg2
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# import talib
import datetime
import datetime as dt
import ccxt
# import ccxt.async_support as ccxt  # noqa: E402

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from pytz import timezone
from verify_that_asset_has_enough_volume import check_volume
from get_info_from_load_markets import get_limit_of_daily_candles_original_limits
from get_info_from_load_markets import get_exchange_object6
from constant_update_of_ohlcv_db_to_plot_later import get_list_of_exchange_ids_for_todays_pairs
from constant_update_of_ohlcv_db_to_plot_later import get_list_of_todays_trading_pairs
from verify_that_models_have_been_formed_by_next_bar_print import get_todays_exchanges_and_pairs_list
def is_pair_active(ohlcv_data_several_last_rows_df,
                   last_timestamp_in_df,
                   timeframe,
                   trading_pair,
                   exchange):
    current_timestamp = time.time()

    timeframe_in_seconds = convert_string_timeframe_into_seconds(timeframe)
    print("current_timestamp")
    print(current_timestamp)
    print("last_timestamp_in_df")
    print(last_timestamp_in_df)
    print("abs(current_timestamp - last_timestamp_in_df)")
    print(abs(current_timestamp - last_timestamp_in_df))
    print("timeframe_in_seconds")
    print(timeframe_in_seconds)

    if abs(current_timestamp - last_timestamp_in_df) < (timeframe_in_seconds):
        return True
    else:
        print(f"inactive trading pair {trading_pair} on {exchange}")
        return False
def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
def drop_table(table_name, engine):
    try:
        conn = engine.connect()
        query = text(f'''DROP TABLE IF EXISTS "{table_name}"''')
        conn.execute(query)
        conn.close()
    except:
        traceback.print_exc()


def connect_to_postgres_db_with_deleting_it_first(database):
    import db_config
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
        try:
            create_database ( engine.url )
        except:
                        traceback.print_exc()
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
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

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

# def connect_to_postgres_db_with_deleting_it_first(database):
#     dialect = db_config.dialect
#     driver = db_config.driver
#     password = db_config.password
#     user = db_config.user
#     host = db_config.host
#     port = db_config.port
#
#     dummy_database = db_config.dummy_database
#
#     engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
#                              isolation_level = 'AUTOCOMMIT' ,
#                              echo = False,
#                              pool_pre_ping = True,
#                              pool_size = 20 , max_overflow = 0,
#                              connect_args={'connect_timeout': 10} )
#     print ( f"{engine} created successfully" )
#
#     # Create database if it does not exist.
#     if not database_exists ( engine.url ):
#         create_database ( engine.url )
#         print ( f'new database created for {engine}' )
#         connection=engine.connect ()
#         print ( f'Connection to {engine} established after creating new database' )
#
#     if database_exists ( engine.url ):
#         print("database exists ok")
#
#         engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
#                                  isolation_level = 'AUTOCOMMIT' , echo = False )
#         try:
#             engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
#         except:
#             pass
#         try:
#             engine.execute ( f'''
#                                 ALTER DATABASE {database} allow_connections = off;
#                                 SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
#
#                             ''' )
#         except:
#             pass
#         try:
#             engine.execute ( f'''DROP DATABASE {database};''' )
#         except:
#             pass
#
#         engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
#                                  isolation_level = 'AUTOCOMMIT' , echo = False )
#         create_database ( engine.url )
#         print ( f'new database created for {engine}' )
#
#     connection = engine.connect ()
#
#     print ( f'Connection to {engine} established. Database already existed.'
#             f' So no new db was created' )
#     return engine , connection

def get_number_of_last_index(ohlcv_data_df):
    number_of_last_index = ohlcv_data_df["index"].max()
    return number_of_last_index
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

def convert_index_to_unix_timestamp(df):
    # convert the index to datetime object
    df.index = pd.to_datetime(df.index)

    # convert the datetime object to Unix timestamp in milliseconds
    df.index = df.index.astype(int) // 10**6

    return df
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

def get_last_timestamp_from_ohlcv_table(ohlcv_data_df):
    last_timestamp = ohlcv_data_df["Timestamp"].iat[-1]
    return last_timestamp

def get_last_index_column_value_from_ohlcv_table(ohlcv_data_df):
    last_index = ohlcv_data_df["index"].iat[-1]
    return last_index

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
def select_rows_excluding_first(df):
    return df.iloc[1:]
def get_first_timestamp_from_ohlcv_table(ohlcv_data_df):
    first_timestamp = ohlcv_data_df["Timestamp"].iat[0]
    return first_timestamp


def get_date_without_time_from_timestamp(timestamp):
    open_time = \
        dt.datetime.fromtimestamp(timestamp)
    # last_timestamp = historical_data_for_crypto_ticker_df["Timestamp"].iloc[-1]
    # last_date_with_time = historical_data_for_crypto_ticker_df["open_time"].iloc[-1]
    # print ( "type(last_date_with_time)\n" , type ( last_date_with_time ) )
    # print ( "last_date_with_time\n" , last_date_with_time )
    date_with_time = open_time.strftime("%Y/%m/%d %H:%M:%S")
    date_without_time = date_with_time.split(" ")
    print("date_with_time\n", date_without_time[0])
    date_without_time = date_without_time[0]
    print("date_without_time\n", date_without_time)
    return date_without_time



new_counter=0
not_active_pair_counter = 0
list_of_inactive_pairs=[]

def get_hisorical_data_from_exchange_for_many_symbols(exchange_dict,last_bitcoin_price,exchange,
                                                            engine,timeframe='1d'):
    print("exchange=",exchange)
    global new_counter
    global list_of_inactive_pairs
    global not_active_pair_counter
    exchange_object=""
    limit_of_daily_candles = 1000
    try:
        print("exchange1=", exchange)
        exchange_object=get_exchange_object6(exchange)




        exchange_object.enableRateLimit = True
    except:
        traceback.print_exc()
    list_of_updated_trading_pairs = []

    try:
        # connection_to_usdt_trading_pairs_ohlcv = \
        #     sqlite3.connect ( os.path.join ( os.getcwd () ,
        #                                      "datasets" ,
        #                                      "sql_databases" ,
        #                                      "all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )

        exchange_object.load_markets ()
        # list_of_all_symbols_from_exchange=exchange_object.symbols
        # print("list_of_all_symbols_from_exchange")
        # print(list_of_all_symbols_from_exchange)

        list_of_trading_pairs_with_USDT = []
        list_of_trading_pairs_with_USD = []
        list_of_trading_pairs_with_BTC = []


        for trading_pair in exchange_dict[exchange]:
            print(f"exchange_dict[{exchange}]")
            print(exchange_dict[exchange])

            try:
                trading_pair_with_underscore = trading_pair.replace('/', "_")
                string_for_comparison_pair_plus_exchange = \
                    f"{trading_pair_with_underscore}" + "_on_" + f"{exchange}"

                if string_for_comparison_pair_plus_exchange in (list_of_crypto_plus_exchange):
                    print("string_for_comparison_pair_plus_exchange")
                    print(string_for_comparison_pair_plus_exchange)
                    # print("list_of_crypto_plus_exchange")
                    # print(list_of_crypto_plus_exchange)

                    # if string_for_comparison_pair_plus_exchange!="1INCH_USDT:USDT_on_gateio":
                    #     continue



                    table_with_ohlcv_data_df = \
                        pd.read_sql_query(f'''select * from "{string_for_comparison_pair_plus_exchange}"''',
                                          engine)

                    last_timestamp_in_original_table = get_last_timestamp_from_ohlcv_table(table_with_ohlcv_data_df)



                    # #delete last row because it is not a complete bar
                    last_index=get_last_index_column_value_from_ohlcv_table(table_with_ohlcv_data_df)
                    engine.execute(f'''DELETE FROM public."{string_for_comparison_pair_plus_exchange}" WHERE "index" >= {last_index};''')

                    # drop the last row from df
                    table_with_ohlcv_data_df = table_with_ohlcv_data_df.drop(table_with_ohlcv_data_df.index[-1])



                    last_timestamp = get_last_timestamp_from_ohlcv_table(table_with_ohlcv_data_df)
                    print(f"last_timestamp for {trading_pair} on {exchange}")
                    print(last_timestamp)
                    date_without_time = get_date_without_time_from_timestamp(last_timestamp)
                    number_of_last_index_in_ohlcv_data_df = \
                        get_number_of_last_index(table_with_ohlcv_data_df)
                    # if not ('active' in exchange_object.markets[trading_pair]):
                    #     drop_table(string_for_comparison_pair_plus_exchange, engine)
                    #     print(f"{string_for_comparison_pair_plus_exchange} is not active")
                    #     continue
                    # if not (exchange_object.markets[trading_pair]['active']):
                    #     drop_table(string_for_comparison_pair_plus_exchange, engine)
                    #     print(f"{string_for_comparison_pair_plus_exchange} is not active")
                    #     continue
                    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']

                    # if exchange!="binance" and trading_pair!="BETA/BUSD":
                    #     continue
                    data=np.nan
                    data_for_btcex=np.nan
                    print("trading_pair20")
                    print(trading_pair)
                    if "_" in trading_pair:
                        trading_pair=trading_pair.replace("_","/")
                    try:
                        if exchange=="btcex":
                            timeframe = "12h"
                            data_for_btcex = exchange_object.fetch_ohlcv(trading_pair, timeframe, since=int(last_timestamp * 1000))
                            print("data_for_btcex")
                            print(data_for_btcex)

                        else:

                            data = exchange_object.fetch_ohlcv(trading_pair,
                                                                        timeframe,since=int(last_timestamp * 1000))


                    except:
                        traceback.print_exc()

                    ohlcv_data_several_last_rows_df=pd.DataFrame()
                    if  exchange != "btcex":
                        ohlcv_data_several_last_rows_df = \
                            pd.DataFrame(data, columns=header).set_index('Timestamp')
                        print(f"ohlcv_data_several_last_rows_df8 for {trading_pair} on {exchange}")
                        print(ohlcv_data_several_last_rows_df)
                        trading_pair = trading_pair.replace("/", "_")

                        ohlcv_data_several_last_rows_df['ticker'] = trading_pair
                        ohlcv_data_several_last_rows_df['exchange'] = exchange
                        ohlcv_data_several_last_rows_df['trading_pair'] = trading_pair + "_on_" + exchange

                        ohlcv_data_several_last_rows_df['volume*low'] = ohlcv_data_several_last_rows_df['volume']*ohlcv_data_several_last_rows_df['low']
                        ohlcv_data_several_last_rows_df['volume*close'] = ohlcv_data_several_last_rows_df['volume'] * \
                                                                        ohlcv_data_several_last_rows_df['close']

                    print(f"exchange_is_{exchange}")
                    if exchange == "btcex":
                        print("btcex1")
                        # header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                        ohlcv_data_several_last_rows_df = pd.DataFrame(data_for_btcex, columns=header)
                        print("btcex2")
                        ohlcv_data_several_last_rows_df.drop_duplicates(subset=["Timestamp"], keep="first", inplace=True)
                        ohlcv_data_several_last_rows_df.sort_values("Timestamp", inplace=True)
                        ohlcv_data_several_last_rows_df = ohlcv_data_several_last_rows_df.set_index('Timestamp')
                        ohlcv_data_several_last_rows_df = resample_dataframe_daily(ohlcv_data_several_last_rows_df)
                        # print("data_df_for_btcex")
                        # print(data_df_for_btcex.to_string())
                        ohlcv_data_several_last_rows_df = convert_index_to_unix_timestamp(ohlcv_data_several_last_rows_df)
                        trading_pair = trading_pair.replace("/", "_")
                        ohlcv_data_several_last_rows_df['ticker'] = trading_pair
                        ohlcv_data_several_last_rows_df['exchange'] = exchange
                        ohlcv_data_several_last_rows_df['trading_pair'] = trading_pair + "_on_" + exchange

                        ohlcv_data_several_last_rows_df['volume*low'] = ohlcv_data_several_last_rows_df['volume'] * \
                                                                        ohlcv_data_several_last_rows_df['low']
                        ohlcv_data_several_last_rows_df['volume*close'] = ohlcv_data_several_last_rows_df['volume'] * \
                                                                          ohlcv_data_several_last_rows_df['close']

                        print("ohlcv_data_several_last_rows_df_btcex")
                        print(ohlcv_data_several_last_rows_df.to_string())
                        # ohlcv_data_several_last_rows_df=select_rows_excluding_first(ohlcv_data_several_last_rows_df)
                        # print("ohlcv_data_several_last_rows_df_btcex_without_first_row")
                        # print(ohlcv_data_several_last_rows_df.to_string())


                    # если  в крипе мало данных , то ее не добавляем
                    # if len(ohlcv_data_several_last_rows_df) < 10:
                    #     continue

                    # # slice last 30 days for volume calculation
                    # min_volume_over_these_many_last_days = 30
                    # data_df_n_days_slice = ohlcv_data_several_last_rows_df.iloc[:-1].tail(min_volume_over_these_many_last_days).copy()
                    #
                    # data_df_n_days_slice["volume_by_close"] = \
                    #     data_df_n_days_slice["volume"] * data_df_n_days_slice["close"]
                    # print("data_df_n_days_slice")
                    # print(data_df_n_days_slice)
                    # min_volume_over_last_n_days_in_dollars = min(data_df_n_days_slice["volume_by_close"])
                    # print("min_volume_over_last_n_days_in_dollars")
                    # print(min_volume_over_last_n_days_in_dollars)
                    # if min_volume_over_last_n_days_in_dollars < 2 * last_bitcoin_price:
                    #     continue



                    current_timestamp = time.time()
                    last_timestamp_in_df = ohlcv_data_several_last_rows_df.tail(1).index.item() / 1000.0
                    print("current_timestamp=", current_timestamp)
                    print("ohlcv_data_several_last_rows_df.tail(1).index.item()=",
                          ohlcv_data_several_last_rows_df.tail(1).index.item() / 1000.0)

                    # check if the pair is active
                    timeframe_in_seconds = convert_string_timeframe_into_seconds(timeframe)
                    if not abs(current_timestamp - last_timestamp_in_df) < (timeframe_in_seconds):
                        print(f"not quite active trading pair {trading_pair} on {exchange}")
                        not_active_pair_counter = not_active_pair_counter + 1
                        print("not_active_pair_counter=", not_active_pair_counter)
                        list_of_inactive_pairs.append(f"{trading_pair}_on_{exchange}")


                        # # drop table from ohlcv db if the pair is inactive
                        # drop_table(string_for_comparison_pair_plus_exchange, engine)

                        # continue
                    print("1program got here")
                    # try:
                    #     ohlcv_data_several_last_rows_df['Timestamp'] = \
                    #         [datetime.datetime.timestamp(float(x)) for x in ohlcv_data_several_last_rows_df.index]
                    #
                    # except Exception as e:
                    #     print("error_message")
                    #     traceback.print_exc()
                    #     time.sleep(3000000)
                    ohlcv_data_several_last_rows_df["Timestamp"] = ohlcv_data_several_last_rows_df.index

                    try:
                        ohlcv_data_several_last_rows_df["open_time"] = ohlcv_data_several_last_rows_df[
                            "Timestamp"].apply(
                            lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
                    except Exception as e:
                        print("error_message")
                        traceback.print_exc()

                    ohlcv_data_several_last_rows_df['Timestamp'] = ohlcv_data_several_last_rows_df["Timestamp"] / 1000.0
                    # time.sleep(3000000)
                    print("2program got here")
                    # ohlcv_data_several_last_rows_df["open_time"] = ohlcv_data_several_last_rows_df.index
                    print("3program got here")
                    ohlcv_data_several_last_rows_df.index = range(0, len(ohlcv_data_several_last_rows_df))
                    print("4program got here")
                    # ohlcv_data_several_last_rows_df = populate_dataframe_with_td_indicator ( ohlcv_data_several_last_rows_df )

                    try:
                        ohlcv_data_several_last_rows_df['open_time'] = pd.to_datetime(
                            ohlcv_data_several_last_rows_df['open_time'])
                        ohlcv_data_several_last_rows_df['open_time_without_date'] = \
                            ohlcv_data_several_last_rows_df['open_time'].dt.strftime('%H:%M:%S')
                    except:
                        traceback.print_exc()

                    ohlcv_data_several_last_rows_df["exchange"] = exchange
                    print("5program got here")

                    asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                        get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)

                    ohlcv_data_several_last_rows_df["asset_type"] = asset_type
                    ohlcv_data_several_last_rows_df["maker_fee"] = maker_fee
                    ohlcv_data_several_last_rows_df["taker_fee"] = taker_fee
                    ohlcv_data_several_last_rows_df["url_of_trading_pair"] = url_of_trading_pair

                    ####################################
                    try:
                        spot_asset_also_available_as_swap_contract_on_same_exchange_bool = \
                        table_with_ohlcv_data_df["spot_asset_also_available_as_swap_contract_on_same_exchange"].iat[0]
                        ohlcv_data_several_last_rows_df[
                            'spot_asset_also_available_as_swap_contract_on_same_exchange'] = spot_asset_also_available_as_swap_contract_on_same_exchange_bool
                    except:
                        ohlcv_data_several_last_rows_df[
                            'spot_asset_also_available_as_swap_contract_on_same_exchange'] = np.nan

                    try:
                        url_of_swap_contract_if_it_exists_bool = \
                        table_with_ohlcv_data_df["url_of_swap_contract_if_it_exists"].iat[0]
                        ohlcv_data_several_last_rows_df[
                            'url_of_swap_contract_if_it_exists'] = url_of_swap_contract_if_it_exists_bool
                    except:
                        ohlcv_data_several_last_rows_df['url_of_swap_contract_if_it_exists'] = np.nan
                    ###################################


                    try:
                        if_margin_true_for_an_asset_bool=table_with_ohlcv_data_df["trading_pair_is_traded_with_margin"].iat[0]
                        ohlcv_data_several_last_rows_df['trading_pair_is_traded_with_margin'] = if_margin_true_for_an_asset_bool
                    except:
                        ohlcv_data_several_last_rows_df['trading_pair_is_traded_with_margin'] = np.nan


                    # ohlcv_data_several_last_rows_df["short_name"] = np.nan
                    # print("6program got here")
                    # ohlcv_data_several_last_rows_df["country"] = np.nan
                    # ohlcv_data_several_last_rows_df["long_name"] = np.nan
                    # ohlcv_data_several_last_rows_df["sector"] = np.nan
                    # # ohlcv_data_several_last_rows_df["long_business_summary"] = long_business_summary
                    # ohlcv_data_several_last_rows_df["website"] = np.nan
                    # ohlcv_data_several_last_rows_df["quote_type"] = np.nan
                    # ohlcv_data_several_last_rows_df["city"] = np.nan
                    # ohlcv_data_several_last_rows_df["exchange_timezone_name"] = np.nan
                    # ohlcv_data_several_last_rows_df["industry"] = np.nan
                    # ohlcv_data_several_last_rows_df["market_cap"] = np.nan







                    ohlcv_data_several_last_rows_df.set_index("open_time")
                    add_time_of_next_candle_print_to_df(ohlcv_data_several_last_rows_df)
                    print("100program got here")
                    # trading_pair_has_stablecoin_as_first_part = \
                    #     check_if_stable_coin_is_the_first_part_of_ticker(trading_pair)

                    # if "BUSD/" in trading_pair:
                    #     time.sleep(3000000)
                    # if trading_pair_has_stablecoin_as_first_part:
                    #     print(f"discarded pair due to stable coin being the first part is {trading_pair}")
                    #     continue
                    print(f"ohlcv_data_several_last_rows_df6_for_{string_for_comparison_pair_plus_exchange}")
                    print(ohlcv_data_several_last_rows_df.to_string())
                    print("101program got here")
                    # last_timestamp_in_df = ohlcv_data_several_last_rows_df.tail(1).index.item() / 1000.0
                    last_timestamp_in_df = ohlcv_data_several_last_rows_df["Timestamp"].iat[-1]
                    print("last_timestamp_in_df12")
                    print(last_timestamp_in_df)
                    # last_timestamp_in_df=last_timestamp_in_df/ 1000.0
                    print("102program got here")
                    is_pair_active_bool = is_pair_active(ohlcv_data_several_last_rows_df, last_timestamp_in_df,
                                                         timeframe, trading_pair,
                                                         exchange)
                    print("103program got here")

                    if len(ohlcv_data_several_last_rows_df) <= 1:
                        print("nothing_added")

                        last_timestamp_in_df = last_timestamp_in_original_table
                        is_pair_active_bool = is_pair_active(ohlcv_data_several_last_rows_df, last_timestamp_in_df,
                                                             timeframe, trading_pair,
                                                             exchange)
                        if not is_pair_active_bool:
                            # drop_table(string_for_comparison_pair_plus_exchange, engine)
                            print(f"{string_for_comparison_pair_plus_exchange} dropped1 nothing_added")
                        continue

                    # nothing new is added and the pair is inactive
                    if not is_pair_active_bool:
                        # drop_table(string_for_comparison_pair_plus_exchange, engine)
                        print(f"{string_for_comparison_pair_plus_exchange} dropped2")
                        continue
                    # try:
                    #     ohlcv_data_several_last_rows_df['open_time'] = \
                    #         [datetime.datetime.timestamp(x) for x in ohlcv_data_several_last_rows_df["Timestamp"]]
                    #     # ohlcv_data_several_last_rows_df["open_time"] = ohlcv_data_several_last_rows_df.index
                    # except:
                    #     print("strange_error")
                    #     traceback.print_exc()
                    #
                    #     time.sleep(3000000)

                    print("ohlcv_data_several_last_rows_df11")
                    print(ohlcv_data_several_last_rows_df)

                    # ohlcv_data_several_last_rows_df.set_index("open_time")
                    ohlcv_data_several_last_rows_df.index = \
                        range(number_of_last_index_in_ohlcv_data_df,
                              number_of_last_index_in_ohlcv_data_df + len(ohlcv_data_several_last_rows_df))
                    print("ohlcv_data_several_last_rows_df13")
                    print(ohlcv_data_several_last_rows_df)

                    try:
                        print("ohlcv_data_several_last_rows_df_first_row_is_not_deleted")
                        print(ohlcv_data_several_last_rows_df.to_string())
                        ohlcv_data_several_last_rows_df = ohlcv_data_several_last_rows_df.iloc[1:, :]
                        print("ohlcv_data_several_last_rows_df_first_row_deleted")
                        print(ohlcv_data_several_last_rows_df.to_string())
                    except:
                        traceback.print_exc()
                    list_of_updated_trading_pairs.append(trading_pair)

                    print(f" final_ohlcv_data_several_last_rows_df56 for {trading_pair} on {exchange}")
                    print(ohlcv_data_several_last_rows_df.to_string())
                    ohlcv_data_several_last_rows_df.to_sql(f"{trading_pair}_on_{exchange}",
                                                           engine,
                                                           if_exists='append')

                    # if string_for_comparison_pair_plus_exchange=="1INCH3L_USDT_on_lbank":
                    #     time.sleep(30000000)





                else:
                    continue

                    # print ( "data=" , data )
            except ccxt.base.errors.RequestTimeout:
                print("found ccxt.base.errors.RequestTimeout error inner")
                continue


            except ccxt.RequestTimeout:
                print("found ccxt.RequestTimeout error inner")
                continue


            except Exception as e:
                print(f"problem with {trading_pair} on {exchange}\n", e)
                traceback.print_exc()
                continue
            finally:

                continue

        # connection_to_usdt_trading_pairs_ohlcv.close()

    # except Exception as e:
    #     print ( f"found {e} error outer" )
    #     traceback.print_exc ()
    #
    #     pass



    except Exception as e:
        print(f"problem with {exchange}\n", e)
        traceback.print_exc()

        #await exchange_object.close ()

    finally:
        print("list_of_updated_trading_pairs")
        print(list_of_updated_trading_pairs)


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


def get_list_of_tables_in_db_with_db_as_parameter(database_where_ohlcv_for_cryptos_is):
    '''get list of all tables in db which is given as parameter'''
    engine_for_ohlcv_data_for_cryptos, connection_to_ohlcv_data_for_cryptos = \
        connect_to_postgres_db_without_deleting_it_first(database_where_ohlcv_for_cryptos_is)

    inspector = inspect(engine_for_ohlcv_data_for_cryptos)
    list_of_tables_in_db = inspector.get_table_names()

    return list_of_tables_in_db


def fetch_historical_usdt_pairs_asynchronously(exchange_dict,last_bitcoin_price,engine,exchanges_list,timeframe):
    start=time.perf_counter()
    # exchanges_list=['aax', 'ascendex', 'bequant', 'bibox', 'bigone',
    #                 'binance', 'binancecoinm', 'binanceus', 'binanceusdm',
    #                 'bit2c', 'bitbank', 'bitbay', 'bitbns', 'bitcoincom',
    #                 'bitfinex', 'bitfinex2', 'bitflyer', 'bitforex', 'bitget',
    #                 'bithumb', 'bitmart', 'bitmex', 'bitopro', 'bitpanda', 'bitrue',
    #                 'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bkex',
    #                 'bl3p', 'blockchaincom', 'btcalpha', 'btcbox', 'btcmarkets',
    #                 'btctradeua', 'btcturk', 'buda', 'bw', 'bybit', 'bytetrade',
    #                 'cdax', 'cex', 'coinbase', 'coinbaseprime', 'coinbasepro',
    #                 'coincheck', 'coinex', 'coinfalcon', 'coinflex', 'coinmate',
    #                 'coinone', 'coinspot', 'crex24', 'cryptocom', 'currencycom',
    #                 'delta', 'deribit', 'digifinex', 'eqonex', 'exmo', 'flowbtc',
    #                 'fmfwio', 'ftx', 'ftxus', 'gateio', 'gemini', 'hitbtc', 'hitbtc3',
    #                 'hollaex', 'huobi', 'huobijp', 'huobipro', 'idex',
    #                 'independentreserve', 'indodax', 'itbit', 'kraken', 'kucoin',
    #                 'kucoinfutures', 'kuna', 'latoken', 'lbank', 'lbank2', 'liquid',
    #                 'luno', 'lykke', 'mercado', 'mexc', 'mexc3', 'ndax', 'novadax',
    #                 'oceanex', 'okcoin', 'okex', 'okex5', 'okx', 'paymium', 'phemex',
    #                 'poloniex', 'probit', 'qtrade', 'ripio', 'stex', 'therock',
    #                 'tidebit', 'tidex', 'timex', 'upbit', 'vcc', 'wavesexchange',
    #                 'wazirx', 'whitebit', 'woo', 'xena', 'yobit', 'zaif', 'zb',
    #                 'zipmex', 'zonda']


    # connection_to_usdt_trading_pairs_daily_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )

    # connection_to_usdt_trading_pairs_4h_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs_4h.db" ) )

    # coroutines = [await get_hisorical_data_from_exchange_for_many_symbols(exchange ) for exchange in  exchanges_list]
    # await asyncio.gather(*coroutines, return_exceptions = True)

    database_name = 'levels_formed_by_highs_and_lows_for_cryptos_0000'
    # list_of_exchanges_for_todays_pairs = get_list_of_exchange_ids_for_todays_pairs(database_name)
    for exchange in exchanges_list:

        # if exchange not in list_of_exchanges_for_todays_pairs:
        #     continue
        # list_of_exchanges_where_next_bar_print_utc_time_00=["bitfinex2","bitfinex","mexc","mexc3","poloniex","coinex","exmo","gateio",
        #                                                 "tokocrypto","binanceusdm","hollaex","zb",
        #                                                 "novadax","kraken","cryptocom","binance","bitmex",
        #                                                 "hitbtc3","gate","delta","currencycom","bybit","kucoin",
        #                                                     "bitmart", "probit", "latoken", "phemex",
        #                                                     "bkex", "bigone", "bitget","bitmart",
        #                                                     "probit", "latoken","bkex", "bigone", "bitget", "whitebit"
        #                                                     ]
        # if exchange not in list_of_exchanges_where_next_bar_print_utc_time_00:
        #     continue
        get_hisorical_data_from_exchange_for_many_symbols(exchange_dict,last_bitcoin_price, exchange,
                                                          engine, timeframe)
    #connection_to_usdt_trading_pairs_daily_ohlcv.close()
    # connection_to_usdt_trading_pairs_4h_ohlcv.close ()
    print("list_of_inactive_pairs\n",list_of_inactive_pairs)
    print("len(list_of_inactive_pairs=",len(list_of_inactive_pairs))
    end = time.perf_counter ()
    print("time in seconds is ", end-start)
    print ( "time in minutes is " , (end - start)/60.0 )
    print ( "time in hours is " , (end - start) / 60.0/60.0 )

def fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price):

    engine , connection_to_ohlcv_for_usdt_pairs =\
        connect_to_postgres_db_without_deleting_it_first (database_name)
    exchanges_list, trading_pairs_list,exchange_dict=get_todays_exchanges_and_pairs_list()



    how_many_exchanges = len ( exchanges_list )
    step_for_exchanges = 3

    # fetch_historical_usdt_pairs_asynchronously(engine,exchanges_list)

    process_list = []
    for exchange_counter in \
            range ( 0 , len ( exchanges_list ) ,
                    step_for_exchanges ):
        print ( "exchange_counter=" , exchange_counter )
        print (
            f"exchanges[{exchange_counter}:{exchange_counter} + {step_for_exchanges}]" )
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        # for number_of_exchange , exchange \
        #         in enumerate ( exchanges_list[exchange_counter:exchange_counter +
        #                                                               how_many_separate_processes_to_spawn_each_corresponding_to_one_exchange] ):
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        p = multiprocessing.Process ( target =
                                      fetch_historical_usdt_pairs_asynchronously ,
                                      args = (exchange_dict,last_bitcoin_price,engine , exchanges_list[
                                                       exchange_counter:exchange_counter + step_for_exchanges],timeframe) )
        p.start ()
        process_list.append ( p )
    for process in process_list:
        process.join ()

    connection_to_ohlcv_for_usdt_pairs.close ()
if __name__=="__main__":
    timeframe='1d'
    last_bitcoin_price=get_real_time_bitcoin_price()
    print("last_bitcoin_price")
    print(last_bitcoin_price)
    database_name="ohlcv_1d_data_for_usdt_pairs_0000"
    list_of_crypto_plus_exchange = \
        get_list_of_tables_in_db_with_db_as_parameter(database_name)
    fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price)
#asyncio.run(get_hisorical_data_from_exchange_for_many_symbols_and_exchanges())
