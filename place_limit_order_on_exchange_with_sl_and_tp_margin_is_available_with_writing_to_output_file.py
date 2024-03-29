import pprint
import time
import traceback
import sys
import os
import pprint
from datetime import datetime

import pandas as pd

# from verify_that_all_pairs_from_df_are_ready_for_bfr import convert_to_necessary_types_values_from_bfr_dataframe
from api_config import api_dict_for_all_exchanges
from create_order_on_crypto_exchange2 import get_exchange_object_when_api_is_used
import ccxt
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_base_of_trading_pair
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_quote_of_trading_pair
import numpy as np
import toml
from pathlib import Path
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
        file.write("\n"+"unknown_side")
    file.write("\n"+"entry_price_is_between_sl_and_tp")
    file.write("\n"+str(entry_price_is_between_sl_and_tp))
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
        file.write("\n"+"amount_of_quote_currency to be borrowed")
        file.write("\n"+str(amount_of_quote_currency))
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(
            get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair),
            amount_of_quote_currency, symbol=trading_pair, params=params)

        file.write("\n"+"borrowed_margin_loan_when_quote_currency_is_borrowed")
        file.write("\n"+str(borrowed_margin_loan))
    except ccxt.InsufficientFunds:
        file.write("\n"+str(traceback.format_exc()))
        raise SystemExit
    except Exception:
        file.write("\n"+str(traceback.format_exc()))
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
        file.write("\n"+"amount_of_base_currency to be borrowed")
        file.write("\n"+str(amount_of_base_currency))
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(base,
                                                                                  amount_of_base_currency,
                                                                                  symbol=trading_pair, params=params)

        file.write("\n"+"borrowed_margin_loan_when_base_currency_is_borrowed")
        file.write("\n"+str(borrowed_margin_loan))
    except ccxt.InsufficientFunds:
        file.write("\n"+str(traceback.format_exc()))
        raise SystemExit
    except Exception:
        file.write("\n"+str(traceback.format_exc()))
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

        file.write("\n"+"margin_mode")
        file.write("\n"+str(margin_mode))
        # print("12margin_account")
        # pprint.pprint(margin_account)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)

        if margin_mode=="isolated":
            debt_in_quote_currency=margin_account[trading_pair][quote]['debt']
        else:
            debt_in_quote_currency = margin_account[quote]['debt']
        file.write("\n"+"debt_in_quote_currency")
        file.write("\n"+(str(debt_in_quote_currency)))

        # Return the borrowed amount of quote currency
        return debt_in_quote_currency
    except Exception as e:
        file.write("\n"+(str(traceback.format_exc())))
        return f"Error: {str(e)}"

def calculate_debt_amount_of_base_currency(file, margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })


        file.write("\n"+"trading_pair_in_calculate_amount_owed_of_base_currency")
        file.write("\n"+trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        if margin_mode=="isolated":
            debt_in_base_currency=margin_account[trading_pair][base]['debt']
        else:
            debt_in_base_currency = margin_account[base]['debt']
        file.write("\n"+"debt_in_base_currency")
        file.write("\n"+str(debt_in_base_currency))



        # Return the borrowed amount of quote currency
        return debt_in_base_currency
    except Exception as e:
        file.write("\n"+str(traceback.format_exc()))
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

    file.write("\n"+"margin_loan_when_quote_currency_is_borrowed has been repaid")
    file.write("\n"+repaid_margin_loan)
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
    file.write("\n"+"debt_amount_of_base_currency")
    file.write("\n"+str(debt_amount_of_base_currency))
    file.write("\n"+"debt_amount_of_quote_currency")
    file.write("\n"+str(debt_amount_of_quote_currency))

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
    file.write("\n"+"base")
    file.write("\n"+str(base))
    repaid_margin_loan = exchange_object_where_api_is_required.repayMargin(base,
        debt_amount_of_base_currency, symbol=trading_pair, params=params)

    file.write("\n"+"margin_loan_when_base_currency_is_borrowed has been repaid")
    file.write("\n"+str(repaid_margin_loan))
    return repaid_margin_loan
def get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,orders, order_id):
    start_time = time.perf_counter()

    if isinstance(orders,list):
        for order in orders:
            # file.write("\n" + "dict_of_open_cancelled_or_closed_orders")
            # file.write("\n" + str(dict_of_open_cancelled_or_closed_orders))
            # for order in dict_of_open_cancelled_or_closed_orders:
            # file.write("\n" + "order1")
            # file.write("\n" + str(order))
            # print("order_id_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print("order_inside_get_order_status_from_list_of_dictionaries_with_all_orders")
            # print(order)
            # print(f"order['status'] of {order['orderId']}")
            # print(order['status'])
            # print("order['info'].keys()")
            # print(order['info'].keys())
            if 'ordId' in order.keys() and 'orderId' not in order.keys():
                if order['ordId'] == order_id:

                    return order['status']
                else:
                    continue

            elif 'ordId' in order['info'].keys() and 'orderId' not in order['info'].keys():
                if order['info']['ordId'] == order_id:

                    return order['status']
                else:
                    continue

    else:
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
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    # print(
                    #     f"3The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['status']

            elif 'orderId' in order['info'].keys():
                if order['info']['orderId'] == order_id:
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    # print(
                    #     f"4The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")
                    return order['info']['status']

    # print("orders where 'is not in orders' may occur")
    # print(orders)
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(
        f"5The function get_order_status_from_list_of_dictionaries_with_all_orders took {duration} seconds to execute.")


    return f"order_id={order_id} is not in orders"


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
def get_exchange_object_where_api_is_required(exchange_id):
    # Load the secrets from the toml file
    secrets = toml.load("secrets_with_api_private_and_public_keys_for_exchanges.toml")
    # public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    # api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    public_api_key = secrets['secrets'][f"{exchange_id}_api_key"]
    api_secret = secrets['secrets'][f"{exchange_id}_api_secret"]
    trading_password = None

    if exchange_id in ["kucoin","okex5"]:
        try:
            # trading_password = api_dict_for_all_exchanges[exchange_id]['trading_password']
            trading_password = secrets['secrets'][f"{exchange_id}_trading_password"]
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

    elif exchange_object_where_api_is_required.id in ['mexc3','lbank','lbank2']:
        if spot_cross_or_isolated_margin=="spot":
            all_orders_on_spot_account = exchange_object_where_api_is_required.fetch_orders(symbol=trading_pair,
                                                                                            since=None, limit=None,
                                                                                            params={})
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

def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account(file, exchange_id,
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
    file.write("\n"+f"12began writing to {os.path.abspath(file.name)} at {datetime.now()}\n")
    try:
        file.write("\n"+str(exchange_id))
        file.write("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
        file.write("\n" + "exchange_object_where_api_is_required="+ str(exchange_object_where_api_is_required))
    except Exception as e:
        file.write("\n"+str(traceback.format_exc()))
    file.write("\n"+"\n")
    file.write("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    file.write("\n"+"\n")
    # file.write("\n"+side_of_limit_order)
    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)
    amount_of_tp=amount_of_asset_for_entry
    amount_of_sl=amount_of_asset_for_entry
    file.write("\n" + "amount_of_asset_for_entry_in_quote_currency=" +str(amount_of_asset_for_entry_in_quote_currency))
    file.write("\n" + "amount_of_asset_for_entry=" +str(amount_of_asset_for_entry))
    
    if side_of_limit_order == "buy":
        file.write("\n"+f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_spot = ""
        order_id = ""


        params = {}

        limit_buy_order = None
        order_id = ""

        # ---------------------------------------------------------
        try:
            spot_balance = exchange_object_where_api_is_required.fetch_balance()
            file.write("\n"+"spot_balance")
            file.write("\n"+str(spot_balance))
        except:
            file.write(str(traceback.format_exc()))

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # file.write("\n"+"isolated_margin_balance")
        # file.write("\n"+isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        try:
            exchange_object_where_api_is_required.load_markets()
        except ccxt.BadRequest:
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        min_quantity = None
        try:
            # file.write("\n" + "symbol_details")
            # file.write("\n" + str(symbol_details))
            # file.write("\n" + "symbol_details['info']")
            # file.write("\n" + str(symbol_details['info']))
            if exchange_id == "lbank" or exchange_id == "lbank2":
                min_quantity=symbol_details['limits']['amount']['min']
                min_notional_value=min_quantity*float(price_of_limit_order)
                file.write("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n" + str(min_quantity))
                file.write("\n" + "min_notional_value in USD")
                file.write("\n" + str(min_notional_value))
            elif exchange_id == "binance":
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                file.write("\n"+"min_notional_value in USD")
                file.write("\n"+str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                file.write("\n"+
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n"+str(min_quantity))
            elif exchange_id == "mexc3" or exchange_id == "mexc":
                min_notional_value=symbol_details['limits']['cost']['min']
                min_quantity=min_notional_value/float(price_of_limit_order)
                file.write("\n" +
                           f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n" + str(min_quantity))
            elif exchange_id == "okex" or exchange_id == "okex5":
                min_notional_value=symbol_details['limits']['cost']['min']
                if not pd.isna(min_notional_value):
                    min_quantity_calculated_from_min_notional_value=min_notional_value/float(price_of_limit_order)
                    file.write("\n" +
                               f"min_quantity_calculated_from_min_notional_value of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    file.write("\n" + str(min_quantity_calculated_from_min_notional_value))

                min_quantity=symbol_details['limits']['amount']['min']
                min_notional_value_in_usd=min_quantity*float(price_of_limit_order)
                file.write("\n" +
                           f"min_quantity in asset of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")

                file.write("\n" +
                           f"min_notional_value_in_usd of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n" + str(min_notional_value_in_usd))

            else:
                file.write("\n" + "symbol_details")
                file.write("\n" + str(symbol_details))
                min_notional_value = symbol_details['limits']['cost']['min']
                file.write("\n"+"min_notional_value in USD")
                file.write("\n"+str(min_notional_value))

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_limit_order)

                file.write("\n"+
                    f"min_quantity found by division of min_notional_value by price_of_limit_order of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n"+str(min_quantity))
                min_quantity_raw = symbol_details['limits']['amount']['min']
                file.write("\n" +
                           f"min_quantity taken directly from symbol_details dict of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n" + str(min_quantity_raw))
                min_notional_value_calculated_from_min_quantity_raw=min_quantity_raw*float(price_of_limit_order)
                file.write("\n" +
                           f"min_notional_value_calculated_from_min_quantity_raw of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                file.write("\n" + str(min_notional_value_calculated_from_min_quantity_raw))
        except:
            file.write("\n"+str(traceback.format_exc()))

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
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
            except ccxt.InsufficientFunds:
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                    file.write("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
                else:
                    file.write("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception:
                file.write("\n" + str(traceback.format_exc()))

            file.write("\n"+f"placed buy limit order on {exchange_id}")
            file.write("\n"+"limit_buy_order")
            file.write("\n"+str(limit_buy_order))

            order_id = limit_buy_order['id']
            file.write("\n"+"order_id")
            file.write("\n"+str(order_id))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                             spot_cross_or_isolated_margin,
                                                                                             exchange_object_where_api_is_required)
            file.write("\n" + "all_orders_on_spot_account")
            file.write("\n" + str(all_orders_on_spot_account))
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)
            file.write("\n"+"limit_buy_order_status_on_spot1")
            file.write("\n"+str(limit_buy_order_status_on_spot))
            file.write("\n"+"limit_buy_order['status']")
            file.write("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit

        except ccxt.InsufficientFunds:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        except:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file=0
        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account1")
            # pprint.pprint(all_orders_on_spot_account)

            limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)
            # if counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file==0 or\
            #         counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file % 10==0:
            file.write("\n"+"limit_buy_order_status_on_spot")
            file.write("\n"+limit_buy_order_status_on_spot)
            file.write("\n" + f"amount_of_tp={amount_of_tp}")
            if limit_buy_order_status_on_spot == "closed" or\
                    limit_buy_order_status_on_spot == "closed".upper() or\
                    limit_buy_order_status_on_spot == "FILLED":
                file.write("\n" + "i will try to place limit_sell_order_tp right now")
                file.write("\n" + "type_of_tp=" + f"{type_of_tp}")
                #place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id=""
                if type_of_tp == "limit":
                    file.write("\n" + "i will try to place limit_sell_order_tp right now. I am inside type_of_tp == limit")
                    file.write("\n" + f"amount_of_tp={amount_of_tp}")
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "spot"
                        all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status == "FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            file.write("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

                        # take profit has been reached
                        if current_price_of_trading_pair >= price_of_tp:

                            if type_of_tp == "market":
                                market_sell_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    amount = amount_of_asset_for_entry / bid
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                file.write("\n" + "market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_sell_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":

                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)

                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled  with type_of_sl == limit")
                                file.write("\n"+"limit_sell_order_sl has been placed")

                                break
                            elif type_of_sl == "market":
                                file.write("\n" + "market_sell_order_sl is going to be placed")
                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled with type_of_sl == market")

                                market_sell_order_sl=""
                                if exchange_id in ['binance','binanceus'] :
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3','huobi','huobipro']:
                                    file.write("\n" + "market_sell_order_sl is going to be placed1")
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    bid = float(prices[trading_pair]['bid'])
                                    # amount = amount_of_asset_for_entry / bid
                                    amount=amount_of_sl
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                    file.write("\n" + f"1market_sell_order_sl = {market_sell_order_sl}")
                                    file.write("\n" + "1market_sell_order_sl has been placed")
                                else:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                file.write("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                file.write("\n"+"market_sell_order_sl has been placed")

                                break
                            elif type_of_sl == "stop":
                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"stop_market_sell_order_sl has been placed")

                                break
                            else:
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                file.write("\n"+
                    f"{order_id} order has been {limit_buy_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                if counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file == 0 or \
                        counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file % 10 == 0:
                    counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file=\
                        counter_for_how_many_times_string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW_is_written_to_file+1
                    # keep waiting for the order to fill
                    string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW=\
                        "\n"+f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_spot}"
                    file.write(string_to_be_written_to_file_that_the_status_of_limit_order_is_still_NEW)
                time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        file.write("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_spot = ""
        order_id = ""
        params={}
        min_quantity=None
        min_notional_value=None
        try:
            file.write("\n"+f"exchange_object_where_api_is_required = {exchange_object_where_api_is_required}")


            # exchange_object_where_api_is_required.load_markets()
            # __________________________________
            # ---------------------------------------------------------
            try:
                spot_balance = exchange_object_where_api_is_required.fetch_balance()
                file.write("\n" + "spot_balance")
                file.write("\n" + str(spot_balance))
            except:
                file.write(str(traceback.format_exc()))

            # Load the valid trading symbols
            try:
                exchange_object_where_api_is_required.load_markets()
            except ccxt.BadRequest:
                file.write(str(traceback.format_exc()))
            except Exception:
                file.write(str(traceback.format_exc()))

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
                # file.write("\n" + "symbol_details")
                # file.write("\n" + str(symbol_details))
                # file.write("\n" + "symbol_details['info']")
                # file.write("\n" + str(symbol_details['info']))
                if exchange_id == "lbank" or exchange_id == "lbank2":
                    min_quantity = symbol_details['limits']['amount']['min']
                    min_notional_value = min_quantity * float(price_of_limit_order)
                    file.write("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    file.write("\n" + str(min_quantity))
                    file.write("\n" + "min_notional_value in USD")
                    file.write("\n" + str(min_notional_value))
                elif exchange_id == "binance":
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    file.write("\n" + "min_notional_value in USD")
                    file.write("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    file.write("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    file.write("\n" + str(min_quantity))
                elif exchange_id == "mexc3" or exchange_id == "mexc":
                    min_quantity = symbol_details['limits']['cost']['min']
                    file.write("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    file.write("\n" + str(min_quantity))
                else:
                    file.write("\n" + "symbol_details")
                    file.write("\n" + str(symbol_details))
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    file.write("\n" + "min_notional_value in USD")
                    file.write("\n" + str(min_notional_value))

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_limit_order)

                    file.write("\n" +
                               f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    file.write("\n" + str(min_quantity))
            except:
                file.write("\n" + str(traceback.format_exc()))

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
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit

            file.write("\n"+f"placed sell limit order on {exchange_id}")
            file.write("\n"+"limit_sell_order")
            file.write("\n"+str(limit_sell_order))

            order_id=get_order_id(limit_sell_order)
            file.write("\n"+"order_id5")
            print(str(order_id))

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)
            file.write("\n"+"limit_sell_order_status_on_spot1")
            file.write("\n"+str(limit_sell_order_status_on_spot))
            file.write("\n"+"limit_sell_order['status']")
            print(str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit


        except:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the sell order to get filled")
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

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_spot_account, order_id)

            file.write("\n"+"limit_sell_order_status_on_spot2")
            file.write("\n"+str(limit_sell_order_status_on_spot))



            if limit_sell_order_status_on_spot == "closed" or\
                    limit_sell_order_status_on_spot == "closed".upper() or\
                    limit_sell_order_status_on_spot == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id=""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id=get_order_id(limit_buy_order_tp)

                # keep looking at the price and wait till either sl or tp has been reached. At the same time look for tp to get filled
                while True:

                    try:
                        #keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "spot"
                        all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status=="FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            #stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            file.write("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:


                            if type_of_tp == "market":
                                market_buy_order_tp = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                file.write("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,trading_pair,params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"limit_buy_order_sl has been placed")

                                break
                            elif type_of_sl == "market":
                                if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                market_buy_order_sl = ""
                                if exchange_id in ['binance', 'binanceus']:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                    prices = exchange_object_where_api_is_required.fetch_tickers()
                                    ask = float(prices[trading_pair]['ask'])
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                file.write("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                file.write("\n" + "market_buy_order_sl has been placed")

                                break
                            elif type_of_sl == "stop":
                                if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")

                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"stop_market_buy_order_sl has been placed")

                                break
                            else:
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                file.write("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                file.write("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_spot}")
                time.sleep(1)
                continue


    else:
        file.write("\n"+f"unknown {side_of_limit_order} value")
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
    print(f"12began writing to {file.name} at {datetime.now()}\n")
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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))

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
            print("limit_buy_order")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id4")
            print(order_id)

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            print("limit_buy_order_status_on_cross_margin1")
            print(limit_buy_order_status_on_cross_margin)
            print("limit_buy_order['status']")
            print(limit_buy_order['status'])

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

            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
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

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status == "FILLED":
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
                                    amount = amount_of_asset_for_entry / bid
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                file.write("\n" + "market_sell_order_tp has been placed")
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
                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
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
                                    amount = amount_of_asset_for_entry / bid
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                file.write("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                file.write("\n" + "market_sell_order_sl has been placed")
                                print("market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "stop":
                                stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
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
                time.sleep(1)
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
                file.write(str(traceback.format_exc()))
            except Exception:
                file.write(str(traceback.format_exc()))

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]
            try:
                # Get the minimum notional value for the symbol
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


            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
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

            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
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
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status == "FILLED":
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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                file.write("\n" + "market_buy_order_tp has been placed")
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
                                if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                file.write("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                file.write("\n" + "market_buy_order_sl has been placed")
                                print("market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
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
                time.sleep(1)
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
    print(f"12began writing to {file.name} at {datetime.now()}\n")
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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value=None
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
            print("limit_buy_order")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id4")
            print(order_id)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            print("limit_buy_order_status_on_isolated_margin1")
            print(limit_buy_order_status_on_isolated_margin)
            print("limit_buy_order['status']")
            print(limit_buy_order['status'])

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

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
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
                            time.sleep(1)
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
                time.sleep(1)
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
                file.write(str(traceback.format_exc()))
            except Exception:
                file.write(str(traceback.format_exc()))

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

            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
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

            limit_sell_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,all_orders_on_isolated_margin_account, order_id)




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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                file.write("\n" + "market_buy_order_tp has been placed")
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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                file.write("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                file.write("\n" + "market_buy_order_sl has been placed")
                                print("market_buy_order_sl has been placed")
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                print("stop_market_buy_order_sl has been placed")
                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
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
                time.sleep(1)
                continue


    else:
        print(f"unknown {side_of_limit_order} value")


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(file, exchange_id,
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
    file.write("\n"+f"12began writing to {file.name} at {datetime.now()}\n")
    try:
        file.write("\n"+str(exchange_id))
        file.write("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        file.write("\n"+str(traceback.format_exc()))
    file.write("\n"+"\n")
    file.write("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    file.write("\n"+"\n")
    # print(side_of_limit_order)
    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)

    if side_of_limit_order == "buy":
        file.write("\n"+f"placing buy limit order on {exchange_id}")
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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            file.write("\n"+"min_notional_value in USD")
            file.write("\n"+str(min_notional_value))

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            file.write("\n"+
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            file.write("\n"+str(min_quantity))
        except:
            file.write("\n"+str(traceback.format_exc()))

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
            file.write("\n"+"margin_loan_when_quote_currency_is_borrowed")
            file.write("\n"+str(margin_loan_when_quote_currency_is_borrowed))

            # if borrowed_margin_loan['info']['code'] == 200:
            #     print("borrowed_margin_loan['info']['code'] == 200")
            #     print(borrowed_margin_loan['info']['code'] == 200)


            try:
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
                file.write("\n"+"created_limit_buy_order")
            except ccxt.InsufficientFunds:
                file.write("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                file.write("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                    file.write("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    file.write("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit
            file.write("\n"+f"placed buy limit order on {exchange_id}")
            file.write("\n"+"limit_buy_order")
            file.write("\n"+str(limit_buy_order))

            order_id = limit_buy_order['id']
            file.write("\n"+"order_id4")
            file.write("\n"+str(order_id))

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            file.write("\n"+"limit_buy_order_status_on_cross_margin1")
            file.write("\n"+str(limit_buy_order_status_on_cross_margin))
            file.write("\n"+"limit_buy_order['status']")
            file.write("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
            # print("all_orders_on_cross_margin_account1")
            # pprint.pprint(all_orders_on_cross_margin_account)

            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            file.write("\n"+"limit_buy_order_status_on_cross_margin")
            file.write("\n"+str(limit_buy_order_status_on_cross_margin))
            if limit_buy_order_status_on_cross_margin == "closed" or\
                    limit_buy_order_status_on_cross_margin == "closed".upper() or\
                    limit_buy_order_status_on_cross_margin == "FILLED":

                # place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)




                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status == "FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

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
                            file.write("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

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
                                    amount = amount_of_asset_for_entry / bid
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                file.write("\n" + "market_sell_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":
                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"limit_sell_order_sl has been placed")

                                # cancel tp because sl has been hit

                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

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
                                    if limit_sell_order_tp_order_status != "CANCELED" and limit_sell_order_tp_order_status != "CANCELLED":
                                        exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    market_sell_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        bid = float(prices[trading_pair]['bid'])
                                        amount = amount_of_asset_for_entry / bid
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'sell', amount,
                                            price=bid)
                                    else:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    file.write("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                    file.write("\n" + "market_sell_order_sl has been placed")
                                    # market_sell_order_sl=\
                                    #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                    file.write("\n"+"market_sell_order_sl has been placed")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    file.write("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    file.write("\n"+str(traceback.format_exc()))

                                # # cancel tp because sl has been hit
                                # if limit_sell_order_tp_order_status != "CANCELED" and limit_sell_order_tp_order_status != "CANCELLED":
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
                                file.write("\n"+"stop_market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

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
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                file.write("\n"+
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
                file.write("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_cross_margin}")
                time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        file.write("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_cross_margin = ""
        order_id = ""
        params = {'type': 'margin',
                  'isIsolated': False  # Set the margin type to cross
                  }
        min_quantity = None
        min_notional_value=None
        # Get the symbol details


        file.write("\n"+f"exchange_object_where_api_is_required={exchange_object_where_api_is_required}")


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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        try:
            # Get the minimum notional value for the symbol
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']

            file.write("\n"+"min_notional_value in USD")
            file.write("\n"+str(min_notional_value))

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            file.write("\n"+
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            file.write("\n"+str(min_quantity))
        except:
            file.write("\n"+str(traceback.format_exc()))

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
            file.write("\n"+"margin_loan_when_base_currency_is_borrowed")
            file.write("\n"+str(margin_loan_when_base_currency_is_borrowed))


            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                file.write("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                file.write("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit

            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                    file.write("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    file.write("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit
            file.write("\n"+f"placed sell limit order on {exchange_id}")
            file.write("\n"+"limit_sell_order")
            file.write("\n"+str(limit_sell_order))

            order_id = limit_sell_order['id']
            file.write("\n"+"order_id5")
            file.write("\n"+str(order_id))

            spot_cross_or_isolated_margin = "cross"
            all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)
            file.write("\n"+"limit_sell_order_status_on_cross_margin1")
            file.write("\n"+limit_sell_order_status_on_cross_margin)
            file.write("\n"+"limit_sell_order['status']")
            file.write("\n"+str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit


        except Exception:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the sell order to get filled")
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

            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_cross_margin_account, order_id)

            file.write("\n"+"limit_sell_order_status_on_cross_margin3")
            file.write("\n"+str(limit_sell_order_status_on_cross_margin))

            if limit_sell_order_status_on_cross_margin == "closed" or\
                    limit_sell_order_status_on_cross_margin == "closed".upper() or limit_sell_order_status_on_cross_margin == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_cross_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status == "FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            file.write("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                file.write("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)
                                break
                            elif type_of_sl == "market":
                                try:
                                    if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                        exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    market_buy_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        ask = float(prices[trading_pair]['ask'])
                                        amount = amount_of_asset_for_entry / ask
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'buy', amount,
                                            price=ask)
                                    else:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    file.write("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                    file.write("\n" + "market_buy_order_sl has been placed")


                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    file.write("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    file.write("\n"+str(traceback.format_exc()))
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"stop_market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                file.write("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                break
            else:
                # keep waiting for the order to fill
                file.write("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_cross_margin}")
                time.sleep(1)
                continue


    else:
        file.write("\n"+f"unknown {side_of_limit_order} value")



def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(file, exchange_id,
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
    file.write("\n"+f"12began writing to {file.name} at {datetime.now()}\n")
    try:
        file.write("\n"+str(exchange_id))
        file.write("\n"+"\n")
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    except Exception as e:
        file.write("\n"+str(traceback.format_exc()))
    file.write("\n"+"\n")
    file.write("\n"+str(exchange_object_where_api_is_required))
    exchange_object_without_api = get_exchange_object6(exchange_id)
    file.write("\n"+"\n")
    # print(side_of_limit_order)

    amount_of_asset_for_entry = \
        convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,
                                                        price_of_limit_order)
    if side_of_limit_order == "buy":
        file.write("\n"+f"placing buy limit order on {exchange_id}")
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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            file.write("\n"+"min_notional_value in USD")
            file.write("\n"+str(min_notional_value))

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            file.write("\n"+
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            file.write("\n"+str(min_quantity))
        except:
            file.write("\n"+str(traceback.format_exc()))

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
            file.write("\n"+"margin_loan_when_quote_currency_is_borrowed")
            file.write("\n"+str(margin_loan_when_quote_currency_is_borrowed))

            # if borrowed_margin_loan['info']['code'] == 200:
            #     print("borrowed_margin_loan['info']['code'] == 200")
            #     print(borrowed_margin_loan['info']['code'] == 200)


            try:
                limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                               amount_of_asset_for_entry,
                                                                                               price_of_limit_order,
                                                                                               params=params)
                file.write("\n"+"created_limit_buy_order")
            except ccxt.InsufficientFunds:
                file.write("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                file.write("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                    file.write("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    file.write("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit
            file.write("\n"+f"placed buy limit order on {exchange_id}")
            file.write("\n"+"limit_buy_order")
            file.write("\n"+str(limit_buy_order))

            order_id = limit_buy_order['id']
            file.write("\n"+"order_id4")
            file.write("\n"+str(order_id))

            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            file.write("\n"+"limit_buy_order_status_on_isolated_margin1")
            file.write("\n"+str(limit_buy_order_status_on_isolated_margin))
            file.write("\n"+"limit_buy_order['status']")
            file.write("\n"+str(limit_buy_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit

        except:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
            # print("all_orders_on_isolated_margin_account1")
            # pprint.pprint(all_orders_on_isolated_margin_account)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            file.write("\n"+"limit_buy_order_status_on_isolated_margin")
            file.write("\n"+str(limit_buy_order_status_on_isolated_margin))
            if limit_buy_order_status_on_isolated_margin == "closed" or\
                    limit_buy_order_status_on_isolated_margin == "closed".upper() or\
                    limit_buy_order_status_on_isolated_margin == "FILLED":

                # place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)




                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "isolated"
                        all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_isolated_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status == "FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

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
                            file.write("\n"+f"take profit order with id = {limit_sell_order_tp_order_id} has "
                                  f"status {limit_sell_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")

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
                                    amount = amount_of_asset_for_entry / bid
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'sell', amount,
                                        price=bid)
                                else:
                                    market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_sell_order_tp = {market_sell_order_tp}")
                                file.write("\n" + "market_sell_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_sell_order_tp has been placed")

                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair <= price_of_sl:
                            if type_of_sl == "limit":
                                limit_sell_order_sl = exchange_object_where_api_is_required.create_limit_sell_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"limit_sell_order_sl has been placed")

                                # cancel tp because sl has been hit

                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

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
                                    if limit_sell_order_tp_order_status != "CANCELED" and limit_sell_order_tp_order_status != "CANCELLED":
                                        exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    market_sell_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        bid = float(prices[trading_pair]['bid'])
                                        amount = amount_of_asset_for_entry / bid
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'sell', amount,
                                            price=bid)
                                    else:
                                        market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_sl, params=params)
                                    file.write("\n" + f"market_sell_order_sl = {market_sell_order_sl}")
                                    file.write("\n" + "market_sell_order_sl has been placed")
                                    # market_sell_order_sl=\
                                    #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)


                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    file.write("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    file.write("\n"+str(traceback.format_exc()))

                                # # cancel tp because sl has been hit
                                # if limit_sell_order_tp_order_status != "CANCELED" and limit_sell_order_tp_order_status != "CANCELLED":
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
                                file.write("\n"+"stop_market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

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
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                file.write("\n"+
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
                file.write("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_isolated_margin}")
                time.sleep(1)
                continue



    elif side_of_limit_order == "sell":
        file.write("\n"+f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_isolated_margin = ""
        order_id = ""
        params = {'type': 'margin',
                  'isIsolated': True  # Set the margin type to isolated
                  }
        min_quantity = None
        min_notional_value=None
        # Get the symbol details


        file.write("\n"+f"exchange_object_where_api_is_required={exchange_object_where_api_is_required}")


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
            file.write(str(traceback.format_exc()))
        except Exception:
            file.write(str(traceback.format_exc()))
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        try:
            # Get the minimum notional value for the symbol
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']

            file.write("\n"+"min_notional_value in USD")
            file.write("\n"+str(min_notional_value))

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_limit_order)

            file.write("\n"+
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            file.write("\n"+str(min_quantity))
        except:
            file.write("\n"+str(traceback.format_exc()))

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
            file.write("\n"+"margin_loan_when_base_currency_is_borrowed")
            file.write("\n"+str(margin_loan_when_base_currency_is_borrowed))


            try:
                limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                 amount_of_asset_for_entry,
                                                                                                 price_of_limit_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                file.write("\n"+f"Account on {exchange_id} has insufficient balance for the requested action")
                file.write("\n"+str(traceback.format_exc()))

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)

                raise SystemExit

            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                    file.write("\n"+
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    raise SystemExit
                else:
                    file.write("\n" + str(traceback.format_exc()))
                    raise SystemExit
            except Exception as e:

                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                file.write("\n"+str(traceback.format_exc()))
                raise SystemExit
            file.write("\n"+f"placed sell limit order on {exchange_id}")
            file.write("\n"+"limit_sell_order")
            file.write("\n"+str(limit_sell_order))

            order_id = limit_sell_order['id']
            file.write("\n"+"order_id5")
            file.write("\n"+str(order_id))

            spot_cross_or_isolated_margin = "isolated"
            all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)


            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)
            file.write("\n"+"limit_sell_order_status_on_isolated_margin1")
            file.write("\n"+str(limit_sell_order_status_on_isolated_margin))
            file.write("\n"+"limit_sell_order['status']")
            file.write("\n"+str(limit_sell_order['status']))

        except ccxt.InvalidOrder as e:
            if "Filter failure: NOTIONAL" in str(e):
                file.write("\n"+"Invalid order: Filter failure: NOTIONAL")
                file.write("\n"+
                    f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                    f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                    f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                raise SystemExit
            else:
                file.write("\n" + str(traceback.format_exc()))
                raise SystemExit


        except Exception:
            file.write("\n"+str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            file.write("\n"+"waiting for the sell order to get filled")
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

            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                all_orders_on_isolated_margin_account, order_id)

            file.write("\n"+"limit_sell_order_status_on_isolated_margin3")
            file.write("\n"+str(limit_sell_order_status_on_isolated_margin))

            if limit_sell_order_status_on_isolated_margin == "closed" or\
                    limit_sell_order_status_on_isolated_margin == "closed".upper() or limit_sell_order_status_on_isolated_margin == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id = ""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    file.write("\n"+"limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    try:
                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "isolated"
                        all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(exchange_object_where_api_is_required,
                            all_orders_on_isolated_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status == "FILLED":
                            file.write("\n"+f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            # stop looking at the price to place stop loss because take profit has been filled
                            break
                        else:
                            file.write("\n"+f"take profit order with id = {limit_buy_order_tp_order_id} has "
                                  f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")

                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write("\n"+f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                        file.write("\n"+f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
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
                                    amount = amount_of_asset_for_entry / ask
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_order(
                                        trading_pair, 'buy', amount,
                                        price=ask)
                                else:
                                    market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_tp, params=params)
                                file.write("\n" + f"market_buy_order_tp = {market_buy_order_tp}")
                                file.write("\n" + "market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                file.write("\n"+"stop_market_buy_order_tp has been placed")
                                break
                            elif type_of_tp == "limit":
                                file.write("\n"+"price of limit tp has been reached")
                            else:
                                file.write("\n"+f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"limit_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)
                                break
                            elif type_of_sl == "market":
                                try:
                                    if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                        exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                           trading_pair, params=params)
                                        file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    market_buy_order_sl = ""
                                    if exchange_id in ['binance', 'binanceus']:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    if exchange_id in ['mexc3', 'huobi', 'huobipro']:
                                        prices = exchange_object_where_api_is_required.fetch_tickers()
                                        ask = float(prices[trading_pair]['ask'])
                                        amount = amount_of_asset_for_entry / ask
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_order(
                                            trading_pair, 'buy', amount,
                                            price=ask)
                                    else:
                                        market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_sl, params=params)
                                    file.write("\n" + f"market_buy_order_sl = {market_buy_order_sl}")
                                    file.write("\n" + "market_buy_order_sl has been placed")


                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    file.write("\n"+str(traceback.format_exc()))
                                except Exception as e:
                                    file.write("\n"+str(traceback.format_exc()))
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                file.write("\n"+"stop_market_buy_order_sl has been placed")
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    file.write("\n"+f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                break
                            else:
                                file.write("\n"+f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("\n"+"neither sl nor tp has been reached")
                            continue
                    except ccxt.RequestTimeout:
                        file.write("\n"+str(traceback.format_exc()))
                        continue

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                file.write("\n"+
                    f"{order_id} order has been {limit_sell_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")
                # repay margin loan because the initial limit buy order has been cancelled
                repay_margin_loan_when_base_currency_is_borrowed(file, margin_mode, trading_pair,
                                                                  exchange_object_without_api,
                                                                  amount_of_asset_for_entry,
                                                                  exchange_object_where_api_is_required, params)
                break
            else:
                # keep waiting for the order to fill
                file.write("\n"+
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_isolated_margin}")
                time.sleep(1)
                continue


    else:
        file.write("\n"+f"unknown {side_of_limit_order} value")



if __name__=="__main__":
    exchange_id = sys.argv[1]
    trading_pair = sys.argv[2]
    trading_pair_with_underscore=trading_pair.replace("/","_")
    output_file=f"output_for_place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file_{trading_pair_with_underscore}_on_{exchange_id}.txt"
    file_path = os.path.join(os.getcwd(), "output_text_files_limit_order", output_file)
    dirpath=os.path.join(os.getcwd(), "output_text_files_limit_order")
    Path(dirpath).mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as file:
        # Retrieve the arguments passed to the script
        print(f"\nbegan writing to {file.name} at {datetime.now()}\n")
        for arg in sys.argv[1:]:
            file.write("\n"+arg+"\n")
        file.write("\n"+sys.argv[1])
        args = sys.argv[1:]  # Exclude the first argument, which is the script filename
        print(sys.argv)
        # Print the arguments
        print("Arguments:", args)

        exchange_id = sys.argv[1]


        trading_pair = sys.argv[2]
        price_of_sl = sys.argv[3]
        type_of_sl = sys.argv[4]
        amount_of_sl = sys.argv[5]
        price_of_tp = sys.argv[6]
        type_of_tp = sys.argv[7]
        amount_of_tp = sys.argv[8]
        post_only_for_limit_tp_bool = sys.argv[9]
        price_of_limit_order = sys.argv[10]
        amount_of_asset_for_entry_in_quote_currency = sys.argv[11]
        side_of_limit_order = sys.argv[12]
        spot_cross_or_isolated_margin = sys.argv[13]
        # Print the values
        file.write("\n" + f"exchange_id :{exchange_id}")
        file.write("\n" + f"trading_pair :{trading_pair}")
        file.write("\n" + f"price_of_sl :{price_of_sl}")
        file.write("\n" + f"type_of_sl :{type_of_sl}")
        file.write("\n" + f"amount_of_sl :{amount_of_sl}")
        file.write("\n" + f"price_of_tp :{price_of_tp}")
        file.write("\n" + f"type_of_tp :{type_of_tp}")
        file.write("\n" + f"amount_of_tp :{amount_of_tp}")
        file.write("\n" + f"post_only_for_limit_tp_bool :{post_only_for_limit_tp_bool}")
        file.write("\n" + f"price_of_limit_order :{price_of_limit_order}")
        file.write("\n" + f"amount_of_asset_for_entry_in_quote_currency :{amount_of_asset_for_entry_in_quote_currency}")
        file.write("\n" + f"side_of_limit_order :{spot_cross_or_isolated_margin}")
        file.write("\n"+f"spot_cross_or_isolated_margin :{spot_cross_or_isolated_margin}")

        # exchange_id="binance"
        # file.write("\n"+exchange_id)
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
        price_of_sl, amount_of_sl, price_of_tp, amount_of_tp, post_only_for_limit_tp_bool, \
            price_of_limit_order, amount_of_asset_for_entry = \
            convert_back_from_string_args_to_necessary_types(price_of_sl,
                                                             amount_of_sl,
                                                             price_of_tp,
                                                             amount_of_tp,
                                                             post_only_for_limit_tp_bool,
                                                             price_of_limit_order,
                                                             amount_of_asset_for_entry_in_quote_currency)

        amount_of_sl =amount_of_asset_for_entry_in_quote_currency
        amount_of_tp=amount_of_asset_for_entry_in_quote_currency
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
            file.write("\n"+f"spot_cross_or_isolated_margin={spot_cross_or_isolated_margin}")
            if spot_cross_or_isolated_margin=="spot":
                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account(file, exchange_id,
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
                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(file, exchange_id,
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
                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(file, exchange_id,
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
                file.write(f"{spot_cross_or_isolated_margin} is neither spot, cross, or isolated")
        else:
            file.write("\n"+"entry price is not between take profit and stop loss")