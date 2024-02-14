import traceback
import datetime
import numpy as np
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
from sqlalchemy import inspect

from sqlalchemy import create_engine

from sqlalchemy_utils import create_database,database_exists
from collections import Counter
from get_info_from_load_markets2 import get_all_time_high_low
from get_info_from_load_markets2 import get_all_time_low_from_some_exchange
from get_info_from_load_markets2 import get_all_time_high_from_some_exchange
from get_info_from_load_markets2 import get_exchange_object2
from get_info_from_load_markets import fetch_entire_ohlcv
from get_info_from_load_markets import fetch_entire_ohlcv_without_exchange_name
from async_update_historical_USDT_pairs_for_1D import connect_to_postgres_db_without_deleting_it_first
from async_update_historical_USDT_pairs_for_1D import get_list_of_tables_in_db
from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
# from shitcoins_with_different_models import pd.read_sql_query
def add_trading_pairs_to_sql_table_if_they_were_processed(table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be,
                                                          engine_for_db_where_ticker_which_may_have_breakout_situations_processed,
                                                          list_of_already_processed_pairs,
                                                          column_name,
                                                          stock_name,
                                                          df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run):
    print("df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run7")
    print(
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.to_string())
    df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.at[
        0, f"{column_name}"] = stock_name

    try:
        if "level_0" in df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.columns:
            df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.drop(
                columns="level_0", inplace=True)
    except:
        traceback.print_exc()
    # df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.reset_index(
    #     inplace=True)

    print("list_of_already_processed_pairs")
    print(list_of_already_processed_pairs)
    print("df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run8")
    print(df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run)

    df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run[
            ~df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run[
                f"{column_name}"].isin(list_of_already_processed_pairs)].copy()

    df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.to_sql(
        table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be,
        engine_for_db_where_ticker_which_may_have_breakout_situations_processed,
        if_exists='append', index=False)

def create_empty_table_if_it_does_not_exist_or_return_list_of_already_processed_pairs_if_table_exists(
        column_name,
        db_where_ticker_which_may_have_breakout_situations,
        table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be):
    engine_for_db_where_ticker_which_may_have_breakout_situations_processed, \
        connection_to_db_where_ticker_which_may_have_breakout_situations_processed = \
        connect_to_postgres_db_without_deleting_it_first(
            db_where_ticker_which_may_have_breakout_situations + "_processed")
    list_of_tables_in_db_where_ticker_which_may_have_breakout_situations_processed = \
        get_list_of_tables_in_db(engine_for_db_where_ticker_which_may_have_breakout_situations_processed)
    list_of_already_processed_pairs = []
    # df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run=pd.DataFrame()


    if table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be not in \
            list_of_tables_in_db_where_ticker_which_may_have_breakout_situations_processed:
        # create empty table in db if it does not yet exist
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
            pd.DataFrame(dtype='object', columns=[f"{column_name}"])
        if "level_0" in df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.columns:
            df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.drop(
                columns="level_0", inplace=True)

        if df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.empty:
            df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.to_sql(
                table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be,
                engine_for_db_where_ticker_which_may_have_breakout_situations_processed,
                if_exists='replace')
    else:
        # if table with already processed pair exists
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
            pd.read_sql_query(
                f'''select * from "{table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be}"''',
                engine_for_db_where_ticker_which_may_have_breakout_situations_processed)
        try:

            if "level_0" in df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.columns:
                df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.drop(
                    columns="level_0", inplace=True)

        except:
            traceback.print_exc()
        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run.reset_index(
            inplace=True)

        last_table_name_in_df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
            df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run[
                f"{column_name}"].iloc[-1]

        engine_for_db_where_ticker_which_may_have_breakout_situations_processed.execute(
            f'''DELETE FROM "{table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be}"
                WHERE {column_name} = '{
            last_table_name_in_df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run}';''')

        df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run = \
            pd.read_sql_query(
                f'''select * from "{table_where_ticker_which_may_have_breakout_situations_from_ath_or_atl_will_be}"''',
                engine_for_db_where_ticker_which_may_have_breakout_situations_processed)

        list_of_already_processed_pairs = list(
            df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run[
                f"{column_name}"])
        list_of_already_processed_pairs = list(set(list_of_already_processed_pairs))

    return list_of_already_processed_pairs,df_with_table_name_which_has_been_already_processed_so_we_dont_need_to_process_it_again_on_next_run

def extract_timestamps_as_string(df):
    timestamp_values = df["Timestamp"].astype(int).astype(str)  # Convert Timestamp column values to string
    print("timestamp_values")
    print(timestamp_values)
    if len(timestamp_values)>1:
        timestamps_string = "_".join(timestamp_values)  # Join values with underscores
        return timestamps_string
    else:
        one_timestamp_as_string=timestamp_values.iloc[0]
        return one_timestamp_as_string

def extract_open_times_as_string(df):
    open_time_values = df["open_time"].astype(str)  # Convert open_time column values to string
    formatted_values = [value.replace(" ", "_") for value in open_time_values]  # Replace space with underscore
    if len(df)>1:
        open_times_string = "__".join(formatted_values)  # Join values with double underscores
        return open_times_string
    else:
        one_open_time_as_string_separated_by_underscore=formatted_values[0]
        return one_open_time_as_string_separated_by_underscore
def add_info_to_df_about_all_time_high_number_of_times_it_was_touched_its_timestamps_and_datetimes(all_time_high,
                                                                                                   df_with_level_atr_bpu_bsu_etc,
                                                                                                   last_two_years_of_data,
                                                                                                   round_to_this_number_of_non_zero_digits):
    number_of_zeroes_in_all_time_high = count_zeros_number_with_e_notaton_is_acceptable(all_time_high)
    # print("number_of_zeroes_in_all_time_high")
    # print(number_of_zeroes_in_all_time_high)
    rounded_all_time_high = round(all_time_high,
                                  number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits)
    # print("rounded_all_time_high")
    # print(rounded_all_time_high)
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df = last_two_years_of_data.copy()
    # round high and low to two decimal number
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["high"] = \
        last_two_years_of_data["high"].apply(round, args=(
            number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits,))
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["low"] = \
        last_two_years_of_data["low"].apply(round, args=(
            number_of_zeroes_in_all_time_high + round_to_this_number_of_non_zero_digits,))

    # print("rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df")
    # print(rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df.to_string())

    ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines = \
        rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df.loc[
            rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["high"] == rounded_all_time_high]

    number_of_times_this_all_time_high_occurred = len(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)
    number_of_times_this_all_time_high_occurred=int(number_of_times_this_all_time_high_occurred)

    # print("ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines123")
    # print(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines.to_string())

    timestamps_of_all_time_highs_as_string = \
        extract_timestamps_as_string(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)

    # print("timestamps_of_all_time_highs_as_string")
    # print(timestamps_of_all_time_highs_as_string)

    open_times_of_all_time_highs_as_string = \
        extract_open_times_as_string(ohlcv_df_with_high_equal_to_ath_slice_should_be_a_few_lines)

    # df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_high_occurred"] = \
    #     df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_high_occurred"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "number_of_times_this_all_time_high_occurred"] = number_of_times_this_all_time_high_occurred

    # df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_highs_as_string"] = \
    #     df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_highs_as_string"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "timestamps_of_all_time_highs_as_string"] = timestamps_of_all_time_highs_as_string

    # df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_highs_as_string"] = \
    #     df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_highs_as_string"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "open_times_of_all_time_highs_as_string"] = open_times_of_all_time_highs_as_string

    df_with_level_atr_bpu_bsu_etc.at[
        0, "round_to_this_number_of_non_zero_digits"] = round_to_this_number_of_non_zero_digits

    # print("df_with_level_atr_bpu_bsu_etc8")
    # print(df_with_level_atr_bpu_bsu_etc.to_string())

    return df_with_level_atr_bpu_bsu_etc


def add_info_to_df_about_all_time_low_number_of_times_it_was_touched_its_timestamps_and_datetimes(all_time_low,
                                                                                                  df_with_level_atr_bpu_bsu_etc,
                                                                                                  last_two_years_of_data,
                                                                                                  round_to_this_number_of_non_zero_digits):
    number_of_zeroes_in_all_time_low = count_zeros_number_with_e_notaton_is_acceptable(all_time_low)
    rounded_all_time_low = round(all_time_low,
                                 number_of_zeroes_in_all_time_low + round_to_this_number_of_non_zero_digits)
    print("rounded_all_time_low")
    print(rounded_all_time_low)
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df = last_two_years_of_data.copy()
    # round high and low to two decimal number
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["high"] = \
        last_two_years_of_data["high"].apply(round, args=(
            number_of_zeroes_in_all_time_low + round_to_this_number_of_non_zero_digits,))
    rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["low"] = \
        last_two_years_of_data["low"].apply(round, args=(
            number_of_zeroes_in_all_time_low + round_to_this_number_of_non_zero_digits,))

    print("rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df")
    print(rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df)

    ohlcv_df_with_low_equal_to_atl_slice_should_be_a_few_lines = \
        rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df.loc[
            rounded_high_and_low_table_with_ohlcv_last_two_years_of_data_df["low"] == rounded_all_time_low]

    number_of_times_this_all_time_low_occurred = len(ohlcv_df_with_low_equal_to_atl_slice_should_be_a_few_lines)

    timestamps_of_all_time_lows_as_string = \
        extract_timestamps_as_string(ohlcv_df_with_low_equal_to_atl_slice_should_be_a_few_lines)

    open_times_of_all_time_lows_as_string = \
        extract_open_times_as_string(ohlcv_df_with_low_equal_to_atl_slice_should_be_a_few_lines)

    # df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_low_occurred"] = \
    #     df_with_level_atr_bpu_bsu_etc["number_of_times_this_all_time_low_occurred"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "number_of_times_this_all_time_low_occurred"] = number_of_times_this_all_time_low_occurred

    # df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_lows_as_string"] = \
    #     df_with_level_atr_bpu_bsu_etc["timestamps_of_all_time_lows_as_string"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "timestamps_of_all_time_lows_as_string"] = timestamps_of_all_time_lows_as_string

    # df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_lows_as_string"] = \
    #     df_with_level_atr_bpu_bsu_etc["open_times_of_all_time_lows_as_string"].astype('object')
    df_with_level_atr_bpu_bsu_etc.at[
        0, "open_times_of_all_time_lows_as_string"] = open_times_of_all_time_lows_as_string

    df_with_level_atr_bpu_bsu_etc.at[
        0, "round_to_this_number_of_non_zero_digits"] = round_to_this_number_of_non_zero_digits

    return df_with_level_atr_bpu_bsu_etc
def generate_placeholder_df_with_default_values_with_max_profit_target_equal_to_zero_and_tp_4_to_100(type_of_stop_loss,
                                                                          min_profit_target_multiple_in_range_func,
                                                                          max_profit_target_multiple_in_range_func):
    list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime = []
    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()

    if type_of_stop_loss == 'calculated':
        list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
            f"max_profit_target_multiple_when_sl_calculated")
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):

            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated")


    elif type_of_stop_loss == 'technical':
        list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
            f"max_profit_target_multiple_when_sl_technical")
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):

            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical")
    else:
        print(f"unknown_stop_loss_type={type_of_stop_loss}")

    if type_of_stop_loss == 'calculated':
        df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame(
            columns=list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime)
        df_with_tp_x_to_one_its_timestamp_and_datetime.at[0, "max_profit_target_multiple_when_sl_calculated"] = 0
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = False
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_sl_calculated"] = 0.0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = 0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = datetime.datetime.fromtimestamp(
                0)
    elif type_of_stop_loss == 'technical':
        df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame(
            columns=list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime)
        df_with_tp_x_to_one_its_timestamp_and_datetime.at[0, "max_profit_target_multiple_when_sl_technical"] = 0
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_technical"] = False
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_sl_technical"] = 0.0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical"] = 0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical"] = datetime.datetime.fromtimestamp(
                0)
    else:
        print(f"unknown_stop_loss_type={type_of_stop_loss} in df filling with default values")
    return df_with_tp_x_to_one_its_timestamp_and_datetime

def generate_df_with_default_values_with_max_profit_target_and_tp_4_to_100(type_of_stop_loss,
                                                                          min_profit_target_multiple_in_range_func,
                                                                          max_profit_target_multiple_in_range_func):
    list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime = []
    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()

    if type_of_stop_loss == 'calculated':
        list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
            f"max_profit_target_multiple_when_sl_calculated")
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):

            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated")


    elif type_of_stop_loss == 'technical':
        list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
            f"max_profit_target_multiple_when_sl_technical")
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):

            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"take_profit_{profit_target_multiple}_to_one_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical")
            list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime.append(
                f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical")
    else:
        print(f"unknown_stop_loss_type={type_of_stop_loss}")

    if type_of_stop_loss == 'calculated':
        df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame(
            columns=list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime)
        df_with_tp_x_to_one_its_timestamp_and_datetime.at[0, "max_profit_target_multiple_when_sl_calculated"] = 3
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = False
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_sl_calculated"] = 0.0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = 0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_calculated"] = datetime.datetime.fromtimestamp(
                0)
    elif type_of_stop_loss == 'technical':
        df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame(
            columns=list_of_columns_in_df_with_tp_x_to_one_its_timestamp_and_datetime)
        df_with_tp_x_to_one_its_timestamp_and_datetime.at[0, "max_profit_target_multiple_when_sl_technical"] = 3
        for profit_target_multiple in range(min_profit_target_multiple_in_range_func,
                                            max_profit_target_multiple_in_range_func + 1, 1):
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_technical"] = False
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"take_profit_{profit_target_multiple}_to_one_sl_technical"] = 0.0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical"] = 0
            df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                0, f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_technical"] = datetime.datetime.fromtimestamp(
                0)
    else:
        print(f"unknown_stop_loss_type={type_of_stop_loss} in df filling with default values")
    return df_with_tp_x_to_one_its_timestamp_and_datetime
def add_to_df_result_of_return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,
        df_with_level_atr_bpu_bsu_etc,
        index_in_iteration,
        entire_original_table_with_ohlcv_data_df,
        side,
        sell_order,
        take_profit_when_sl_is_technical_3_to_1,
        technical_stop_loss):
    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()

    try:
        # add statistical info to df if technical sl and tp have been reached
        max_distance_from_level_price_in_this_bar_in_atr, \
            take_profit_when_sl_is_technical_3_to_1_is_reached, \
            technical_stop_loss_is_reached, \
            daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
            timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached, \
            timestamp_when_technical_stop_loss_was_reached, \
            sell_order_was_touched, \
            timestamp_when_sell_order_was_touched, \
            first_bar_after_bfr_opened_lower_than_sell_order,\
            df_with_tp_x_to_one_its_timestamp_and_datetime = return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,
            index_in_iteration,
            entire_original_table_with_ohlcv_data_df,
            side,
            sell_order,
            take_profit_when_sl_is_technical_3_to_1,
            technical_stop_loss)

        if df_with_tp_x_to_one_its_timestamp_and_datetime.empty:
            type_of_stop_loss = "technical"
            min_profit_target_multiple_in_range_func = 4
            max_profit_target_multiple_in_range_func = 100
            df_with_tp_x_to_one_its_timestamp_and_datetime = generate_placeholder_df_with_default_values_with_max_profit_target_equal_to_zero_and_tp_4_to_100(
                type_of_stop_loss,
                min_profit_target_multiple_in_range_func,
                max_profit_target_multiple_in_range_func)

        print("technical_sl_df_with_tp_x_to_one_its_timestamp_and_datetime123_sell_order")
        print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())

        df_with_level_atr_bpu_bsu_etc.at[0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
        df_with_level_atr_bpu_bsu_etc.at[0, "first_bar_after_bfr_opened_lower_than_sell_order"] = first_bar_after_bfr_opened_lower_than_sell_order
        df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_technical_3_to_1_is_reached"] = take_profit_when_sl_is_technical_3_to_1_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_take_profit_when_sl_is_technical_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached
        if pd.isna(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] = \
                datetime.datetime.fromtimestamp(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "technical_stop_loss_is_reached"] = technical_stop_loss_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_technical_stop_loss_was_reached"] = timestamp_when_technical_stop_loss_was_reached
        if pd.isna(timestamp_when_technical_stop_loss_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_technical_stop_loss_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_technical_stop_loss_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_technical_stop_loss_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "sell_order_was_touched"] = sell_order_was_touched
        df_with_level_atr_bpu_bsu_etc.at[0, "max_distance_from_level_price_in_this_bar_in_atr"] = max_distance_from_level_price_in_this_bar_in_atr

        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_sell_order_was_touched"] = timestamp_when_sell_order_was_touched
        if pd.isna(timestamp_when_sell_order_was_touched) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_sell_order_was_touched"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_sell_order_was_touched)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_sell_order_was_touched"] = datetime.datetime.fromtimestamp(
                0)
    except:
        traceback.print_exc()

    df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached = pd.concat(
        [df_with_level_atr_bpu_bsu_etc, df_with_tp_x_to_one_its_timestamp_and_datetime], axis=1)
    print("df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached1")
    print(df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached.to_string())
    return df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached


def add_to_df_result_of_return_bool_whether_calculated_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,
        df_with_level_atr_bpu_bsu_etc,
        index_in_iteration,
        entire_original_table_with_ohlcv_data_df,
        side,
        sell_order,
        take_profit_when_sl_is_calculated_3_to_1,
        calculated_stop_loss):
    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()

    try:
        # add statistical info to df if calculated sl and tp have been reached
        max_distance_from_level_price_in_this_bar_in_atr,\
            take_profit_when_sl_is_calculated_3_to_1_is_reached, \
            calculated_stop_loss_is_reached, \
            daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
            timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached, \
            timestamp_when_calculated_stop_loss_was_reached, \
            sell_order_was_touched, \
            timestamp_when_sell_order_was_touched, \
            first_bar_after_bfr_opened_lower_than_sell_order,\
            df_with_tp_x_to_one_its_timestamp_and_datetime = return_bool_whether_calculated_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,
            index_in_iteration,
            entire_original_table_with_ohlcv_data_df, side,
            sell_order,
            take_profit_when_sl_is_calculated_3_to_1,
            calculated_stop_loss)

        if df_with_tp_x_to_one_its_timestamp_and_datetime.empty:
            type_of_stop_loss = "calculated"
            min_profit_target_multiple_in_range_func = 4
            max_profit_target_multiple_in_range_func = 100
            df_with_tp_x_to_one_its_timestamp_and_datetime = generate_placeholder_df_with_default_values_with_max_profit_target_equal_to_zero_and_tp_4_to_100(
                type_of_stop_loss,
                min_profit_target_multiple_in_range_func,
                max_profit_target_multiple_in_range_func)

        print("calculated_sl_df_with_tp_x_to_one_its_timestamp_and_datetime123_sell_order")
        print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())

        df_with_level_atr_bpu_bsu_etc.at[0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
        df_with_level_atr_bpu_bsu_etc.at[0, "first_bar_after_bfr_opened_lower_than_sell_order"] = first_bar_after_bfr_opened_lower_than_sell_order
        df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_calculated_3_to_1_is_reached"] = take_profit_when_sl_is_calculated_3_to_1_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached
        if pd.isna(timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "calculated_stop_loss_is_reached"] = calculated_stop_loss_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_calculated_stop_loss_was_reached"] = timestamp_when_calculated_stop_loss_was_reached
        if pd.isna(timestamp_when_calculated_stop_loss_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_calculated_stop_loss_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_calculated_stop_loss_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_calculated_stop_loss_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "sell_order_was_touched"] = sell_order_was_touched
        df_with_level_atr_bpu_bsu_etc.at[
            0, "max_distance_from_level_price_in_this_bar_in_atr"] = max_distance_from_level_price_in_this_bar_in_atr
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_sell_order_was_touched"] = timestamp_when_sell_order_was_touched
        if pd.isna(timestamp_when_sell_order_was_touched) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_sell_order_was_touched"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_sell_order_was_touched)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_sell_order_was_touched"] = datetime.datetime.fromtimestamp(
                0)
    except:
        traceback.print_exc()

    df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached = pd.concat(
        [df_with_level_atr_bpu_bsu_etc, df_with_tp_x_to_one_its_timestamp_and_datetime], axis=1)
    print("df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached2")
    print(df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached.to_string())
    return df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached

def add_to_df_result_of_return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached(level_price,
                                                                                            advanced_atr,df_with_level_atr_bpu_bsu_etc,
                                                                                            index_in_iteration,
                                                                                            entire_original_table_with_ohlcv_data_df,
                                                                                            side,
                                                                                            buy_order,
                                                                                            take_profit_when_sl_is_technical_3_to_1,
                                                                                            technical_stop_loss):
    df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame()


    try:
        # add statistical info to df if technical sl and tp have been reached
        max_distance_from_level_price_in_this_bar_in_atr,\
            take_profit_when_sl_is_technical_3_to_1_is_reached, \
            technical_stop_loss_is_reached, \
            daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
            timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached, \
            timestamp_when_technical_stop_loss_was_reached, \
            buy_order_was_touched, \
            timestamp_when_buy_order_was_touched, \
            first_bar_after_bfr_opened_lower_than_buy_order,\
            df_with_tp_x_to_one_its_timestamp_and_datetime = return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached(level_price,
                        advanced_atr,
            index_in_iteration,
            entire_original_table_with_ohlcv_data_df,
            side,
            buy_order,
            take_profit_when_sl_is_technical_3_to_1,
            technical_stop_loss)

        if df_with_tp_x_to_one_its_timestamp_and_datetime.empty:
            type_of_stop_loss = "technical"
            min_profit_target_multiple_in_range_func = 4
            max_profit_target_multiple_in_range_func = 100
            df_with_tp_x_to_one_its_timestamp_and_datetime = generate_placeholder_df_with_default_values_with_max_profit_target_equal_to_zero_and_tp_4_to_100(
                type_of_stop_loss,
                min_profit_target_multiple_in_range_func,
                max_profit_target_multiple_in_range_func)
        print("technical_sl_df_with_tp_x_to_one_its_timestamp_and_datetime123_buy_order")
        print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())



        df_with_level_atr_bpu_bsu_etc.at[0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
        df_with_level_atr_bpu_bsu_etc.at[0, "first_bar_after_bfr_opened_lower_than_buy_order"] = first_bar_after_bfr_opened_lower_than_buy_order
        df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_technical_3_to_1_is_reached"] = take_profit_when_sl_is_technical_3_to_1_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_take_profit_when_sl_is_technical_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached
        if pd.isna(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] = \
                datetime.datetime.fromtimestamp(timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "technical_stop_loss_is_reached"] = technical_stop_loss_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_technical_stop_loss_was_reached"] = timestamp_when_technical_stop_loss_was_reached
        if pd.isna(timestamp_when_technical_stop_loss_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_technical_stop_loss_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_technical_stop_loss_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_technical_stop_loss_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "buy_order_was_touched"] = buy_order_was_touched
        df_with_level_atr_bpu_bsu_etc.at[
            0, "max_distance_from_level_price_in_this_bar_in_atr"] = max_distance_from_level_price_in_this_bar_in_atr
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_buy_order_was_touched"] = timestamp_when_buy_order_was_touched
        if pd.isna(timestamp_when_buy_order_was_touched) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_buy_order_was_touched"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_buy_order_was_touched)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_buy_order_was_touched"] = datetime.datetime.fromtimestamp(
                0)
    except:
        traceback.print_exc()
    df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached = pd.concat(
        [df_with_level_atr_bpu_bsu_etc, df_with_tp_x_to_one_its_timestamp_and_datetime], axis=1)
    print("df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached3")
    print(df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached.to_string())
    return df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached

def add_to_df_result_of_return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached(level_price,
                        advanced_atr,
        df_with_level_atr_bpu_bsu_etc,
        index_in_iteration,
        entire_original_table_with_ohlcv_data_df,
        side,
        buy_order,
        take_profit_when_sl_is_calculated_3_to_1,
        calculated_stop_loss):

    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()

    try:
        # add statistical info to df if calculated sl and tp have been reached
        max_distance_from_level_price_in_this_bar_in_atr,\
            take_profit_when_sl_is_calculated_3_to_1_is_reached, \
            calculated_stop_loss_is_reached, \
            daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
            timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached, \
            timestamp_when_calculated_stop_loss_was_reached, \
            buy_order_was_touched, \
            timestamp_when_buy_order_was_touched, \
            first_bar_after_bfr_opened_lower_than_buy_order,\
            df_with_tp_x_to_one_its_timestamp_and_datetime = return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached(level_price,
                        advanced_atr,
            index_in_iteration,
            entire_original_table_with_ohlcv_data_df, side,
            buy_order,
            take_profit_when_sl_is_calculated_3_to_1,
            calculated_stop_loss)

        if df_with_tp_x_to_one_its_timestamp_and_datetime.empty:
            type_of_stop_loss = "calculated"
            min_profit_target_multiple_in_range_func = 4
            max_profit_target_multiple_in_range_func = 100
            df_with_tp_x_to_one_its_timestamp_and_datetime = generate_placeholder_df_with_default_values_with_max_profit_target_equal_to_zero_and_tp_4_to_100(
                type_of_stop_loss,
                min_profit_target_multiple_in_range_func,
                max_profit_target_multiple_in_range_func)


        print("calculated_sl_df_with_tp_x_to_one_its_timestamp_and_datetime123_buy_order")
        print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())

        df_with_level_atr_bpu_bsu_etc.at[0, "daily_data_not_enough_to_get_whether_tp_or_sl_was_reached_first"] = daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first
        df_with_level_atr_bpu_bsu_etc.at[0, "first_bar_after_bfr_opened_lower_than_buy_order"] = first_bar_after_bfr_opened_lower_than_buy_order


        df_with_level_atr_bpu_bsu_etc.at[0, "take_profit_when_sl_is_calculated_3_to_1_is_reached"] = take_profit_when_sl_is_calculated_3_to_1_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached
        if pd.isna(timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"] = datetime.datetime.fromtimestamp(
                0)


        df_with_level_atr_bpu_bsu_etc.at[0, "calculated_stop_loss_is_reached"] = calculated_stop_loss_is_reached
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_calculated_stop_loss_was_reached"] = timestamp_when_calculated_stop_loss_was_reached
        if pd.isna(timestamp_when_calculated_stop_loss_was_reached) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_calculated_stop_loss_was_reached"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_calculated_stop_loss_was_reached)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_calculated_stop_loss_was_reached"] = datetime.datetime.fromtimestamp(
                0)

        df_with_level_atr_bpu_bsu_etc.at[0, "buy_order_was_touched"] = buy_order_was_touched
        df_with_level_atr_bpu_bsu_etc.at[
            0, "max_distance_from_level_price_in_this_bar_in_atr"] = max_distance_from_level_price_in_this_bar_in_atr
        df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_when_buy_order_was_touched"] = timestamp_when_buy_order_was_touched
        if pd.isna(timestamp_when_buy_order_was_touched) == False:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_buy_order_was_touched"] = \
                datetime.datetime.fromtimestamp(
                    timestamp_when_buy_order_was_touched)
        else:
            df_with_level_atr_bpu_bsu_etc.at[0, "datetime_when_buy_order_was_touched"] = datetime.datetime.fromtimestamp(
                0)
    except:
        traceback.print_exc()

    df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached = pd.concat(
        [df_with_level_atr_bpu_bsu_etc, df_with_tp_x_to_one_its_timestamp_and_datetime], axis=1)
    print("df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached4")
    print(df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached.to_string())
    return df_with_level_atr_bpu_bsu_etc_plus_info_about_whether_tp_mre_than_three_was_reached
# def split_and_remove_letters(string_with_letters):
#     # Split the list on "_"
#     split_lst = string_with_letters.split("_")
#
#     # Remove elements that contain letters
#     split_lst_without_letters = [elem for elem in split_lst if not any(char.isalpha() for char in elem)]
#
#     return split_lst_without_letters

# def split_and_remove_letters(string_with_letters):
#     # Split the list on "_"
#     split_lst = string_with_letters.split("_")
#
#     # Remove elements that contain letters
#     split_lst_without_letters = [elem for elem in split_lst if not (any(char.isalpha() for char in elem) and not (len(elem)==1 and elem=="e"))]
#
#     return split_lst_without_letters
def return_bool_whether_calculated_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,i,
                                                                         entire_original_table_with_ohlcv_data_df,
                                                                         side,
                                                                         sell_order,
                                                                         take_profit_when_sl_is_calculated_3_to_1,
                                                                         calculated_stop_loss):
    ####################################################
    ####################################################
    ####################################################
    # iterate over each row in a slice from the original table to understand if sl or tp were achieved first

    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = i
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]

    open_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
    high_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
    low_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
    close_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
    volume_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
    timestamp_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

    take_profit_when_sl_is_calculated_3_to_1_is_reached = False
    calculated_stop_loss_is_reached = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = False
    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = np.nan
    timestamp_when_calculated_stop_loss_was_reached = np.nan
    sell_order_was_touched=False
    timestamp_when_sell_order_was_touched=np.nan
    first_bar_after_bfr_opened_lower_than_sell_order = False
    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached = np.nan
    max_distance_from_level_price_in_this_bar_in_atr = 0.0

    for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
            range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                  len(entire_original_table_with_ohlcv_data_df)):
        open_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
        high_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
        low_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
        close_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
        volume_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
        timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

        # check if sell order was touched before sl or tp
        if sell_order_was_touched == False:

            #check if price has ever moved away from level price for more than 2 atr
            max_distance_from_level_price_in_this_bar=\
                max(abs(level_price-high_of_bar_in_each_iteration_beginning_with_first_bar),
                    abs(level_price-low_of_bar_in_each_iteration_beginning_with_first_bar))
            max_distance_from_level_price_in_this_bar_in_atr=float(max_distance_from_level_price_in_this_bar)/float(advanced_atr)
            # if max_distance_from_level_price_in_this_bar_in_atr>2:
            #     max_distance_from_level_price_in_this_bar_in_atr=True

            if high_of_bar_in_each_iteration_beginning_with_first_bar >= sell_order >= low_of_bar_in_each_iteration_beginning_with_first_bar:
                sell_order_was_touched = True
                timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

        if side == "sell":
            if open_of_first_bar_after_bfr_has_formed > sell_order:
                # after bfr forming the bar opened higher than sell order
                first_bar_after_bfr_opened_lower_than_sell_order = False
                if low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < calculated_stop_loss:
                    # current price in iteration is between calculated sl and tp 3 to 1
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True

                    continue
                elif low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has not
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_calculated_sl_or_sell_order_was_reached_first = True
                    calculated_stop_loss_is_reached = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < calculated_stop_loss:
                    # take_profit_when_sl_is_calculated_3_to_1 is reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has been reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    calculated_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case1")
                    continue
            else:
                # after bfr forming the bar opened lower than sell order
                first_bar_after_bfr_opened_lower_than_sell_order = True
                if low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < calculated_stop_loss:
                    # current price in iteration is between calculated sl and tp 3 to 1
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True

                    continue
                elif low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has not
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_calculated_sl_or_sell_order_was_reached_first = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    calculated_stop_loss_is_reached = True
                    break
                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < calculated_stop_loss:
                    # take_profit_when_sl_is_calculated_3_to_1 is reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = True
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_calculated_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has been reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    calculated_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case2")
                    continue
        else:
            print(f"side={side} is incorrect. Use another function")

    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()
    try:
        if pd.isna(index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached) == False:
            type_of_stop_loss="calculated"
            df_with_tp_x_to_one_its_timestamp_and_datetime=check_which_tp_were_also_achieved_when_order_is_sell(calculated_stop_loss,
                                                                sell_order, type_of_stop_loss,
                                                                entire_original_table_with_ohlcv_data_df,
                                                                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached)
            print("df_with_tp_x_to_one_its_timestamp_and_datetime012345")
            print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())
    except:
        traceback.print_exc()
    return max_distance_from_level_price_in_this_bar_in_atr,\
        take_profit_when_sl_is_calculated_3_to_1_is_reached, \
        calculated_stop_loss_is_reached, \
        daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
        timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached, \
        timestamp_when_calculated_stop_loss_was_reached, \
        sell_order_was_touched, \
        timestamp_when_sell_order_was_touched,\
        first_bar_after_bfr_opened_lower_than_sell_order,\
        df_with_tp_x_to_one_its_timestamp_and_datetime

    ##############################################
    ##############################################
    ##############################################
def return_bool_whether_calculated_sl_tp_and_buy_order_have_been_reached(level_price,
                        advanced_atr,i,
                                                                         entire_original_table_with_ohlcv_data_df,

                                                                         side,
                                                                         buy_order,
                                                                         take_profit_when_sl_is_calculated_3_to_1,
                                                                         calculated_stop_loss):
    ####################################################
    ####################################################
    ####################################################
    # iterate over each row in a slice from the original table to understand if sl or tp were achieved first


    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = i
    print("first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached")
    print(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached)
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]

    print('df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.index')
    print(df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.index)

    # df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = entire_original_table_with_ohlcv_data_df.copy()

    open_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
    high_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
    low_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
    close_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
    volume_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
    timestamp_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

    take_profit_when_sl_is_calculated_3_to_1_is_reached = False
    calculated_stop_loss_is_reached = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = False
    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = np.nan
    timestamp_when_calculated_stop_loss_was_reached = np.nan
    buy_order_was_touched=False
    timestamp_when_buy_order_was_touched=np.nan
    first_bar_after_bfr_opened_lower_than_buy_order=False
    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached = np.nan
    max_distance_from_level_price_in_this_bar_in_atr = 0.0
    for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
            range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                  len(entire_original_table_with_ohlcv_data_df)):
        open_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
        high_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
        low_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
        close_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
        volume_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
        timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

        # caluculation when the side is BUY

        # check if buy order was touched before sl or tp
        if buy_order_was_touched == False:


            # check if price has ever moved away from level price for more than 2 atr
            max_distance_from_level_price_in_this_bar = \
                max(abs(level_price - high_of_bar_in_each_iteration_beginning_with_first_bar),
                    abs(level_price - low_of_bar_in_each_iteration_beginning_with_first_bar))
            max_distance_from_level_price_in_this_bar_in_atr = float(max_distance_from_level_price_in_this_bar) / float(
                advanced_atr)
            # if max_distance_from_level_price_in_this_bar_in_atr > 2:
            #     max_distance_from_level_price_in_this_bar_in_atr = True


            if high_of_bar_in_each_iteration_beginning_with_first_bar >= buy_order >= low_of_bar_in_each_iteration_beginning_with_first_bar:
                buy_order_was_touched = True
                timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

        if side == "buy":
            if open_of_first_bar_after_bfr_has_formed < buy_order:
                # after bfr forming the bar opened lower than buy order
                first_bar_after_bfr_opened_lower_than_buy_order = True



                if high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > calculated_stop_loss:
                    # current price in iteration is between calculated sl and tp 3 to 1
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True

                    continue
                elif high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has not
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_calculated_sl_or_buy_order_was_reached_first = True
                    calculated_stop_loss_is_reached = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > calculated_stop_loss:
                    # take_profit_when_sl_is_calculated_3_to_1 is reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached=\
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has been reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    calculated_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case3")
                    continue
            else:
                # after bfr forming the bar opened higher than buy order
                first_bar_after_bfr_opened_lower_than_buy_order = False
                if high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > calculated_stop_loss:
                    # current price in iteration is between calculated sl and tp 3 to 1
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True

                    continue
                elif high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has not
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     daily_data_is_not_enough_to_determine_whether_calculated_sl_or_buy_order_was_reached_first = True
                    #     buy_order_was_touched = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    calculated_stop_loss_is_reached = True
                    break
                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > calculated_stop_loss:
                    # take_profit_when_sl_is_calculated_3_to_1 is reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first = True
                    #     buy_order_was_touched = True
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_calculated_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= calculated_stop_loss:
                    # calculated stop loss has been reached and tp 3 to 1 has been reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    take_profit_when_sl_is_calculated_3_to_1_is_reached = True
                    calculated_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_calculated_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break

                else:
                    print("unknown case4")
                    continue


        else:
            print(f"side={side} is incorrect. Use another function")

    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()
    try:
        if pd.isna(index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached) == False:
            type_of_stop_loss="calculated"
            df_with_tp_x_to_one_its_timestamp_and_datetime=check_which_tp_were_also_achieved_when_order_is_buy(calculated_stop_loss,
                                                                buy_order, type_of_stop_loss,
                                                                entire_original_table_with_ohlcv_data_df,
                                                                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_calculated_tp_3_to_1_was_reached)
            print("df_with_tp_x_to_one_its_timestamp_and_datetime2")
            print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())
    except:
        traceback.print_exc()
    return max_distance_from_level_price_in_this_bar_in_atr,\
        take_profit_when_sl_is_calculated_3_to_1_is_reached,\
        calculated_stop_loss_is_reached,\
        daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first,\
        timestamp_when_take_profit_when_sl_is_calculated_3_to_1_was_reached,\
        timestamp_when_calculated_stop_loss_was_reached,\
        buy_order_was_touched,\
        timestamp_when_buy_order_was_touched,\
        first_bar_after_bfr_opened_lower_than_buy_order,\
        df_with_tp_x_to_one_its_timestamp_and_datetime

    ##############################################
    ##############################################
    ##############################################


def return_bool_whether_technical_sl_tp_and_sell_order_have_been_reached(level_price,
                        advanced_atr,i,
                                                                          entire_original_table_with_ohlcv_data_df,
                                                                          side,
                                                                          sell_order,
                                                                          take_profit_when_sl_is_technical_3_to_1,
                                                                          technical_stop_loss):
    ####################################################
    ####################################################
    ####################################################
    # iterate over each row in a slice from the original table to understand if sl or tp were achieved first


    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = i
    print("first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached23")
    print(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached)
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]


    print("entire_original_table_with_ohlcv_data_df.tail(5).to_string()")
    print(entire_original_table_with_ohlcv_data_df.tail(5).to_string())
    print("df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.tail(5).to_string()")
    print(df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.tail(5).to_string())

    open_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
    high_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
    low_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
    close_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
    volume_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
    timestamp_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]




    print("open_of_first_bar_after_bfr_has_formed")
    print(open_of_first_bar_after_bfr_has_formed)
    print("high_of_first_bar_after_bfr_has_formed")
    print(high_of_first_bar_after_bfr_has_formed)

    take_profit_when_sl_is_technical_3_to_1_is_reached = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = False
    technical_stop_loss_is_reached = False
    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = False
    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = np.nan
    timestamp_when_technical_stop_loss_was_reached = np.nan
    sell_order_was_touched = False
    timestamp_when_sell_order_was_touched = np.nan
    first_bar_after_bfr_opened_lower_than_sell_order = False
    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached = np.nan
    max_distance_from_level_price_in_this_bar_in_atr = 0.0

    for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
            range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                  len(entire_original_table_with_ohlcv_data_df)):
        open_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
        high_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
        low_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
        close_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
        volume_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
        timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

        # check if sell order was touched before sl or tp
        if sell_order_was_touched == False:

            # check if price has ever moved away from level price for more than 2 atr
            max_distance_from_level_price_in_this_bar = \
                max(abs(level_price - high_of_bar_in_each_iteration_beginning_with_first_bar),
                    abs(level_price - low_of_bar_in_each_iteration_beginning_with_first_bar))
            max_distance_from_level_price_in_this_bar_in_atr = float(max_distance_from_level_price_in_this_bar) / float(
                advanced_atr)
            # if max_distance_from_level_price_in_this_bar_in_atr > 2:
            #     max_distance_from_level_price_in_this_bar_in_atr = True

            if high_of_bar_in_each_iteration_beginning_with_first_bar >= sell_order >= low_of_bar_in_each_iteration_beginning_with_first_bar:
                sell_order_was_touched = True
                timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

        # print("********************************************")
        # print("low_of_bar_in_each_iteration_beginning_with_first_bar")
        # print(low_of_bar_in_each_iteration_beginning_with_first_bar)
        # print("timestamp_of_bar_in_each_iteration_beginning_with_first_bar")
        # print(timestamp_of_bar_in_each_iteration_beginning_with_first_bar)
        # print("datetime_of_bar_in_each_iteration_beginning_with_first_bar")
        # print(datetime.datetime.fromtimestamp(timestamp_of_bar_in_each_iteration_beginning_with_first_bar))
        # print("take_profit_when_sl_is_technical_3_to_1")
        # print(take_profit_when_sl_is_technical_3_to_1)
        # print("high_of_bar_in_each_iteration_beginning_with_first_bar")
        # print(high_of_bar_in_each_iteration_beginning_with_first_bar)
        # print("technical_stop_loss")
        # print(technical_stop_loss)
        # print("sell_order")
        # print(sell_order)
        # print("sell_order_was_touched")
        # print(sell_order_was_touched)
        # print("df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.index")
        # print(df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.index)
        # print("first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached")
        # print(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached)
        # print("index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached")
        # print(index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached)
        # print("len(entire_original_table_with_ohlcv_data_df) + 1)")
        # print(len(entire_original_table_with_ohlcv_data_df) + 1)


        if side == "sell":
            if open_of_first_bar_after_bfr_has_formed > sell_order:
                # after bfr forming the bar opened higher than sell order
                first_bar_after_bfr_opened_lower_than_sell_order = False
                if low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < technical_stop_loss:
                    # current price in iteration is between technical sl and tp 3 to 1
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True

                    continue
                elif low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has not
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_technical_sl_or_sell_order_was_reached_first = True
                    technical_stop_loss_is_reached = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < technical_stop_loss:
                    # take_profit_when_sl_is_technical_3_to_1 is reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has been reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    technical_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case5")
                    continue
            else:
                # after bfr forming the bar opened lower than sell order
                first_bar_after_bfr_opened_lower_than_sell_order = True
                if low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < technical_stop_loss:
                    # current price in iteration is between technical sl and tp 3 to 1
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True

                    continue
                elif low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has not
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_technical_sl_or_sell_order_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    technical_stop_loss_is_reached = True
                    break
                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar < technical_stop_loss:
                    # take_profit_when_sl_is_technical_3_to_1 is reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = True
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_when_sl_is_technical_3_to_1 \
                        and high_of_bar_in_each_iteration_beginning_with_first_bar >= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has been reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < sell_order:
                    #     sell_order_was_touched = False
                    # else:
                    #     timestamp_when_sell_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     sell_order_was_touched = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    technical_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case6")
                    print("low_of_bar_in_each_iteration_beginning_with_first_bar")
                    print(low_of_bar_in_each_iteration_beginning_with_first_bar)
                    print("timestamp_of_bar_in_each_iteration_beginning_with_first_bar")
                    print(timestamp_of_bar_in_each_iteration_beginning_with_first_bar)
                    print("datetime_of_bar_in_each_iteration_beginning_with_first_bar")
                    print(datetime.datetime.fromtimestamp(timestamp_of_bar_in_each_iteration_beginning_with_first_bar))
                    print("take_profit_when_sl_is_technical_3_to_1")
                    print(take_profit_when_sl_is_technical_3_to_1)
                    print("high_of_bar_in_each_iteration_beginning_with_first_bar")
                    print(high_of_bar_in_each_iteration_beginning_with_first_bar)
                    print("technical_stop_loss")
                    print(technical_stop_loss)
                    print("sell_order")
                    print(sell_order)
                    continue
        else:
            print(f"side={side} is incorrect. Use another function")

    df_with_tp_x_to_one_its_timestamp_and_datetime=pd.DataFrame()
    try:
        if pd.isna(index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached) == False:
            type_of_stop_loss="technical"
            df_with_tp_x_to_one_its_timestamp_and_datetime=check_which_tp_were_also_achieved_when_order_is_sell(technical_stop_loss,
                                                                sell_order, type_of_stop_loss,
                                                                entire_original_table_with_ohlcv_data_df,
                                                                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached)
            print("df_with_tp_x_to_one_its_timestamp_and_datetime3")
            print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())
    except:
        traceback.print_exc()
    return max_distance_from_level_price_in_this_bar_in_atr,\
        take_profit_when_sl_is_technical_3_to_1_is_reached, \
        technical_stop_loss_is_reached, \
        daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
        timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached, \
        timestamp_when_technical_stop_loss_was_reached, \
        sell_order_was_touched, \
        timestamp_when_sell_order_was_touched,\
        first_bar_after_bfr_opened_lower_than_sell_order,\
        df_with_tp_x_to_one_its_timestamp_and_datetime

    ##############################################
    ##############################################
    ##############################################


def return_bool_whether_technical_sl_tp_and_buy_order_have_been_reached(level_price,
                        advanced_atr,i,
                                                                         entire_original_table_with_ohlcv_data_df,
                                                                         side,
                                                                         buy_order,
                                                                         take_profit_when_sl_is_technical_3_to_1,
                                                                         technical_stop_loss):
    ####################################################
    ####################################################
    ####################################################
    # iterate over each row in a slice from the original table to understand if sl or tp were achieved first

    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = i
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]

    print("first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached1")
    print(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached)

    open_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
    high_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
    low_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
    close_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
    volume_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
    timestamp_of_first_bar_after_bfr_has_formed = \
        df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
            first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

    print("open_of_first_bar_after_bfr_has_formed")
    print(open_of_first_bar_after_bfr_has_formed)
    print("high_of_first_bar_after_bfr_has_formed")
    print(high_of_first_bar_after_bfr_has_formed)

    take_profit_when_sl_is_technical_3_to_1_is_reached = False
    technical_stop_loss_is_reached = False

    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first=False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_buy_order_was_reached_first=False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_calculated_3_to_1_or_sell_order_was_reached_first = False
    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = False
    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = np.nan
    timestamp_when_technical_stop_loss_was_reached = np.nan
    buy_order_was_touched = False
    timestamp_when_buy_order_was_touched = np.nan
    first_bar_after_bfr_opened_lower_than_buy_order = False
    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached=np.nan
    max_distance_from_level_price_in_this_bar_in_atr = 0.0

    for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
            range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                  len(entire_original_table_with_ohlcv_data_df)):
        open_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
        high_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
        low_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
        close_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
        volume_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
        timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
            df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

        print("open_of_bar_in_each_iteration_beginning_with_first_bar")
        print(open_of_bar_in_each_iteration_beginning_with_first_bar)

        # calculation when the side is BUY

        # check if buy order was touched before sl or tp
        if buy_order_was_touched == False:

            # check if price has ever moved away from level price for more than 2 atr
            max_distance_from_level_price_in_this_bar = \
                max(abs(level_price - high_of_bar_in_each_iteration_beginning_with_first_bar),
                    abs(level_price - low_of_bar_in_each_iteration_beginning_with_first_bar))
            max_distance_from_level_price_in_this_bar_in_atr = float(max_distance_from_level_price_in_this_bar) / float(
                advanced_atr)
            # if max_distance_from_level_price_in_this_bar_in_atr > 2:
            #     max_distance_from_level_price_in_this_bar_in_atr = True

            if high_of_bar_in_each_iteration_beginning_with_first_bar >= buy_order >= low_of_bar_in_each_iteration_beginning_with_first_bar:
                buy_order_was_touched = True
                timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

        if side == "buy":
            if open_of_first_bar_after_bfr_has_formed < buy_order:
                # after bfr forming the bar opened lower than buy order
                first_bar_after_bfr_opened_lower_than_buy_order = True



                if high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > technical_stop_loss:
                    # current price in iteration is between technical sl and tp 3 to 1

                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True

                    continue
                elif high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has not

                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_technical_sl_or_buy_order_was_reached_first = True
                    technical_stop_loss_is_reached = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > technical_stop_loss:
                    # take_profit_when_sl_is_technical_3_to_1 is reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has been reached
                    # if high_of_bar_in_each_iteration_beginning_with_first_bar < buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    technical_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case7")
                    continue
            else:
                # after bfr forming the bar opened higher than buy order
                first_bar_after_bfr_opened_lower_than_buy_order = False

                # # check if buy order was touched before sl or tp
                # if buy_order_was_touched == False:
                #     if high_of_bar_in_each_iteration_beginning_with_first_bar >= buy_order >= low_of_bar_in_each_iteration_beginning_with_first_bar:
                #         buy_order_was_touched = True
                #         timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

                if high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > technical_stop_loss:
                    # current price in iteration is between technical sl and tp 3 to 1
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True

                    continue
                elif high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has not
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_technical_sl_or_buy_order_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    technical_stop_loss_is_reached = True
                    break
                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar > technical_stop_loss:
                    # take_profit_when_sl_is_technical_3_to_1 is reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    #     daily_data_is_not_enough_to_determine_whether_take_profit_when_sl_is_technical_3_to_1_or_buy_order_was_reached_first = True
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached = \
                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached
                    break

                elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_when_sl_is_technical_3_to_1 \
                        and low_of_bar_in_each_iteration_beginning_with_first_bar <= technical_stop_loss:
                    # technical stop loss has been reached and tp 3 to 1 has been reached
                    # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                    #     buy_order_was_touched = False
                    # else:
                    #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    #     buy_order_was_touched = True
                    take_profit_when_sl_is_technical_3_to_1_is_reached = True
                    technical_stop_loss_is_reached = True
                    daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                    timestamp_when_technical_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                    break
                else:
                    print("unknown case8")
                    continue


        else:
            print(f"side={side} is incorrect. Use another function")

    df_with_tp_x_to_one_its_timestamp_and_datetime = pd.DataFrame()
    try:
        if pd.isna(index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached) == False:
            type_of_stop_loss="technical"
            df_with_tp_x_to_one_its_timestamp_and_datetime=check_which_tp_were_also_achieved_when_order_is_buy(technical_stop_loss,
                                                                buy_order, type_of_stop_loss,
                                                                entire_original_table_with_ohlcv_data_df,
                                                                index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_technical_tp_3_to_1_was_reached)
            print("df_with_tp_x_to_one_its_timestamp_and_datetime4 order buy type of sl technical")
            print(df_with_tp_x_to_one_its_timestamp_and_datetime.to_string())

    except:
        traceback.print_exc()

    return max_distance_from_level_price_in_this_bar_in_atr,\
        take_profit_when_sl_is_technical_3_to_1_is_reached, \
        technical_stop_loss_is_reached, \
        daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first, \
        timestamp_when_take_profit_when_sl_is_technical_3_to_1_was_reached, \
        timestamp_when_technical_stop_loss_was_reached, \
        buy_order_was_touched, \
        timestamp_when_buy_order_was_touched,\
        first_bar_after_bfr_opened_lower_than_buy_order,\
        df_with_tp_x_to_one_its_timestamp_and_datetime

    ##############################################
    ##############################################
    ##############################################
def check_which_tp_were_also_achieved_when_order_is_sell(stop_loss,
                                                        sell_order,
                                                        type_of_stop_loss,
                                                        entire_original_table_with_ohlcv_data_df,
                                                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_tp_3_to_1_was_reached):
    distance_between_stop_loss_and_sell_order = stop_loss - sell_order
    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached=\
        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_tp_3_to_1_was_reached
    # take_profit_when_sl_is_technical_3_to_1 = (buy_order - stop_loss) * 3 + buy_order
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]
    stop_loss_is_reached=False
    max_profit_target_multiple=3
    timestamp_when_max_take_profit_was_reached=0
    datetime_when_max_take_profit_was_reached=datetime.datetime.fromtimestamp(0)
    min_profit_target_multiple_in_range_func = 4
    max_profit_target_multiple_in_range_func = 100
    df_with_tp_x_to_one_its_timestamp_and_datetime = \
        generate_df_with_default_values_with_max_profit_target_and_tp_4_to_100(type_of_stop_loss,
                                                                              min_profit_target_multiple_in_range_func,
                                                                              max_profit_target_multiple_in_range_func)
    for profit_target_multiple in range(4,max_profit_target_multiple_in_range_func +1,1):
        if stop_loss_is_reached==True:
            break
        take_profit_is_x_to_one_is_reached= False
        take_profit_x_to_one = sell_order - (stop_loss - sell_order) * profit_target_multiple
        for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
                range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                      len(entire_original_table_with_ohlcv_data_df)):
            open_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
            high_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
            low_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
            close_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
            volume_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
            timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

            if low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_x_to_one \
                    and high_of_bar_in_each_iteration_beginning_with_first_bar <stop_loss:
                # current price in iteration is between take_profit_is_x_to_one and sl


                continue
            elif low_of_bar_in_each_iteration_beginning_with_first_bar > take_profit_x_to_one \
                    and high_of_bar_in_each_iteration_beginning_with_first_bar >=  stop_loss:
                # stop loss has been reached and tp 3 to 1 has not

                timestamp_when_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                stop_loss_is_reached = True

                break
            elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_x_to_one \
                    and high_of_bar_in_each_iteration_beginning_with_first_bar < stop_loss:
                # take_profit_is_x_to_one is reached

                timestamp_when_take_profit_is_x_to_one_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                take_profit_is_x_to_one_is_reached = True
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                    0, f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"] = take_profit_is_x_to_one_is_reached
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                    0, f"take_profit_{profit_target_multiple}_to_one_sl_{type_of_stop_loss}"] = take_profit_x_to_one
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                    0, f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"] = timestamp_when_take_profit_is_x_to_one_was_reached
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[
                    0, f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"] = \
                    datetime.datetime.fromtimestamp(timestamp_when_take_profit_is_x_to_one_was_reached)
                max_profit_target_multiple = profit_target_multiple
                break

            elif low_of_bar_in_each_iteration_beginning_with_first_bar <= take_profit_x_to_one \
                    and high_of_bar_in_each_iteration_beginning_with_first_bar >= stop_loss:
                # stop loss has been reached and tp 3 to 1 has been reached

                take_profit_is_x_to_one_is_reached = True
                stop_loss_is_reached = True
                daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                timestamp_when_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                timestamp_when_take_profit_is_x_to_one_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                break
            else:
                print("unknown case8")
                continue
    df_with_tp_x_to_one_its_timestamp_and_datetime.at[
        0, f"max_profit_target_multiple_when_sl_{type_of_stop_loss}"] = max_profit_target_multiple

    return df_with_tp_x_to_one_its_timestamp_and_datetime
def check_which_tp_were_also_achieved_when_order_is_buy(stop_loss,
                                                        buy_order,
                                                        type_of_stop_loss,
                                                        entire_original_table_with_ohlcv_data_df,
                                                        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_tp_3_to_1_was_reached):
    distance_between_stop_loss_and_buy_order = buy_order - stop_loss
    first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached=\
        index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached_when_tp_3_to_1_was_reached
    # take_profit_when_sl_is_technical_3_to_1 = (buy_order - stop_loss) * 3 + buy_order
    df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached = \
        entire_original_table_with_ohlcv_data_df.iloc[
        first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached:len(
            entire_original_table_with_ohlcv_data_df) + 1]
    stop_loss_is_reached=False
    max_profit_target_multiple=3
    timestamp_when_max_take_profit_was_reached=0
    datetime_when_max_take_profit_was_reached=datetime.datetime.fromtimestamp(0)
    timestamp_when_take_profit_is_x_to_one_was_reached=0
    min_profit_target_multiple_in_range_func=4
    max_profit_target_multiple_in_range_func=100
    df_with_tp_x_to_one_its_timestamp_and_datetime=\
        generate_df_with_default_values_with_max_profit_target_and_tp_4_to_100(type_of_stop_loss,
                                                                          min_profit_target_multiple_in_range_func,
                                                                          max_profit_target_multiple_in_range_func)


    for profit_target_multiple in range(min_profit_target_multiple_in_range_func,max_profit_target_multiple_in_range_func+1,1):
        if stop_loss_is_reached==True:
            break
        take_profit_is_x_to_one_is_reached= False
        take_profit_x_to_one=(buy_order - stop_loss) * profit_target_multiple + buy_order
        for index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached in \
                range(first_index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached,
                      len(entire_original_table_with_ohlcv_data_df)):
            open_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "open"]
            high_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "high"]
            low_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "low"]
            close_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "close"]
            volume_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "volume"]
            timestamp_of_bar_in_each_iteration_beginning_with_first_bar = \
                df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached.at[
                    index_in_df_ohlcv_slice_where_we_need_to_check_if_sl_tp_were_reached, "Timestamp"]

            if high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_x_to_one \
                    and low_of_bar_in_each_iteration_beginning_with_first_bar > stop_loss:
                # current price in iteration is between take_profit_is_x_to_onesl and tp 3 to 1
                # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                #     buy_order_was_touched = False
                # else:
                #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                #     buy_order_was_touched = True

                continue
            elif high_of_bar_in_each_iteration_beginning_with_first_bar < take_profit_x_to_one \
                    and low_of_bar_in_each_iteration_beginning_with_first_bar <= stop_loss:
                # stop loss has been reached and tp 3 to 1 has not
                # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                #     buy_order_was_touched = False
                # else:
                #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                #     buy_order_was_touched = True
                #     daily_data_is_not_enough_to_determine_whether_technical_sl_or_buy_order_was_reached_first = True
                timestamp_when_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                stop_loss_is_reached = True

                break
            elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_x_to_one \
                    and low_of_bar_in_each_iteration_beginning_with_first_bar > stop_loss:
                # take_profit_is_x_to_one is reached
                # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                #     buy_order_was_touched = False
                # else:
                #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                #     buy_order_was_touched = True
                #     daily_data_is_not_enough_to_determine_whether_take_profit_is_x_to_one_or_buy_order_was_reached_first = True
                timestamp_when_take_profit_is_x_to_one_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

                take_profit_is_x_to_one_is_reached = True
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[0,f"take_profit_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"]=take_profit_is_x_to_one_is_reached
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[0,f"take_profit_{profit_target_multiple}_to_one_sl_{type_of_stop_loss}"]=take_profit_x_to_one
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[0,f"timestamp_of_tp_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"]=timestamp_when_take_profit_is_x_to_one_was_reached
                df_with_tp_x_to_one_its_timestamp_and_datetime.at[0,f"datetime_of_tp_{profit_target_multiple}_to_one_is_reached_sl_{type_of_stop_loss}"]=\
                    datetime.datetime.fromtimestamp(timestamp_when_take_profit_is_x_to_one_was_reached)
                max_profit_target_multiple = profit_target_multiple
                break

            elif high_of_bar_in_each_iteration_beginning_with_first_bar >= take_profit_x_to_one \
                    and low_of_bar_in_each_iteration_beginning_with_first_bar <= stop_loss:
                # stop loss has been reached and tp 3 to 1 has been reached
                # if low_of_bar_in_each_iteration_beginning_with_first_bar > buy_order:
                #     buy_order_was_touched = False
                # else:
                #     timestamp_when_buy_order_was_touched = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                #     buy_order_was_touched = True
                take_profit_is_x_to_one_is_reached = True
                stop_loss_is_reached = True
                daily_data_is_not_enough_to_determine_whether_tp_or_sl_was_reached_first = True
                timestamp_when_stop_loss_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar
                timestamp_when_take_profit_is_x_to_one_was_reached = timestamp_of_bar_in_each_iteration_beginning_with_first_bar

                break
            else:
                print("unknown case8")
                continue
    # timestamp_when_max_take_profit_was_reached=timestamp_when_take_profit_is_x_to_one_was_reached
    # datetime_when_max_take_profit_was_reached=datetime.datetime.fromtimestamp(timestamp_when_max_take_profit_was_reached)
    df_with_tp_x_to_one_its_timestamp_and_datetime.at[
        0, f"max_profit_target_multiple_when_sl_{type_of_stop_loss}"] = max_profit_target_multiple

    return df_with_tp_x_to_one_its_timestamp_and_datetime



def return_exchange_ids_names_and_number_of_exchanges_where_crypto_is_traded(df_with_strings_of_exchanges_where_pair_is_traded,stock_name):
    # get base of trading pair
    base = get_base_of_trading_pair(trading_pair=stock_name)
    quote = get_quote_of_trading_pair(trading_pair=stock_name)
    base_slash_quote = base + "/" + quote
    #########################################################
    # find row where base is equal to base from df_with_strings_of_exchanges_where_pair_is_traded
    exchange_id_string_where_trading_pair_is_traded = ""
    exchange_names_string_where_trading_pair_is_traded = ""
    number_of_exchanges_where_pair_is_traded_on = np.nan
    try:

        exchange_id_string_where_trading_pair_is_traded = \
            df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "exchanges_where_pair_is_traded"]
        exchange_names_string_where_trading_pair_is_traded = \
            df_with_strings_of_exchanges_where_pair_is_traded.loc[
                base_slash_quote, "unique_exchanges_where_pair_is_traded"]
        number_of_exchanges_where_pair_is_traded_on = \
            df_with_strings_of_exchanges_where_pair_is_traded.loc[
                base_slash_quote, "number_of_exchanges_where_pair_is_traded_on"]


    except:
        traceback.print_exc()

    return exchange_id_string_where_trading_pair_is_traded,\
        exchange_names_string_where_trading_pair_is_traded,\
        number_of_exchanges_where_pair_is_traded_on
def split_and_remove_letters(string_with_letters):
    # Split the list on "_"
    split_lst = string_with_letters.split("_")

    # Remove elements that contain letters
    split_lst_without_letters = [elem for elem in split_lst if not (any(char.isalpha() for char in elem) and not ("e-" in elem))]

    return split_lst_without_letters

def convert_to_string(lst):
    return [str(x) for x in lst]
def remove_all_on(values_and_exchanges):
    return [value for value in values_and_exchanges if value != "on"]
def remove_outliers_from_string(string, outliers):
    # Split the string into a list of values and exchanges
    values_and_exchanges = string.split('_')
    values_and_exchanges=remove_all_on(values_and_exchanges)
    outliers=convert_to_string(outliers)

    print("values_and_exchanges")
    print(values_and_exchanges)
    # Initialize a list to store the removed exchange names
    removed_exchanges = []

    # Remove outliers and associated exchanges from the list
    for outlier in outliers:
        if outlier in values_and_exchanges:
            index = values_and_exchanges.index(outlier)
            print(f"index of {outlier}")
            print(index)
            exchange = values_and_exchanges[index + 1]
            popped_out_exchange=values_and_exchanges.pop(index + 1)
            print("popped_out_exchange")
            print(popped_out_exchange)
            popped_out_last_close_price=values_and_exchanges.pop(index)
            print("popped_out_last_close_price")
            print(popped_out_last_close_price)

            removed_exchanges.append(exchange)

    # Join the remaining values and exchanges into a string
    modified_string = '_'.join(values_and_exchanges)

    # Return the modified string and the list of removed exchange names
    return (modified_string, removed_exchanges)


def remove_outliers_from_string_some_value_plus_exchange(string, outlier_exchanges):
    # Split the string into a list of values and exchanges
    values_and_exchanges = string.split('_')
    values_and_exchanges=remove_all_on(values_and_exchanges)
    # outliers=convert_to_string(outliers)

    print("values_and_exchanges")
    print(values_and_exchanges)
    # Initialize a list to store the removed exchange names
    removed_exchanges = []

    # Remove outliers and associated exchanges from the list
    for outlier_exchange in outlier_exchanges:
        if outlier_exchange in values_and_exchanges:
            index = values_and_exchanges.index(outlier_exchange)
            print(f"index of {outlier_exchange}")
            print(index)
            exchange = values_and_exchanges[index]
            popped_out_exchange = values_and_exchanges.pop(index)
            print("popped_out_exchange")
            print(popped_out_exchange)

            popped_out_value_before_exchange=values_and_exchanges.pop(index - 1)
            print("popped_out_value_before_exchange")
            print(popped_out_value_before_exchange)


            removed_exchanges.append(exchange)

    # Join the remaining values and exchanges into a string
    modified_string = '_'.join(values_and_exchanges)

    # Return the modified string and the list of removed exchange names
    return (modified_string, removed_exchanges)
def remove_outliers_return_excluded_and_included_values(lst):
    # Calculate median
    median = float(sum(lst))/len(lst)
    # Calculate absolute elements
    absolute_deviation = [abs(x - median) for x in lst]
    median_absolute_deviation = float(sum(absolute_deviation))/len(absolute_deviation)
    # calculate modified z-score
    modified_z_scores = [0.6745 * (x - median) / median_absolute_deviation
                       for x in lst]
    modified_z_scores = [abs(z_score) for z_score in modified_z_scores]
    # Calculate max threshold
    max_threshold = 3
    excluded_outliers = [x for (x, m, le) in
                       zip(lst, modified_z_scores, absolute_deviation)
                       if m > max_threshold or le > median*1.3]
    # Remove outliers
    included_in_list = [x for x in lst if x not in excluded_outliers]
    return excluded_outliers,included_in_list
def remove_outliers(lst):
    # Calculate median
    median = float(sum(lst))/len(lst)
    # Calculate absolute elements
    absolute_deviation = [abs(x - median) for x in lst]
    median_absolute_deviation = float(sum(absolute_deviation))/len(absolute_deviation)
    # calculate modified z-score
    modified_z_scores = [0.6745 * (x - median) / median_absolute_deviation
                       for x in lst]
    modified_z_scores = [abs(z_score) for z_score in modified_z_scores]
    # Calculate max threshold
    max_threshold = 2
    excluded_outliers = [x for (x, m, le) in
                       zip(lst, modified_z_scores, absolute_deviation)
                       if m > max_threshold or le > median*1.3]
    # Remove outliers
    included_in_list = [x for x in lst if x not in excluded_outliers]
    return included_in_list
def generate_min_volume_ath_atl_plus_exchange_string(
        exchange_id_string_where_trading_pair_is_traded,
        stock_name):
    # add_min_volume_on_each_exchange

    string_of_number_of_available_days_from_all_exchanges=""
    string_of_number_of_available_days_from_all_exchanges_plus_exchange = ""
    string_all_volumes_by_low_on_which_exchange = ""
    string_all_atls_on_which_exchange=""
    string_all_aths_on_which_exchange=""
    string_all_atls_without_exchange = ""
    string_all_aths_without_exchange = ""
    string_of_last_close_prices_on_all_exchanges=''
    string_of_last_close_prices_on_all_exchanges_with_exchanges = ''
    string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers=''

    try:
        list_of_absolutely_all_exchange_ids_where_pair_is_traded = exchange_id_string_where_trading_pair_is_traded.split(
            "_")
        print("list_of_absolutely_all_exchange_ids_where_pair_is_traded5")
        print(list_of_absolutely_all_exchange_ids_where_pair_is_traded)
        # list_of_all_aths_from_all_exchanges = []
        list_of_all_volumes_by_low_from_all_exchanges = []
        list_of_all_atls_from_all_exchanges=[]
        list_of_all_aths_from_all_exchanges=[]
        list_of_all_aths_from_all_exchanges_without_exchange=[]
        list_of_all_atls_from_all_exchanges_without_exchange = []
        list_last_close_prices_on_all_exchanges=[]
        list_last_close_prices_on_all_exchanges_with_exchanges = []
        list_last_close_prices_on_all_exchanges_in_float=[]
        list_of_all_last_close_prices_without_outliers = []
        list_of_all_last_close_prices_only_outliers=[]
        list_exchanges_where_the_pair_is_different=[]
        list_of_number_of_available_days_from_all_exchanges=[]
        list_of_number_of_available_days_from_all_exchanges_plus_exchange=[]

        for exchange_id in list_of_absolutely_all_exchange_ids_where_pair_is_traded:
            exchange_object = get_exchange_object2(exchange_id)
            crypto_pair_name = stock_name.split("_on_")[0]
            crypto_pair_name = crypto_pair_name.replace("_", "/")
            print("crypto_pair_name4")
            print(crypto_pair_name)

            try:
                if ":" in crypto_pair_name:
                    exchange_object.load_markets()
                    if crypto_pair_name not in exchange_object.symbols:
                        print("crypto_pair_name5")
                        print(crypto_pair_name)
                        # find not swap but spot ath and ath if swap on this exchange is not traded
                        crypto_pair_name = crypto_pair_name.split(":")[0]
            except:
                traceback.print_exc()
            try:
                # atl_from_some_other_exchange = \
                #     get_all_time_low_from_some_exchange(exchange_object, crypto_pair_name)
                min_volume_over_this_many_days_in_dollars = 7

                number_of_available_days_from_one_exchange,\
                    min_volume_over_last_several_days_in_dollars,\
                    ath_in_df, atl_in_df,last_close_price = \
                    min_volume_ath_and_atl(exchange_object, crypto_pair_name, min_volume_over_this_many_days_in_dollars)

                if min_volume_over_last_several_days_in_dollars > 1:
                    min_volume_over_last_several_days_in_dollars = int(min_volume_over_last_several_days_in_dollars)

                # list_of_all_min_volumes on different_exchanges
                list_of_all_volumes_by_low_from_all_exchanges.append(
                    str(min_volume_over_last_several_days_in_dollars) + "_on_" + exchange_id)
                # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
                string_all_volumes_by_low_on_which_exchange = '_'.join(
                    [str(x) for x in list_of_all_volumes_by_low_from_all_exchanges])

                #######################################################
                list_of_number_of_available_days_from_all_exchanges_plus_exchange.append(
                    str(number_of_available_days_from_one_exchange) + "_on_" + exchange_id)
                string_of_number_of_available_days_from_all_exchanges_plus_exchange = '_'.join(
                    [str(x) for x in list_of_number_of_available_days_from_all_exchanges_plus_exchange])

                list_of_number_of_available_days_from_all_exchanges.append(
                    str(number_of_available_days_from_one_exchange))
                string_of_number_of_available_days_from_all_exchanges = '_'.join(
                    [str(x) for x in list_of_number_of_available_days_from_all_exchanges])
                #######################################################


                # list_of_all_aths_from_all_exchanges
                list_of_all_aths_from_all_exchanges.append(
                    str(ath_in_df) + "_on_" + exchange_id)
                # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
                string_all_aths_on_which_exchange = '_'.join(
                    [str(x) for x in list_of_all_aths_from_all_exchanges])

                # list_of_all_aths_from_all_exchanges without exchange
                list_of_all_aths_from_all_exchanges_without_exchange.append(
                    str(ath_in_df))
                # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
                string_all_aths_without_exchange = '_'.join(
                    [str(x) for x in list_of_all_aths_from_all_exchanges_without_exchange])

                # list_of_all_atls_from_all_exchanges
                list_of_all_atls_from_all_exchanges.append(
                    str(atl_in_df) + "_on_" + exchange_id)
                # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
                string_all_atls_on_which_exchange = '_'.join(
                    [str(x) for x in list_of_all_atls_from_all_exchanges])

                # list_of_all_atls_from_all_exchanges without exchange
                list_of_all_atls_from_all_exchanges_without_exchange.append(
                    str(atl_in_df))


                # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
                string_all_atls_without_exchange = '_'.join(
                    [str(x) for x in list_of_all_atls_from_all_exchanges_without_exchange])

                ########################################
                ######################################
                list_last_close_prices_on_all_exchanges.append(
                    str(last_close_price))

                list_last_close_prices_on_all_exchanges_in_float.append(last_close_price)

                string_of_last_close_prices_on_all_exchanges='_'.join(
                    [str(x) for x in list_last_close_prices_on_all_exchanges])

                list_last_close_prices_on_all_exchanges_with_exchanges.append(
                    str(last_close_price) + "_on_" + exchange_id)

                string_of_last_close_prices_on_all_exchanges_with_exchanges = '_'.join(
                    [str(x) for x in list_last_close_prices_on_all_exchanges_with_exchanges])



            except:
                traceback.print_exc()

        list_of_all_last_close_prices_only_outliers, \
            list_of_all_last_close_prices_without_outliers = \
            remove_outliers_return_excluded_and_included_values(
                list_last_close_prices_on_all_exchanges_in_float)

        print(f"list_last_close_prices_on_all_exchanges_in_float for {stock_name}")
        print(list_last_close_prices_on_all_exchanges_in_float)
        print(f"list_of_all_last_close_prices_without_outliers for {stock_name}")
        print(list_of_all_last_close_prices_without_outliers)
        print(f"list_of_all_last_close_prices_only_outliers for {stock_name}")
        print(list_of_all_last_close_prices_only_outliers)

        ###############################################
        string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers, \
            list_exchanges_where_the_pair_is_different = \
            remove_outliers_from_string(string_of_number_of_available_days_from_all_exchanges_plus_exchange,
                                        list_of_all_last_close_prices_only_outliers)
        list_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers = \
            split_and_remove_letters(string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers)
        string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers = '_'.join(
            [str(x) for x in list_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers])
        ###############################################

        string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers,\
            list_exchanges_where_the_pair_is_different=\
            remove_outliers_from_string(string_of_last_close_prices_on_all_exchanges_with_exchanges,
                                        list_of_all_last_close_prices_only_outliers)
        list_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers=\
            split_and_remove_letters(string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers)
        string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers = '_'.join(
            [str(x) for x in list_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers])

        print(f"string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers for {stock_name}")
        print(string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers)
        print(f"exchanges_where_the_pair_is_different for {stock_name}")
        print(list_exchanges_where_the_pair_is_different)

        string_all_volumes_by_low_on_which_exchange_without_outlier=\
            remove_outliers_from_string_some_value_plus_exchange(
                string_all_volumes_by_low_on_which_exchange, list_exchanges_where_the_pair_is_different)[0]
        list_of_all_volumes_by_low_without_exchange_without_outlier=\
            split_and_remove_letters(string_all_volumes_by_low_on_which_exchange_without_outlier)
        string_all_volumes_by_low_without_exchange_without_outlier = '_'.join(
            [str(x) for x in list_of_all_volumes_by_low_without_exchange_without_outlier])

        print(f"string_all_volumes_by_low_without_exchange_without_outlier for {stock_name}")
        print(string_all_volumes_by_low_without_exchange_without_outlier)


        print(f"string_all_volumes_by_low_on_which_exchange_without_outlier for {stock_name}")
        print(string_all_volumes_by_low_on_which_exchange_without_outlier)

        string_all_atls_on_which_exchange_without_outlier = \
            remove_outliers_from_string_some_value_plus_exchange(
                string_all_atls_on_which_exchange, list_exchanges_where_the_pair_is_different)[0]
        list_of_all_atls_without_exchange_without_outlier = \
            split_and_remove_letters(string_all_atls_on_which_exchange_without_outlier)
        string_all_atls_without_exchange_without_outlier = '_'.join(
            [str(x) for x in list_of_all_atls_without_exchange_without_outlier])

        print(f"string_all_atls_on_which_exchange_without_outlier for {stock_name}")
        print(string_all_atls_on_which_exchange_without_outlier)

        string_all_aths_on_which_exchange_without_outlier = \
            remove_outliers_from_string_some_value_plus_exchange(
                string_all_aths_on_which_exchange, list_exchanges_where_the_pair_is_different)[0]
        list_of_all_aths_without_exchange_without_outlier = \
            split_and_remove_letters(string_all_aths_on_which_exchange_without_outlier)
        string_all_aths_without_exchange_without_outlier='_'.join(
                    [str(x) for x in list_of_all_aths_without_exchange_without_outlier])

        print(f"string_all_aths_on_which_exchange_without_outlier for {stock_name}")
        print(string_all_aths_on_which_exchange_without_outlier)





        return string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers,\
            string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers,\
            string_all_volumes_by_low_on_which_exchange, \
            string_all_volumes_by_low_on_which_exchange_without_outlier, \
            string_all_volumes_by_low_without_exchange_without_outlier,\
            string_all_aths_on_which_exchange, \
            string_all_aths_without_exchange, \
            string_all_aths_on_which_exchange_without_outlier, \
            string_all_aths_without_exchange_without_outlier, \
            string_all_atls_on_which_exchange, \
            string_all_atls_without_exchange, \
            string_all_atls_on_which_exchange_without_outlier, \
            string_all_atls_without_exchange_without_outlier, \
            string_of_last_close_prices_on_all_exchanges,\
            string_of_last_close_prices_on_all_exchanges_with_exchanges, \
            string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers,\
            string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers

    except:
        traceback.print_exc()
        return string_all_volumes_by_low_on_which_exchange

database_name="ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
engine_for_db_with_todays_ohlcv1, connection_to_ohlcv_for_usdt_pairs1 = \
    connect_to_postgres_db_without_deleting_it_first(database_name)

list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db=get_list_of_tables_in_db(engine_for_db_with_todays_ohlcv1)

def min_volume_ath_and_atl(exchange_object, crypto_pair_name, min_volume_over_this_many_days_in_dollars):

    # ohclv = exchange_object.fetch_ohlcv(crypto_pair_name,"1d")
    # df = pd.DataFrame(ohclv, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
    timeframe="1d"
    limit_of_daily_candles=1000

    # database_name="ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    # engine_for_db_with_todays_ohlcv, connection_to_ohlcv_for_todays_usdt_pairs = \
    #     connect_to_postgres_db_without_deleting_it_first(database_name)

    table_with_ohlcv_table = crypto_pair_name.replace("/", "_") + "_on_" + exchange_object.id

    df=pd.DataFrame()
    if table_with_ohlcv_table in list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db:
        try:
            global engine_for_db_with_todays_ohlcv1


            df = \
                pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                                  engine_for_db_with_todays_ohlcv1)
            print("df found in ohlcv database")
        except:
            print(f"123problem with {crypto_pair_name} on {exchange_object.id}")
            traceback.print_exc()
    else:
        print(f"fetching {crypto_pair_name} on {exchange_object.id} because it is not in ohlcv db")
        df=fetch_entire_ohlcv_without_exchange_name(
            exchange_object,crypto_pair_name, timeframe,limit_of_daily_candles)

    # df_last_several_days_copy=pd.DataFrame(columns=["volume_by_low"])
    number_of_available_days_from_one_exchange=len(df)

    df_last_several_days=df.tail(min_volume_over_this_many_days_in_dollars)
    df_last_several_days_without_last_row=df_last_several_days.head(min_volume_over_this_many_days_in_dollars-1)
    df_last_several_days_copy = df_last_several_days_without_last_row.copy()
    df_last_several_days_copy["volume_by_low"]=df_last_several_days["volume"]*df_last_several_days["low"]
    min_volume_in_a_week = min(df_last_several_days_copy["volume_by_low"])

    ath_in_df = max(df["high"])
    atl_in_df = min(df["low"])


    last_close_price=df["close"].iat[-1]



    print(f"df_last_several_days_copy on {exchange_object} with min volume in usd = {min_volume_in_a_week}")
    print(df_last_several_days_copy.to_string())

    return number_of_available_days_from_one_exchange, min_volume_in_a_week, ath_in_df, atl_in_df, last_close_price
def drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string):
    unique_items = []
    for item in string.split('_'):
        if item not in unique_items:
            unique_items.append(item)
    return '_'.join(unique_items)

def get_list_of_all_tables_in_0000_ohlcv_df(engine_for_ohlcv_data_for_stocks_0000):
    list_of_tables_in_ohlcv_db_0000 = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_0000)
    return list_of_tables_in_ohlcv_db_0000

def get_list_of_all_tables_in_1600_ohlcv_df(engine_for_ohlcv_data_for_stocks_1600):
    list_of_tables_in_ohlcv_db_1600 = \
            get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_1600)
    return list_of_tables_in_ohlcv_db_1600
def get_engine_for_0000_ohlcv_database(db_where_ohlcv_data_for_stocks_is_stored_0000):
    # db_where_ohlcv_data_for_stocks_is_stored_1600 = "ohlcv_1d_data_for_usdt_pairs_1600"
    engine_for_ohlcv_data_for_stocks_0000 , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored_0000 )

    # engine_for_ohlcv_data_for_stocks_1600, \
    #     connection_to_ohlcv_data_for_stocks_1600 = \
    #     connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_1600)
    return engine_for_ohlcv_data_for_stocks_0000

def get_engine_for_1600_ohlcv_database(db_where_ohlcv_data_for_stocks_is_stored_1600):
    # db_where_ohlcv_data_for_stocks_is_stored_1600 = "ohlcv_1d_data_for_usdt_pairs_1600"
    # engine_for_ohlcv_data_for_stocks_0000 , \
    # connection_to_ohlcv_data_for_stocks = \
    #     connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored_0000 )

    engine_for_ohlcv_data_for_stocks_1600, \
        connection_to_ohlcv_data_for_stocks_1600 = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_1600)
    return engine_for_ohlcv_data_for_stocks_1600

def fill_df_with_info_if_ath_was_broken_on_other_exchanges(stock_name,
                                                           db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                           db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                           table_with_ohlcv_data_df,
                                                           engine_for_ohlcv_data_for_stocks_0000,
                                                           engine_for_ohlcv_data_for_stocks_1600,
                                                           all_time_high_in_stock,
                                                           list_of_tables_in_ohlcv_db_1600,
                                                           levels_formed_by_ath_df,
                                                           row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero):
    try:
        ################################################################################
        ######################################################################################
        # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
        df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000 = \
            return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
                db_where_ohlcv_data_for_stocks_is_stored_0000)

        # print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000")
        # print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.to_string())
        #########################################################################################################

        ######################################################################################

        # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
        df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600 = \
            return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
                db_where_ohlcv_data_for_stocks_is_stored_1600)

        # print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600")
        # print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.to_string())
        #######################################################################################################
        #####################################################################################
        db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded = "db_with_trading_pair_statistics"
        table_where_row_names_are_pairs_and_values_are_strings_of_exchanges = "exchanges_where_each_pair_is_traded"
        df_with_strings_of_exchanges_where_pair_is_traded = pd.DataFrame()
        try:
            df_with_strings_of_exchanges_where_pair_is_traded = return_df_with_strings_where_pair_is_traded(
                db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded,
                table_where_row_names_are_pairs_and_values_are_strings_of_exchanges)
        except:
            traceback.print_exc()

        print("df_with_strings_of_exchanges_where_pair_is_traded")
        print(df_with_strings_of_exchanges_where_pair_is_traded.tail(20).to_string())
        #######################################################################################################
        # get base of trading pair
        base = get_base_of_trading_pair(trading_pair=stock_name)
        quote = get_quote_of_trading_pair(trading_pair=stock_name)
        base_slash_quote = base + "/" + quote

        #########################################################
        # find row where base is equal to base from df_with_strings_of_exchanges_where_pair_is_traded
        exchange_id_string_where_trading_pair_is_traded = ""
        exchange_names_string_where_trading_pair_is_traded = ""
        number_of_exchanges_where_pair_is_traded_on = np.nan
        try:
            df_with_strings_of_exchanges_where_pair_is_traded.set_index("trading_pair_new_column", inplace=True)

            exchange_id_string_where_trading_pair_is_traded = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "exchanges_where_pair_is_traded"]
            exchange_names_string_where_trading_pair_is_traded = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "unique_exchanges_where_pair_is_traded"]
            number_of_exchanges_where_pair_is_traded_on = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "number_of_exchanges_where_pair_is_traded_on"]

            print("exchange_id_string_where_trading_pair_is_traded")
            print(exchange_id_string_where_trading_pair_is_traded)
            print("exchange_names_string_where_trading_pair_is_traded")
            print(exchange_names_string_where_trading_pair_is_traded)
            print("number_of_exchanges_where_pair_is_traded_on")
            print(number_of_exchanges_where_pair_is_traded_on)

        except:
            traceback.print_exc()
        ##########################################################

        # # get base of trading pair
        # exchange_of_pair = get_exchange_of_trading_pair(trading_pair=stock_name)
        # get ohlcv_data_df from different exchanges for one base in trading_pair

        counter_of_number_of_exchanges_where_level_had_been_broken = 0
        string_of_exchanges_where_level_was_broken = ""
        string_of_all_exchanges_where_pair_is_traded = ""
        string_of_exchanges_where_level_was_not_broken = ""

        for col in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.columns:
            print("column_name")
            print(col)
            if 'table_name' in col:
                ################################
                table_with_ohlcv_data_df = table_with_ohlcv_data_df[
                    ["Timestamp", "open", "high", "low", "close", "volume"]]
                table_with_ohlcv_data_df_numpy_array = table_with_ohlcv_data_df.to_numpy()
                # print("table_with_ohlcv_data_df_numpy_array")
                # print(table_with_ohlcv_data_df_numpy_array)
                last_ath_timestamp, last_ath_row_number_in_the_original_table = \
                    get_last_ath_timestamp_and_row_number(table_with_ohlcv_data_df_numpy_array,
                                                          all_time_high_in_stock)

                for trading_pair_with_exchange_table_name_in_ohlcv_database in [
                    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.loc[base, col]]:
                    if pd.isna(trading_pair_with_exchange_table_name_in_ohlcv_database):
                        print("trading_pair_with_exchange_table_name_in_ohlcv_database is nan")
                        continue
                    print("trading_pair_with_exchange_table_name_in_ohlcv_databaseue_of_cell_if_df_it_should_be_table_name")
                    print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                    table_with_0000_ohlcv_data_df_on_other_exchanges = \
                        pd.read_sql_query(f'''select * from "{trading_pair_with_exchange_table_name_in_ohlcv_database}"''',
                                          engine_for_ohlcv_data_for_stocks_0000)
                    print("table_with_ohlcv_data_df_on_other_exchanges1")
                    print(table_with_0000_ohlcv_data_df_on_other_exchanges.tail(5).to_string())
                    print("trading_pair_with_exchange_table_name_in_ohlcv_database1")
                    print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                    exchange_of_pair = get_exchange_of_trading_pair(
                        trading_pair=trading_pair_with_exchange_table_name_in_ohlcv_database)
                    print("exchange_of_pair")
                    print(exchange_of_pair)

                    row_number_in_ohlcv_table_on_other_exchanges = \
                        get_row_number_when_timestamp_is_not_index(table_with_0000_ohlcv_data_df_on_other_exchanges,
                                                                   last_ath_timestamp)
                    print("row_number_in_ohlcv_table_on_other_exchanges")
                    print(row_number_in_ohlcv_table_on_other_exchanges)
                    table_with_0000_ohlcv_data_df_on_other_exchanges = table_with_0000_ohlcv_data_df_on_other_exchanges[
                        ["Timestamp", "open", "high", "low", "close", "volume"]]
                    table_with_ohlcv_data_df_on_other_exchanges_numpy_array = table_with_0000_ohlcv_data_df_on_other_exchanges.to_numpy()
                    high_on_another_exchange = find_high_for_timestamp(last_ath_timestamp,
                                                                       table_with_ohlcv_data_df_on_other_exchanges_numpy_array)
                    number_of_days_where_ath_was_not_broken = 2 * 366
                    ath_is_not_broken_for_a_long_time = check_ath_breakout(
                        table_with_ohlcv_data_df_on_other_exchanges_numpy_array,
                        number_of_days_where_ath_was_not_broken,
                        high_on_another_exchange,
                        row_number_in_ohlcv_table_on_other_exchanges)
                    print(f"ath for {base} is not broken = {ath_is_not_broken_for_a_long_time}")

                    string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair
                    string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                        string_of_all_exchanges_where_pair_is_traded)
                    if ath_is_not_broken_for_a_long_time == False:
                        counter_of_number_of_exchanges_where_level_had_been_broken = \
                            counter_of_number_of_exchanges_where_level_had_been_broken + 1
                        string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair
                        string_of_exchanges_where_level_was_broken = remove_first_underscore(
                            string_of_exchanges_where_level_was_broken)
                    else:
                        string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair
                        string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                            string_of_exchanges_where_level_was_not_broken)

                    # check if pair with the same base is traded on huobi and other 1600 exchanges
                    if base in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.index:
                        print(f"base = {base} is on 1600 exchange")
                        tables_which_start_with_base_in_1600_ohlcv_db = [table for table in list_of_tables_in_ohlcv_db_1600
                                                                         if table.startswith(f'{base}_')]
                        for table_which_start_with_base_in_1600_ohlcv_db in tables_which_start_with_base_in_1600_ohlcv_db:
                            print("table_which_start_with_base_in_1600_ohlcv_db")
                            print(table_which_start_with_base_in_1600_ohlcv_db)
                            table_with_1600_ohlcv_data_df_on_other_exchanges = \
                                pd.read_sql_query(
                                    f'''select * from "{table_which_start_with_base_in_1600_ohlcv_db}"''',
                                    engine_for_ohlcv_data_for_stocks_1600)
                            table_with_1600_ohlcv_data_df_on_other_exchanges = \
                            table_with_1600_ohlcv_data_df_on_other_exchanges[
                                ["Timestamp", "open", "high", "low", "close", "volume"]]
                            print("table_with_1600_ohlcv_data_df_on_other_exchanges")
                            print(table_with_1600_ohlcv_data_df_on_other_exchanges)
                            closest_timestamp, high_corresponding_to_closest_timestamp, closest_timestamp_plus_one_day, high_plus_one_day = \
                                find_closest_timestamp_high_high_plus_one_day_using_index(
                                    table_with_1600_ohlcv_data_df_on_other_exchanges, last_ath_timestamp)
                            max_high_on_1600_exchange = max(high_corresponding_to_closest_timestamp, high_plus_one_day)
                            print("high_corresponding_to_closest_timestamp")
                            print(high_corresponding_to_closest_timestamp)
                            print("high_plus_one_day")
                            print(high_plus_one_day)

                            timestamp_of_possible_ath_on_1600_exchange = np.nan
                            if max_high_on_1600_exchange == high_corresponding_to_closest_timestamp:
                                timestamp_of_possible_ath_on_1600_exchange = closest_timestamp
                            else:
                                timestamp_of_possible_ath_on_1600_exchange = closest_timestamp_plus_one_day
                            print("max_high_on_1600_exchange")
                            print(max_high_on_1600_exchange)
                            row_number_of_possible_ath_on_1600_exchange = \
                                get_row_number_when_timestamp_is_not_index(table_with_1600_ohlcv_data_df_on_other_exchanges,
                                                                           timestamp_of_possible_ath_on_1600_exchange)
                            table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange = \
                                table_with_1600_ohlcv_data_df_on_other_exchanges.to_numpy()
                            ath_is_not_broken_for_a_long_time_on_1600_exchange_ = check_ath_breakout(
                                table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange,
                                number_of_days_where_ath_was_not_broken,
                                max_high_on_1600_exchange,
                                row_number_of_possible_ath_on_1600_exchange)
                            exchange_of_pair_for_1600_exchange = get_exchange_of_trading_pair(
                                trading_pair=table_which_start_with_base_in_1600_ohlcv_db)
                            print("exchange_of_pair_for_1600_exchange")
                            print(exchange_of_pair_for_1600_exchange)
                            string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair_for_1600_exchange
                            string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                                string_of_all_exchanges_where_pair_is_traded)
                            if ath_is_not_broken_for_a_long_time_on_1600_exchange_ == False:
                                counter_of_number_of_exchanges_where_level_had_been_broken = \
                                    counter_of_number_of_exchanges_where_level_had_been_broken + 1
                                string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair_for_1600_exchange
                                string_of_exchanges_where_level_was_broken = remove_first_underscore(
                                    string_of_exchanges_where_level_was_broken)
                            else:
                                string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair_for_1600_exchange
                                string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                                    string_of_exchanges_where_level_was_not_broken)

        try:
            string_of_exchanges_where_level_was_broken = \
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                    string_of_exchanges_where_level_was_broken)
            string_of_exchanges_where_level_was_not_broken = \
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                    string_of_exchanges_where_level_was_not_broken)
            string_of_all_exchanges_where_pair_is_traded = \
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                    string_of_all_exchanges_where_pair_is_traded)
            print("string_of_exchanges_where_level_was_broken")
            print(string_of_exchanges_where_level_was_broken)
            print("string_of_exchanges_where_level_was_not_broken")
            print(string_of_exchanges_where_level_was_not_broken)
            print("string_of_all_exchanges_where_pair_is_traded")
            print(string_of_all_exchanges_where_pair_is_traded)

        except:
            traceback.print_exc()

        # add_min_volume_on_each_exchange
        ######################################
        string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers, \
            string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers, \
            string_all_volumes_by_low_on_which_exchange, \
            string_all_volumes_by_low_on_which_exchange_without_outlier, \
            string_all_volumes_by_low_without_exchange_without_outlier, \
            string_all_aths_on_which_exchange, \
            string_all_aths_without_exchange, \
            string_all_aths_on_which_exchange_without_outlier, \
            string_all_aths_without_exchange_without_outlier, \
            string_all_atls_on_which_exchange, \
            string_all_atls_without_exchange, \
            string_all_atls_on_which_exchange_without_outlier, \
            string_all_atls_without_exchange_without_outlier, \
            string_of_last_close_prices_on_all_exchanges, \
            string_of_last_close_prices_on_all_exchanges_with_exchanges, \
            string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers, \
            string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers = generate_min_volume_ath_atl_plus_exchange_string(
            exchange_id_string_where_trading_pair_is_traded,
            stock_name)
        ######################################

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_from_db_where_level_had_been_broken"] = counter_of_number_of_exchanges_where_level_had_been_broken
        print("levels_formed_by_ath_df4")
        print(levels_formed_by_ath_df.to_string())

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_from_db_where_level_was_broken"] = string_of_exchanges_where_level_was_broken
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_from_db_where_level_was_not_broken"] = string_of_exchanges_where_level_was_not_broken
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_all_exchanges_from_db_where_pair_is_traded"] = string_of_all_exchanges_where_pair_is_traded

        ########################
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "exchange_id_string_where_trading_pair_is_traded"] = exchange_id_string_where_trading_pair_is_traded
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "exchange_names_string_where_trading_pair_is_traded"] = exchange_names_string_where_trading_pair_is_traded
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_where_pair_is_traded_on"] = number_of_exchanges_where_pair_is_traded_on
        ########################
        ########################
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_on_which_exchange"] = string_all_volumes_by_low_on_which_exchange
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_on_which_exchange_without_outlier"] = string_all_volumes_by_low_on_which_exchange_without_outlier
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_without_exchange_without_outlier"] = string_all_volumes_by_low_without_exchange_without_outlier

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_on_which_exchange"] = string_all_aths_on_which_exchange
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_without_exchange"] = string_all_aths_without_exchange
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_on_which_exchange_without_outlier"] = string_all_aths_on_which_exchange_without_outlier
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_without_exchange_without_outlier"] = string_all_aths_without_exchange_without_outlier

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_on_which_exchange"] = string_all_atls_on_which_exchange
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_without_exchange"] = string_all_atls_without_exchange
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_on_which_exchange_without_outlier"] = string_all_atls_on_which_exchange_without_outlier
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_without_exchange_without_outlier"] = string_all_atls_without_exchange_without_outlier

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_last_close_prices_on_all_exchanges"] = string_of_last_close_prices_on_all_exchanges
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_last_close_prices_on_all_exchanges_with_exchanges"] = string_of_last_close_prices_on_all_exchanges_with_exchanges
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_with_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_without_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers

        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_available_days_plus_exchange_without_outliers"] = string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers
        levels_formed_by_ath_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_available_days_without_exchange_without_outliers"] = string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers

    except:
        traceback.print_exc()

    return levels_formed_by_ath_df

def fill_df_with_info_if_atl_was_broken_on_other_exchanges(stock_name,
                                                           db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                           db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                           table_with_ohlcv_data_df,
                                                           engine_for_ohlcv_data_for_stocks_0000,
                                                           engine_for_ohlcv_data_for_stocks_1600,
                                                           all_time_low_in_stock,
                                                           list_of_tables_in_ohlcv_db_1600,
                                                           levels_formed_by_atl_df,
                                                           row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero):
    try:
        # we will iterate over each row of this df to understand if ath or atl was broken on a 2 year time period on different exchanges
        df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000 = \
            return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
                db_where_ohlcv_data_for_stocks_is_stored_0000)

        # print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000")
        # print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.to_string())
        #########################################################################################################

        ######################################################################################

        # we will iterate over each row of this df to understand if ath or atl was broken on a 2 year time period on different exchanges
        df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600 = \
            return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
                db_where_ohlcv_data_for_stocks_is_stored_1600)

        # print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600")
        # print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.to_string())
        #######################################################################################################
        #####################################################################################
        db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded = "db_with_trading_pair_statistics"
        table_where_row_names_are_pairs_and_values_are_strings_of_exchanges = "exchanges_where_each_pair_is_traded"
        df_with_strings_of_exchanges_where_pair_is_traded = pd.DataFrame()
        try:
            df_with_strings_of_exchanges_where_pair_is_traded = return_df_with_strings_where_pair_is_traded(
                db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded,
                table_where_row_names_are_pairs_and_values_are_strings_of_exchanges)
        except:
            traceback.print_exc()

        print("df_with_strings_of_exchanges_where_pair_is_traded")
        print(df_with_strings_of_exchanges_where_pair_is_traded.tail(20).to_string())
        #######################################################################################################
        # get base of trading pair
        base = get_base_of_trading_pair(trading_pair=stock_name)
        quote = get_quote_of_trading_pair(trading_pair=stock_name)
        base_slash_quote = base + "/" + quote
        # df_with_strings_of_exchanges_where_pair_is_traded["base_of_trading_pair"]=base


        #########################################################
        # find row where base is equal to base from df_with_strings_of_exchanges_where_pair_is_traded
        exchange_id_string_where_trading_pair_is_traded = ""
        exchange_names_string_where_trading_pair_is_traded = ""
        number_of_exchanges_where_pair_is_traded_on = np.nan
        try:

            df_with_strings_of_exchanges_where_pair_is_traded.set_index("trading_pair_new_column", inplace=True)
            exchange_id_string_where_trading_pair_is_traded = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "exchanges_where_pair_is_traded"]
            exchange_names_string_where_trading_pair_is_traded = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "unique_exchanges_where_pair_is_traded"]
            number_of_exchanges_where_pair_is_traded_on = \
                df_with_strings_of_exchanges_where_pair_is_traded.loc[base_slash_quote, "number_of_exchanges_where_pair_is_traded_on"]






            print("exchange_id_string_where_trading_pair_is_traded")
            print(exchange_id_string_where_trading_pair_is_traded)
            print("exchange_names_string_where_trading_pair_is_traded")
            print(exchange_names_string_where_trading_pair_is_traded)
            print("number_of_exchanges_where_pair_is_traded_on")
            print(number_of_exchanges_where_pair_is_traded_on)

        except:
            traceback.print_exc()
        ##########################################################

        # # get base of trading pair
        # exchange_of_pair = get_exchange_of_trading_pair(trading_pair=stock_name)
        # get ohlcv_data_df from different exchanges for one base in trading_pair

        counter_of_number_of_exchanges_where_level_had_been_broken = 0
        string_of_exchanges_where_level_was_broken = ""
        string_of_all_exchanges_where_pair_is_traded = ""
        string_of_exchanges_where_level_was_not_broken = ""

        for col in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.columns:
            print("column_name")
            print(col)
            if 'table_name' in col:
                ################################
                table_with_ohlcv_data_df = table_with_ohlcv_data_df[
                    ["Timestamp", "open", "high", "low", "close", "volume"]]
                table_with_ohlcv_data_df_numpy_array = table_with_ohlcv_data_df.to_numpy()
                # print("table_with_ohlcv_data_df_numpy_array")
                # print(table_with_ohlcv_data_df_numpy_array)
                last_atl_timestamp, last_atl_row_number_in_the_original_table = \
                    get_last_atl_timestamp_and_row_number(table_with_ohlcv_data_df_numpy_array,
                                                          all_time_low_in_stock)

                for trading_pair_with_exchange_table_name_in_ohlcv_database in [
                    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.loc[base, col]]:
                    if pd.isna(trading_pair_with_exchange_table_name_in_ohlcv_database):
                        print("trading_pair_with_exchange_table_name_in_ohlcv_database is nan")
                        continue
                    print("trading_pair_with_exchange_table_name_in_ohlcv_databaseue_of_cell_if_df_it_should_be_table_name")
                    print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                    table_with_0000_ohlcv_data_df_on_other_exchanges = \
                        pd.read_sql_query(f'''select * from "{trading_pair_with_exchange_table_name_in_ohlcv_database}"''',
                                          engine_for_ohlcv_data_for_stocks_0000)
                    print("table_with_ohlcv_data_df_on_other_exchanges1")
                    print(table_with_0000_ohlcv_data_df_on_other_exchanges.tail(5).to_string())
                    print("trading_pair_with_exchange_table_name_in_ohlcv_database1")
                    print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                    exchange_of_pair = get_exchange_of_trading_pair(
                        trading_pair=trading_pair_with_exchange_table_name_in_ohlcv_database)
                    print("exchange_of_pair")
                    print(exchange_of_pair)

                    row_number_in_ohlcv_table_on_other_exchanges = \
                        get_row_number_when_timestamp_is_not_index(table_with_0000_ohlcv_data_df_on_other_exchanges,
                                                                   last_atl_timestamp)
                    print("row_number_in_ohlcv_table_on_other_exchanges")
                    print(row_number_in_ohlcv_table_on_other_exchanges)
                    table_with_0000_ohlcv_data_df_on_other_exchanges = table_with_0000_ohlcv_data_df_on_other_exchanges[
                        ["Timestamp", "open", "high", "low", "close", "volume"]]
                    table_with_ohlcv_data_df_on_other_exchanges_numpy_array = table_with_0000_ohlcv_data_df_on_other_exchanges.to_numpy()
                    low_on_another_exchange = find_low_for_timestamp(last_atl_timestamp,
                                                                     table_with_ohlcv_data_df_on_other_exchanges_numpy_array)
                    number_of_days_where_atl_was_not_broken = 2 * 366
                    atl_is_not_broken_for_a_long_time = check_atl_breakout(
                        table_with_ohlcv_data_df_on_other_exchanges_numpy_array,
                        number_of_days_where_atl_was_not_broken,
                        low_on_another_exchange,
                        row_number_in_ohlcv_table_on_other_exchanges)
                    print(f"atl for {base} is not broken = {atl_is_not_broken_for_a_long_time}")

                    string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair
                    string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                        string_of_all_exchanges_where_pair_is_traded)
                    if atl_is_not_broken_for_a_long_time == False:
                        counter_of_number_of_exchanges_where_level_had_been_broken = \
                            counter_of_number_of_exchanges_where_level_had_been_broken + 1
                        string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair
                        string_of_exchanges_where_level_was_broken = remove_first_underscore(
                            string_of_exchanges_where_level_was_broken)
                    else:
                        string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair
                        string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                            string_of_exchanges_where_level_was_not_broken)

                    # check if pair with the same base is traded on huobi and other 1600 exchanges
                    if base in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.index:
                        print(f"base = {base} is on huobi")
                        tables_which_start_with_base_in_1600_ohlcv_db = [table for table in list_of_tables_in_ohlcv_db_1600
                                                                         if table.startswith(f'{base}_')]
                        for table_which_start_with_base_in_1600_ohlcv_db in tables_which_start_with_base_in_1600_ohlcv_db:
                            print("table_which_start_with_base_in_1600_ohlcv_db")
                            print(table_which_start_with_base_in_1600_ohlcv_db)
                            table_with_1600_ohlcv_data_df_on_other_exchanges = \
                                pd.read_sql_query(
                                    f'''select * from "{table_which_start_with_base_in_1600_ohlcv_db}"''',
                                    engine_for_ohlcv_data_for_stocks_1600)
                            table_with_1600_ohlcv_data_df_on_other_exchanges = \
                            table_with_1600_ohlcv_data_df_on_other_exchanges[
                                ["Timestamp", "open", "high", "low", "close", "volume"]]
                            print("table_with_1600_ohlcv_data_df_on_other_exchanges")
                            print(table_with_1600_ohlcv_data_df_on_other_exchanges)
                            closest_timestamp, low_corresponding_to_closest_timestamp, closest_timestamp_plus_one_day, low_plus_one_day = \
                                find_closest_timestamp_low_low_plus_one_day_using_index(
                                    table_with_1600_ohlcv_data_df_on_other_exchanges, last_atl_timestamp)
                            min_low_on_1600_exchange = min(low_corresponding_to_closest_timestamp, low_plus_one_day)
                            print("low_corresponding_to_closest_timestamp")
                            print(low_corresponding_to_closest_timestamp)
                            print("low_plus_one_day")
                            print(low_plus_one_day)

                            timestamp_of_possible_atl_on_1600_exchange = np.nan
                            if min_low_on_1600_exchange == low_corresponding_to_closest_timestamp:
                                timestamp_of_possible_atl_on_1600_exchange = closest_timestamp
                            else:
                                timestamp_of_possible_atl_on_1600_exchange = closest_timestamp_plus_one_day
                            print("min_low_on_1600_exchange")
                            print(min_low_on_1600_exchange)
                            row_number_of_possible_atl_on_1600_exchange = \
                                get_row_number_when_timestamp_is_not_index(table_with_1600_ohlcv_data_df_on_other_exchanges,
                                                                           timestamp_of_possible_atl_on_1600_exchange)
                            table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange = \
                                table_with_1600_ohlcv_data_df_on_other_exchanges.to_numpy()
                            atl_is_not_broken_for_a_long_time_on_1600_exchange_ = check_atl_breakout(
                                table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange,
                                number_of_days_where_atl_was_not_broken,
                                min_low_on_1600_exchange,
                                row_number_of_possible_atl_on_1600_exchange)
                            exchange_of_pair_for_1600_exchange = get_exchange_of_trading_pair(
                                trading_pair=table_which_start_with_base_in_1600_ohlcv_db)
                            print("exchange_of_pair_for_1600_exchange")
                            print(exchange_of_pair_for_1600_exchange)
                            string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair_for_1600_exchange
                            string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                                string_of_all_exchanges_where_pair_is_traded)
                            if atl_is_not_broken_for_a_long_time_on_1600_exchange_ == False:
                                counter_of_number_of_exchanges_where_level_had_been_broken = \
                                    counter_of_number_of_exchanges_where_level_had_been_broken + 1
                                string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair_for_1600_exchange
                                string_of_exchanges_where_level_was_broken = remove_first_underscore(
                                    string_of_exchanges_where_level_was_broken)
                            else:
                                string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair_for_1600_exchange
                                string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                                    string_of_exchanges_where_level_was_not_broken)

        try:
            string_of_exchanges_where_level_was_broken=\
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_exchanges_where_level_was_broken)
            string_of_exchanges_where_level_was_not_broken=\
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_exchanges_where_level_was_not_broken)
            string_of_all_exchanges_where_pair_is_traded=\
                drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_all_exchanges_where_pair_is_traded)
        except:
            traceback.print_exc()

        # # create two strings of aths and atls on all exchanges where pair is traded
        # string_list_of_aths = ""
        # string_list_of_atls = ""
        # try:
        #     list_of_absolutely_all_exchange_ids_where_pair_is_traded = exchange_id_string_where_trading_pair_is_traded.split(
        #         "_")
        #     print("list_of_absolutely_all_exchange_ids_where_pair_is_traded5")
        #     print(list_of_absolutely_all_exchange_ids_where_pair_is_traded)
        #     # list_of_all_aths_from_all_exchanges = []
        #     list_of_all_atls_from_all_exchanges = []
        #     for exchange_id in list_of_absolutely_all_exchange_ids_where_pair_is_traded:
        #         exchange_object = get_exchange_object2(exchange_id)
        #         crypto_pair_name=stock_name.split("_on_")[0]
        #         crypto_pair_name=crypto_pair_name.replace("_","/")
        #         print("crypto_pair_name4")
        #         print(crypto_pair_name)
        #
        #         try:
        #             if ":" in crypto_pair_name:
        #                 exchange_object.load_markets()
        #                 if crypto_pair_name not in exchange_object.symbols:
        #                     print("crypto_pair_name5")
        #                     print(crypto_pair_name)
        #                     #find not swap but spot ath and ath if swap on this exchange is not traded
        #                     crypto_pair_name=crypto_pair_name.split(":")[0]
        #         except:
        #             traceback.print_exc()
        #         try:
        #             atl_from_some_other_exchange = \
        #                 get_all_time_low_from_some_exchange(exchange_object, crypto_pair_name)
        #             print("atl_from_some_other_exchange2")
        #             print(atl_from_some_other_exchange)
        #             # list_of_all_aths_from_all_exchanges.append(ath_from_some_other_exchange)
        #             list_of_all_atls_from_all_exchanges.append(atl_from_some_other_exchange)
        #             # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
        #             string_list_of_atls = '_'.join([str(x) for x in list_of_all_atls_from_all_exchanges])
        #         except:
        #             traceback.print_exc()
        #
        # except:
        #     traceback.print_exc()

        # add_min_volume_on_each_exchange
        ######################################
        string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers, \
            string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers, \
            string_all_volumes_by_low_on_which_exchange, \
            string_all_volumes_by_low_on_which_exchange_without_outlier, \
            string_all_volumes_by_low_without_exchange_without_outlier, \
            string_all_aths_on_which_exchange, \
            string_all_aths_without_exchange, \
            string_all_aths_on_which_exchange_without_outlier, \
            string_all_aths_without_exchange_without_outlier, \
            string_all_atls_on_which_exchange, \
            string_all_atls_without_exchange, \
            string_all_atls_on_which_exchange_without_outlier, \
            string_all_atls_without_exchange_without_outlier, \
            string_of_last_close_prices_on_all_exchanges, \
            string_of_last_close_prices_on_all_exchanges_with_exchanges, \
            string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers, \
            string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers = generate_min_volume_ath_atl_plus_exchange_string(
            exchange_id_string_where_trading_pair_is_traded,
            stock_name)

        # try:
        #     list_of_absolutely_all_exchange_ids_where_pair_is_traded = exchange_id_string_where_trading_pair_is_traded.split(
        #         "_")
        #     print("list_of_absolutely_all_exchange_ids_where_pair_is_traded5")
        #     print(list_of_absolutely_all_exchange_ids_where_pair_is_traded)
        #     # list_of_all_aths_from_all_exchanges = []
        #     list_of_all_volumes_by_low_from_all_exchanges = []
        #     for exchange_id in list_of_absolutely_all_exchange_ids_where_pair_is_traded:
        #         exchange_object = get_exchange_object2(exchange_id)
        #         crypto_pair_name=stock_name.split("_on_")[0]
        #         crypto_pair_name=crypto_pair_name.replace("_","/")
        #         print("crypto_pair_name4")
        #         print(crypto_pair_name)
        #
        #         try:
        #             if ":" in crypto_pair_name:
        #                 exchange_object.load_markets()
        #                 if crypto_pair_name not in exchange_object.symbols:
        #                     print("crypto_pair_name5")
        #                     print(crypto_pair_name)
        #                     #find not swap but spot ath and ath if swap on this exchange is not traded
        #                     crypto_pair_name=crypto_pair_name.split(":")[0]
        #         except:
        #             traceback.print_exc()
        #         try:
        #             # atl_from_some_other_exchange = \
        #             #     get_all_time_low_from_some_exchange(exchange_object, crypto_pair_name)
        #             min_volume_over_this_many_days_in_dollars=7
        #             min_volume_over_last_several_days_in_dollars=\
        #                 min_volume_in_a_week(exchange_object, crypto_pair_name, min_volume_over_this_many_days_in_dollars)
        #
        #             if min_volume_over_last_several_days_in_dollars >1:
        #                 min_volume_over_last_several_days_in_dollars=int(min_volume_over_last_several_days_in_dollars)
        #
        #             # list_of_all_aths_from_all_exchanges.append(ath_from_some_other_exchange)
        #             list_of_all_volumes_by_low_from_all_exchanges.append(str(min_volume_over_last_several_days_in_dollars)+"_on_"+exchange_id)
        #             # string_list_of_aths = '_'.join([str(x) for x in list_of_all_aths_from_all_exchanges])
        #             string_all_volumes_by_low_on_which_exchange = '_'.join([str(x) for x in list_of_all_volumes_by_low_from_all_exchanges])
        #         except:
        #             traceback.print_exc()
        #
        # except:
        #     traceback.print_exc()

        #################################

        print("levels_formed_by_atl_df1")
        print(levels_formed_by_atl_df.to_string())

        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_from_db_where_level_had_been_broken"] = counter_of_number_of_exchanges_where_level_had_been_broken
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_from_db_where_level_was_broken"] = string_of_exchanges_where_level_was_broken
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_from_db_where_level_was_not_broken"] = string_of_exchanges_where_level_was_not_broken
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_all_exchanges_from_db_where_pair_is_traded"] = string_of_all_exchanges_where_pair_is_traded

        print("levels_formed_by_atl_df2")
        print(levels_formed_by_atl_df.to_string())
        ########################
        print("exchange_id_string_where_trading_pair_is_traded123")
        print(exchange_id_string_where_trading_pair_is_traded)
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "exchange_id_string_where_trading_pair_is_traded"] = exchange_id_string_where_trading_pair_is_traded
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "exchange_names_string_where_trading_pair_is_traded"] = exchange_names_string_where_trading_pair_is_traded
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_where_pair_is_traded_on"] = number_of_exchanges_where_pair_is_traded_on
        ########################
        ########################
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_on_which_exchange"] = string_all_volumes_by_low_on_which_exchange
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_on_which_exchange_without_outlier"] = string_all_volumes_by_low_on_which_exchange_without_outlier
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_volumes_by_low_without_exchange_without_outlier"] = string_all_volumes_by_low_without_exchange_without_outlier

        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_on_which_exchange"] = string_all_aths_on_which_exchange
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_without_exchange"] = string_all_aths_without_exchange
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_on_which_exchange_without_outlier"] = string_all_aths_on_which_exchange_without_outlier
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_aths_without_exchange_without_outlier"] = string_all_aths_without_exchange_without_outlier

        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_on_which_exchange"] = string_all_atls_on_which_exchange
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_without_exchange"] = string_all_atls_without_exchange
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_on_which_exchange_without_outlier"] = string_all_atls_on_which_exchange_without_outlier
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_all_atls_without_exchange_without_outlier"] = string_all_atls_without_exchange_without_outlier

        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_last_close_prices_on_all_exchanges"] = string_of_last_close_prices_on_all_exchanges
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_last_close_prices_on_all_exchanges_with_exchanges"] = string_of_last_close_prices_on_all_exchanges_with_exchanges
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_with_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_without_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers

        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_available_days_plus_exchange_without_outliers"] = string_of_number_of_available_days_from_all_exchanges_plus_exchange_without_outliers
        levels_formed_by_atl_df.at[
            row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_available_days_without_exchange_without_outliers"] = string_of_number_of_available_days_from_all_exchanges_without_exchanges_without_outliers
        # levels_formed_by_atl_df.at[
        #     row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_with_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_with_exchanges_without_outliers
        # levels_formed_by_atl_df.at[
        #     row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "last_close_on_all_exchanges_without_exchanges_without_outliers"] = string_of_last_close_prices_on_all_exchanges_without_exchanges_without_outliers



    except:
            traceback.print_exc()

    return levels_formed_by_atl_df


def get_row_number_when_timestamp_is_not_index(table_with_ohlcv_data_df_on_other_exchanges, atl_or_ath_timestamp):
    """
    Returns the row number of the row in which the column "Timestamp" equals to atl_timestamp.
    """
    print("inner_atl_of_ath_timestamp")
    print(atl_or_ath_timestamp)
    print("inner_table_with_ohlcv_data_df_on_other_exchanges")
    print(table_with_ohlcv_data_df_on_other_exchanges.tail(10).to_string())
    print("table_with_ohlcv_data_df_on_other_exchanges.index[table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp]")
    print(table_with_ohlcv_data_df_on_other_exchanges.index[
        table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp].tolist())
    # find the row number where "Timestamp" equals atl_timestamp
    row_number=np.nan
    try:
        row_number = table_with_ohlcv_data_df_on_other_exchanges.index[
            table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp].tolist()[0]
    except:
        traceback.print_exc()

    print("row_number2")
    print(row_number)

    return row_number


def get_row_number_when_timestamp_is_index(table_with_ohlcv_data_df_on_other_exchanges, atl_or_ath_timestamp):
    """
    Returns the row number of the row in which the index "Timestamp" equals to atl_or_ath_timestamp.
    """
    # find the row number where the index equals atl_or_ath_timestamp
    row_number = table_with_ohlcv_data_df_on_other_exchanges.index.get_loc(atl_or_ath_timestamp)

    return row_number
def get_last_atl_timestamp_and_row_number(table_with_ohlcv_data_df_slice_numpy_array, ATL):
    # Find the rows where the low equals the ATL
    atl_rows = np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL)[0]
    print("np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL)")
    print(np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL))

    print("atl_rows1")
    print(atl_rows)

    print("ATL1")
    print(ATL)

    # print("table_with_ohlcv_data_df_slice_numpy_array1")
    # print(table_with_ohlcv_data_df_slice_numpy_array)


    if len(atl_rows) > 0:
        # Get the timestamp of the last row where the low equals the ATL
        last_atl_timestamp = table_with_ohlcv_data_df_slice_numpy_array[atl_rows[-1], 0]

        # Get the row number of the last ATL row
        last_atl_row_number = atl_rows[-1]

        return last_atl_timestamp, last_atl_row_number
    else:
        return None

def find_high_for_timestamp(timestamp_of_ath, table_with_ohlcv_data_df_numpy_array):
    timestamp_column = table_with_ohlcv_data_df_numpy_array[:, 0]
    high_column = table_with_ohlcv_data_df_numpy_array[:, 2]
    index = np.where(timestamp_column == timestamp_of_ath)[0]
    if len(index) > 0:
        high_that_might_be_ath = high_column[index[0]]
        return high_that_might_be_ath
    else:
        return None

def find_low_for_timestamp(timestamp_of_atl, table_with_ohlcv_data_df_numpy_array):
    timestamp_column = table_with_ohlcv_data_df_numpy_array[:, 0]
    low_column = table_with_ohlcv_data_df_numpy_array[:, 3]
    index = np.where(timestamp_column == timestamp_of_atl)[0]
    if len(index) > 0:
        low_that_might_be_atl = low_column[index[0]]
        return low_that_might_be_atl
    else:
        return None


def get_last_ath_timestamp_and_row_number(table_with_ohlcv_data_df_slice_numpy_array, ATH):
    # Find the rows where the high equals the ATH
    ath_rows = np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 2] == ATH)[0]

    if len(ath_rows) > 0:
        # Get the timestamp of the last row where the high equals the ATH
        last_ath_timestamp = table_with_ohlcv_data_df_slice_numpy_array[ath_rows[-1], 0]

        # Get the row number of the last ATH row
        last_ath_row_number = ath_rows[-1]

        return last_ath_timestamp, last_ath_row_number
    else:
        return None


def connect_to_postgres_db_without_deleting_it_first(database):
    import db_config
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' , echo = True )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db
def check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_ath_was_not_broken,
                       ath,
                       row_of_last_ath):

    if np.isnan(row_of_last_ath):
        return True

    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_ath - number_of_days_where_ath_was_not_broken)
    # print("start_row_index")
    # print(start_row_index)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_ath + 1]
    # print("selected_rows")
    # print(selected_rows)

    # Determine if the high was broken during the selected period
    ath_is_not_broken_for_a_long_time = True
    max_high_over_given_perion = np.max(selected_rows[:, 2])
    # print("max_high_over_given_perion_when_true")
    # print(max_high_over_given_perion)
    if max_high_over_given_perion > ath:
        # print("max_high_over_given_perion_when_false")
        # print(max_high_over_given_perion)
        ath_is_not_broken_for_a_long_time = False

    return ath_is_not_broken_for_a_long_time


def find_closest_timestamp_high_low_closest_timestamp_high_low_plus_one_day(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the corresponding low and high values
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    low = closest_row['low'].values[0]
    high = closest_row['high'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding low and high values for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    low_plus_one_day = closest_row_plus_one_day['low'].values[0]
    high_plus_one_day = closest_row_plus_one_day['high'].values[0]

    return closest_timestamp, low, high, closest_timestamp_plus_one_day, low_plus_one_day, high_plus_one_day


def find_closest_timestamp_high_closest_timestamp_plus_one_day_high_plus_one_day(df, last_ath_timestamp):
    # # Convert the last_ath_timestamp to a pandas Timestamp object
    # last_ath_timestamp = pd.Timestamp(last_ath_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_ath_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_ath_timestamp).abs().argsort()[0]]

    # Find the corresponding high value
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    high = closest_row['high'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding high value for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    high_plus_one_day = closest_row_plus_one_day['high'].values[0]

    return closest_timestamp, high, closest_timestamp_plus_one_day, high_plus_one_day


def find_closest_timestamp_low_closest_timestamp_plus_one_day_low_plus_one_day(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the corresponding low value
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    low = closest_row['low'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding low value for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    low_plus_one_day = closest_row_plus_one_day['low'].values[0]

    return closest_timestamp, low, closest_timestamp_plus_one_day, low_plus_one_day


def find_closest_timestamp_high_high_plus_one_day_using_index(df, last_ath_timestamp):
    # # Convert the last_ath_timestamp to a pandas Timestamp object
    # last_ath_timestamp = pd.Timestamp(last_ath_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_ath_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_ath_timestamp).abs().argsort()[0]]

    # Find the index of the closest Timestamp in the DataFrame
    closest_index = df.index[df['Timestamp'] == closest_timestamp][0]

    # Find the corresponding high value
    high = df.loc[closest_index, 'high']

    # Find the Timestamp and high value for the next row in the DataFrame
    closest_timestamp_plus_one_day=np.nan
    high_plus_one_day=np.nan
    try:
        if len(df)>closest_index + 1:
            closest_timestamp_plus_one_day = df.loc[closest_index + 1, 'Timestamp']
        else:
            closest_timestamp_plus_one_day = df.loc[closest_index, 'Timestamp']
    except:
        traceback.print_exc()
    try:
        if len(df) > closest_index + 1:
            high_plus_one_day = df.loc[closest_index + 1, 'high']
        else:
            high_plus_one_day = df.loc[closest_index, 'high']
    except:
        traceback.print_exc()

    return closest_timestamp, high, closest_timestamp_plus_one_day, high_plus_one_day


def find_closest_timestamp_low_low_plus_one_day_using_index(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the index of the closest Timestamp in the DataFrame
    closest_index = df.index[df['Timestamp'] == closest_timestamp][0]

    # Find the corresponding low value
    low = df.loc[closest_index, 'low']

    # Find the Timestamp and low value for the next row in the DataFrame
    closest_timestamp_plus_one_day=np.nan
    low_plus_one_day=np.nan
    try:
        if len(df) > closest_index + 1:
            closest_timestamp_plus_one_day = df.loc[closest_index + 1, 'Timestamp']
        else:
            closest_timestamp_plus_one_day = df.loc[closest_index, 'Timestamp']
    except:
        traceback.print_exc()
    try:
        if len(df) > closest_index + 1:
            low_plus_one_day = df.loc[closest_index + 1, 'low']
        else:
            low_plus_one_day = df.loc[closest_index, 'low']
    except:
        traceback.print_exc()

    return closest_timestamp, low, closest_timestamp_plus_one_day, low_plus_one_day


def check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_atl_was_not_broken,
                       atl,
                       row_of_last_atl):
    if np.isnan(row_of_last_atl):
        return True
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_atl - number_of_days_where_atl_was_not_broken)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_atl + 1]

    # Determine if the low was broken during the selected period
    atl_is_not_broken_for_a_long_time = True
    min_low_over_given_period = np.min(selected_rows[:, 3])
    if min_low_over_given_period < atl:
        atl_is_not_broken_for_a_long_time = False

    return atl_is_not_broken_for_a_long_time

def return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(db_where_ohlcv_data_for_stocks_is_stored):

    engine_for_ohlcv_data_for_stocks, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored)
    list_of_tables_in_ohlcv_db = get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks)
    # print("list_of_tables_in_ohlcv_db")
    # print(list_of_tables_in_ohlcv_db)

    # iterate over the list of table names
    base_list = []
    for table_name in list_of_tables_in_ohlcv_db:

        exchange = table_name.split("_on_")[1]
        trading_pair = table_name.split("_on_")[0]
        base = trading_pair.split("_")[0]
        quote = trading_pair.split("_")[1]
        base_list.append(base)

    # count the occurrences of each value in the list
    counted_values = Counter(base_list)
    # get the maximum count of any value in the list
    max_count = max(counted_values.values())

    #drop duplicates in base_list
    base_list=list(set(base_list))


    # create a dictionary of column names and empty lists
    columns = [f'{i}_table_name' for i in range(1, max_count + 1)]
    data_frame_with_columns_as_base = pd.DataFrame(index=base_list, columns=columns)

    for counter,base in enumerate(base_list):
        # print(f"counter = {counter}")

        new_list = [value for value in list_of_tables_in_ohlcv_db if value.startswith(base + "_")]
        list_without_nans=new_list.copy()
        new_list.extend([None] * (len(data_frame_with_columns_as_base.columns) - len(new_list)))

        data_frame_with_columns_as_base.loc[base] = new_list
        data_frame_with_columns_as_base.loc[base,"number_of_tables"] = len(list_without_nans)
        # data_frame_with_columns_as_base['number_of_tables'] = data_frame_with_columns_as_base['number_of_tables'].astype(int)
        # print("new_list")
        # print(new_list)

    # print("data_frame_with_columns_as_base")
    # print(data_frame_with_columns_as_base.to_string())
    # print("len(data_frame_with_columns_as_base)")
    # print(len(data_frame_with_columns_as_base))
    connection_to_ohlcv_data_for_stocks.close()
    return data_frame_with_columns_as_base


def return_df_with_strings_where_pair_is_traded(
        db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded,
        table_where_row_names_are_pairs_and_values_are_strings_of_exchanges):
    engine_for_db_with_string_of_exchanges_where_pair_is_traded, \
        connection_to_db_with_string_of_exchanges_where_pair_is_traded = \
        connect_to_postgres_db_without_deleting_it_first(
            db_where_trading_pair_is_row_and_string_of_exchanges_where_pair_is_traded)
    df_with_strings_of_exchanges_where_pair_is_traded = pd.read_sql_query(
        f'''select * from "{table_where_row_names_are_pairs_and_values_are_strings_of_exchanges}"''',
        engine_for_db_with_string_of_exchanges_where_pair_is_traded)
    print("df_with_strings_of_exchanges_where_pair_is_traded12")
    print(df_with_strings_of_exchanges_where_pair_is_traded.tail(20).to_string())

    df_with_strings_of_exchanges_where_pair_is_traded = df_with_strings_of_exchanges_where_pair_is_traded[
        df_with_strings_of_exchanges_where_pair_is_traded['trading_pair'].str.find(':') == -1]

    connection_to_db_with_string_of_exchanges_where_pair_is_traded.close()
    return df_with_strings_of_exchanges_where_pair_is_traded


def get_base_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return base

def get_exchange_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return exchange

def get_quote_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return quote

def remove_first_underscore(string):
    if string.startswith("_"):
        return string[1:]
    else:
        return string

if __name__=="__main__":
    db_where_ohlcv_data_for_stocks_is_stored = "ohlcv_1d_data_for_usdt_pairs_0000"
    db_where_ohlcv_data_for_stocks_is_stored=\
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored)



