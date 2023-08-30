import pprint

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
def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db
def delete_ohlcv_tables_from_db_of_non_active_pairs(db_with_trading_pair_statistics,db_where_ohlcv_data_for_stocks_is_stored):
    list_of_non_active_trading_pairs=[]
    list_of_tables_to_be_deleted=[]

    table_with_strings_where_each_pair_is_traded = "exchanges_where_each_pair_is_traded"
    engine_for_db_with_trading_pair_statistics, connection_to_db_with_trading_pair_statistics = \
        connect_to_postgres_db_without_deleting_it_first(db_with_trading_pair_statistics)

    df_with_strings_where_each_pair_is_traded = \
        pd.read_sql_query(f'''select * from "{table_with_strings_where_each_pair_is_traded}"''',
                          engine_for_db_with_trading_pair_statistics)

    list_of_all_pairs_from_all_exchanges=list(df_with_strings_where_each_pair_is_traded["trading_pair"])

    print("list_of_all_pairs_from_all_exchanges")
    print(list_of_all_pairs_from_all_exchanges)

    engine_for_ohlcv_data_for_stocks, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored)

    list_of_tables_in_ohlcv_db = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks)

    list_of_tables_in_ohlcv_db_with_underscore_and_without_exchange=\
        [table_in_ohlcv_db.split("_on_")[0] for table_in_ohlcv_db in list_of_tables_in_ohlcv_db]
    list_of_tables_in_ohlcv_db_with_slash_and_without_exchange=\
        [trading_pair_with_underscore.replace("_","/") for trading_pair_with_underscore in list_of_tables_in_ohlcv_db_with_underscore_and_without_exchange]
    print("list_of_tables_in_ohlcv_db_with_slash_and_without_exchange")
    print(list_of_tables_in_ohlcv_db_with_slash_and_without_exchange)

    for table_name_with_slash_and_without_exchange in list_of_tables_in_ohlcv_db_with_slash_and_without_exchange:
        if table_name_with_slash_and_without_exchange not in list_of_all_pairs_from_all_exchanges:
            list_of_non_active_trading_pairs.append(table_name_with_slash_and_without_exchange)

    print("list_of_non_active_trading_pairs")
    print(list_of_non_active_trading_pairs)

    for non_active_trading_pair_table_name in list_of_non_active_trading_pairs:
        non_active_trading_pair_table_name=non_active_trading_pair_table_name.replace("/","_")
        for table_name in list_of_tables_in_ohlcv_db:
            if table_name.startswith(non_active_trading_pair_table_name):
                list_of_tables_to_be_deleted.append(table_name)

                drop_table(table_name,
                           engine_for_ohlcv_data_for_stocks)

    print("list_of_tables_to_be_deleted")
    print(list_of_tables_to_be_deleted)



if __name__=="__main__":
    db_with_trading_pair_statistics = "db_with_trading_pair_statistics"
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000"
    delete_ohlcv_tables_from_db_of_non_active_pairs(db_with_trading_pair_statistics,
                                                    db_where_ohlcv_data_for_stocks_is_stored)