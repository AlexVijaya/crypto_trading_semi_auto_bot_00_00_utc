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




    engine_for_ohlcv_data_for_stocks, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored)

    list_of_tables_in_ohlcv_db = get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks)

    print("list_of_tables_in_ohlcv_db")
    print(list_of_tables_in_ohlcv_db)

    for table_name_in_ohlcv_db in list_of_tables_in_ohlcv_db:
        try:
            base_underscore_quote_without_exchange=table_name_in_ohlcv_db.split("_on_")[0]
            exchange_of_ohlcv_table = table_name_in_ohlcv_db.split("_on_")[1]
            base_slash_quote_without_exchange=base_underscore_quote_without_exchange.replace("_","/")

            # row_where_trading_pair_is_equal_to_ohlcv_trading_pair=\
            #     df_with_strings_where_each_pair_is_traded.loc[df_with_strings_where_each_pair_is_traded["trading_pair"]==base_slash_quote_without_exchange,:]

            exchanges_where_pair_is_traded = \
                df_with_strings_where_each_pair_is_traded.loc[
                df_with_strings_where_each_pair_is_traded["trading_pair"] == base_slash_quote_without_exchange, "exchanges_where_pair_is_traded"]

            print("exchanges_where_pair_is_traded")
            print(exchanges_where_pair_is_traded)
            string_with_exchanges_where_pair_is_traded=exchanges_where_pair_is_traded.values[0]
            print("string_with_exchanges_where_pair_is_traded")
            print(string_with_exchanges_where_pair_is_traded)
            list_of_exchanges_where_pair_is_traded=string_with_exchanges_where_pair_is_traded.split("_")
            print(f"list_of_exchanges_where_{table_name_in_ohlcv_db}_is_traded")
            print(list_of_exchanges_where_pair_is_traded)
            if exchange_of_ohlcv_table not in list_of_exchanges_where_pair_is_traded:
                list_of_tables_to_be_deleted.append(table_name_in_ohlcv_db)
                drop_table(table_name_in_ohlcv_db,
                           engine_for_ohlcv_data_for_stocks)

            print("list_of_tables_to_be_deleted")
            print(list_of_tables_to_be_deleted)
        except:
            traceback.print_exc()

    # drop_table(table_name,
    #            engine_for_ohlcv_data_for_stocks)

    # print("list_of_tables_to_be_deleted")
    # print(list_of_tables_to_be_deleted)



if __name__=="__main__":
    db_with_trading_pair_statistics = "db_with_trading_pair_statistics"
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_1d_data_for_usdt_pairs_0000"
    delete_ohlcv_tables_from_db_of_non_active_pairs(db_with_trading_pair_statistics,
                                                    db_where_ohlcv_data_for_stocks_is_stored)