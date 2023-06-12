import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
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
import threading
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
def connect_to_postgres_db_without_deleting_it_first(database):
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
def get_last_index_column_value_from_ohlcv_table(ohlcv_data_df):
    last_index = ohlcv_data_df["index"].iat[-1]
    return last_index

def get_last_timestamp_from_ohlcv_table(ohlcv_data_df):
    last_timestamp = ohlcv_data_df["Timestamp"].iat[-1]
    return last_timestamp
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
def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
def get_number_of_last_index(ohlcv_data_df):
    number_of_last_index = ohlcv_data_df["index"].max()
    return number_of_last_index
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
def constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db(engine,trading_pair,exchange,timeframe):
    exchange_object = ""

    while True:
        try:
            try:
                print("exchange1=", exchange)
                exchange_object = get_exchange_object6(exchange)

                exchange_object.enableRateLimit = True
            except:
                traceback.print_exc()

            trading_pair_with_underscore = trading_pair.replace('/', "_")
            string_for_comparison_pair_plus_exchange = \
                f"{trading_pair_with_underscore}" + "_on_" + f"{exchange}"
            table_with_ohlcv_data_df = \
                pd.read_sql_query(f'''select * from "{string_for_comparison_pair_plus_exchange}"''',
                                  engine)

            last_timestamp_in_original_table = get_last_timestamp_from_ohlcv_table(table_with_ohlcv_data_df)

            # #delete last row because it is not a complete bar
            last_index = get_last_index_column_value_from_ohlcv_table(table_with_ohlcv_data_df)

            # drop the last row from df
            table_with_ohlcv_data_df = table_with_ohlcv_data_df.drop(table_with_ohlcv_data_df.index[-1])

            last_timestamp = get_last_timestamp_from_ohlcv_table(table_with_ohlcv_data_df)
            print(f"last_timestamp for {trading_pair} on {exchange}")
            print(last_timestamp)
            date_without_time = get_date_without_time_from_timestamp(last_timestamp)
            number_of_last_index_in_ohlcv_data_df = \
                get_number_of_last_index(table_with_ohlcv_data_df)

            header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']

            # if exchange!="binance" and trading_pair!="BETA/BUSD":
            #     continue
            data = np.nan

            try:
                print(f"now i am fetching ohlcv from exchange {exchange} for {trading_pair}")
                data = exchange_object.fetch_ohlcv(trading_pair, timeframe, since=int(last_timestamp * 1000))
            except:
                traceback.print_exc()

            ohlcv_data_several_last_rows_df = \
                pd.DataFrame(data, columns=header).set_index('Timestamp')
            print("ohlcv_data_several_last_rows_df1")
            print(ohlcv_data_several_last_rows_df)
            # trading_pair = trading_pair.replace("/", "_")

            ohlcv_data_several_last_rows_df['ticker'] = trading_pair_with_underscore
            ohlcv_data_several_last_rows_df['exchange'] = exchange
            ohlcv_data_several_last_rows_df['trading_pair'] = trading_pair_with_underscore + "_on_" + exchange

            ohlcv_data_several_last_rows_df['volume*low'] = ohlcv_data_several_last_rows_df['volume'] * \
                                                            ohlcv_data_several_last_rows_df['low']
            ohlcv_data_several_last_rows_df['volume*close'] = ohlcv_data_several_last_rows_df['volume'] * \
                                                              ohlcv_data_several_last_rows_df['close']

            current_timestamp = time.time()
            last_timestamp_in_df = ohlcv_data_several_last_rows_df.tail(1).index.item() / 1000.0
            print("current_timestamp=", current_timestamp)
            print("ohlcv_data_several_last_rows_df.tail(1).index.item()=",
                  ohlcv_data_several_last_rows_df.tail(1).index.item() / 1000.0)

            # check if the pair is active
            timeframe_in_seconds = convert_string_timeframe_into_seconds(timeframe)
            if not abs(current_timestamp - last_timestamp_in_df) < (timeframe_in_seconds):
                print(f"not quite active trading pair {trading_pair_with_underscore} on {exchange}")

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

            ohlcv_data_several_last_rows_df.set_index("open_time")
            add_time_of_next_candle_print_to_df(ohlcv_data_several_last_rows_df)
            print("100program got here")

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

                # last_timestamp_in_df = last_timestamp_in_original_table
                # is_pair_active_bool = is_pair_active(ohlcv_data_several_last_rows_df, last_timestamp_in_df,
                #                                      timeframe, trading_pair,
                #                                      exchange)
                # if not is_pair_active_bool:
                #     drop_table(string_for_comparison_pair_plus_exchange, engine)
                #     print(f"{string_for_comparison_pair_plus_exchange} dropped1 nothing_added")
                # continue

            # nothing new is added and the pair is inactive
            # if not is_pair_active_bool:
            #     drop_table(string_for_comparison_pair_plus_exchange, engine)
            #     print(f"{string_for_comparison_pair_plus_exchange} dropped2")
            #     continue
            # try:
            #     ohlcv_data_several_last_rows_df['open_time'] = \
            #         [datetime.datetime.timestamp(x) for x in ohlcv_data_several_last_rows_df["Timestamp"]]
            #     # ohlcv_data_several_last_rows_df["open_time"] = ohlcv_data_several_last_rows_df.index
            # except:
            #     print("strange_error")
            #     traceback.print_exc()
            #
            #     time.sleep(3000000)

            print(f"ohlcv_data_several_last_rows_df11 for {exchange}")
            print(ohlcv_data_several_last_rows_df)

            # ohlcv_data_several_last_rows_df.set_index("open_time")
            ohlcv_data_several_last_rows_df.index = \
                range(number_of_last_index_in_ohlcv_data_df,
                      number_of_last_index_in_ohlcv_data_df + len(ohlcv_data_several_last_rows_df))
            print(f"ohlcv_data_several_last_rows_df13 for {trading_pair} on {exchange}")
            print(ohlcv_data_several_last_rows_df.to_string())

            try:
                print("ohlcv_data_several_last_rows_df_first_row_is_not_deleted")
                print(ohlcv_data_several_last_rows_df.to_string())
                ohlcv_data_several_last_rows_df = ohlcv_data_several_last_rows_df.iloc[1:, :]
                print("ohlcv_data_several_last_rows_df_first_row_deleted")
                print(ohlcv_data_several_last_rows_df.to_string())
            except:
                traceback.print_exc()
            # list_of_updated_trading_pairs.append(trading_pair)

            engine.execute(
                f'''DELETE FROM public."{string_for_comparison_pair_plus_exchange}" WHERE "index" >= {last_index};''')
            ohlcv_data_several_last_rows_df.to_sql(f"{trading_pair}_on_{exchange}",
                                                   engine,
                                                   if_exists='append')
            print(f"table updated for {trading_pair} on {exchange}")
            time.sleep(5)
        except:
            print(f"1error with exchange = {exchange}")
            traceback.print_exc()


if __name__=="__main__":
    database_name = "ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    engine_for_ohlcv_data_for_cryptos, connection_to_ohlcv_data_for_cryptos = \
        connect_to_postgres_db_without_deleting_it_first(database_name)
    trading_pair="ACH/USDT"
    exchange="gateio"
    timeframe="1d"
    list_of_exchanges=["gateio","kucoin","mexc3","huobipro","bybit","btcex"]
    for exchange in list_of_exchanges:
        try:
            print(f"starting thread for {exchange}")
            t = threading.Thread(target=constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db,
                                 args=(engine_for_ohlcv_data_for_cryptos, trading_pair, exchange, timeframe))
            # constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db(engine_for_ohlcv_data_for_cryptos,
            #                                                                      trading_pair,
            #                                                                      exchange,
            #                                                                      timeframe)
            t.start()
            print("this is outside of thread")
        except:
            print(f"error with exchange = {exchange}")
            traceback.print_exc()
