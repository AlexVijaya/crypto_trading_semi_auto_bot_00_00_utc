from statistics import mean
import pandas as pd
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import os
import time
import datetime
import traceback
import datetime as dt
import tzlocal
import numpy as np
from collections import Counter
from sqlalchemy_utils import create_database,database_exists
import db_config
# from sqlalchemy import MetaData
from sqlalchemy import inspect
import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_ath_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_atl_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_ath_timestamp_and_row_number
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_atl_timestamp_and_row_number
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_base_of_trading_pair
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_quote_of_trading_pair
from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
from get_info_from_load_markets import get_spread
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_ath_was_broken_on_other_exchanges
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_atl_was_broken_on_other_exchanges
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_df_with_strings_where_pair_is_traded
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_exchange_ids_names_and_number_of_exchanges_where_crypto_is_traded
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_to_df_result_of_return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_to_df_result_of_return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_to_df_result_of_return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_to_df_result_of_return_bool_whether_calculated_sl_tp_and_sell_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_info_to_df_about_all_time_high_number_of_times_it_was_touched_its_timestamps_and_datetimes
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_info_to_df_about_all_time_low_number_of_times_it_was_touched_its_timestamps_and_datetimes
from drop_historical_ohlcv_the_length_of_which_is_a_multiple_of_100_without_deleting_primary_db_and_without_deleting_db_with_low_volume import is_length_multiple_of_100
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import add_trading_pairs_to_sql_table_if_they_were_processed
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import create_empty_table_if_it_does_not_exist_or_return_list_of_already_processed_pairs_if_table_exists
def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
def print_df_to_file(dataframe, subdirectory_name):
    series = dataframe.squeeze()
    # get today's date
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")

    # create file name
    file_name = f"atr_level_sl_tp_for_cryptos_{date_today}.txt"

    # create directory if it doesn't exist
    if not os.path.exists(subdirectory_name):
        os.makedirs(subdirectory_name)

    with open(os.path.join(subdirectory_name, file_name), "a") as file:
        # print horizontal line
        file.write("\n"+"+" * 111 + "\n")

        # print series to file
        file.write(str(series))

        # print horizontal line again
        file.write("\n" + "+" * 111)

    print(f"Series appended to {file_name} in {subdirectory_name}")
def find_if_level_is_round(level):
    level = str ( level )
    level_is_round=False

    if "." in level:  # quick check if it is decimal
        decimal_part = level.split ( "." )[1]
        # print(f"decimal part of {mirror_level} is {decimal_part}")
        if decimal_part=="0":
            print(f"level is round")
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part=="25":
            print(f"level is round")
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part == "5":
            print ( f"level is round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part == "75":
            print ( f"level is round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        else:
            print ( f"level is not round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            return level_is_round


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

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db

def get_all_time_high_from_ohlcv_table(engine_for_ohlcv_data_for_stocks,
                                      table_with_ohlcv_table):
    table_with_ohlcv_data_df = \
        pd.read_sql_query ( f'''select * from "{table_with_ohlcv_table}"''' ,
                            engine_for_ohlcv_data_for_stocks )
    print("table_with_ohlcv_data_df")
    print ( table_with_ohlcv_data_df )

    all_time_high_in_stock=table_with_ohlcv_data_df["high"].max()
    print ( "all_time_high_in_stock" )
    print ( all_time_high_in_stock )

    return all_time_high_in_stock, table_with_ohlcv_data_df

def get_all_time_low_from_ohlcv_table(engine_for_ohlcv_data_for_stocks,
                                      table_with_ohlcv_table):
    table_with_ohlcv_data_df = \
        pd.read_sql_query ( f'''select * from "{table_with_ohlcv_table}"''' ,
                            engine_for_ohlcv_data_for_stocks )
    print("table_with_ohlcv_data_df")
    print ( table_with_ohlcv_data_df )

    all_time_low_in_stock=table_with_ohlcv_data_df["low"].min()
    print ( "all_time_low_in_stock" )
    print ( all_time_low_in_stock )

    return all_time_low_in_stock, table_with_ohlcv_data_df

# def drop_table(table_name,engine):
#     engine.execute (
#         f"DROP TABLE IF EXISTS {table_name};" )
from sqlalchemy import text

def drop_table(table_name, engine):
    conn = engine.connect()
    query = text(f'''DROP TABLE IF EXISTS "{table_name}"''')
    conn.execute(query)
    conn.close()

def get_last_close_price_of_asset(ohlcv_table_df):
    last_close_price=ohlcv_table_df["close"].iat[-1]
    return last_close_price

def get_date_with_and_without_time_from_timestamp(timestamp):

    try:
        open_time = \
            dt.datetime.fromtimestamp ( timestamp  )
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


# def get_high_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
#     # get high of bpu2
#     high_of_bpu2=False
#     try:
#         if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
#             print ( "there is no bpu2" )
#         else:
#             high_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "high"]
#             print ( "high_of_bpu2_inside_function" )
#             print ( high_of_bpu2 )
#     except:
#         traceback.print_exc ()
#     return high_of_bpu2

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

def get_ohlc_of_false_breakout_bar(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1):
    low_of_false_breakout_bar = False
    high_of_false_breakout_bar = False
    open_of_false_breakout_bar = False
    close_of_false_breakout_bar = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 2 == row_number_of_bpu1:
            print ( "there is no false_breakout_bar" )
        elif len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no false_breakout_bar" )
        else:
            low_of_false_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "low"]
            open_of_false_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "open"]
            close_of_false_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "close"]
            high_of_false_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "high"]
            # print ( "high_of_false_breakout_bar" )
            # print ( high_of_false_breakout_bar )
    except:
        traceback.print_exc ()
    return open_of_false_breakout_bar , high_of_false_breakout_bar , low_of_false_breakout_bar , close_of_false_breakout_bar

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

def calculate_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):
    # calcualte atr over 5 days before bpu2. bpu2 is not included

    list_of_true_ranges = []
    for row_number_for_atr_calculation_backwards in range ( 0 , atr_over_this_period ):
        try:
            if (row_number_of_bpu1 - row_number_for_atr_calculation_backwards)<0:
                continue
            if truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 , "high"]:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            else:
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
    atr = mean ( list_of_true_ranges )
    # print ( "atr" )
    # print ( atr )
    return atr

def calculate_advanced_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):


    list_of_true_ranges = []
    for row_number_for_atr_calculation_backwards in range ( 0 , atr_over_this_period ):
        try:
            if (row_number_of_bpu1 - row_number_for_atr_calculation_backwards) < 0:
                continue
            if truncated_high_and_low_table_with_ohlcv_data_df.loc[
                row_number_of_bpu1 + 1 , "high"]:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            else:
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
    # print ( "list_of_true_ranges" )
    # print ( list_of_true_ranges )
    # print ( "percentile_20" )
    # print ( percentile_20 )
    # print ( "percentile_80" )
    # print ( percentile_80 )
    list_of_non_rejected_true_ranges=[]
    for true_range_in_list in list_of_true_ranges:
        if true_range_in_list>=percentile_20 and true_range_in_list<=percentile_80:
            list_of_non_rejected_true_ranges.append(true_range_in_list)
    atr=mean(list_of_non_rejected_true_ranges)

    return atr
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


def trunc(num, digits):
    if num!=False:
        try:
            l = str(float(num)).split('.')
            digits = min(len(l[1]), digits)
            return float(l[0] + '.' + l[1][:digits])
        except:
            traceback.print_exc()
    else:
        return False
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

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_ath(last_several_rows_in_np_array_slice_but_one,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice_but_one)):
        current_low=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][3]
        previous_low=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward-1][3]
        current_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][4]
        previous_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward - 1][4]
        # print ( "last_several_rows_in_np_array_slice_but_one" )
        # print(last_several_rows_in_np_array_slice_but_one)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )

        #учитываем поджатие по лоям
        if current_low<previous_low:
            break
        else:
            #учитываем еще и поджатие по закрытиям
            if current_close<previous_close:
                break
            else:
                number_of_bars_which_fulfil_suppression_criterion=\
                    number_of_bars_which_fulfil_suppression_criterion+1
    return number_of_bars_which_fulfil_suppression_criterion

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_atl(last_several_rows_in_np_array_slice_but_one,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice_but_one)):
        current_high=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][2]
        current_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][4]
        previous_high=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward-1][2]
        previous_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward - 1][4]
        # print ( "last_several_rows_in_np_array_slice_but_one" )
        # print(last_several_rows_in_np_array_slice_but_one)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )
        #учитываем поджатие по хаям к историческому минимуму
        if current_high>previous_high:
            break
        else:
            #еще учитываем поджатие по закрытиям
            if current_close>previous_close:
                break
            else:
                number_of_bars_which_fulfil_suppression_criterion=\
                    number_of_bars_which_fulfil_suppression_criterion+1
    return number_of_bars_which_fulfil_suppression_criterion

def find_min_volume_over_last_n_days (
                            last_n_rows_for_volume_check ):

    min_volume_over_last_n_days = np.amin ( last_n_rows_for_volume_check )

    return min_volume_over_last_n_days



def create_text_file_and_writ_text_to_it(text, subdirectory_name):
  # Declare the path to the current directory
  current_directory = os.getcwd()

  # Create the subdirectory in the current directory if it does not exist
  subdirectory_path = os.path.join(current_directory, subdirectory_name)
  os.makedirs(subdirectory_path, exist_ok=True)

  # Get the current date
  today = datetime.datetime.now().strftime('%Y-%m-%d')

  # Create the file path by combining the subdirectory and the file name (today's date)
  file_path = os.path.join(subdirectory_path, "crypto_" + today + '.txt')

  # Check if the file exists
  if not os.path.exists(file_path):
    # Create the file if it does not exist
    open(file_path, 'a').close()

  # Open the file for writing
  with open(file_path, 'a') as f:
    # Redirect the output of the print function to the file
    print = lambda x: f.write(str(x) + '\n')

    # Output the text to the file using the print function
    print(text)

  # Close the file
  f.close()






def search_for_tickers_with_false_breakout_situations(db_where_ohlcv_data_for_stocks_is_stored,
                                          db_where_ticker_which_may_have_false_breakout_situations,
                                               table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be ,
                                               table_where_ticker_which_may_have_false_breakout_situations_from_atl_will_be,
                                               advanced_atr_over_this_period,
                                                number_of_bars_in_suppression_to_check_for_volume_acceptance,
                                                factor_to_multiply_atr_by_to_check_suppression,
                                                count_min_volume_over_this_many_days
                                               ):


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    # engine_for_db_where_ticker_which_may_have_false_breakout_situations , \
    # connection_to_db_where_ticker_which_may_have_false_breakout_situations = \
    #     connect_to_postgres_db_without_deleting_it_first ( db_where_ticker_which_may_have_false_breakout_situations )
    #
    # engine_for_db_where_ticker_which_may_have_fast_breakout_situations_no_drop, \
    #     connection_to_db_where_ticker_which_may_have_fast_breakout_situations_no_drop = \
    #     connect_to_postgres_db_without_deleting_it_first(
    #         db_where_ticker_which_may_have_false_breakout_situations + "_no_drop")

    engine_for_db_where_ticker_which_may_have_fast_breakout_situations_hist, \
        connection_to_db_where_ticker_which_may_have_fast_breakout_situations_hist = \
        connect_to_postgres_db_without_deleting_it_first(
            db_where_ticker_which_may_have_false_breakout_situations + "_hist")

    ##############################
    ##############################
    ##############################
    engine_for_db_where_ticker_which_may_have_false_breakout_situations_processed, \
        connection_to_db_where_ticker_which_may_have_false_breakout_situations_processed = \
        connect_to_postgres_db_without_deleting_it_first(
            db_where_ticker_which_may_have_false_breakout_situations + "_processed")
    list_of_tables_in_db_where_ticker_which_may_have_false_breakout_situations_processed = \
        get_list_of_tables_in_db(engine_for_db_where_ticker_which_may_have_false_breakout_situations_processed)
    list_of_already_processed_pairs = []
    ############################
    ############################
    ############################
    ############################
    ############################
    ############################
    column_name = "already_processed_pairs_for_this_bfr"
    table_where_ticker_which_may_have_false_breakout_situations_from_ath_or_atl_will_be = table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be
    list_of_already_processed_pairs, \
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
        create_empty_table_if_it_does_not_exist_or_return_list_of_already_processed_pairs_if_table_exists(
            column_name,
            db_where_ticker_which_may_have_false_breakout_situations,
            table_where_ticker_which_may_have_false_breakout_situations_from_ath_or_atl_will_be)
    ############################
    ############################
    ############################

    # uncomment this drop if you want to create table with bfr again every time the program is launched
    # drop_table ( table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be ,
    #              engine_for_db_where_ticker_which_may_have_fast_breakout_situations_hist )



    # drop_table ( table_where_ticker_which_may_have_false_breakout_situations_from_atl_will_be ,
    #              engine_for_db_where_ticker_which_may_have_false_breakout_situations )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )

    ##########################################################
    db_where_ohlcv_data_for_stocks_is_stored_0000 = np.nan
    db_where_ohlcv_data_for_stocks_is_stored_1600 = np.nan
    engine_for_ohlcv_data_for_stocks_0000 = np.nan
    engine_for_ohlcv_data_for_stocks_1600 = np.nan
    list_of_tables_in_ohlcv_db_1600 = np.nan
    try:
        #######################################################################################
        ###################################################################################
        db_where_ohlcv_data_for_stocks_is_stored_0000 = db_where_ohlcv_data_for_stocks_is_stored
        db_where_ohlcv_data_for_stocks_is_stored_1600 = "ohlcv_1d_data_for_usdt_pairs_1600"
        engine_for_ohlcv_data_for_stocks_0000, \
            connection_to_ohlcv_data_for_stocks = \
            connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_0000)

        engine_for_ohlcv_data_for_stocks_1600, \
            connection_to_ohlcv_data_for_stocks_1600 = \
            connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_1600)
        ###################################################################################
        #######################################################################################

        ###################################################################################
        # ---------------------------------------------------------------------------
        list_of_tables_in_ohlcv_db_0000 = \
            get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_0000)

        list_of_tables_in_ohlcv_db_1600 = \
            get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_1600)

        print('list_of_tables_in_ohlcv_db_1600')
        print(list_of_tables_in_ohlcv_db_1600)
        # -----------------------------------------------------------------------------
        ###################################################################################
    except:
        traceback.print_exc()

    counter=0
    list_of_tickers_where_ath_is_also_limit_level=[]
    list_of_tickers_where_atl_is_also_limit_level = []
    list_of_stocks_which_broke_ath=[]
    list_of_stocks_which_broke_atl = []

    #########################################################################
    db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded = "db_with_trading_pair_statistics"
    table_where_row_names_are_pairs_and_values_are_strings_of_exchanges = "exchanges_where_each_pair_is_traded"
    df_with_strings_of_exchanges_where_pair_is_traded = pd.DataFrame()
    try:
        df_with_strings_of_exchanges_where_pair_is_traded = return_df_with_strings_where_pair_is_traded(
            db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded,
            table_where_row_names_are_pairs_and_values_are_strings_of_exchanges)
        df_with_strings_of_exchanges_where_pair_is_traded.set_index("trading_pair_new_column", inplace=True)
    except:
        traceback.print_exc()

    print("df_with_strings_of_exchanges_where_pair_is_traded1")
    print(df_with_strings_of_exchanges_where_pair_is_traded.tail(20).to_string())

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            counter=counter+1
            print ( f'{stock_name} is'
                    f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )

            ##############################
            ##############################
            ##############################
            if stock_name in list_of_already_processed_pairs:
                print(f"{stock_name} has_been_discarded")
                continue

            add_trading_pairs_to_sql_table_if_they_were_processed(
                table_where_ticker_which_may_have_false_breakout_situations_from_ath_or_atl_will_be,
                engine_for_db_where_ticker_which_may_have_false_breakout_situations_processed,
                list_of_already_processed_pairs,
                column_name,
                stock_name,
                df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run)
            ######################
            ######################
            ######################

            table_with_ohlcv_data_df = \
                pd.read_sql_query ( f'''select * from "{stock_name}"''' ,
                                    engine_for_ohlcv_data_for_stocks )

            if is_length_multiple_of_100(table_with_ohlcv_data_df):
                continue

            entire_original_table_with_ohlcv_data_df = pd.DataFrame()
            try:
                entire_original_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()
            except:
                traceback.print_exc()

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            # number_of_available_days
            number_of_available_days = np.nan
            try:
                number_of_available_days = len(table_with_ohlcv_data_df)
            except:
                traceback.print_exc()
            # print ("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0 , "exchange"]

            spot_asset_also_available_as_swap_contract_on_same_exchange = ""
            url_of_swap_contract_if_it_exists = ""
            try:
                spot_asset_also_available_as_swap_contract_on_same_exchange = table_with_ohlcv_data_df.loc[
                    0, "spot_asset_also_available_as_swap_contract_on_same_exchange"]
                url_of_swap_contract_if_it_exists = table_with_ohlcv_data_df.loc[0, "url_of_swap_contract_if_it_exists"]
            except:
                traceback.print_exc()
            # short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
                        table_with_ohlcv_data_df)

                # do not short unshortable assets
                # if asset_type == 'spot':
#                    continue

            except:
                traceback.print_exc()

            #########################################################
            # find row where base is equal to base from df_with_strings_of_exchanges_where_pair_is_traded
            exchange_id_string_where_trading_pair_is_traded = ""
            exchange_names_string_where_trading_pair_is_traded = ""
            number_of_exchanges_where_pair_is_traded_on = np.nan
            try:

                exchange_id_string_where_trading_pair_is_traded, \
                    exchange_names_string_where_trading_pair_is_traded, \
                    number_of_exchanges_where_pair_is_traded_on = \
                    return_exchange_ids_names_and_number_of_exchanges_where_crypto_is_traded(
                        df_with_strings_of_exchanges_where_pair_is_traded, stock_name)

            except:
                traceback.print_exc()


            for index_in_iteration in range(len(entire_original_table_with_ohlcv_data_df), 3, -1):
                print(f"{index_in_iteration}/{len(entire_original_table_with_ohlcv_data_df)} has been processed")
                table_with_ohlcv_data_df = entire_original_table_with_ohlcv_data_df.iloc[:index_in_iteration]
                ##########################################################
                #########################################################################
                # Select last 365*2 rows (last two years) of data
                last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

                # Round ohlc and adjclose to 6 decimal places
                # last_two_years_of_data = last_two_years_of_data.round(
    #               {'open': 6, 'high': 6, 'low': 6, 'close': 6, 'adjclose': 6})

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
                timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'Timestamp']
                open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
                high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
                low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
                close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
                volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'volume']

                # Find Timestamp, open, high, low, close, volume of bar after false_breakout bar
                timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'Timestamp']
                open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'open']
                high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'high']
                low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'low']
                close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'close']
                volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'volume']

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

                if last_two_years_of_data.tail(30)['volume'].min() < 750:
                    continue

                if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
                    continue


                # find all time high in last_two_years_of_data_but_one_last_day
                all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
                print(f"all_time_high: {all_time_high}")

                all_time_high_row_numbers =\
                    last_two_years_of_data_but_two_last_days[last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

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
                   last_all_time_high_row_number + 1:,"high"].max() > all_time_high:
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

                advanced_atr=\
                    calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_false_breakout_bar_row_number)


                if open_of_next_day_bar_after_break_out_bar>close_of_false_breakout_bar or\
                    close_of_next_day_bar_after_break_out_bar>open_of_false_breakout_bar or\
                        low_of_next_day_bar_after_break_out_bar>low_of_false_breakout_bar:
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
                date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar =\
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
                print("list_of_stocks_which_broke_ath")
                print(list_of_stocks_which_broke_ath)

                df_with_level_atr_bpu_bsu_etc = pd.DataFrame()
                df_with_level_atr_bpu_bsu_etc.at[0, "ticker"] = stock_name
                df_with_level_atr_bpu_bsu_etc.at[0, "exchange"] = exchange

                df_with_level_atr_bpu_bsu_etc.at[0, "model"] = "ЛОЖНЫЙ_ПРОБОЙ_ATH_2Б"
                df_with_level_atr_bpu_bsu_etc.at[0, "ath"] = all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "advanced_atr"] = advanced_atr

                df_with_level_atr_bpu_bsu_etc.at[0, "advanced_atr_over_this_period"] = \
                    advanced_atr_over_this_period
                df_with_level_atr_bpu_bsu_etc.at[0, "open_of_bsu"] = open_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_bsu"] = high_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "low_of_bsu"] = low_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "close_of_bsu"] = close_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_bsu"] = volume_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_bsu"] = timestamp_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_bsu"] = date_of_last_ath

                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_pre_false_breakout_bar"] = timestamp_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_pre_false_breakout_bar"] = date_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "open_of_pre_false_breakout_bar"] = open_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_pre_false_breakout_bar"] = high_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "low_of_pre_false_breakout_bar"] = low_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "close_of_pre_false_breakout_bar"] = close_of_pre_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_pre_false_breakout_bar"] = volume_of_pre_false_breakout_bar

                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_false_breakout_bar"] = timestamp_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_false_breakout_bar"] = date_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "open_of_false_breakout_bar"] = open_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_false_breakout_bar"] = high_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "low_of_false_breakout_bar"] = low_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "close_of_false_breakout_bar"] = close_of_false_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_false_breakout_bar"] = volume_of_false_breakout_bar

                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_next_day_bar_after_break_out_bar"] = timestamp_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_next_day_bar_after_break_out_bar"] = date_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "open_of_next_day_bar_after_break_out_bar"] = open_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_next_day_bar_after_break_out_bar"] = high_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "low_of_next_day_bar_after_break_out_bar"] = low_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "close_of_next_day_bar_after_break_out_bar"] = close_of_next_day_bar_after_break_out_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_next_day_bar_after_break_out_bar"] = volume_of_next_day_bar_after_break_out_bar


                df_with_level_atr_bpu_bsu_etc.at[0, "min_volume_over_last_n_days"] =  last_two_years_of_data['volume'].tail(count_min_volume_over_this_many_days).min()
                df_with_level_atr_bpu_bsu_etc.at[0, "count_min_volume_over_this_many_days"] = count_min_volume_over_this_many_days

                df_with_level_atr_bpu_bsu_etc.at[0, "sell_order"] = sell_order
                df_with_level_atr_bpu_bsu_etc.at[0, "technical_stop_loss"] = technical_stop_loss
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_3_to_1"] = take_profit_when_stop_loss_is_technical_3_to_1
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_4_to_1"] = take_profit_when_stop_loss_is_technical_4_to_1
                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_technical_sl_and_sell_order_in_atr"] = distance_between_technical_stop_loss_and_sell_order_in_atr
                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_technical_sl_and_sell_order"] = distance_between_technical_stop_loss_and_sell_order

                df_with_level_atr_bpu_bsu_etc.at[0, "suppression_by_lows"] = suppression_flag_for_lows
                df_with_level_atr_bpu_bsu_etc.at[0, "number_of_bars_when_we_check_suppression_by_lows"] = number_of_bars_when_we_check_suppression_by_lows
                df_with_level_atr_bpu_bsu_etc.at[0, "suppression_by_closes"] = suppression_flag_for_closes
                df_with_level_atr_bpu_bsu_etc.at[0, "number_of_bars_when_we_check_suppression_by_closes"] = number_of_bars_when_we_check_suppression_by_closes

                print("df_with_level_atr_bpu_bsu_etc")
                print(df_with_level_atr_bpu_bsu_etc.to_string())

                try:
                    asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                        get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)

                    df_with_level_atr_bpu_bsu_etc.at[0,"asset_type"] = asset_type
                    df_with_level_atr_bpu_bsu_etc.at[0,"maker_fee"] = maker_fee
                    df_with_level_atr_bpu_bsu_etc.at[0,"taker_fee"] = taker_fee
                    df_with_level_atr_bpu_bsu_etc.at[0,"url_of_trading_pair"] = url_of_trading_pair
                    df_with_level_atr_bpu_bsu_etc.at[0, "number_of_available_bars"] = number_of_available_days
                    try:
                        df_with_level_atr_bpu_bsu_etc.at[0, "trading_pair_is_traded_with_margin"]=\
                            get_bool_if_asset_is_traded_with_margin(table_with_ohlcv_data_df)
                    except:
                        traceback.print_exc()

                    try:
                        df_with_level_atr_bpu_bsu_etc.loc[
                            0, "spot_asset_also_available_as_swap_contract_on_same_exchange"] = \
                            spot_asset_also_available_as_swap_contract_on_same_exchange
                        df_with_level_atr_bpu_bsu_etc.loc[
                            0, "url_of_swap_contract_if_it_exists"] = \
                            url_of_swap_contract_if_it_exists
                    except:
                        traceback.print_exc()
                except:
                    traceback.print_exc()
                # try:
                #     #############################################
                #     # add info to dataframe about whether level was broken on other exchanges
                #     df_with_level_atr_bpu_bsu_etc = fill_df_with_info_if_ath_was_broken_on_other_exchanges(stock_name,
                #                                                                                      db_where_ohlcv_data_for_stocks_is_stored_0000,
                #                                                                                      db_where_ohlcv_data_for_stocks_is_stored_1600,
                #                                                                                      table_with_ohlcv_data_df,
                #                                                                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                                                                      engine_for_ohlcv_data_for_stocks_1600,
                #                                                                                      all_time_high,
                #                                                                                      list_of_tables_in_ohlcv_db_1600,
                #                                                                                      df_with_level_atr_bpu_bsu_etc,
                #                                                                                      0)
                # except:
                #     traceback.print_exc()

                df_with_level_atr_bpu_bsu_etc.at[0, "ticker_last_column"] = stock_name
                try:
                    df_with_level_atr_bpu_bsu_etc.at[0, "base"] = get_base_of_trading_pair(trading_pair=stock_name)
                except:
                    traceback.print_exc()
                df_with_level_atr_bpu_bsu_etc.at[0, "ticker_will_be_traced_and_position_entered"] = False

                side = "sell"
                df_with_level_atr_bpu_bsu_etc.at[0, "side"] = side

                df_with_level_atr_bpu_bsu_etc.at[0, "stop_loss_is_technical"] = False
                df_with_level_atr_bpu_bsu_etc.at[0, "stop_loss_is_calculated"] = False


                df_with_level_atr_bpu_bsu_etc.at[0, "market_or_limit_stop_loss"] = 'market'
                df_with_level_atr_bpu_bsu_etc.at[0, "market_or_limit_take_profit"] = 'limit'
                df_with_level_atr_bpu_bsu_etc.at[0, "position_size"] = 0

                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_x_to_one"] = 3

                #########################################################################
                #########################################################################
                #########################################################################
                try:
                    df_with_level_atr_bpu_bsu_etc.at[0, "exchange_names_string_where_trading_pair_is_traded"] = exchange_names_string_where_trading_pair_is_traded
                    df_with_level_atr_bpu_bsu_etc.at[0, "exchange_id_string_where_trading_pair_is_traded"] = exchange_id_string_where_trading_pair_is_traded
                    df_with_level_atr_bpu_bsu_etc.at[0, "number_of_exchanges_where_pair_is_traded_on"] = number_of_exchanges_where_pair_is_traded_on
                except:
                    traceback.print_exc()

                #########################################################################
                #########################################################################
                #########################################################################

                # Choose whether to use spot trading or margin trading with either cross or isolated margin
                df_with_level_atr_bpu_bsu_etc.at[0, "spot_without_margin"] = False
                df_with_level_atr_bpu_bsu_etc.at[0, "margin"] = False
                df_with_level_atr_bpu_bsu_etc.at[0, "cross_margin"] = False
                df_with_level_atr_bpu_bsu_etc.at[0, "isolated_margin"] = False

                try:
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_position_entry_price"] = sell_order
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_stop_loss_price"] = technical_stop_loss
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_position_entry_price_default_value"] = sell_order
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_stop_loss_price_default_value"] = technical_stop_loss
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_take_profit_price"] = take_profit_when_stop_loss_is_technical_3_to_1
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_take_profit_price_default_value"] = take_profit_when_stop_loss_is_technical_3_to_1

                    df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_bfr_was_found"] = int(time.time())
                    df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_bfr_was_found"] = datetime.datetime.now()
                except:
                    traceback.print_exc()

                try:
                    # add info to df if sl, order, and tp were reached
                    level_price=all_time_high
                    df_with_level_atr_bpu_bsu_etc=add_to_df_result_of_return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,
                        df_with_level_atr_bpu_bsu_etc,
                        index_in_iteration,
                        entire_original_table_with_ohlcv_data_df,
                        side,
                        sell_order,
                        take_profit_when_stop_loss_is_technical_3_to_1,
                        technical_stop_loss)
                except:
                    traceback.print_exc()
                round_to_this_number_of_non_zero_digits = 2
                try:
                    df_with_level_atr_bpu_bsu_etc = add_info_to_df_about_all_time_high_number_of_times_it_was_touched_its_timestamps_and_datetimes(
                        all_time_high,
                        df_with_level_atr_bpu_bsu_etc,
                        last_two_years_of_data,
                        round_to_this_number_of_non_zero_digits)
                except:
                    traceback.print_exc()
                try:
                    df_with_level_atr_bpu_bsu_etc.to_sql(
                        table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be,
                        connection_to_db_where_ticker_which_may_have_fast_breakout_situations_hist,
                        if_exists='append')
                except:
                    traceback.print_exc()
                # df_with_level_atr_bpu_bsu_etc.to_sql(
                #     table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be,
                #     engine_for_db_where_ticker_which_may_have_false_breakout_situations,
                #     if_exists='append')
                # print_df_to_file(df_with_level_atr_bpu_bsu_etc,
                #                  'current_rebound_breakout_and_false_breakout')

        except:
            traceback.print_exc()

    # string_for_output = f"Список инструментов, которые сформировали модель ЛОЖНЫЙ ПРОБОЙ исторического максимума 2МЯ БАРАМИ:\n" \
    #                     f"{list_of_stocks_which_broke_ath}\n\n"
    # # Use the function to create a text file with the text
    # # in the subdirectory "current_rebound_breakout_and_false_breakout"
    # create_text_file_and_writ_text_to_it(string_for_output,
    #                                      'current_rebound_breakout_and_false_breakout')
    print ( "list_of_stocks_which_broke_ath" )
    print ( list_of_stocks_which_broke_ath )
    print ( "list_of_stocks_which_broke_atl" )
    print ( list_of_stocks_which_broke_atl )




if __name__=="__main__":
    start_time=time.time ()
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000_pagination"
    count_only_round_rebound_level=False
    db_where_ticker_which_may_have_false_breakout_situations=\
        "levels_formed_by_highs_and_lows_for_cryptos_0000"
    table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be =\
        "current_false_breakout_of_ath_by_two_bars"
    table_where_ticker_which_may_have_false_breakout_situations_from_atl_will_be =\
        "current_false_breakout_of_atl_by_two_bars"

    if count_only_round_rebound_level:
        db_where_ticker_which_may_have_false_breakout_situations=\
            "round_levels_formed_by_highs_and_lows_for_cryptos_0000"
    #0.05 means 5%
    
    atr_over_this_period = 30
    advanced_atr_over_this_period=30
    number_of_bars_in_suppression_to_check_for_volume_acceptance=14
    factor_to_multiply_atr_by_to_check_suppression=1
    count_min_volume_over_this_many_days=7
    search_for_tickers_with_false_breakout_situations(
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              db_where_ticker_which_may_have_false_breakout_situations,
                                              table_where_ticker_which_may_have_false_breakout_situations_from_ath_will_be,
                                                table_where_ticker_which_may_have_false_breakout_situations_from_atl_will_be,
                                            advanced_atr_over_this_period,
                                            number_of_bars_in_suppression_to_check_for_volume_acceptance,
                                            factor_to_multiply_atr_by_to_check_suppression,count_min_volume_over_this_many_days)

    end_time = time.time ()
    overall_time = end_time - start_time
    print ( 'overall time in minutes=' , overall_time / 60.0 )
    print ( 'overall time in hours=' , overall_time / 3600.0 )
    print ( 'overall time=' , str ( datetime.timedelta ( seconds = overall_time ) ) )
    print ( 'start_time=' , start_time )
    print ( 'end_time=' , end_time )