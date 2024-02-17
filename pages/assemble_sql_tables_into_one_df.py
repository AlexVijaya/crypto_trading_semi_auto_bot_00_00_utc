from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
import asyncio
import os
import sys
import time
import traceback
import db_config
import sqlalchemy
import psycopg2
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# import talib
import datetime
import ccxt as ccxt_not_async
import ccxt.async_support as ccxt  # noqa: E402

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from sqlalchemy import inspect
import datetime as dt
from sqlalchemy import text
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from shitcoins_with_different_models import return_df_from_an_sql_query
import streamlit as st
def filter_tables(list_of_tables_in_bfr_models_db, list_of_all_possible_table_names_in_bfr_db):
    return [table for table in list_of_tables_in_bfr_models_db if table in list_of_all_possible_table_names_in_bfr_db]
def get_list_of_tables_in_db(engine_for_bfr_models_db):
    '''get list of all tables in db which is given as parameter'''
    inspector = inspect(engine_for_bfr_models_db)
    list_of_tables_in_db = inspector.get_table_names()

    return list_of_tables_in_db
# Define a function to check if a row exists in the worksheet
# Define a function to check if a row exists in the worksheet
def row_exists(worksheet, row_data):
    st.write("row_data")
    st.write(row_data)
    all_rows = worksheet.get_all_values()
    existing_data = pd.DataFrame(all_rows[1:], columns=all_rows[0])  # Assuming the first row is the header

    # Convert the input row data to a DataFrame for comparison
    new_row_df = pd.DataFrame([row_data], columns=existing_data.columns)
    new_row_df.reset_index(drop=True,inplace=True)
    st.write("new_row_df")
    st.write(new_row_df)
    st.write("existing_data")
    st.write(existing_data)
    # st.write("type(existing_data)")
    # st.write(type(existing_data))
    # st.write("type(existing_data)")
    # st.write(type(existing_data))
    # new_row_df_dict=new_row_df.to_dict(orient="records")
    # Check for duplicates in the existing data usingisin() with the new row
    # new_row_df=new_row_df.reset_index(inplace=True)
    # Assuming new_row_df is the DataFrame you want to reset the index for


    # new_row_df.reset_index(drop=True, inplace=True)

    duplicate_mask = existing_data.isin(new_row_df)
    st.write("duplicate_mask")
    st.write(duplicate_mask)
    row_already_exists = existing_data[duplicate_mask.all(axis=1)]
    st.write("row_already_exists")
    st.write(row_already_exists)

    return not row_already_exists.empty
def write_to_google_sheets1(dataframe):
    json_file_name = 'aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Define the path to the JSON file relative to the script's directory
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_dir_where_json_file_is, scope)
    gc = gspread.authorize(credentials)
    st.write("authorize ok!")
    # Convert datetime columns to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime(
        '%Y-%m-%d %H:%M:%S')
    dataframe = dataframe.fillna(-1000000)

    # Open the spreadsheet by its title
    spreadsheet = gc.open('streamlit_app_google_sheet')

    # Check if the worksheet exists
    # date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_models"
    worksheet = None
    for ws in spreadsheet.worksheets():
        if ws.title == worksheet_title:
            worksheet = ws
            print(f'Worksheet "{worksheet_title}" found!')
            break



    # # Clear the existing data in the worksheet
    # dataframe_that_is_already_in_the_worksheet=pd.DataFrame()
    # try:
    #     data = worksheet.get_all_values()
    #     st.write(type(data))
    #     # Create DataFrame with the first row as the header
    #     df = pd.DataFrame(data, columns=data[0])
    #
    #     # Drop the duplicated header row
    #     dataframe_that_is_already_in_the_worksheet = df[1:]
    #
    #     st.write("dataframe_that_is_already_in_the_worksheet1")
    #     st.write(dataframe_that_is_already_in_the_worksheet)
    #     column_names = dataframe_that_is_already_in_the_worksheet.columns.values.tolist()
    #     # Remove '_x' from each value if it ends with '_x'
    #     column_names = [name[:-2] if name.endswith('_x') else name for name in column_names]
    #
    #     # Update the Google Spreadsheet with the column names and corresponding values from the DataFrame
    #     # worksheet.insert_row(column_names, index=1, value_input_option='USER_ENTERED')
    #
    #     # Filter rows where the "index" column is equal to 0
    #     # dataframe_that_is_already_in_the_worksheet = dataframe_that_is_already_in_the_worksheet[dataframe_that_is_already_in_the_worksheet['index'] == 0]
    #     st.write("dataframe_that_is_already_in_the_worksheet2")
    #     st.write(dataframe_that_is_already_in_the_worksheet)
    # except:
    #     dataframe_that_is_already_in_the_worksheet = pd.DataFrame(columns=['ticker', ])
    #     st.write("dataframe_that_is_already_in_the_worksheet3")
    #     st.write(dataframe_that_is_already_in_the_worksheet)
    #     traceback.print_exc()
    #
    # st.write("dataframe_that_is_already_in_the_worksheet")
    # st.write(dataframe_that_is_already_in_the_worksheet)



    # worksheet.clear()


    # Convert datetime columns to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime('%Y-%m-%d %H:%M:%S')
    # Assuming df is your DataFrame
    dataframe = dataframe.convert_dtypes()

    # Handle missing values and get the column names from the DataFrame
    cleaned_df = dataframe.fillna(-1000000)
    st.write("cleaned_df")
    st.dataframe(cleaned_df)
    # Perform an inner join based on a common column
    # merged_data=pd.DataFrame()
    # if not dataframe_that_is_already_in_the_worksheet.empty:
    #     merged_data = dataframe_that_is_already_in_the_worksheet.merge(cleaned_df, on='ticker', how='outer')
    # else:
    #     merged_data=cleaned_df
    column_names = cleaned_df.columns.values.tolist()
    # Create a new worksheet if it doesn't exist
    if worksheet is None:
        worksheet = spreadsheet.add_worksheet(worksheet_title, 100, 100)  # You can adjust the dimensions as needed
        worksheet.append_row(column_names, value_input_option='USER_ENTERED')  # Write column names
        print(f'Worksheet "{worksheet_title}" created successfully!')
    # Remove '_x' from each value if it ends with '_x'
    # column_names = [name[:-2] if name.endswith('_x') else name for name in column_names]

    # Update the Google Spreadsheet with the column names and corresponding values from the DataFrame
    # worksheet.append_row(column_names, value_input_option='USER_ENTERED')  # Write column names

    # Append the data from the DataFrame to the worksheet
    for index, row in cleaned_df.iterrows():
        st.write("list(row)")
        st.write(list(row))

        # Assuming 'row' is the new row data to be appended
        if not row_exists(worksheet, row):
            worksheet.append_row(list(row), value_input_option='USER_ENTERED')
        else:
            st.write("Row already exists, not appending.")



        # worksheet.append_row(list(row), value_input_option='USER_ENTERED')

    data = worksheet.get_all_values()
    #     st.write(type(data))
    # Create DataFrame with the first row as the header
    df = pd.DataFrame(data, columns=data[0])
    df.drop_duplicates(subset=["ticker","timestamp_when_bfr_was_found"],inplace=True)
    worksheet.clear()
    # Append the data to the worksheet
    worksheet.append_rows(df.values.tolist(), value_input_option='USER_ENTERED')
    st.write("DataFrame written to Google Spreadsheet successfully!")

def find_unique_elements(list1, list2):
    unique_in_list1 = [item for item in list1 if item not in list2]
    unique_in_list2 = [item for item in list2 if item not in list1]
    return unique_in_list1, unique_in_list2
def write_to_google_sheets2(dataframe):
    json_file_name = 'aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Go one level up by getting the parent directory of the current directory
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    # Define the path to the JSON file relative to the parent directory
    path_to_dir_where_json_file_is = os.path.join(parent_directory, 'datasets', 'json_key_for_google',json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_dir_where_json_file_is, scope)
    gc = gspread.authorize(credentials)
    st.write("authorize ok!")
    # Convert datetime columns to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime(
        '%Y-%m-%d %H:%M:%S')
    dataframe = dataframe.fillna(-1000000)

    # Open the spreadsheet by its title
    spreadsheet = gc.open('streamlit_app_google_sheet')

    # Check if the worksheet exists
    # date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_models"
    worksheet = None
    for ws in spreadsheet.worksheets():
        if ws.title == worksheet_title:
            worksheet = ws
            print(f'Worksheet "{worksheet_title}" found!')
            break






    # Convert datetime column 'datetime_when_bfr_was_found' to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime('%Y-%m-%d %H:%M:%S')
    # Assuming df is your DataFrame
    dataframe = dataframe.convert_dtypes()

    # Handle missing values and get the column names from the DataFrame
    cleaned_df = dataframe.fillna(-1000000)
    st.write("cleaned_df")
    st.dataframe(cleaned_df)
    # Perform an inner join based on a common column
    # merged_data=pd.DataFrame()
    # if not dataframe_that_is_already_in_the_worksheet.empty:
    #     merged_data = dataframe_that_is_already_in_the_worksheet.merge(cleaned_df, on='ticker', how='outer')
    # else:
    #     merged_data=cleaned_df

    # # Loop through columns, apply scientific notation to columns starting with "volume" and not containing "usd" (case-insensitive)
    # for column in cleaned_df.columns:
    #     if column.startswith('volume') and 'usd' not in column.lower():
    #         try:
    #             cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce')
    #             cleaned_df[column] = cleaned_df[column].map('{:e}'.format)
    #             st.write("cleaned_df[column]")
    #             st.write(cleaned_df[column].to_string())
    #         except ValueError:
    #             traceback.print_exc()

    column_names = cleaned_df.columns.values.tolist()
    # Create a new worksheet if it doesn't exist
    if worksheet is None:
        worksheet = spreadsheet.add_worksheet(worksheet_title, 100, 100)  # You can adjust the dimensions as needed
        worksheet.append_row(column_names, value_input_option='USER_ENTERED')  # Write column names
        print(f'Worksheet "{worksheet_title}" created successfully!')

        # Append the data from the DataFrame to the worksheet
        for index, row in cleaned_df.iterrows():
            st.write("list(row)")
            st.write(list(row))

            # Assuming 'row' is the new row data to be appended
            if not row_exists(worksheet, row):

                worksheet.append_row(list(row), value_input_option='USER_ENTERED')
            else:
                st.write("Row already exists, not appending.")

    else:
        already_existing_data_in_worksheet = worksheet.get_all_values()
        already_existing_data_in_worksheet_df = pd.DataFrame(already_existing_data_in_worksheet, columns=already_existing_data_in_worksheet[0])

        # # Loop through columns, apply scientific notation to columns starting with "volume" and not containing "usd" (case-insensitive)
        # for column in already_existing_data_in_worksheet_df.columns:
        #     if column.startswith('volume') and 'usd' not in column.lower():
        #         try:
        #             # Convert to numeric with float type, preserving non-convertible values
        #             converted_values = pd.to_numeric(already_existing_data_in_worksheet_df[column], errors='coerce')
        #
        #             # Replace the original column with the converted values, or retain the original if conversion fails
        #             already_existing_data_in_worksheet_df[column] = converted_values.fillna(already_existing_data_in_worksheet_df[column])
        #
        #             # Apply scientific notation only to numeric data
        #             already_existing_data_in_worksheet_df[column] = already_existing_data_in_worksheet_df[column].apply(
        #                 lambda x: '{:g}'.format(x) if pd.notnull(x) and pd.api.types.is_number(x) else x)
        #         except ValueError:
        #             traceback.print_exc()
        st.write("already_existing_data_in_worksheet_df")
        st.dataframe(already_existing_data_in_worksheet_df)
        already_existing_data_in_worksheet_df=already_existing_data_in_worksheet_df[1:]
        st.write("already_existing_data_in_worksheet_df")
        st.dataframe(already_existing_data_in_worksheet_df)
        # Assuming df1 and df2 are your DataFrames

        num_columns_in_cleaned_df = len(cleaned_df.columns)
        st.write("num_columns_in_cleaned_df")
        st.write(num_columns_in_cleaned_df)
        num_columns_in_already_existing_data_in_worksheet_df = len(already_existing_data_in_worksheet_df.columns)
        st.write("num_columns_in_already_existing_data_in_worksheet_df")
        st.write(num_columns_in_already_existing_data_in_worksheet_df)

        result_a, result_b = find_unique_elements(already_existing_data_in_worksheet_df.columns, cleaned_df.columns)
        st.write("Unique elements in already_existing_data_in_worksheet_df:", result_a)
        st.write("Unique elements in cleaned_df:", result_b)


        concatenated_df = pd.concat([already_existing_data_in_worksheet_df, cleaned_df], ignore_index=True)
        st.write("concatenated_df1")
        st.dataframe(concatenated_df)
        concatenated_df.drop_duplicates(subset=("ticker"),inplace=True,ignore_index=False)
        st.write("concatenated_df2")
        st.dataframe(concatenated_df)
        # Assuming already_existing_data_in_worksheet_df_length is the length of the already_existing_data_in_worksheet_df DataFrame
        length_of_existing_data = len(already_existing_data_in_worksheet_df)

        # The last part of concatenated_df without already_existing_data_in_worksheet_df in the beginning
        st.write("length_of_existing_data")
        st.write(length_of_existing_data)
        remaining_data_df = concatenated_df[length_of_existing_data:]

        remaining_data_df = remaining_data_df.fillna(-1000000)
        worksheet.append_rows(remaining_data_df.values.tolist(), value_input_option='USER_ENTERED')



    st.write("DataFrame written to Google Spreadsheet successfully!")

def write_to_google_sheets(dataframe):
    json_file_name='aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # path_to_dir_where_json_file_is = os.path.join(os.getcwd(), '/home/alex/PycharmProjects/crypto_trading_semi_auto_bot_00_00_utc/datasets/', 'json_key_for_google')
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')
    os.path.join(current_directory, 'datasets', 'json_key_for_google')
    path_to_json=os.path.join(path_to_dir_where_json_file_is, json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, scope)
    gc = gspread.authorize(credentials)
    st.write("authorize ok!")
    # Convert datetime columns to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime('%Y-%m-%d %H:%M:%S')
    cleaned_df = dataframe.fillna(-1000000)  # Replace NaN with 0 (or any other appropriate value)
    # Get the column names from the DataFrame
    column_names = cleaned_df.columns.values.tolist()

    # Authorize and update the Google Spreadsheet
    # sheet = gc.open("streamlit_app_google_sheet").sheet1

    # Open the spreadsheet by its title
    spreadsheet = gc.open('streamlit_app_google_sheet')

    # Check if the worksheet exists
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = date_today
    worksheet_found = False
    for worksheet in spreadsheet.worksheets():
        if worksheet.title == worksheet_title:
            worksheet_found = True
            break

    # Create a new worksheet if it doesn't exist
    if not worksheet_found:
        spreadsheet.add_worksheet(worksheet_title, 100, 100)  # You can adjust the dimensions as needed
        print(f'Worksheet "{worksheet_title}" created successfully!')
    else:
        print(f'Worksheet "{worksheet_title}" already exists.')

    worksheet = spreadsheet.worksheet(worksheet_title)


    # sheet.clear()  # Clear the existing data in the sheet
    worksheet.append_rows([column_names] + cleaned_df.values.tolist(), value_input_option='USER_ENTERED')

    # Get existing rows from the worksheet
    existing_records = worksheet.get_all_records()

    # Append only the new rows to the worksheet
    new_rows = dataframe.fillna(-1000000)
    new_unique_records = new_rows.to_dict('records')
    existing_unique_records = [record for record in existing_records if record not in new_unique_records]

    print("existing_unique_records")
    print(existing_unique_records)
    # Append only the new rows to the worksheet
    rows_to_append = [record for record in new_unique_records if record not in existing_unique_records]
    print("rows_to_append")
    print(rows_to_append)

    # print("[column_names] + cleaned_df.values.tolist())")
    # print([column_names] + cleaned_df.values.tolist())
    if rows_to_append:
        worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
        print(f"{len(rows_to_append)} new rows appended to the worksheet.")
    else:
        print("All rows already exist in the worksheet. No rows appended.")

def write_to_google_sheets3(dataframe):
    json_file_name='aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # path_to_dir_where_json_file_is = os.path.join(os.getcwd(), '/home/alex/PycharmProjects/crypto_trading_semi_auto_bot_00_00_utc/datasets/', 'json_key_for_google')
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # path_to_dir_where_json_file_is = os.path.join(os.getcwd(), '/home/alex/PycharmProjects/crypto_trading_semi_auto_bot_00_00_utc/datasets/', 'json_key_for_google')
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')
    path_to_json=os.path.join(path_to_dir_where_json_file_is, json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, scope)
    gc = gspread.authorize(credentials)
    st.write("authorize ok!")
    # Convert datetime columns to string format
    dataframe['datetime_when_bfr_was_found'] = pd.to_datetime(dataframe['datetime_when_bfr_was_found']).dt.strftime('%Y-%m-%d %H:%M:%S')
    cleaned_df = dataframe.fillna(-1000000)  # Replace NaN with 0 (or any other appropriate value)
    # Get the column names from the DataFrame
    column_names = cleaned_df.columns.values.tolist()

    # Authorize and update the Google Spreadsheet
    # sheet = gc.open("streamlit_app_google_sheet").sheet1

    # Open the spreadsheet by its title
    spreadsheet = gc.open('streamlit_app_google_sheet')

    # Check if the worksheet exists
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_model"
    worksheet_found = False
    for worksheet in spreadsheet.worksheets():
        if worksheet.title == worksheet_title:
            worksheet_found = True
            break

    # Create a new worksheet if it doesn't exist
    if not worksheet_found:
        spreadsheet.add_worksheet(worksheet_title, 100, 100)  # You can adjust the dimensions as needed
        print(f'Worksheet "{worksheet_title}" created successfully!')
    else:
        print(f'Worksheet "{worksheet_title}" already exists.')

    worksheet = spreadsheet.worksheet(worksheet_title)


    # # sheet.clear()  # Clear the existing data in the sheet
    # worksheet.append_rows([column_names] + cleaned_df.values.tolist(), value_input_option='USER_ENTERED')

    # Get existing rows from the worksheet
    existing_records = worksheet.get_all_records()

    # Append only the new rows to the worksheet
    new_rows = dataframe.fillna(-1000000)
    new_unique_records = new_rows.to_dict('records')
    existing_unique_records = [record for record in existing_records if record not in new_unique_records]

    print("existing_unique_records")
    print(existing_unique_records)
    # Append only the new rows to the worksheet
    rows_to_append = [record for record in new_unique_records if record not in existing_unique_records]
    print("rows_to_append")
    print(rows_to_append)

    # print("[column_names] + cleaned_df.values.tolist())")
    # print([column_names] + cleaned_df.values.tolist())
    if rows_to_append:
        worksheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
        print(f"{len(rows_to_append)} new rows appended to the worksheet.")
    else:
        print("All rows already exist in the worksheet. No rows appended.")
def remove_false_rows(dataframe, column_name):
    # Assuming 'merged_dataframe' is the DataFrame and 'ticker_will_be_traced_and_position_entered' is the column name

    # Select rows where the column value is True
    filtered_dataframe = dataframe[dataframe[column_name] == True]

    return filtered_dataframe
def assemble_sql_tables_into_one_df(db_where_bfr_models_are_stored):


    engine_for_bfr_models_db, \
        connection_to_bfr_models_db = \
        connect_to_postgres_db_without_deleting_it_first(db_where_bfr_models_are_stored)
    list_of_tables_in_bfr_models_db=get_list_of_tables_in_db(engine_for_bfr_models_db)

    list_of_all_possible_table_names_in_bfr_db = ["current_breakout_situations_of_atl_position_entry_next_day",
                                                  "current_breakout_situations_of_ath_position_entry_next_day",
                                                  "current_breakout_situations_of_atl_position_entry_on_day_two",
                                                  "current_breakout_situations_of_ath_position_entry_on_day_two",
                                                  "current_false_breakout_of_atl_by_one_bar",
                                                  "current_false_breakout_of_ath_by_one_bar",
                                                  "current_false_breakout_of_atl_by_two_bars",
                                                  "current_false_breakout_of_ath_by_two_bars",
                                                  "current_rebound_situations_from_atl",
                                                  "current_rebound_situations_from_ath",
                                                  "current_complex_false_breakout_of_atl",
                                                  "current_complex_false_breakout_of_ath",
                                                  "current_fast_breakout_situations_of_ath",
                                                  "current_fast_breakout_situations_of_atl"]

    print("list_of_tables_in_bfr_models_db")
    print(list_of_tables_in_bfr_models_db)
    filtered_tables = filter_tables(list_of_tables_in_bfr_models_db, list_of_all_possible_table_names_in_bfr_db)
    print("filtered_tables")
    print(filtered_tables)

    # Initialize an empty list to store the dataframes
    dfs = []
    for bfr_table in filtered_tables:
        table_with_bfr_models_df = \
            return_df_from_an_sql_query(f'''select * from "{bfr_table}"''',
                              engine_for_bfr_models_db)

        dfs.append(table_with_bfr_models_df)
    # Concatenate the list of dataframes into a single dataframe
    merged_dataframe = pd.concat(dfs, ignore_index=True)
    print("merged_dataframe")
    print(merged_dataframe)
    return merged_dataframe

if __name__=="__main__":
    db_where_bfr_models_are_stored="levels_formed_by_highs_and_lows_for_cryptos_0000"
    # merged_dataframe=pd.DataFrame()
    merged_dataframe=assemble_sql_tables_into_one_df(db_where_bfr_models_are_stored)
    st.link_button("See google spreadsheet with bfr data","https://docs.google.com/spreadsheets/d/1mBapTa6oZmJ_nFgqrHiLsW5mvkIYLaVJKjgSO12KBwc/edit#gid=2105616670")
    column_name_to_filter_false_values_of_which="ticker_will_be_traced_and_position_entered"
    filtered_merged_dataframe = remove_false_rows(merged_dataframe, column_name_to_filter_false_values_of_which)
    write_to_google_sheets2(filtered_merged_dataframe)
