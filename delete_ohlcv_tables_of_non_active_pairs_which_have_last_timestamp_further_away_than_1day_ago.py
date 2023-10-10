import pprint
from fetch_historical_USDT_pairs_for_1D import connect_to_postgres_db_with_deleting_it_first
from insert_into_df_traded_trading_pairs_for_each_exchange_exchange_as_column_name import connect_to_postgres_db_without_deleting_it_first
import ccxt
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import time
import traceback
import re
import numpy as np
from not_in_hindsight_search_for_tickers_with_ath_equal_to_limit_level import drop_table
import db_config
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from sqlalchemy import text
from insert_into_df_trading_pair_with_string_of_exchanges_where_it_is_traded import connect_to_postgres_db_without_deleting_it_first
from sqlalchemy import inspect
from fetch_historical_USDT_pairs_for_1D import convert_string_timeframe_into_seconds
def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db
def delete_ohlcv_tables_from_db_of_non_active_pairs(db_where_ohlcv_data_for_stocks_is_stored):
    not_active_pair_counter=0
    list_of_inactive_pairs=[]

    engine_for_ohlcv_data_for_stocks, connection_to_ohlcv_for_usdt_pairs = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored)

    list_of_tables = get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks)
    print("list_of_tables")
    print(list_of_tables)



    for table_with_strings_where_each_pair_is_traded in list_of_tables:

        data_df = pd.read_sql_query(f'''select * from "{table_with_strings_where_each_pair_is_traded}"''',
                                    engine_for_ohlcv_data_for_stocks)




        trading_pair=table_with_strings_where_each_pair_is_traded.split("_on_")[0]
        exchange=table_with_strings_where_each_pair_is_traded.split("_on_")[1]

        if data_df.empty:

            drop_table(f"{trading_pair}_on_{exchange}",
                       engine_for_ohlcv_data_for_stocks)
            print(f"{trading_pair}_on_{exchange} is empty")
            continue

        # list_of_inactive_pairs=[]
        current_timestamp = time.time()
        current_timestamp= current_timestamp
        last_timestamp_in_df = data_df["Timestamp"].iat[-1]
        print("current_timestamp=", current_timestamp)
        # print("data_df.tail(1).index.item()=", data_df.tail(1).index.item() / 1000.0)
        # check if the pair is active
        timeframe = '1d'
        timeframe_in_seconds = convert_string_timeframe_into_seconds(timeframe)
        print("timeframe_in_seconds")
        print(timeframe_in_seconds)
        print("last_timestamp_in_df")
        print(last_timestamp_in_df)
        print(f"abs(current_timestamp - last_timestamp_in_df) for {trading_pair}")
        print(abs(current_timestamp - last_timestamp_in_df))
        if abs(current_timestamp - last_timestamp_in_df) > (timeframe_in_seconds)*2:
            print(f"not quite active trading pair {trading_pair} on {exchange}")
            not_active_pair_counter = not_active_pair_counter + 1
            print("not_active_pair_counter=", not_active_pair_counter)
            list_of_inactive_pairs.append(f"{trading_pair}_on_{exchange}")
            drop_table(f"{trading_pair}_on_{exchange}",
                       engine_for_ohlcv_data_for_stocks)

        # if table_with_strings_where_each_pair_is_traded=="BEAM_USDT_on_binance":
        #     time.sleep(500000)

    print("list_of_inactive_pairs")
    print(list_of_inactive_pairs)



if __name__=="__main__":
    # db_with_trading_pair_statistics = "db_with_trading_pair_statistics"
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000"
    delete_ohlcv_tables_from_db_of_non_active_pairs(db_where_ohlcv_data_for_stocks_is_stored)