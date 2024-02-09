from statistics import mean
import pandas as pd
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import os
import time
import datetime
import traceback
from sqlalchemy_utils import create_database, database_exists
import db_config
from sqlalchemy import inspect
from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import get_list_of_tables_in_db
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def merge_dataframes(dataframes_list):
    """
    Merges multiple dataframes into a single dataframe and
    reindexes the resulting dataframe.
    """
    # Merge the dataframes using pd.concat
    df = pd.concat(dataframes_list)

    print("df1")
    print(df)

    # # Reindex the merged dataframe
    # df_copy = df.reindex()
    df.index=list(range(0,len(df)))
    df["index"]=list(range(0,len(df)))
    # df.set_index(list(range(0,len(df))))
    print("df_copy")
    print(df)

    return df
def get_common_elements(list1, list2):
    """
    Returns a list of elements that are present in both list1 and list2.
    """
    # Convert both input lists into sets
    set1 = set(list1)
    set2 = set(list2)

    # Compute and return the intersection of the two sets
    return list(set1.intersection(set2))
def remove_rows_by_column(df, column_name, column_value):
    """
    Removes all rows from a dataframe in which the value
    of a particular column is equal to a specific value.
    """
    # Create a query string
    query_str = f'{column_name} == "{column_value}"'

    # Query the dataframe and return the result
    return df.query(query_str)

def remove_rows_by_column2(df, column_name, column_value):
    """
    Removes all rows from a dataframe in which the value
    of a particular column is equal to a specific value.
    """
    # Create a condition
    condition = (df[column_name] == column_value)

    # Filter the dataframe based on the condition
    return df.loc[~condition]
def build_entire_df_of_assets_which_will_be_used_for_position_entry(database_name):
    engine_for_db_with_bfr,connection_to_db_with_bfr\
        =connect_to_postgres_db_without_deleting_it_first(database_name)
    list_of_table_names_with_bfr=get_list_of_tables_in_db(engine_for_db_with_bfr)
    # print("list_of_table_names_with_bfr")
    # print(list_of_table_names_with_bfr)
    list_of_tables_which_are_acceptable_to_be_looked_at_for_joining=[
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

    list_of_tables_which_will_be_looked_at_for_joining=\
        get_common_elements(list_of_table_names_with_bfr,
                            list_of_tables_which_are_acceptable_to_be_looked_at_for_joining)

    print("list_of_tables_which_will_be_looked_at_for_joining")
    print(list_of_tables_which_will_be_looked_at_for_joining)


    list_of_dataframes_in_the_resulting_merged_df=[]
    for table_name_with_bfr in list_of_tables_which_will_be_looked_at_for_joining:
        df_with_bfr=pd.read_sql ( f'''select * from {table_name_with_bfr} ;''' ,
                                                 connection_to_db_with_bfr)
        list_of_dataframes_in_the_resulting_merged_df.append(df_with_bfr)
        # print(f"df_with_bfr for {table_name_with_bfr}")
        # print(df_with_bfr)


    resulting_df_with_bfr=\
        merge_dataframes(list_of_dataframes_in_the_resulting_merged_df)

    print("resulting_df_with_bfr")
    print(resulting_df_with_bfr.to_string())

    # Remove all rows from the dataframe in which the
    # column 'ticker_will_be_traced_and_position_entered' is equal to 'False'
    df_where_tracing_is_enabled = remove_rows_by_column2(
        resulting_df_with_bfr,
        column_name='ticker_will_be_traced_and_position_entered',
        column_value=False
    )
    df_where_tracing_is_enabled_copy=df_where_tracing_is_enabled.copy()
    df_where_tracing_is_enabled_copy.index = list(range(0, len(df_where_tracing_is_enabled)))
    df_where_tracing_is_enabled_copy["index"] = list(range(0, len(df_where_tracing_is_enabled)))

    print("df_where_tracing_is_enabled_copy")
    print(df_where_tracing_is_enabled_copy.to_string())
    return df_where_tracing_is_enabled_copy


if __name__=="__main__":
    database_name="levels_formed_by_highs_and_lows_for_cryptos_0000"
    build_entire_df_of_assets_which_will_be_used_for_position_entry(database_name)