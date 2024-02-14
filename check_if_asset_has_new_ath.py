from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
from get_info_from_load_markets import get_spread
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
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_row_number_when_timestamp_is_index
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_ath_timestamp_and_row_number
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_atl_timestamp_and_row_number
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_ath_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_atl_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_ath_timestamp_and_row_number
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_last_atl_timestamp_and_row_number

from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_exchange_of_trading_pair
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_row_number_when_timestamp_is_not_index
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_low_for_timestamp
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import remove_first_underscore
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_closest_timestamp_low_low_plus_one_day_using_index
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_closest_timestamp_high_high_plus_one_day_using_index
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_closest_timestamp_high_closest_timestamp_plus_one_day_high_plus_one_day
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_closest_timestamp_low_closest_timestamp_plus_one_day_low_plus_one_day
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import find_high_for_timestamp
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_row_number_when_timestamp_is_index
from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
from get_info_from_load_markets import get_spread
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_atl_was_broken_on_other_exchanges
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_engine_for_1600_ohlcv_database
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_engine_for_0000_ohlcv_database
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import drop_duplicates_in_string_in_which_names_are_separated_by_underscores
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_ath_was_broken_on_other_exchanges
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import fill_df_with_info_if_atl_was_broken_on_other_exchanges
def get_last_row_as_dataframe(df):
    """
    Creates a new data frame consisting of only the last row of the given data frame
    """
    last_row_index = df.index[-1]
    last_row_df = df.loc[[last_row_index]]
    return last_row_df

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

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db

def get_last_high_price_of_asset(ohlcv_table_df):
    last_high_price=ohlcv_table_df["high"].iat[-1]
    return last_high_price

def get_second_last_high_price_of_asset(ohlcv_table_df):
    second_last_high_price=ohlcv_table_df["high"].iat[-2]
    return second_last_high_price

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
    print("ohlcv_table_df3")
    print(ohlcv_table_df)
    last_close_price=ohlcv_table_df["close"].iat[-1]
    return last_close_price

import os
import datetime

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




def check_if_asset_is_approaching_its_ath(percentage_between_ath_and_closing_price,
                                          db_where_ohlcv_data_for_stocks_is_stored,
                                          count_only_round_ath,
                                          db_where_levels_formed_by_ath_will_be,
                                          table_where_levels_formed_by_ath_will_be):

    levels_formed_by_ath_df=pd.DataFrame(columns = ["ticker",
                                                    "ath",
                                                    "exchange",
                                                    "short_name",
                                                    "timestamp_1",
                                                    "timestamp_2",
                                                    "timestamp_3"])
    list_of_assets_with_last_close_close_to_ath=[]


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    #we will iterate over each row of this df to understand if ath or atl was broken on a 2 year time period on different exchanges
    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names=\
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(db_where_ohlcv_data_for_stocks_is_stored)




    engine_for_db_where_levels_formed_by_ath_will_be , \
    connection_to_db_where_levels_formed_by_ath_will_be = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_levels_formed_by_ath_will_be )

    drop_table ( table_where_levels_formed_by_ath_will_be ,
                 engine_for_db_where_levels_formed_by_ath_will_be )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )


##########################################################
    db_where_ohlcv_data_for_stocks_is_stored_0000=np.nan
    db_where_ohlcv_data_for_stocks_is_stored_1600=np.nan
    engine_for_ohlcv_data_for_stocks_0000=np.nan
    engine_for_ohlcv_data_for_stocks_1600=np.nan
    list_of_tables_in_ohlcv_db_1600=np.nan

    try:
        #######################################################################################
        ###################################################################################
        db_where_ohlcv_data_for_stocks_is_stored_0000=db_where_ohlcv_data_for_stocks_is_stored
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
        all_time_high_in_stock, table_with_ohlcv_data_df=\
            get_all_time_high_from_ohlcv_table ( engine_for_ohlcv_data_for_stocks ,
                                            stock_name )




        # number_of_available_days
        number_of_available_days = np.nan
        try:
            number_of_available_days = len(table_with_ohlcv_data_df)
        except:
            traceback.print_exc()

        if count_only_round_ath==True:
            level_is_round_bool=find_if_level_is_round ( all_time_high_in_stock )
            if not level_is_round_bool:
                print(f"in {stock_name} level={all_time_high_in_stock} is not round and is ATL")
                continue
        last_close_price=np.nan
        try:
            last_close_price=get_last_close_price_of_asset ( table_with_ohlcv_data_df )
        except:
            traceback.print_exc()
        print("last_close_price")
        print ( last_close_price)

        last_high_price = np.nan
        try:
            last_high_price = get_last_high_price_of_asset(table_with_ohlcv_data_df)
        except:
            traceback.print_exc()
        print("last_high_price")
        print(last_high_price)

        second_last_high_price = np.nan
        try:
            second_last_high_price = get_second_last_high_price_of_asset(table_with_ohlcv_data_df)
        except:
            traceback.print_exc()
        print("second_last_high_price")
        print(second_last_high_price)


        # distance_in_percent_to_ath_from_close_price=\
        #     (all_time_high_in_stock-last_close_price)/all_time_high_in_stock
        if all_time_high_in_stock==last_high_price or all_time_high_in_stock==second_last_high_price:
            # print(f"last closing price={last_close_price} is"
            #       f" within {percentage_between_ath_and_closing_price}% range to ath={all_time_high_in_stock}")
            list_of_assets_with_last_close_close_to_ath.append(stock_name)
            print("list_of_assets_with_last_close_close_to_ath")
            print ( list_of_assets_with_last_close_close_to_ath )
            df_where_high_equals_ath=\
                table_with_ohlcv_data_df[table_with_ohlcv_data_df["high"]==all_time_high_in_stock]
            print ( "df_where_high_equals_ath" )
            print ( df_where_high_equals_ath )
            exchange=table_with_ohlcv_data_df["exchange"].iat[0]
            # short_name = table_with_ohlcv_data_df["short_name"].iat[0]


            levels_formed_by_ath_df.at[counter - 1 , "ticker"] = stock_name
            levels_formed_by_ath_df.at[counter - 1 , "exchange"] = exchange
            # levels_formed_by_ath_df.at[counter - 1 , "short_name"] = short_name
            levels_formed_by_ath_df.at[
                counter - 1, "model"] = "Новый All Time High"
            levels_formed_by_ath_df.at[counter - 1 , "ath"] = all_time_high_in_stock
            for number_of_timestamp,timestamp_of_ath in enumerate(df_where_high_equals_ath.loc[:,"Timestamp"]):
                print("number_of_timestamp")
                print ( number_of_timestamp )
                print ( "timestamp_of_ath" )
                print ( timestamp_of_ath )
                levels_formed_by_ath_df.at[counter - 1 , f"timestamp_{number_of_timestamp+1}"]=\
                    timestamp_of_ath





            print("levels_formed_by_ath_df")
            print ( levels_formed_by_ath_df )
            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)

                levels_formed_by_ath_df.at[counter - 1, "asset_type"] = asset_type
                levels_formed_by_ath_df.at[counter - 1, "maker_fee"] = maker_fee
                levels_formed_by_ath_df.at[counter - 1, "taker_fee"] = taker_fee
                levels_formed_by_ath_df.at[counter - 1, "url_of_trading_pair"] = url_of_trading_pair
                levels_formed_by_ath_df.at[counter - 1, "number_of_available_bars"] = number_of_available_days
            except:
                traceback.print_exc()
            try:
                #############################################
                # add info to dataframe about whether level was broken on other exchanges
                levels_formed_by_ath_df = fill_df_with_info_if_ath_was_broken_on_other_exchanges(stock_name,
                                                                                                 db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                                                                 db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                                                                 table_with_ohlcv_data_df,
                                                                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                                                                 engine_for_ohlcv_data_for_stocks_1600,
                                                                                                 all_time_high_in_stock,
                                                                                                 list_of_tables_in_ohlcv_db_1600,
                                                                                                 levels_formed_by_ath_df,
                                                                                                 counter-1)
            except:
                traceback.print_exc()

            last_row_of_levels_formed_by_atl_df = get_last_row_as_dataframe(levels_formed_by_ath_df)
            last_row_of_levels_formed_by_atl_df.to_sql(table_where_levels_formed_by_ath_will_be,
                                                       engine_for_db_where_levels_formed_by_ath_will_be,
                                                       if_exists='append')

    #         ################################################################################
    #         ######################################################################################
    #         # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
    #         df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000 = \
    #             return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
    #                 db_where_ohlcv_data_for_stocks_is_stored_0000)
    #
    #         print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000")
    #         print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.to_string())
    #         #########################################################################################################
    #
    #         ######################################################################################
    #
    #
    #         # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
    #         df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600 = \
    #             return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
    #                 db_where_ohlcv_data_for_stocks_is_stored_1600)
    #
    #         print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600")
    #         print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.to_string())
    #         #######################################################################################################
    #
    #         #get base of trading pair
    #         base=get_base_of_trading_pair(trading_pair=stock_name)
    #
    #         # # get base of trading pair
    #         # exchange_of_pair = get_exchange_of_trading_pair(trading_pair=stock_name)
    #         #get ohlcv_data_df from different exchanges for one base in trading_pair
    #
    #         counter_of_number_of_exchanges_where_level_had_been_broken = 0
    #         string_of_exchanges_where_level_was_broken = ""
    #         string_of_all_exchanges_where_pair_is_traded = ""
    #         string_of_exchanges_where_level_was_not_broken = ""
    #
    #         for col in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.columns:
    #             print("column_name")
    #             print(col)
    #             if 'table_name' in col:
    #                 ################################
    #                 table_with_ohlcv_data_df = table_with_ohlcv_data_df[
    #                     ["Timestamp", "open", "high", "low", "close", "volume"]]
    #                 table_with_ohlcv_data_df_numpy_array = table_with_ohlcv_data_df.to_numpy()
    #                 # print("table_with_ohlcv_data_df_numpy_array")
    #                 # print(table_with_ohlcv_data_df_numpy_array)
    #                 last_ath_timestamp, last_ath_row_number_in_the_original_table = \
    #                     get_last_ath_timestamp_and_row_number(table_with_ohlcv_data_df_numpy_array,
    #                                                           all_time_high_in_stock)
    #
    #
    #                 for trading_pair_with_exchange_table_name_in_ohlcv_database in [df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.loc[base, col]]:
    #                     if pd.isna(trading_pair_with_exchange_table_name_in_ohlcv_database):
    #                         print("trading_pair_with_exchange_table_name_in_ohlcv_database is nan")
    #                         continue
    #                     print("trading_pair_with_exchange_table_name_in_ohlcv_databaseue_of_cell_if_df_it_should_be_table_name")
    #                     print(trading_pair_with_exchange_table_name_in_ohlcv_database)
    #
    #                     table_with_0000_ohlcv_data_df_on_other_exchanges = \
    #                         pd.read_sql_query(f'''select * from "{trading_pair_with_exchange_table_name_in_ohlcv_database}"''',
    #                                           engine_for_ohlcv_data_for_stocks_0000)
    #                     print("table_with_ohlcv_data_df_on_other_exchanges1")
    #                     print(table_with_0000_ohlcv_data_df_on_other_exchanges.tail(5).to_string())
    #                     print("trading_pair_with_exchange_table_name_in_ohlcv_database1")
    #                     print(trading_pair_with_exchange_table_name_in_ohlcv_database)
    #
    #                     exchange_of_pair = get_exchange_of_trading_pair(trading_pair=trading_pair_with_exchange_table_name_in_ohlcv_database)
    #                     print("exchange_of_pair")
    #                     print(exchange_of_pair)
    #
    #
    #                     row_number_in_ohlcv_table_on_other_exchanges=\
    #                         get_row_number_when_timestamp_is_not_index(table_with_0000_ohlcv_data_df_on_other_exchanges,
    #                                                                last_ath_timestamp)
    #                     print("row_number_in_ohlcv_table_on_other_exchanges")
    #                     print(row_number_in_ohlcv_table_on_other_exchanges)
    #                     table_with_0000_ohlcv_data_df_on_other_exchanges = table_with_0000_ohlcv_data_df_on_other_exchanges[
    #                         ["Timestamp", "open", "high", "low", "close", "volume"]]
    #                     table_with_ohlcv_data_df_on_other_exchanges_numpy_array = table_with_0000_ohlcv_data_df_on_other_exchanges.to_numpy()
    #                     high_on_another_exchange=find_high_for_timestamp(last_ath_timestamp, table_with_ohlcv_data_df_on_other_exchanges_numpy_array)
    #                     number_of_days_where_ath_was_not_broken=2*366
    #                     ath_is_not_broken_for_a_long_time=check_ath_breakout(table_with_ohlcv_data_df_on_other_exchanges_numpy_array,
    #                                        number_of_days_where_ath_was_not_broken,
    #                                        high_on_another_exchange,
    #                                        row_number_in_ohlcv_table_on_other_exchanges)
    #                     print(f"ath for {base} is not broken = {ath_is_not_broken_for_a_long_time}")
    #
    #                     string_of_all_exchanges_where_pair_is_traded=string_of_all_exchanges_where_pair_is_traded+"_"+exchange_of_pair
    #                     string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
    #                         string_of_all_exchanges_where_pair_is_traded)
    #                     if ath_is_not_broken_for_a_long_time==False:
    #                         counter_of_number_of_exchanges_where_level_had_been_broken=\
    #                             counter_of_number_of_exchanges_where_level_had_been_broken+1
    #                         string_of_exchanges_where_level_was_broken=string_of_exchanges_where_level_was_broken+"_"+exchange_of_pair
    #                         string_of_exchanges_where_level_was_broken=remove_first_underscore(string_of_exchanges_where_level_was_broken)
    #                     else:
    #                         string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair
    #                         string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
    #                             string_of_exchanges_where_level_was_not_broken)
    #
    #                     #check if pair with the same base is traded on huobi and other 1600 exchanges
    #                     if base in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.index:
    #                         print(f"base = {base} is on 1600 exchange")
    #                         tables_which_start_with_base_in_1600_ohlcv_db = [table for table in list_of_tables_in_ohlcv_db_1600 if table.startswith(f'{base}_')]
    #                         for table_which_start_with_base_in_1600_ohlcv_db in tables_which_start_with_base_in_1600_ohlcv_db:
    #                             print("table_which_start_with_base_in_1600_ohlcv_db")
    #                             print(table_which_start_with_base_in_1600_ohlcv_db)
    #                             table_with_1600_ohlcv_data_df_on_other_exchanges = \
    #                                 pd.read_sql_query(
    #                                     f'''select * from "{table_which_start_with_base_in_1600_ohlcv_db}"''',
    #                                     engine_for_ohlcv_data_for_stocks_1600)
    #                             table_with_1600_ohlcv_data_df_on_other_exchanges=table_with_1600_ohlcv_data_df_on_other_exchanges[
    #                                 ["Timestamp", "open", "high", "low", "close", "volume"]]
    #                             print("table_with_1600_ohlcv_data_df_on_other_exchanges")
    #                             print(table_with_1600_ohlcv_data_df_on_other_exchanges)
    #                             closest_timestamp, high_corresponding_to_closest_timestamp, closest_timestamp_plus_one_day, high_plus_one_day=\
    #                                 find_closest_timestamp_high_high_plus_one_day_using_index(table_with_1600_ohlcv_data_df_on_other_exchanges,last_ath_timestamp)
    #                             max_high_on_1600_exchange=max(high_corresponding_to_closest_timestamp,high_plus_one_day)
    #                             print("high_corresponding_to_closest_timestamp")
    #                             print(high_corresponding_to_closest_timestamp)
    #                             print("high_plus_one_day")
    #                             print(high_plus_one_day)
    #
    #                             timestamp_of_possible_ath_on_1600_exchange=np.nan
    #                             if max_high_on_1600_exchange==high_corresponding_to_closest_timestamp:
    #                                 timestamp_of_possible_ath_on_1600_exchange=closest_timestamp
    #                             else:
    #                                 timestamp_of_possible_ath_on_1600_exchange=closest_timestamp_plus_one_day
    #                             print("max_high_on_1600_exchange")
    #                             print(max_high_on_1600_exchange)
    #                             row_number_of_possible_ath_on_1600_exchange=\
    #                                 get_row_number_when_timestamp_is_not_index(table_with_1600_ohlcv_data_df_on_other_exchanges,
    #                                                                        timestamp_of_possible_ath_on_1600_exchange)
    #                             table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange=\
    #                                 table_with_1600_ohlcv_data_df_on_other_exchanges.to_numpy()
    #                             ath_is_not_broken_for_a_long_time_on_1600_exchange_ = check_ath_breakout(
    #                                 table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange,
    #                                 number_of_days_where_ath_was_not_broken,
    #                                 max_high_on_1600_exchange,
    #                                 row_number_of_possible_ath_on_1600_exchange)
    #                             exchange_of_pair_for_1600_exchange = get_exchange_of_trading_pair(
    #                                 trading_pair=table_which_start_with_base_in_1600_ohlcv_db)
    #                             print("exchange_of_pair_for_1600_exchange")
    #                             print(exchange_of_pair_for_1600_exchange)
    #                             string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair_for_1600_exchange
    #                             string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
    #                                 string_of_all_exchanges_where_pair_is_traded)
    #                             if ath_is_not_broken_for_a_long_time_on_1600_exchange_ == False:
    #                                 counter_of_number_of_exchanges_where_level_had_been_broken = \
    #                                     counter_of_number_of_exchanges_where_level_had_been_broken + 1
    #                                 string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair_for_1600_exchange
    #                                 string_of_exchanges_where_level_was_broken = remove_first_underscore(
    #                                     string_of_exchanges_where_level_was_broken)
    #                             else:
    #                                 string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair_for_1600_exchange
    #                                 string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
    #                                     string_of_exchanges_where_level_was_not_broken)
    #
    #         try:
    #             string_of_exchanges_where_level_was_broken = \
    #                 drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
    #                     string_of_exchanges_where_level_was_broken)
    #             string_of_exchanges_where_level_was_not_broken = \
    #                 drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
    #                     string_of_exchanges_where_level_was_not_broken)
    #             string_of_all_exchanges_where_pair_is_traded = \
    #                 drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
    #                     string_of_all_exchanges_where_pair_is_traded)
    #         except:
    #             traceback.print_exc()
    #
    #
    #
    #         levels_formed_by_ath_df.at[counter - 1, "number_of_exchanges_where_level_had_been_broken"] = counter_of_number_of_exchanges_where_level_had_been_broken
    #         levels_formed_by_ath_df.at[
    #             counter - 1, "string_of_exchanges_where_level_was_broken"] = string_of_exchanges_where_level_was_broken
    #         levels_formed_by_ath_df.at[
    #             counter - 1, "string_of_exchanges_where_level_was_not_broken"] = string_of_exchanges_where_level_was_not_broken
    #         levels_formed_by_ath_df.at[
    #             counter - 1, "string_of_all_exchanges_where_pair_is_traded"] = string_of_all_exchanges_where_pair_is_traded
    #
    #
    #         ####################################################################
    #         ###############################################






    levels_formed_by_ath_df.reset_index(inplace = True)
    string_for_output=f"\nСписок инструментов, в которых New All Time High за последние 2 дня:\n" \
                      f"{list_of_assets_with_last_close_close_to_ath}\n"
    # Use the function to create a text file with the text
    # in the subdirectory "current_rebound_breakout_and_false_breakout"
    create_text_file_and_writ_text_to_it(string_for_output, 'current_rebound_breakout_and_false_breakout')



    # levels_formed_by_ath_df.to_sql(table_where_levels_formed_by_ath_will_be,
    #                                engine_for_db_where_levels_formed_by_ath_will_be,
    #                                if_exists = 'replace')
    print ( "levels_formed_by_ath_df" )
    print ( levels_formed_by_ath_df )

if __name__=="__main__":
    start_time = time.time()
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000"
    count_only_round_ath=False
    db_where_levels_formed_by_ath_will_be="levels_formed_by_highs_and_lows_for_cryptos_0000"
    table_where_levels_formed_by_ath_will_be = "current_asset_had_ath_within_two_last_days_period"

    if count_only_round_ath:
        db_where_levels_formed_by_ath_will_be="round_levels_formed_by_highs_and_lows_for_cryptos_0000"
    percentage_between_ath_and_closing_price=10
    check_if_asset_is_approaching_its_ath(percentage_between_ath_and_closing_price,
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              count_only_round_ath,
                                              db_where_levels_formed_by_ath_will_be,
                                              table_where_levels_formed_by_ath_will_be)

    end_time = time.time()
    overall_time = end_time - start_time
    print('overall time in minutes=', overall_time / 60.0)
    print('overall time in hours=', overall_time / 3600.0)
    print('overall time=', str(datetime.timedelta(seconds=overall_time)))
    print('start_time=', start_time)
    print('end_time=', end_time)