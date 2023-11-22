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
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import get_list_of_tables_in_db
from sqlalchemy import text
def get_volume_low_value(dataframe, timestamp):
    volume_low_value = dataframe.loc[dataframe["Timestamp"] == timestamp, "volume*low"].values
    if len(volume_low_value) > 0:
        return volume_low_value[0]
    else:
        return None

def remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(list_of_pairs,starts_with_this_trading_pair):
    filtered_strings = [s for s in list_of_pairs if s.startswith(f"{starts_with_this_trading_pair}")]
    return filtered_strings
def add_min_volume_in_usd_over_n_days_to_column_in_bfr_tables():
    database_with_ohlcv_with_low_volume="ohlcv_1d_data_for_low_volume_usdt_pairs_0000_pagination"
    engine_for_ohlcv_data_for_stocks_low_volume, \
        connection_to_ohlcv_data_for_stocks_low_volume = \
        connect_to_postgres_db_without_deleting_it_first(database_with_ohlcv_with_low_volume)

    database_with_ohlcv_with_normal_volume="ohlcv_1d_data_for_usdt_pairs_0000_pagination"
    engine_for_ohlcv_data_for_stocks_normal_volume, \
        connection_to_ohlcv_data_for_stocks_normal_volume = \
        connect_to_postgres_db_without_deleting_it_first(database_with_ohlcv_with_normal_volume)

    database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = "levels_formed_by_highs_and_lows_for_cryptos_0000_hist"
    engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist, \
        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
        connect_to_postgres_db_without_deleting_it_first(database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

    list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_low_volume)

    list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_normal_volume)

    list_of_tables_in_database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
        get_list_of_tables_in_db(engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

    # cursor_for_connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.cursor()

    list_of_columns_to_add=["suppression_by_lows"]


    for table_name_in_bfr_database in list_of_tables_in_database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist:

        print("table_name_in_bfr_database")
        print(table_name_in_bfr_database)
        table_name_in_bfr_database_df = \
            pd.read_sql_query(f'''select * from "{table_name_in_bfr_database}"''',
                              engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

        print("table_name_in_bfr_database_df")
        print(table_name_in_bfr_database_df)

        list_of_columns_in_sql_table=table_name_in_bfr_database_df.columns
        for column_name_to_add in list_of_columns_to_add:

            # if column_name_to_add not in list_of_columns_in_sql_table:
            #     # add additional column of type TEXT
            #     sql = f"ALTER TABLE {table_name_in_bfr_database} ADD COLUMN {column_name_to_add} BOOL"
            #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(sql)

            # if column_name_to_add in list_of_columns_in_sql_table:
            #     # change type of column to double precision
            #     sql = f"ALTER TABLE {table_name_in_bfr_database} ALTER COLUMN {column_name_to_add} TYPE " \
            #           f"DOUBLE PRECISION USING {column_name_to_add}::DOUBLE PRECISION;"
            #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(sql)

            if column_name_to_add in list_of_columns_in_sql_table:
                # add 86400 to timestamp column
                sql = f'''UPDATE {table_name_in_bfr_database} SET suppression_by_highs_or_lows = {column_name_to_add};'''
                connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(sql)


    connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.close()



if __name__=="__main__":
    add_min_volume_in_usd_over_n_days_to_column_in_bfr_tables()