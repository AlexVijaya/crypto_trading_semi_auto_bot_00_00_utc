from statistics import mean
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_ath_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_atl_breakout
import pandas as pd
import sys
from datetime import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from subprocess import Popen, PIPE
import subprocess
from get_info_from_load_markets import get_exchange_object6
from current_search_for_tickers_with_rebound_situations_off_atl import check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level
from current_search_for_tickers_with_rebound_situations_off_atl import check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level
from current_search_for_tickers_with_rebound_situations_off_ath import check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level
from current_search_for_tickers_with_rebound_situations_off_ath import check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level
from current_search_for_tickers_with_rebound_situations_off_atl import get_timestamp_of_bpu2
from current_search_for_tickers_with_fast_breakout_of_atl import calculate_atr_without_paranormal_bars_from_numpy_array
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import os
from current_search_for_tickers_with_rebound_situations_off_atl import get_timestamp_of_bpu2
from current_search_for_tickers_with_rebound_situations_off_atl import get_ohlc_of_bpu2
from count_leading_zeros_in_a_number import count_zeros
from get_info_from_load_markets import count_zeros_number_with_e_notaton_is_acceptable
from current_search_for_tickers_with_fast_breakout_of_atl import get_date_with_and_without_time_from_timestamp
import time
import traceback
from current_search_for_tickers_with_rebound_situations_off_atl import get_volume_of_bpu2
from current_search_for_tickers_with_rebound_situations_off_atl import calculate_advanced_atr
from before_entry_current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_current_price_of_asset
from sqlalchemy_utils import create_database, database_exists
# import db_config
from sqlalchemy import inspect
from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
from before_entry_current_search_for_tickers_with_breakout_situations_of_ath_position_entry_next_day import get_list_of_tables_in_db
import datetime
from build_entire_df_of_assets_which_will_be_used_for_position_entry import build_entire_df_of_assets_which_will_be_used_for_position_entry
import numpy as np
from current_search_for_tickers_with_rebound_situations_off_atl import get_last_close_price_of_asset
from fetch_historical_ohlcv_data_for_one_USDT_pair_for_1D_without_inserting_into_db import fetch_one_ohlcv_table
from update_todays_USDT_pairs_where_models_have_formed_for_1D_next_bar_print_utc_time_00 import get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table
import math

def return_args_for_placing_limit_or_stop_order(row_df):
    # trading_pair = base_slash_quote
    # price_of_sl = 0
    # price_of_tp = 0

    amount_of_asset_for_entry_in_quote_currency = row_df.loc[index, "position_size"]
    # position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
    # amount_of_asset_for_entry = position_size_in_shares_of_asset
    # price_of_limit_order = row_df.loc[index, "buy_order"]
    # amount_of_sl = position_size_in_shares_of_asset
    # amount_of_tp = position_size_in_shares_of_asset
    # stop_loss_is_calculated = row_df.loc[index, "stop_loss_is_calculated"]
    # stop_loss_is_technical = row_df.loc[index, "stop_loss_is_technical"]
    type_of_sl = row_df.loc[index, "market_or_limit_stop_loss"]
    type_of_tp = row_df.loc[index, "market_or_limit_take_profit"]
    price_of_tp = row_df.loc[index, "final_take_profit_price"]
    price_of_sl = row_df.loc[index, "final_stop_loss_price"]
    price_of_limit_or_stop_order = row_df.loc[index, "final_position_entry_price"]

    # market_or_limit_take_profit = row_df.loc[index, "market_or_limit_take_profit"]
    # take_profit_x_to_one = row_df.loc[index, "take_profit_x_to_one"]
    # take_profit_when_sl_is_technical_3_to_1 = row_df.loc[
    #     index, "take_profit_when_sl_is_technical_3_to_1"]
    # take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[
    #     index, "take_profit_when_sl_is_calculated_3_to_1"]

    spot_cross_or_isolated_margin = ""

    spot_without_margin_bool = row_df.loc[index, "spot_without_margin"]
    print("row_df")
    print(row_df.to_string())
    print("index12")
    print(index)
    # spot_without_margin_bool=bool(spot_without_margin_bool)
    print("spot_without_margin_bool")
    print(spot_without_margin_bool)
    print("type(spot_without_margin_bool)")
    print(type(spot_without_margin_bool))
    cross_margin_bool = row_df.loc[index, "cross_margin"]
    isolated_margin_bool = row_df.loc[index, "isolated_margin"]

    if spot_without_margin_bool == True:
        spot_cross_or_isolated_margin = "spot"
    elif cross_margin_bool == True:
        spot_cross_or_isolated_margin = "cross"
    elif isolated_margin_bool == True:
        spot_cross_or_isolated_margin = "isolated"
    else:
        print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated1")

    # take_profit_3_1 = np.nan
    # if "take_profit_3_1" in row_df.columns:
    #     take_profit_3_1 = row_df.loc[index, "take_profit_3_1"]
    # if is_not_nan(take_profit_3_1):
    #     price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0
    #
    # if stop_loss_is_technical:
    #     price_of_sl = row_df.loc[index, "technical_stop_loss"]
    #     if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
    #         price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
    # if stop_loss_is_calculated:
    #     price_of_sl = row_df.loc[index, "calculated_stop_loss"]
    #     if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
    #         price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

    # if market_or_limit_stop_loss == 'market':
    #     type_of_sl = 'market'
    # if market_or_limit_stop_loss == 'limit':
    #     type_of_sl = 'limit'
    # 
    # if market_or_limit_take_profit == 'market':
    #     type_of_tp = 'market'
    # if market_or_limit_take_profit == 'limit':
    #     type_of_tp = 'limit'

    side_of_limit_or_stop_order = row_df.loc[index, "side"]
    post_only_for_limit_tp_bool = False

    # args = [exchange_id,
    #         trading_pair,
    #         price_of_sl,
    #         type_of_sl,
    #         amount_of_sl,
    #         price_of_tp,
    #         type_of_tp,
    #         amount_of_tp,
    #         post_only_for_limit_tp_bool,
    #         price_of_limit_order,
    #         amount_of_asset_for_entry,
    #         side_of_limit_order,
    #         spot_cross_or_isolated_margin]

    return price_of_sl,\
        type_of_sl,\
        price_of_tp,\
        type_of_tp,\
        side_of_limit_or_stop_order,\
        price_of_limit_or_stop_order,\
        spot_cross_or_isolated_margin,\
        amount_of_asset_for_entry_in_quote_currency
def convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,price_of_entry_order):
    amount_of_asset_for_entry_in_base_currency = float(amount_of_asset_for_entry_in_quote_currency) / float(
        price_of_entry_order)
    return amount_of_asset_for_entry_in_base_currency
def run_separate_file_that_enters_position(row_df,index,current_price_of_asset,exchange_id,base_slash_quote):
    sell_order_price = row_df.loc[index, "sell_order"]
    if current_price_of_asset < sell_order_price:
        # run file that places sell limit order
        trading_pair = base_slash_quote
        price_of_sl = 0
        price_of_tp = 0
        type_of_sl = None
        type_of_tp = None
        position_size_in_usd = row_df.loc[index, "position_size"]
        position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
        amount_of_asset_for_entry = position_size_in_shares_of_asset
        price_of_limit_order = row_df.loc[index, "sell_order"]
        amount_of_sl = position_size_in_shares_of_asset
        amount_of_tp = position_size_in_shares_of_asset
        stop_loss_is_calculated = row_df.loc[index, "stop_loss_is_calculated"]
        stop_loss_is_technical = row_df.loc[index, "stop_loss_is_technical"]
        market_or_limit_stop_loss = row_df.loc[index, "market_or_limit_stop_loss"]

        market_or_limit_take_profit = row_df.loc[index, "market_or_limit_take_profit"]
        take_profit_x_to_one = row_df.loc[index, "take_profit_x_to_one"]
        take_profit_when_sl_is_technical_3_to_1 = row_df.loc[index, "take_profit_when_sl_is_technical_3_to_1"]
        take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[index, "take_profit_when_sl_is_calculated_3_to_1"]

        take_profit_3_1 = np.nan
        if "take_profit_3_1" in row_df.columns:
            take_profit_3_1 = row_df.loc[index, "take_profit_3_1"]
        if is_not_nan(take_profit_3_1):
            price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0

        if stop_loss_is_technical:
            price_of_sl = row_df.loc[index, "technical_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
                price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
        if stop_loss_is_calculated:
            price_of_sl = row_df.loc[index, "calculated_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
                price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

        if market_or_limit_stop_loss == 'market':
            type_of_sl = 'market'
        if market_or_limit_stop_loss == 'limit':
            type_of_sl = 'limit'

        if market_or_limit_take_profit == 'market':
            type_of_tp = 'market'
        if market_or_limit_take_profit == 'limit':
            type_of_tp = 'limit'

        side_of_limit_order = row_df.loc[index, "side"]
        post_only_for_limit_tp_bool = False

        spot_cross_or_isolated_margin = ""

        spot_without_margin_bool = row_df.loc[index, "spot_without_margin"]
        cross_margin_bool = row_df.loc[index, "cross_margin"]
        isolated_margin_bool = row_df.loc[index, "isolated_margin"]

        if spot_without_margin_bool == True:
            spot_cross_or_isolated_margin = "spot"
        elif cross_margin_bool == True:
            spot_cross_or_isolated_margin = "cross"
        elif isolated_margin_bool == True:
            spot_cross_or_isolated_margin = "isolated"
        else:
            print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated")

        args = [exchange_id,
                trading_pair,
                price_of_sl,
                type_of_sl,
                amount_of_sl,
                price_of_tp,
                type_of_tp,
                amount_of_tp,
                post_only_for_limit_tp_bool,
                price_of_limit_order,
                amount_of_asset_for_entry,
                side_of_limit_order,
                                  spot_cross_or_isolated_margin]

        # convert all elements in the args list into string because this is how popen works
        args = convert_list_elements_to_string(args)

        # command_args = [sys.executable, 'place_limit_order_on_exchange_with_sl_and_tp.py'] + args
        # print("executing place_place_limit_order_on_exchange_with_sl_and_tp.py as popen ")

        command_args = [sys.executable, 'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
        print("executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")


        print("command_args")
        print(command_args)
        # Run the command using subprocess Popen

        process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    else:
        # run file that places sell stop market order

        trading_pair = base_slash_quote
        price_of_sl = 0
        price_of_tp = 0
        type_of_sl = None
        type_of_tp = None
        position_size_in_usd = row_df.loc[index, "position_size"]
        position_size_in_shares_of_asset = position_size_in_usd / current_price_of_asset
        amount_of_asset_for_entry = position_size_in_shares_of_asset
        price_of_buy_or_sell_market_stop_order = row_df.loc[index, "sell_order"]
        amount_of_sl = position_size_in_shares_of_asset
        amount_of_tp = position_size_in_shares_of_asset
        stop_loss_is_calculated = row_df.loc[index, "stop_loss_is_calculated"]
        stop_loss_is_technical = row_df.loc[index, "stop_loss_is_technical"]
        market_or_limit_stop_loss = row_df.loc[index, "market_or_limit_stop_loss"]

        market_or_limit_take_profit = row_df.loc[index, "market_or_limit_take_profit"]
        take_profit_x_to_one = row_df.loc[index, "take_profit_x_to_one"]
        take_profit_when_sl_is_technical_3_to_1 = row_df.loc[
            index, "take_profit_when_sl_is_technical_3_to_1"]
        take_profit_when_sl_is_calculated_3_to_1 = row_df.loc[
            index, "take_profit_when_sl_is_calculated_3_to_1"]

        spot_cross_or_isolated_margin = ""

        spot_without_margin_bool = row_df.loc[index, "spot_without_margin"]
        cross_margin_bool = row_df.loc[index, "cross_margin"]
        isolated_margin_bool = row_df.loc[index, "isolated_margin"]

        if spot_without_margin_bool == True:
            spot_cross_or_isolated_margin = "spot"
        elif cross_margin_bool == True:
            spot_cross_or_isolated_margin = "cross"
        elif isolated_margin_bool == True:
            spot_cross_or_isolated_margin = "isolated"
        else:
            print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated")

        take_profit_3_1 = np.nan
        if "take_profit_3_1" in row_df.columns:
            take_profit_3_1 = row_df.loc[index, "take_profit_3_1"]
        if is_not_nan(take_profit_3_1):
            price_of_tp = take_profit_3_1 * take_profit_x_to_one / 3.0

        if stop_loss_is_technical:
            price_of_sl = row_df.loc[index, "technical_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_technical_3_to_1):
                price_of_tp = take_profit_when_sl_is_technical_3_to_1 * take_profit_x_to_one / 3.0
        if stop_loss_is_calculated:
            price_of_sl = row_df.loc[index, "calculated_stop_loss"]
            if is_not_nan(take_profit_when_sl_is_calculated_3_to_1):
                price_of_tp = take_profit_when_sl_is_calculated_3_to_1 * take_profit_x_to_one / 3.0

        if market_or_limit_stop_loss == 'market':
            type_of_sl = 'market'
        if market_or_limit_stop_loss == 'limit':
            type_of_sl = 'limit'

        if market_or_limit_take_profit == 'market':
            type_of_tp = 'market'
        if market_or_limit_take_profit == 'limit':
            type_of_tp = 'limit'

        side_of_buy_or_sell_market_stop_order = row_df.loc[index, "side"]
        post_only_for_limit_tp_bool = False

        args = [exchange_id,
                trading_pair,
                stop_loss_is_calculated,
                stop_loss_is_technical,
                price_of_sl,
                type_of_sl,
                amount_of_sl,
                price_of_tp,
                type_of_tp,
                amount_of_tp,
                post_only_for_limit_tp_bool,
                price_of_buy_or_sell_market_stop_order,
                amount_of_asset_for_entry,
                side_of_buy_or_sell_market_stop_order,
                spot_cross_or_isolated_margin]

        # convert all elements in the args list into string because this is how popen works
        args = convert_list_elements_to_string(args)
        print("args")
        print(args)
        # command_args3 = [sys.executable, 'place_buy_or_sell_stop_order_with_sl_and_tp.py'] + args
        # #
        # print("4executing place_buy_or_sell_stop_order_with_sl_and_tp.py as popen ")

        command_args3 = [sys.executable,
                         'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
        print(
            "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

        print("command_args3")
        print(command_args3)

        # # #delete this when debug is finished
        # phrase_to_print="what is your name"
        # command_args2=[sys.executable, "test.py"]+[phrase_to_print]
        # print("command_args2")
        # print(command_args2)
        process = Popen(command_args3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def convert_to_necessary_types_values_from_bfr_dataframe(stop_loss_is_calculated,
                                                         stop_loss_is_technical,
                                                         price_of_sl,
                                                         amount_of_sl,
                                                         post_only_for_limit_tp_bool,
                                                         price_of_buy_or_sell_market_stop_order,
                                                         amount_of_asset_for_entry):
    stop_loss_is_calculated=bool(stop_loss_is_calculated)
    stop_loss_is_technical=bool(stop_loss_is_technical)
    price_of_sl=float(price_of_sl)
    amount_of_sl=float(amount_of_sl)
    post_only_for_limit_tp_bool=bool(post_only_for_limit_tp_bool)
    price_of_buy_or_sell_market_stop_order=float(price_of_buy_or_sell_market_stop_order)
    amount_of_asset_for_entry=float(amount_of_asset_for_entry)
    return stop_loss_is_calculated,stop_loss_is_technical,price_of_sl,\
        amount_of_sl,post_only_for_limit_tp_bool,\
        price_of_buy_or_sell_market_stop_order,amount_of_asset_for_entry

def convert_column_to_boolean(df, column_name):
    """
    Converts a specified column of a DataFrame from string type to boolean.
    Returns the modified DataFrame.
    """
    df[column_name] = df[column_name].astype(bool)
    print(f"{column_name} converted to bool")

    return df
def convert_list_elements_to_string(lst):
    """
    Converts all elements in a list to strings.
    """
    return [str(elem) for elem in lst]
def is_not_nan(value):
    return not math.isnan(value)
def delete_last_row(df):
    # Make a copy of the dataframe without the last row
    modified_df = df.iloc[:-1].copy()

    # Return the modified DataFrame
    return modified_df
def check_if_utc_midnight_has_arrived():
    current_time = datetime.datetime.utcnow().time()
    target_time = datetime.time(hour=0, minute=0, second=1)
    # Format the time object to exclude the decimal part
    current_time_str = current_time.strftime('%H:%M:%S')
    target_time_str = target_time.strftime('%H:%M:%S')
    print("current_time_str")
    print(current_time_str)
    print("target_time_str")
    print(target_time_str)


    if current_time_str == target_time_str:
        print("It's 00:00:01 UTC!")
        return True
    else:
        print("Not yet 00:00:01 UTC.")
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_ath(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period,
                                                                                      acceptable_backlash):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []
    list_with_tickers_ready_for_rebound_off_ath=[]
    list_with_tickers_ready_for_rebound_off_atl=[]

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                table_with_ohlcv_data_df = table_with_ohlcv_data_df.iloc[:-1]

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
                        table_with_ohlcv_data_df)

                if asset_type == 'spot':
                    continue
            except:
                traceback.print_exc()

            # truncated_high_and_low_table_with_ohlcv_data_df[["high","low"]]=table_with_ohlcv_data_df[["high","low"]].round(decimals=2)
            # print("truncated_high_and_low_table_with_ohlcv_data_df")
            # print ( truncated_high_and_low_table_with_ohlcv_data_df)
            # print ( "before_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df.head(10).to_string() )

            # truncate high and low to two decimal number

            table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()

            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            print('table_with_ohlcv_data_df.loc[0,"close"]')
            print(table_with_ohlcv_data_df.loc[0, "close"])

            last_close_price = get_last_close_price_of_asset(table_with_ohlcv_data_df)
            number_of_zeroes_in_price = count_zeros_number_with_e_notaton_is_acceptable(last_close_price)

            # round high and low to two decimal number
            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(number_of_zeroes_in_price + 3,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(number_of_zeroes_in_price + 3,))

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            number_of_all_rows_in_df = len(truncated_high_and_low_table_with_ohlcv_data_df)
            list_of_periods = list(range(20, number_of_all_rows_in_df, 20))
            list_of_periods.append(len(truncated_high_and_low_table_with_ohlcv_data_df))
            # print ( "number_of_all_rows_in_df" )
            # print ( number_of_all_rows_in_df )
            # print ( "list_of_periods" )
            # print ( list_of_periods )

            # for last_row_in_slice in list_of_periods:
            # print ( "last_row_in_slice" )
            # print ( last_row_in_slice )
            truncated_high_and_low_table_with_ohlcv_data_df_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df.tail(365 * 2)
            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            table_with_ohlcv_data_df_slice = initial_table_with_ohlcv_data_df.tail(365 * 2).copy()

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head(10).to_string() )
            #

            # print ( "truncated_high_and_low_table_with_ohlcv_data_df_slice" )
            # print ( truncated_high_and_low_table_with_ohlcv_data_df_slice.tail(10).to_string())

            all_time_high = truncated_high_and_low_table_with_ohlcv_data_df_slice["high"].max()
            all_time_low = truncated_high_and_low_table_with_ohlcv_data_df_slice["low"].min()

            # print("all_time_high")
            # print(all_time_high)
            # print("all_time_low")
            # print(all_time_low)
            ohlcv_df_with_low_equal_to_atl_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["low"] == all_time_low]
            ohlcv_df_with_high_equal_to_ath_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["high"] == all_time_high]

            ######################################################

            ###############################################

            # find rebound from ath
            if len(ohlcv_df_with_high_equal_to_ath_slice) > 1:

                print("ohlcv_df_with_high_equal_to_ath_slice")
                print(ohlcv_df_with_high_equal_to_ath_slice.to_string())
                # print ( "list_with_tickers_ready_for_rebound_off_ath" )
                # print ( list_with_tickers_ready_for_rebound_off_ath )
                ohlcv_df_with_high_equal_to_ath_slice = \
                    ohlcv_df_with_high_equal_to_ath_slice.rename(columns={"index": "index_column"})
                # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )

                print("1output")

                row_number_of_bpu1 = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[1]
                row_number_of_bsu = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[0]
                row_number_of_bpu2 = row_number_of_bpu1 + 1

                # check if the found ath is legit and no broken for the last 2 years
                ath_is_not_broken_for_a_long_time = True
                try:
                    number_of_days_where_ath_was_not_broken = 366 * 2
                    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                    ath_is_not_broken_for_a_long_time = check_ath_breakout(
                        table_with_ohlcv_data_df_slice_numpy_array,
                        number_of_days_where_ath_was_not_broken,
                        all_time_high,
                        row_number_of_bsu)
                    print(f"ath={all_time_high}")
                    print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

                except:
                    traceback.print_exc()

                if ath_is_not_broken_for_a_long_time == False:
                    continue

                # # check if the found atl is legit and no broken for the last 2 years
                # atl_is_not_broken_for_a_long_time = True
                # try:
                #     number_of_days_where_atl_was_not_broken = 366 * 2
                #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                #                                                            number_of_days_where_atl_was_not_broken,
                #                                                            all_time_low,
                #                                                            last_all_time_low_row_number)
                #     print(f"atl={all_time_low}")
                #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
                #
                # except:
                #     pass
                #
                # if atl_is_not_broken_for_a_long_time == False:
                #     continue

                #############################################

                # print("row_number_of_bsu")
                # print(row_number_of_bsu)
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                print("row_number_of_bpu2")
                print(row_number_of_bpu2)
                print("len(truncated_high_and_low_table_with_ohlcv_data_df)-1")
                print(len(truncated_high_and_low_table_with_ohlcv_data_df) - 1)

                print("2output")
                if row_number_of_bpu2 != len(truncated_high_and_low_table_with_ohlcv_data_df) - 1:
                    continue
                print("3output")
                # print ( "row_number_of_bsu" )
                # print ( row_number_of_bsu )
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                # print("row_number_of_bpu2")
                # print(row_number_of_bpu2)

                # get ohlcv of tvx with high and low truncated
                # open_of_tvx,high_of_tvx,low_of_tvx,close_of_tvx=\
                #     get_ohlc_of_tvx(truncated_high_and_low_table_with_ohlcv_data_df,
                #                      row_number_of_bpu1)
                # get ohlcv of bpu2 with high and low truncated
                open_of_bpu2, high_of_bpu2, low_of_bpu2, close_of_bpu2 = \
                    get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # atr = calculate_atr(atr_over_this_period,
                #                     table_with_ohlcv_data_df,
                #                     row_number_of_bpu1)
                advanced_atr = calculate_advanced_atr(advanced_atr_over_this_period,
                                                      table_with_ohlcv_data_df,
                                                      row_number_of_bpu1)
                # atr = round(atr, 20)
                # advanced_atr = round(advanced_atr, 20)

                low_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "open"]
                close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "close"]
                close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "close"]
                high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "high"]

                # get ohlcv of bsu, bpu1,bpu2, tvx
                # get ohlcv of bpu2
                # print ("table_with_ohlcv_data_df_2")
                # print (table_with_ohlcv_data_df.head(10).to_string())
                true_open_of_bpu2, true_high_of_bpu2, true_low_of_bpu2, true_close_of_bpu2 = \
                    get_ohlc_of_bpu2(table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # get ohlcv of tvx
                # open_of_bpu2 = high_of_bpu2 = low_of_bpu2 = close_of_bpu2 = volume_of_bpu2 = timestamp_of_bpu2 = False
                open_of_tvx = high_of_tvx = low_of_tvx = close_of_tvx = volume_of_tvx = timestamp_of_tvx = False
                # try:
                #     true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                #         get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                # except:
                #     pass
                # get ohlc of bsu, bpu1
                true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                # true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                # true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "high"]
                #
                # print("table_with_ohlcv_data_df_slice_in_ath")
                # print(table_with_ohlcv_data_df_slice.head(10).to_string())
                true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "open"]
                true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bsu, "close"]
                true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "close"]
                true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "high"]

                volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu, "volume"]
                volume_of_bpu1 = table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1, "volume"]
                volume_of_bpu2 = get_volume_of_bpu2(table_with_ohlcv_data_df,
                                                    row_number_of_bpu1)

                print("4output")

                # if all_time_high <= 1:
                #     if volume_of_bpu1 < 1000 or volume_of_bsu < 1000 or volume_of_bpu2 < 1000:
                #         continue
                # print("5output")
                # if volume_of_bpu1 < 750 or volume_of_bsu < 750 or volume_of_bpu2 < 750:
                #     continue
                print("6output")
                # if open_of_tvx>=close_of_bpu2:
                #     continue

                # if true_high_of_tvx<all_time_high-0.5*atr:
                #     continue

                timestamp_of_bpu2 = get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                                          row_number_of_bpu1)
                timestamp_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1, "Timestamp"]
                timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu, "Timestamp"]

                timestamp_of_bpu2_with_time, timestamp_of_bpu2_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu2)
                timestamp_of_bpu1_with_time, timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu1)
                timestamp_of_bsu_with_time, timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bsu)

                # print ( "high_of_bpu2" )
                # print ( high_of_bpu2 )

                # calcualte atr over 5 days before bpu2. bpu2 is not included
                # atr_over_this_period = 30

                asset_not_open_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level(acceptable_backlash, advanced_atr, open_of_bsu,
                                                                      open_of_bpu1, open_of_bpu2,
                                                                      high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                      low_of_bsu, low_of_bpu1, low_of_bpu2)
                asset_not_close_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level(acceptable_backlash, advanced_atr, close_of_bsu,
                                                                       close_of_bpu1, close_of_bpu2,
                                                                       high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                       low_of_bsu, low_of_bpu1, low_of_bpu2)

                # print("asset_not_open_into_level_bool")
                # print(asset_not_open_into_level_bool)
                # print("asset_not_close_into_level_bool")
                # print(asset_not_close_into_level_bool)

                print("7output")
                if not asset_not_open_into_level_bool:
                    continue
                print("8output")
                if not asset_not_close_into_level_bool:
                    continue

                if advanced_atr > 0:
                    backlash = abs(all_time_high - true_high_of_bpu2)
                    if (backlash <= advanced_atr * acceptable_backlash) and (all_time_high - high_of_bpu2) >= 0:
                        list_with_tickers_ready_for_rebound_off_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_with_tickers_ready_for_rebound_off_atl:
        return True
    elif stock_name in list_with_tickers_ready_for_rebound_off_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_atl(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period,
                                                                                      acceptable_backlash):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []
    list_with_tickers_ready_for_rebound_off_atl=[]
    list_with_tickers_ready_for_rebound_off_ath=[]

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                table_with_ohlcv_data_df = table_with_ohlcv_data_df.iloc[:-1]

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue



            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']



            print("exchange")
            print(exchange)
            # print("short_name")
            # print(short_name)

            # truncated_high_and_low_table_with_ohlcv_data_df[["high","low"]]=table_with_ohlcv_data_df[["high","low"]].round(decimals=2)
            # print("truncated_high_and_low_table_with_ohlcv_data_df")
            # print ( truncated_high_and_low_table_with_ohlcv_data_df)
            # print ( "before_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df.head(10).to_string() )

            # truncate high and low to two decimal number

            table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy()

            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round, args=(20,))
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round, args=(20,))

            # print('table_with_ohlcv_data_df.loc[0,"close"]')
            # print ( table_with_ohlcv_data_df.loc[0 , "close"] )

            last_close_price = get_last_close_price_of_asset(table_with_ohlcv_data_df)
            number_of_zeroes_in_price = count_zeros_number_with_e_notaton_is_acceptable(last_close_price)

            # round high and low to two decimal number
            truncated_high_and_low_table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply(round, args=(number_of_zeroes_in_price + 3,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round, args=(number_of_zeroes_in_price + 3,))

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            # number_of_all_rows_in_df=len(truncated_high_and_low_table_with_ohlcv_data_df)
            # list_of_periods=list(range(20,number_of_all_rows_in_df,20))
            # list_of_periods.append(len(truncated_high_and_low_table_with_ohlcv_data_df))
            # print ( "number_of_all_rows_in_df" )
            # print ( number_of_all_rows_in_df )
            # print ( "list_of_periods" )
            # print ( list_of_periods )

            # for last_row_in_slice in list_of_periods:
            # print ( "last_row_in_slice" )
            # print ( last_row_in_slice )
            truncated_high_and_low_table_with_ohlcv_data_df_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df.tail(365 * 2)
            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

            table_with_ohlcv_data_df_slice = initial_table_with_ohlcv_data_df.tail(365 * 2).copy()

            # print ( "initial_table_with_ohlcv_data_df" )
            # print ( initial_table_with_ohlcv_data_df.head(10).to_string() )
            #

            # print ( "truncated_high_and_low_table_with_ohlcv_data_df_slice" )
            # print ( truncated_high_and_low_table_with_ohlcv_data_df_slice )

            all_time_high = truncated_high_and_low_table_with_ohlcv_data_df_slice["high"].max()
            all_time_low = truncated_high_and_low_table_with_ohlcv_data_df_slice["low"].min()

            # print("all_time_high")
            # print(all_time_high)
            # print("all_time_low")
            # print(all_time_low)
            ohlcv_df_with_low_equal_to_atl_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["low"] == all_time_low]
            ohlcv_df_with_high_equal_to_ath_slice = \
                truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[
                    truncated_high_and_low_table_with_ohlcv_data_df_slice["high"] == all_time_high]

            ######################################################

            # find rebound from atl
            if len(ohlcv_df_with_low_equal_to_atl_slice) > 1:
                # list_with_tickers_ready_for_rebound_off_atl.append(stock_name)
                # print ( "ohlcv_df_with_low_equal_to_atl_slice" )
                # print ( ohlcv_df_with_low_equal_to_atl_slice )
                # print ( "list_with_tickers_ready_for_rebound_off_atl" )
                # print ( list_with_tickers_ready_for_rebound_off_atl )
                ohlcv_df_with_low_equal_to_atl_slice = \
                    ohlcv_df_with_low_equal_to_atl_slice.rename(columns={"index": "index_column"})
                # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )
                row_number_of_bpu1 = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[1]
                row_number_of_bsu = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[0]
                row_number_of_bpu2 = row_number_of_bpu1 + 1

                # check if the found atl is legit and no broken for the last 2 years
                last_all_time_low_row_number = row_number_of_bsu
                atl_is_not_broken_for_a_long_time = True
                try:
                    number_of_days_where_atl_was_not_broken = 366 * 2
                    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                    atl_is_not_broken_for_a_long_time = check_atl_breakout(
                        table_with_ohlcv_data_df_slice_numpy_array,
                        number_of_days_where_atl_was_not_broken,
                        all_time_low,
                        last_all_time_low_row_number)
                    print(f"atl={all_time_low}")
                    print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

                except:
                    traceback.print_exc()

                if atl_is_not_broken_for_a_long_time == False:
                    continue

                # print("row_number_of_bsu")
                # print(row_number_of_bsu)
                # print("row_number_of_bpu1")
                # print(row_number_of_bpu1)
                # print("row_number_of_bpu2")
                # print(row_number_of_bpu2)
                # print("len(truncated_high_and_low_table_with_ohlcv_data_df)-1")
                # print(len(truncated_high_and_low_table_with_ohlcv_data_df)-1)
                # print("len(truncated_high_and_low_table_with_ohlcv_data_df_slice)-1")
                # print(len(truncated_high_and_low_table_with_ohlcv_data_df_slice) - 1)

                if row_number_of_bpu2 != len(truncated_high_and_low_table_with_ohlcv_data_df) - 1:
                    continue
                # print ( "row_number_of_bpu1" )
                # print ( row_number_of_bpu1 )

                # get ohlcv of bsu, bpu1,bpu2, tvx from truncated high and low df
                # get ohlcv of bpu2 from NOT truncated high and low df
                open_of_bpu2 = high_of_bpu2 = low_of_bpu2 = close_of_bpu2 = False
                open_of_tvx = high_of_tvx = low_of_tvx = close_of_tvx = False
                try:
                    open_of_bpu2, high_of_bpu2, low_of_bpu2, close_of_bpu2 = \
                        get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1)
                except:
                    traceback.print_exc()

                # # get ohlcv of tvx from NOT truncated high and low df
                # try:
                #     open_of_tvx , high_of_tvx , low_of_tvx , close_of_tvx = \
                #         get_ohlc_of_tvx ( truncated_high_and_low_table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                # except:
                #     pass

                # if open_of_tvx==False:
                #
                #     print ( "row_number_of_bpu1" )
                #     print ( row_number_of_bpu1 )
                #     print ( "table_with_ohlcv_data_df" )
                #     print ( table_with_ohlcv_data_df.iloc[row_number_of_bpu1-5:row_number_of_bpu1+5,:].to_string () )
                #     #time.sleep(10000)

                # get ohlc of bsu, bpu1 from truncated high and low df
                low_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "open"]
                close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "close"]
                close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "close"]
                high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "high"]

                # get ohlcv of bsu, bpu1,bpu2, tvx
                # get ohlcv of bpu2
                true_open_of_bpu2, true_high_of_bpu2, true_low_of_bpu2, true_close_of_bpu2 = \
                    get_ohlc_of_bpu2(table_with_ohlcv_data_df,
                                     row_number_of_bpu1)

                # get ohlcv of tvx
                # true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                #     get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                #                       row_number_of_bpu1 )
                # get ohlc of bsu, bpu1
                true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "low"]
                true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1, "low"]
                true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "open"]
                true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "open"]
                true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bsu, "close"]
                true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "close"]
                true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu, "high"]
                true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                    row_number_of_bpu1, "high"]

                volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu, "volume"]
                volume_of_bpu1 = table_with_ohlcv_data_df.loc[row_number_of_bpu1, "volume"]
                volume_of_bpu2 = get_volume_of_bpu2(table_with_ohlcv_data_df, row_number_of_bpu1)

                # atr = calculate_atr ( atr_over_this_period ,
                #                       table_with_ohlcv_data_df ,
                #                       row_number_of_bpu1 )
                advanced_atr = calculate_advanced_atr(advanced_atr_over_this_period,
                                                      table_with_ohlcv_data_df,
                                                      row_number_of_bpu1)

                # atr = round ( atr ,20)
                # advanced_atr = round ( advanced_atr ,20)

                # print("true_low_of_bsu")
                # print(true_low_of_bsu)
                # print ( "true_low_of_bpu1" )
                # print ( true_low_of_bpu1 )
                # print ( "true_low_of_bpu2" )
                # print ( true_low_of_bpu2 )

                # if all_time_low<=1:
                #     if volume_of_bpu1 < 1000 or volume_of_bsu < 1000 or volume_of_bpu2 < 1000:
                #         continue
                #
                # if volume_of_bpu1<750 or volume_of_bsu<750 or volume_of_bpu2<750:
                #     continue

                # if open_of_tvx<=close_of_bpu2:
                #     continue
                #
                # if true_low_of_tvx > all_time_low + 0.5 * atr:
                #     continue

                timestamp_of_bpu2 = get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,
                                                          row_number_of_bpu1)
                timestamp_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1, "Timestamp"]
                timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu, "Timestamp"]

                timestamp_of_bpu2_with_time, timestamp_of_bpu2_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu2)
                timestamp_of_bpu1_with_time, timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bpu1)
                timestamp_of_bsu_with_time, timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp(
                    timestamp_of_bsu)

                # print ( "low_of_bpu2" )
                # print ( low_of_bpu2 )

                # calcualte atr over 5 days before bpu2. bpu2 is not included
                # atr_over_this_period = 30

                asset_not_open_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level(acceptable_backlash, advanced_atr, open_of_bsu,
                                                                      open_of_bpu1, open_of_bpu2,
                                                                      high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                      low_of_bsu, low_of_bpu1, low_of_bpu2)
                asset_not_close_into_level_bool = \
                    check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level(acceptable_backlash, advanced_atr, close_of_bsu,
                                                                       close_of_bpu1, close_of_bpu2,
                                                                       high_of_bsu, high_of_bpu1, high_of_bpu2,
                                                                       low_of_bsu, low_of_bpu1, low_of_bpu2)

                if not asset_not_open_into_level_bool:
                    continue

                if not asset_not_close_into_level_bool:
                    continue

                if advanced_atr > 0:
                    backlash = abs(true_low_of_bpu2 - all_time_low)
                    if (backlash <= advanced_atr * acceptable_backlash) and (low_of_bpu2 - all_time_low) >= 0:
                        stop_loss = all_time_low - (advanced_atr * 0.05)
                        calculated_backlash_from_advanced_atr = advanced_atr * 0.05
                        buy_order = all_time_low + (advanced_atr * 0.5)
                        take_profit_3_to_1 = buy_order + (advanced_atr * 0.5) * 3
                        take_profit_4_to_1 = buy_order + (advanced_atr * 0.5) * 4

                        # stop_loss = round(stop_loss, 3)
                        # calculated_backlash_from_advanced_atr = round(calculated_backlash_from_advanced_atr, 3)
                        # buy_order = round(buy_order, 3)
                        # take_profit_3_to_1 = round(take_profit_3_to_1, 3)
                        # take_profit_4_to_1 = round(take_profit_4_to_1, 3)

                        # advanced_atr = round(advanced_atr, 3)
                        # low_of_bsu = round(low_of_bsu, 3)
                        # low_of_bpu1 = round(low_of_bpu1, 3)
                        # low_of_bpu2 = round(low_of_bpu2, 3)
                        # close_of_bpu2 = round(close_of_bpu2, 3)

                        list_with_tickers_ready_for_rebound_off_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_with_tickers_ready_for_rebound_off_atl:
        return True
    elif stock_name in list_with_tickers_ready_for_rebound_off_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_one_bar(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]
            # print("last_two_years_of_data_but_one_last_day")
            # print(last_two_years_of_data_but_one_last_day.to_string())

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_one_last_day['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years

            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_atl_was_not_broken,
                    all_time_low,
                    last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            print(f"false_breakout_bar_row_number={false_breakout_bar_row_number}")
            print(f"last_all_time_low_row_number={last_all_time_low_row_number}")
            if false_breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            print(f"low_of_false_breakout_bar={low_of_false_breakout_bar}")
            print(f"all_time_low={all_time_low}")
            if low_of_false_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar <= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_false_breakout_bar <= open_of_false_breakout_bar:
                continue

            print(f"7found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_false_breakout_bar_row_number)

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            distance_between_current_atl_and_false_breakout_bar_open = \
                open_of_false_breakout_bar - all_time_low
            distance_between_current_atl_and_false_breakout_bar_close = \
                all_time_low - close_of_false_breakout_bar
            if distance_between_current_atl_and_false_breakout_bar_open == 0:
                continue

            if not (distance_between_current_atl_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)

            buy_order = all_time_low + (advanced_atr * 0.5)
            technical_stop_loss = low_of_false_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss
            take_profit_when_stop_loss_is_technical_3_to_1 = buy_order + (buy_order - technical_stop_loss) * 3
            take_profit_when_stop_loss_is_technical_4_to_1 = buy_order + (buy_order - technical_stop_loss) * 4
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # buy_order = round(buy_order, 3)
            # technical_stop_loss = round(technical_stop_loss, 3)
            # take_profit_when_stop_loss_is_technical_3_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_3_to_1, 3)
            # take_profit_when_stop_loss_is_technical_4_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_4_to_1, 3)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr, 3)

            # open_of_bar_next_day_after_false_breakout_bar = \
            #     round(open_of_bar_next_day_after_false_breakout_bar,20)
            # advanced_atr = \
            #     round(advanced_atr, 3)

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_one_bar(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_one_last_day['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_ath_was_not_broken,
                    all_time_high,
                    last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            #############################################

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if false_breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_false_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar >= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_false_breakout_bar >= open_of_false_breakout_bar:
                continue

            print(f"7found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)

            # if suppression_flag_for_lows==False:
            #     continue

            # print(f"last_n_lows_for_{stock_name}")
            # print(last_n_lows)
            #
            # print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_false_breakout_bar_row_number)

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            distance_between_current_ath_and_false_breakout_bar_open = \
                all_time_high - open_of_false_breakout_bar
            distance_between_current_ath_and_false_breakout_bar_close = \
                close_of_false_breakout_bar - all_time_high
            if distance_between_current_ath_and_false_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_two_bars(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_false_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after false_breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate false_breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate false_breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate false_breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate false_breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate false_breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate false_breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-false_breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-false_breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-false_breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-false_breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-false_breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-false_breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_two_last_days['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years

            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_atl_was_not_broken,
                    all_time_low,
                    last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический минимум был не ближе, чем 3 дня до пробоя
            if false_breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_false_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar >= all_time_low:
                continue
            print(f"5.5found_stock={stock_name}", f"atl={all_time_low}",
                  f"open_of_next_day_bar_after_break_out_bar={open_of_next_day_bar_after_break_out_bar}  ")
            if open_of_next_day_bar_after_break_out_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_next_day_bar_after_break_out_bar <= all_time_low:
                continue

            print(f"7found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"8found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_false_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar < close_of_false_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar < open_of_false_breakout_bar or \
                    high_of_next_day_bar_after_break_out_bar < high_of_false_breakout_bar:
                continue

            print(f"9found_stock={stock_name}")

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            # check that second false breakout bar does not open and close into level
            distance_between_current_atl_and_false_breakout_bar_open = \
                open_of_false_breakout_bar - all_time_low
            distance_between_current_atl_and_false_breakout_bar_close = \
                all_time_low - close_of_false_breakout_bar
            if distance_between_current_atl_and_false_breakout_bar_open == 0:
                continue

            print(f"10found_stock={stock_name}")

            if not (distance_between_current_atl_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            print(f"11found_stock={stock_name}")

            # check that second false breakout bar does not open and close into level
            distance_between_current_atl_and_next_day_bar_after_break_out_bar_open = \
                open_of_next_day_bar_after_break_out_bar - all_time_low
            distance_between_current_atl_and_next_day_bar_after_break_out_bar_close = \
                all_time_low - close_of_next_day_bar_after_break_out_bar
            if distance_between_current_atl_and_next_day_bar_after_break_out_bar_open == 0:
                continue

            print(f"12found_stock={stock_name}")

            if not (distance_between_current_atl_and_next_day_bar_after_break_out_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_next_day_bar_after_break_out_bar_close > advanced_atr * 0.05):
                continue

            print(f"13found_stock={stock_name}")

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            print(f"14found_stock={stock_name}")

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_two_bars(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                timeframe,
                                                                                                last_bitcoin_price,
                                                                                                advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            false_breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of false_breakout_bar
            timestamp_of_false_breakout_bar = last_two_years_of_data.loc[
                false_breakout_bar_row_number, 'Timestamp']
            open_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'open']
            high_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'high']
            low_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'low']
            close_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'close']
            volume_of_false_breakout_bar = last_two_years_of_data.loc[false_breakout_bar_row_number, 'volume']

            if pd.isna(open_of_false_breakout_bar) or pd.isna(close_of_false_breakout_bar) or \
                    pd.isna(low_of_false_breakout_bar) or pd.isna(high_of_false_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_two_last_days
            pre_false_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_two_last_days
            pre_false_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            timestamp_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'Timestamp']
            open_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'open']
            high_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'high']
            low_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'low']
            close_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[pre_false_breakout_bar_row_number, 'close']
            volume_of_pre_false_breakout_bar = pre_false_breakout_bar_df.loc[
                pre_false_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after false_breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of false_breakout_bar
            # print(f"Timestamp of candidate false_breakout bar: {timestamp_of_false_breakout_bar}")
            # print(f"Open of candidate false_breakout bar: {open_of_false_breakout_bar}")
            # print(f"High of candidate false_breakout bar: {high_of_false_breakout_bar}")
            # print(f"Low of candidate false_breakout bar: {low_of_false_breakout_bar}")
            # print(f"Close of candidate false_breakout bar: {close_of_false_breakout_bar}")
            # print(f"Volume of candidate false_breakout bar: {volume_of_false_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_false_breakout_bar
            # print(f"Timestamp of pre-false_breakout bar: {timestamp_of_pre_false_breakout_bar}")
            # print(f"Open of pre-false_breakout bar: {open_of_pre_false_breakout_bar}")
            # print(f"High of pre-false_breakout bar: {high_of_pre_false_breakout_bar}")
            # print(f"Low of pre-false_breakout bar: {low_of_pre_false_breakout_bar}")
            # print(f"Close of pre-false_breakout bar: {close_of_pre_false_breakout_bar}")
            # print(f"Volume of pre-false_breakout bar: {volume_of_pre_false_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_false_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(
                    table_with_ohlcv_data_df_slice_numpy_array,
                    number_of_days_where_ath_was_not_broken,
                    all_time_high,
                    last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            #############################################

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический максимум был не ближе, чем 3 дня до пробоя
            if false_breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_false_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_false_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_false_breakout_bar <= all_time_high:
                continue

            if open_of_next_day_bar_after_break_out_bar <= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            if close_of_next_day_bar_after_break_out_bar >= all_time_high:
                continue

            print(f"7found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)
            print(f"8found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_false_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar > close_of_false_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar > open_of_false_breakout_bar or \
                    low_of_next_day_bar_after_break_out_bar > low_of_false_breakout_bar:
                continue

            # print(f"open_of_false_breakout_bar={open_of_false_breakout_bar}")
            # print(
            #     f"close_of_false_breakout_bar={close_of_false_breakout_bar}")

            # check that first false breakout bar does not open and close into level
            distance_between_current_ath_and_false_breakout_bar_open = \
                all_time_high - open_of_false_breakout_bar
            distance_between_current_ath_and_false_breakout_bar_close = \
                close_of_false_breakout_bar - all_time_high
            if distance_between_current_ath_and_false_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_false_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_false_breakout_bar_close > advanced_atr * 0.05):
                continue

            # check that second false breakout bar does not open and close into level
            distance_between_current_ath_and_next_day_bar_after_break_out_bar_open = \
                all_time_high - open_of_next_day_bar_after_break_out_bar
            distance_between_current_ath_and_next_day_bar_after_break_out_bar_close = \
                close_of_next_day_bar_after_break_out_bar - all_time_high
            if distance_between_current_ath_and_next_day_bar_after_break_out_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_next_day_bar_after_break_out_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_next_day_bar_after_break_out_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_false_breakout_bar, date_of_pre_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_false_breakout_bar)
            date_and_time_of_false_breakout_bar, date_of_false_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_false_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            sell_order = all_time_high - (advanced_atr * 0.5)
            technical_stop_loss = max(high_of_false_breakout_bar, high_of_next_day_bar_after_break_out_bar) + (
                    0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_sell_order = technical_stop_loss - sell_order
            take_profit_when_stop_loss_is_technical_3_to_1 = sell_order - (technical_stop_loss - sell_order) * 3
            take_profit_when_stop_loss_is_technical_4_to_1 = sell_order - (technical_stop_loss - sell_order) * 4
            distance_between_technical_stop_loss_and_sell_order_in_atr = \
                distance_between_technical_stop_loss_and_sell_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss,20)
            # take_profit_when_stop_loss_is_technical_3_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_3_to_1,20)
            # take_profit_when_stop_loss_is_technical_4_to_1 = \
            #     round(take_profit_when_stop_loss_is_technical_4_to_1,20)

            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_sell_order_in_atr,20)
            # sell_order = round(sell_order,20)
            # advanced_atr = round(advanced_atr,20)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False


def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_day_two(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            print("include_last_day_in_bfr_model_assessment")
            print(include_last_day_in_bfr_model_assessment)
            print("type(include_last_day_in_bfr_model_assessment)")
            print(type(include_last_day_in_bfr_model_assessment))
            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_two_last_days
            pre_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_two_last_days
            pre_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_ath_was_not_broken,
                                                                       all_time_high,
                                                                       last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический максимум был не ближе, чем 3 дня до пробоя
            if breakout_bar_row_number - last_all_time_high_row_number < 3:
                print("breakout_bar_row_number - last_all_time_high_row_number < 3")
                print(f"breakout_bar_row_number={breakout_bar_row_number}")
                print(f"last_all_time_high_row_number={last_all_time_high_row_number}")
                print(f"high_of_last_all_time_high={high_of_last_all_time_high}")
                print(f"high_of_breakout_bar={high_of_breakout_bar}")
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                print('''last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high''')
                continue

            print(f"3found_stock={stock_name}")

            if high_of_breakout_bar <= all_time_high:
                print('''high_of_breakout_bar <= all_time_high''')
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar >= all_time_high:
                print('''open_of_breakout_bar >= all_time_high''')
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar <= all_time_high:
                print('''close_of_breakout_bar <= all_time_high''')
                continue

            print(f"6found_stock={stock_name}")

            # #cмотрим поджатие
            # number_of_bars_when_we_check_suppression_by_lows=3
            # last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            # suppression_flag = True
            # for i in range(len(last_n_lows) - 1):
            #     if last_n_lows[i + 1] < last_n_lows[i]:
            #         suppression_flag = False
            #         break
            # if suppression_flag==False:
            #     continue

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True

            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] < last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_closes_for_{stock_name}")
            print(last_n_closes)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar < close_of_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar < close_of_breakout_bar:
                continue

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_ath_and_breakout_bar_open = \
                all_time_high - open_of_breakout_bar
            distance_between_current_ath_and_breakout_bar_close = \
                close_of_breakout_bar - all_time_high
            if distance_between_current_ath_and_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)

            calculated_stop_loss = all_time_high - (advanced_atr * 0.05)
            buy_order = all_time_high + (advanced_atr * 0.5)
            take_profit_when_sl_is_calculated_3_to_1 = (buy_order - calculated_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_calculated_4_to_1 = (buy_order - calculated_stop_loss) * 4 + buy_order

            # round decimals for ease of looking at
            # buy_order = round(buy_order,20)
            # calculated_stop_loss = round(calculated_stop_loss,20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1,20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1,20)

            # plot all lines with advanced atr (stop loss is technical)
            technical_stop_loss = low_of_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss
            take_profit_when_sl_is_technical_3_to_1 = (buy_order - technical_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_technical_4_to_1 = (buy_order - technical_stop_loss) * 4 + buy_order
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss,20)
            # take_profit_when_sl_is_technical_3_to_1 = \
            #     round(take_profit_when_sl_is_technical_3_to_1,20)
            # take_profit_when_sl_is_technical_4_to_1 = \
            #     round(take_profit_when_sl_is_technical_4_to_1,20)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr,20)

            list_of_stocks_which_broke_ath.append(stock_name)

        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:


            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue


            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']



            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[
                next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue

            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_two_last_days['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_two_last_days[
                    last_two_years_of_data_but_two_last_days['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years
            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_atl_was_not_broken,
                                                                       all_time_low,
                                                                       last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            # проверяем, ближайший исторический минимум был не ближе, чем 3 дня до пробоя
            if breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            # # проверяем поджатие
            # suppression_flag=True
            # last_n_highs = list(last_two_years_of_data['high'].tail(3))
            # for i in range(len(last_n_highs) - 1):
            #     if last_n_highs[i + 1] > last_n_highs[i]:
            #         suppression_flag=False
            #         break
            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_two_last_days_array,
                                                                       pre_breakout_bar_row_number)

            if open_of_next_day_bar_after_break_out_bar > close_of_breakout_bar or \
                    close_of_next_day_bar_after_break_out_bar > close_of_breakout_bar:
                continue

            print(f"8found_stock={stock_name}")

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_atl_and_breakout_bar_open = \
                open_of_breakout_bar - all_time_low
            distance_between_current_atl_and_breakout_bar_close = \
                all_time_low - close_of_breakout_bar
            if distance_between_current_atl_and_breakout_bar_open == 0:
                continue

            print(f"9found_stock={stock_name}")

            if not (distance_between_current_atl_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            print(f"10found_stock={stock_name}")

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            print(f"11found_stock={stock_name}")
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            print(f"12found_stock={stock_name}")
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            print(f"13found_stock={stock_name}")
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar = \
                get_date_with_and_without_time_from_timestamp(
                    timestamp_of_next_day_bar_after_break_out_bar)
            print(f"14found_stock={stock_name}")

            list_of_stocks_which_broke_atl.append(stock_name)

        except:
            traceback.print_exc()

    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False


def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_the_next_day(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db = [stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # counter = counter + 1
            # print(f'{stock_name} is'
            #       f' number {counter} out of {len(list_of_tables_in_ohlcv_db)}\n')

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df = fetch_one_ohlcv_table(stock_name, timeframe, last_bitcoin_price)

            # ##########################
            # #delete this in the future
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################

            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue

            if table_with_ohlcv_data_df.empty:
                continue

            # print("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
            #             table_with_ohlcv_data_df)
            #
            #     # do not short unshortable assets
            #     # if asset_type == 'spot':
            # #                    continue
            #
            # except:
            #     traceback.print_exc()

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")
            #
            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_one_last_day['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # check if the found ath is legit and no broken for the last 2 years
            ath_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_ath_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                ath_is_not_broken_for_a_long_time = check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_ath_was_not_broken,
                                                                       all_time_high,
                                                                       last_all_time_high_row_number)
                print(f"ath={all_time_high}")
                print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if ath_is_not_broken_for_a_long_time == False:
                continue

            # # check if the found atl is legit and no broken for the last 2 years
            # atl_is_not_broken_for_a_long_time = True
            # try:
            #     number_of_days_where_atl_was_not_broken = 366 * 2
            #     table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
            #     atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
            #                                                            number_of_days_where_atl_was_not_broken,
            #                                                            all_time_low,
            #                                                            last_all_time_low_row_number)
            #     print(f"atl={all_time_low}")
            #     print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")
            #
            # except:
            #     pass
            #
            # if atl_is_not_broken_for_a_long_time == False:
            #     continue

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_high_row_number + 1:, "high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar <= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            # проверяем поджатие по лоям
            number_of_bars_when_we_check_suppression_by_lows = 3
            last_n_lows = list(last_two_years_of_data['low'].tail(number_of_bars_when_we_check_suppression_by_lows))
            suppression_flag_for_lows = True

            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_lows = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            last_n_lows = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            suppression_flag_for_closes = True
            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag_for_closes = False
                    break
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_breakout_bar_row_number)

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_ath_and_breakout_bar_open = \
                all_time_high - open_of_breakout_bar
            distance_between_current_ath_and_breakout_bar_close = \
                close_of_breakout_bar - all_time_high
            if distance_between_current_ath_and_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)

            calculated_stop_loss = all_time_high - (advanced_atr * 0.05)
            buy_order = all_time_high + (advanced_atr * 0.5)
            take_profit_when_sl_is_calculated_3_to_1 = (buy_order - calculated_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_calculated_4_to_1 = (buy_order - calculated_stop_loss) * 4 + buy_order

            # round decimals for ease of looking at
            # buy_order = round(buy_order, 20)
            # calculated_stop_loss = round(calculated_stop_loss, 20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1, 20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1, 20)

            # plot all lines with advanced atr (stop loss is technical)
            technical_stop_loss = low_of_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss

            take_profit_when_sl_is_technical_3_to_1 = (buy_order - technical_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_technical_4_to_1 = (buy_order - technical_stop_loss) * 4 + buy_order
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            # technical_stop_loss = round(technical_stop_loss, 20)
            # take_profit_when_sl_is_technical_3_to_1 = \
            #     round(take_profit_when_sl_is_technical_3_to_1, 20)
            # take_profit_when_sl_is_technical_4_to_1 = \
            #     round(take_profit_when_sl_is_technical_4_to_1, 20)
            # distance_between_technical_stop_loss_and_buy_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_buy_order_in_atr, 20)

            list_of_stocks_which_broke_ath.append(stock_name)
            print("list_of_stocks_which_broke_ath")
            print(list_of_stocks_which_broke_ath)
        except:
            traceback.print_exc()
    # check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False
def verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_the_next_day(include_last_day_in_bfr_model_assessment, stock_name,
                                                                                                                     timeframe,
                                                                                                                     last_bitcoin_price,
                                                                                                                     advanced_atr_over_this_period):
    list_of_tables_in_ohlcv_db=[stock_name]

    list_of_stocks_which_broke_ath = []
    list_of_stocks_which_broke_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            # counter = counter + 1
            # print(f'{stock_name} is'
            #       f' number {counter} out of {len(list_of_tables_in_ohlcv_db)}\n')

            # if stock_name not in ['BBBY', 'LAZR', 'LCID', 'RIVN', 'XERS'] :
            #     continue

            table_with_ohlcv_data_df=fetch_one_ohlcv_table(stock_name,timeframe,last_bitcoin_price)


            # ##########################
            # #delete this in the future in production
            # table_with_ohlcv_data_df=delete_last_row(table_with_ohlcv_data_df)
            # ##########################





            # if the df is empty do not continue the current loop
            if table_with_ohlcv_data_df.empty:
                continue



            if table_with_ohlcv_data_df.empty:
                continue

            # print("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0, "exchange"]
            # short_name = table_with_ohlcv_data_df.loc[0, 'short_name']

            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
            #             table_with_ohlcv_data_df)
            #
            #     # do not short unshortable assets
            #     # if asset_type == 'spot':
            # #                    continue
            #
            # except:
            #     traceback.print_exc()

            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            if include_last_day_in_bfr_model_assessment!=True:
                # Select all rows in last_two_years_of_data excluding the last row
                last_two_years_of_data = last_two_years_of_data.iloc[:-1]

            # Round ohlc and adjclose to 6 decimal places
            # last_two_years_of_data = last_two_years_of_data.round(
            #               {'open': 6, 'high': 6, 'low': 6, 'close': 6, 'adjclose': 6})

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-1]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last row
            last_two_years_of_data_but_one_last_day = last_two_years_of_data.iloc[:-1]

            # Find row number of last row in last_two_years_of_data_but_one_last_day
            pre_breakout_bar_row_number = last_two_years_of_data_but_one_last_day.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_one_last_day
            pre_breakout_bar_df = last_two_years_of_data_but_one_last_day.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())

            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            # if last_two_years_of_data.tail(30)['volume'].min() < 750:
            #     continue
            #
            # if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
            #     continue

            # find all time low in last_two_years_of_data_but_one_last_day
            all_time_low = last_two_years_of_data_but_one_last_day['low'].min()
            print(f"all_time_low: {all_time_low}")

            all_time_low_row_numbers = \
                last_two_years_of_data_but_one_last_day[
                    last_two_years_of_data_but_one_last_day['low'] == all_time_low].index

            last_all_time_low_row_number = all_time_low_row_numbers[-1]

            # check if the found atl is legit and no broken for the last 2 years
            atl_is_not_broken_for_a_long_time = True
            try:
                number_of_days_where_atl_was_not_broken = 366 * 2
                table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                atl_is_not_broken_for_a_long_time = check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                                                                       number_of_days_where_atl_was_not_broken,
                                                                       all_time_low,
                                                                       last_all_time_low_row_number)
                print(f"atl={all_time_low}")
                print(f"atl_is_not_broken_for_a_long_time for {stock_name}={atl_is_not_broken_for_a_long_time}")

            except:
                traceback.print_exc()

            if atl_is_not_broken_for_a_long_time == False:
                continue

            # Find timestamps of all_time_low rows and create list out of them
            all_time_low_timestamps = last_two_years_of_data_but_one_last_day.loc[all_time_low_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'Timestamp']
            open_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'open']
            high_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'high']
            low_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'low']
            close_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'close']
            volume_of_last_all_time_low = last_two_years_of_data_but_one_last_day.loc[
                last_all_time_low_row_number, 'volume']
            print(f"1found_stock={stock_name}")

            if breakout_bar_row_number - last_all_time_low_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_one_last_day.loc[
               last_all_time_low_row_number + 1:, "low"].min() < all_time_low:
                continue

            print(f"3found_stock={stock_name}")

            if low_of_breakout_bar >= all_time_low:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar <= all_time_low:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar >= all_time_low:
                continue

            print(f"6found_stock={stock_name}")

            # проверяем поджатие по хайам
            number_of_bars_when_we_check_suppression_by_highs = 3
            suppression_flag_for_highs = True
            last_n_highs = list(
                last_two_years_of_data['high'].tail(number_of_bars_when_we_check_suppression_by_highs))
            for i in range(len(last_n_highs) - 1):
                if last_n_highs[i + 1] > last_n_highs[i]:
                    suppression_flag_for_highs = False
                    break

            # проверяем поджатие по закрытиям
            number_of_bars_when_we_check_suppression_by_closes = 3
            suppression_flag_for_closes = True
            last_n_closes = list(
                last_two_years_of_data['close'].tail(number_of_bars_when_we_check_suppression_by_closes))
            for i in range(len(last_n_closes) - 1):
                if last_n_closes[i + 1] > last_n_closes[i]:
                    suppression_flag_for_closes = False
                    break

            # if suppression_flag==False:
            #     continue
            # print(f"last_n_highs_for_{stock_name}")
            # print(last_n_highs)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_one_last_day_array = last_two_years_of_data_but_one_last_day.to_numpy()

            advanced_atr = \
                calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                       last_two_years_of_data_but_one_last_day_array,
                                                                       pre_breakout_bar_row_number)

            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_atl_and_breakout_bar_open = \
                open_of_breakout_bar - all_time_low
            distance_between_current_atl_and_breakout_bar_close = \
                all_time_low - close_of_breakout_bar
            if distance_between_current_atl_and_breakout_bar_open == 0:
                continue

            if not (distance_between_current_atl_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_atl_and_breakout_bar_close > advanced_atr * 0.05):
                continue

            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_low_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)

            list_of_stocks_which_broke_atl.append(stock_name)
            print("list_of_stocks_which_broke_atl")
            print(list_of_stocks_which_broke_atl)

            # calculated_stop_loss = all_time_low + (advanced_atr * 0.05)
            # sell_order = all_time_low - (advanced_atr * 0.5)
            # take_profit_when_sl_is_calculated_3_to_1 = sell_order - (calculated_stop_loss - sell_order) * 3
            # take_profit_when_sl_is_calculated_4_to_1 = sell_order - (calculated_stop_loss - sell_order) * 4
            # # round decimals for ease of looking at
            # sell_order = round(sell_order, 20)
            # calculated_stop_loss = round(calculated_stop_loss, 20)
            # take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1, 20)
            # take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1, 20)
            #
            # # plot all lines with advanced atr (stop loss is technical)
            # technical_stop_loss = high_of_breakout_bar + (0.05 * advanced_atr)
            # distance_between_technical_stop_loss_and_sell_order = technical_stop_loss - sell_order
            # take_profit_when_sl_is_technical_3_to_1 = sell_order - (technical_stop_loss - sell_order) * 3
            # take_profit_when_sl_is_technical_4_to_1 = sell_order - (technical_stop_loss - sell_order) * 4
            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     distance_between_technical_stop_loss_and_sell_order / advanced_atr
            # # round technical stop loss and take profit for ease of looking at
            # # technical_stop_loss = round(technical_stop_loss,20)
            # # take_profit_when_sl_is_technical_3_to_1 = \
            # #     round(take_profit_when_sl_is_technical_3_to_1, 3)
            # # take_profit_when_sl_is_technical_4_to_1 = \
            # #     round(take_profit_when_sl_is_technical_4_to_1, 3)
            # distance_between_technical_stop_loss_and_sell_order_in_atr = \
            #     round(distance_between_technical_stop_loss_and_sell_order_in_atr, 20)
            #
            # df_with_level_atr_bpu_bsu_etc = pd.DataFrame()
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker"] = stock_name
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "exchange"] = exchange
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "model"] = "ПРОБОЙ_ATL_с_подтверждением_вход_на_следующий_день"
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "atl"] = all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "advanced_atr"] = advanced_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "advanced_atr_over_this_period"] = \
            #     advanced_atr_over_this_period
            # # df_with_level_atr_bpu_bsu_etc.loc[
            # #     0, "low_of_bsu"] = all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_bsu"] = open_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_bsu"] = high_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_bsu"] = low_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_bsu"] = close_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_bsu"] = volume_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "timestamp_of_bsu"] = timestamp_of_last_all_time_low
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_bsu"] = date_of_last_ath
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "timestamp_of_pre_breakout_bar"] = timestamp_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_pre_breakout_bar"] = date_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_pre_breakout_bar"] = open_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_pre_breakout_bar"] = high_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_pre_breakout_bar"] = low_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_pre_breakout_bar"] = close_of_pre_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_pre_breakout_bar"] = volume_of_pre_breakout_bar
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "human_date_of_breakout_bar"] = date_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "open_of_breakout_bar"] = open_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "high_of_breakout_bar"] = high_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "low_of_breakout_bar"] = low_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "close_of_breakout_bar"] = close_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "volume_of_breakout_bar"] = volume_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.at[0, "timestamp_of_breakout_bar"] = timestamp_of_breakout_bar
            # df_with_level_atr_bpu_bsu_etc.at[0, "human_date_of_breakout_bar"] = date_of_breakout_bar
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "min_volume_over_last_n_days"] = last_two_years_of_data['volume'].tail(
            #     count_min_volume_over_this_many_days).min()
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "count_min_volume_over_this_many_days"] = count_min_volume_over_this_many_days
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "sell_order"] = sell_order
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "calculated_stop_loss"] = calculated_stop_loss
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_calculated_3_to_1"] = take_profit_when_sl_is_calculated_3_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_calculated_4_to_1"] = take_profit_when_sl_is_calculated_4_to_1
            #
            # distance_between_calculated_stop_loss_and_sell_order = calculated_stop_loss - sell_order
            # distance_between_calculated_stop_loss_and_sell_order_in_atr = \
            #     distance_between_calculated_stop_loss_and_sell_order / advanced_atr
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "distance_between_calculated_stop_loss_and_sell_order_in_atr"] = \
            #     distance_between_calculated_stop_loss_and_sell_order_in_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "technical_stop_loss"] = technical_stop_loss
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_technical_3_to_1"] = take_profit_when_sl_is_technical_3_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_when_sl_is_technical_4_to_1"] = take_profit_when_sl_is_technical_4_to_1
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "distance_between_technical_sl_and_sell_order_in_atr"] = distance_between_technical_stop_loss_and_sell_order_in_atr
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "suppression_by_highs"] = suppression_flag_for_highs
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "number_of_bars_when_we_check_suppression_by_highs"] = number_of_bars_when_we_check_suppression_by_highs
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "suppression_by_closes"] = suppression_flag_for_closes
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "number_of_bars_when_we_check_suppression_by_closes"] = number_of_bars_when_we_check_suppression_by_closes
            #
            # try:
            #     asset_type, maker_fee, taker_fee, url_of_trading_pair = \
            #         get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(table_with_ohlcv_data_df)
            #
            #     df_with_level_atr_bpu_bsu_etc.at[0, "asset_type"] = asset_type
            #     df_with_level_atr_bpu_bsu_etc.at[0, "maker_fee"] = maker_fee
            #     df_with_level_atr_bpu_bsu_etc.at[0, "taker_fee"] = taker_fee
            #     df_with_level_atr_bpu_bsu_etc.at[0, "url_of_trading_pair"] = url_of_trading_pair
            #     df_with_level_atr_bpu_bsu_etc.at[0, "number_of_available_bars"] = number_of_available_days
            #     try:
            #         df_with_level_atr_bpu_bsu_etc.at[0, "trading_pair_is_traded_with_margin"] = \
            #             get_bool_if_asset_is_traded_with_margin(table_with_ohlcv_data_df)
            #     except:
            #         traceback.print_exc()
            # except:
            #     traceback.print_exc()
            #
            # # try:
            # #     #############################################
            # #     # add info to dataframe about whether level was broken on other exchanges
            # #     df_with_level_atr_bpu_bsu_etc = fill_df_with_info_if_atl_was_broken_on_other_exchanges(stock_name,
            # #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_0000,
            # #                                                                                            db_where_ohlcv_data_for_stocks_is_stored_1600,
            # #                                                                                            table_with_ohlcv_data_df,
            # #                                                                                            engine_for_ohlcv_data_for_stocks_0000,
            # #                                                                                            engine_for_ohlcv_data_for_stocks_1600,
            # #                                                                                            all_time_low,
            # #                                                                                            list_of_tables_in_ohlcv_db_1600,
            # #                                                                                            df_with_level_atr_bpu_bsu_etc,
            # #                                                                                            0)
            # # except:
            # #     traceback.print_exc()
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker_last_column"] = stock_name
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "ticker_will_be_traced_and_position_entered"] = False
            #
            # side = "sell"
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "side"] = side
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "stop_loss_is_technical"] = False
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "stop_loss_is_calculated"] = False
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "market_or_limit_stop_loss"] = 'market'
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "market_or_limit_take_profit"] = 'limit'
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "position_size"] = 0
            #
            # df_with_level_atr_bpu_bsu_etc.loc[
            #     0, "take_profit_x_to_one"] = 3
            #
            # # df_with_level_atr_bpu_bsu_etc.to_sql(
            # #     table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be,
            # #     engine_for_db_where_ticker_which_may_have_breakout_situations,
            # #     if_exists='append')
            # # print_df_to_file(df_with_level_atr_bpu_bsu_etc,
            # #                  'current_rebound_breakout_and_false_breakout')

        except:
            traceback.print_exc()

    # string_for_output = f"Список инструментов, которые сформировали модель ПРОБОЙ исторического минимума (с подтверждением)." \
    #                     f"Вход на следующий день после пробоя:\n" \
    #                     f"{list_of_stocks_which_broke_atl}\n\n"
    # # Use the function to create a text file with the text
    # # in the subdirectory "current_rebound_breakout_and_false_breakout"
    # create_text_file_and_writ_text_to_it(string_for_output,
    #                                      'current_rebound_breakout_and_false_breakout')


    print("list_of_stocks_which_broke_ath")
    print(list_of_stocks_which_broke_ath)
    print("list_of_stocks_which_broke_atl")
    print(list_of_stocks_which_broke_atl)

    #check if the stock_name fulfils all criteria for BFR models
    if stock_name in list_of_stocks_which_broke_atl:
        return True
    elif stock_name in list_of_stocks_which_broke_ath:
        return True
    else:
        return False

def get_base_slash_quote_from_stock_name_with_underscore_between_base_and_quote_and_exchange(
        stock_name_with_underscore_between_base_and_quote_and_exchange):
    base_underscore_quote=\
        stock_name_with_underscore_between_base_and_quote_and_exchange.split("_on_")[0]
    base_slash_quote=base_underscore_quote.replace("_","/")
    return base_slash_quote

def fetch_dataframe_from_google_spreadsheet(spread_sheet_title):
    json_file_name = 'aerobic-form-407506-39b825814c4a.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Define the path to the JSON file relative to the script's directory
    path_to_dir_where_json_file_is = os.path.join(current_directory, 'datasets', 'json_key_for_google')
    path_to_json = os.path.join(path_to_dir_where_json_file_is, json_file_name)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_json, scope)
    gc = gspread.authorize(credentials)
    print("authorize ok!")


    # Open the spreadsheet by its title
    spreadsheet = gc.open(spread_sheet_title)

    # Check if the worksheet exists
    # date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    worksheet_title = "BFR_models"
    worksheet = None
    for ws in spreadsheet.worksheets():
        if ws.title == worksheet_title:
            worksheet = ws
            print(f'Worksheet "{worksheet_title}" found!')
            break

    # Convert the data in the worksheet to a DataFrame
    data = worksheet.get_all_values()
    # Assuming 'data' is the list of lists obtained from the worksheet
    df_from_sheet = pd.DataFrame(data[1:], columns=data[0])
    df_from_sheet = convert_commas_to_points(df_from_sheet)
    df_from_sheet = convert_string_boolean(df_from_sheet)

    print("df_from_sheet1")
    print(df_from_sheet)

    return df_from_sheet

def convert_commas_to_points(df):
    # Define a function to handle conversion
    def convert_value(value):
        if isinstance(value, str) and ',' in value:
            try:
                return float(value.replace(',', '.'))
            except ValueError:
                return value  # Return the original value if the conversion fails
        else:
            return value  # Return the original value if it's not a string with a comma

    # Apply the conversion to the entire DataFrame using applymap
    return df.applymap(convert_value)

def convert_string_boolean(df):
    # Replace string values with boolean values
    df.replace({'TRUE': True, 'FALSE': False}, inplace=True)
    return df
if __name__=="__main__":
    # stock_name='BTC_USDT_on_binance'

    # database_name = "levels_formed_by_highs_and_lows_for_cryptos_0000"
    # df_with_bfr=\
    #     build_entire_df_of_assets_which_will_be_used_for_position_entry(database_name)

    spread_sheet_title='streamlit_app_google_sheet'
    df_with_bfr=fetch_dataframe_from_google_spreadsheet(spread_sheet_title)


    #if columns in the bfr dataframe are str we convert them to bool
    column_name_list_which_must_be_converted_from_str_to_bool=\
        ["stop_loss_is_technical","stop_loss_is_calculated","spot_without_margin","margin",
         "cross_margin","isolated_margin","include_last_day_in_bfr_model_assessment",
         "trading_pair_is_traded_with_margin","spot_asset_also_available_as_swap_contract_on_same_exchange",
         "suppression_by_closes","suppression_by_lows"]
    for column_name in column_name_list_which_must_be_converted_from_str_to_bool:
        try:
            df_with_bfr=convert_column_to_boolean(df_with_bfr, column_name)
        except:
            traceback.print_exc()

    utc_position_entry_time_list=list(df_with_bfr["utc_position_entry_time"])
    # Remove seconds and keep only hours and minutes
    utc_position_entry_time_list_without_seconds = [time_str.rsplit(':', 1)[0] for time_str in utc_position_entry_time_list]
    print("utc_position_entry_time_list")
    print(utc_position_entry_time_list)

    interpreter = sys.executable

    while True:
        current_utc_time = datetime.datetime.now(timezone.utc).strftime('%H:%M')
        current_utc_time_without_leading_zero = datetime.datetime.now(timezone.utc).strftime('%-H:%M')
        print("current_utc_time")
        print(current_utc_time)
        print("utc_position_entry_time_list_without_seconds")
        print(utc_position_entry_time_list_without_seconds)
        #delete "not" when in production
        if current_utc_time in utc_position_entry_time_list_without_seconds or\
                current_utc_time_without_leading_zero in utc_position_entry_time_list_without_seconds:
            #next bar print time has arrived
            print("desired time is now")
            # iterate over each row in df_with_bfr and verify that pair still satisfies the desired
            # criteria for bfr
            for index, row in df_with_bfr.iterrows():
                print("row1")
                print(pd.DataFrame(row).T.to_string())
                row_df=pd.DataFrame(row).T
                model_type=row_df.loc[index,"model"]



                stock_name_with_underscore_between_base_and_quote_and_exchange = \
                    row_df.loc[index, "ticker"]
                print("stock_name_with_underscore_between_base_and_quote_and_exchange")
                print(stock_name_with_underscore_between_base_and_quote_and_exchange)
                base_slash_quote=\
                    get_base_slash_quote_from_stock_name_with_underscore_between_base_and_quote_and_exchange(
                    stock_name_with_underscore_between_base_and_quote_and_exchange)

                exchange_id=row_df.loc[index, "exchange"]

                include_last_day_in_bfr_model_assessment=False
                include_last_day_in_bfr_model_assessment=row_df.loc[index, "include_last_day_in_bfr_model_assessment"]

                trade_status=row_df.loc[index, "trade_status"]
                if trade_status!="must_verify_if_bfr_conditions_are_fulfilled":
                    continue


                exchange_object = get_exchange_object6(exchange_id)
                advanced_atr_over_this_period = 30
                acceptable_backlash = 0.05
                timeframe = "1d"
                last_bitcoin_price = 30000
                count_min_volume_over_this_many_days = 7
                if model_type == "ПРОБОЙ_ATL_с_подтверждением_вход_на_следующий_день":
                    trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day = \
                        verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_the_next_day(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)
                    print("trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day")
                    print(trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day)

                    if trading_pair_is_ready_for_breakout_of_atl_situations_entry_point_next_day:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        sell_order_price = row_df.loc[index, "sell_order"]
                        if current_price_of_asset < sell_order_price:
                            # run file that places sell limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places sell stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)




                elif model_type == "ПРОБОЙ_ATH_с_подтверждением_вход_на_следующий_день":
                    trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day = \
                        verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_the_next_day(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)
                    print("trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day")
                    print(trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day)

                    if trading_pair_is_ready_for_breakout_of_ath_situations_entry_point_next_day:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        buy_order_price = row_df.loc[index, "buy_order"]
                        if current_price_of_asset > buy_order_price:
                            # run file that places buy limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            print("1side_of_limit_order")
                            print(side_of_limit_order)
                            print("1spot_cross_or_isolated_margin")
                            print(spot_cross_or_isolated_margin)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            print("1args")
                            print(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places buy stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)
                elif model_type == "ПРОБОЙ_ATL_с_подтверждением_вход_на_2й_день":
                    trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two = \
                        verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)
                    print("trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two")
                    print(trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two)

                    if trading_pair_is_ready_for_breakout_of_atl_position_entry_on_day_two:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        sell_order_price = row_df.loc[index, "sell_order"]
                        if current_price_of_asset < sell_order_price:
                            # run file that places sell limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places sell stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)




                elif model_type == "ПРОБОЙ_ATH_с_подтверждением_вход_на_2й_день":
                    trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two = \
                        verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_ath_position_entry_on_day_two(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)
                    print("trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two")
                    print(trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two)

                    if trading_pair_is_ready_for_breakout_of_ath_position_entry_on_day_two:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        buy_order_price = row_df.loc[index, "buy_order"]
                        buy_order_price=float(buy_order_price)
                        if current_price_of_asset > buy_order_price:
                            # run file that places buy limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places buy stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)

                elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATL_1Б":
                    trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar = \
                        verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_one_bar(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)

                    print("trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar")
                    print(trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar)

                    if trading_pair_is_ready_for_false_breakout_situations_of_atl_by_one_bar:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        buy_order_price = row_df.loc[index, "buy_order"]
                        if current_price_of_asset > buy_order_price:
                            # run file that places buy limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places buy stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)


                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print("5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)


                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


                            print("process")
                            print(process)

                elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATH_1Б":
                    trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar = \
                        verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_one_bar(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)

                    print("trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar")
                    print(trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar)

                    if trading_pair_is_ready_for_false_breakout_situations_of_ath_by_one_bar:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        sell_order_price = row_df.loc[index, "sell_order"]
                        if current_price_of_asset < sell_order_price:
                            # run file that places sell limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places sell stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)



                elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATL_2Б":
                    trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars = \
                        verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_atl_by_two_bars(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)

                    print("trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars")
                    print(trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars)

                    if trading_pair_is_ready_for_false_breakout_situations_of_atl_by_two_bars:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        buy_order_price = row_df.loc[index, "buy_order"]
                        if current_price_of_asset > buy_order_price:
                            # run file that places buy limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places buy stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)

                elif model_type == "ЛОЖНЫЙ_ПРОБОЙ_ATH_2Б":
                    trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars = \
                        verify_that_asset_is_still_on_the_list_of_found_models_false_breakout_situations_of_ath_by_two_bars(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period)

                    print("trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars")
                    print(trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars)

                    if trading_pair_is_ready_for_false_breakout_situations_of_ath_by_two_bars:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        sell_order_price = row_df.loc[index, "sell_order"]
                        if current_price_of_asset < sell_order_price:
                            # run file that places sell limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places sell stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)


                elif model_type == "ОТБОЙ_от_ATL":
                    trading_pair_is_ready_for_rebound_situations_off_atl = \
                        verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_atl(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period, acceptable_backlash)

                    print("trading_pair_is_ready_for_rebound_situations_off_atl")
                    print(trading_pair_is_ready_for_rebound_situations_off_atl)

                    if trading_pair_is_ready_for_rebound_situations_off_atl:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        buy_order_price = row_df.loc[index, "buy_order"]
                        if current_price_of_asset > buy_order_price:
                            # run file that places buy limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            #
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places buy stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)

                elif model_type == "ОТБОЙ_от_ATH":
                    trading_pair_is_ready_for_rebound_situations_off_ath = \
                        verify_that_asset_is_still_on_the_list_of_found_models_rebound_situations_off_ath(
                            include_last_day_in_bfr_model_assessment, stock_name_with_underscore_between_base_and_quote_and_exchange, timeframe,
                            last_bitcoin_price, advanced_atr_over_this_period, acceptable_backlash)
                    print("trading_pair_is_ready_for_rebound_situations_off_ath")
                    print(trading_pair_is_ready_for_rebound_situations_off_ath)

                    if trading_pair_is_ready_for_rebound_situations_off_ath:
                        current_price_of_asset = get_current_price_of_asset(
                            exchange_object, base_slash_quote)

                        sell_order_price = row_df.loc[index, "sell_order"]
                        if current_price_of_asset < sell_order_price:
                            # run file that places sell limit order
                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False
                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_limit_order, \
                                price_of_limit_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_limit_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_limit_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)

                            command_args = [sys.executable,
                                            'place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "executing place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args")
                            print(command_args)
                            # Run the command using subprocess Popen

                            process = Popen(command_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        else:
                            # run file that places sell stop market order

                            trading_pair = base_slash_quote

                            post_only_for_limit_tp_bool = False

                            amount_of_sl = 0
                            amount_of_tp = 0

                            price_of_sl, \
                                type_of_sl, \
                                price_of_tp, \
                                type_of_tp, \
                                side_of_buy_or_sell_market_stop_order, \
                                price_of_buy_or_sell_market_stop_order, \
                                spot_cross_or_isolated_margin, \
                                amount_of_asset_for_entry_in_quote_currency = return_args_for_placing_limit_or_stop_order(
                                row_df)

                            args = [exchange_id,
                                    trading_pair,
                                    price_of_sl,
                                    type_of_sl,
                                    amount_of_sl,
                                    price_of_tp,
                                    type_of_tp,
                                    amount_of_tp,
                                    post_only_for_limit_tp_bool,
                                    price_of_buy_or_sell_market_stop_order,
                                    amount_of_asset_for_entry_in_quote_currency,
                                    side_of_buy_or_sell_market_stop_order,
                                    spot_cross_or_isolated_margin]

                            # convert all elements in the args list into string because this is how popen works
                            args = convert_list_elements_to_string(args)
                            print("args")
                            print(args)

                            command_args7 = [sys.executable,
                                             'place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py'] + args
                            print(
                                "5executing place_buy_or_sell_stop_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.py as popen ")

                            print("command_args7")
                            print(command_args7)

                            process = Popen(command_args7, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                            print("process")
                            print(process)



                else:
                    print("no_bfr_model_yet")

            break
        else:
            # next bar print time has not yet arrived
            # for index, row in df_with_bfr.iterrows():
            #     print("row2")
            #     print(pd.DataFrame(row).T.to_string())
            #     row_df = pd.DataFrame(row).T
            #     model_type = row_df.loc[index, "model"]
            #
            #     print("model_type")
            #     print(model_type)
            print("desired time has not yet arrived")
            time.sleep(1)
            continue
        # time.sleep(1)

    # verify_that_asset_is_still_on_the_list_of_found_models_breakout_situations_of_atl_position_entry_on_day_two(stock_name)