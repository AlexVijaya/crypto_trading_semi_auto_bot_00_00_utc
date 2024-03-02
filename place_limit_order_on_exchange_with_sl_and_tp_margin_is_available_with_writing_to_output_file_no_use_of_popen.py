# import pprint
import time
import traceback
import sys
import os
import pprint
from datetime import datetime
# from before_entry_current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_current_price_of_asset
import pandas as pd
# from shitcoins_with_different_models import pd.read_sql_query
# from verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used import convert_column_to_boolean
# from verify_that_all_pairs_from_df_are_ready_for_bfr import convert_to_necessary_types_values_from_bfr_dataframe
# from api_config import api_dict_for_all_exchanges
# from create_order_on_crypto_exchange2 import get_exchange_object_when_api_is_used
import ccxt
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
# from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6
# from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_base_of_trading_pair
# from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_quote_of_trading_pair
import numpy as np
import streamlit as st
import toml
from pathlib import Path
# from verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used import fetch_dataframe_from_google_spreadsheet
from verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used import update_one_cell_in_google_spreadsheet_column_name_is_argument
from verify_that_all_pairs_from_df_are_ready_for_bfr_google_spreadsheed_is_used_popen_is_not_used import fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed
import datetime
# from datetime import timezone
def check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,trading_pair,file):


    exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)

    # Load available markets
    markets = exchange_object_where_api_is_required.load_markets()

    # Check if the specified trading_pair exists in the loaded markets
    if trading_pair in markets:
        # Retrieve the trading rules for the specified trading_pair
        market_for_trading_pair = markets[trading_pair]


        # Access the "orderTypes" list within the 'info' section of the dictionary
        order_types = market_for_trading_pair['info']['orderTypes']

        # Search if the word "MARKET" is present in the list
        if 'MARKET' in order_types:
            file.wrtie("'MARKET' order is present in the orderTypes list.")
            return True
        else:
            print("'MARKET' order is not present in the orderTypes list.")
            return False
    else:
        print(f"The trading pair {trading_pair} is not available on MEXC exchange.")
def return_args_for_placing_limit_or_stop_order(row_df,index):

    amount_of_asset_for_entry_in_quote_currency = row_df.loc[index, "position_size"]

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
def convert_back_from_string_args_to_necessary_types(price_of_sl,
                                                         amount_of_sl,
                                                         price_of_tp,
                                                         amount_of_tp,
                                                         post_only_for_limit_tp_bool,
                                                         price_of_limit_order_or_buy_or_sell_market_stop_order,
                                                         amount_of_asset_for_entry):
    # stop_loss_is_calculated=bool(stop_loss_is_calculated)
    # stop_loss_is_technical=bool(stop_loss_is_technical)
    price_of_sl=float(price_of_sl)
    amount_of_sl=float(amount_of_sl)
    price_of_tp = float(price_of_tp)
    amount_of_tp = float(amount_of_tp)
    post_only_for_limit_tp_bool=bool(post_only_for_limit_tp_bool)
    price_of_limit_order_or_buy_or_sell_market_stop_order=float(price_of_limit_order_or_buy_or_sell_market_stop_order)
    amount_of_asset_for_entry=float(amount_of_asset_for_entry)
    return price_of_sl, amount_of_sl, price_of_tp, amount_of_tp, post_only_for_limit_tp_bool,\
        price_of_limit_order_or_buy_or_sell_market_stop_order, amount_of_asset_for_entry
def convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,price_of_entry_order):
    amount_of_asset_for_entry_in_base_currency = float(amount_of_asset_for_entry_in_quote_currency) / float(
        price_of_entry_order)
    return amount_of_asset_for_entry_in_base_currency
def check_if_entry_price_is_between_sl_and_tp(file, price_of_sl,price_of_tp,order_price,side):
    entry_price_is_between_sl_and_tp=False
    if side == "buy":
        if price_of_tp>order_price and order_price>price_of_sl:
            entry_price_is_between_sl_and_tp=True
        else:
            entry_price_is_between_sl_and_tp=False

    elif side == "sell":
        if price_of_tp < order_price and order_price < price_of_sl:
            entry_price_is_between_sl_and_tp = True
        else:
            entry_price_is_between_sl_and_tp = False
    else:
        pass
        print("\n"+"unknown_side")
    print("\n"+"entry_price_is_between_sl_and_tp")
    print("\n"+str(entry_price_is_between_sl_and_tp))
    return entry_price_is_between_sl_and_tp
def get_current_timestamp_in_milliseconds():
    timestamp_ms = int(time.time() * 1000)
    return timestamp_ms

def get_current_timestamp_in_seconds():
    timestamp_s = int(time.time())
    return timestamp_s

def borrow_margin_loan_when_quote_currency_is_borrowed(file, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    borrowed_margin_loan = np.nan
    try:
        amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)
        print("\n"+"amount_of_quote_currency to be borrowed")
        print("\n"+str(amount_of_quote_currency))
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(
            get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair),
            amount_of_quote_currency, symbol=trading_pair, params=params)

        print("\n"+"borrowed_margin_loan_when_quote_currency_is_borrowed")
        print("\n"+str(borrowed_margin_loan))
    except ccxt.InsufficientFunds:
        print("\n"+str(traceback.format_exc()))
        raise SystemExit
    except Exception:
        print("\n"+str(traceback.format_exc()))
        raise SystemExit

    return borrowed_margin_loan

def borrow_margin_loan_when_base_currency_is_borrowed(file, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    borrowed_margin_loan = np.nan
    try:
        amount_of_base_currency = amount_of_asset_for_entry
        base = get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        print("\n"+"amount_of_base_currency to be borrowed")
        print("\n"+str(amount_of_base_currency))
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(base,
                                                                                  amount_of_base_currency,
                                                                                  symbol=trading_pair, params=params)

        print("\n"+"borrowed_margin_loan_when_base_currency_is_borrowed")
        print("\n"+str(borrowed_margin_loan))
    except ccxt.InsufficientFunds:
        print("\n"+str(traceback.format_exc()))
        raise SystemExit
    except Exception:
        print("\n"+str(traceback.format_exc()))
        raise SystemExit
    return borrowed_margin_loan
def calculate_total_amount_of_quote_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_quote_currency")
        print(trading_pair)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        total_in_quote_currency=margin_account[trading_pair][quote]['total']
        print("total_in_quote_currency")
        print(total_in_quote_currency)
        print("type(total_in_quote_currency)")
        print(type(total_in_quote_currency))


        # Return the borrowed amount of quote currency
        return total_in_quote_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"

def calculate_total_amount_of_base_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_base_currency")
        print(trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        total_in_base_currency=margin_account[trading_pair][base]['total']
        print("total_in_base_currency")
        print(total_in_base_currency)
        print("type(total_in_base_currency)")
        print(type(total_in_base_currency))


        # Return the borrowed amount of quote currency
        return total_in_base_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"
def calculate_used_amount_of_quote_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_quote_currency")
        print(trading_pair)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        used_in_quote_currency=margin_account[trading_pair][quote]['used']
        print("used_in_quote_currency")
        print(used_in_quote_currency)
        print("type(used_in_quote_currency)")
        print(type(used_in_quote_currency))


        # Return the borrowed amount of quote currency
        return used_in_quote_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"

def calculate_used_amount_of_base_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_base_currency")
        print(trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        used_in_base_currency=margin_account[trading_pair][base]['used']
        print("used_in_base_currency")
        print(used_in_base_currency)
        print("type(used_in_base_currency)")
        print(type(used_in_base_currency))


        # Return the borrowed amount of quote currency
        return used_in_base_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"
def calculate_free_amount_of_quote_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_quote_currency")
        print(trading_pair)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        free_in_quote_currency=margin_account[trading_pair][quote]['free']
        print("free_in_quote_currency")
        print(free_in_quote_currency)
        print("type(free_in_quote_currency)")
        print(type(free_in_quote_currency))


        # Return the borrowed amount of quote currency
        return free_in_quote_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"

def calculate_free_amount_of_base_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_base_currency")
        print(trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        free_in_base_currency=margin_account[trading_pair][base]['free']
        print("free_in_base_currency")
        print(free_in_base_currency)
        print("type(free_in_base_currency)")
        print(type(free_in_base_currency))


        # Return the borrowed amount of quote currency
        return free_in_base_currency
    except Exception as e:
        print(str(traceback.format_exc()))
        return f"Error: {str(e)}"
def calculate_debt_amount_of_quote_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("\n"+"margin_mode")
        print("\n"+str(margin_mode))
        # print("12margin_account")
        # pprint.pprint(margin_account)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)

        if margin_mode=="isolated":
            debt_in_quote_currency=margin_account[trading_pair][quote]['debt']
        else:
            debt_in_quote_currency = margin_account[quote]['debt']
        print("\n"+"debt_in_quote_currency")
        print("\n"+(str(debt_in_quote_currency)))

        # Return the borrowed amount of quote currency
        return debt_in_quote_currency
    except Exception as e:
        print("\n"+(str(traceback.format_exc())))
        return f"Error: {str(e)}"

def calculate_debt_amount_of_base_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })


        print("\n"+"trading_pair_in_calculate_amount_owed_of_base_currency")
        print("\n"+trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        if margin_mode=="isolated":
            debt_in_base_currency=margin_account[trading_pair][base]['debt']
        else:
            debt_in_base_currency = margin_account[base]['debt']
        print("\n"+"debt_in_base_currency")
        print("\n"+str(debt_in_base_currency))



        # Return the borrowed amount of quote currency
        return debt_in_base_currency
    except Exception as e:
        print("\n"+str(traceback.format_exc()))
        return f"Error: {str(e)}"
def repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    # amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)

    debt_amount_of_quote_currency=calculate_debt_amount_of_quote_currency(file, margin_mode,
                                                                          exchange_object_where_api_is_required,
                                                                          trading_pair)

    # code_for_interest=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
    # borrow_interest=\
    #     exchange_object_where_api_is_required.fetchBorrowInterest(code=code_for_interest,
    #                                                               symbol=trading_pair,
    #                                                               since=current_timestamp_in_milliseconds,
    #                                                               params=params)
    # print("borrow_interest")
    # print(borrow_interest)
    repaid_margin_loan = exchange_object_where_api_is_required.repayMargin(
        get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair),
        debt_amount_of_quote_currency, symbol=trading_pair, params=params)

    print("\n"+"margin_loan_when_quote_currency_is_borrowed has been repaid")
    print("\n"+repaid_margin_loan)
    return repaid_margin_loan

def repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    # amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)

    debt_amount_of_base_currency=calculate_debt_amount_of_base_currency(file, margin_mode,
                                                                          exchange_object_where_api_is_required,
                                                                          trading_pair)
    debt_amount_of_quote_currency = calculate_debt_amount_of_quote_currency(file, margin_mode,
                                                                          exchange_object_where_api_is_required,
                                                                          trading_pair)
    print("\n"+"debt_amount_of_base_currency")
    print("\n"+str(debt_amount_of_base_currency))
    print("\n"+"debt_amount_of_quote_currency")
    print("\n"+str(debt_amount_of_quote_currency))

    # code_for_interest=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
    # borrow_interest=\
    #     exchange_object_where_api_is_required.fetchBorrowInterest(code=code_for_interest,
    #                                                               symbol=trading_pair,
    #                                                               since=current_timestamp_in_milliseconds,
    #                                                               params=params)
    # print("borrow_interest")
    # print(borrow_interest)
    base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
    quote = get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
    print("\n"+"base")
    print("\n"+str(base))
    repaid_margin_loan = exchange_object_where_api_is_required.repayMargin(base,
        debt_amount_of_base_currency, symbol=trading_pair, params=params)

    print("\n"+"margin_loan_when_base_currency_is_borrowed has been repaid")
    print("\n"+str(repaid_margin_loan))
    return repaid_margin_loan

def get_origQty_from_list_of_dictionaries_with_all_orders(orders, order_id):
    start_time = time.perf_counter()

    if isinstance(orders,list):

        for order in orders:
            # print("\n" + "dict_of_open_cancelled_or_closed_orders")
            # print("\n" + str(dict_of_open_cancelled_or_closed_orders))
            # for order in dict_of_open_cancelled_or_closed_orders:
            # print("\n" + "order1")
            # print("\n" + str(order))
            # print("order_id_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['info']['origQty'] of {order['orderId']}")
            # print(order['info']['origQty'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'ordId' in order.keys() and 'orderId' not in order.keys():
                if order['ordId'] == order_id:
                    print("order1")
                    print(order)
                    # print("\n" + "'ordId' in order.keys() and 'orderId' not in order.keys()")
                    return order['info']['origQty']

                else:
                    continue

            elif 'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys():
                if order['info']['ordId'] == order_id:
                    print("order2")
                    print(order)
                    # print("\n" + "'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys()")
                    return order['info']['origQty']
                else:
                    continue
            elif 'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order3")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['info']['origQty']123")
                    # print(order['info']['origQty'])
                    return order['info']['origQty']
                else:
                    continue
            elif 'orderId' in order.keys() and 'ordId' not in order.keys():
                if order['orderId'] == order_id:
                    print("order4")
                    print(order)
                    # print("\n" + "'orderId' in order.keys() and 'ordId' not in order.keys()")
                    return order['info']['origQty']
                else:
                    continue
            #for gateio
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys() and "filled" not in order.keys():
                if order['info']['id'] == order_id and 'origQty' in order['info'].keys():
                    print("order5")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['info']['origQty']123")
                    # print(order['info']['origQty'])
                    return order['info']['origQty']
                else:
                    continue
            # for kucoin
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys():
                if order['info']['id'] == order_id and "filled" in order.keys():
                    print("order6")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['info']['origQty']123")
                    # print(order['info']['origQty'])
                    return order['filled']
                else:
                    continue
            else:
                print("\n" + "'orderId' 'ordId' do not fulfill necessary criteria")


    else:
        print("NOT isinstance(orders,list)")
        for order in orders:
            # print("order_id_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['info']['origQty'] of {order['orderId']}")
            # print(order['info']['origQty'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'orderId' in order.keys():
                if order['orderId'] == order_id:
                    print("order6")
                    print(order)
                    # print(
                    #     f"3The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['info']['origQty']

            elif 'orderId' in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order7")
                    print(order)

                    # print(
                    #     f"4The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['info']['origQty']

    # print("orders where 'is not in orders' may occur")
    # print(orders)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"5The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")


    return f"order_id={order_id} is not in orders"

def get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,orders, order_id):
    start_time = time.perf_counter()
    print("execution of get_order_status_from_list_of_dictionaries_with_all_orders")

    if isinstance(orders,list):

        for order in orders:
            # print("\n" + "dict_of_open_cancelled_or_closed_orders")
            # print("\n" + str(dict_of_open_cancelled_or_closed_orders))
            # for order in dict_of_open_cancelled_or_closed_orders:
            # print("\n" + "order1")
            # print("\n" + str(order))
            # print("order_id_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['status'] of {order['orderId']}")
            # print(order['status'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'ordId' in order.keys() and 'orderId' not in order.keys():
                if order['ordId'] == order_id:
                    print("order1")
                    print(order)
                    # print("\n" + "'ordId' in order.keys() and 'orderId' not in order.keys()")
                    return order['status']

                else:
                    continue

            elif 'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys():
                if order['info']['ordId'] == order_id:
                    print("order2")
                    print(order)
                    # print("\n" + "'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys()")
                    return order['status']
                else:
                    continue
            elif 'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order3")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['status']123")
                    # print(order['status'])
                    return order['status']
                else:
                    continue
            elif 'orderId' in order.keys() and 'ordId' not in order.keys():
                if order['orderId'] == order_id:
                    print("order4")
                    print(order)
                    # print("\n" + "'orderId' in order.keys() and 'ordId' not in order.keys()")
                    return order['status']
                else:
                    continue
            #for gateio
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys() and 'status' not in order.keys():
                if order['info']['id'] == order_id and 'status' in order['info'].keys():
                    print("order5")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['status']123")
                    # print(order['status'])
                    return order['info']['status']
                else:
                    continue
            #for kucoin
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys():

                if order['info']['id'] == order_id and 'status' in order.keys():
                    print("order6")
                    print(order)
                    # print("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # print("\n" + "order['status']123")
                    # print(order['status'])
                    return order['status']
                else:
                    continue
            else:
                print("\n" + "'orderId' 'ordId' do not fulfill necessary criteria")


    else:
        print("NOT isinstance(orders,list)")
        for order in orders:
            # print("order_id_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['status'] of {order['orderId']}")
            # print(order['status'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'orderId' in order.keys():
                if order['orderId'] == order_id:
                    print("order6")
                    print(order)
                    # print(
                    #     f"3The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['status']

            elif 'orderId' in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order7")
                    print(order)

                    # print(
                    #     f"4The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['info']['status']

    # print("orders where 'is not in orders' may occur")
    # print(orders)

    try:
        if exchange_object_where_api_is_required.name=="kucoin":
            return exchange_object_where_api_is_required.fetch_order_status(
                symbol=trading_pair,
                id=order_id,
                params={})
    except:
        traceback.print_exc()

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"5The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")


    return f"order_id={order_id} is not in orders"
def get_order_amount_from_list_of_dictionaries_with_all_orders(orders, order_id):
    start_time = time.perf_counter()
    print("execution of get_order_amount_from_list_of_dictionaries_with_all_orders")

    if isinstance(orders,list):

        for order in orders:
            # file.write("\n" + "dict_of_open_cancelled_or_closed_orders")
            # file.write("\n" + str(dict_of_open_cancelled_or_closed_orders))
            # for order in dict_of_open_cancelled_or_closed_orders:
            # file.write("\n" + "order1")
            # file.write("\n" + str(order))
            # print("order_id_inside_get_order_amount_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_amount_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['amount'] of {order['orderId']}")
            # print(order['amount'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'ordId' in order.keys() and 'orderId' not in order.keys():
                if order['ordId'] == order_id:
                    print("order1")
                    print(order)
                    # file.write("\n" + "'ordId' in order.keys() and 'orderId' not in order.keys()")
                    return order['amount']

                else:
                    continue

            elif 'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys():
                if order['info']['ordId'] == order_id:
                    print("order2")
                    print(order)
                    # file.write("\n" + "'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys()")
                    return order['amount']
                else:
                    continue
            elif 'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order3")
                    print(order)
                    # file.write("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # file.write("\n" + "order['amount']123")
                    # file.write(order['amount'])
                    return order['amount']
                else:
                    continue
            elif 'orderId' in order.keys() and 'ordId' not in order.keys():
                if order['orderId'] == order_id:
                    print("order4")
                    print(order)
                    # file.write("\n" + "'orderId' in order.keys() and 'ordId' not in order.keys()")
                    return order['amount']
                else:
                    continue
            #for gateio
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys() and 'amount' not in order.keys():
                if order['info']['id'] == order_id and 'amount' in order['info'].keys():
                    print("order5")
                    print(order)
                    # file.write("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # file.write("\n" + "order['amount']123")
                    # file.write(order['amount'])
                    return order['info']['amount']
                else:
                    continue
            #for kucoin
            elif 'id' in order['info'].keys() and 'ordId' not in order['info'].keys():

                if order['info']['id'] == order_id and 'amount' in order.keys():
                    print("order62")
                    print(order)
                    # file.write("\n" + "'orderId' in order['info'].keys() and 'ordId' not in order['info'].keys()")
                    # file.write("\n" + "order['amount']123")
                    # file.write(order['amount'])
                    return order['amount']
                else:
                    continue
            else:
                print("\n" + "'orderId' 'ordId' do not fulfill necessary criteria")


    else:
        file.write("NOT isinstance(orders,list)")
        for order in orders:
            # print("order_id_inside_get_order_amount_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_amount_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['amount'] of {order['orderId']}")
            # print(order['amount'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'orderId' in order.keys():
                if order['orderId'] == order_id:
                    print("order63")
                    print(order)
                    # print(
                    #     f"3The function get_order_amount_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['amount']

            elif 'orderId' in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    print("order7")
                    print(order)

                    # print(
                    #     f"4The function get_order_amount_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['info']['amount']

    # print("orders where 'is not in orders' may occur")
    # print(orders)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"5The function get_order_amount_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")


    return f"order_id={order_id} is not in orders"

def get_amount_of_free_base_currency_i_own(spot_balance, base_currency):
    amount_of_free_base_currency=spot_balance['free'][base_currency]
    return amount_of_free_base_currency
def get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(orders, order_id):
    start_time = time.perf_counter()
    order_dict = {}
    for order in orders:
        if 'orderId' in order.keys():
            order_dict[order['orderId']] = order
        elif 'orderId' in order['info'].keys():
            order_dict[order['info']['orderId']] = order['info']

    if order_id in order_dict:
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(
            f"1The function get_order_status_from_list_of_dictionaries_with_all_orders_sped_up took {duration} seconds to execute.")
        return order_dict[order_id]['status']

    print("orders where 'is not in orders' may occur")
    print(orders)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"2The function get_order_status_from_list_of_dictionaries_with_all_orders_sped_up took {duration} seconds to execute.")
    return f"order_id={order_id} is not in orders"

def get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(base_slash_quote: str)->str:
    base=base_slash_quote.split("/")[0]
    quote=base_slash_quote.split("/")[1]
    return base
def remove_slash_from_trading_pair_name(trading_pair: str)->str:
    trading_pair=trading_pair.replace("/","")
    return trading_pair
def get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(base_slash_quote: str)->str:
    base=base_slash_quote.split("/")[0]
    quote=base_slash_quote.split("/")[1]
    return quote
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

def get_public_api_key(exchange_id):
    # Load the secrets from the toml file
    # secrets = toml.load("secrets_with_api_private_and_public_keys_for_exchanges.toml")
    # public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    # api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    public_api_key = st.secrets['secrets'][f"{exchange_id}_api_key"]
    # api_secret = st.secrets['secrets'][f"{exchange_id}_api_secret"]

    return public_api_key
def get_exchange_object_where_api_is_required(exchange_id):
    # Load the secrets from the toml file
    # secrets = toml.load("secrets_with_api_private_and_public_keys_for_exchanges.toml")
    # public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    # api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    public_api_key = st.secrets['secrets'][f"{exchange_id}_api_key"]
    api_secret = st.secrets['secrets'][f"{exchange_id}_api_secret"]
    trading_password = None
    print("public_api_key")
    print(public_api_key)
    if exchange_id in ["kucoin","okex5"]:
        try:
            # trading_password = api_dict_for_all_exchanges[exchange_id]['trading_password']
            trading_password = st.secrets['secrets'][f"{exchange_id}_trading_password"]
        except:
            print(str(traceback.format_exc()))

    exchange_object_where_api_is_required = \
        get_exchange_object_with_api_key(exchange_name=exchange_id,
                                         public_api_key=public_api_key,
                                         api_secret=api_secret,
                                         trading_password=trading_password)
    return exchange_object_where_api_is_required
# def get_order_id(order):
#     return order['id']
def get_order_status(exchange_id,order_id,trading_pair):
    exchange_object_where_api_is_required=get_exchange_object_where_api_is_required(exchange_id)
    # Fetch the order from the exchange
    # try:
    #     order = exchange_object_where_api_is_required.fetch_order(order_id)
    # except ccxt.base.errors.ArgumentsRequired:
    order = exchange_object_where_api_is_required.fetch_order(order_id,trading_pair)

    # Return the order's status
    return order['status']
def convert_trading_pair_with_underscore_and_exchange_into_trading_pair_with_slash(trading_pair_with_underscore_and_exchange):
    trading_pair_with_underscore=trading_pair_with_underscore_and_exchange.split("_on_")[0]
    trading_pair_with_slash=trading_pair_with_underscore.replace("_","/")
    return trading_pair_with_slash
def get_price(exchange_object, trading_pair):
    if "_" in trading_pair:
        trading_pair = convert_trading_pair_with_underscore_and_exchange_into_trading_pair_with_slash(trading_pair)
    try:
        ticker = exchange_object.fetch_ticker(trading_pair)
        return ticker['last']  # Return the last price of the asset
    except:
        print(str(traceback.format_exc()))
def get_order_id(order):
    order_id=order['id']
    return order_id

def get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,spot_cross_or_isolated_margin,exchange_object_where_api_is_required):
    if exchange_object_where_api_is_required.id in ['binance',]:
        if spot_cross_or_isolated_margin=="spot":
            all_orders_on_spot_account = exchange_object_where_api_is_required.fetch_orders(symbol=trading_pair,
                                                                                            since=None, limit=None,
                                                                                            params={})
            return all_orders_on_spot_account
        elif spot_cross_or_isolated_margin=="cross":
            # sapi_get_margin_allorders works only for binance
            all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isCross': 'TRUE',
            })
            return all_orders_on_cross_margin_account
        elif spot_cross_or_isolated_margin=="isolated":
            # sapi_get_margin_allorders works only for binance
            all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE'})
            return all_orders_on_isolated_margin_account
        else:
            print(f"spot_cross_or_isolated_margin variable value problem")
            return None

    elif exchange_object_where_api_is_required.id in ['mexc3','mexc','lbank','lbank2']:
        if spot_cross_or_isolated_margin=="spot":
            # trading_pair="RPL/USDT"
            # print("trading_pair23")
            # print(trading_pair)
            # print("exchange_object_where_api_is_required23")
            # print(exchange_object_where_api_is_required)
            all_orders_on_spot_account = exchange_object_where_api_is_required.fetch_orders(symbol=trading_pair,
                                                                                            since=None, limit=None,
                                                                                            params={})
            print("all_orders_on_spot_account4")
            print(all_orders_on_spot_account)

            return all_orders_on_spot_account
        elif spot_cross_or_isolated_margin=="cross":
            # sapi_get_margin_allorders works only for binance
            all_orders_on_cross_margin_account = exchange_object_where_api_is_required.fetch_orders(symbol=trading_pair,
                                                                                            since=None, limit=None,params={'isCross': 'TRUE'})
            return all_orders_on_cross_margin_account
        elif spot_cross_or_isolated_margin=="isolated":
            # sapi_get_margin_allorders works only for binance
            all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.fetch_orders(symbol=trading_pair,
                                                                                            since=None, limit=None,params={'isIsolated': 'TRUE'})

            return all_orders_on_isolated_margin_account
        else:
            print(f"spot_cross_or_isolated_margin variable value problem")
            return None
    elif exchange_object_where_api_is_required.id in ['okex5',]:
        if spot_cross_or_isolated_margin == "spot":
            all_open_orders_on_spot_account=exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,since=None, limit=None,
                                                                                            params={})
            all_cancelled_orders_on_spot_account = exchange_object_where_api_is_required.fetchCanceledOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={})
            all_closed_orders_on_spot_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={})
            all_orders_on_spot_account=all_open_orders_on_spot_account+all_cancelled_orders_on_spot_account+all_closed_orders_on_spot_account
            return all_orders_on_spot_account
        elif spot_cross_or_isolated_margin=="cross":
            all_open_orders_on_cross_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isCross': 'TRUE'})
            all_cancelled_orders_on_cross_account = exchange_object_where_api_is_required.fetchCanceledOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isCross': 'TRUE'})
            all_closed_orders_on_cross_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isCross': 'TRUE'})
            all_orders_on_cross_account = all_open_orders_on_cross_account + all_cancelled_orders_on_cross_account + all_closed_orders_on_cross_account
            return all_orders_on_cross_account
        elif spot_cross_or_isolated_margin=="isolated":
            all_open_orders_on_isolated_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isIsolated': 'TRUE'})
            all_cancelled_orders_on_isolated_account = exchange_object_where_api_is_required.fetchCanceledOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isIsolated': 'TRUE'})
            all_closed_orders_on_isolated_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isIsolated': 'TRUE'})
            all_orders_on_isolated_account = all_open_orders_on_isolated_account + all_cancelled_orders_on_isolated_account + all_closed_orders_on_isolated_account
            return all_orders_on_isolated_account

    elif exchange_object_where_api_is_required.id in ['kucoin',]:
        if spot_cross_or_isolated_margin == "spot":
            all_open_orders_on_spot_account=exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,since=None, limit=None,
                                                                                            params={})
            # all_cancelled_orders_on_spot_account = exchange_object_where_api_is_required.fetchCanceledOrders(symbol=trading_pair,
            #                                                                                         since=None,
            #                                                                                         limit=None,
            #                                                                                         params={})
            all_closed_orders_on_spot_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={})
            all_orders_on_spot_account=all_open_orders_on_spot_account+all_closed_orders_on_spot_account
            return all_orders_on_spot_account
        elif spot_cross_or_isolated_margin=="cross":
            all_open_orders_on_cross_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isCross': 'TRUE'})
            # all_cancelled_orders_on_cross_account = exchange_object_where_api_is_required.fetchCanceledOrders(
            #     symbol=trading_pair,
            #     since=None,
            #     limit=None,
            #     params={'isCross': 'TRUE'})
            all_closed_orders_on_cross_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isCross': 'TRUE'})
            all_orders_on_cross_account = all_open_orders_on_cross_account + all_closed_orders_on_cross_account
            return all_orders_on_cross_account
        elif spot_cross_or_isolated_margin=="isolated":
            all_open_orders_on_isolated_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isIsolated': 'TRUE'})
            # all_cancelled_orders_on_isolated_account = exchange_object_where_api_is_required.fetchCanceledOrders(
            #     symbol=trading_pair,
            #     since=None,
            #     limit=None,
            #     params={'isIsolated': 'TRUE'})
            all_closed_orders_on_isolated_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isIsolated': 'TRUE'})
            all_orders_on_isolated_account = all_open_orders_on_isolated_account + all_closed_orders_on_isolated_account
            return all_orders_on_isolated_account
    elif exchange_object_where_api_is_required.id in ['gate','gateio']:
        if spot_cross_or_isolated_margin == "spot":
            all_open_orders_on_spot_account=exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,since=None, limit=None,
                                                                                            params={})
            all_cancelled_orders_on_spot_account = []
            all_closed_orders_on_spot_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={})
            all_orders_on_spot_account=all_open_orders_on_spot_account+all_cancelled_orders_on_spot_account+all_closed_orders_on_spot_account
            return all_orders_on_spot_account
        elif spot_cross_or_isolated_margin=="cross":
            all_open_orders_on_cross_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isCross': 'TRUE'})
            all_cancelled_orders_on_cross_account = []
            all_closed_orders_on_cross_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isCross': 'TRUE'})
            all_orders_on_cross_account = all_open_orders_on_cross_account + all_cancelled_orders_on_cross_account + all_closed_orders_on_cross_account
            return all_orders_on_cross_account
        elif spot_cross_or_isolated_margin=="isolated":
            all_open_orders_on_isolated_account = exchange_object_where_api_is_required.fetchOpenOrders(symbol=trading_pair,
                                                                                                    since=None,
                                                                                                    limit=None,
                                                                                                    params={'isIsolated': 'TRUE'})
            all_cancelled_orders_on_isolated_account = []
            all_closed_orders_on_isolated_account = exchange_object_where_api_is_required.fetchClosedOrders(
                symbol=trading_pair,
                since=None,
                limit=None,
                params={'isIsolated': 'TRUE'})
            all_orders_on_isolated_account = all_open_orders_on_isolated_account + all_cancelled_orders_on_isolated_account + all_closed_orders_on_isolated_account
            return all_orders_on_isolated_account

    else:
        print(f"{exchange_object_where_api_is_required.id} is not in list of exchanges for the if conditions above")
def place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account1(row_df, row_index,file, exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry_in_quote_currency,side_of_stop_market_order):
    output_file = "output_for_place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account1.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_spot_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print("\n"+f"12began writing to {file.name} at {datetime.datetime.now()}\n")
    try:
        print("\n"+str(exchange_id))
        print("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        print("\n"+str(traceback.format_exc()))

    print("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)

    # print(side_of_stop_market_order)
    # external_while_loop_break_flag=False
    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_stop_market_order)
    amount_of_tp = amount_of_asset_for_entry
    amount_of_sl = amount_of_asset_for_entry
    print("\n" + "amount_of_asset_for_entry_in_quote_currency=" + str(amount_of_asset_for_entry_in_quote_currency))
    print("\n" + "amount_of_asset_for_entry=" + str(amount_of_asset_for_entry))
    trade_status = row_df.loc[row_index, "trade_status"]

    print("trade_status1")
    print(trade_status)

    stop_market_or_limit_order_to_use_for_entry=row_df.loc[row_index, "stop_market_or_limit_order_to_use_for_entry"]
    print("stop_market_or_limit_order_to_use_for_entry")
    print(stop_market_or_limit_order_to_use_for_entry)



    # while True:
    current_price_of_trading_pair=get_price(exchange_object_without_api, trading_pair)
    print("current_price_of_trading_pair")
    print(current_price_of_trading_pair)
    if side_of_stop_market_order == "buy":
        # if current_price_of_trading_pair<price_of_stop_market_order:
        #     print("\n"+f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}")
        #     print(
        #         "\n" + f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}")
        #     print(
        #         "\n" + f"the price must be highter")
        #     # # time.sleep(1)
        #     return f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}"

        print("\n"+f"trying to place buy stop_market_order on {exchange_id}")

        market_buy_order_status_on_spot_margin = ""


        # we want to place a buy order with spot margin
        params = {}



        stop_market_buy_order = None
        order_id = ""

        if trade_status=="bfr_conditions_are_met" and current_price_of_trading_pair<price_of_stop_market_order:
            trade_status="stop_market_order_will_be_used"
            column_name = "trade_status"
            cell_value = "stop_market_order_will_be_used"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value

            stop_market_or_limit_order_to_use_for_entry = "stop_market_order"
            column_name = "stop_market_or_limit_order_to_use_for_entry"
            cell_value = stop_market_or_limit_order_to_use_for_entry
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value

        if trade_status=="bfr_conditions_are_met" and current_price_of_trading_pair>=price_of_stop_market_order:
            trade_status="limit_order_will_be_used"
            column_name = "trade_status"
            cell_value = "limit_order_will_be_used"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value


            stop_market_or_limit_order_to_use_for_entry = "limit_order"
            column_name = "stop_market_or_limit_order_to_use_for_entry"
            cell_value = stop_market_or_limit_order_to_use_for_entry
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value



        current_stop_market_or_limit_order_to_use_for_entry=\
            get_stop_market_or_limit_order_to_use_for_entry_from_df_given_row_index(row_index,df_with_bfr)

        print("current_stop_market_or_limit_order_to_use_for_entry1")
        print(current_stop_market_or_limit_order_to_use_for_entry)

        if current_stop_market_or_limit_order_to_use_for_entry not in ["limit_order","stop_market_order"]:
            return 'current_trade_status not in ["limit_order_will_be_used","stop_market_or_limit_order_to_use_for_entry"]'



        # ---------------------------------------------------------

        # ---------------------------------------------------------
        try:
            spot_balance = exchange_object_where_api_is_required.fetch_balance()
            print("\n" + "spot_balance")
            print("\n" + str(spot_balance))
        except:
            print(str(traceback.format_exc()))
            # Load the valid trading symbols
            try:
                exchange_object_where_api_is_required.load_markets()
                print("markets_loaded")
            except ccxt.BadRequest:
                traceback.print_exc()
                print(str(traceback.format_exc()))
            except Exception:
                traceback.print_exc()
                print(str(traceback.format_exc()))
        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        min_quantity = None
        try:
            # print("\n" + "symbol_details")
            # print("\n" + str(symbol_details))
            # print("\n" + "symbol_details['info']")
            # print("\n" + str(symbol_details['info']))
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(
                        price_of_stop_market_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_stop_market_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(
                    price_of_stop_market_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
        except:
            print("\n" + str(traceback.format_exc()))

        margin_mode="spot"

        # sys.exit(1)

        # we need current timestamp to get borrow interest since that timestamp to add this interest to the repay ammount
        # current_timestamp_in_milliseconds = get_current_timestamp_in_seconds()

        # ---------------------------------------------------------

        # amount_of_asset_for_entry=0
        stop_market_buy_order = ""
        try:

            # #borrow margin before creating an order. Borrow exactly how much your position is
            # margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(file, trading_pair,
            #                                                    exchange_object_without_api,
            #                                                    amount_of_asset_for_entry,
            #                                                    exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_quote_currency_is not borrowed because it is spot")
            # print(margin_loan_when_quote_currency_is_borrowed)

            # if borrowed_margin_loan['info']['code'] == 200:
            #     print("borrowed_margin_loan['info']['code'] == 200")
            #     print(borrowed_margin_loan['info']['code'] == 200)

            # amount_of_asset_for_entry = \
            #     convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
            #                                                     price_of_stop_market_order)

            print("\n"+"amount_of_asset_for_entry")
            print("\n"+str(amount_of_asset_for_entry))
            try:




                if trade_status=="stop_market_order_will_be_used" \
                        and current_price_of_trading_pair>=price_of_stop_market_order \
                        and stop_market_or_limit_order_to_use_for_entry == "stop_market_order":
                    print("\n" + "trying to place stop_market_buy_order")
                    print("\n" + "trying to place stop_market_buy_order")
                    if exchange_id in ['binance', 'binanceus']:
                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_buy_order(trading_pair,
                                                                                                       amount_of_asset_for_entry,
                                                                                                   # price_of_stop_market_order,
                                                                                                   params=params)
                        column_name = "trade_status"
                        cell_value = "placed_market_order_waiting_for_it_to_get_filled"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name, cell_value)
                        df_with_bfr[column_name].iat[row_index] = cell_value
                        print("df_with_bfr.to_string()")
                        print(df_with_bfr.to_string())
                        trade_status = cell_value

                        ###############################################
                        column_name = "entry_order_id"
                        cell_value = stop_market_buy_order['id']
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name,
                                                                                      cell_value)
                        #########################################

                    elif exchange_id in ['mexc3', 'huobi', 'huobipro','kucoin', 'mexc']:
                        prices = exchange_object_where_api_is_required.fetch_tickers()
                        ask = float(prices[trading_pair]['ask'])
                        amount = amount_of_asset_for_entry
                        print("\n" + "amount")
                        print("\n" + str(amount))
                        print("\n" + "ask")
                        print("\n" + str(ask))
                        print("amount1=",amount)


                        ###################################
                        ###################################
                        ###################################

                        # uncomment the following if you encounter market or "BadRequest mexc3 {"msg":"api market order is disabled","code":30019}"


                        # market_orders_are_allowed_on_exchange = \
                        #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                        #                                                                  trading_pair, file)
                        # if market_orders_are_allowed_on_exchange == False:
                        #
                        #     # imitation of market order buy placing a limit order
                        #     percantage_distance_between_ask_price_and_imitation_limit_order=0.05 # 0.05 means 5%
                        #     # plus should be minus if the limit is sell order
                        #     stop_market_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(
                        #         trading_pair, amount, ask+percantage_distance_between_ask_price_and_imitation_limit_order*ask, params=params)
                        #     print("\n" + "imitation limit_buy_order has been placed to imitate stop_market_buy_order")
                        #     stop_market_buy_order_order_id = get_order_id(stop_market_buy_order)
                        # elif market_orders_are_allowed_on_exchange == True:
                        #     stop_market_buy_order = exchange_object_where_api_is_required.create_market_order(
                        #     trading_pair, 'buy', amount,
                        #     price=ask)
                        # else:
                        #     print("\n" + "market_orders_are_allowed_on_exchange=" + f"{market_orders_are_allowed_on_exchange}")

                        ###################################
                        ###################################
                        ###################################

                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_order(
                            trading_pair, 'buy', amount,
                            price=ask)

                        column_name = "trade_status"
                        cell_value = "placed_market_order_waiting_for_it_to_get_filled"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name, cell_value)
                        df_with_bfr[column_name].iat[row_index] = cell_value
                        print("df_with_bfr.to_string()")
                        print(df_with_bfr.to_string())
                        trade_status = cell_value

                        # print("\n" + "stop_market_buy_order12")
                        # print("\n" + str(stop_market_buy_order))
                        ###############################################
                        column_name = "entry_order_id"
                        cell_value = stop_market_buy_order['id']
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name,
                                                                                      cell_value)
                        #########################################


                    else:
                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_buy_order(
                            trading_pair,
                            amount_of_asset_for_entry,
                            # price_of_stop_market_order,
                            params=params)

                        column_name = "trade_status"
                        cell_value = "placed_market_order_waiting_for_it_to_get_filled"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name, cell_value)
                        df_with_bfr[column_name].iat[row_index] = cell_value
                        print("df_with_bfr.to_string()")
                        print(df_with_bfr.to_string())
                        trade_status = cell_value

                        ###############################################
                        column_name = "entry_order_id"
                        cell_value = stop_market_buy_order['id']
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name,
                                                                                      cell_value)
                        #########################################

                    # print("\n" + "stop_market_buy_order")
                    # print("\n" + stop_market_buy_order)
                    # print("\n" + "stop_market_buy_order")
                    # print("\n" + stop_market_buy_order)
                    print("\n"+"created_stop_market_buy_order")

                # else:
                #     print('trade_status=="stop_market_order_will_be_used" \
                #         and current_price_of_trading_pair>=price_of_stop_market_order \
                #         and stop_market_or_limit_order_to_use_for_entry == "stop_market_order" this condition is not fulfilled')
                #     return "three conditions are not satisfied"

                if trade_status=="must_verify_if_bfr_conditions_are_fulfilled":
                    return "must_verify_if_bfr_conditions_are_fulfilled"

                list_of_possible_trade_status=["bfr_conditions_are_met","stop_market_order_will_be_used",
                                               "placed_market_order_waiting_for_it_to_get_filled",
                                               "must_verify_if_bfr_conditions_are_fulfilled",
                                               "placed_limit_buy_order_waiting_for_it_to_get_filled",
                                               "market_take_profit_has_been_filled",
                                               "waiting_for_price_to_reach_either_tp_or_sl",
                                               "limit_take_profit_has_been_filled",
                                               "limit_take_profit_has_been_placed",
                                               "market_take_profit_has_been_filled",
                                               "market_take_profit_has_been_placed",
                                               "stop_market_take_profit_has_been_filled",
                                               "limit_stop_loss_is_placed",
                                               "limit_stop_loss_is_filled",
                                               "market_stop_loss_is_placed",
                                               "market_stop_loss_is_filled",
                                               "stop_market_stop_loss_is_placed", "stop_market_stop_loss_is_used",
                                               "neither_sl_nor_tp_has_been_reached",
                                               "limit_order_has_been_cancelled","limit_buy_order_is_filled","limit_sell_order_is_filled"]
                if trade_status not in list_of_possible_trade_status:
                    print(f"{trade_status} not in list")
                    return f"{trade_status} not in list"
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                # repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                #                                                   exchange_object_without_api,
                #                                                   amount_of_asset_for_entry,
                #                                                   exchange_object_where_api_is_required, params)
                # external_while_loop_break_flag = True
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n" + "Invalid order: Filter failure: NOTIONAL")
                    print("\n" +
                               f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                               f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                               f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:


                print("\n"+str(traceback.format_exc()))
                print("\n"+str(traceback.format_exc()))
                # external_while_loop_break_flag = True
                # raise SystemExit
            print("\n"+f"placed buy stop market order on {exchange_id}")
            print("\n"+"stop_market_buy_order")
            print("\n"+str(stop_market_buy_order))

            # print("type(stop_market_buy_order)")
            # print(type(stop_market_buy_order))
            # order_id = stop_market_buy_order['id']
            # if pd.isna(stop_market_buy_order):
            #     order_id=df_with_bfr.loc[row_index,"entry_order_id"]
            #     print("order_id2")
            #     print(order_id)
            # else:
            #     order_id = stop_market_buy_order['id']
            #     print("order_id3")
            #     print(order_id)

            try:
                order_id = df_with_bfr.loc[row_index, "entry_order_id"]
                print("order_id2")
                print(order_id)
            except KeyError:
                try:
                    order_id = stop_market_buy_order['id']
                    print("order_id3")
                    print(order_id)
                except KeyError:
                    raise SystemExit
                    # import sys
                    # sys.exit("Exiting due to error in retrieving order ID")

            # order_id = stop_market_buy_order['id']
            # print("order_id3")
            # print(order_id)

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            if exchange_id in ["mexc3","mexc"]:
                orig_quantity = get_origQty_from_list_of_dictionaries_with_all_orders(all_orders_on_spot_account, order_id)
                amount_of_tp = orig_quantity
                amount_of_sl = orig_quantity
            else:
                orig_quantity = get_origQty_from_list_of_dictionaries_with_all_orders(all_orders_on_spot_account, order_id)
                # orig_quantity = stop_market_buy_order['info']['origQty']
                amount_of_tp = orig_quantity
                amount_of_sl = orig_quantity

            # # amount of tp sometimes is not equal to order amount
            # spot_balance = exchange_object_where_api_is_required.fetch_balance()
            # amount_of_tp = get_amount_of_free_base_currency_i_own(spot_balance, trading_pair.split("/")[0])
            # print("amount_of_tp_from_spot_balance")
            # print(amount_of_tp)
            # amount_of_sl = amount_of_tp

            # print("\n"+"order_id4")
            # print("\n"+str(order_id))
            # print("\n" + "orig_quantity")
            # print("\n" + str(orig_quantity))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            stop_market_buy_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_margin_account, order_id)
            print("\n"+"stop_market_buy_order_status_on_spot_margin1")
            print("\n"+str(stop_market_buy_order_status_on_spot_margin))
            # print("\n"+"stop_markett_buy_order['status']")
            # print("\n"+str(stop_market_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                # external_while_loop_break_flag = True
                raise SystemExit

        except:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_market_order_is_still_NEW_is_written_to_file = 0

        # wait till order is filled (that is closed)
        # while True:
        print("\n"+"waiting for the buy order to get filled")
        # sapi_get_margin_allorders works only for binance
        spot_cross_or_isolated_margin = "spot"
        all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                             spot_cross_or_isolated_margin,
                                                                                             exchange_object_where_api_is_required)
        # print("all_orders_on_spot_margin_account1")
        # pprint.pprint(all_orders_on_spot_margin_account)

        stop_market_buy_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
            all_orders_on_spot_margin_account, order_id)
        print("\n"+"stop_market_buy_order_status_on_spot")
        print("\n"+str(stop_market_buy_order_status_on_spot_margin))
        if stop_market_buy_order_status_on_spot_margin == "closed" or\
                stop_market_buy_order_status_on_spot_margin == "closed".upper() or\
                stop_market_buy_order_status_on_spot_margin == "FILLED":

            # place take profit right away as soon as stop_market order has been fulfilled
            limit_sell_order_tp_order_id = np.nan
            if trade_status != "market_order_is_filled_and_limit_tp_is_placed"  and trade_status!="limit_take_profit_has_been_filled"\
                    and trade_status!="market_stop_loss_is_placed" and trade_status!="market_stop_loss_is_filled":
                if trade_status != "neither_sl_nor_tp_has_been_reached":
                    print("\n" + "i will try to place limit_sell_order_tp right now")
                    print("\n" + "type_of_tp=" + f"{type_of_tp}")
                    if type_of_tp == "limit":
                        print("\n" + "amount_of_tp=" + f"{amount_of_tp}")
                        limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                            trading_pair, amount_of_tp, price_of_tp, params=params)
                        print("\n"+"limit_sell_order_tp has been placed")
                        # limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)

                        limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                        if pd.isna(limit_sell_order_tp):
                            limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                            print("limit_sell_order_tp_order_id123")
                            print(limit_sell_order_tp_order_id)
                        else:
                            limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                            print("limit_sell_order_tp_order_id1234")
                            print(limit_sell_order_tp_order_id)

                        column_name = "trade_status"
                        cell_value = "market_order_is_filled_and_limit_tp_is_placed"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                      cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "market_order_is_filled_and_limit_tp_is_placed"

                        ##############################################################
                        ##############################################################
                        column_name = "tp_order_id"
                        cell_value = limit_sell_order_tp_order_id
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                      cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                    ####################################


            # keep looking at the price and wait till either sl or tp has been reached
            # while True:

                if trade_status == "market_take_profit_has_been_filled":
                    return "market_take_profit_has_been_filled"
                if trade_status != "market_order_is_filled_and_limit_tp_is_placed" \
                        and trade_status != "neither_sl_nor_tp_has_been_reached":
                    return "limit_order_is_not_yet_filled"
                current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_trading_pair1")
                print(current_price_of_trading_pair)

                try:
                    # keep looking if limit take profit has been filled
                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)

                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print("current_price_of_trading_pair1")
                    print(current_price_of_trading_pair)

                    limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                        all_orders_on_spot_margin_account, limit_sell_order_tp_order_id)
                    # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                    #     all_orders_on_spot_account, limit_sell_order_tp_order_id)

                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print("current_price_of_trading_pair2")
                    print(current_price_of_trading_pair)

                    try:
                        if trade_status == 'neither_sl_nor_tp_has_been_reached':
                            limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                            print("limit_sell_order_tp_order_id12345678")
                            print(limit_sell_order_tp_order_id)
                    except:
                        traceback.print_exc()


                    if limit_sell_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                        print("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                        # repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                        #                                           exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)

                        # if repaid_margin_loan['info']['code'] == 200:
                        #     print("repaid_margin_loan['info']['code'] == 200")
                        #     print(repaid_margin_loan['info']['code'] == 200)

                        column_name = "trade_status"
                        cell_value = "limit_take_profit_has_been_filled"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name, cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "limit_take_profit_has_been_filled"

                        return "limit_take_profit_has_been_filled"
                    else:
                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("current_price_of_trading_pair3")
                        print(current_price_of_trading_pair)
                        print("\n" + f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                          f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                    print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print("current_price_of_trading_pair4")
                    print(current_price_of_trading_pair)
                    print("\n" + f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                    print(
                        "\n" + f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                    trade_status = "neither_sl_nor_tp_has_been_reached"
                    column_name = "trade_status"
                    cell_value = trade_status
                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                  cell_value)
                    df_with_bfr.at[row_index, column_name] = cell_value

                    # take profit has been reached
                    if current_price_of_trading_pair >= price_of_tp:
                        # if type_of_tp == "limit":
                        #     limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        #         trading_pair, amount_of_tp, price_of_tp, params=params)
                        #     print("limit_sell_order_tp has been placed")
                        # external_while_loop_break_flag = True
                        #     break
                        if type_of_tp == "market":
                            market_sell_order_tp = ""
                            if exchange_id in ['binance', 'binanceus']:
                                market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                    trading_pair, amount_of_tp, params=params)
                                column_name = "trade_status"
                                cell_value = "market_take_profit_has_been_filled"
                                update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                              column_name, cell_value)
                                df_with_bfr.at[row_index, column_name] = cell_value
                                trade_status = "market_take_profit_has_been_filled"
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                return "market_take_profit_has_been_filled"
                            if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                prices = exchange_object_where_api_is_required.fetch_tickers()
                                bid = float(prices[trading_pair]['bid'])
                                amount = amount_of_tp
                                market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                    trading_pair, 'sell', amount,
                                    price=bid)
                                column_name = "trade_status"
                                cell_value = "market_take_profit_has_been_filled"
                                update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                              column_name, cell_value)
                                df_with_bfr.at[row_index, column_name] = cell_value
                                trade_status = "market_take_profit_has_been_filled"
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                return "market_take_profit_has_been_filled"
                            else:
                                market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                    trading_pair, amount_of_tp, params=params)
                                column_name = "trade_status"
                                cell_value = "market_take_profit_has_been_filled"
                                update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                              column_name, cell_value)
                                df_with_bfr.at[row_index, column_name] = cell_value
                                trade_status = "market_take_profit_has_been_filled"
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                return "market_take_profit_has_been_filled"
                            # print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                            # print("\n" + "market_sell_order_tp has been placed")


                        elif type_of_tp == "stop":
                            stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                            print("\n"+"stop_market_sell_order_tp has been placed")
                            print("\n" + "stop_market_sell_order_tp has been placed")
                            column_name = "trade_status"
                            cell_value = "stop_market_take_profit_has_been_filled"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                          column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "stop_market_take_profit_has_been_filled"
                            return "stop_market_take_profit_has_been_filled"
                        elif type_of_tp == "limit":
                            print("\n"+"price of limit tp has been reached")
                        else:
                            print("\n"+f"there is no order called {type_of_tp}")

                    # stop loss has been reached
                    if trade_status == "stop_market_take_profit_has_been_filled" \
                            and trade_status == "market_take_profit_has_been_filled" \
                            and trade_status == "limit_take_profit_has_been_filled":
                        return "tp_is_filled"

                    print("current_price_of_trading_pair5")
                    print(current_price_of_trading_pair)
                    print("price_of_sl")
                    print(price_of_sl)

                    if current_price_of_trading_pair <= price_of_sl:
                        print("current_price_of_trading_pair <= price_of_sl")
                        if type_of_sl == "limit":
                            limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                trading_pair, amount_of_sl, price_of_sl, params=params)
                            print("\n"+"limit_sell_order_sl has been placed")

                            # cancel tp because sl has been hit

                            if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                   trading_pair, params=params)
                                print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                # # repay margin loan when stop loss is achieved
                                # repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                #                                       exchange_object_without_api,
                                #                                                   amount_of_asset_for_entry,
                                #                                                   exchange_object_where_api_is_required,
                                #                                                   params)

                                # if repaid_margin_loan['info']['code'] == 200:
                                #     print("repaid_margin_loan['info']['code'] == 200")
                                #     print(repaid_margin_loan['info']['code'] == 200)

                            column_name = "trade_status"
                            cell_value = "limit_stop_loss_is_placed"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                          column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "limit_stop_loss_is_placed"
                            return "limit_stop_loss_is_placed"
                        elif type_of_sl == "market":
                            print("\n" + "market_sell_order_sl is going to be placed")
                            try:
                                # market_sell_order_sl=\
                                    # exchange_object_where_api_is_required.sapiPostMarginOrder(remove_slash_from_trading_pair_name(trading_pair),
                                    #                                                           side = "sell",
                                    #                                                           type ="market",
                                    #                                                           quantity = amount_of_sl, isIsolated= True)
                                # exchange_object_where_api_is_required.sapiPostMarginOrder({"symbol":remove_slash_from_trading_pair_name(trading_pair),"side":'sell',"type":'market',"quantity":amount_of_sl, "isIsolted":True})
                                # print("1amount_of_sl")
                                # print(amount_of_sl)
                                # print("1params")
                                # print(params)

                                # we need to cancel tp first otherwise we will have insufficient funds to sell with sl.
                                # borrowed amount already locked in tp order
                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)

                                    print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                market_sell_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                    column_name = "trade_status"
                                    cell_value = "market_stop_loss_is_placed"
                                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr,
                                                                                                  row_index,
                                                                                                  column_name,
                                                                                                  cell_value)
                                    df_with_bfr.at[row_index, column_name] = cell_value
                                    trade_status = "market_stop_loss_is_placed"
                                    return "market_stop_loss_is_placed"
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_sl
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                    column_name = "trade_status"
                                    cell_value = "market_stop_loss_is_placed"
                                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr,
                                                                                                  row_index,
                                                                                                  column_name,
                                                                                                  cell_value)
                                    df_with_bfr.at[row_index, column_name] = cell_value
                                    trade_status = "market_stop_loss_is_placed"
                                    return "market_stop_loss_is_placed"
                                else:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                    column_name = "trade_status"
                                    cell_value = "market_stop_loss_is_placed"
                                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr,
                                                                                                  row_index,
                                                                                                  column_name,
                                                                                                  cell_value)
                                    df_with_bfr.at[row_index, column_name] = cell_value
                                    trade_status = "market_stop_loss_is_placed"
                                    return "market_stop_loss_is_placed"
                                # market_sell_order_sl=\
                                #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                # print("\n"+"market_sell_order_sl has been placed")

                                # # repay margin loan when stop loss is achieved
                                # repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                #                                                   exchange_object_without_api,
                                #                                                   amount_of_asset_for_entry,
                                #                                                   exchange_object_where_api_is_required,
                                #                                                   params)

                            except ccxt.InsufficientFunds:
                                print("\n"+str(traceback.format_exc()))
                            except Exception as e:
                                print("\n"+str(traceback.format_exc()))

                            # # cancel tp because sl has been hit
                            # if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                            #     print("4limit_sell_order_tp_order_status")
                            #     print(limit_sell_order_tp_order_status)
                            #     print("limit_sell_order_tp_order_id")
                            #     print(limit_sell_order_tp_order_id)
                            #     exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                            #                                                        trading_pair, params=params)
                            #     print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                            #
                            #     # repay margin loan when stop loss is achieved
                            #     repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                            #                                           exchange_object_without_api,
                            #                                                       amount_of_asset_for_entry,
                            #                                                       exchange_object_where_api_is_required,
                            #                                                       params)

                                # if repaid_margin_loan['info']['code'] == 200:
                                #     print("repaid_margin_loan['info']['code'] == 200")
                                #     print(repaid_margin_loan['info']['code'] == 200)

                            # external_while_loop_break_flag = True
                            # break
                        elif type_of_sl == "stop":

                            if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                   trading_pair, params=params)
                                print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                            stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                            print("\n" + "stop_market_sell_order_sl has been placed")

                            print("\n" + "stop_market_sell_order_sl has been placed")
                            column_name = "trade_status"
                            cell_value = "stop_market_stop_loss_is_placed"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                          column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "stop_market_stop_loss_is_placed"
                            return "stop_market_stop_loss_is_placed"

                                # # repay margin loan when stop loss is achieved
                                # repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                #                                       exchange_object_without_api,
                                #                                                   amount_of_asset_for_entry,
                                #                                                   exchange_object_where_api_is_required,
                                #                                                   params)

                                # if repaid_margin_loan['info']['code'] == 200:
                                #     print("repaid_margin_loan['info']['code'] == 200")
                                #     print(repaid_margin_loan['info']['code'] == 200)
                            # external_while_loop_break_flag = True
                            # break
                        else:
                            print("\n"+f"there is no order called {type_of_sl}")

                    # neither sl nor tp has been reached
                    else:
                        print("\n" + "neither sl nor tp has been reached")
                        column_name = "trade_status"
                        cell_value = "neither_sl_nor_tp_has_been_reached"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                                      column_name, cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "neither_sl_nor_tp_has_been_reached"
                        return "neither_sl_nor_tp_has_been_reached"
                except ccxt.RequestTimeout:
                    print("\n"+str(traceback.format_exc()))
                    # continue

            # stop waiting for the order to be filled because it has been already filled
            # external_while_loop_break_flag = True
            # break

        elif stop_market_buy_order_status_on_spot_margin in ["canceled", "cancelled", "canceled".upper(),
                                                           "cancelled".upper()]:
            print("\n" +
                       f"{order_id} order has been {stop_market_buy_order_status_on_spot_margin} so i will no longer wait for tp or sp to be achieved")
            column_name = "trade_status"
            cell_value = " stop_market_buy_order_has_been_cancelled"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                          cell_value)
            df_with_bfr.at[row_index, column_name] = cell_value
            trade_status = "stop_market_buy_order_has_been_cancelled"
            return "stop_market_buy_order_has_been_cancelled"
        else:
            # keep waiting for the order to fill
            if counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_market_order_is_still_NEW_is_written_to_file == 0 or \
                    counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_market_order_is_still_NEW_is_written_to_file % 10 == 0:
                counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_market_order_is_still_NEW_is_written_to_file = \
                    counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_market_order_is_still_NEW_is_written_to_file + 1
                # keep waiting for the order to fill
                string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW = \
                    "\n" + f"waiting for the order to fill because the status of {order_id} is still {stop_market_buy_order_status_on_spot_margin}"
                print(string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW)



    elif side_of_stop_market_order == "sell":
        # if current_price_of_trading_pair>price_of_stop_market_order:
        #     print("\n"+
        #         f"current price of {trading_pair} = {current_price_of_trading_pair} and it is > price_of_stop_market_order={price_of_stop_market_order}")
        #     # time.sleep(1)
        #     continue
        # else:

        print("\n"+f"placing sell stop_market_order on {exchange_id}")
        stop_market_sell_order = None
        stop_market_sell_order_status_on_spot_margin = ""
        order_id = ""
        params = {}
        min_quantity = None
        min_notional_value=None
        # Get the symbol details


        print("\n"+f"exchange_object_where_api_is_required={exchange_object_where_api_is_required}")


        # exchange_object_where_api_is_required.load_markets()
        # __________________________________
        # # show balance on spot
        # print("exchange_object_where_api_is_required.fetch_balance()")
        # print(exchange_object_where_api_is_required.fetch_balance())

        # show balance on cross margin
        # cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # # show balance on spot margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        print("going to load markets")
        exchange_object_where_api_is_required.load_markets()
        print("markets loaded")
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]
        print("symbol_details")
        print(str(symbol_details))
        try:
            # print("\n" + "symbol_details")
            # print("\n" + str(symbol_details))
            # print("\n" + "symbol_details['info']")
            # print("\n" + str(symbol_details['info']))
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(
                        price_of_stop_market_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_stop_market_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(
                    price_of_stop_market_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
        except:
            print("\n" + str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)

        # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("trading_pair")
        # print(trading_pair)
        # print("open_orders")
        # print(open_orders_on_cross_margin_account)
        # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
        # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("Orders")
        # print(Orders)


        margin_mode = "spot"
        amount_of_asset_for_entry = 0
        try:
            # # borrow margin before creating an order. Borrow exactly how much your position is
            # margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(
            #     trading_pair,
            #     exchange_object_without_api,
            #     amount_of_asset_for_entry,
            #     exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_base_currency_is not _borrowed because it is spot")
            # print(margin_loan_when_base_currency_is_borrowed)
            amount_of_asset_for_entry = \
                convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                                price_of_stop_market_order)

            try:
                # stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(trading_pair,
                #                                                                                  amount_of_asset_for_entry,
                #                                                                                  # price_of_stop_market_order,
                #                                                                                  params=params)
                if exchange_id in ['binance', 'binanceus']:
                    stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(trading_pair,
                                                                                                   amount_of_asset_for_entry,
                                                                                               # price_of_stop_market_order,
                                                                                               params=params)
                elif exchange_id in ['mexc3', 'huobi', 'huobipro']:
                    prices = exchange_object_where_api_is_required.fetch_tickers()
                    bid = float(prices[trading_pair]['bid'])
                    amount = amount_of_asset_for_entry
                    print("\n" + "amount")
                    print("\n" + str(amount))
                    print("\n" + "bid")
                    print("\n" + str(bid))
                    stop_market_sell_order = exchange_object_where_api_is_required.create_market_order(
                        trading_pair, 'sell', amount,
                        price=bid)
                    # print("\n" + "stop_market_sell_order12")
                    # print("\n" + str(stop_market_sell_order))
                else:
                    stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(
                        trading_pair,
                        amount_of_asset_for_entry,
                        # price_of_stop_market_order,
                        params=params)
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                #                                                   exchange_object_without_api,
                #                                                   amount_of_asset_for_entry,
                #                                                   exchange_object_where_api_is_required, params)
                external_while_loop_break_flag = True
                raise SystemExit

            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                    #                                                   exchange_object_without_api,
                    #                                                   amount_of_asset_for_entry,
                    #                                                   exchange_object_where_api_is_required, params)
                    external_while_loop_break_flag = True
                    raise SystemExit
            except Exception as e:

                # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                #                                                   exchange_object_without_api,
                #                                                   amount_of_asset_for_entry,
                #                                                   exchange_object_where_api_is_required, params)
                print("\n"+str(traceback.format_exc()))
                external_while_loop_break_flag = True
                raise SystemExit
            print("\n"+f"placed sell stop_market order on {exchange_id}")
            print("\n"+"stop_market_sell_order")
            print("\n"+str(stop_market_sell_order))

            order_id = stop_market_sell_order['id']
            if exchange_id in ["mexc3", "mexc"]:
                orig_quantity = stop_market_sell_order['info']['origQty']
                amount_of_tp = orig_quantity
                amount_of_sl = orig_quantity
            else:
                orig_quantity = stop_market_sell_order['info']['origQty']
                amount_of_tp = orig_quantity
                amount_of_sl = orig_quantity
            print("\n"+"order_id5")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            stop_market_sell_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_margin_account, order_id)
            print("\n"+"stop_market_sell_order_status_on_spot_margin1")
            print("\n"+str(stop_market_sell_order_status_on_spot_margin))
            print("\n"+"stop_market_sell_order['status']")
            print("\n"+str(stop_market_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                external_while_loop_break_flag = True
                raise SystemExit


        except Exception:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_margin_account1")
            # pprint.pprint(all_orders_on_spot_margin_account)

            stop_market_sell_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_margin_account, order_id)

            print("\n"+"stop_market_sell_order_status_on_spot_margin3")
            print("\n"+str(stop_market_sell_order_status_on_spot_margin))

            if stop_market_sell_order_status_on_spot_margin == "closed" or\
                    stop_market_sell_order_status_on_spot_margin == "closed".upper() or stop_market_sell_order_status_on_spot_margin == "FILLED":
                # place take profit right away as soon as stop_market order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)


                # keep looking at the price and wait till either sl or tp has been reached
                while True:
                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "spot"
                        all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_spot_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                            #                                                   exchange_object_without_api,
                            #                                                   amount_of_asset_for_entry,
                            #                                                   exchange_object_where_api_is_required, params)
                            # stop looking at the price to place stop loss because take profit has been filled
                            external_while_loop_break_flag = True
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")




                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_buy_order_tp has been placed")

                            #     break
                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_buy_order_tp has been placed")
                                external_while_loop_break_flag = True
                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                    #                                                   exchange_object_without_api,
                                    #                                                   amount_of_asset_for_entry,
                                    #                                                   exchange_object_where_api_is_required,
                                    #                                                   params)
                                external_while_loop_break_flag = True
                                break
                            elif type_of_sl == "market":
                                try:
                                    if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                        exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro','mexc']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        ask = float(prices[trading_pair]['ask'])
                                        amount = amount_of_sl
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'buy', amount,
                                            price=ask)
                                    else:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    print("\n"+"market_buy_order_sl has been placed")

                                    # repay margin loan when stop loss is achieved
                                    # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                    #                                                   exchange_object_without_api,
                                    #                                                   amount_of_asset_for_entry,
                                    #                                                   exchange_object_where_api_is_required,
                                    #                                                   params)

                                except ccxt.InsufficientFunds:
                                    print("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    print("\n"+str(traceback.format_exc()))
                                external_while_loop_break_flag = True
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                external_while_loop_break_flag = True
                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue
                # stop waiting for the order to be filled because it has been already filled
                external_while_loop_break_flag = True
                break

            elif stop_market_sell_order_status_on_spot_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {stop_market_sell_order_status_on_spot_margin} so i will no longer wait for tp or sp to be achieved")

                # # repay margin loan because the initial stop_market buy order has been cancelled
                # repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                #                                                   exchange_object_without_api,
                #                                                   amount_of_asset_for_entry,
                #                                                   exchange_object_where_api_is_required, params)
                external_while_loop_break_flag = True
                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {stop_market_sell_order_status_on_spot_margin}")
                # # time.sleep(1)
                continue


    else:
        print("\n"+f"unknown {side_of_stop_market_order} value")
    # if external_while_loop_break_flag == True:
    #     print("\n"+"external_while_loop_break_flag = True so while loop is breaking")
def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account(df_with_bfr,row_df, row_index, file, exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry_in_quote_currency,side_of_limit_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_spot_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print("\n"+f"12began writing to {os.path.abspath(file.name)} at {datetime.datetime.now()}\n")
    try:
        print("\n"+str(exchange_id))
        print("\n"+"\n")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("--------------------------------------------------")
        print("\n" + str(exchange_id))
        print("\n" + "\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
        print("\n" + "exchange_object_where_api_is_required="+ str(exchange_object_where_api_is_required))
    except Exception as e:
        print("\n"+str(traceback.format_exc()))
    print("\n"+"\n")
    print("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    print("\n"+"\n")
    # print("\n"+side_of_limit_order)
    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)
    amount_of_tp=amount_of_asset_for_entry
    amount_of_sl=amount_of_asset_for_entry
    print("\n" + "amount_of_asset_for_entry_in_quote_currency=" +str(amount_of_asset_for_entry_in_quote_currency))
    print("\n" + "amount_of_asset_for_entry=" +str(amount_of_asset_for_entry))

    trade_status = row_df.loc[row_index, "trade_status"]
    print("trade_status1")
    print(trade_status)

    stop_market_or_limit_order_to_use_for_entry = row_df.loc[row_index, "stop_market_or_limit_order_to_use_for_entry"]
    print("stop_market_or_limit_order_to_use_for_entry")
    print(stop_market_or_limit_order_to_use_for_entry)

    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)


    if side_of_limit_order == "buy":
        print("\n"+f"placing buy limit order on {exchange_id}")

        limit_buy_order_status_on_spot = ""
        order_id = ""


        params = {}

        limit_buy_order = None


        if trade_status=="bfr_conditions_are_met" and current_price_of_trading_pair>=price_of_limit_order:
            trade_status="limit_order_will_be_used"
            column_name = "trade_status"
            cell_value = "limit_order_will_be_used"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value


            stop_market_or_limit_order_to_use_for_entry = "limit_order"
            column_name = "stop_market_or_limit_order_to_use_for_entry"
            cell_value = stop_market_or_limit_order_to_use_for_entry
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value


        if trade_status=="bfr_conditions_are_met" and current_price_of_trading_pair<price_of_limit_order:
            trade_status="stop_market_order_will_be_used"
            column_name = "trade_status"
            cell_value = "stop_market_order_will_be_used"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value


            stop_market_or_limit_order_to_use_for_entry = "stop_market_order"
            column_name = "stop_market_or_limit_order_to_use_for_entry"
            cell_value = stop_market_or_limit_order_to_use_for_entry
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index,
                                                                          column_name, cell_value)
            df_with_bfr[column_name].iat[row_index] = cell_value

        current_stop_market_or_limit_order_to_use_for_entry=\
            get_stop_market_or_limit_order_to_use_for_entry_from_df_given_row_index(row_index,df_with_bfr)

        print("current_stop_market_or_limit_order_to_use_for_entry1")
        print(current_stop_market_or_limit_order_to_use_for_entry)

        if current_stop_market_or_limit_order_to_use_for_entry not in ["limit_order","stop_market_order"]:
            print('current_trade_status not in ["limit_order_will_be_used","stop_market_or_limit_order_to_use_for_entry"]')
            print(current_stop_market_or_limit_order_to_use_for_entry)
            return 'current_trade_status not in ["limit_order_will_be_used","stop_market_or_limit_order_to_use_for_entry"]'

        stop_market_or_limit_order_to_use_for_entry = row_df.loc[
            row_index, "stop_market_or_limit_order_to_use_for_entry"]
        if stop_market_or_limit_order_to_use_for_entry != "limit_order":
            return 'stop_market_or_limit_order_to_use_for_entry != "limit_order"'

        # ---------------------------------------------------------
        try:
            spot_balance = exchange_object_where_api_is_required.fetch_balance()
            print("\n"+"spot_balance")
            print("\n"+str(spot_balance))
            print("spot_balance")
            print(spot_balance)
        except:
            traceback.print_exc()
            print(str(traceback.format_exc()))

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("\n"+"isolated_margin_balance")
        # print("\n"+isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
            print("markets_loaded")
        except ccxt.BadRequest:
            traceback.print_exc()
            print(str(traceback.format_exc()))
        except Exception:
            traceback.print_exc()
            print(str(traceback.format_exc()))

        # Get the symbol details
        print("trading_pair123")
        print(trading_pair)
        public_api_key=get_public_api_key(exchange_id)
        print("public_api_key")
        print(public_api_key)
        print("exchange_object_where_api_is_required")
        print(exchange_object_where_api_is_required)
        # print("exchange_object_where_api_is_required.markets")
        # print(exchange_object_where_api_is_required.markets)
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        min_quantity = None
        try:
            # print("\n" + "symbol_details")
            # print("\n" + str(symbol_details))
            # print("\n" + "symbol_details['info']")
            # print("\n" + str(symbol_details['info']))
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity=symbol_details['limits']['amount']['min']
                min_notional_value=min_quantity*float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n"+"min_notional_value in USD")
                print("\n"+str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n"+
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n"+str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value=symbol_details['limits']['cost']['min']
                min_quantity=min_notional_value/float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value=symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value=min_notional_value/float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity=symbol_details['limits']['amount']['min']
                min_notional_value_in_usd=min_quantity*float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n"+"min_notional_value in USD")
                print("\n"+str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n"+
                    f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n"+str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw=min_quantity_raw*float(price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
        except:
            print("\n"+str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isIsolated': 'TRUE'})
        # print("closed_orders_on_isolated")
        # pprint.pprint(closed_orders)

        # spot_cross_or_isolated_margin = "spot"
        # all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
        #                                                                              spot_cross_or_isolated_margin,
        #                                                                              exchange_object_where_api_is_required)
        # print("all_orders_on_spot_account")
        # pprint.pprint(all_orders_on_spot_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_spot_account = exchange_object_where_api_is_required.fetch_open_orders(
        #     symbol=trading_pair, since=None, limit=None, params={})

        # print("open_orders_on_spot_account")
        # pprint.pprint(open_orders_on_spot_account)

        # ---------------------------------------------------------
        try:
            try:
                print("trade_status2")
                print(trade_status)
                if trade_status=="limit_order_will_be_used" \
                        and  current_price_of_trading_pair>=price_of_limit_order \
                        and stop_market_or_limit_order_to_use_for_entry == "limit_order":
                    limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                                   amount_of_asset_for_entry,
                                                                                                   price_of_limit_order,
                                                                                                   params=params)
                    print("limit_buy_order1")
                    print(limit_buy_order)
                    column_name="trade_status"
                    cell_value="placed_limit_buy_order_waiting_for_it_to_get_filled"
                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                    df_with_bfr[column_name].iat[row_index]=cell_value
                    print("df_with_bfr.to_string()")
                    print(df_with_bfr.to_string())
                    trade_status="placed_limit_buy_order_waiting_for_it_to_get_filled"


                    ###############################################
                    column_name = "entry_order_id"
                    cell_value = limit_buy_order['id']
                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                  cell_value)
                    #########################################

                # else:
                #     print('trade_status=="limit_order_will_be_used" \
                #         and  current_price_of_trading_pair>=price_of_limit_order \
                #         and stop_market_or_limit_order_to_use_for_entry == "limit_order" this condition is not satisfied')
                #     return "three condtions are not met"

                if trade_status=="must_verify_if_bfr_conditions_are_fulfilled":
                    return "must_verify_if_bfr_conditions_are_fulfilled"

                list_of_possible_trade_status=["bfr_conditions_are_met","limit_order_will_be_used",
                                               "must_verify_if_bfr_conditions_are_fulfilled",
                                               "placed_limit_buy_order_waiting_for_it_to_get_filled",
                                               "market_take_profit_has_been_filled",
                                               "waiting_for_price_to_reach_either_tp_or_sl",
                                               "limit_take_profit_has_been_filled",
                                               "limit_take_profit_has_been_placed",
                                               "market_take_profit_has_been_filled",
                                               "market_take_profit_has_been_placed",
                                               "stop_market_take_profit_has_been_filled",
                                               "limit_stop_loss_is_placed",
                                               "limit_stop_loss_is_filled",
                                               "market_stop_loss_is_placed",
                                               "market_stop_loss_is_filled",
                                               "stop_market_stop_loss_is_placed",
                                               "neither_sl_nor_tp_has_been_reached",
                                               "limit_order_has_been_cancelled","limit_buy_order_is_filled","limit_sell_order_is_filled"]
                if trade_status not in list_of_possible_trade_status:
                    print(f"{trade_status} not in list")
                    return f"{trade_status} not in list"


            except ccxt.InsufficientFunds:
                print("\n"+str(traceback.format_exc()))
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception:
                print("\n" + str(traceback.format_exc()))

            print("\n"+f"placed buy limit order on {exchange_id}")
            print("\n"+"limit_buy_order1")
            print("\n"+str(limit_buy_order))

            if pd.isna(limit_buy_order):
                order_id=df_with_bfr.loc[row_index,"entry_order_id"]
            else:
                order_id = limit_buy_order['id']

            print("\n"+"order_id")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                             spot_cross_or_isolated_margin,
                                                                                             exchange_object_where_api_is_required)
            # print("\n" + "all_orders_on_spot_account")
            # print("\n" + str(all_orders_on_spot_account))
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)
            try:
                if "not in orders" in limit_buy_order_status_on_spot and exchange_id!="gateio":

                    limit_buy_order_status_on_spot = exchange_object_where_api_is_required.fetch_order_status(symbol=trading_pair,
                                                                                                    id=order_id,
                                                                                                    params={})
            except:
                traceback.print_exc()

            print("\n"+"limit_buy_order_status_on_spot1")
            print("\n"+str(limit_buy_order_status_on_spot))
            # print("\n"+"limit_buy_order['status']")
            # print("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit

        except ccxt.InsufficientFunds:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        except:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file=0
        # wait till order is filled (that is closed)
        # while True:


        print("\n"+"waiting for the buy order to get filled")
        # sapi_get_margin_allorders works only for binance
        spot_cross_or_isolated_margin = "spot"
        all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                     spot_cross_or_isolated_margin,
                                                                                     exchange_object_where_api_is_required)
        # print("all_orders_on_spot_account1")
        # pprint.pprint(all_orders_on_spot_account)

        limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
            all_orders_on_spot_account, order_id)
        try:
            if "not in orders" in limit_buy_order_status_on_spot and exchange_id!="gateio":
                limit_buy_order_status_on_spot = exchange_object_where_api_is_required.fetch_order_status(
                    symbol=trading_pair,
                    id=order_id,
                    params={})
        except:
            traceback.print_exc()

        # if counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file==0 or\
        #         counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file % 10==0:
        print("\n"+"limit_buy_order_status_on_spot")
        print("\n"+limit_buy_order_status_on_spot)
        print("\n" + f"amount_of_tp={amount_of_tp}")


        try:
            current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_trading_pair3")
            print(current_price_of_trading_pair)
            advanced_atr = row_df.loc[
                row_index, "advanced_atr"]
            max_allowed_atr_number_away_from_level=4
            max_allowed_distance_between_level_and_current_price=advanced_atr*max_allowed_atr_number_away_from_level
            if "ath" in row_df.columns:
                ath = row_df.loc[
                    row_index, "ath"]
                ath=float(ath)
                print("ath=")
                print(ath)
                print("type(ath)=")
                print(type(ath))
                if ath>0:
                    distance_between_current_price_and_level=abs(current_price_of_trading_pair-ath)
                    distance_between_current_price_and_level_in_atr=distance_between_current_price_and_level/advanced_atr
                    if distance_between_current_price_and_level>max_allowed_distance_between_level_and_current_price:
                        print(f"i_will_cancel_order for {trading_pair} on {exchange_id} because"
                              f" distance_between_current_price_and_level_in_atr={distance_between_current_price_and_level_in_atr}")
                        # exchange_object_where_api_is_required.cancel_order(order_id,
                        #                                                    trading_pair, params=params)
            if "atl" in row_df.columns:
                atl = row_df.loc[
                    row_index, "atl"]
                atl=float(atl)
                print("atl=")
                print(atl)
                print("type(atl)=")
                print(type(atl))
                if atl>0:
                    distance_between_current_price_and_level=abs(atl-current_price_of_trading_pair)
                    distance_between_current_price_and_level_in_atr=distance_between_current_price_and_level/advanced_atr
                    if distance_between_current_price_and_level>max_allowed_distance_between_level_and_current_price:
                        print(f"i_will_cancel_order for {trading_pair} on {exchange_id} because"
                              f" distance_between_current_price_and_level_in_atr={distance_between_current_price_and_level_in_atr}")
                        # exchange_object_where_api_is_required.cancel_order(order_id,
                        #
        except:
            traceback.print_exc()



        if limit_buy_order_status_on_spot == "closed" or\
                limit_buy_order_status_on_spot == "closed".upper() or\
                limit_buy_order_status_on_spot == "FILLED":

            # amount of tp sometimes is not equal to order amount
            spot_balance = exchange_object_where_api_is_required.fetch_balance()
            amount_of_tp = get_amount_of_free_base_currency_i_own(spot_balance, trading_pair.split("/")[0])
            print("amount_of_tp_from_spot_balance")
            print(amount_of_tp)
            amount_of_sl=amount_of_tp


            limit_sell_order_tp_order_id = np.nan
            if trade_status != "limit_buy_order_is_filled_and_limit_tp_is_placed" and trade_status!="limit_take_profit_has_been_filled"\
                    and trade_status!="market_stop_loss_is_placed" and trade_status!="market_stop_loss_is_filled":
                print("trade_status12345")
                print(trade_status)
                if trade_status != "neither_sl_nor_tp_has_been_reached":
                    print("\n" + "i will try to place limit_sell_order_tp right now")
                    print("\n" + "type_of_tp=" + f"{type_of_tp}")
                    #place take profit right away as soon as limit order has been fulfilled
                    # limit_sell_order_tp_order_id=""
                    if type_of_tp == "limit":
                        print("\n" + "i will try to place limit_sell_order_tp right now. I am inside type_of_tp == limit")
                        print("\n" + f"amount_of_tp={amount_of_tp}")


                        limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                            trading_pair, amount_of_tp, price_of_tp, params=params)
                        print("\n"+"limit_sell_order_tp has been placed")

                        #######################
                        #######################
                        #######################
                        limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                        print("limit_sell_order_tp12345")
                        print(limit_sell_order_tp)
                        if pd.isna(limit_sell_order_tp):
                            limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                            print("limit_sell_order_tp_order_id123")
                            print(limit_sell_order_tp_order_id)
                        else:
                            limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                            print("limit_sell_order_tp_order_id1234")
                            print(limit_sell_order_tp_order_id)

                        column_name = "trade_status"
                        cell_value = "limit_buy_order_is_filled_and_limit_tp_is_placed"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                      cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "limit_buy_order_is_filled_and_limit_tp_is_placed"

                        ##############################################################
                        ##############################################################
                        column_name = "tp_order_id"
                        cell_value = limit_sell_order_tp_order_id
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name,
                                                                                      cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        ####################################


            # keep looking at the price and wait till either sl or tp has been reached

            # while True:
            if trade_status== "market_take_profit_has_been_filled":
                return "market_take_profit_has_been_filled"
            if trade_status!= "limit_buy_order_is_filled_and_limit_tp_is_placed" \
                    and trade_status!= "limit_sell_order_is_filled_and_limit_tp_is_placed" \
                    and trade_status!="neither_sl_nor_tp_has_been_reached":
                return "limit_order_is_not_yet_filled"
            current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_trading_pair1")
            print(current_price_of_trading_pair)
            try:
                # keep looking if limit take profit has been filled
                spot_cross_or_isolated_margin = "spot"
                all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                             spot_cross_or_isolated_margin,
                                                                                             exchange_object_where_api_is_required)

                current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_trading_pair1")
                print(current_price_of_trading_pair)
                try:
                    if trade_status=='neither_sl_nor_tp_has_been_reached':
                        limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                        print("limit_sell_order_tp_order_id12345678")
                        print(limit_sell_order_tp_order_id)
                except:
                    traceback.print_exc()


                print("limit_sell_order_tp_order_id12")
                print(limit_sell_order_tp_order_id)

                limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                    all_orders_on_spot_account, limit_sell_order_tp_order_id)

                current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_trading_pair2")
                print(current_price_of_trading_pair)

                # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                if limit_sell_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                    print("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")
                    # stop looking at the price to place stop loss because take profit has been filled
                    # break
                    column_name = "trade_status"
                    cell_value = "limit_take_profit_has_been_filled"
                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                    df_with_bfr.at[row_index, column_name] = cell_value
                    trade_status = "limit_take_profit_has_been_filled"

                    return "limit_take_profit_has_been_filled"
                else:
                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print("current_price_of_trading_pair3")
                    print(current_price_of_trading_pair)
                    print("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                          f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_trading_pair4")
                print(current_price_of_trading_pair)
                print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                trade_status="neither_sl_nor_tp_has_been_reached"
                column_name = "trade_status"
                cell_value = trade_status
                update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                df_with_bfr.at[row_index, column_name] = cell_value

                # take profit has been reached
                if current_price_of_trading_pair >= price_of_tp:

                    if type_of_tp == "market":
                        market_sell_order_tp = ""
                        if exchange_id in ['binance', 'binanceus']:
                            market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_tp, params=params)
                            column_name = "trade_status"
                            cell_value = "market_take_profit_has_been_filled"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_take_profit_has_been_filled"
                            print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                            print("\n" + "market_sell_order_tp has been placed")
                            return "market_take_profit_has_been_filled"
                        if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                            prices = exchange_object_where_api_is_required.fetch_tickers()
                            bid = float(prices[trading_pair]['bid'])
                            amount = amount_of_tp
                            market_orders_are_allowed_on_exchange=\
                                check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,trading_pair,file)
                            market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                trading_pair, 'sell', amount,
                                price=bid)
                            column_name = "trade_status"
                            cell_value = "market_take_profit_has_been_filled"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_take_profit_has_been_filled"
                            print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                            print("\n" + "market_sell_order_tp has been placed")
                            return "market_take_profit_has_been_filled"
                        else:
                            market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_tp, params=params)
                            column_name = "trade_status"
                            cell_value = "market_take_profit_has_been_filled"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_take_profit_has_been_filled"
                            print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                            print("\n" + "market_sell_order_tp has been placed")
                            return "market_take_profit_has_been_filled"


                        # break
                    elif type_of_tp == "stop":
                        stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                            trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                        print("\n"+"stop_market_sell_order_tp has been placed")
                        column_name = "trade_status"
                        cell_value = "stop_market_take_profit_has_been_filled"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "stop_market_take_profit_has_been_filled"
                        return "stop_market_take_profit_has_been_filled"
                        # break
                    elif type_of_tp == "limit":
                        print("\n"+"price of limit tp has been reached")
                    else:
                        print("\n"+f"there is no order called {type_of_tp}")



                # stop loss has been reached
                if trade_status =="stop_market_take_profit_has_been_filled" \
                        and trade_status=="market_take_profit_has_been_filled" \
                        and trade_status=="limit_take_profit_has_been_filled":
                    return "tp_is_filled"
                elif current_price_of_trading_pair <= price_of_sl:
                    print("current_price_of_trading_pair <= price_of_sl")
                    if type_of_sl == "limit":

                        limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                            trading_pair, amount_of_sl, price_of_sl, params=params)

                        if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                               trading_pair, params=params)
                            print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled  with type_of_sl == limit")
                        print("\n"+"limit_sell_order_sl has been placed")
                        column_name = "trade_status"
                        cell_value = "limit_stop_loss_is_placed"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "limit_stop_loss_is_placed"
                        return "limit_stop_loss_is_placed"
                        # break
                    elif type_of_sl == "market":
                        print("\n" + "market_sell_order_sl is going to be placed")
                        if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                            print("limit_sell_order_tp_order_id_to_cancel")
                            print(limit_sell_order_tp_order_id)

                            limit_sell_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                               trading_pair, params=params)
                            print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled with type_of_sl == market")

                        market_sell_order_sl=""
                        if exchange_id in ['binance','binanceus'] :
                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_sl, params=params)
                            column_name = "trade_status"
                            cell_value = "market_stop_loss_is_placed"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_stop_loss_is_placed"
                            return "market_stop_loss_is_placed"
                        if exchange_id in ['mexc3','huobi','huobipro']:
                            print("\n" + "market_sell_order_sl is going to be placed1")
                            prices = exchange_object_where_api_is_required.fetch_tickers()
                            bid = float(prices[trading_pair]['bid'])
                            # amount = amount_of_tp
                            amount=amount_of_sl
                            print("\n" + "amount_of_sl (supposed to be in asset quantity= " + str(amount_of_sl))

                            # market_orders_are_allowed_on_exchange = \
                            #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                            #                                                                  trading_pair, file)
                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                trading_pair, 'sell', amount,
                                price=bid)
                            print("\n" + f"1market_sell_order_sl = {market_sell_order_sl}")
                            print("\n" + "1market_sell_order_sl has been placed")

                            # print("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                            # print("\n" + "market_sell_order_sl has been placed")

                            column_name = "trade_status"
                            cell_value = "market_stop_loss_is_placed"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_stop_loss_is_placed"
                            return "market_stop_loss_is_placed"

                        else:
                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_sl, params=params)
                            column_name = "trade_status"
                            cell_value = "market_stop_loss_is_placed"
                            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                            df_with_bfr.at[row_index, column_name] = cell_value
                            trade_status = "market_stop_loss_is_placed"
                            return "market_stop_loss_is_placed"



                        # break
                    elif type_of_sl == "stop":
                        if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                               trading_pair, params=params)
                            print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                        stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                            trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                        print("\n"+"stop_market_sell_order_sl has been placed")
                        column_name = "trade_status"
                        cell_value = "stop_market_stop_loss_is_placed"
                        update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                        df_with_bfr.at[row_index, column_name] = cell_value
                        trade_status = "stop_market_stop_loss_is_placed"
                        return "stop_market_stop_loss_is_placed"


                        # break
                    else:
                        print("\n"+f"there is no order called {type_of_sl}")

                # neither sl nor tp has been reached
                else:
                    # # time.sleep(1)
                    print("\n"+"neither sl nor tp has been reached")
                    column_name = "trade_status"
                    cell_value = "neither_sl_nor_tp_has_been_reached"
                    update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
                    df_with_bfr.at[row_index, column_name] = cell_value
                    trade_status = "neither_sl_nor_tp_has_been_reached"
                    return "neither_sl_nor_tp_has_been_reached"
                    # continue
            except ccxt.RequestTimeout:
                print("\n"+str(traceback.format_exc()))
                # continue

            # # stop waiting for the order to be filled because it has been already filled
            # break

        elif limit_buy_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(),
                                                           "cancelled".upper()]:
            print("\n"+
                f"{order_id} order has been {limit_buy_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
            column_name = "trade_status"
            cell_value = "limit_order_has_been_cancelled"
            update_one_cell_in_google_spreadsheet_column_name_is_argument(df_with_bfr, row_index, column_name, cell_value)
            df_with_bfr.at[row_index, column_name] = cell_value
            trade_status = "limit_order_has_been_cancelled"
            return "limit_order_has_been_cancelled"
            # break
        else:
            if counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file == 0 or \
                    counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file % 10 == 0:
                counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file=\
                    counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file+1
                # keep waiting for the order to fill
                string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW=\
                    "\n"+f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_spot}"
                print(string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW)
            # # time.sleep(1)
            # continue



    elif side_of_limit_order == "sell":
        print("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_spot = ""
        order_id = ""
        params={}
        min_quantity=None
        min_notional_value=None
        try:
            print("\n"+f"exchange_object_where_api_is_required = {exchange_object_where_api_is_required}")


            # exchange_object_where_api_is_required.load_markets()
            # __________________________________
            # ---------------------------------------------------------
            try:
                spot_balance = exchange_object_where_api_is_required.fetch_balance()
                print("\n" + "spot_balance")
                print("\n" + str(spot_balance))
                print("spot_balance")
                print(spot_balance)
            except:
                print(str(traceback.format_exc()))

            # Load the valid trading symbols
            try:
                exchange_object_where_api_is_required.load_markets()
            except ccxt.BadRequest:
                print(str(traceback.format_exc()))
            except Exception:
                print(str(traceback.format_exc()))

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            # # Get the minimum notional value for the symbol
            # min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            #
            # print("min_notional_value in USD")
            # print(min_notional_value)

            # Get the minimum notional value for the symbol

            # Get the minimum notional value for the symbol
            min_notional_value = None
            min_quantity = None
            try:
                # print("\n" + "symbol_details")
                # print("\n" + str(symbol_details))
                # print("\n" + "symbol_details['info']")
                # print("\n" + str(symbol_details['info']))
                if exchange_id == "lbank" or exchange_id == "lbank2":
                    min_quantity = symbol_details['limits']['amount']['min']
                    min_notional_value = min_quantity * float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))
                elif exchange_id == "binance":
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                elif exchange_id == "mexc3" or exchange_id == "mexc":
                    min_quantity = symbol_details['limits']['cost']['min']
                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                else:
                    print("\n" + "symbol_details")
                    print("\n" + str(symbol_details))
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
            except:
                print("\n" + str(traceback.format_exc()))

            # print(
            #     f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            # print(min_quantity)

            #
            # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
            # print("future_balance")
            # print(future_balance)

            # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
            #                                                                            limit=None, params={})
            # print("canceled_orders")
            # print(canceled_orders)

            # ------------------------closed orders

            # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
            # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

            # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("closed_orders_on_spot")
            # print(closed_orders_on_spot)

            # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
            # exchange_object_where_api_is_required.load_markets()

            # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("closed_orders_on_cross_margin_account")
            # print(closed_orders_on_cross_margin_account)

            # print("dir(exchange_object_where_api_is_required)")
            # print(dir(exchange_object_where_api_is_required))

            # Fetch closed orders from the margin account
            # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
            # closed_orders_on_spot = exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("closed_orders_on_spot")
            # print(closed_orders_on_spot)

            # sapi_get_margin_allorders works only for binance


            # print("dir(exchange_object_where_api_is_required)")
            # print(dir(exchange_object_where_api_is_required))

            # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("all_orders_on_cross_margin_account")
            # pprint.pprint(all_orders_on_cross_margin_account)

            # --------------------------open_orders
            # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})

            # open_orders_on_spot_account = exchange_object_where_api_is_required.fetch_open_orders(
            #     symbol=trading_pair, since=None, limit=None, params={})
            # print("open_orders_on_spot_account")
            # pprint.pprint(open_orders_on_spot_account)

            # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })

            # print("trading_pair")
            # print(trading_pair)
            # print("open_orders")
            # print(open_orders_on_cross_margin_account)
            # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
            # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("Orders")
            # print(Orders)

            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                print("\n"+str(traceback.format_exc()))
                raise SystemExit

            print("\n"+f"placed sell limit order on {exchange_id}")
            print("\n"+"limit_sell_order")
            print("\n"+str(limit_sell_order))

            order_id=get_order_id(limit_sell_order)
            print("\n"+"order_id5")
            print(str(order_id))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)

            try:
                if "not in orders" in limit_sell_order_status_on_spot:

                    limit_sell_order_status_on_spot = exchange_object_where_api_is_required.fetch_order_status(symbol=trading_pair,
                                                                                                    id=order_id,
                                                                                                    params={})
            except:
                traceback.print_exc()

            print("\n"+"limit_sell_order_status_on_spot1")
            print("\n"+str(limit_sell_order_status_on_spot))
            print("\n"+"limit_sell_order['status']")
            print(str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit


        except:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin="spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)

            print("\n"+"limit_sell_order_status_on_spot2")
            print("\n"+str(limit_sell_order_status_on_spot))

            try:
                if "not in orders" in limit_sell_order_status_on_spot:

                    limit_sell_order_status_on_spot = exchange_object_where_api_is_required.fetch_order_status(symbol=trading_pair,
                                                                                                    id=order_id,
                                                                                                    params={})
            except:
                traceback.print_exc()



            if limit_sell_order_status_on_spot == "closed" or\
                    limit_sell_order_status_on_spot == "closed".upper() or\
                    limit_sell_order_status_on_spot == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id=""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id=get_order_id(limit_buy_order_tp)

                    try:
                        limit_buy_order_tp_order_id = df_with_bfr.loc[row_index, "tp_order_id"]
                        print("limit_buy_order_tp_order_id")
                        print(limit_buy_order_tp_order_id)
                    except:
                        traceback.print_exc()

                # keep looking at the price and wait till either sl or tp has been reached. At the same time look for tp to get filled
                while True:

                    try:
                        #keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "spot"
                        all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            #stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:


                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro','mexc']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,trading_pair,params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_buy_order_sl has been placed")

                                break
                            elif type_of_sl == "market":
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                market_buy_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro','mexc']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_sl
                                    print("\n" + "amount (quantity)")
                                    print("\n" + str(amount))

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                print("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                print("\n" + "market_buy_order_sl has been placed")
                                print("\n" + "-----------------------------------------")
                                break
                            elif type_of_sl == "stop":
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_buy_order_sl has been placed")
                                print("\n" + "-----------------------------------------")
                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_spot}")
                # time.sleep(1)
                continue


    else:
        print("\n"+f"unknown {side_of_limit_order} value")
def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_cross_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {file.name} at {datetime.datetime.now()}\n")
    try:
        print(str(exchange_id))
        print("\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        print(str(traceback.format_exc()))
    print("\n")
    print(str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    print("\n")
    # print(side_of_limit_order)

    if side_of_limit_order == "buy":
        print(f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_cross_margin = ""
        order_id = ""

        # we want to place a buy order with cross margin
        params = {'type': 'margin',
                  'isCross': True  # Set the margin type to cross
                  }

        limit_buy_order = None
        order_id = ""

        # ---------------------------------------------------------
        cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            print(
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            print(min_quantity)
        except:
            print(str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isICross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)

        # ---------------------------------------------------------
        try:
            try:
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
            except ccxt.InsufficientFunds:
                print(str(traceback.format_exc()))
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            print(f"placed buy limit order on {exchange_id}")
            print("limit_buy_order2")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id4")
            print(order_id)

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("limit_buy_order_status_on_cross_margin1")
            print(limit_buy_order_status_on_cross_margin)
            # print("limit_buy_order['status']")
            # print(limit_buy_order['status'])

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("Invalid order: Filter failure: NOTIONAL")
                print(
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            print(str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
            # print("all_orders_on_cross_margin_account1")
            # pprint.pprint(all_orders_on_cross_margin_account)

            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("limit_buy_order_status_on_cross_margin")
            print(limit_buy_order_status_on_cross_margin)
            if limit_buy_order_status_on_cross_margin == "closed" or\
                    limit_buy_order_status_on_cross_margin == "closed".upper() or\
                    limit_buy_order_status_on_cross_margin == "FILLED":

                # place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)


                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print(f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print(f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print(f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print(f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                        # take profit has been reached
                        if current_price_of_trading_pair >= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_sell_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_sell_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                print("market_sell_order_tp has been placed")


                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                print("stop_market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "limit":
                                print("price of limit tp has been reached")
                            else:
                                print(f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":
                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("limit_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "market":
                                market_sell_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_sl

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                print("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                print("\n" + "market_sell_order_sl has been placed")

                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "stop":
                                stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print(str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                print(
                    f"{order_id} order has been {limit_buy_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print(
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_cross_margin}")
                # time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        print(f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_cross_margin = ""
        order_id = ""
        params = {'type': 'margin',
                  'isCross': True  # Set the margin type to cross
                  }
        min_quantity = None
        min_notional_value=None
        try:
            print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


            # exchange_object_where_api_is_required.load_markets()
            # __________________________________
            # # show balance on spot
            # print("exchange_object_where_api_is_required.fetch_balance()")
            # print(exchange_object_where_api_is_required.fetch_balance())

            # show balance on cross margin
            cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
            # print("cross_margin_balance")
            # print(cross_margin_balance)

            # # show balance on isolated margin
            # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
            # print("isolated_margin_balance")
            # print(isolated_margin_balance)
            # # __________________________

            # Load the valid trading symbols
            try:
                exchange_object_where_api_is_required.load_markets()
            except ccxt.BadRequest:
                print(str(traceback.format_exc()))
            except Exception:
                print(str(traceback.format_exc()))

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]
            try:
                if exchange_id == "lbank" or exchange_id == "lbank2":
                    min_quantity = symbol_details['limits']['amount']['min']
                    min_notional_value = min_quantity * float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))
                elif exchange_id == "binance":
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                elif exchange_id == "mexc3" or exchange_id == "mexc":
                    min_notional_value = symbol_details['limits']['cost']['min']
                    min_quantity = min_notional_value / float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                elif exchange_id == "okex" or exchange_id == "okex5":
                    min_notional_value = symbol_details['limits']['cost']['min']
                    if not pd.isna(min_notional_value):
                        min_quantity_calculated_from_min_notional_value = min_notional_value / float(
                            price_of_limit_order)
                        print("\n" +
                                   f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                        print("\n" + str(min_quantity_calculated_from_min_notional_value))

                    min_quantity = symbol_details['limits']['amount']['min']
                    min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                    print("\n" +
                               f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_notional_value_in_usd))

                else:
                    print("\n" + "symbol_details")
                    print("\n" + str(symbol_details))
                    min_notional_value = symbol_details['limits']['cost']['min']
                    print("\n" + "min_notional_value in USD")
                    print("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    print("\n" +
                               f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity))
                    min_quantity_raw = symbol_details['limits']['amount']['min']
                    print("\n" +
                               f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_raw))
                    min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(
                        price_of_limit_order)
                    print("\n" +
                               f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
            except:
                print(str(traceback.format_exc()))

            #
            # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
            # print("future_balance")
            # print(future_balance)

            # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
            #                                                                            limit=None, params={})
            # print("canceled_orders")
            # print(canceled_orders)

            # ------------------------closed orders

            # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
            # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

            # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("closed_orders_on_spot")
            # print(closed_orders_on_spot)

            # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
            # exchange_object_where_api_is_required.load_markets()

            # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("closed_orders_on_cross_margin_account")
            # print(closed_orders_on_cross_margin_account)

            # print("dir(exchange_object_where_api_is_required)")
            # print(dir(exchange_object_where_api_is_required))

            # Fetch closed orders from the margin account
            # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
            # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
            #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #      'isCross': 'TRUE'})
            # print("closed_orders_on_cross")
            # pprint.pprint(closed_orders)

            # # sapi_get_margin_allorders works only for binance
            # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE'})
            # print("all_orders_on_cross_margin_account")
            # pprint.pprint(all_orders_on_cross_margin_account)

            # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("all_orders_on_cross_margin_account")
            # pprint.pprint(all_orders_on_cross_margin_account)

            # --------------------------open_orders
            # # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
            # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })

            # print("open_orders_on_cross_margin_account")
            # pprint.pprint(open_orders_on_cross_margin_account)

            # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })

            # print("trading_pair")
            # print(trading_pair)
            # print("open_orders")
            # print(open_orders_on_cross_margin_account)
            # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
            # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("Orders")
            # print(Orders)

            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                print(str(traceback.format_exc()))
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            print(f"placed sell limit order on {exchange_id}")
            print("limit_sell_order")
            print(limit_sell_order)

            order_id = limit_sell_order['id']
            print("order_id4")
            print(order_id)

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("limit_sell_order_status_on_cross_margin1")
            print(limit_sell_order_status_on_cross_margin)
            print("limit_sell_order['status']")
            print(limit_sell_order['status'])

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("Invalid order: Filter failure: NOTIONAL")
                print(
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit


        except:
            print(str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_cross_margin_account1")
            # pprint.pprint(all_orders_on_cross_margin_account)

            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)

            print("limit_sell_order_status_on_cross_margin3")
            print(limit_sell_order_status_on_cross_margin)

            if limit_sell_order_status_on_cross_margin == "closed" or\
                    limit_sell_order_status_on_cross_margin == "closed".upper() or\
                    limit_sell_order_status_on_cross_margin == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print(f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print(f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print(f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_buy_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("stop_market_buy_order_tp has been placed")
                                break
                            else:
                                print(f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "market":
                                market_buy_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_sl
                                    print("\n" + "amount (quantity)")
                                    print("\n" + str(amount))

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                print("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                print("\n" + "market_buy_order_sl has been placed")
                                print("market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_buy_order_sl has been placed")

                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print(str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print(
                    f"{order_id} order has been {limit_sell_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print(
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_cross_margin}")
                # time.sleep(1)
                continue


    else:
        print(f"unknown {side_of_limit_order} value")

def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required=None
    all_orders_on_isolated_margin_account=""
    order_id=""

    #uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {file.name} at {datetime.datetime.now()}\n")
    try:
        print(str(exchange_id))
        print("\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        print(str(traceback.format_exc()))
    print("\n")
    print(str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    print("\n")
    # print(side_of_limit_order)

    if side_of_limit_order=="buy":
        print(f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_isolated_margin = ""
        order_id = ""

        # we want to place a buy order with isolated margin
        params = {'type': 'margin',
                  'isIsolated': True  # Set the margin type to isolated
                  }


        limit_buy_order=None
        order_id=""

        #---------------------------------------------------------
        cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # show balance on isolated margin
        isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        print("isolated_margin_balance")
        print(isolated_margin_balance)
        # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value=None
        try:
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(
                        price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(
                    price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
        except:
            print(str(traceback.format_exc()))



        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
                                                                                   limit=None, params={})
        print("canceled_orders")
        print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isIsolated': 'TRUE'})
        # print("closed_orders_on_isolated")
        # pprint.pprint(closed_orders)

        # sapi_get_margin_allorders works only for binance
        all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
            'symbol': remove_slash_from_trading_pair_name(trading_pair),
            'isIsolated': 'TRUE'})
        print("all_orders_on_isolated_margin_account")
        pprint.pprint(all_orders_on_isolated_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        open_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
            'symbol': remove_slash_from_trading_pair_name(trading_pair),
            'isIsolated': 'TRUE',
        })

        print("open_orders_on_isolated_margin_account")
        pprint.pprint(open_orders_on_isolated_margin_account)


        #---------------------------------------------------------
        try:
            try:
                limit_buy_order=exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                             amount_of_asset_for_entry,
                                                                                             price_of_limit_order,
                                                                                             params=params)
            except ccxt.InsufficientFunds:
                print(str(traceback.format_exc()))
                raise SystemExit

            print(f"placed buy limit order on {exchange_id}")
            print("limit_buy_order3")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id4")
            print(order_id)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("limit_buy_order_status_on_isolated_margin1")
            print(limit_buy_order_status_on_isolated_margin)
            # print("limit_buy_order['status']")
            # print(limit_buy_order['status'])

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("Invalid order: Filter failure: NOTIONAL")
                print(f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                      f"or {amount_of_asset_for_entry*get_price(exchange_object_without_api,trading_pair)} "
                      f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            print(str(traceback.format_exc()))



        #wait till order is filled (that is closed)
        while True:
            print("waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE'})
            print("all_orders_on_isolated_margin_account1")
            pprint.pprint(all_orders_on_isolated_margin_account)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("limit_buy_order_status_on_isolated_margin")
            print(limit_buy_order_status_on_isolated_margin)
            if limit_buy_order_status_on_isolated_margin=="closed" or limit_buy_order_status_on_isolated_margin == "closed".upper() or limit_buy_order_status_on_isolated_margin == "FILLED":
                #keep looking at the price and wait till either sl or tp has been reached
                while True:
                    try:
                        current_price_of_trading_pair=get_price(exchange_object_without_api,trading_pair)
                        print(f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print(f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                        #take profit has been reached
                        if current_price_of_trading_pair>=price_of_tp:
                            if type_of_tp=="limit":
                                limit_sell_order_tp=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_tp,price_of_tp, params=params)
                                print("limit_buy_order_tp has been placed")
                                break
                            elif type_of_tp=="market":
                                market_sell_order_tp=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_tp, params=params)
                                print("market_buy_order_tp has been placed")
                                break
                            elif type_of_tp=="stop":
                                stop_market_sell_order_tp=exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair,"sell",amount_of_tp,price_of_tp, params=params)
                                print("stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                print("price of limit tp has been reached")
                            else:
                                print(f"there is no order called {type_of_tp}")

                        #stop loss has been reached
                        elif current_price_of_trading_pair<=price_of_sl:
                            if type_of_sl=="limit":
                                limit_sell_order_sl=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_sl,price_of_sl, params=params)
                                print("limit_sell_order_sl has been placed")
                                break
                            elif type_of_sl=="market":
                                market_sell_order_sl=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_sl, params=params)
                                print("market_sell_order_sl has been placed")

                                break
                            elif type_of_sl=="stop":
                                stop_market_order_sl=exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_sell_order_sl has been placed")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        #neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print(str(traceback.format_exc()))
                        continue

                #stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_isolated_margin in ["canceled","cancelled","canceled".upper(),"cancelled".upper()]:
                print(f"{order_id} order has been {limit_buy_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                #keep waiting for the order to fill
                print(f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_isolated_margin}")
                # time.sleep(1)
                continue



    elif side_of_limit_order=="sell":
        print(f"placing sell limit order on {exchange_id}")
        limit_sell_order=None
        limit_sell_order_status_on_isolated_margin=""
        order_id=""
        params = {'type': 'margin',
                  'isIsolated': True  # Set the margin type to isolated
                  }
        min_notional_value=None
        try:
            print("exchange_object_where_api_is_required=",exchange_object_where_api_is_required)


            # exchange_object_where_api_is_required.load_markets()
#__________________________________
            # # show balance on spot
            # print("exchange_object_where_api_is_required.fetch_balance()")
            # print(exchange_object_where_api_is_required.fetch_balance())

            # show balance on cross margin
            cross_margin_balance=exchange_object_where_api_is_required.fetch_balance({'type':'margin'})
            # print("cross_margin_balance")
            # print(cross_margin_balance)

            # show balance on isolated margin
            isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
            print("isolated_margin_balance")
            print(isolated_margin_balance)
#__________________________

            # Load the valid trading symbols
            try:
                exchange_object_where_api_is_required.load_markets()
            except ccxt.BadRequest:
                print(str(traceback.format_exc()))
            except Exception:
                print(str(traceback.format_exc()))

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            # Get the minimum notional value for the symbol
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']

            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            print(f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            print(min_quantity)

            #
            # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
            # print("future_balance")
            # print(future_balance)

            canceled_orders=exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None, limit=None, params={})
            print("canceled_orders")
            print(canceled_orders)



            #------------------------closed orders

            # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
            # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})


            # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("closed_orders_on_spot")
            # print(closed_orders_on_spot)


            # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
            # exchange_object_where_api_is_required.load_markets()

            # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("closed_orders_on_cross_margin_account")
            # print(closed_orders_on_cross_margin_account)

            # print("dir(exchange_object_where_api_is_required)")
            # print(dir(exchange_object_where_api_is_required))

            # Fetch closed orders from the margin account
            #somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
            closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders({'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE'})
            print("closed_orders_on_isolated")
            pprint.pprint(closed_orders)

            # sapi_get_margin_allorders works only for binance
            all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE'})
            print("all_orders_on_isolated_margin_account")
            pprint.pprint(all_orders_on_isolated_margin_account)

            # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })
            # print("all_orders_on_cross_margin_account")
            # pprint.pprint(all_orders_on_cross_margin_account)



            #--------------------------open_orders
            # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
            open_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE',
            })

            print("open_orders_on_isolated_margin_account")
            pprint.pprint(open_orders_on_isolated_margin_account)

            # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
            #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
            #     'isCross': 'TRUE',
            # })


            # print("trading_pair")
            # print(trading_pair)
            # print("open_orders")
            # print(open_orders_on_cross_margin_account)
            # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
            # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
            # print("Orders")
            # print(Orders)

            try:
                limit_sell_order=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,params=params)
            except ccxt.InsufficientFunds:
                print(str(traceback.format_exc()))
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            print(f"placed sell limit order on {exchange_id}")
            print("limit_sell_order")
            print(limit_sell_order)

            order_id=limit_sell_order['id']
            print("order_id4")
            print(order_id)

            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("limit_sell_order_status_on_isolated_margin1")
            print(limit_sell_order_status_on_isolated_margin)
            print("limit_sell_order['status']")
            print(limit_sell_order['status'])

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("Invalid order: Filter failure: NOTIONAL")
                print(f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                      f"or {amount_of_asset_for_entry*get_price(exchange_object_without_api,trading_pair)} "
                      f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit


        except:
            print(str(traceback.format_exc()))
            raise SystemExit


        # wait till order is filled (that is closed)
        while True:
            print("waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            all_orders_on_isolated_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
                'symbol': remove_slash_from_trading_pair_name(trading_pair),
                'isIsolated': 'TRUE'})
            print("all_orders_on_isolated_margin_account1")
            pprint.pprint(all_orders_on_isolated_margin_account)

            limit_sell_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,all_orders_on_isolated_margin_account, order_id)




            print("limit_sell_order_status2")
            print(limit_sell_order_status)

            if limit_sell_order_status == "closed" or limit_sell_order_status == "closed".upper() or limit_sell_order_status == "FILLED":
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print(f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print(f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            if type_of_tp == "limit":
                                limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_tp, price_of_tp, params=params)
                                print("limit_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                print("price of limit tp has been reached")
                            else:
                                print(f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("limit_buy_order_sl has been placed")
                                break
                            elif type_of_sl == "market":
                                market_buy_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_sl
                                    print("\n" + "amount (quantity)")
                                    print("\n" + str(amount))

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                print("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                print("\n" + "market_buy_order_sl has been placed")
                                print("market_buy_order_sl has been placed")
                                print("\n" + "-----------------------------------------")
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_buy_order_sl has been placed")
                                print("\n" + "-----------------------------------------")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print(str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status in ["canceled","cancelled","canceled".upper(),"cancelled".upper()]:
                print(f"{order_id} order has been {limit_sell_order_status} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print(f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status}")
                # time.sleep(1)
                continue


    else:
        print(f"unknown {side_of_limit_order} value")


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(df_with_bfr,row_df, row_index,file, exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry_in_quote_currency,side_of_limit_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_cross_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print("\n"+f"12began writing to {file.name} at {datetime.datetime.now()}\n")
    try:
        print("\n"+str(exchange_id))
        print("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        print("\n"+str(traceback.format_exc()))
    print("\n"+"\n")
    print("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    print("\n"+"\n")
    # print(side_of_limit_order)
    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)
    amount_of_tp = amount_of_asset_for_entry
    amount_of_sl = amount_of_asset_for_entry

    trade_status = row_df.loc[row_index, "trade_status"]

    if side_of_limit_order == "buy":
        print("\n"+f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_cross_margin = ""
        order_id = ""

        # we want to place a buy order with Cross margin
        params = {'type': 'margin',
                  'isIsolated': False  # Set the margin type to Cross
                  }

        limit_buy_order = None
        order_id = ""

        # ---------------------------------------------------------
        # cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # # show balance on cross margin
        # cross_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_cross_account()  # not uniform, see dir(exchange)
        # print("cross_margin_balance")
        # print(cross_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))

        except:
            print("\n"+str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isICross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)
        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))
        # # Use describe() to get the method details
        # method_details = exchange_object_where_api_is_required.describe()
        # print(method_details)

        # print(dir(exchange_object_where_api_is_required))
        margin_mode="cross"

        # sys.exit(1)

        # we need current timestamp to get borrow interest since that timestamp to add this interest to the repay ammount
        # current_timestamp_in_milliseconds = get_current_timestamp_in_seconds()

        # ---------------------------------------------------------
        try:

            #borrow margin before creating an order. Borrow exactly how much your position is
            margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(file, trading_pair,
                                                               exchange_object_without_api,
                                                               amount_of_asset_for_entry,
                                                               exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_quote_currency_is_borrowed")
            print("\n"+str(margin_loan_when_quote_currency_is_borrowed))

            # if borrowed_margin_loan['info']['code'] == 200:
            #     print("borrowed_margin_loan['info']['code'] == 200")
            #     print(borrowed_margin_loan['info']['code'] == 200)


            try:
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
                print("\n"+"created_limit_buy_order")
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                print("\n"+str(traceback.format_exc()))
                raise SystemExit
            print("\n"+f"placed buy limit order on {exchange_id}")
            print("\n"+"limit_buy_order4")
            print("\n"+str(limit_buy_order))

            order_id = limit_buy_order['id']
            print("\n"+"order_id4")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("\n"+"limit_buy_order_status_on_cross_margin1")
            print("\n"+str(limit_buy_order_status_on_cross_margin))
            # print("\n"+"limit_buy_order['status']")
            # print("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
            # print("all_orders_on_cross_margin_account1")
            # pprint.pprint(all_orders_on_cross_margin_account)

            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("\n"+"limit_buy_order_status_on_cross_margin")
            print("\n"+str(limit_buy_order_status_on_cross_margin))
            if limit_buy_order_status_on_cross_margin == "closed" or\
                    limit_buy_order_status_on_cross_margin == "closed".upper() or\
                    limit_buy_order_status_on_cross_margin == "FILLED":

                # place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)




                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                            repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)

                            # if repaid_margin_loan['info']['code'] == 200:
                            #     print("repaid_margin_loan['info']['code'] == 200")
                            #     print(repaid_margin_loan['info']['code'] == 200)


                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                        # take profit has been reached
                        if current_price_of_trading_pair >= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_sell_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_sell_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":
                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_sell_order_sl has been placed")

                                # cancel tp because sl has been hit

                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                break
                            elif type_of_sl == "market":
                                try:
                                    # market_sell_order_sl=\
                                        # exchange_object_where_api_is_required.sapiPostMarginOrder(remove_slash_from_trading_pair_name(trading_pair),
                                        #                                                           side = "sell",
                                        #                                                           type ="market",
                                        #                                                           quantity = amount_of_sl, isCross= True)
                                    # exchange_object_where_api_is_required.sapiPostMarginOrder({"symbol":remove_slash_from_trading_pair_name(trading_pair),"side":'sell',"type":'market',"quantity":amount_of_sl, "isIsolted":True})
                                    # print("1amount_of_sl")
                                    # print(amount_of_sl)
                                    # print("1params")
                                    # print(params)

                                    # we need to cancel tp first otherwise we will have insufficient funds to sell with sl.
                                    # borrowed amount already locked in tp order
                                    if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                        exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    market_sell_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        bid = float(prices[trading_pair]['bid'])
                                        amount = amount_of_sl

                                        market_orders_are_allowed_on_exchange = \
                                            check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                                                                                         trading_pair,
                                                                                                         file)
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'sell', amount,
                                            price=bid)
                                    else:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    print("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                    print("\n" + "market_sell_order_sl has been placed")

                                    # market_sell_order_sl=\
                                    #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                    # print("\n"+"market_sell_order_sl has been placed")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    print("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    print("\n"+str(traceback.format_exc()))

                                # # cancel tp because sl has been hit
                                # if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                #     print("4limit_sell_order_tp_order_status")
                                #     print(limit_sell_order_tp_order_status)
                                #     print("limit_sell_order_tp_order_id")
                                #     print(limit_sell_order_tp_order_id)
                                #     exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                #                                                        trading_pair, params=params)
                                #     print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                #
                                #     # repay margin loan when stop loss is achieved
                                #     repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                #                                           exchange_object_without_api,
                                #                                                       amount_of_asset_for_entry,
                                #                                                       exchange_object_where_api_is_required,
                                #                                                       params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                break
                            elif type_of_sl == "stop":
                                stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_sell_order_sl has been placed")

                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)

                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {limit_buy_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")

                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                # if repaid_margin_loan['info']['code'] == 200:
                #     print("repaid_margin_loan['info']['code'] == 200")
                #     print(repaid_margin_loan['info']['code'] == 200)


                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_cross_margin}")
                # time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        print("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_cross_margin = ""
        order_id = ""
        params = {'type': 'margin',
                  'isIsolated': False  # Set the margin type to cross
                  }
        min_quantity = None
        min_notional_value=None
        # Get the symbol details


        print("\n"+f"exchange_object_where_api_is_required={exchange_object_where_api_is_required}")


        # exchange_object_where_api_is_required.load_markets()
        # __________________________________
        # # show balance on spot
        # print("exchange_object_where_api_is_required.fetch_balance()")
        # print(exchange_object_where_api_is_required.fetch_balance())

        # show balance on cross margin
        # cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # # show balance on cross margin
        # cross_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_cross_account()  # not uniform, see dir(exchange)
        # print("cross_margin_balance")
        # print(cross_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        try:
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))

        except:
            print("\n" + str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)

        # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("trading_pair")
        # print(trading_pair)
        # print("open_orders")
        # print(open_orders_on_cross_margin_account)
        # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
        # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("Orders")
        # print(Orders)
        margin_mode = "cross"
        try:
            # borrow margin before creating an order. Borrow exactly how much your position is
            margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(file,
                trading_pair,
                exchange_object_without_api,
                amount_of_asset_for_entry,
                exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_base_currency_is_borrowed")
            print("\n"+str(margin_loan_when_base_currency_is_borrowed))


            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit

            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                print("\n"+str(traceback.format_exc()))
                raise SystemExit
            print("\n"+f"placed sell limit order on {exchange_id}")
            print("\n"+"limit_sell_order")
            print("\n"+str(limit_sell_order))

            order_id = limit_sell_order['id']
            print("\n"+"order_id5")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("\n"+"limit_sell_order_status_on_cross_margin1")
            print("\n"+limit_sell_order_status_on_cross_margin)
            print("\n"+"limit_sell_order['status']")
            print("\n"+str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit


        except Exception:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_cross_margin_account1")
            # pprint.pprint(all_orders_on_cross_margin_account)

            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)

            print("\n"+"limit_sell_order_status_on_cross_margin3")
            print("\n"+str(limit_sell_order_status_on_cross_margin))

            if limit_sell_order_status_on_cross_margin == "closed" or\
                    limit_sell_order_status_on_cross_margin == "closed".upper() or limit_sell_order_status_on_cross_margin == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_cross_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_buy_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)
                                break
                            elif type_of_sl == "market":
                                try:
                                    if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                        exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    market_buy_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        ask = float(prices[trading_pair]['ask'])
                                        amount = amount_of_sl
                                        print("\n" + "amount (quantity)")
                                        print("\n" + str(amount))

                                        market_orders_are_allowed_on_exchange = \
                                            check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                                                                                         trading_pair,
                                                                                                         file)
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'buy', amount,
                                            price=ask)
                                    else:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    print("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                    print("\n" + "market_buy_order_sl has been placed")
                                    print("\n" + "-----------------------------------------")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    print("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    print("\n"+str(traceback.format_exc()))
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_buy_order_sl has been placed")
                                print("\n"+"-----------------------------------------")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_cross_margin}")
                # time.sleep(1)
                continue


    else:
        print("\n"+f"unknown {side_of_limit_order} value")



def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(df_with_bfr,row_df, row_index,file, exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry_in_quote_currency,side_of_limit_order):



    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1.txt"


    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_isolated_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print("\n"+f"12began writing to {file.name} at {datetime.datetime.now()}\n")
    try:
        print("\n"+str(exchange_id))
        print("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        print("\n"+str(traceback.format_exc()))
    print("\n"+"\n")
    print("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    print("\n"+"\n")
    # print(side_of_limit_order)

    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)
    amount_of_tp = amount_of_asset_for_entry
    amount_of_sl = amount_of_asset_for_entry


    trade_status = row_df.loc[row_index, "trade_status"]
    if side_of_limit_order == "buy":
        print("\n"+f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_isolated_margin = ""
        order_id = ""

        # we want to place a buy order with isolated margin
        params = {'type': 'margin',
                  'isIsolated': True  # Set the margin type to isolated
                  }

        limit_buy_order = None
        order_id = ""

        # ---------------------------------------------------------
        isolated_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))

        except:
            print("\n" + str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isICross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)
        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))
        # # Use describe() to get the method details
        # method_details = exchange_object_where_api_is_required.describe()
        # print(method_details)

        # print(dir(exchange_object_where_api_is_required))
        margin_mode="isolated"

        # sys.exit(1)

        # we need current timestamp to get borrow interest since that timestamp to add this interest to the repay ammount
        # current_timestamp_in_milliseconds = get_current_timestamp_in_seconds()

        # ---------------------------------------------------------
        try:

            #borrow margin before creating an order. Borrow exactly how much your position is
            margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(file, trading_pair,
                                                               exchange_object_without_api,
                                                               amount_of_asset_for_entry,
                                                               exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_quote_currency_is_borrowed")
            print("\n"+str(margin_loan_when_quote_currency_is_borrowed))

            # if borrowed_margin_loan['info']['code'] == 200:
            #     print("borrowed_margin_loan['info']['code'] == 200")
            #     print(borrowed_margin_loan['info']['code'] == 200)


            try:
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
                print("\n"+"created_limit_buy_order")
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                print("\n"+str(traceback.format_exc()))
                raise SystemExit
            print("\n"+f"placed buy limit order on {exchange_id}")
            print("\n"+"limit_buy_order5")
            print("\n"+str(limit_buy_order))

            order_id = limit_buy_order['id']
            print("\n"+"order_id4")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("\n"+"limit_buy_order_status_on_isolated_margin1")
            print("\n"+str(limit_buy_order_status_on_isolated_margin))
            # print("\n"+"limit_buy_order['status']")
            # print("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
            # print("all_orders_on_isolated_margin_account1")
            # pprint.pprint(all_orders_on_isolated_margin_account)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("\n"+"limit_buy_order_status_on_isolated_margin")
            print("\n"+str(limit_buy_order_status_on_isolated_margin))
            if limit_buy_order_status_on_isolated_margin == "closed" or\
                    limit_buy_order_status_on_isolated_margin == "closed".upper() or\
                    limit_buy_order_status_on_isolated_margin == "FILLED":

                # place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)




                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "isolated"
                        all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_isolated_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                            repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)

                            # if repaid_margin_loan['info']['code'] == 200:
                            #     print("repaid_margin_loan['info']['code'] == 200")
                            #     print(repaid_margin_loan['info']['code'] == 200)


                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                        # take profit has been reached
                        if current_price_of_trading_pair >= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_sell_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_sell_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                print("\n" + "market_sell_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":
                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_sell_order_sl has been placed")

                                # cancel tp because sl has been hit

                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                break
                            elif type_of_sl == "market":
                                try:
                                    # market_sell_order_sl=\
                                        # exchange_object_where_api_is_required.sapiPostMarginOrder(remove_slash_from_trading_pair_name(trading_pair),
                                        #                                                           side = "sell",
                                        #                                                           type ="market",
                                        #                                                           quantity = amount_of_sl, isIsolated= True)
                                    # exchange_object_where_api_is_required.sapiPostMarginOrder({"symbol":remove_slash_from_trading_pair_name(trading_pair),"side":'sell',"type":'market',"quantity":amount_of_sl, "isIsolted":True})
                                    # print("1amount_of_sl")
                                    # print(amount_of_sl)
                                    # print("1params")
                                    # print(params)

                                    # we need to cancel tp first otherwise we will have insufficient funds to sell with sl.
                                    # borrowed amount already locked in tp order
                                    if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                        exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    market_sell_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        bid = float(prices[trading_pair]['bid'])
                                        amount = amount_of_sl

                                        market_orders_are_allowed_on_exchange = \
                                            check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                                                                                         trading_pair,
                                                                                                         file)
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'sell', amount,
                                            price=bid)
                                    else:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    print("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                    print("\n" + "market_sell_order_sl has been placed")

                                    # market_sell_order_sl=\
                                    #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)


                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    print("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    print("\n"+str(traceback.format_exc()))

                                # # cancel tp because sl has been hit
                                # if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                #     print("4limit_sell_order_tp_order_status")
                                #     print(limit_sell_order_tp_order_status)
                                #     print("limit_sell_order_tp_order_id")
                                #     print(limit_sell_order_tp_order_id)
                                #     exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                #                                                        trading_pair, params=params)
                                #     print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                #
                                #     # repay margin loan when stop loss is achieved
                                #     repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                #                                           exchange_object_without_api,
                                #                                                       amount_of_asset_for_entry,
                                #                                                       exchange_object_where_api_is_required,
                                #                                                       params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                break
                            elif type_of_sl == "stop":
                                stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_sell_order_sl has been placed")

                                if limit_sell_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)

                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {limit_buy_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")

                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                # if repaid_margin_loan['info']['code'] == 200:
                #     print("repaid_margin_loan['info']['code'] == 200")
                #     print(repaid_margin_loan['info']['code'] == 200)


                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_isolated_margin}")
                # time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        print("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_isolated_margin = ""
        order_id = ""
        params = {'type': 'margin',
                  'isIsolated': True  # Set the margin type to isolated
                  }
        min_quantity = None
        min_notional_value=None
        # Get the symbol details


        print("\n"+f"exchange_object_where_api_is_required={exchange_object_where_api_is_required}")


        # exchange_object_where_api_is_required.load_markets()
        # __________________________________
        # # show balance on spot
        # print("exchange_object_where_api_is_required.fetch_balance()")
        # print(exchange_object_where_api_is_required.fetch_balance())

        # show balance on cross margin
        # cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
        # print("cross_margin_balance")
        # print(cross_margin_balance)

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            print(str(traceback.format_exc()))
        except Exception:
            print(str(traceback.format_exc()))
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        try:
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value = symbol_details['limits']['cost']['min']
                min_quantity = min_notional_value / float(price_of_limit_order)
                print("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value = symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value = min_notional_value / float(price_of_limit_order)
                    print("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity = symbol_details['limits']['amount']['min']
                min_notional_value_in_usd = min_quantity * float(price_of_limit_order)
                print("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                print("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_in_usd))

            else:
                print("\n" + "symbol_details")
                print("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                print("\n" + "min_notional_value in USD")
                print("\n" + str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                print("\n" +
                           f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                print("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw = min_quantity_raw * float(price_of_limit_order)
                print("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print("\n" + str(min_notional_value_calculated_from_min_quantity_raw))

        except:
            print("\n" + str(traceback.format_exc()))

        #
        # future_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'future'})
        # print("future_balance")
        # print(future_balance)

        # canceled_orders = exchange_object_where_api_is_required.fetch_canceled_orders(symbol=trading_pair, since=None,
        #                                                                            limit=None, params={})
        # print("canceled_orders")
        # print(canceled_orders)

        # ------------------------closed orders

        # ClosedOrder=exchange_object_where_api_is_required.fetchClosedOrder(id, symbol=None, params={})
        # ClosedOrders=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})

        # closed_orders_on_spot=exchange_object_where_api_is_required.fetchClosedOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("closed_orders_on_spot")
        # print(closed_orders_on_spot)

        # OpenOrder=exchange_object_where_api_is_required.fetchOpenOrder(id, symbol=None, params={})
        # exchange_object_where_api_is_required.load_markets()

        # closed_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_closedorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("closed_orders_on_cross_margin_account")
        # print(closed_orders_on_cross_margin_account)

        # print("dir(exchange_object_where_api_is_required)")
        # print(dir(exchange_object_where_api_is_required))

        # Fetch closed orders from the margin account
        # somehow here symbol must be without slash so we use remove_slash_from_trading_pair_name()
        # closed_orders = exchange_object_where_api_is_required.sapi_get_margin_allorders(
        #     {'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #      'isCross': 'TRUE'})
        # print("closed_orders_on_cross")
        # pprint.pprint(closed_orders)

        # # sapi_get_margin_allorders works only for binance
        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE'})
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # all_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_allorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })
        # print("all_orders_on_cross_margin_account")
        # pprint.pprint(all_orders_on_cross_margin_account)

        # --------------------------open_orders
        # # open_orders_on_spot=exchange_object_where_api_is_required.fetch_open_orders(symbol=trading_pair, since=None, limit=None, params={})
        # open_orders_on_cross_margin_account = exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("open_orders_on_cross_margin_account")
        # pprint.pprint(open_orders_on_cross_margin_account)

        # open_orders_on_cross_margin_account=exchange_object_where_api_is_required.sapi_get_margin_openorders({
        #     'symbol': remove_slash_from_trading_pair_name(trading_pair),
        #     'isCross': 'TRUE',
        # })

        # print("trading_pair")
        # print(trading_pair)
        # print("open_orders")
        # print(open_orders_on_cross_margin_account)
        # Order=exchange_object_where_api_is_required.fetchOrder(id, symbol=None, params={})
        # Orders=exchange_object_where_api_is_required.fetchOrders(symbol=trading_pair, since=None, limit=None, params={})
        # print("Orders")
        # print(Orders)
        margin_mode = "isolated"
        try:
            # borrow margin before creating an order. Borrow exactly how much your position is
            margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(file,
                trading_pair,
                exchange_object_without_api,
                amount_of_asset_for_entry,
                exchange_object_where_api_is_required, params)
            print("\n"+"margin_loan_when_base_currency_is_borrowed")
            print("\n"+str(margin_loan_when_base_currency_is_borrowed))


            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                print("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                print("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit

            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("\n"+"Invalid order: Filter failure: NOTIONAL")
                    print("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    print("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                print("\n"+str(traceback.format_exc()))
                raise SystemExit
            print("\n"+f"placed sell limit order on {exchange_id}")
            print("\n"+"limit_sell_order")
            print("\n"+str(limit_sell_order))

            order_id = limit_sell_order['id']
            print("\n"+"order_id5")
            print("\n"+str(order_id))

            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("\n"+"limit_sell_order_status_on_isolated_margin1")
            print("\n"+str(limit_sell_order_status_on_isolated_margin))
            print("\n"+"limit_sell_order['status']")
            print("\n"+str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                print("\n"+"Invalid order: Filter failure: NOTIONAL")
                print("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                print("\n" + str(traceback.format_exc()))
                raise SystemExit


        except Exception:
            print("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("\n"+"waiting for the sell order to get filled")
            # print("order_id2")
            # print(order_id)
            #
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_isolated_margin_account1")
            # pprint.pprint(all_orders_on_isolated_margin_account)

            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)

            print("\n"+"limit_sell_order_status_on_isolated_margin3")
            print("\n"+str(limit_sell_order_status_on_isolated_margin))

            if limit_sell_order_status_on_isolated_margin == "closed" or\
                    limit_sell_order_status_on_isolated_margin == "closed".upper() or limit_sell_order_status_on_isolated_margin == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "isolated"
                        all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(trading_pair,exchange_object_where_api_is_required,
                            all_orders_on_isolated_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status in ["filled","FILLED", "closed", "CLOSED"]:
                            print("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            print("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        print("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        print("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            # if type_of_tp == "limit":
                            #     limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                            #         trading_pair, amount_of_tp, price_of_tp, params=params)
                            #     print("limit_buy_order_tp has been placed")
                            #     break
                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_tp

                                    # market_orders_are_allowed_on_exchange = \
                                    #     check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                    #                                                                  trading_pair, file)
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                print("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                print("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                print("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                print("\n"+"price of limit tp has been reached")
                            else:
                                print("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                print("\n"+"limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)
                                break
                            elif type_of_sl == "market":
                                try:
                                    if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                        exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    market_buy_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        ask = float(prices[trading_pair]['ask'])
                                        amount = amount_of_sl
                                        print("\n" + "amount (quantity)")
                                        print("\n" + str(amount))

                                        market_orders_are_allowed_on_exchange = \
                                            check_if_exchange_allows_market_orders_for_this_trading_pair(exchange_id,
                                                                                                         trading_pair,
                                                                                                         file)
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'buy', amount,
                                            price=ask)
                                    else:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    print("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                    print("\n" + "market_buy_order_sl has been placed")
                                    print("\n" + "-----------------------------------------")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    print("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    print("\n"+str(traceback.format_exc()))
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("\n"+"stop_market_buy_order_sl has been placed")
                                print("\n" + "-----------------------------------------")
                                if limit_buy_order_tp_order_status not in ["canceled","cancelled","CANCELLED","CANCELED"]:
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                print("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            # time.sleep(1)
                            print("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        print("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")
                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                break
            else:
                # keep waiting for the order to fill
                print("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_isolated_margin}")
                # time.sleep(1)
                continue


    else:
        print("\n"+f"unknown {side_of_limit_order} value")

def get_trade_status_from_df_given_row_index(row_index_to_be_found,df_with_bfr):
    trade_status=""
    for row_index, row in df_with_bfr.iterrows():

        if row_index==row_index_to_be_found:
            row_df=pd.DataFrame(row).T
            trade_status = row_df.loc[row_index, "trade_status"]
    return trade_status


def get_stop_market_or_limit_order_to_use_for_entry_from_df_given_row_index(row_index_to_be_found,df_with_bfr):
    stop_market_or_limit_order_to_use_for_entry=""
    for row_index, row in df_with_bfr.iterrows():

        if row_index==row_index_to_be_found:
            row_df=pd.DataFrame(row).T
            stop_market_or_limit_order_to_use_for_entry = row_df.loc[row_index, "stop_market_or_limit_order_to_use_for_entry"]
    return stop_market_or_limit_order_to_use_for_entry

if __name__=="__main__":



    output_file=f"output_for_place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.txt"
    file_path = os.path.join(os.getcwd(), "output_text_files_limit_order", output_file)
    dirpath=os.path.join(os.getcwd(), "output_text_files_limit_order")
    Path(dirpath).mkdir(parents=True, exist_ok=True)


    # spread_sheet_title = 'streamlit_app_google_sheet'
    # df_with_bfr = fetch_dataframe_from_google_spreadsheet(spread_sheet_title)
    # # if columns in the bfr dataframe are str we convert them to bool
    # column_name_list_which_must_be_converted_from_str_to_bool = \
    #     ["stop_loss_is_technical", "stop_loss_is_calculated", "spot_without_margin", "margin",
    #      "cross_margin", "isolated_margin", "include_last_day_in_bfr_model_assessment",
    #      "trading_pair_is_traded_with_margin", "spot_asset_also_available_as_swap_contract_on_same_exchange",
    #      "suppression_by_closes", "suppression_by_lows"]
    # for column_name in column_name_list_which_must_be_converted_from_str_to_bool:
    #     try:
    #         df_with_bfr = convert_column_to_boolean(df_with_bfr, column_name)
    #     except:
    #         traceback.print_exc()


    with open(file_path, "w") as file:
        # watch forever dataframe from spread sheet
        spread_sheet_title = 'streamlit_app_google_sheet'
        df_with_bfr = fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed(
            spread_sheet_title)
        last_df_with_bfr_was_fetched_at=datetime.datetime.now()
        while True:
            try:
                # Retrieve the arguments passed to the script
                print(f"\nbegan writing to {file.name} at {datetime.datetime.now()}\n")

                current_timestamp=datetime.datetime.now()
                difference_between_current_timestamp_and_when_df_was_last_fetched=current_timestamp-last_df_with_bfr_was_fetched_at
                print("difference_between_current_timestamp_and_when_df_was_last_fetched")
                print(difference_between_current_timestamp_and_when_df_was_last_fetched)
                if difference_between_current_timestamp_and_when_df_was_last_fetched.total_seconds() >= 15:
                    spread_sheet_title = 'streamlit_app_google_sheet'
                    df_with_bfr = fetch_dataframe_from_google_spreadsheet_with_converting_string_types_to_boolean_where_needed(
                        spread_sheet_title)
                    last_df_with_bfr_was_fetched_at = datetime.datetime.now()
                for row_index, row in df_with_bfr.iterrows():
                    # print("row1")
                    # print(pd.DataFrame(row).T.to_string())
                    row_df=pd.DataFrame(row).T

                    try:
                        trade_status = row_df.loc[row_index, "trade_status"]
                        if trade_status == "must_verify_if_bfr_conditions_are_fulfilled":
                            continue

                        utc_position_entry_time_list = list(df_with_bfr["utc_position_entry_time"])
                        # Remove seconds and keep only hours and minutes
                        utc_position_entry_time_list_without_seconds = [time_str.rsplit(':', 1)[0] for time_str in
                                                                        utc_position_entry_time_list]
                        print("utc_position_entry_time_list")
                        print(utc_position_entry_time_list)

                        # current_utc_time = datetime.datetime.now(timezone.utc).strftime('%H:%M')
                        # current_utc_time_without_leading_zero = datetime.datetime.now(timezone.utc).strftime('%-H:%M')
                        # print("current_utc_time")
                        # print(current_utc_time)
                        # print("utc_position_entry_time_list_without_seconds")
                        # print(utc_position_entry_time_list_without_seconds)

                        stock_name_with_underscore_between_base_and_quote_and_exchange = \
                            row_df.loc[row_index, "ticker"]


                        # if current_utc_time not in utc_position_entry_time_list_without_seconds and \
                        #         current_utc_time_without_leading_zero not in utc_position_entry_time_list_without_seconds:
                        #     print(f"for {stock_name_with_underscore_between_base_and_quote_and_exchange} "
                        #           f"current_utc_time not in utc_position_entry_time_list_without_seconds and \
                        #         current_utc_time_without_leading_zero not in utc_position_entry_time_list_without_seconds")
                        #
                        #     continue

                        model_type=row_df.loc[row_index,"model"]

                        trading_pair_with_underscore=stock_name_with_underscore_between_base_and_quote_and_exchange.split("_on_")[0]
                        trading_pair_with_slash=trading_pair_with_underscore.replace("_","/")
                        trading_pair = trading_pair_with_slash

                        exchange_id = stock_name_with_underscore_between_base_and_quote_and_exchange = \
                            row_df.loc[row_index, "exchange"]

                        type_of_sl = row_df.loc[row_index, "market_or_limit_stop_loss"]
                        type_of_tp = row_df.loc[row_index, "market_or_limit_take_profit"]
                        price_of_tp = row_df.loc[row_index, "final_take_profit_price"]
                        price_of_sl = row_df.loc[row_index, "final_stop_loss_price"]
                        price_of_limit_or_stop_order = row_df.loc[row_index, "final_position_entry_price"]

                        spot_cross_or_isolated_margin = ""

                        spot_without_margin_bool = row_df.loc[row_index, "spot_without_margin"]
                        cross_margin_bool = row_df.loc[row_index, "cross_margin"]
                        isolated_margin_bool = row_df.loc[row_index, "isolated_margin"]



                        if spot_without_margin_bool == True:
                            spot_cross_or_isolated_margin = "spot"
                        elif cross_margin_bool == True:
                            spot_cross_or_isolated_margin = "cross"
                        elif isolated_margin_bool == True:
                            spot_cross_or_isolated_margin = "isolated"
                        else:
                            print(f"{spot_cross_or_isolated_margin} is not spot, cross or isolated1")

                        amount_of_asset_for_entry_in_quote_currency = row_df.loc[row_index, "position_size"]

                        post_only_for_limit_tp_bool = False
                        price_of_limit_order = price_of_limit_or_stop_order

                        side_of_limit_order = row_df.loc[row_index, "side"]

                        # Print the values
                        print("\n" + "_________________________________________________________")
                        print("\n" + f"exchange_id :{exchange_id}")
                        print("\n" + f"trading_pair :{trading_pair}")
                        print("\n" + f"price_of_sl :{price_of_sl}")
                        print("\n" + f"type_of_sl :{type_of_sl}")

                        print("\n" + f"price_of_tp :{price_of_tp}")
                        print("\n" + f"type_of_tp :{type_of_tp}")

                        print("\n" + f"post_only_for_limit_tp_bool :{post_only_for_limit_tp_bool}")
                        print("\n" + f"price_of_limit_order :{price_of_limit_order}")
                        print("\n" + f"amount_of_asset_for_entry_in_quote_currency :{amount_of_asset_for_entry_in_quote_currency}")
                        print("\n" + f"side_of_limit_order :{side_of_limit_order}")
                        print("\n"+f"spot_cross_or_isolated_margin :{spot_cross_or_isolated_margin}")

                        # exchange_id="binance"
                        # print("\n"+exchange_id)
                        #
                        # trading_pair="ADA/USDT"
                        # price_of_sl=0.2451
                        # type_of_sl="market"
                        #
                        # price_of_tp=0.2444
                        # type_of_tp="limit"
                        #
                        # post_only_for_limit_tp_bool=False
                        # price_of_limit_order=0.2448
                        #
                        # spot_cross_or_isolated_margin = "cross"
                        #
                        # amount_of_asset_for_entry_in_base_currency=21

                        # amount_of_asset_for_entry_in_base_currency = \
                        #     convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                        #                                                     price_of_limit_order)
                        #
                        # amount_of_sl = amount_of_asset_for_entry_in_base_currency
                        # amount_of_tp = amount_of_asset_for_entry_in_base_currency
                        amount_of_sl = amount_of_asset_for_entry_in_quote_currency
                        amount_of_tp = amount_of_asset_for_entry_in_quote_currency
                        price_of_sl, amount_of_sl, price_of_tp, amount_of_tp, post_only_for_limit_tp_bool, \
                            price_of_limit_order, amount_of_asset_for_entry = \
                            convert_back_from_string_args_to_necessary_types(price_of_sl,
                                                                             amount_of_sl,
                                                                             price_of_tp,
                                                                             amount_of_tp,
                                                                             post_only_for_limit_tp_bool,
                                                                             price_of_limit_order,
                                                                             amount_of_asset_for_entry_in_quote_currency)

                        # side_of_limit_order="sell"

                        # Print the values
                        # print(f"Exchange ID :{exchange_id}" )

                        # print("Trading Pair:", trading_pair)
                        # print("Price of SL:", price_of_sl)
                        # print("Type of SL:", type_of_sl)
                        # print("Amount of SL:", amount_of_sl)
                        # print("Price of TP:", price_of_tp)
                        # print("Type of TP:", type_of_tp)
                        # print("Amount of TP:", amount_of_tp)
                        # print("Post Only for Limit TP (bool):", post_only_for_limit_tp_bool)
                        # print("Price of Limit Order:", price_of_limit_order)
                        # print("Amount of Asset for Entry:", amount_of_asset_for_entry)
                        # print("Side of Limit Order:", side_of_limit_order)

                        entry_price_is_between_sl_and_tp = \
                            check_if_entry_price_is_between_sl_and_tp(file, price_of_sl, price_of_tp, price_of_limit_order,
                                                                      side_of_limit_order)
                        if entry_price_is_between_sl_and_tp:
                            print("\n"+f"spot_cross_or_isolated_margin={spot_cross_or_isolated_margin}")
                            if spot_cross_or_isolated_margin=="spot":
                                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account(df_with_bfr,row_df, row_index, file, exchange_id,
                                                                                                                  trading_pair,
                                                                                                                  price_of_sl, type_of_sl,
                                                                                                                  amount_of_sl,
                                                                                                                  price_of_tp, type_of_tp,
                                                                                                                  amount_of_tp,
                                                                                                                  post_only_for_limit_tp_bool,
                                                                                                                  price_of_limit_order,
                                                                                                                  amount_of_asset_for_entry_in_quote_currency,
                                                                                                                  side_of_limit_order)

                            elif spot_cross_or_isolated_margin=="cross":
                                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(df_with_bfr,row_df, row_index,file, exchange_id,
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
                                                                                                                                  side_of_limit_order)
                            elif spot_cross_or_isolated_margin=="isolated":
                                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(df_with_bfr,row_df, row_index, file, exchange_id,
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
                                                                                                                                  side_of_limit_order)
                            else:
                                print(f"{spot_cross_or_isolated_margin} is neither spot, cross, or isolated")
                        else:
                            print("\n"+"entry price is not between take profit and stop loss")
                            # do checking for the next trading pair
                            continue
                    except:
                        traceback.print_exc()
                        continue
            except:
                traceback.print_exc()
                continue
