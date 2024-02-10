# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
import asyncio
import os
import sys
import time
import traceback
# import db_config
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
# from fetch_historical_USDT_pairs_for_1D_delete_first_primary_db_and_delete_low_volume_db import remove_values_from_list
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_list_of_tables_in_db
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import drop_table
def is_length_multiple_of_100(df):
    length = len(df)
    return length % 100 == 0
def drop_all_ohlcv_tables(database_name_for_low_volume_pairs,database_name,exchange_name_to_drop):

    engine_for_ohlcv_database_with_enough_volume , connection_to_ohlcv_for_usdt_pairs =\
        connect_to_postgres_db_without_deleting_it_first (database_name)

    engine_for_ohlcv_database_without_enough_volume, connection_to_ohlcv_for_usdt_pairs_without_enough_volume = \
        connect_to_postgres_db_without_deleting_it_first(database_name_for_low_volume_pairs)

    list_of_tables_in_db_with_enough_volume=get_list_of_tables_in_db(engine_for_ohlcv_database_with_enough_volume)
    list_of_tables_in_db_with_low_volume=get_list_of_tables_in_db(engine_for_ohlcv_database_without_enough_volume)

    counter_for_enough_volume_tables_the_length_of_which_is_a_multiple_of_100=0
    counter_for_low_volume_tables_the_length_of_which_is_a_multiple_of=0
    #drop table in the database with enough volume if its name ends with a specific exchange name
    for number_of_iterations,table_name_with_enough_volume in enumerate(list_of_tables_in_db_with_enough_volume):
        print(f"{number_of_iterations}/{len(list_of_tables_in_db_with_enough_volume)} tables in enough volume db have been processed")
        table_with_ohlcv_data_df_with_enough_volume = \
            pd.read_sql_query(f'''select * from "{table_name_with_enough_volume}"''',
                              engine_for_ohlcv_database_with_enough_volume)

        # if the df is empty do not continue the current loop
        if table_with_ohlcv_data_df_with_enough_volume.empty:
            continue

        if is_length_multiple_of_100(table_with_ohlcv_data_df_with_enough_volume):
            print(f"{table_name_with_enough_volume} has the length of {len(table_with_ohlcv_data_df_with_enough_volume)}."
                  f" It is a multiple of 100")
            counter_for_enough_volume_tables_the_length_of_which_is_a_multiple_of_100=\
                counter_for_enough_volume_tables_the_length_of_which_is_a_multiple_of_100+1
        # drop_table(table_name_with_enough_volume,engine_for_ohlcv_database_with_enough_volume)
        # print("table= " + table_name_with_enough_volume + " dropped")

    # drop table in the database without enough volume if its name ends with a specific exchange name
    for number_of_iterations,table_name_with_low_volume in enumerate(list_of_tables_in_db_with_low_volume):
        print(f"{number_of_iterations}/{len(list_of_tables_in_db_with_low_volume)} tables in low volume db have been processed")
        table_with_ohlcv_data_df_low_volume = \
            pd.read_sql_query(f'''select * from "{table_name_with_low_volume}"''',
                              engine_for_ohlcv_database_without_enough_volume)

        # if the df is empty do not continue the current loop
        if table_with_ohlcv_data_df_low_volume.empty:
            continue

        if is_length_multiple_of_100(table_with_ohlcv_data_df_low_volume):
            print(f"{table_name_with_low_volume} has the length of {len(table_with_ohlcv_data_df_low_volume)}."
                  f" It is a multiple of 100")
            counter_for_low_volume_tables_the_length_of_which_is_a_multiple_of=\
                counter_for_low_volume_tables_the_length_of_which_is_a_multiple_of+1
        # drop_table(table_name_with_low_volume, engine_for_ohlcv_database_without_enough_volume)
        # print("table= " + table_name_with_low_volume + " dropped")
    print("final counter_for_enough_volume_tables_the_length_of_which_is_a_multiple_of_100")
    print(counter_for_enough_volume_tables_the_length_of_which_is_a_multiple_of_100)
    print("final counter_for_low_volume_tables_the_length_of_which_is_a_multiple_of_100")
    print(counter_for_low_volume_tables_the_length_of_which_is_a_multiple_of)
if __name__=="__main__":
    start_time=time.time ()
    database_name="ohlcv_1d_data_for_usdt_pairs_0000_pagination"
    database_name_for_low_volume_pairs = "ohlcv_1d_data_for_low_volume_usdt_pairs_0000_pagination"
    exchange_name_to_drop="whitebit"
    
    drop_all_ohlcv_tables(database_name_for_low_volume_pairs,database_name,exchange_name_to_drop)
    end_time = time.time()
    overall_time = end_time - start_time
    print('overall time in minutes=', overall_time / 60.0)
    print('overall time in hours=', overall_time / 3600.0)
    print('overall time=', str(datetime.timedelta(seconds=overall_time)))
    print('start_time=', start_time)
    print('end_time=', end_time)


