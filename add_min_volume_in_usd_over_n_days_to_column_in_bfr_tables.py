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


    for table_name_in_bfr_database in list_of_tables_in_database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist:
        print("table_name_in_bfr_database")
        print(table_name_in_bfr_database)
        table_name_in_bfr_database_df = \
            pd.read_sql_query(f'''select * from "{table_name_in_bfr_database}"''',
                              engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

        print("table_name_in_bfr_database_df")
        print(table_name_in_bfr_database_df)
        if "timestamp_of_false_breakout_bar" in table_name_in_bfr_database_df.columns:

            for index, row in table_name_in_bfr_database_df.iterrows():
                print(f"index={index} out of {len(table_name_in_bfr_database_df)}")

                ticker = row["ticker"]
                timestamp_of_false_breakout_bar = row["timestamp_of_false_breakout_bar"]
                timestamp_of_false_breakout_bar=int(timestamp_of_false_breakout_bar)
                print(f"Ticker: {ticker}, Timestamp: {timestamp_of_false_breakout_bar}")

                if ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume:
                    ohlcv_df_normal_volume = \
                        pd.read_sql_query(f'''select * from "{ticker}"''',
                                          engine_for_ohlcv_data_for_stocks_normal_volume)


                    volume_by_low_value=get_volume_low_value(ohlcv_df_normal_volume, timestamp_of_false_breakout_bar)
                    print("volume_by_low_value")
                    print(volume_by_low_value)

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET min_volume_in_usd_over_last_n_days = {volume_by_low_value} WHERE "ticker" = '{ticker}' AND timestamp_of_false_breakout_bar = {timestamp_of_false_breakout_bar}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()
                    # connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.commit()



                elif ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                    ohlcv_df_low_volume = \
                        pd.read_sql_query(f'''select * from "{ticker}"''',
                                          engine_for_ohlcv_data_for_stocks_low_volume)
                    volume_by_low_value = get_volume_low_value(ohlcv_df_low_volume, timestamp_of_false_breakout_bar)
                    print("volume_by_low_value")
                    print(volume_by_low_value)

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET min_volume_in_usd_over_last_n_days = {volume_by_low_value} WHERE "ticker" = '{ticker}' AND timestamp_of_false_breakout_bar = {timestamp_of_false_breakout_bar}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()


                elif  ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume and \
                    ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                    print(f"{ticker} is both in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                          f"and list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
                else:
                    print(f"{ticker} is neither in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                          f"nor list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")

        elif "timestamp_of_breakout_bar" in table_name_in_bfr_database_df.columns:
            for index, row in table_name_in_bfr_database_df.iterrows():
                ticker = row["ticker"]
                timestamp_of_breakout_bar = row["timestamp_of_breakout_bar"]
                timestamp_of_breakout_bar=int(timestamp_of_breakout_bar)
                print(f"Ticker: {ticker}, Timestamp: {timestamp_of_breakout_bar}")

                if ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume:
                    ohlcv_df_normal_volume = \
                        pd.read_sql_query(f'''select * from "{ticker}"''',
                                          engine_for_ohlcv_data_for_stocks_normal_volume)
                    volume_by_low_value = get_volume_low_value(ohlcv_df_normal_volume, timestamp_of_breakout_bar)
                    print("volume_by_low_value")
                    print(volume_by_low_value)

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET min_volume_in_usd_over_last_n_days = {volume_by_low_value} WHERE "ticker" = '{ticker}' AND timestamp_of_breakout_bar = {timestamp_of_breakout_bar}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                elif ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                    ohlcv_df_low_volume = \
                        pd.read_sql_query(f'''select * from "{ticker}"''',
                                          engine_for_ohlcv_data_for_stocks_low_volume)
                    volume_by_low_value = get_volume_low_value(ohlcv_df_low_volume, timestamp_of_breakout_bar)
                    print("volume_by_low_value")
                    print(volume_by_low_value)

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET min_volume_in_usd_over_last_n_days = {volume_by_low_value} WHERE "ticker" = '{ticker}' AND timestamp_of_breakout_bar = {timestamp_of_breakout_bar}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()


                elif ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume and \
                        ticker in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                    print(f"{ticker} is both in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                          f"and list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
                else:
                    print(f"{ticker} is neither in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                          f"nor list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
        else:
            continue
    connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.close()



if __name__=="__main__":
    add_min_volume_in_usd_over_n_days_to_column_in_bfr_tables()