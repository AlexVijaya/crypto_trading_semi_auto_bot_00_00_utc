from constant_update_of_ohlcv_db_to_plot_later import get_async_connection_to_db_without_deleting_it_first
from constant_update_of_ohlcv_db_to_plot_later import async_get_list_of_tables_from_db
import asyncio
import asyncpg
import db_config

# async def async_get_ticker_list_from_one_table(conn,table_name):
#     # async_record_object_ticker_list = await conn.fetch(f'''SELECT ticker FROM public."{table_name}"''')
#     ticker_list = [async_record_object_table['ticker'] for async_record_object_table in async_record_object_ticker_list]
#     return ticker_list
# async def async_get_dict_with_exchange_as_key_and_trading_pairs_as_values(database_name,list_of_acceptable_tables_for_search_if_model_is_met):
#     conn = await get_async_connection_to_db_without_deleting_it_first(database_name)
#     list_of_all_tables_in_db_with_models = await async_get_list_of_tables_from_db(database_name_with_models)
#     list_with_common_tables_of_models = \
#         find_common_elements(list_of_acceptable_tables_for_search_if_model_is_met, list_of_all_tables_in_db_with_models)
#     ticker_list=[]
#     tasks=[]
#     for table_name in list_with_common_tables_of_models:
#         task=asyncio.create_task (async_get_ticker_list_from_one_table(conn,table_name))
#         tasks.append(task)
#
#     ticker_list=await asyncio.gather(*tasks)
#     print("ticker_list1")
#     print(ticker_list)
#     await conn.close()
#     return ticker_list

def find_common_elements(list1, list2):
    """
    Function that takes two lists and returns a list of all elements found in both lists.

    Args:
        list1 (list): list to search through
        list2 (list): list to search against

    Returns:
        elements (list): list of elements found in both lists
    """

    return [element for element in list1 if element in list2]
# def verify_that_all_models_have_been_formed_at_next_print_time(database_name_with_models,
#                                                                list_of_acceptable_tables_for_search_if_model_is_met):
#     # list_of_all_tables_in_db_with_models= asyncio.run(async_get_list_of_tables_from_db(database_name_with_models))
#     # list_with_common_tables_of_models=\
#     #     find_common_elements(list_of_acceptable_tables_for_search_if_model_is_met, list_of_all_tables_in_db_with_models)
#     ticker_list = asyncio.run(async_get_dict_with_exchange_as_key_and_trading_pairs_as_values(database_name_with_models,
#                                                                                               list_of_acceptable_tables_for_search_if_model_is_met))
#
#     print("ticker_list")
#     print(ticker_list)


async def get_tickers_from_tables(pool, tables):
    tickers = []
    async with pool.acquire() as conn:
        for table in tables:
            query = f'''SELECT ticker FROM {table}'''
            result = await conn.fetch(query)
            tickers.extend([row['ticker'] for row in result])
    return tickers

async def return_list_of_tickers_in_db_in_all_tables(database_name_with_models,list_of_acceptable_tables_for_search_if_model_is_met):
    import db_config
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database


    list_of_all_tables_in_db_with_models=await async_get_list_of_tables_from_db(database_name_with_models)


    list_with_common_tables_of_models = \
                find_common_elements(list_of_acceptable_tables_for_search_if_model_is_met, list_of_all_tables_in_db_with_models)

    pool = await asyncpg.create_pool(database=database_name_with_models, user=user, password=password, host=host)

    tickers = await get_tickers_from_tables(pool, list_with_common_tables_of_models)
    print(tickers)
    return tickers
def create_exchange_dict(trading_pairs):
    exchange_dict = {}
    for pair in trading_pairs:
        trading_pair,exchange  = pair.split("_on_")
        trading_pair = trading_pair.replace("_", "/")  # replace colon with slash in trading pair
        if exchange not in exchange_dict:
            exchange_dict[exchange] = []
        exchange_dict[exchange].append(trading_pair)
    return exchange_dict
def get_dict_keys(my_dict):
    """
    Returns a list of all the keys in a dictionary.
    """
    return list(my_dict.keys())
def get_dict_values(my_dict):
    """
    Returns a list of all the unique values in a dictionary.
    """
    # Create an empty list to store the values
    values_list = []

    # Iterate over each key-value pair in the dictionary
    for key, value in my_dict.items():
        # Extend the values list with the current value
        values_list.extend(value)

    # Remove duplicates from the values list
    unique_values = list(set(values_list))

    return unique_values

def get_todays_exchanges_and_pairs_list():
    database_name_with_models = 'levels_formed_by_highs_and_lows_for_cryptos_0000'
    list_of_acceptable_tables_for_search_if_model_is_met = [
        'current_breakout_situations_of_ath_position_entry_next_day',
        'current_breakout_situations_of_atl_position_entry_next_day',
        'current_breakout_situations_of_ath_position_entry_on_day_two',
        'current_breakout_situations_of_atl_position_entry_on_day_two',
        'current_false_breakout_of_atl_by_one_bar',
        'current_false_breakout_of_ath_by_one_bar',
        'current_false_breakout_of_atl_by_two_bars',
        'current_false_breakout_of_ath_by_two_bars',
        'current_rebound_situations_from_atl',
        'current_rebound_situations_from_ath',
        'complex_false_breakout_of_atl',
        'complex_false_breakout_of_ath'
    ]
    tickers = \
        asyncio.run(return_list_of_tickers_in_db_in_all_tables(
            database_name_with_models, list_of_acceptable_tables_for_search_if_model_is_met))
    exchange_dict = create_exchange_dict(tickers)
    print(exchange_dict)
    list_of_exchanges_where_update_should_be_done = get_dict_keys(exchange_dict)
    # print("list_of_exchanges_where_update_should_be_done")
    # print(list_of_exchanges_where_update_should_be_done)

    list_of_unique_trading_pairs = get_dict_values(exchange_dict)
    # print("list_of_unique_trading_pairs")
    # print(list_of_unique_trading_pairs)
    return list_of_exchanges_where_update_should_be_done,list_of_unique_trading_pairs,exchange_dict

if __name__=="__main__":
    list_of_exchanges_where_update_should_be_done,list_of_unique_trading_pairs,exchange_dict=get_todays_exchanges_and_pairs_list()
    print("list_of_exchanges_where_update_should_be_done")
    print(list_of_exchanges_where_update_should_be_done)
    print("list_of_unique_trading_pairs")
    print(list_of_unique_trading_pairs)