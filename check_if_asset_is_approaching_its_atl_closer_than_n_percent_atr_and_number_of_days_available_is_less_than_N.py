from statistics import mean
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
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
from get_info_from_load_markets import get_spread
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_ath_was_broken_on_other_exchanges
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_atl_was_broken_on_other_exchanges
from check_if_asset_has_new_atl import get_last_row_as_dataframe
def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
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

def calculate_atr_without_paranormal_bars_from_numpy_array(atr_over_this_period,
                  numpy_array_slice,
                  row_number_last_bar):
    list_of_true_ranges = []
    advanced_atr=False
    percentile_20=False
    percentile_80=False
    number_of_rows_in_numpy_array=len(numpy_array_slice)
    array_of_true_ranges=False
    np.set_printoptions(threshold=np.inf)
    # print("numpy_array_slice")
    # print(numpy_array_slice)
    # print("atr_over_this_period")
    # print(atr_over_this_period)
    # print("row_number_last_bar")
    # print(row_number_last_bar)
    # print("number_of_rows_in_numpy_array")
    # print(number_of_rows_in_numpy_array)
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
    # print("array_of_true_ranges")
    # print(array_of_true_ranges)

    list_of_non_rejected_true_ranges = []
    for true_range_in_array in array_of_true_ranges:

        if true_range_in_array >= percentile_20 and true_range_in_array <= percentile_80:
            list_of_non_rejected_true_ranges.append ( true_range_in_array )
    # print("list_of_non_rejected_true_ranges")
    # print ( list_of_non_rejected_true_ranges )
    advanced_atr = mean ( list_of_non_rejected_true_ranges )

    return advanced_atr

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

def get_all_time_low_from_ohlcv_table(engine_for_ohlcv_data_for_stocks,
                                      table_with_ohlcv_table):
    table_with_ohlcv_data_df = \
        pd.read_sql_query ( f'''select * from "{table_with_ohlcv_table}"''' ,
                            engine_for_ohlcv_data_for_stocks )
    # print("table_with_ohlcv_data_df")
    # print ( table_with_ohlcv_data_df )

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

def get_columns_from_table(engine, table):

    cursor=engine.execute(f"""
    select COLUMN_NAME from information_schema.columns where table_name='{table}'
    """)
    return [row[0] for row in cursor]
def get_columns(df):
    return list(df.columns)

def sql_add_columns(table_name, columns_to_be_added_to_sql_table,engine):
    for column_name in columns_to_be_added_to_sql_table:
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
        engine.execute(sql)

def get_new_list_of_elements_that_are_present_in_first_list_and_absent_in_second(list1, list2):
    return [elem for elem in list1 if elem not in list2]

def add_lacking_columns_to_sql_db_atl_used(last_row_of_levels_formed_by_atl_df,
                                  engine_for_db_where_levels_formed_by_atl_will_be):

    columns_in_partial_sql_table_models_list = get_columns_from_table(
        engine_for_db_where_levels_formed_by_atl_will_be,
        table_where_levels_formed_by_atl_will_be)
    list_of_columns_in_one_row_df = get_columns(last_row_of_levels_formed_by_atl_df)
    columns_to_be_added_to_sql_table = \
        get_new_list_of_elements_that_are_present_in_first_list_and_absent_in_second(
            list_of_columns_in_one_row_df, columns_in_partial_sql_table_models_list)

    print("columns_to_be_added_to_sql_table")
    print(columns_to_be_added_to_sql_table)
    if len(columns_to_be_added_to_sql_table) > 0:
        sql_add_columns(table_where_levels_formed_by_atl_will_be,
                        columns_to_be_added_to_sql_table,
                        engine_for_db_where_levels_formed_by_atl_will_be)

def check_if_asset_is_approaching_its_atl(db_where_ohlcv_data_for_stocks_is_stored_for_todays_pairs,
                                          minimum_number_of_days_available,
                                          percentage_between_ath_and_closing_price_of_atr,
                                          advanced_atr_over_this_period,
                                          db_where_ohlcv_data_for_stocks_is_stored,
                                          count_only_round_atl,
                                          db_where_levels_formed_by_atl_will_be,
                                          table_where_levels_formed_by_atl_will_be):

    levels_formed_by_atl_df=pd.DataFrame(columns = ["ticker",
                                                    "atl",
                                                    "exchange",
                                                    "short_name",
                                                    "timestamp_1",
                                                    "timestamp_2",
                                                    "timestamp_3"])
    list_of_assets_with_last_close_close_to_atl=[]


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    engine_for_ohlcv_data_for_stocks_for_todays_pairs, \
        connection_to_ohlcv_data_for_stocks_for_todays_pairs = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_for_todays_pairs)

    engine_for_db_where_levels_formed_by_atl_will_be , \
    connection_to_db_where_levels_formed_by_atl_will_be = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_levels_formed_by_atl_will_be )

    drop_table ( table_where_levels_formed_by_atl_will_be ,
                 engine_for_db_where_levels_formed_by_atl_will_be )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )

    list_of_tables_in_ohlcv_db_for_todays_pairs = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_for_todays_pairs)

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
    for stock_name in list_of_tables_in_ohlcv_db:
        counter=counter+1
        print ( f'{stock_name} is'
                f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )

        # if stock_name!="HLBZ":
        #     continue

        all_time_low_in_stock, table_with_ohlcv_data_df=\
            get_all_time_low_from_ohlcv_table ( engine_for_ohlcv_data_for_stocks ,
                                            stock_name )

        # if the df is empty do not continue the current loop
        if table_with_ohlcv_data_df.empty:
            continue

        # number_of_available_days
        number_of_available_days = np.nan
        try:
            number_of_available_days = len(table_with_ohlcv_data_df)
        except:
            traceback.print_exc()

        print("table_with_ohlcv_data_df")
        print(table_with_ohlcv_data_df.tail(10).to_string())


        # calculate_volume_over_this_period=30
        # min_volume_over_n_days=min(table_with_ohlcv_data_df["volume"].tail(calculate_volume_over_this_period))
        # print("min_volume_over_n_days")
        # print(min_volume_over_n_days)
        # if min_volume_over_n_days<750:
        #     continue

        if count_only_round_atl==True:
            level_is_round_bool=find_if_level_is_round ( all_time_low_in_stock )
            if not level_is_round_bool:
                print(f"in {stock_name} level={all_time_low_in_stock} is not round and is ATL")
                continue

        last_close_price = np.nan
        try:
            last_close_price = get_last_close_price_of_asset(table_with_ohlcv_data_df)
        except:
            traceback.print_exc()
        print("last_close_price")
        print ( last_close_price)

        last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)
        last_two_years_of_data_numpy_array = last_two_years_of_data.to_numpy()
        last_bar_number = last_two_years_of_data.index[-1]
        advanced_atr = \
            calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                   last_two_years_of_data_numpy_array,
                                                                   last_bar_number)


        distance_from_last_close_price_to_atl=last_close_price-all_time_low_in_stock

        if distance_from_last_close_price_to_atl <= advanced_atr*(percentage_between_ath_and_closing_price_of_atr/100.0):
            # print(f"last closing price={last_close_price} is"
            #       f" within {percentage_between_atl_and_closing_price}% range to atl={all_time_low_in_stock}")
            list_of_assets_with_last_close_close_to_atl.append(stock_name)
            print(f"list_of_assets_with_last_close_closer_to_ath_than_{percentage_between_ath_and_closing_price_of_atr}%ATR({advanced_atr_over_this_period})")
            print(f"last_close_price_for_stock={stock_name}")
            print(last_close_price)
            print(f"advanced_atr_for_stock={stock_name}")
            print(advanced_atr)
            print(f"all_time_low_in_stock_for_stock={stock_name}")
            print(all_time_low_in_stock)
            print(f"distance_from_last_close_price_to_atl_in_stock_for_stock={stock_name}")
            print(distance_from_last_close_price_to_atl)


            print("list_of_assets_with_last_close_close_to_atl")
            print ( list_of_assets_with_last_close_close_to_atl )



            df_where_low_equals_atl=\
                table_with_ohlcv_data_df[table_with_ohlcv_data_df["low"]==all_time_low_in_stock]
            print ( "df_where_low_equals_atl" )
            print ( df_where_low_equals_atl )
            exchange=table_with_ohlcv_data_df["exchange"].iat[0]
            # short_name = table_with_ohlcv_data_df["short_name"].iat[0]


            levels_formed_by_atl_df.at[counter - 1 , "ticker"] = stock_name
            levels_formed_by_atl_df.at[counter - 1 , "exchange"] = exchange
            # levels_formed_by_atl_df.at[counter - 1 , "short_name"] = short_name
            levels_formed_by_atl_df.at[
                counter - 1, "model"] = f"РАССТОЯНИЕ ОТ CLOSE ДО ATL <{percentage_between_ath_and_closing_price_of_atr}% ATR"
            levels_formed_by_atl_df.at[counter - 1 , "atl"] = all_time_low_in_stock
            levels_formed_by_atl_df.at[counter - 1, "advanced_atr"] = advanced_atr
            levels_formed_by_atl_df.at[counter - 1, "advanced_atr_over_this_period"] = \
                advanced_atr_over_this_period




            for number_of_timestamp,timestamp_of_atl in enumerate(df_where_low_equals_atl.loc[:,"Timestamp"]):
                print("number_of_timestamp")
                print ( number_of_timestamp )
                print ( "timestamp_of_atl" )
                print ( timestamp_of_atl )
                levels_formed_by_atl_df.at[counter - 1 , f"timestamp_{number_of_timestamp+1}"]=\
                    timestamp_of_atl





            print("levels_formed_by_atl_df")
            print ( levels_formed_by_atl_df )

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)

                levels_formed_by_atl_df.at[counter - 1, "asset_type"] = asset_type
                levels_formed_by_atl_df.at[counter - 1, "maker_fee"] = maker_fee
                levels_formed_by_atl_df.at[counter - 1, "taker_fee"] = taker_fee
                levels_formed_by_atl_df.at[counter - 1, "url_of_trading_pair"] = url_of_trading_pair
                levels_formed_by_atl_df.at[counter - 1, "number_of_available_bars"] = number_of_available_days
            except:
                traceback.print_exc()


            try:
                #############################################
                # add info to dataframe about whether level was broken on other exchanges
                levels_formed_by_atl_df = fill_df_with_info_if_atl_was_broken_on_other_exchanges(stock_name,
                                                                                                       db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                                                                       db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                                                                       table_with_ohlcv_data_df,
                                                                                                       engine_for_ohlcv_data_for_stocks_0000,
                                                                                                       engine_for_ohlcv_data_for_stocks_1600,
                                                                                                       all_time_low_in_stock,
                                                                                                       list_of_tables_in_ohlcv_db_1600,
                                                                                                       levels_formed_by_atl_df,
                                                                                                       counter-1)
            except:
                traceback.print_exc()

            distance_from_last_close_price_to_atl_in_atr = distance_from_last_close_price_to_atl / advanced_atr
            levels_formed_by_atl_df.at[counter - 1, "distance_from_last_close_price_to_atl_in_atr"] = \
                distance_from_last_close_price_to_atl_in_atr


            last_row_of_levels_formed_by_atl_df = get_last_row_as_dataframe(levels_formed_by_atl_df)



            #add lacking column to the sql table if these columns are in df but not in db table
            if len(levels_formed_by_atl_df)>1:
                try:
                    add_lacking_columns_to_sql_db_atl_used(last_row_of_levels_formed_by_atl_df,
                                                  engine_for_db_where_levels_formed_by_atl_will_be)
                except:
                    traceback.print_exc()

            last_row_of_levels_formed_by_atl_df.to_sql(table_where_levels_formed_by_atl_will_be,
                                                       engine_for_db_where_levels_formed_by_atl_will_be,
                                                       if_exists='append')

            # table_name = "from_close_to_ath_less_than_n_of_atr_and_has_less_than_n_days"
            # column_name = "timestamp_4"
            # sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"
            # engine_for_db_where_levels_formed_by_atl_will_be.execute(sql)
            # print("column added")
            # time.sleep(50000000000000)


    levels_formed_by_atl_df.reset_index(inplace = True)
    string_for_output = f"Список инструментов, в которых расстояние от " \
                        f"цены закрытия до цены исторического минимума <{percentage_between_ath_and_closing_price_of_atr}% ATR({advanced_atr_over_this_period}):\n\n" \
                        f"{list_of_assets_with_last_close_close_to_atl}"

    # Use the function to create a text file with the text
    # in the subdirectory "current_rebound_breakout_and_false_breakout"
    create_text_file_and_writ_text_to_it(string_for_output, 'current_rebound_breakout_and_false_breakout')
    # levels_formed_by_atl_df.to_sql(table_where_levels_formed_by_atl_will_be,
    #                                engine_for_db_where_levels_formed_by_atl_will_be,
    #                                if_exists = 'replace')
    # print ( "levels_formed_by_atl_df" )
    # print ( levels_formed_by_atl_df )


if __name__=="__main__":
    percentage_between_ath_and_closing_price_of_atr=100
    minimum_number_of_days_available = 50
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000"
    db_where_ohlcv_data_for_stocks_is_stored_for_todays_pairs = "ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    count_only_round_atl=False
    db_where_levels_formed_by_atl_will_be="levels_formed_by_highs_and_lows_for_cryptos_0000"
    table_where_levels_formed_by_atl_will_be = "from_close_to_atl_less_than_n_of_atr_and_has_less_than_n_days"

    if count_only_round_atl:
        db_where_levels_formed_by_atl_will_be="round_levels_formed_by_highs_and_lows_for_cryptos_0000"

    advanced_atr_over_this_period=30
    check_if_asset_is_approaching_its_atl(db_where_ohlcv_data_for_stocks_is_stored_for_todays_pairs,
                                          minimum_number_of_days_available,
                                          percentage_between_ath_and_closing_price_of_atr,
                                          advanced_atr_over_this_period,
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                                count_only_round_atl,
                                              db_where_levels_formed_by_atl_will_be,
                                              table_where_levels_formed_by_atl_will_be)