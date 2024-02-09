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
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_bool_whether_calculated_sl_tp_and_sell_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached
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

def get_ohlc_of_breakout_bar(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1):
    low_of_breakout_bar = False
    high_of_breakout_bar = False
    open_of_breakout_bar = False
    close_of_breakout_bar = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 2 == row_number_of_bpu1:
            print ( "there is no breakout_bar" )
        elif len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no breakout_bar" )
        else:
            low_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "low"]
            open_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "open"]
            close_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "close"]
            high_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "high"]
            # print ( "high_of_breakout_bar" )
            # print ( high_of_breakout_bar )
    except:
        traceback.print_exc ()
    return open_of_breakout_bar , high_of_breakout_bar , low_of_breakout_bar , close_of_breakout_bar

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





def search_for_tickers_with_breakout_situations(db_where_ohlcv_data_for_stocks_is_stored,
                                          db_where_ticker_which_may_have_breakout_situations,
                                               table_where_ticker_which_may_have_breakout_situations_from_ath_will_be ,
                                               table_where_ticker_which_may_have_breakout_situations_from_atl_will_be,
                                               advanced_atr_over_this_period,
                                                number_of_bars_in_suppression_to_check_for_volume_acceptance,
                                                factor_to_multiply_atr_by_to_check_suppression,
                                                count_min_volume_over_this_many_days
                                               ):


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    # engine_for_db_where_ticker_which_may_have_breakout_situations , \
    # connection_to_db_where_ticker_which_may_have_breakout_situations = \
    #     connect_to_postgres_db_without_deleting_it_first ( db_where_ticker_which_may_have_breakout_situations )

    engine_for_db_where_ticker_which_may_have_breakout_situations_hist, \
        connection_to_db_where_ticker_which_may_have_breakout_situations_hist = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ticker_which_may_have_breakout_situations+"_hist1")


    ##############################
    ##############################
    ##############################
    engine_for_db_where_ticker_which_may_have_breakout_situations_processed, \
        connection_to_db_where_ticker_which_may_have_breakout_situations_processed = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ticker_which_may_have_breakout_situations + "_proc")
    list_of_tables_in_db_where_ticker_which_may_have_breakout_situations_processed = \
        get_list_of_tables_in_db(engine_for_db_where_ticker_which_may_have_breakout_situations_processed)
    list_of_already_processed_pairs=[]
    # df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run=pd.DataFrame()


    ############################
    ############################
    ############################
    column_name="already_processed_pairs_for_this_bfr"
    table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be=table_where_ticker_which_may_have_breakout_situations_from_ath_will_be
    list_of_already_processed_pairs,\
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run=\
        create_empty_table_if_it_does_not_exist_or_return_list_of_already_processed_pairs_if_table_exists(
        column_name,
        db_where_ticker_which_may_have_breakout_situations,
        table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be)
    ############################
    ############################
    ############################

    # # uncomment this drop if you want to create table with bfr again every time the program is launched
    # drop_table ( table_where_ticker_which_may_have_breakout_situations_from_ath_will_be ,
    #              engine_for_db_where_ticker_which_may_have_breakout_situations_hist )


    # drop_table ( table_where_ticker_which_may_have_breakout_situations_from_atl_will_be ,
    #              engine_for_db_where_ticker_which_may_have_breakout_situations )

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
    #########################################################################
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
    #######################################################################################################

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            counter=counter+1
            counter=int(counter)
            print ( f'{stock_name} is'
                    f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )

            # if stock_name!="HBAR_USDT:USDT_on_woo":
            #     continue




            ##############################
            ##############################
            ##############################
            if stock_name in list_of_already_processed_pairs:
                print(f"{stock_name} has_been_discarded")
                continue

            add_trading_pairs_to_sql_table_if_they_were_processed(
                table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be,
                engine_for_db_where_ticker_which_may_have_breakout_situations_processed,
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
            if table_with_ohlcv_data_df.empty:
                continue

            # print ("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0 , "exchange"]


            spot_asset_also_available_as_swap_contract_on_same_exchange=""
            url_of_swap_contract_if_it_exists=""
            try:
                spot_asset_also_available_as_swap_contract_on_same_exchange = table_with_ohlcv_data_df.loc[0 , "spot_asset_also_available_as_swap_contract_on_same_exchange"]
                url_of_swap_contract_if_it_exists = table_with_ohlcv_data_df.loc[0 , "url_of_swap_contract_if_it_exists"]
            except:
                traceback.print_exc()

            # short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
                        table_with_ohlcv_data_df)
            except:
                traceback.print_exc()

            #######################################################################################################
            #####################################################################################

            # get base of trading pair
            # base = get_base_of_trading_pair(trading_pair=stock_name)
            # quote = get_quote_of_trading_pair(trading_pair=stock_name)
            # base_slash_quote=base+"/"+quote
            #########################################################
            # find row where base is equal to base from df_with_strings_of_exchanges_where_pair_is_traded
            exchange_id_string_where_trading_pair_is_traded = ""
            exchange_names_string_where_trading_pair_is_traded = ""
            number_of_exchanges_where_pair_is_traded_on = np.nan
            try:

                # exchange_id_string_where_trading_pair_is_traded = \
                #     df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "exchanges_where_pair_is_traded"]
                # exchange_names_string_where_trading_pair_is_traded = \
                #     df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "unique_exchanges_where_pair_is_traded"]
                # number_of_exchanges_where_pair_is_traded_on = \
                #     df_with_strings_of_exchanges_where_pair_is_traded.loc[
                #         base_slash_quote, "number_of_exchanges_where_pair_is_traded_on"]

                exchange_id_string_where_trading_pair_is_traded,\
                    exchange_names_string_where_trading_pair_is_traded,\
                    number_of_exchanges_where_pair_is_traded_on=\
                    return_exchange_ids_names_and_number_of_exchanges_where_crypto_is_traded(
                        df_with_strings_of_exchanges_where_pair_is_traded,stock_name)

            except:
                traceback.print_exc()
            ##########################################################
            #########################################################################
            #########################################################################
            #########################################################################


            for index_in_iteration in range(len(entire_original_table_with_ohlcv_data_df), 3, -1):
                print(f"{index_in_iteration}/{len(entire_original_table_with_ohlcv_data_df)} has been processed")
                table_with_ohlcv_data_df = entire_original_table_with_ohlcv_data_df.iloc[:index_in_iteration]


                # Select last 365*2 rows (last two years) of data
                last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

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
                #
                # if last_two_years_of_data.tail(30)['volume'].min() < 750:
                #     continue
                #
                # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
                #     continue

                # find all time high in last_two_years_of_data_but_one_last_day
                all_time_high = last_two_years_of_data_but_one_last_day['high'].max()
                print(f"all_time_high: {all_time_high}")

                ################
                ################
                ################
                # round_to_this_number_of_non_zero_digits=3
                # number_of_zeroes_in_all_time_high = count_zeros_number_with_e_notaton_is_acceptable(all_time_high)
                # rounded_all_time_high=round(all_time_high, number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits)
                # print("rounded_all_time_high")
                # print(rounded_all_time_high)
                # rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df = last_two_years_of_data.copy()
                # # round high and low to two decimal number
                # rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["high"] = \
                #     last_two_years_of_data["high"].apply(round, args=(number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits,))
                # rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["low"] = \
                #     last_two_years_of_data["low"].apply(round, args=(number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits,))
                #
                # print("rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df")
                # print(rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df.to_string())
                #
                # ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines = \
                #     rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df.loc[
                #         rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["high"] == rounded_all_time_high]
                #
                # number_of_times_this_all_time_high_occurred=len(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)
                #
                # timestamps_of_all_time_highs_as_string=\
                #     extract_timestamps_as_string(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)
                #
                # open_times_of_all_time_highs_as_string = \
                #     extract_open_times_as_string(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)
                #
                # df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_high_occurred"] = \
                #     df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_high_occurred"].astype('object')
                # df_with_level_atr_bpu_bsu_etc.at[
                #     0, "number_of_times_this_all_time_high_occurred"] = number_of_times_this_all_time_high_occurred
                #
                # df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_highs_as_string"] = \
                #     df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_highs_as_string"].astype('object')
                # df_with_level_atr_bpu_bsu_etc.at[
                #     0, "timestamps_of_all_time_highs_as_string"] = timestamps_of_all_time_highs_as_string
                #
                # df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_highs_as_string"] = \
                #     df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_highs_as_string"].astype('object')
                # df_with_level_atr_bpu_bsu_etc.at[
                #     0, "open_times_of_all_time_highs_as_string"] = open_times_of_all_time_highs_as_string
                ################
                ################
                ################








                all_time_high_row_numbers =\
                    last_two_years_of_data_but_one_last_day[last_two_years_of_data_but_one_last_day['high'] == all_time_high].index

                last_all_time_high_row_number = all_time_high_row_numbers[-1]

                #check if the found ath is legit and no broken for the last 2 years
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

                if ath_is_not_broken_for_a_long_time==False:
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
                   last_all_time_high_row_number + 1:,"high"].max() > all_time_high:
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

                advanced_atr=\
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
                print("list_of_stocks_which_broke_ath")
                print(list_of_stocks_which_broke_ath)

                # df_with_level_atr_bpu_bsu_etc = pd.DataFrame(dtype='object',columns=['ticker', 'exchange', 'model', 'ath', 'advanced_atr', 'advanced_atr_over_this_period', 'high_of_bsu', 'volume_of_bsu', 'timestamp_of_bsu', 'human_date_of_bsu', 'open_of_breakout_bar', 'high_of_breakout_bar', 'low_of_breakout_bar', 'close_of_breakout_bar', 'volume_of_breakout_bar', 'timestamp_of_breakout_bar', 'human_date_of_breakout_bar', 'min_volume_over_last_n_days', 'count_min_volume_over_this_many_days', 'buy_order', 'calculated_stop_loss', 'take_profit_when_sl_is_calculated_3_to_1', 'take_profit_when_sl_is_calculated_4_to_1', 'distance_between_calculated_sl_and_buy_order_in_atr', 'distance_between_calculated_sl_and_buy_order', 'technical_stop_loss', 'take_profit_when_sl_is_technical_3_to_1', 'take_profit_when_sl_is_technical_4_to_1', 'distance_between_technical_sl_and_buy_order_in_atr', 'distance_between_technical_sl_and_buy_order', 'suppression_by_lows', 'number_of_bars_when_we_check_suppression_by_lows', 'suppression_by_closes', 'number_of_bars_when_we_check_suppression_by_closes', 'asset_type', 'maker_fee', 'taker_fee', 'url_of_trading_pair', 'number_of_available_bars', 'trading_pair_is_traded_with_margin', 'spot_asset_also_available_as_swap_contract_on_same_exchange', 'url_of_swap_contract_if_it_exists', 'ticker_last_column', 'base', 'ticker_will_be_traced_and_position_entered', 'side', 'stop_loss_is_technical', 'stop_loss_is_calculated', 'market_or_limit_stop_loss', 'market_or_limit_take_profit', 'position_size', 'take_profit_x_to_one', 'exchange_names_string_where_trading_pair_is_traded', 'exchange_id_string_where_trading_pair_is_traded', 'number_of_exchanges_where_pair_is_traded_on', 'spot_without_margin', 'margin', 'cross_margin', 'isolated_margin', 'final_position_entry_price', 'final_stop_loss_price', 'final_position_entry_price_default_value', 'final_stop_loss_price_default_value', 'final_take_profit_price', 'final_take_profit_price_default_value', 'timestamp_when_bfr_was_found', 'datetime_when_bfr_was_found', 'daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first', 'first_bar_after_bfr_opened_lower_than_buy_order', 'take_profit_when_sl_is_technical_3_to_1_is_reached', 'timestamp_take_profit_when_sl_is_technical_3_to_1_was_reached', 'datetime_take_profit_when_sl_is_technical_3_to_1_was_reached', 'technical_stop_loss_is_reached', 'timestamp_when_technical_stop_loss_was_reached', 'datetime_when_technical_stop_loss_was_reached', 'buy_order_was_touched', 'max_distance_from_level_price_in_this_bar_in_atr', 'timestamp_when_buy_order_was_touched', 'datetime_when_buy_order_was_touched', 'max_profit_target_multiple_when_sl_technical', 'take_profit_4_to_one_is_reached_sl_technical', 'take_profit_4_to_one_sl_technical', 'timestamp_of_tp_4_to_one_is_reached_sl_technical', 'datetime_of_tp_4_to_one_is_reached_sl_technical', 'take_profit_5_to_one_is_reached_sl_technical', 'take_profit_5_to_one_sl_technical', 'timestamp_of_tp_5_to_one_is_reached_sl_technical', 'datetime_of_tp_5_to_one_is_reached_sl_technical', 'take_profit_6_to_one_is_reached_sl_technical', 'take_profit_6_to_one_sl_technical', 'timestamp_of_tp_6_to_one_is_reached_sl_technical', 'datetime_of_tp_6_to_one_is_reached_sl_technical', 'take_profit_7_to_one_is_reached_sl_technical', 'take_profit_7_to_one_sl_technical', 'timestamp_of_tp_7_to_one_is_reached_sl_technical', 'datetime_of_tp_7_to_one_is_reached_sl_technical', 'take_profit_8_to_one_is_reached_sl_technical', 'take_profit_8_to_one_sl_technical', 'timestamp_of_tp_8_to_one_is_reached_sl_technical', 'datetime_of_tp_8_to_one_is_reached_sl_technical', 'take_profit_9_to_one_is_reached_sl_technical', 'take_profit_9_to_one_sl_technical', 'timestamp_of_tp_9_to_one_is_reached_sl_technical', 'datetime_of_tp_9_to_one_is_reached_sl_technical', 'take_profit_10_to_one_is_reached_sl_technical', 'take_profit_10_to_one_sl_technical', 'timestamp_of_tp_10_to_one_is_reached_sl_technical', 'datetime_of_tp_10_to_one_is_reached_sl_technical', 'take_profit_11_to_one_is_reached_sl_technical', 'take_profit_11_to_one_sl_technical', 'timestamp_of_tp_11_to_one_is_reached_sl_technical', 'datetime_of_tp_11_to_one_is_reached_sl_technical', 'take_profit_12_to_one_is_reached_sl_technical', 'take_profit_12_to_one_sl_technical', 'timestamp_of_tp_12_to_one_is_reached_sl_technical', 'datetime_of_tp_12_to_one_is_reached_sl_technical', 'take_profit_13_to_one_is_reached_sl_technical', 'take_profit_13_to_one_sl_technical', 'timestamp_of_tp_13_to_one_is_reached_sl_technical', 'datetime_of_tp_13_to_one_is_reached_sl_technical', 'take_profit_14_to_one_is_reached_sl_technical', 'take_profit_14_to_one_sl_technical', 'timestamp_of_tp_14_to_one_is_reached_sl_technical', 'datetime_of_tp_14_to_one_is_reached_sl_technical', 'take_profit_15_to_one_is_reached_sl_technical', 'take_profit_15_to_one_sl_technical', 'timestamp_of_tp_15_to_one_is_reached_sl_technical', 'datetime_of_tp_15_to_one_is_reached_sl_technical', 'take_profit_16_to_one_is_reached_sl_technical', 'take_profit_16_to_one_sl_technical', 'timestamp_of_tp_16_to_one_is_reached_sl_technical', 'datetime_of_tp_16_to_one_is_reached_sl_technical', 'take_profit_17_to_one_is_reached_sl_technical', 'take_profit_17_to_one_sl_technical', 'timestamp_of_tp_17_to_one_is_reached_sl_technical', 'datetime_of_tp_17_to_one_is_reached_sl_technical', 'take_profit_18_to_one_is_reached_sl_technical', 'take_profit_18_to_one_sl_technical', 'timestamp_of_tp_18_to_one_is_reached_sl_technical', 'datetime_of_tp_18_to_one_is_reached_sl_technical', 'take_profit_19_to_one_is_reached_sl_technical', 'take_profit_19_to_one_sl_technical', 'timestamp_of_tp_19_to_one_is_reached_sl_technical', 'datetime_of_tp_19_to_one_is_reached_sl_technical', 'take_profit_20_to_one_is_reached_sl_technical', 'take_profit_20_to_one_sl_technical', 'timestamp_of_tp_20_to_one_is_reached_sl_technical', 'datetime_of_tp_20_to_one_is_reached_sl_technical', 'take_profit_21_to_one_is_reached_sl_technical', 'take_profit_21_to_one_sl_technical', 'timestamp_of_tp_21_to_one_is_reached_sl_technical', 'datetime_of_tp_21_to_one_is_reached_sl_technical', 'take_profit_22_to_one_is_reached_sl_technical', 'take_profit_22_to_one_sl_technical', 'timestamp_of_tp_22_to_one_is_reached_sl_technical', 'datetime_of_tp_22_to_one_is_reached_sl_technical', 'take_profit_23_to_one_is_reached_sl_technical', 'take_profit_23_to_one_sl_technical', 'timestamp_of_tp_23_to_one_is_reached_sl_technical', 'datetime_of_tp_23_to_one_is_reached_sl_technical', 'take_profit_24_to_one_is_reached_sl_technical', 'take_profit_24_to_one_sl_technical', 'timestamp_of_tp_24_to_one_is_reached_sl_technical', 'datetime_of_tp_24_to_one_is_reached_sl_technical', 'take_profit_25_to_one_is_reached_sl_technical', 'take_profit_25_to_one_sl_technical', 'timestamp_of_tp_25_to_one_is_reached_sl_technical', 'datetime_of_tp_25_to_one_is_reached_sl_technical', 'take_profit_26_to_one_is_reached_sl_technical', 'take_profit_26_to_one_sl_technical', 'timestamp_of_tp_26_to_one_is_reached_sl_technical', 'datetime_of_tp_26_to_one_is_reached_sl_technical', 'take_profit_27_to_one_is_reached_sl_technical', 'take_profit_27_to_one_sl_technical', 'timestamp_of_tp_27_to_one_is_reached_sl_technical', 'datetime_of_tp_27_to_one_is_reached_sl_technical', 'take_profit_28_to_one_is_reached_sl_technical', 'take_profit_28_to_one_sl_technical', 'timestamp_of_tp_28_to_one_is_reached_sl_technical', 'datetime_of_tp_28_to_one_is_reached_sl_technical', 'take_profit_29_to_one_is_reached_sl_technical', 'take_profit_29_to_one_sl_technical', 'timestamp_of_tp_29_to_one_is_reached_sl_technical', 'datetime_of_tp_29_to_one_is_reached_sl_technical', 'take_profit_30_to_one_is_reached_sl_technical', 'take_profit_30_to_one_sl_technical', 'timestamp_of_tp_30_to_one_is_reached_sl_technical', 'datetime_of_tp_30_to_one_is_reached_sl_technical', 'take_profit_31_to_one_is_reached_sl_technical', 'take_profit_31_to_one_sl_technical', 'timestamp_of_tp_31_to_one_is_reached_sl_technical', 'datetime_of_tp_31_to_one_is_reached_sl_technical', 'take_profit_32_to_one_is_reached_sl_technical', 'take_profit_32_to_one_sl_technical', 'timestamp_of_tp_32_to_one_is_reached_sl_technical', 'datetime_of_tp_32_to_one_is_reached_sl_technical', 'take_profit_33_to_one_is_reached_sl_technical', 'take_profit_33_to_one_sl_technical', 'timestamp_of_tp_33_to_one_is_reached_sl_technical', 'datetime_of_tp_33_to_one_is_reached_sl_technical', 'take_profit_34_to_one_is_reached_sl_technical', 'take_profit_34_to_one_sl_technical', 'timestamp_of_tp_34_to_one_is_reached_sl_technical', 'datetime_of_tp_34_to_one_is_reached_sl_technical', 'take_profit_35_to_one_is_reached_sl_technical', 'take_profit_35_to_one_sl_technical', 'timestamp_of_tp_35_to_one_is_reached_sl_technical', 'datetime_of_tp_35_to_one_is_reached_sl_technical', 'take_profit_36_to_one_is_reached_sl_technical', 'take_profit_36_to_one_sl_technical', 'timestamp_of_tp_36_to_one_is_reached_sl_technical', 'datetime_of_tp_36_to_one_is_reached_sl_technical', 'take_profit_37_to_one_is_reached_sl_technical', 'take_profit_37_to_one_sl_technical', 'timestamp_of_tp_37_to_one_is_reached_sl_technical', 'datetime_of_tp_37_to_one_is_reached_sl_technical', 'take_profit_38_to_one_is_reached_sl_technical', 'take_profit_38_to_one_sl_technical', 'timestamp_of_tp_38_to_one_is_reached_sl_technical', 'datetime_of_tp_38_to_one_is_reached_sl_technical', 'take_profit_39_to_one_is_reached_sl_technical', 'take_profit_39_to_one_sl_technical', 'timestamp_of_tp_39_to_one_is_reached_sl_technical', 'datetime_of_tp_39_to_one_is_reached_sl_technical', 'take_profit_40_to_one_is_reached_sl_technical', 'take_profit_40_to_one_sl_technical', 'timestamp_of_tp_40_to_one_is_reached_sl_technical', 'datetime_of_tp_40_to_one_is_reached_sl_technical', 'take_profit_41_to_one_is_reached_sl_technical', 'take_profit_41_to_one_sl_technical', 'timestamp_of_tp_41_to_one_is_reached_sl_technical', 'datetime_of_tp_41_to_one_is_reached_sl_technical', 'take_profit_42_to_one_is_reached_sl_technical', 'take_profit_42_to_one_sl_technical', 'timestamp_of_tp_42_to_one_is_reached_sl_technical', 'datetime_of_tp_42_to_one_is_reached_sl_technical', 'take_profit_43_to_one_is_reached_sl_technical', 'take_profit_43_to_one_sl_technical', 'timestamp_of_tp_43_to_one_is_reached_sl_technical', 'datetime_of_tp_43_to_one_is_reached_sl_technical', 'take_profit_44_to_one_is_reached_sl_technical', 'take_profit_44_to_one_sl_technical', 'timestamp_of_tp_44_to_one_is_reached_sl_technical', 'datetime_of_tp_44_to_one_is_reached_sl_technical', 'take_profit_45_to_one_is_reached_sl_technical', 'take_profit_45_to_one_sl_technical', 'timestamp_of_tp_45_to_one_is_reached_sl_technical', 'datetime_of_tp_45_to_one_is_reached_sl_technical', 'take_profit_46_to_one_is_reached_sl_technical', 'take_profit_46_to_one_sl_technical', 'timestamp_of_tp_46_to_one_is_reached_sl_technical', 'datetime_of_tp_46_to_one_is_reached_sl_technical', 'take_profit_47_to_one_is_reached_sl_technical', 'take_profit_47_to_one_sl_technical', 'timestamp_of_tp_47_to_one_is_reached_sl_technical', 'datetime_of_tp_47_to_one_is_reached_sl_technical', 'take_profit_48_to_one_is_reached_sl_technical', 'take_profit_48_to_one_sl_technical', 'timestamp_of_tp_48_to_one_is_reached_sl_technical', 'datetime_of_tp_48_to_one_is_reached_sl_technical', 'take_profit_49_to_one_is_reached_sl_technical', 'take_profit_49_to_one_sl_technical', 'timestamp_of_tp_49_to_one_is_reached_sl_technical', 'datetime_of_tp_49_to_one_is_reached_sl_technical', 'take_profit_50_to_one_is_reached_sl_technical', 'take_profit_50_to_one_sl_technical', 'timestamp_of_tp_50_to_one_is_reached_sl_technical', 'datetime_of_tp_50_to_one_is_reached_sl_technical', 'take_profit_51_to_one_is_reached_sl_technical', 'take_profit_51_to_one_sl_technical', 'timestamp_of_tp_51_to_one_is_reached_sl_technical', 'datetime_of_tp_51_to_one_is_reached_sl_technical', 'take_profit_52_to_one_is_reached_sl_technical', 'take_profit_52_to_one_sl_technical', 'timestamp_of_tp_52_to_one_is_reached_sl_technical', 'datetime_of_tp_52_to_one_is_reached_sl_technical', 'take_profit_53_to_one_is_reached_sl_technical', 'take_profit_53_to_one_sl_technical', 'timestamp_of_tp_53_to_one_is_reached_sl_technical', 'datetime_of_tp_53_to_one_is_reached_sl_technical', 'take_profit_54_to_one_is_reached_sl_technical', 'take_profit_54_to_one_sl_technical', 'timestamp_of_tp_54_to_one_is_reached_sl_technical', 'datetime_of_tp_54_to_one_is_reached_sl_technical', 'take_profit_55_to_one_is_reached_sl_technical', 'take_profit_55_to_one_sl_technical', 'timestamp_of_tp_55_to_one_is_reached_sl_technical', 'datetime_of_tp_55_to_one_is_reached_sl_technical', 'take_profit_56_to_one_is_reached_sl_technical', 'take_profit_56_to_one_sl_technical', 'timestamp_of_tp_56_to_one_is_reached_sl_technical', 'datetime_of_tp_56_to_one_is_reached_sl_technical', 'take_profit_57_to_one_is_reached_sl_technical', 'take_profit_57_to_one_sl_technical', 'timestamp_of_tp_57_to_one_is_reached_sl_technical', 'datetime_of_tp_57_to_one_is_reached_sl_technical', 'take_profit_58_to_one_is_reached_sl_technical', 'take_profit_58_to_one_sl_technical', 'timestamp_of_tp_58_to_one_is_reached_sl_technical', 'datetime_of_tp_58_to_one_is_reached_sl_technical', 'take_profit_59_to_one_is_reached_sl_technical', 'take_profit_59_to_one_sl_technical', 'timestamp_of_tp_59_to_one_is_reached_sl_technical', 'datetime_of_tp_59_to_one_is_reached_sl_technical', 'take_profit_60_to_one_is_reached_sl_technical', 'take_profit_60_to_one_sl_technical', 'timestamp_of_tp_60_to_one_is_reached_sl_technical', 'datetime_of_tp_60_to_one_is_reached_sl_technical', 'take_profit_61_to_one_is_reached_sl_technical', 'take_profit_61_to_one_sl_technical', 'timestamp_of_tp_61_to_one_is_reached_sl_technical', 'datetime_of_tp_61_to_one_is_reached_sl_technical', 'take_profit_62_to_one_is_reached_sl_technical', 'take_profit_62_to_one_sl_technical', 'timestamp_of_tp_62_to_one_is_reached_sl_technical', 'datetime_of_tp_62_to_one_is_reached_sl_technical', 'take_profit_63_to_one_is_reached_sl_technical', 'take_profit_63_to_one_sl_technical', 'timestamp_of_tp_63_to_one_is_reached_sl_technical', 'datetime_of_tp_63_to_one_is_reached_sl_technical', 'take_profit_64_to_one_is_reached_sl_technical', 'take_profit_64_to_one_sl_technical', 'timestamp_of_tp_64_to_one_is_reached_sl_technical', 'datetime_of_tp_64_to_one_is_reached_sl_technical', 'take_profit_65_to_one_is_reached_sl_technical', 'take_profit_65_to_one_sl_technical', 'timestamp_of_tp_65_to_one_is_reached_sl_technical', 'datetime_of_tp_65_to_one_is_reached_sl_technical', 'take_profit_66_to_one_is_reached_sl_technical', 'take_profit_66_to_one_sl_technical', 'timestamp_of_tp_66_to_one_is_reached_sl_technical', 'datetime_of_tp_66_to_one_is_reached_sl_technical', 'take_profit_67_to_one_is_reached_sl_technical', 'take_profit_67_to_one_sl_technical', 'timestamp_of_tp_67_to_one_is_reached_sl_technical', 'datetime_of_tp_67_to_one_is_reached_sl_technical', 'take_profit_68_to_one_is_reached_sl_technical', 'take_profit_68_to_one_sl_technical', 'timestamp_of_tp_68_to_one_is_reached_sl_technical', 'datetime_of_tp_68_to_one_is_reached_sl_technical', 'take_profit_69_to_one_is_reached_sl_technical', 'take_profit_69_to_one_sl_technical', 'timestamp_of_tp_69_to_one_is_reached_sl_technical', 'datetime_of_tp_69_to_one_is_reached_sl_technical', 'take_profit_70_to_one_is_reached_sl_technical', 'take_profit_70_to_one_sl_technical', 'timestamp_of_tp_70_to_one_is_reached_sl_technical', 'datetime_of_tp_70_to_one_is_reached_sl_technical', 'take_profit_71_to_one_is_reached_sl_technical', 'take_profit_71_to_one_sl_technical', 'timestamp_of_tp_71_to_one_is_reached_sl_technical', 'datetime_of_tp_71_to_one_is_reached_sl_technical', 'take_profit_72_to_one_is_reached_sl_technical', 'take_profit_72_to_one_sl_technical', 'timestamp_of_tp_72_to_one_is_reached_sl_technical', 'datetime_of_tp_72_to_one_is_reached_sl_technical', 'take_profit_73_to_one_is_reached_sl_technical', 'take_profit_73_to_one_sl_technical', 'timestamp_of_tp_73_to_one_is_reached_sl_technical', 'datetime_of_tp_73_to_one_is_reached_sl_technical', 'take_profit_74_to_one_is_reached_sl_technical', 'take_profit_74_to_one_sl_technical', 'timestamp_of_tp_74_to_one_is_reached_sl_technical', 'datetime_of_tp_74_to_one_is_reached_sl_technical', 'take_profit_75_to_one_is_reached_sl_technical', 'take_profit_75_to_one_sl_technical', 'timestamp_of_tp_75_to_one_is_reached_sl_technical', 'datetime_of_tp_75_to_one_is_reached_sl_technical', 'take_profit_76_to_one_is_reached_sl_technical', 'take_profit_76_to_one_sl_technical', 'timestamp_of_tp_76_to_one_is_reached_sl_technical', 'datetime_of_tp_76_to_one_is_reached_sl_technical', 'take_profit_77_to_one_is_reached_sl_technical', 'take_profit_77_to_one_sl_technical', 'timestamp_of_tp_77_to_one_is_reached_sl_technical', 'datetime_of_tp_77_to_one_is_reached_sl_technical', 'take_profit_78_to_one_is_reached_sl_technical', 'take_profit_78_to_one_sl_technical', 'timestamp_of_tp_78_to_one_is_reached_sl_technical', 'datetime_of_tp_78_to_one_is_reached_sl_technical', 'take_profit_79_to_one_is_reached_sl_technical', 'take_profit_79_to_one_sl_technical', 'timestamp_of_tp_79_to_one_is_reached_sl_technical', 'datetime_of_tp_79_to_one_is_reached_sl_technical', 'take_profit_80_to_one_is_reached_sl_technical', 'take_profit_80_to_one_sl_technical', 'timestamp_of_tp_80_to_one_is_reached_sl_technical', 'datetime_of_tp_80_to_one_is_reached_sl_technical', 'take_profit_81_to_one_is_reached_sl_technical', 'take_profit_81_to_one_sl_technical', 'timestamp_of_tp_81_to_one_is_reached_sl_technical', 'datetime_of_tp_81_to_one_is_reached_sl_technical', 'take_profit_82_to_one_is_reached_sl_technical', 'take_profit_82_to_one_sl_technical', 'timestamp_of_tp_82_to_one_is_reached_sl_technical', 'datetime_of_tp_82_to_one_is_reached_sl_technical', 'take_profit_83_to_one_is_reached_sl_technical', 'take_profit_83_to_one_sl_technical', 'timestamp_of_tp_83_to_one_is_reached_sl_technical', 'datetime_of_tp_83_to_one_is_reached_sl_technical', 'take_profit_84_to_one_is_reached_sl_technical', 'take_profit_84_to_one_sl_technical', 'timestamp_of_tp_84_to_one_is_reached_sl_technical', 'datetime_of_tp_84_to_one_is_reached_sl_technical', 'take_profit_85_to_one_is_reached_sl_technical', 'take_profit_85_to_one_sl_technical', 'timestamp_of_tp_85_to_one_is_reached_sl_technical', 'datetime_of_tp_85_to_one_is_reached_sl_technical', 'take_profit_86_to_one_is_reached_sl_technical', 'take_profit_86_to_one_sl_technical', 'timestamp_of_tp_86_to_one_is_reached_sl_technical', 'datetime_of_tp_86_to_one_is_reached_sl_technical', 'take_profit_87_to_one_is_reached_sl_technical', 'take_profit_87_to_one_sl_technical', 'timestamp_of_tp_87_to_one_is_reached_sl_technical', 'datetime_of_tp_87_to_one_is_reached_sl_technical', 'take_profit_88_to_one_is_reached_sl_technical', 'take_profit_88_to_one_sl_technical', 'timestamp_of_tp_88_to_one_is_reached_sl_technical', 'datetime_of_tp_88_to_one_is_reached_sl_technical', 'take_profit_89_to_one_is_reached_sl_technical', 'take_profit_89_to_one_sl_technical', 'timestamp_of_tp_89_to_one_is_reached_sl_technical', 'datetime_of_tp_89_to_one_is_reached_sl_technical', 'take_profit_90_to_one_is_reached_sl_technical', 'take_profit_90_to_one_sl_technical', 'timestamp_of_tp_90_to_one_is_reached_sl_technical', 'datetime_of_tp_90_to_one_is_reached_sl_technical', 'take_profit_91_to_one_is_reached_sl_technical', 'take_profit_91_to_one_sl_technical', 'timestamp_of_tp_91_to_one_is_reached_sl_technical', 'datetime_of_tp_91_to_one_is_reached_sl_technical', 'take_profit_92_to_one_is_reached_sl_technical', 'take_profit_92_to_one_sl_technical', 'timestamp_of_tp_92_to_one_is_reached_sl_technical', 'datetime_of_tp_92_to_one_is_reached_sl_technical', 'take_profit_93_to_one_is_reached_sl_technical', 'take_profit_93_to_one_sl_technical', 'timestamp_of_tp_93_to_one_is_reached_sl_technical', 'datetime_of_tp_93_to_one_is_reached_sl_technical', 'take_profit_94_to_one_is_reached_sl_technical', 'take_profit_94_to_one_sl_technical', 'timestamp_of_tp_94_to_one_is_reached_sl_technical', 'datetime_of_tp_94_to_one_is_reached_sl_technical', 'take_profit_95_to_one_is_reached_sl_technical', 'take_profit_95_to_one_sl_technical', 'timestamp_of_tp_95_to_one_is_reached_sl_technical', 'datetime_of_tp_95_to_one_is_reached_sl_technical', 'take_profit_96_to_one_is_reached_sl_technical', 'take_profit_96_to_one_sl_technical', 'timestamp_of_tp_96_to_one_is_reached_sl_technical', 'datetime_of_tp_96_to_one_is_reached_sl_technical', 'take_profit_97_to_one_is_reached_sl_technical', 'take_profit_97_to_one_sl_technical', 'timestamp_of_tp_97_to_one_is_reached_sl_technical', 'datetime_of_tp_97_to_one_is_reached_sl_technical', 'take_profit_98_to_one_is_reached_sl_technical', 'take_profit_98_to_one_sl_technical', 'timestamp_of_tp_98_to_one_is_reached_sl_technical', 'datetime_of_tp_98_to_one_is_reached_sl_technical', 'take_profit_99_to_one_is_reached_sl_technical', 'take_profit_99_to_one_sl_technical', 'timestamp_of_tp_99_to_one_is_reached_sl_technical', 'datetime_of_tp_99_to_one_is_reached_sl_technical', 'take_profit_100_to_one_is_reached_sl_technical', 'take_profit_100_to_one_sl_technical', 'timestamp_of_tp_100_to_one_is_reached_sl_technical', 'datetime_of_tp_100_to_one_is_reached_sl_technical', 'take_profit_when_sl_is_calculated_3_to_1_is_reached', 'timestamp_take_profit_when_sl_is_calculated_3_to_1_was_reached', 'datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached', 'calculated_stop_loss_is_reached', 'timestamp_when_calculated_stop_loss_was_reached', 'datetime_when_calculated_stop_loss_was_reached', 'max_profit_target_multiple_when_sl_calculated', 'take_profit_4_to_one_is_reached_sl_calculated', 'take_profit_4_to_one_sl_calculated', 'timestamp_of_tp_4_to_one_is_reached_sl_calculated', 'datetime_of_tp_4_to_one_is_reached_sl_calculated', 'take_profit_5_to_one_is_reached_sl_calculated', 'take_profit_5_to_one_sl_calculated', 'timestamp_of_tp_5_to_one_is_reached_sl_calculated', 'datetime_of_tp_5_to_one_is_reached_sl_calculated', 'take_profit_6_to_one_is_reached_sl_calculated', 'take_profit_6_to_one_sl_calculated', 'timestamp_of_tp_6_to_one_is_reached_sl_calculated', 'datetime_of_tp_6_to_one_is_reached_sl_calculated', 'take_profit_7_to_one_is_reached_sl_calculated', 'take_profit_7_to_one_sl_calculated', 'timestamp_of_tp_7_to_one_is_reached_sl_calculated', 'datetime_of_tp_7_to_one_is_reached_sl_calculated', 'take_profit_8_to_one_is_reached_sl_calculated', 'take_profit_8_to_one_sl_calculated', 'timestamp_of_tp_8_to_one_is_reached_sl_calculated', 'datetime_of_tp_8_to_one_is_reached_sl_calculated', 'take_profit_9_to_one_is_reached_sl_calculated', 'take_profit_9_to_one_sl_calculated', 'timestamp_of_tp_9_to_one_is_reached_sl_calculated', 'datetime_of_tp_9_to_one_is_reached_sl_calculated', 'take_profit_10_to_one_is_reached_sl_calculated', 'take_profit_10_to_one_sl_calculated', 'timestamp_of_tp_10_to_one_is_reached_sl_calculated', 'datetime_of_tp_10_to_one_is_reached_sl_calculated', 'take_profit_11_to_one_is_reached_sl_calculated', 'take_profit_11_to_one_sl_calculated', 'timestamp_of_tp_11_to_one_is_reached_sl_calculated', 'datetime_of_tp_11_to_one_is_reached_sl_calculated', 'take_profit_12_to_one_is_reached_sl_calculated', 'take_profit_12_to_one_sl_calculated', 'timestamp_of_tp_12_to_one_is_reached_sl_calculated', 'datetime_of_tp_12_to_one_is_reached_sl_calculated', 'take_profit_13_to_one_is_reached_sl_calculated', 'take_profit_13_to_one_sl_calculated', 'timestamp_of_tp_13_to_one_is_reached_sl_calculated', 'datetime_of_tp_13_to_one_is_reached_sl_calculated', 'take_profit_14_to_one_is_reached_sl_calculated', 'take_profit_14_to_one_sl_calculated', 'timestamp_of_tp_14_to_one_is_reached_sl_calculated', 'datetime_of_tp_14_to_one_is_reached_sl_calculated', 'take_profit_15_to_one_is_reached_sl_calculated', 'take_profit_15_to_one_sl_calculated', 'timestamp_of_tp_15_to_one_is_reached_sl_calculated', 'datetime_of_tp_15_to_one_is_reached_sl_calculated', 'take_profit_16_to_one_is_reached_sl_calculated', 'take_profit_16_to_one_sl_calculated', 'timestamp_of_tp_16_to_one_is_reached_sl_calculated', 'datetime_of_tp_16_to_one_is_reached_sl_calculated', 'take_profit_17_to_one_is_reached_sl_calculated', 'take_profit_17_to_one_sl_calculated', 'timestamp_of_tp_17_to_one_is_reached_sl_calculated', 'datetime_of_tp_17_to_one_is_reached_sl_calculated', 'take_profit_18_to_one_is_reached_sl_calculated', 'take_profit_18_to_one_sl_calculated', 'timestamp_of_tp_18_to_one_is_reached_sl_calculated', 'datetime_of_tp_18_to_one_is_reached_sl_calculated', 'take_profit_19_to_one_is_reached_sl_calculated', 'take_profit_19_to_one_sl_calculated', 'timestamp_of_tp_19_to_one_is_reached_sl_calculated', 'datetime_of_tp_19_to_one_is_reached_sl_calculated', 'take_profit_20_to_one_is_reached_sl_calculated', 'take_profit_20_to_one_sl_calculated', 'timestamp_of_tp_20_to_one_is_reached_sl_calculated', 'datetime_of_tp_20_to_one_is_reached_sl_calculated', 'take_profit_21_to_one_is_reached_sl_calculated', 'take_profit_21_to_one_sl_calculated', 'timestamp_of_tp_21_to_one_is_reached_sl_calculated', 'datetime_of_tp_21_to_one_is_reached_sl_calculated', 'take_profit_22_to_one_is_reached_sl_calculated', 'take_profit_22_to_one_sl_calculated', 'timestamp_of_tp_22_to_one_is_reached_sl_calculated', 'datetime_of_tp_22_to_one_is_reached_sl_calculated', 'take_profit_23_to_one_is_reached_sl_calculated', 'take_profit_23_to_one_sl_calculated', 'timestamp_of_tp_23_to_one_is_reached_sl_calculated', 'datetime_of_tp_23_to_one_is_reached_sl_calculated', 'take_profit_24_to_one_is_reached_sl_calculated', 'take_profit_24_to_one_sl_calculated', 'timestamp_of_tp_24_to_one_is_reached_sl_calculated', 'datetime_of_tp_24_to_one_is_reached_sl_calculated', 'take_profit_25_to_one_is_reached_sl_calculated', 'take_profit_25_to_one_sl_calculated', 'timestamp_of_tp_25_to_one_is_reached_sl_calculated', 'datetime_of_tp_25_to_one_is_reached_sl_calculated', 'take_profit_26_to_one_is_reached_sl_calculated', 'take_profit_26_to_one_sl_calculated', 'timestamp_of_tp_26_to_one_is_reached_sl_calculated', 'datetime_of_tp_26_to_one_is_reached_sl_calculated', 'take_profit_27_to_one_is_reached_sl_calculated', 'take_profit_27_to_one_sl_calculated', 'timestamp_of_tp_27_to_one_is_reached_sl_calculated', 'datetime_of_tp_27_to_one_is_reached_sl_calculated', 'take_profit_28_to_one_is_reached_sl_calculated', 'take_profit_28_to_one_sl_calculated', 'timestamp_of_tp_28_to_one_is_reached_sl_calculated', 'datetime_of_tp_28_to_one_is_reached_sl_calculated', 'take_profit_29_to_one_is_reached_sl_calculated', 'take_profit_29_to_one_sl_calculated', 'timestamp_of_tp_29_to_one_is_reached_sl_calculated', 'datetime_of_tp_29_to_one_is_reached_sl_calculated', 'take_profit_30_to_one_is_reached_sl_calculated', 'take_profit_30_to_one_sl_calculated', 'timestamp_of_tp_30_to_one_is_reached_sl_calculated', 'datetime_of_tp_30_to_one_is_reached_sl_calculated', 'take_profit_31_to_one_is_reached_sl_calculated', 'take_profit_31_to_one_sl_calculated', 'timestamp_of_tp_31_to_one_is_reached_sl_calculated', 'datetime_of_tp_31_to_one_is_reached_sl_calculated', 'take_profit_32_to_one_is_reached_sl_calculated', 'take_profit_32_to_one_sl_calculated', 'timestamp_of_tp_32_to_one_is_reached_sl_calculated', 'datetime_of_tp_32_to_one_is_reached_sl_calculated', 'take_profit_33_to_one_is_reached_sl_calculated', 'take_profit_33_to_one_sl_calculated', 'timestamp_of_tp_33_to_one_is_reached_sl_calculated', 'datetime_of_tp_33_to_one_is_reached_sl_calculated', 'take_profit_34_to_one_is_reached_sl_calculated', 'take_profit_34_to_one_sl_calculated', 'timestamp_of_tp_34_to_one_is_reached_sl_calculated', 'datetime_of_tp_34_to_one_is_reached_sl_calculated', 'take_profit_35_to_one_is_reached_sl_calculated', 'take_profit_35_to_one_sl_calculated', 'timestamp_of_tp_35_to_one_is_reached_sl_calculated', 'datetime_of_tp_35_to_one_is_reached_sl_calculated', 'take_profit_36_to_one_is_reached_sl_calculated', 'take_profit_36_to_one_sl_calculated', 'timestamp_of_tp_36_to_one_is_reached_sl_calculated', 'datetime_of_tp_36_to_one_is_reached_sl_calculated', 'take_profit_37_to_one_is_reached_sl_calculated', 'take_profit_37_to_one_sl_calculated', 'timestamp_of_tp_37_to_one_is_reached_sl_calculated', 'datetime_of_tp_37_to_one_is_reached_sl_calculated', 'take_profit_38_to_one_is_reached_sl_calculated', 'take_profit_38_to_one_sl_calculated', 'timestamp_of_tp_38_to_one_is_reached_sl_calculated', 'datetime_of_tp_38_to_one_is_reached_sl_calculated', 'take_profit_39_to_one_is_reached_sl_calculated', 'take_profit_39_to_one_sl_calculated', 'timestamp_of_tp_39_to_one_is_reached_sl_calculated', 'datetime_of_tp_39_to_one_is_reached_sl_calculated', 'take_profit_40_to_one_is_reached_sl_calculated', 'take_profit_40_to_one_sl_calculated', 'timestamp_of_tp_40_to_one_is_reached_sl_calculated', 'datetime_of_tp_40_to_one_is_reached_sl_calculated', 'take_profit_41_to_one_is_reached_sl_calculated', 'take_profit_41_to_one_sl_calculated', 'timestamp_of_tp_41_to_one_is_reached_sl_calculated', 'datetime_of_tp_41_to_one_is_reached_sl_calculated', 'take_profit_42_to_one_is_reached_sl_calculated', 'take_profit_42_to_one_sl_calculated', 'timestamp_of_tp_42_to_one_is_reached_sl_calculated', 'datetime_of_tp_42_to_one_is_reached_sl_calculated', 'take_profit_43_to_one_is_reached_sl_calculated', 'take_profit_43_to_one_sl_calculated', 'timestamp_of_tp_43_to_one_is_reached_sl_calculated', 'datetime_of_tp_43_to_one_is_reached_sl_calculated', 'take_profit_44_to_one_is_reached_sl_calculated', 'take_profit_44_to_one_sl_calculated', 'timestamp_of_tp_44_to_one_is_reached_sl_calculated', 'datetime_of_tp_44_to_one_is_reached_sl_calculated', 'take_profit_45_to_one_is_reached_sl_calculated', 'take_profit_45_to_one_sl_calculated', 'timestamp_of_tp_45_to_one_is_reached_sl_calculated', 'datetime_of_tp_45_to_one_is_reached_sl_calculated', 'take_profit_46_to_one_is_reached_sl_calculated', 'take_profit_46_to_one_sl_calculated', 'timestamp_of_tp_46_to_one_is_reached_sl_calculated', 'datetime_of_tp_46_to_one_is_reached_sl_calculated', 'take_profit_47_to_one_is_reached_sl_calculated', 'take_profit_47_to_one_sl_calculated', 'timestamp_of_tp_47_to_one_is_reached_sl_calculated', 'datetime_of_tp_47_to_one_is_reached_sl_calculated', 'take_profit_48_to_one_is_reached_sl_calculated', 'take_profit_48_to_one_sl_calculated', 'timestamp_of_tp_48_to_one_is_reached_sl_calculated', 'datetime_of_tp_48_to_one_is_reached_sl_calculated', 'take_profit_49_to_one_is_reached_sl_calculated', 'take_profit_49_to_one_sl_calculated', 'timestamp_of_tp_49_to_one_is_reached_sl_calculated', 'datetime_of_tp_49_to_one_is_reached_sl_calculated', 'take_profit_50_to_one_is_reached_sl_calculated', 'take_profit_50_to_one_sl_calculated', 'timestamp_of_tp_50_to_one_is_reached_sl_calculated', 'datetime_of_tp_50_to_one_is_reached_sl_calculated', 'take_profit_51_to_one_is_reached_sl_calculated', 'take_profit_51_to_one_sl_calculated', 'timestamp_of_tp_51_to_one_is_reached_sl_calculated', 'datetime_of_tp_51_to_one_is_reached_sl_calculated', 'take_profit_52_to_one_is_reached_sl_calculated', 'take_profit_52_to_one_sl_calculated', 'timestamp_of_tp_52_to_one_is_reached_sl_calculated', 'datetime_of_tp_52_to_one_is_reached_sl_calculated', 'take_profit_53_to_one_is_reached_sl_calculated', 'take_profit_53_to_one_sl_calculated', 'timestamp_of_tp_53_to_one_is_reached_sl_calculated', 'datetime_of_tp_53_to_one_is_reached_sl_calculated', 'take_profit_54_to_one_is_reached_sl_calculated', 'take_profit_54_to_one_sl_calculated', 'timestamp_of_tp_54_to_one_is_reached_sl_calculated', 'datetime_of_tp_54_to_one_is_reached_sl_calculated', 'take_profit_55_to_one_is_reached_sl_calculated', 'take_profit_55_to_one_sl_calculated', 'timestamp_of_tp_55_to_one_is_reached_sl_calculated', 'datetime_of_tp_55_to_one_is_reached_sl_calculated', 'take_profit_56_to_one_is_reached_sl_calculated', 'take_profit_56_to_one_sl_calculated', 'timestamp_of_tp_56_to_one_is_reached_sl_calculated', 'datetime_of_tp_56_to_one_is_reached_sl_calculated', 'take_profit_57_to_one_is_reached_sl_calculated', 'take_profit_57_to_one_sl_calculated', 'timestamp_of_tp_57_to_one_is_reached_sl_calculated', 'datetime_of_tp_57_to_one_is_reached_sl_calculated', 'take_profit_58_to_one_is_reached_sl_calculated', 'take_profit_58_to_one_sl_calculated', 'timestamp_of_tp_58_to_one_is_reached_sl_calculated', 'datetime_of_tp_58_to_one_is_reached_sl_calculated', 'take_profit_59_to_one_is_reached_sl_calculated', 'take_profit_59_to_one_sl_calculated', 'timestamp_of_tp_59_to_one_is_reached_sl_calculated', 'datetime_of_tp_59_to_one_is_reached_sl_calculated', 'take_profit_60_to_one_is_reached_sl_calculated', 'take_profit_60_to_one_sl_calculated', 'timestamp_of_tp_60_to_one_is_reached_sl_calculated', 'datetime_of_tp_60_to_one_is_reached_sl_calculated', 'take_profit_61_to_one_is_reached_sl_calculated', 'take_profit_61_to_one_sl_calculated', 'timestamp_of_tp_61_to_one_is_reached_sl_calculated', 'datetime_of_tp_61_to_one_is_reached_sl_calculated', 'take_profit_62_to_one_is_reached_sl_calculated', 'take_profit_62_to_one_sl_calculated', 'timestamp_of_tp_62_to_one_is_reached_sl_calculated', 'datetime_of_tp_62_to_one_is_reached_sl_calculated', 'take_profit_63_to_one_is_reached_sl_calculated', 'take_profit_63_to_one_sl_calculated', 'timestamp_of_tp_63_to_one_is_reached_sl_calculated', 'datetime_of_tp_63_to_one_is_reached_sl_calculated', 'take_profit_64_to_one_is_reached_sl_calculated', 'take_profit_64_to_one_sl_calculated', 'timestamp_of_tp_64_to_one_is_reached_sl_calculated', 'datetime_of_tp_64_to_one_is_reached_sl_calculated', 'take_profit_65_to_one_is_reached_sl_calculated', 'take_profit_65_to_one_sl_calculated', 'timestamp_of_tp_65_to_one_is_reached_sl_calculated', 'datetime_of_tp_65_to_one_is_reached_sl_calculated', 'take_profit_66_to_one_is_reached_sl_calculated', 'take_profit_66_to_one_sl_calculated', 'timestamp_of_tp_66_to_one_is_reached_sl_calculated', 'datetime_of_tp_66_to_one_is_reached_sl_calculated', 'take_profit_67_to_one_is_reached_sl_calculated', 'take_profit_67_to_one_sl_calculated', 'timestamp_of_tp_67_to_one_is_reached_sl_calculated', 'datetime_of_tp_67_to_one_is_reached_sl_calculated', 'take_profit_68_to_one_is_reached_sl_calculated', 'take_profit_68_to_one_sl_calculated', 'timestamp_of_tp_68_to_one_is_reached_sl_calculated', 'datetime_of_tp_68_to_one_is_reached_sl_calculated', 'take_profit_69_to_one_is_reached_sl_calculated', 'take_profit_69_to_one_sl_calculated', 'timestamp_of_tp_69_to_one_is_reached_sl_calculated', 'datetime_of_tp_69_to_one_is_reached_sl_calculated', 'take_profit_70_to_one_is_reached_sl_calculated', 'take_profit_70_to_one_sl_calculated', 'timestamp_of_tp_70_to_one_is_reached_sl_calculated', 'datetime_of_tp_70_to_one_is_reached_sl_calculated', 'take_profit_71_to_one_is_reached_sl_calculated', 'take_profit_71_to_one_sl_calculated', 'timestamp_of_tp_71_to_one_is_reached_sl_calculated', 'datetime_of_tp_71_to_one_is_reached_sl_calculated', 'take_profit_72_to_one_is_reached_sl_calculated', 'take_profit_72_to_one_sl_calculated', 'timestamp_of_tp_72_to_one_is_reached_sl_calculated', 'datetime_of_tp_72_to_one_is_reached_sl_calculated', 'take_profit_73_to_one_is_reached_sl_calculated', 'take_profit_73_to_one_sl_calculated', 'timestamp_of_tp_73_to_one_is_reached_sl_calculated', 'datetime_of_tp_73_to_one_is_reached_sl_calculated', 'take_profit_74_to_one_is_reached_sl_calculated', 'take_profit_74_to_one_sl_calculated', 'timestamp_of_tp_74_to_one_is_reached_sl_calculated', 'datetime_of_tp_74_to_one_is_reached_sl_calculated', 'take_profit_75_to_one_is_reached_sl_calculated', 'take_profit_75_to_one_sl_calculated', 'timestamp_of_tp_75_to_one_is_reached_sl_calculated', 'datetime_of_tp_75_to_one_is_reached_sl_calculated', 'take_profit_76_to_one_is_reached_sl_calculated', 'take_profit_76_to_one_sl_calculated', 'timestamp_of_tp_76_to_one_is_reached_sl_calculated', 'datetime_of_tp_76_to_one_is_reached_sl_calculated', 'take_profit_77_to_one_is_reached_sl_calculated', 'take_profit_77_to_one_sl_calculated', 'timestamp_of_tp_77_to_one_is_reached_sl_calculated', 'datetime_of_tp_77_to_one_is_reached_sl_calculated', 'take_profit_78_to_one_is_reached_sl_calculated', 'take_profit_78_to_one_sl_calculated', 'timestamp_of_tp_78_to_one_is_reached_sl_calculated', 'datetime_of_tp_78_to_one_is_reached_sl_calculated', 'take_profit_79_to_one_is_reached_sl_calculated', 'take_profit_79_to_one_sl_calculated', 'timestamp_of_tp_79_to_one_is_reached_sl_calculated', 'datetime_of_tp_79_to_one_is_reached_sl_calculated', 'take_profit_80_to_one_is_reached_sl_calculated', 'take_profit_80_to_one_sl_calculated', 'timestamp_of_tp_80_to_one_is_reached_sl_calculated', 'datetime_of_tp_80_to_one_is_reached_sl_calculated', 'take_profit_81_to_one_is_reached_sl_calculated', 'take_profit_81_to_one_sl_calculated', 'timestamp_of_tp_81_to_one_is_reached_sl_calculated', 'datetime_of_tp_81_to_one_is_reached_sl_calculated', 'take_profit_82_to_one_is_reached_sl_calculated', 'take_profit_82_to_one_sl_calculated', 'timestamp_of_tp_82_to_one_is_reached_sl_calculated', 'datetime_of_tp_82_to_one_is_reached_sl_calculated', 'take_profit_83_to_one_is_reached_sl_calculated', 'take_profit_83_to_one_sl_calculated', 'timestamp_of_tp_83_to_one_is_reached_sl_calculated', 'datetime_of_tp_83_to_one_is_reached_sl_calculated', 'take_profit_84_to_one_is_reached_sl_calculated', 'take_profit_84_to_one_sl_calculated', 'timestamp_of_tp_84_to_one_is_reached_sl_calculated', 'datetime_of_tp_84_to_one_is_reached_sl_calculated', 'take_profit_85_to_one_is_reached_sl_calculated', 'take_profit_85_to_one_sl_calculated', 'timestamp_of_tp_85_to_one_is_reached_sl_calculated', 'datetime_of_tp_85_to_one_is_reached_sl_calculated', 'take_profit_86_to_one_is_reached_sl_calculated', 'take_profit_86_to_one_sl_calculated', 'timestamp_of_tp_86_to_one_is_reached_sl_calculated', 'datetime_of_tp_86_to_one_is_reached_sl_calculated', 'take_profit_87_to_one_is_reached_sl_calculated', 'take_profit_87_to_one_sl_calculated', 'timestamp_of_tp_87_to_one_is_reached_sl_calculated', 'datetime_of_tp_87_to_one_is_reached_sl_calculated', 'take_profit_88_to_one_is_reached_sl_calculated', 'take_profit_88_to_one_sl_calculated', 'timestamp_of_tp_88_to_one_is_reached_sl_calculated', 'datetime_of_tp_88_to_one_is_reached_sl_calculated', 'take_profit_89_to_one_is_reached_sl_calculated', 'take_profit_89_to_one_sl_calculated', 'timestamp_of_tp_89_to_one_is_reached_sl_calculated', 'datetime_of_tp_89_to_one_is_reached_sl_calculated', 'take_profit_90_to_one_is_reached_sl_calculated', 'take_profit_90_to_one_sl_calculated', 'timestamp_of_tp_90_to_one_is_reached_sl_calculated', 'datetime_of_tp_90_to_one_is_reached_sl_calculated', 'take_profit_91_to_one_is_reached_sl_calculated', 'take_profit_91_to_one_sl_calculated', 'timestamp_of_tp_91_to_one_is_reached_sl_calculated', 'datetime_of_tp_91_to_one_is_reached_sl_calculated', 'take_profit_92_to_one_is_reached_sl_calculated', 'take_profit_92_to_one_sl_calculated', 'timestamp_of_tp_92_to_one_is_reached_sl_calculated', 'datetime_of_tp_92_to_one_is_reached_sl_calculated', 'take_profit_93_to_one_is_reached_sl_calculated', 'take_profit_93_to_one_sl_calculated', 'timestamp_of_tp_93_to_one_is_reached_sl_calculated', 'datetime_of_tp_93_to_one_is_reached_sl_calculated', 'take_profit_94_to_one_is_reached_sl_calculated', 'take_profit_94_to_one_sl_calculated', 'timestamp_of_tp_94_to_one_is_reached_sl_calculated', 'datetime_of_tp_94_to_one_is_reached_sl_calculated', 'take_profit_95_to_one_is_reached_sl_calculated', 'take_profit_95_to_one_sl_calculated', 'timestamp_of_tp_95_to_one_is_reached_sl_calculated', 'datetime_of_tp_95_to_one_is_reached_sl_calculated', 'take_profit_96_to_one_is_reached_sl_calculated', 'take_profit_96_to_one_sl_calculated', 'timestamp_of_tp_96_to_one_is_reached_sl_calculated', 'datetime_of_tp_96_to_one_is_reached_sl_calculated', 'take_profit_97_to_one_is_reached_sl_calculated', 'take_profit_97_to_one_sl_calculated', 'timestamp_of_tp_97_to_one_is_reached_sl_calculated', 'datetime_of_tp_97_to_one_is_reached_sl_calculated', 'take_profit_98_to_one_is_reached_sl_calculated', 'take_profit_98_to_one_sl_calculated', 'timestamp_of_tp_98_to_one_is_reached_sl_calculated', 'datetime_of_tp_98_to_one_is_reached_sl_calculated', 'take_profit_99_to_one_is_reached_sl_calculated', 'take_profit_99_to_one_sl_calculated', 'timestamp_of_tp_99_to_one_is_reached_sl_calculated', 'datetime_of_tp_99_to_one_is_reached_sl_calculated', 'take_profit_100_to_one_is_reached_sl_calculated', 'take_profit_100_to_one_sl_calculated', 'timestamp_of_tp_100_to_one_is_reached_sl_calculated', 'datetime_of_tp_100_to_one_is_reached_sl_calculated'])
                df_with_level_atr_bpu_bsu_etc = pd.DataFrame(dtype='object')
                df_with_level_atr_bpu_bsu_etc.at[0, "ticker"] = stock_name
                df_with_level_atr_bpu_bsu_etc.at[0, "exchange"] = exchange

                df_with_level_atr_bpu_bsu_etc.at[0, "model"] = "ПРОБОЙ_ATH_с_подтверждением_вход_на_следующий_день"
                df_with_level_atr_bpu_bsu_etc.at[0, "ath"] = all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "advanced_atr"] = advanced_atr

                df_with_level_atr_bpu_bsu_etc.at[0, "advanced_atr_over_this_period"] = \
                    advanced_atr_over_this_period
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_bsu"] = all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_bsu"] = volume_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_bsu"] = timestamp_of_last_all_time_high
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_bsu"] = date_of_last_ath


                df_with_level_atr_bpu_bsu_etc.at[0, "open_of_breakout_bar"] = open_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "high_of_breakout_bar"] = high_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "low_of_breakout_bar"] = low_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "close_of_breakout_bar"] = close_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "volume_of_breakout_bar"] = volume_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_breakout_bar"] = timestamp_of_breakout_bar
                df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_breakout_bar"] = date_of_breakout_bar

                df_with_level_atr_bpu_bsu_etc.at[0, "min_volume_over_last_n_days"] =  last_two_years_of_data['volume'].tail(count_min_volume_over_this_many_days).min()
                df_with_level_atr_bpu_bsu_etc.at[0, "count_min_volume_over_this_many_days"] = count_min_volume_over_this_many_days

                df_with_level_atr_bpu_bsu_etc.at[0, "min_volume_in_usd_over_last_n_days"] = last_two_years_of_data[
                    'volume*low'].tail(
                    count_min_volume_over_this_many_days).min()

                df_with_level_atr_bpu_bsu_etc.at[0, "buy_order"] = buy_order
                df_with_level_atr_bpu_bsu_etc.at[0, "calculated_stop_loss"] = calculated_stop_loss
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_calculated_3_to_1"] = take_profit_when_sl_is_calculated_3_to_1
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_calculated_4_to_1"] = take_profit_when_sl_is_calculated_4_to_1

                distance_between_calculated_stop_loss_and_buy_order = buy_order - calculated_stop_loss
                distance_between_calculated_stop_loss_and_buy_order_in_atr = \
                    distance_between_calculated_stop_loss_and_buy_order / advanced_atr
                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_calculated_sl_and_buy_order_in_atr"] =\
                    distance_between_calculated_stop_loss_and_buy_order_in_atr
                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_calculated_sl_and_buy_order"] = \
                    distance_between_calculated_stop_loss_and_buy_order

                df_with_level_atr_bpu_bsu_etc.at[0, "technical_stop_loss"] = technical_stop_loss
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_technical_3_to_1"] = take_profit_when_sl_is_technical_3_to_1
                df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_technical_4_to_1"] = take_profit_when_sl_is_technical_4_to_1
                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_technical_sl_and_buy_order_in_atr"] = distance_between_technical_stop_loss_and_buy_order_in_atr

                df_with_level_atr_bpu_bsu_etc.at[0, "distance_between_technical_sl_and_buy_order"] = distance_between_technical_stop_loss_and_buy_order

                df_with_level_atr_bpu_bsu_etc.at[0, "suppression_by_lows"] = suppression_flag_for_lows
                df_with_level_atr_bpu_bsu_etc.at[0, "number_of_bars_when_we_check_suppression_by_lows"] = number_of_bars_when_we_check_suppression_by_lows
                df_with_level_atr_bpu_bsu_etc.at[0, "suppression_by_closes"] = suppression_flag_for_closes
                df_with_level_atr_bpu_bsu_etc.at[0, "number_of_bars_when_we_check_suppression_by_closes"] = number_of_bars_when_we_check_suppression_by_closes

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
                #
                #     df_with_level_atr_bpu_bsu_etc = fill_df_with_info_if_ath_was_broken_on_other_exchanges(stock_name,
                #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_0000,
                #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_1600,
                #                                                                                            table_with_ohlcv_data_df,
                #                                                                                            engine_for_ohlcv_data_for_stocks_0000,
                #                                                                                            engine_for_ohlcv_data_for_stocks_1600,
                #                                                                                            all_time_high,
                #                                                                                            list_of_tables_in_ohlcv_db_1600,
                #                                                                                            df_with_level_atr_bpu_bsu_etc,
                #                                                                                            0)
                # except:
                #     traceback.print_exc()

                df_with_level_atr_bpu_bsu_etc.at[0, "ticker_last_column"] = stock_name
                try:
                    df_with_level_atr_bpu_bsu_etc.at[0, "base"] = get_base_of_trading_pair(trading_pair=stock_name)
                except:
                    traceback.print_exc()
                df_with_level_atr_bpu_bsu_etc.at[0, "ticker_will_be_traced_and_position_entered"] = False

                side = "buy"
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
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_position_entry_price"]= buy_order
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_stop_loss_price"] = technical_stop_loss
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_position_entry_price_default_value"] = buy_order
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_stop_loss_price_default_value"] = technical_stop_loss
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_take_profit_price"] = take_profit_when_sl_is_technical_3_to_1
                    df_with_level_atr_bpu_bsu_etc.at[0, "final_take_profit_price_default_value"] = take_profit_when_sl_is_technical_3_to_1
                    df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_bfr_was_found"] = int(time.time())
                    df_with_level_atr_bpu_bsu_etc.at[0, "trade_status"] = "must_verify_if_bfr_conditions_are_fulfilled"
                    df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_bfr_was_found"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    df_with_level_atr_bpu_bsu_etc.at[0, "utc_position_entry_time"] = ""
                    df_with_level_atr_bpu_bsu_etc.at[0, "include_last_day_in_bfr_model_assessment"] = True
                except:
                    traceback.print_exc()



                ################################
                ################################
                # ################################
                #
                # try:
                #     # add statistical info to df if calculated sl and tp have been reached
                #     take_profit_when_sl_is_calculated_3_to_1_is_reached, \
                #     calculated_stop_loss_is_reached, \
                #     daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
                #     timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached, \
                #     timestamp_when_calculated_stop_loss_was_reached, \
                #     buy_order_was_touched, \
                #     timestamp_when_buy_order_was_touched, \
                #     first_bar_after_bfr_opened_lower_than_buy_order=return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached(index_in_iteration,
                #                                                              entire_original_table_with_ohlcv_data_df,
                #                                                              table_with_ohlcv_data_df,
                #                                                              side,
                #                                                              buy_order,
                #                                                              take_profit_when_sl_is_calculated_3_to_1,
                #                                                              calculated_stop_loss)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "first_bar_after_bfr_opened_lower_than_buy_order"] = first_bar_after_bfr_opened_lower_than_buy_order
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "take_profit_when_sl_is_calculated_3_to_1_is_reached"] = take_profit_when_sl_is_calculated_3_to_1_is_reached
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached
                #     if pd.isna(timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached) == False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = \
                #             datetime.datetime.fromtimestamp(
                #                 timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                #                 0)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "calculated_stop_loss_is_reached"] = calculated_stop_loss_is_reached
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_when_calculated_stop_loss_was_reached"] = timestamp_when_calculated_stop_loss_was_reached
                #     if pd.isna(timestamp_when_calculated_stop_loss_was_reached) == False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_calculated_stop_loss_was_reached"] = \
                #             datetime.datetime.fromtimestamp(
                #                 timestamp_when_calculated_stop_loss_was_reached)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_calculated_stop_loss_was_reached"] = datetime.datetime.fromtimestamp(
                #                 0)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "buy_order_was_touched"] = buy_order_was_touched
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_when_buy_order_was_touched"] = timestamp_when_buy_order_was_touched
                #     if pd.isna(timestamp_when_buy_order_was_touched) == False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_buy_order_was_touched"] = \
                #             datetime.datetime.fromtimestamp(
                #                 timestamp_when_buy_order_was_touched)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_buy_order_was_touched"] = datetime.datetime.fromtimestamp(
                #                 0)
                # except:
                #     traceback.print_exc()
                #
                # try:
                #     # add statistical info to df if technical sl and tp have been reached
                #     take_profit_when_sl_is_technical_3_to_1_is_reached, \
                #         technical_stop_loss_is_reached, \
                #         daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
                #         timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached, \
                #         timestamp_when_technical_stop_loss_was_reached, \
                #         buy_order_was_touched, \
                #         timestamp_when_buy_order_was_touched,\
                #         first_bar_after_bfr_opened_lower_than_buy_order=return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached(index_in_iteration,
                #                                                              entire_original_table_with_ohlcv_data_df,
                #                                                              table_with_ohlcv_data_df,
                #                                                              side,
                #                                                              buy_order,
                #                                                              take_profit_when_sl_is_technical_3_to_1,
                #                                                              technical_stop_loss)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "first_bar_after_bfr_opened_lower_than_buy_order"] = first_bar_after_bfr_opened_lower_than_buy_order
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "take_profit_when_sl_is_technical_3_to_1_is_reached"] = take_profit_when_sl_is_technical_3_to_1_is_reached
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_take_profit_when_sl_is_technical_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached
                #     if pd.isna(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached)==False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] =\
                #             datetime.datetime.fromtimestamp(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                #                 0)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "technical_stop_loss_is_reached"] = technical_stop_loss_is_reached
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_when_technical_stop_loss_was_reached"] = timestamp_when_technical_stop_loss_was_reached
                #     if pd.isna(timestamp_when_technical_stop_loss_was_reached)==False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_technical_stop_loss_was_reached"] = \
                #             datetime.datetime.fromtimestamp(
                #                 timestamp_when_technical_stop_loss_was_reached)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_technical_stop_loss_was_reached"] =datetime.datetime.fromtimestamp(
                #                 0)
                #
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "buy_order_was_touched"] = buy_order_was_touched
                #     df_with_level_atr_bpu_bsu_etc.loc[
                #         0, "timestamp_when_buy_order_was_touched"] = timestamp_when_buy_order_was_touched
                #     if pd.isna(timestamp_when_buy_order_was_touched)==False:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_buy_order_was_touched"] = \
                #             datetime.datetime.fromtimestamp(
                #                 timestamp_when_buy_order_was_touched)
                #     else:
                #         df_with_level_atr_bpu_bsu_etc.loc[
                #             0, "datetime_when_buy_order_was_touched"] = datetime.datetime.fromtimestamp(
                #                 0)
                # except:
                #     traceback.print_exc()

                try:
                    # add info to df if sl, order, and tp were reached
                    level_price=all_time_high
                    df_with_level_atr_bpu_bsu_etc=add_to_df_result_of_return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached(
                        level_price,
                        advanced_atr,
                        df_with_level_atr_bpu_bsu_etc,
                        index_in_iteration,
                        entire_original_table_with_ohlcv_data_df,
                        side,
                        buy_order,
                        take_profit_when_sl_is_technical_3_to_1,
                        technical_stop_loss)

                    df_with_level_atr_bpu_bsu_etc=add_to_df_result_of_return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached(
                        level_price,
                        advanced_atr,
                        df_with_level_atr_bpu_bsu_etc,
                        index_in_iteration,
                        entire_original_table_with_ohlcv_data_df,
                        side,
                        buy_order,
                        take_profit_when_sl_is_calculated_3_to_1,
                        calculated_stop_loss)
                except:
                    traceback.print_exc()

                ############################################
                ############################################
                ############################################

                # print("df_with_level_atr_bpu_bsu_etc.columns")
                # print(list(df_with_level_atr_bpu_bsu_etc.columns))

                # print("number_of_times_this_all_time_high_occurred")
                # print(number_of_times_this_all_time_high_occurred)
                # print("timestamps_of_all_time_highs_as_string")
                # print(timestamps_of_all_time_highs_as_string)
                # print("open_times_of_all_time_highs_as_string")
                # print(open_times_of_all_time_highs_as_string)

                round_to_this_number_of_non_zero_digits=2
                try:
                    df_with_level_atr_bpu_bsu_etc=add_info_to_df_about_all_time_high_number_of_times_it_was_touched_its_timestamps_and_datetimes(
                        all_time_high,
                        df_with_level_atr_bpu_bsu_etc,
                        last_two_years_of_data,
                        round_to_this_number_of_non_zero_digits)
                except:
                    traceback.print_exc()

                try:
                    # add found bfr to new db where there is no table drop
                    df_with_level_atr_bpu_bsu_etc.to_sql(
                        table_where_ticker_which_may_have_breakout_situations_from_ath_will_be,
                        engine_for_db_where_ticker_which_may_have_breakout_situations_hist,
                        if_exists='append')

                except:
                    traceback.print_exc()

            # df_with_level_atr_bpu_bsu_etc.to_sql(
            #     table_where_ticker_which_may_have_breakout_situations_from_ath_will_be,
            #     engine_for_db_where_ticker_which_may_have_breakout_situations,
            #     if_exists='append')
            # print_df_to_file(df_with_level_atr_bpu_bsu_etc,
            #                  'current_rebound_breakout_and_false_breakout')


        except:
            traceback.print_exc()

    # string_for_output = f"Список инструментов, которые сформировали модель ПРОБОЙ исторического максимума (с подтверждением)." \
    #                     f"Вход на следующий день после пробоя:\n" \
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
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_low_volume_usdt_pairs_0000_pagination"
    count_only_round_rebound_level=False
    db_where_ticker_which_may_have_breakout_situations=\
        "levels_formed_by_highs_and_lows_for_cryptos_0000"
    table_where_ticker_which_may_have_breakout_situations_from_ath_will_be =\
        "current_breakout_situations_of_ath_position_entry_next_day"
    table_where_ticker_which_may_have_breakout_situations_from_atl_will_be =\
        "current_breakout_situations_of_atl_position_entry_next_day"

    if count_only_round_rebound_level:
        db_where_ticker_which_may_have_breakout_situations=\
            "round_levels_formed_by_highs_and_lows_for_cryptos_0000"
    #0.05 means 5%
    
    atr_over_this_period = 30
    advanced_atr_over_this_period=30
    number_of_bars_in_suppression_to_check_for_volume_acceptance=14
    factor_to_multiply_atr_by_to_check_suppression=1
    count_min_volume_over_this_many_days=7
    search_for_tickers_with_breakout_situations(
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              db_where_ticker_which_may_have_breakout_situations,
                                              table_where_ticker_which_may_have_breakout_situations_from_ath_will_be,
                                                table_where_ticker_which_may_have_breakout_situations_from_atl_will_be,
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