# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
from sqlalchemy import inspect
import asyncio
import os
import sys
import time
import traceback
# import db_config
from sqlalchemy import text
import sqlalchemy
import psycopg2
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# import talib
import datetime
import datetime as dt
import ccxt
# import ccxt.async_support as ccxt  # noqa: E402

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from pytz import timezone
from verify_that_asset_has_enough_volume import check_volume
from get_info_from_load_markets import get_limit_of_daily_candles_original_limits
import asyncio

from sqlalchemy import create_engine, MetaData, Table, Column
import asyncpg
from get_info_from_load_markets import async_fetch_entire_ohlcv_without_exchange_name
from get_info_from_load_markets import async_fetch_entire_ohlcv_without_exchange_name_with_load_markets
from get_info_from_load_markets import get_exchange_object3
from get_info_from_load_markets import async_get_exchange_object3
async def get_async_connection_to_db_without_deleting_it_first(database_name):
    import db_config
    dialect = db_config.dialect
    # driver = db_config.driver
    driver = db_config.async_driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port
    conn = await asyncpg.connect(user=user, password=password,
                                 database=database_name,
                                 host=host)
    return conn


async def async_get_list_of_tables_from_db(database_name):
    conn = await get_async_connection_to_db_without_deleting_it_first(database_name)
    async_record_object_tables_list = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    table_names_list = [async_record_object_table['table_name'] for async_record_object_table in async_record_object_tables_list]
    print("table_names_list")
    print(table_names_list)
    await conn.close()
    return table_names_list
async def get_tickers_from_all_tables(database_name,table_names_list):

    conn = await get_async_connection_to_db_without_deleting_it_first(database_name)

    tickers = []
    # tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")

    for table_name in table_names_list:
        columns = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name=$1", table_name)
        columns_strings=[async_record_object_column['column_name'] for async_record_object_column in columns]

        if 'ticker' in columns_strings:

            ticker_values = await conn.fetch(f'''SELECT ticker FROM {table_name}''')
            tickers.extend([ticker['ticker'] for ticker in ticker_values])


    await conn.close()
    return list(set(tickers))
def drop_none_from_list(my_list):
    new_list = list(filter(lambda x: x is not None, my_list))
    return new_list
async def get_todays_exchanges_from_all_tables(database_name,table_names_list):

    conn = await get_async_connection_to_db_without_deleting_it_first(database_name)

    exchange_id_strings = []
    # tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")

    for table_name in table_names_list:
        columns = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name=$1", table_name)
        columns_strings=[async_record_object_column['column_name'] for async_record_object_column in columns]

        if 'exchange_id_string_where_trading_pair_is_traded' in columns_strings:

            exchange_id_string_values = await conn.fetch(f'''SELECT exchange_id_string_where_trading_pair_is_traded FROM {table_name}''')
            exchange_id_strings.extend([exchange_id_string['exchange_id_string_where_trading_pair_is_traded'] for exchange_id_string in exchange_id_string_values])

    print("exchange_id_strings1234")
    print(exchange_id_strings)
    exchange_id_strings=drop_none_from_list(exchange_id_strings)

    one_big_string_of_exchanges="_".join(exchange_id_strings)
    print("one_big_string_of_exchanges")
    print(one_big_string_of_exchanges)
    list_of_todays_exchanges=one_big_string_of_exchanges.split("_")
    list_of_todays_exchanges=list(set(list_of_todays_exchanges))
    print("list_of_todays_exchanges")
    print(list_of_todays_exchanges)




    await conn.close()
    return list_of_todays_exchanges

async def async_get_list_of_exchange_objects_based_on_list_of_exchange_ids(list_of_exchange_ids):
    tasks=[]
    for exchange_id in list_of_exchange_ids:
        task=asyncio.create_task(async_get_exchange_object3(exchange_name=exchange_id))
        tasks.append(task)
    exchange_id_list=await asyncio.gather(*tasks)
    return exchange_id_list




async def async_fetch_all_tickers_from_all_exchanges_where_they_are_traded(tickers):
    tasks=[]
    counter=0
    for ticker_with_exchange in tickers:
        counter=counter+1
        ticker_without_exchange=ticker_with_exchange.split("_on_")[0]
        exchange_id = ticker_with_exchange.split("_on_")[1]
        ticker_without_exchange=ticker_without_exchange.replace("_","/")

        timeframe="1d"
        limit_of_daily_candles=1000

        exchange_object=await async_get_exchange_object3(exchange_name=exchange_id)
        try:
            # await exchange_object.load_markets()

            print(f"ticker_with_exchange = {ticker_with_exchange} is {counter} out of {len(tickers)}")
            print(ticker_with_exchange)
            # asyncio.get_running_loop().set_debug(True)
            task=asyncio.create_task(async_fetch_entire_ohlcv_without_exchange_name_with_load_markets(exchange_object,
                                                                                                      ticker_without_exchange,
                                                                                                      timeframe,
                                                                                                      limit_of_daily_candles))
            tasks.append(task)

            # ohlcv_table=await async_fetch_entire_ohlcv_without_exchange_name(exchange_object,ticker_without_exchange, timeframe,limit_of_daily_candles)
            # print("ohlcv_table")
            # print(ohlcv_table)
        finally:
            await exchange_object.close()
    result=await asyncio.gather(*tasks)
    print("result1")
    print(result)
def get_list_of_exchanges_from_list_of_tickers_plus_exchange(tickers):
    list_of_exchanges=[]
    for ticker_with_exchange in tickers:

        ticker_without_exchange = ticker_with_exchange.split("_on_")[0]
        exchange_id = ticker_with_exchange.split("_on_")[1]
        ticker_without_exchange = ticker_without_exchange.replace("_", "/")
        list_of_exchanges.append(exchange_id)
    list_of_exchanges=list(set(list_of_exchanges))
    return list_of_exchanges

def get_list_of_todays_trading_pairs(database_name):
    list_of_tickers_without_exchange=[]
    table_names_list = asyncio.run(async_get_list_of_tables_from_db(database_name))
    tickers = asyncio.run(get_tickers_from_all_tables(database_name, table_names_list))
    for ticker_with_exchange in tickers:
        ticker_without_exchange = ticker_with_exchange.split("_on_")[0]
        ticker_without_exchange=ticker_without_exchange.replace("_","/")
        list_of_tickers_without_exchange.append(ticker_without_exchange)
        if ":" in ticker_without_exchange:
            ticker_without_exchange_and_without_colon=ticker_without_exchange.split(":")[0]
            list_of_tickers_without_exchange.append(ticker_without_exchange_and_without_colon)

    list_of_tickers_without_exchange = list(set(list_of_tickers_without_exchange))
    # results=asyncio.run(async_fetch_all_tickers_from_all_exchanges_where_they_are_traded(tickers))

    return list_of_tickers_without_exchange



def get_list_of_exchange_ids_for_todays_pairs(database_name):

    table_names_list = asyncio.run(async_get_list_of_tables_from_db(database_name))
    print("table_names_list")
    print(table_names_list)
    tickers = asyncio.run(get_tickers_from_all_tables(database_name, table_names_list))
    print("tickers3")
    print(tickers)
    list_of_exchanges_for_todays_pairs=get_list_of_exchanges_from_list_of_tickers_plus_exchange(tickers)
    print("list_of_exchanges_for_todays_pairs3")
    print(list_of_exchanges_for_todays_pairs)
    list_of_todays_exchanges=  asyncio.run(get_todays_exchanges_from_all_tables(database_name, table_names_list))
    print("list_of_todays_exchanges3")
    print(list_of_todays_exchanges)
    # results=asyncio.run(async_fetch_all_tickers_from_all_exchanges_where_they_are_traded(tickers))


    print("list_of_todays_exchanges123")
    print(list_of_todays_exchanges)

    return list_of_todays_exchanges

def get_ohlcv_of_todays_pairs_asyncronously(database_name):

    table_names_list = asyncio.run(async_get_list_of_tables_from_db(database_name))
    tickers = asyncio.run(get_tickers_from_all_tables(database_name, table_names_list))
    list_of_exchanges_for_todays_pairs=get_list_of_exchanges_from_list_of_tickers_plus_exchange(tickers)
    results=asyncio.run(async_fetch_all_tickers_from_all_exchanges_where_they_are_traded(tickers))


    print(results)

    return results


if __name__=="__main__":
    database_name = 'levels_formed_by_highs_and_lows_for_cryptos_0000'
    list_of_exchanges_for_todays_pairs=get_list_of_exchange_ids_for_todays_pairs(database_name)


