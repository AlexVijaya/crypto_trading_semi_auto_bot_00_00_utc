import pprint
import time
import traceback
import sys
import os
import pprint
from datetime import datetime
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

def convert_price_in_base_asset_into_quote_currency(amount_of_asset_for_entry_in_quote_currency,price_of_entry_order):
    amount_of_asset_for_entry_in_base_currency = float(amount_of_asset_for_entry_in_quote_currency) / float(
        price_of_entry_order)
    return amount_of_asset_for_entry_in_base_currency
def check_if_entry_price_is_between_sl_and_tp(price_of_sl,price_of_tp,order_price,side):
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
        print("unknown_side")
    print("entry_price_is_between_sl_and_tp")
    print(entry_price_is_between_sl_and_tp)
    return entry_price_is_between_sl_and_tp
def get_current_timestamp_in_milliseconds():
    timestamp_ms = int(time.time() * 1000)
    return timestamp_ms

def get_current_timestamp_in_seconds():
    timestamp_s = int(time.time())
    return timestamp_s

def borrow_margin_loan_when_quote_currency_is_borrowed(trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    borrowed_margin_loan = np.nan
    try:
        amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)
        print("amount_of_quote_currency to be borrowed")
        print(amount_of_quote_currency)
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(
            get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair),
            amount_of_quote_currency, symbol=trading_pair, params=params)

        print("borrowed_margin_loan_when_quote_currency_is_borrowed")
        print(borrowed_margin_loan)
    except ccxt.InsufficientFunds:
        traceback.print_exc()
        raise SystemExit
    except Exception:
        traceback.print_exc()
        raise SystemExit

    return borrowed_margin_loan

def borrow_margin_loan_when_base_currency_is_borrowed(trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    borrowed_margin_loan = np.nan
    try:
        amount_of_base_currency = amount_of_asset_for_entry
        base = get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        print("amount_of_base_currency to be borrowed")
        print(amount_of_base_currency)
        borrowed_margin_loan = exchange_object_where_api_is_required.borrowMargin(base,
                                                                                  amount_of_base_currency,
                                                                                  symbol=trading_pair, params=params)

        print("borrowed_margin_loan_when_base_currency_is_borrowed")
        print(borrowed_margin_loan)
    except ccxt.InsufficientFunds:
        traceback.print_exc()
        raise SystemExit
    except Exception:
        traceback.print_exc()
        raise SystemExit
    return borrowed_margin_loan
def calculate_total_amount_of_quote_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"

def calculate_total_amount_of_base_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"
def calculate_used_amount_of_quote_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"

def calculate_used_amount_of_base_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"
def calculate_free_amount_of_quote_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"

def calculate_free_amount_of_base_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
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
        traceback.print_exc()
        return f"Error: {str(e)}"
def calculate_debt_amount_of_quote_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_mode")
        print(margin_mode)
        print("12margin_account")
        pprint.pprint(margin_account)
        quote=get_quote_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)

        if margin_mode=="isolated":
            debt_in_quote_currency=margin_account[trading_pair][quote]['debt']
        else:
            debt_in_quote_currency = margin_account[quote]['debt']
        print("debt_in_quote_currency")
        print(debt_in_quote_currency)

        # Return the borrowed amount of quote currency
        return debt_in_quote_currency
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"

def calculate_debt_amount_of_base_currency(margin_mode, exchange_object_where_api_is_required, trading_pair):
    try:
        # Fetch the margin account details
        margin_account = exchange_object_where_api_is_required.fetchBalance({"marginMode" : margin_mode })

        print("margin_account")
        pprint.pprint(margin_account)
        print("trading_pair_in_calculate_amount_owed_of_base_currency")
        print(trading_pair)
        base=get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)
        if margin_mode=="isolated":
            debt_in_base_currency=margin_account[trading_pair][base]['debt']
        else:
            debt_in_base_currency = margin_account[base]['debt']
        print("debt_in_base_currency")
        print(debt_in_base_currency)
        print("type(debt_in_base_currency)")
        print(type(debt_in_base_currency))


        # Return the borrowed amount of quote currency
        return debt_in_base_currency
    except Exception as e:
        traceback.print_exc()
        return f"Error: {str(e)}"
def repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    # amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)

    debt_amount_of_quote_currency=calculate_debt_amount_of_quote_currency(margin_mode,
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

    print("margin_loan_when_quote_currency_is_borrowed has been repaid")
    print(repaid_margin_loan)
    return repaid_margin_loan

def repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                       exchange_object_without_api,
                                                      amount_of_asset_for_entry,
                                                      exchange_object_where_api_is_required,params):
    # amount_of_quote_currency = amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)

    debt_amount_of_base_currency=calculate_debt_amount_of_base_currency(margin_mode,
                                                                          exchange_object_where_api_is_required,
                                                                          trading_pair)
    debt_amount_of_quote_currency = calculate_debt_amount_of_quote_currency(margin_mode,
                                                                          exchange_object_where_api_is_required,
                                                                          trading_pair)
    print("debt_amount_of_base_currency")
    print(debt_amount_of_base_currency)
    print("debt_amount_of_quote_currency")
    print(debt_amount_of_quote_currency)

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
    print("base")
    print(base)
    repaid_margin_loan = exchange_object_where_api_is_required.repayMargin(base,
        debt_amount_of_base_currency, symbol=trading_pair, params=params)

    print("margin_loan_when_base_currency_is_borrowed has been repaid")
    print(repaid_margin_loan)
    return repaid_margin_loan
def  get_order_status_from_list_of_dictionaries_with_all_orders(orders, order_id):
    start_time = time.perf_counter()
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

    if exchange_id in [ "kucoin","okex5"]:
        try:
            # trading_password = api_dict_for_all_exchanges[exchange_id]['trading_password']
            trading_password = secrets['secrets'][f"{exchange_id}_trading_password"]
        except:
            traceback.print_exc()

    exchange_object_where_api_is_required = \
        get_exchange_object_with_api_key(exchange_name=exchange_id,
                                         public_api_key=public_api_key
                                         , api_secret=api_secret,
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
        traceback.print_exc()
def get_order_id(order):
    order_id=order['id']
    return order_id

def get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,spot_cross_or_isolated_margin,exchange_object_where_api_is_required):
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


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_spot_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)

    if side_of_stop_market_order == "buy":
        print(f"placing buy limit order on {exchange_id}")
        limit_buy_order = None
        limit_buy_order_status_on_spot = ""
        order_id = ""

        # we want to place a buy order with isolated margin
        params = {}

        limit_buy_order = None
        order_id = ""

        # ---------------------------------------------------------
        spot_balance = exchange_object_where_api_is_required.fetch_balance()
        print("spot_balance")
        print(spot_balance)

        # # show balance on isolated margin
        # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
        # print("isolated_margin_balance")
        # print(isolated_margin_balance)
        # # __________________________

        # Load the valid trading symbols
        exchange_object_where_api_is_required.load_markets()

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        min_quantity = None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

            print(
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            print(min_quantity)
        except:
            traceback.print_exc()

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
                                                                                               price_of_stop_market_order,
                                                                                               params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit

            print(f"placed buy limit order on {exchange_id}")
            print("limit_buy_order")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id")
            print(order_id)

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            print("all_orders_on_spot_account")
            pprint.pprint(all_orders_on_spot_account)

            limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(
                all_orders_on_spot_account, order_id)
            print("limit_buy_order_status_on_spot1")
            print(limit_buy_order_status_on_spot)
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

        except ccxt.InsufficientFunds:
            traceback.print_exc()
            raise SystemExit

        except:
            print(str(traceback.format_exc()))
            raise SystemExit

        # wait till order is filled (that is closed)
        while True:
            print("waiting for the buy order to get filled")
            # sapi_get_margin_allorders works only for binance
            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account1")
            # pprint.pprint(all_orders_on_spot_account)

            limit_buy_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(
                all_orders_on_spot_account, order_id)
            print("limit_buy_order_status_on_spot")
            print(limit_buy_order_status_on_spot)
            if limit_buy_order_status_on_spot == "closed" or\
                    limit_buy_order_status_on_spot == "closed".upper() or\
                    limit_buy_order_status_on_spot == "FILLED":
                #place take profit right away as soon as limit order has been fulfilled
                limit_sell_order_tp_order_id=""
                if type_of_tp == "limit":
                    limit_sell_order_tp = exchange_object_where_api_is_required.create_limit_sell_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("limit_sell_order_tp has been placed")
                    limit_sell_order_tp_order_id = get_order_id(limit_sell_order_tp)
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

                    # keep looking if limit take profit has been filled
                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_account, limit_sell_order_tp_order_id)
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

                        if type_of_tp == "market":
                            market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_tp, params=params)
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
                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_sl, params=params)
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

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_buy_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(),
                                                               "cancelled".upper()]:
                print(
                    f"{order_id} order has been {limit_buy_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print(
                    f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_spot}")
                time.sleep(1)
                continue



    elif side_of_stop_market_order == "sell":
        print(f"placing sell limit order on {exchange_id}")
        limit_sell_order = None
        limit_sell_order_status_on_spot = ""
        order_id = ""
        params={}
        min_quantity=None
        min_notional_value=None
        try:
            print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


            # exchange_object_where_api_is_required.load_markets()
            # __________________________________
            # # show balance on spot
            spot_balance = exchange_object_where_api_is_required.fetch_balance()
            print("spot_balance")
            print(spot_balance)

            # # show balance on cross margin
            # cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
            # print("cross_margin_balance")
            # print(cross_margin_balance)

            # show balance on isolated margin
            isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
            print("isolated_margin_balance")
            print(isolated_margin_balance)
            # __________________________

            # Load the valid trading symbols
            exchange_object_where_api_is_required.load_markets()

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            # # Get the minimum notional value for the symbol
            # min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            #
            # print("min_notional_value in USD")
            # print(min_notional_value)

            # Get the minimum notional value for the symbol

            try:
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("min_notional_value in USD")
                print(min_notional_value)

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print(
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print(min_quantity)
            except:
                traceback.print_exc()

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
                                                                                                 price_of_stop_market_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit

            print(f"placed sell limit order on {exchange_id}")
            print("limit_sell_order")
            print(limit_sell_order)

            order_id=get_order_id(limit_sell_order)
            print("order_id5")
            print(order_id)

            spot_cross_or_isolated_margin = "spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            # print("all_orders_on_spot_account")
            # pprint.pprint(all_orders_on_spot_account)

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(
                all_orders_on_spot_account, order_id)
            print("limit_sell_order_status_on_spot1")
            print(limit_sell_order_status_on_spot)
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
            spot_cross_or_isolated_margin="spot"
            all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                         spot_cross_or_isolated_margin,
                                                                                         exchange_object_where_api_is_required)
            print("all_orders_on_spot_account")
            pprint.pprint(all_orders_on_spot_account)

            limit_sell_order_status_on_spot = get_order_status_from_list_of_dictionaries_with_all_orders(
                all_orders_on_spot_account, order_id)

            print("limit_sell_order_status_on_spot2")
            print(limit_sell_order_status_on_spot)



            if limit_sell_order_status_on_spot == "closed" or\
                    limit_sell_order_status_on_spot == "closed".upper() or\
                    limit_sell_order_status_on_spot == "FILLED":
                # place take profit right away as soon as limit order has been fulfilled
                limit_buy_order_tp_order_id=""
                if type_of_tp == "limit":
                    limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                        trading_pair, amount_of_tp, price_of_tp, params=params)
                    print("limit_buy_order_tp has been placed but not yet filled")
                    limit_buy_order_tp_order_id=get_order_id(limit_buy_order_tp)

                # keep looking at the price and wait till either sl or tp has been reached. At the same time look for tp to get filled
                while True:

                    #keep looking if limit take profit has been filled
                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_account, limit_buy_order_tp_order_id)
                    # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                    #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                    if limit_buy_order_tp_order_status=="FILLED":
                        print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                        #stop looking at the price to place stop loss because take profit has been filled
                        break
                    else:
                        print(f"take profit order with id = {limit_buy_order_tp_order_id} has "
                              f"status {limit_buy_order_tp_order_status} and not yet filled. I'll keep waiting")


                    current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                    print(f"waiting for the price to reach either tp={price_of_tp} or sl={price_of_sl}")
                    print(f"current_price_of_trading_pair {trading_pair} is {current_price_of_trading_pair}")
                    # take profit has been reached
                    if current_price_of_trading_pair <= price_of_tp:


                        if type_of_tp == "market":
                            market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_tp, params=params)
                            print("market_buy_order_tp has been placed")
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
                            if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
                                exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,trading_pair,params=params)
                                print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                            break
                        elif type_of_sl == "market":
                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_sl, params=params)
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
                            if limit_buy_order_tp_order_status!= "CANCELED" and limit_buy_order_tp_order_status!= "CANCELLED":
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

                # stop waiting for the order to be filled because it has been already filled
                break

            elif limit_sell_order_status_on_spot in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                print(
                    f"{order_id} order has been {limit_sell_order_status_on_spot} so i will no longer wait for tp or sp to be achieved")
                break
            else:
                # keep waiting for the order to fill
                print(
                    f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_spot}")
                time.sleep(1)
                continue


    else:
        print(f"unknown {side_of_stop_market_order} value")
def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_cross_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)

    if side_of_stop_market_order == "buy":
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
        exchange_object_where_api_is_required.load_markets()

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value = None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

            print(
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            print(min_quantity)
        except:
            traceback.print_exc()

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
                                                                                               price_of_stop_market_order,
                                                                                               params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
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
            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

            limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

                    # keep looking if limit take profit has been filled
                    spot_cross_or_isolated_margin = "cross"
                    all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)

                    limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
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
                            market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_tp, params=params)
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
                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                trading_pair, amount_of_sl, params=params)
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



    elif side_of_stop_market_order == "sell":
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
            exchange_object_where_api_is_required.load_markets()

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]
            try:
                # Get the minimum notional value for the symbol
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']

                print("min_notional_value in USD")
                print(min_notional_value)

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print(
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print(min_quantity)
            except:
                traceback.print_exc()

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
                                                                                                 price_of_stop_market_order,
                                                                                                 params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
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


            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

            limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

                    # keep looking if limit take profit has been filled
                    spot_cross_or_isolated_margin = "cross"
                    all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
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
                            market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_tp, params=params)
                            print("market_buy_order_tp has been placed")
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
                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_sl, params=params)
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
        print(f"unknown {side_of_stop_market_order} value")

def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required=None
    all_orders_on_isolated_margin_account=""
    order_id=""

    #uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)

    if side_of_stop_market_order=="buy":
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
        exchange_object_where_api_is_required.load_markets()

        # Get the symbol details
        symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

        # Get the minimum notional value for the symbol
        min_notional_value=None
        try:
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']
            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

            print(
                f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
            print(min_quantity)
        except:
            traceback.print_exc()



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
                                                                                             price_of_stop_market_order,
                                                                                             params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit

            print(f"placed buy limit order on {exchange_id}")
            print("limit_buy_order")
            print(limit_buy_order)

            order_id = limit_buy_order['id']
            print("order_id4")
            print(order_id)

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

            limit_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                all_orders_on_isolated_margin_account, order_id)
            print("limit_buy_order_status_on_isolated_margin")
            print(limit_buy_order_status_on_isolated_margin)
            if limit_buy_order_status_on_isolated_margin=="closed" or limit_buy_order_status_on_isolated_margin == "closed".upper() or limit_buy_order_status_on_isolated_margin == "FILLED":
                #keep looking at the price and wait till either sl or tp has been reached
                while True:
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



    elif side_of_stop_market_order=="sell":
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
            exchange_object_where_api_is_required.load_markets()

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            # Get the minimum notional value for the symbol
            min_notional_value = symbol_details['info']['filters'][6]['minNotional']

            print("min_notional_value in USD")
            print(min_notional_value)

            # Calculate the minimum quantity based on the minimum notional value
            min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

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
                                                                                               price_of_stop_market_order,params=params)
            except ccxt.InsufficientFunds:
                traceback.print_exc()
                raise SystemExit
            except ccxt.InvalidOrder as e:
                if "Filter failure: NOTIONAL" in str(e):
                    print("Invalid order: Filter failure: NOTIONAL")
                    print(
                        f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                        f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                        f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                    raise SystemExit
            print(f"placed sell limit order on {exchange_id}")
            print("limit_sell_order")
            print(limit_sell_order)

            order_id=limit_sell_order['id']
            print("order_id4")
            print(order_id)

            limit_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

            limit_sell_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(all_orders_on_isolated_margin_account, order_id)




            print("limit_sell_order_status2")
            print(limit_sell_order_status)

            if limit_sell_order_status == "closed" or limit_sell_order_status == "closed".upper() or limit_sell_order_status == "FILLED":
                # keep looking at the price and wait till either sl or tp has been reached
                while True:

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
                            market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_tp, params=params)
                            print("market_buy_order_tp has been placed")
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
                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_sl, params=params)
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
        print(f"unknown {side_of_stop_market_order} value")


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_cross_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)

    external_while_loop_break_flag = False
    while True:
        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
        if side_of_stop_market_order == "buy":
            print(f"placing buy limit order on {exchange_id}")
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
            cross_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
            # print("cross_margin_balance")
            # print(cross_margin_balance)

            # # show balance on cross margin
            # cross_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_cross_account()  # not uniform, see dir(exchange)
            # print("cross_margin_balance")
            # print(cross_margin_balance)
            # # __________________________

            # Load the valid trading symbols
            exchange_object_where_api_is_required.load_markets()

            # Get the symbol details
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            # Get the minimum notional value for the symbol
            min_notional_value = None
            try:
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                print("min_notional_value in USD")
                print(min_notional_value)

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print(
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print(min_quantity)
            except:
                traceback.print_exc()

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
                margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(trading_pair,
                                                                   exchange_object_without_api,
                                                                   amount_of_asset_for_entry,
                                                                   exchange_object_where_api_is_required, params)
                print("margin_loan_when_quote_currency_is_borrowed")
                print(margin_loan_when_quote_currency_is_borrowed)

                # if borrowed_margin_loan['info']['code'] == 200:
                #     print("borrowed_margin_loan['info']['code'] == 200")
                #     print(borrowed_margin_loan['info']['code'] == 200)


                try:
                    limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
                                                                                                   amount_of_asset_for_entry,
                                                                                                   price_of_stop_market_order,
                                                                                                   params=params)
                    print("created_limit_buy_order")
                except ccxt.InsufficientFunds:
                    print(f"Account on {exchange_id} has insufficient balance for the requested action")
                    traceback.print_exc()

                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    external_while_loop_break_flag = True
                    raise SystemExit
                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit
                except Exception as e:

                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    traceback.print_exc()
                    external_while_loop_break_flag = True
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
                limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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
                    external_while_loop_break_flag = True
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

                limit_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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

                        # keep looking if limit take profit has been filled
                        spot_cross_or_isolated_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)

                        limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                            all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                        # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                        if limit_sell_order_tp_order_status == "FILLED":
                            print(f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)

                            # if repaid_margin_loan['info']['code'] == 200:
                            #     print("repaid_margin_loan['info']['code'] == 200")
                            #     print(repaid_margin_loan['info']['code'] == 200)


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
                                market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                    trading_pair, amount_of_tp, params=params)
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

                                # cancel tp because sl has been hit

                                if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
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
                                        print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                        trading_pair, amount_of_sl, params=params)
                                    # market_sell_order_sl=\
                                    #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                    print("market_sell_order_sl has been placed")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    traceback.print_exc()
                                except Exception as e:
                                    traceback.print_exc()

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
                                #     repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
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
                                print("stop_market_sell_order_sl has been placed")
                                if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)

                                break
                            else:
                                print(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            print("neither sl nor tp has been reached")
                            continue

                    # stop waiting for the order to be filled because it has been already filled
                    break

                elif limit_buy_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(),
                                                                   "cancelled".upper()]:
                    print(
                        f"{order_id} order has been {limit_buy_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")

                    # repay margin loan because the initial limit buy order has been cancelled
                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)

                    # if repaid_margin_loan['info']['code'] == 200:
                    #     print("repaid_margin_loan['info']['code'] == 200")
                    #     print(repaid_margin_loan['info']['code'] == 200)


                    break
                else:
                    # keep waiting for the order to fill
                    print(
                        f"waiting for the order to fill because the status of {order_id} is still {limit_buy_order_status_on_cross_margin}")
                    time.sleep(1)
                    continue



        elif side_of_stop_market_order == "sell":
            print(f"placing sell limit order on {exchange_id}")
            limit_sell_order = None
            limit_sell_order_status_on_cross_margin = ""
            order_id = ""
            params = {'type': 'margin',
                      'isIsolated': False  # Set the margin type to cross
                      }
            min_quantity = None
            min_notional_value=None
            # Get the symbol details


            print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


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
            exchange_object_where_api_is_required.load_markets()
            symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

            try:
                # Get the minimum notional value for the symbol
                min_notional_value = symbol_details['info']['filters'][6]['minNotional']

                print("min_notional_value in USD")
                print(min_notional_value)

                # Calculate the minimum quantity based on the minimum notional value
                min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                print(
                    f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                print(min_quantity)
            except:
                traceback.print_exc()

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
                margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(
                    trading_pair,
                    exchange_object_without_api,
                    amount_of_asset_for_entry,
                    exchange_object_where_api_is_required, params)
                print("margin_loan_when_base_currency_is_borrowed")
                print(margin_loan_when_base_currency_is_borrowed)


                try:
                    limit_sell_order = exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,
                                                                                                     amount_of_asset_for_entry,
                                                                                                     price_of_stop_market_order,
                                                                                                     params=params)
                except ccxt.InsufficientFunds:
                    print(f"Account on {exchange_id} has insufficient balance for the requested action")
                    traceback.print_exc()

                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    external_while_loop_break_flag = True
                    raise SystemExit

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit
                except Exception as e:

                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    traceback.print_exc()
                    external_while_loop_break_flag = True
                    raise SystemExit
                print(f"placed sell limit order on {exchange_id}")
                print("limit_sell_order")
                print(limit_sell_order)

                order_id = limit_sell_order['id']
                print("order_id5")
                print(order_id)

                spot_cross_or_isolated_margin = "cross"
                all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                             spot_cross_or_isolated_margin,
                                                                                             exchange_object_where_api_is_required)


                limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
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
                    external_while_loop_break_flag = True
                    raise SystemExit


            except Exception:
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

                limit_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                    all_orders_on_cross_margin_account, order_id)

                print("limit_sell_order_status_on_cross_margin3")
                print(limit_sell_order_status_on_cross_margin)

                if limit_sell_order_status_on_cross_margin == "closed" or\
                        limit_sell_order_status_on_cross_margin == "closed".upper() or limit_sell_order_status_on_cross_margin == "FILLED":
                    # place take profit right away as soon as limit order has been fulfilled
                    limit_buy_order_tp_order_id = ""
                    if type_of_tp == "limit":
                        limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                            trading_pair, amount_of_tp, price_of_tp, params=params)
                        print("limit_buy_order_tp has been placed but not yet filled")
                        limit_buy_order_tp_order_id = get_order_id(limit_buy_order_tp)
                    # keep looking at the price and wait till either sl or tp has been reached
                    while True:

                        # keep looking if limit take profit has been filled
                        spot_cross_or_cross_margin = "cross"
                        all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                     spot_cross_or_isolated_margin,
                                                                                                     exchange_object_where_api_is_required)
                        limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                            all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                        # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                        #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                        if limit_buy_order_tp_order_status == "FILLED":
                            print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
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
                                market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                    trading_pair, amount_of_tp, params=params)
                                print("market_buy_order_tp has been placed")
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
                                if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                    exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                       trading_pair, params=params)
                                    print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
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
                                        print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                    market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                        trading_pair, amount_of_sl, params=params)
                                    print("market_buy_order_sl has been placed")

                                    # repay margin loan when stop loss is achieved
                                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required,
                                                                                      params)

                                except ccxt.InsufficientFunds:
                                    traceback.print_exc()
                                except Exception as e:
                                    traceback.print_exc()
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

                    # stop waiting for the order to be filled because it has been already filled
                    break

                elif limit_sell_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                    print(
                        f"{order_id} order has been {limit_sell_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                    # repay margin loan because the initial limit buy order has been cancelled
                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                      exchange_object_without_api,
                                                                      amount_of_asset_for_entry,
                                                                      exchange_object_where_api_is_required, params)
                    break
                else:
                    # keep waiting for the order to fill
                    print(
                        f"waiting for the order to fill because the status of {order_id} is still {limit_sell_order_status_on_cross_margin}")
                    time.sleep(1)
                    continue


        else:
            print(f"unknown {side_of_stop_market_order} value")
        if external_while_loop_break_flag == True:
            print("external_while_loop_break_flag = True so while loop is breaking")
            break

def place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account1(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_spot_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)
    external_while_loop_break_flag=False
    while True:
        current_price_of_trading_pair=get_price(exchange_object_without_api, trading_pair)
        if side_of_stop_market_order == "buy":
            if current_price_of_trading_pair<price_of_stop_market_order:
                print(f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:
                print(f"placing buy stop_market_order on {exchange_id}")

                market_buy_order_status_on_spot_margin = ""
                order_id = ""

                # we want to place a buy order with spot margin
                params = {}



                stop_market_buy_order = None
                order_id = ""

                # ---------------------------------------------------------


                # Load the valid trading symbols
                exchange_object_where_api_is_required.load_markets()

                # Get the symbol details
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                # Get the minimum notional value for the symbol
                min_notional_value = None
                try:
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                margin_mode="spot"

                # sys.exit(1)

                # we need current timestamp to get borrow interest since that timestamp to add this interest to the repay ammount
                # current_timestamp_in_milliseconds = get_current_timestamp_in_seconds()

                # ---------------------------------------------------------
                try:

                    # #borrow margin before creating an order. Borrow exactly how much your position is
                    # margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(trading_pair,
                    #                                                    exchange_object_without_api,
                    #                                                    amount_of_asset_for_entry,
                    #                                                    exchange_object_where_api_is_required, params)
                    print("margin_loan_when_quote_currency_is not borrowed because it is spot")
                    # print(margin_loan_when_quote_currency_is_borrowed)

                    # if borrowed_margin_loan['info']['code'] == 200:
                    #     print("borrowed_margin_loan['info']['code'] == 200")
                    #     print(borrowed_margin_loan['info']['code'] == 200)


                    try:
                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_buy_order(trading_pair,
                                                                                                       amount_of_asset_for_entry,
                                                                                                       # price_of_stop_market_order,
                                                                                                       params=params)
                        print("created_stop_market_buy_order")
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                        #                                                   exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit
                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                            #                                               exchange_object_without_api,
                            #                                                   amount_of_asset_for_entry,
                            #                                                   exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed buy stop market order on {exchange_id}")
                    print("stop_market_buy_order")
                    print(stop_market_buy_order)

                    order_id = stop_market_buy_order['id']
                    print("order_id4")
                    print(order_id)

                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    stop_market_buy_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_margin_account, order_id)
                    print("stop_market_buy_order_status_on_spot_margin1")
                    print(stop_market_buy_order_status_on_spot_margin)
                    print("stop_markett_buy_order['status']")
                    print(stop_market_buy_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
                        raise SystemExit

                except:
                    print(str(traceback.format_exc()))
                    raise SystemExit

                # wait till order is filled (that is closed)
                while True:
                    print("waiting for the buy order to get filled")
                    # sapi_get_margin_allorders works only for binance
                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                         spot_cross_or_isolated_margin,
                                                                                                         exchange_object_where_api_is_required)
                    # print("all_orders_on_spot_margin_account1")
                    # pprint.pprint(all_orders_on_spot_margin_account)

                    stop_market_buy_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_margin_account, order_id)
                    print("stop_market_buy_order_status_on_spot_margin")
                    print(stop_market_buy_order_status_on_spot_margin)
                    if stop_market_buy_order_status_on_spot_margin == "closed" or\
                            stop_market_buy_order_status_on_spot_margin == "closed".upper() or\
                            stop_market_buy_order_status_on_spot_margin == "FILLED":

                        # place take profit right away as soon as stop_market order has been fulfilled
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
                                spot_cross_or_isolated_margin = "spot"
                                all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                             spot_cross_or_isolated_margin,
                                                                                                             exchange_object_where_api_is_required)

                                limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_spot_margin_account, limit_sell_order_tp_order_id)
                                # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                                if limit_sell_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                                    # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                    #                                           exchange_object_without_api,
                                    #                                                   amount_of_asset_for_entry,
                                    #                                                   exchange_object_where_api_is_required, params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                    external_while_loop_break_flag = True
                                    #     break
                                    if type_of_tp == "market":
                                        market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
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

                                        # cancel tp because sl has been hit

                                        if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # # repay margin loan when stop loss is achieved
                                            # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                            #                                       exchange_object_without_api,
                                            #                                                   amount_of_asset_for_entry,
                                            #                                                   exchange_object_where_api_is_required,
                                            #                                                   params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
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
                                                print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                                trading_pair, amount_of_sl, params=params)
                                            # market_sell_order_sl=\
                                            #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                            print("market_sell_order_sl has been placed")

                                            # # repay margin loan when stop loss is achieved
                                            # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                            #                                                   exchange_object_without_api,
                                            #                                                   amount_of_asset_for_entry,
                                            #                                                   exchange_object_where_api_is_required,
                                            #                                                   params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()

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
                                        #     repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                        #                                           exchange_object_without_api,
                                        #                                                       amount_of_asset_for_entry,
                                        #                                                       exchange_object_where_api_is_required,
                                        #                                                       params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_sell_order_sl has been placed")
                                        if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # # repay margin loan when stop loss is achieved
                                            # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                            #                                       exchange_object_without_api,
                                            #                                                   amount_of_asset_for_entry,
                                            #                                                   exchange_object_where_api_is_required,
                                            #                                                   params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue

                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_buy_order_status_on_spot_margin in ["canceled", "cancelled", "canceled".upper(),
                                                                       "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_buy_order_status_on_spot_margin} so i will no longer wait for tp or sp to be achieved")

                        # # repay margin loan because the initial stop_market buy order has been cancelled
                        # repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                        #                                                   exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)

                        # if repaid_margin_loan['info']['code'] == 200:
                        #     print("repaid_margin_loan['info']['code'] == 200")
                        #     print(repaid_margin_loan['info']['code'] == 200)

                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_buy_order_status_on_spot_margin}")
                        time.sleep(1)
                        continue



        elif side_of_stop_market_order == "sell":
            if current_price_of_trading_pair>price_of_stop_market_order:
                print(
                    f"current price of {trading_pair} = {current_price_of_trading_pair} and it is > price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:

                print(f"placing sell stop_market_order on {exchange_id}")
                stop_market_sell_order = None
                stop_market_sell_order_status_on_spot_margin = ""
                order_id = ""
                params = {}
                min_quantity = None
                min_notional_value=None
                # Get the symbol details


                print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


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
                exchange_object_where_api_is_required.load_markets()
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                try:
                    # Get the minimum notional value for the symbol
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']

                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                try:
                    # # borrow margin before creating an order. Borrow exactly how much your position is
                    # margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(
                    #     trading_pair,
                    #     exchange_object_without_api,
                    #     amount_of_asset_for_entry,
                    #     exchange_object_where_api_is_required, params)
                    print("margin_loan_when_base_currency_is not _borrowed because it is spot")
                    # print(margin_loan_when_base_currency_is_borrowed)


                    try:
                        stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(trading_pair,
                                                                                                         amount_of_asset_for_entry,
                                                                                                         # price_of_stop_market_order,
                                                                                                         params=params)
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                        #                                                   exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit

                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                            #                                                   exchange_object_without_api,
                            #                                                   amount_of_asset_for_entry,
                            #                                                   exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                        #                                                   exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed sell stop_market order on {exchange_id}")
                    print("stop_market_sell_order")
                    print(stop_market_sell_order)

                    order_id = stop_market_sell_order['id']
                    print("order_id5")
                    print(order_id)

                    spot_cross_or_isolated_margin = "spot"
                    all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)


                    stop_market_sell_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_margin_account, order_id)
                    print("stop_market_sell_order_status_on_spot_margin1")
                    print(stop_market_sell_order_status_on_spot_margin)
                    print("stop_market_sell_order['status']")
                    print(stop_market_sell_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
                        raise SystemExit


                except Exception:
                    print(str(traceback.format_exc()))
                    raise SystemExit

                # wait till order is filled (that is closed)
                while True:
                    print("waiting for the sell order to get filled")
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

                    stop_market_sell_order_status_on_spot_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_spot_margin_account, order_id)

                    print("stop_market_sell_order_status_on_spot_margin3")
                    print(stop_market_sell_order_status_on_spot_margin)

                    if stop_market_sell_order_status_on_spot_margin == "closed" or\
                            stop_market_sell_order_status_on_spot_margin == "closed".upper() or stop_market_sell_order_status_on_spot_margin == "FILLED":
                        # place take profit right away as soon as stop_market order has been fulfilled
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
                                spot_cross_or_isolated_margin = "spot"
                                all_orders_on_spot_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                             spot_cross_or_isolated_margin,
                                                                                                             exchange_object_where_api_is_required)
                                limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_spot_margin_account, limit_buy_order_tp_order_id)
                                # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                                if limit_buy_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                                    # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                    #                                                   exchange_object_without_api,
                                    #                                                   amount_of_asset_for_entry,
                                    #                                                   exchange_object_where_api_is_required, params)
                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                        market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
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
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            # repay margin loan when stop loss is achieved
                                            # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                            #                                                   exchange_object_without_api,
                                            #                                                   amount_of_asset_for_entry,
                                            #                                                   exchange_object_where_api_is_required,
                                            #                                                   params)
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "market":
                                        try:
                                            if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                                exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                                   trading_pair, params=params)
                                                print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                                trading_pair, amount_of_sl, params=params)
                                            print("market_buy_order_sl has been placed")

                                            # repay margin loan when stop loss is achieved
                                            # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                            #                                                   exchange_object_without_api,
                                            #                                                   amount_of_asset_for_entry,
                                            #                                                   exchange_object_where_api_is_required,
                                            #                                                   params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_buy_order_sl has been placed")
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue
                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_sell_order_status_on_spot_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_sell_order_status_on_spot_margin} so i will no longer wait for tp or sp to be achieved")

                        # # repay margin loan because the initial stop_market buy order has been cancelled
                        # repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                        #                                                   exchange_object_without_api,
                        #                                                   amount_of_asset_for_entry,
                        #                                                   exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_sell_order_status_on_spot_margin}")
                        time.sleep(1)
                        continue


        else:
            print(f"unknown {side_of_stop_market_order} value")
        if external_while_loop_break_flag == True:
            print("external_while_loop_break_flag = True so while loop is breaking")
            break
def place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_cross_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)
    external_while_loop_break_flag=False
    while True:
        current_price_of_trading_pair=get_price(exchange_object_without_api, trading_pair)
        if side_of_stop_market_order == "buy":
            if current_price_of_trading_pair<price_of_stop_market_order:
                print(f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:
                print(f"placing buy stop_market_order on {exchange_id}")

                market_buy_order_status_on_cross_margin = ""
                order_id = ""

                # we want to place a buy order with cross margin
                params = {'type': 'margin',
                          'isIsolated': False  # Set the margin type to cross
                          }

                stop_market_buy_order = None
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
                exchange_object_where_api_is_required.load_markets()

                # Get the symbol details
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                # Get the minimum notional value for the symbol
                min_notional_value = None
                try:
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                    margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(trading_pair,
                                                                       exchange_object_without_api,
                                                                       amount_of_asset_for_entry,
                                                                       exchange_object_where_api_is_required, params)
                    print("margin_loan_when_quote_currency_is_borrowed")
                    print(margin_loan_when_quote_currency_is_borrowed)

                    # if borrowed_margin_loan['info']['code'] == 200:
                    #     print("borrowed_margin_loan['info']['code'] == 200")
                    #     print(borrowed_margin_loan['info']['code'] == 200)


                    try:
                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_buy_order(trading_pair,
                                                                                                       amount_of_asset_for_entry,
                                                                                                       # price_of_stop_market_order,
                                                                                                       params=params)
                        print("created_stop_market_buy_order")
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit
                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed buy stop market order on {exchange_id}")
                    print("stop_market_buy_order")
                    print(stop_market_buy_order)

                    order_id = stop_market_buy_order['id']
                    print("order_id4")
                    print(order_id)

                    spot_cross_or_isolated_margin = "cross"
                    all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    stop_market_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_cross_margin_account, order_id)
                    print("stop_market_buy_order_status_on_cross_margin1")
                    print(stop_market_buy_order_status_on_cross_margin)
                    print("stop_markett_buy_order['status']")
                    print(stop_market_buy_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
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

                    stop_market_buy_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_cross_margin_account, order_id)
                    print("stop_market_buy_order_status_on_cross_margin")
                    print(stop_market_buy_order_status_on_cross_margin)
                    if stop_market_buy_order_status_on_cross_margin == "closed" or\
                            stop_market_buy_order_status_on_cross_margin == "closed".upper() or\
                            stop_market_buy_order_status_on_cross_margin == "FILLED":

                        # place take profit right away as soon as stop_market order has been fulfilled
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

                                limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_cross_margin_account, limit_sell_order_tp_order_id)
                                # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                                if limit_sell_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required, params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                    external_while_loop_break_flag = True
                                    #     break
                                    if type_of_tp == "market":
                                        market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
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

                                        # cancel tp because sl has been hit

                                        if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                  exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
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
                                                print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                                trading_pair, amount_of_sl, params=params)
                                            # market_sell_order_sl=\
                                            #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                            print("market_sell_order_sl has been placed")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()

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
                                        #     repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                        #                                           exchange_object_without_api,
                                        #                                                       amount_of_asset_for_entry,
                                        #                                                       exchange_object_where_api_is_required,
                                        #                                                       params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_sell_order_sl has been placed")
                                        if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                  exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue

                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_buy_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(),
                                                                       "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_buy_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")

                        # repay margin loan because the initial stop_market buy order has been cancelled
                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)

                        # if repaid_margin_loan['info']['code'] == 200:
                        #     print("repaid_margin_loan['info']['code'] == 200")
                        #     print(repaid_margin_loan['info']['code'] == 200)

                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_buy_order_status_on_cross_margin}")
                        time.sleep(1)
                        continue



        elif side_of_stop_market_order == "sell":
            if current_price_of_trading_pair>price_of_stop_market_order:
                print(
                    f"current price of {trading_pair} = {current_price_of_trading_pair} and it is > price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:

                print(f"placing sell stop_market_order on {exchange_id}")
                stop_market_sell_order = None
                stop_market_sell_order_status_on_cross_margin = ""
                order_id = ""
                params = {'type': 'margin',
                          'isIsolated': False  # Set the margin type to cross
                          }
                min_quantity = None
                min_notional_value=None
                # Get the symbol details


                print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


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
                exchange_object_where_api_is_required.load_markets()
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                try:
                    # Get the minimum notional value for the symbol
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']

                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                    margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(
                        trading_pair,
                        exchange_object_without_api,
                        amount_of_asset_for_entry,
                        exchange_object_where_api_is_required, params)
                    print("margin_loan_when_base_currency_is_borrowed")
                    print(margin_loan_when_base_currency_is_borrowed)


                    try:
                        stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(trading_pair,
                                                                                                         amount_of_asset_for_entry,
                                                                                                         # price_of_stop_market_order,
                                                                                                         params=params)
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit

                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed sell stop_market order on {exchange_id}")
                    print("stop_market_sell_order")
                    print(stop_market_sell_order)

                    order_id = stop_market_sell_order['id']
                    print("order_id5")
                    print(order_id)

                    spot_cross_or_isolated_margin = "cross"
                    all_orders_on_cross_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)


                    stop_market_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_cross_margin_account, order_id)
                    print("stop_market_sell_order_status_on_cross_margin1")
                    print(stop_market_sell_order_status_on_cross_margin)
                    print("stop_market_sell_order['status']")
                    print(stop_market_sell_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
                        raise SystemExit


                except Exception:
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

                    stop_market_sell_order_status_on_cross_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_cross_margin_account, order_id)

                    print("stop_market_sell_order_status_on_cross_margin3")
                    print(stop_market_sell_order_status_on_cross_margin)

                    if stop_market_sell_order_status_on_cross_margin == "closed" or\
                            stop_market_sell_order_status_on_cross_margin == "closed".upper() or stop_market_sell_order_status_on_cross_margin == "FILLED":
                        # place take profit right away as soon as stop_market order has been fulfilled
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
                                limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_cross_margin_account, limit_buy_order_tp_order_id)
                                # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                                if limit_buy_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required, params)
                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                        market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
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
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "market":
                                        try:
                                            if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                                exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                                   trading_pair, params=params)
                                                print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                                trading_pair, amount_of_sl, params=params)
                                            print("market_buy_order_sl has been placed")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_buy_order_sl has been placed")
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue
                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_sell_order_status_on_cross_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_sell_order_status_on_cross_margin} so i will no longer wait for tp or sp to be achieved")
                        # repay margin loan because the initial stop_market buy order has been cancelled
                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_sell_order_status_on_cross_margin}")
                        time.sleep(1)
                        continue


        else:
            print(f"unknown {side_of_stop_market_order} value")
        if external_while_loop_break_flag == True:
            print("external_while_loop_break_flag = True so while loop is breaking")
            break
def place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_stop_market_order, amount_of_asset_for_entry,side_of_stop_market_order):
    output_file = "output_for_place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required = None
    all_orders_on_isolated_margin_account = ""
    order_id = ""

    # uncomment this when in production and add tab after this line
    # with open(file_path, "a") as file:
    # Retrieve the arguments passed to the script
    print(f"12began writing to {__file__} at {datetime.now()}\n")
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
    # print(side_of_stop_market_order)
    external_while_loop_break_flag=False
    while True:
        current_price_of_trading_pair=get_price(exchange_object_without_api, trading_pair)
        if side_of_stop_market_order == "buy":
            if current_price_of_trading_pair<price_of_stop_market_order:
                print(f"current price of {trading_pair} = {current_price_of_trading_pair} and it is < price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:
                print(f"placing buy stop_market_order on {exchange_id}")

                market_buy_order_status_on_isolated_margin = ""
                order_id = ""

                # we want to place a buy order with isolated margin
                params = {'type': 'margin',
                          'isIsolated': True  # Set the margin type to isolated
                          }

                stop_market_buy_order = None
                order_id = ""

                # ---------------------------------------------------------
                # isolated_margin_balance = exchange_object_where_api_is_required.fetch_balance({'type': 'margin'})
                # print("isolated_margin_balance")
                # print(isolated_margin_balance)

                # # show balance on isolated margin
                # isolated_margin_balance = exchange_object_where_api_is_required.sapi_get_margin_isolated_account()  # not uniform, see dir(exchange)
                # print("isolated_margin_balance")
                # print(isolated_margin_balance)
                # # __________________________

                # Load the valid trading symbols
                exchange_object_where_api_is_required.load_markets()

                # Get the symbol details
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                # Get the minimum notional value for the symbol
                min_notional_value = None
                try:
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']
                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                    margin_loan_when_quote_currency_is_borrowed=borrow_margin_loan_when_quote_currency_is_borrowed(trading_pair,
                                                                       exchange_object_without_api,
                                                                       amount_of_asset_for_entry,
                                                                       exchange_object_where_api_is_required, params)
                    print("margin_loan_when_quote_currency_is_borrowed")
                    print(margin_loan_when_quote_currency_is_borrowed)

                    # if borrowed_margin_loan['info']['code'] == 200:
                    #     print("borrowed_margin_loan['info']['code'] == 200")
                    #     print(borrowed_margin_loan['info']['code'] == 200)


                    try:
                        stop_market_buy_order = exchange_object_where_api_is_required.create_market_buy_order(trading_pair,
                                                                                                       amount_of_asset_for_entry,
                                                                                                       # price_of_stop_market_order,
                                                                                                       params=params)
                        print("created_stop_market_buy_order")
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit
                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed buy stop market order on {exchange_id}")
                    print("stop_market_buy_order")
                    print(stop_market_buy_order)

                    order_id = stop_market_buy_order['id']
                    print("order_id4")
                    print(order_id)

                    spot_cross_or_isolated_margin = "isolated"
                    all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)
                    stop_market_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_isolated_margin_account, order_id)
                    print("stop_market_buy_order_status_on_isolated_margin1")
                    print(stop_market_buy_order_status_on_isolated_margin)
                    print("stop_markett_buy_order['status']")
                    print(stop_market_buy_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
                        raise SystemExit

                except:
                    print(str(traceback.format_exc()))
                    raise SystemExit

                # wait till order is filled (that is closed)
                while True:
                    print("waiting for the buy order to get filled")
                    # sapi_get_margin_allorders works only for binance
                    spot_cross_or_isolated_margin = "isolated"
                    all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                         spot_cross_or_isolated_margin,
                                                                                                         exchange_object_where_api_is_required)
                    # print("all_orders_on_isolated_margin_account1")
                    # pprint.pprint(all_orders_on_isolated_margin_account)

                    stop_market_buy_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_isolated_margin_account, order_id)
                    print("stop_market_buy_order_status_on_isolated_margin")
                    print(stop_market_buy_order_status_on_isolated_margin)
                    if stop_market_buy_order_status_on_isolated_margin == "closed" or\
                            stop_market_buy_order_status_on_isolated_margin == "closed".upper() or\
                            stop_market_buy_order_status_on_isolated_margin == "FILLED":

                        # place take profit right away as soon as stop_market order has been fulfilled
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
                                spot_cross_or_isolated_margin = "isolated"
                                all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                             spot_cross_or_isolated_margin,
                                                                                                             exchange_object_where_api_is_required)

                                limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_isolated_margin_account, limit_sell_order_tp_order_id)
                                # limit_sell_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_sell_order_tp_order_id)
                                if limit_sell_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_sell_order_tp_order_id} has been filled")

                                    repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required, params)

                                    # if repaid_margin_loan['info']['code'] == 200:
                                    #     print("repaid_margin_loan['info']['code'] == 200")
                                    #     print(repaid_margin_loan['info']['code'] == 200)


                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                    external_while_loop_break_flag = True
                                    #     break
                                    if type_of_tp == "market":
                                        market_sell_order_tp = exchange_object_where_api_is_required.create_market_sell_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_sell_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_sell_order_tp has been placed")
                                        external_while_loop_break_flag = True
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

                                        # cancel tp because sl has been hit

                                        if limit_sell_order_tp_order_status!= "CANCELED" and limit_sell_order_tp_order_status!= "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                  exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
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
                                                print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            market_sell_order_sl = exchange_object_where_api_is_required.create_market_sell_order(
                                                trading_pair, amount_of_sl, params=params)
                                            # market_sell_order_sl=\
                                            #     exchange_object_where_api_is_required.create_order( symbol=trading_pair, type="market", side="sell", amount= amount_of_sl, params=params)
                                            print("market_sell_order_sl has been placed")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()

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
                                        #     repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                        #                                           exchange_object_without_api,
                                        #                                                       amount_of_asset_for_entry,
                                        #                                                       exchange_object_where_api_is_required,
                                        #                                                       params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)

                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "sell", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_sell_order_sl has been placed")
                                        if limit_sell_order_tp_order_status!="CANCELED" and limit_sell_order_tp_order_status!="CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_sell_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_sell_order_tp_order_id} has been canceled")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                                  exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                            # if repaid_margin_loan['info']['code'] == 200:
                                            #     print("repaid_margin_loan['info']['code'] == 200")
                                            #     print(repaid_margin_loan['info']['code'] == 200)
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue

                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_buy_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(),
                                                                       "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_buy_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")

                        # repay margin loan because the initial stop_market buy order has been cancelled
                        repay_margin_loan_when_quote_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)

                        # if repaid_margin_loan['info']['code'] == 200:
                        #     print("repaid_margin_loan['info']['code'] == 200")
                        #     print(repaid_margin_loan['info']['code'] == 200)

                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_buy_order_status_on_isolated_margin}")
                        time.sleep(1)
                        continue



        elif side_of_stop_market_order == "sell":
            if current_price_of_trading_pair>price_of_stop_market_order:
                print(
                    f"current price of {trading_pair} = {current_price_of_trading_pair} and it is > price_of_stop_market_order={price_of_stop_market_order}")
                time.sleep(1)
                continue
            else:

                print(f"placing sell stop_market_order on {exchange_id}")
                stop_market_sell_order = None
                stop_market_sell_order_status_on_isolated_margin = ""
                order_id = ""
                params = {'type': 'margin',
                          'isIsolated': True  # Set the margin type to isolated
                          }
                min_quantity = None
                min_notional_value=None
                # Get the symbol details


                print("exchange_object_where_api_is_required=", exchange_object_where_api_is_required)


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
                exchange_object_where_api_is_required.load_markets()
                symbol_details = exchange_object_where_api_is_required.markets[trading_pair]

                try:
                    # Get the minimum notional value for the symbol
                    min_notional_value = symbol_details['info']['filters'][6]['minNotional']

                    print("min_notional_value in USD")
                    print(min_notional_value)

                    # Calculate the minimum quantity based on the minimum notional value
                    min_quantity = float(min_notional_value) / float(price_of_stop_market_order)

                    print(
                        f"min_quantity of {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)}")
                    print(min_quantity)
                except:
                    traceback.print_exc()

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
                    margin_loan_when_base_currency_is_borrowed = borrow_margin_loan_when_base_currency_is_borrowed(
                        trading_pair,
                        exchange_object_without_api,
                        amount_of_asset_for_entry,
                        exchange_object_where_api_is_required, params)
                    print("margin_loan_when_base_currency_is_borrowed")
                    print(margin_loan_when_base_currency_is_borrowed)


                    try:
                        stop_market_sell_order = exchange_object_where_api_is_required.create_market_sell_order(trading_pair,
                                                                                                         amount_of_asset_for_entry,
                                                                                                         # price_of_stop_market_order,
                                                                                                         params=params)
                    except ccxt.InsufficientFunds:
                        print(f"Account on {exchange_id} has insufficient balance for the requested action")
                        traceback.print_exc()

                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        raise SystemExit

                    except ccxt.InvalidOrder as e:
                        if "Filter failure: NOTIONAL" in str(e):
                            print("Invalid order: Filter failure: NOTIONAL")
                            print(
                                f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                                f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                                f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")

                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                              exchange_object_without_api,
                                                                              amount_of_asset_for_entry,
                                                                              exchange_object_where_api_is_required, params)
                            external_while_loop_break_flag = True
                            raise SystemExit
                    except Exception as e:

                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        traceback.print_exc()
                        external_while_loop_break_flag = True
                        raise SystemExit
                    print(f"placed sell stop_market order on {exchange_id}")
                    print("stop_market_sell_order")
                    print(stop_market_sell_order)

                    order_id = stop_market_sell_order['id']
                    print("order_id5")
                    print(order_id)

                    spot_cross_or_isolated_margin = "isolated"
                    all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                 spot_cross_or_isolated_margin,
                                                                                                 exchange_object_where_api_is_required)


                    stop_market_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_isolated_margin_account, order_id)
                    print("stop_market_sell_order_status_on_isolated_margin1")
                    print(stop_market_sell_order_status_on_isolated_margin)
                    print("stop_market_sell_order['status']")
                    print(stop_market_sell_order['status'])

                except ccxt.InvalidOrder as e:
                    if "Filter failure: NOTIONAL" in str(e):
                        print("Invalid order: Filter failure: NOTIONAL")
                        print(
                            f"{amount_of_asset_for_entry} {get_base_of_trading_pair_base_slash_quote_without_exchange_are_argument(trading_pair)} "
                            f"or {amount_of_asset_for_entry * get_price(exchange_object_without_api, trading_pair)} "
                            f"USD amount of your order is too small for entry. The amount should be > {min_notional_value} USD")
                        external_while_loop_break_flag = True
                        raise SystemExit


                except Exception:
                    print(str(traceback.format_exc()))
                    raise SystemExit

                # wait till order is filled (that is closed)
                while True:
                    print("waiting for the sell order to get filled")
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

                    stop_market_sell_order_status_on_isolated_margin = get_order_status_from_list_of_dictionaries_with_all_orders(
                        all_orders_on_isolated_margin_account, order_id)

                    print("stop_market_sell_order_status_on_isolated_margin3")
                    print(stop_market_sell_order_status_on_isolated_margin)

                    if stop_market_sell_order_status_on_isolated_margin == "closed" or\
                            stop_market_sell_order_status_on_isolated_margin == "closed".upper() or stop_market_sell_order_status_on_isolated_margin == "FILLED":
                        # place take profit right away as soon as stop_market order has been fulfilled
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
                                spot_cross_or_isolated_margin = "isolated"
                                all_orders_on_isolated_margin_account = get_all_orders_on_spot_cross_or_isolated_margin(trading_pair,
                                                                                                             spot_cross_or_isolated_margin,
                                                                                                             exchange_object_where_api_is_required)
                                limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders(
                                    all_orders_on_isolated_margin_account, limit_buy_order_tp_order_id)
                                # limit_buy_order_tp_order_status = get_order_status_from_list_of_dictionaries_with_all_orders_sped_up(
                                #     all_orders_on_spot_account, limit_buy_order_tp_order_id)
                                if limit_buy_order_tp_order_status == "FILLED":
                                    print(f"take profit order with order id = {limit_buy_order_tp_order_id} has been filled")
                                    repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                      exchange_object_without_api,
                                                                                      amount_of_asset_for_entry,
                                                                                      exchange_object_where_api_is_required, params)
                                    # stop looking at the price to place stop loss because take profit has been filled
                                    external_while_loop_break_flag = True
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
                                        market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                            trading_pair, amount_of_tp, params=params)
                                        print("market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_tp == "stop":
                                        stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_tp, price_of_tp, params=params)
                                        print("stop_market_buy_order_tp has been placed")
                                        external_while_loop_break_flag = True
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
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "market":
                                        try:
                                            if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                                exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                                   trading_pair, params=params)
                                                print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                                trading_pair, amount_of_sl, params=params)
                                            print("market_buy_order_sl has been placed")

                                            # repay margin loan when stop loss is achieved
                                            repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                                              exchange_object_without_api,
                                                                                              amount_of_asset_for_entry,
                                                                                              exchange_object_where_api_is_required,
                                                                                              params)

                                        except ccxt.InsufficientFunds:
                                            traceback.print_exc()
                                        except Exception as e:
                                            traceback.print_exc()
                                        external_while_loop_break_flag = True
                                        break
                                    elif type_of_sl == "stop":
                                        stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                            trading_pair, "buy", amount_of_sl, price_of_sl, params=params)
                                        print("stop_market_buy_order_sl has been placed")
                                        if limit_buy_order_tp_order_status != "CANCELED" and limit_buy_order_tp_order_status != "CANCELLED":
                                            exchange_object_where_api_is_required.cancel_order(limit_buy_order_tp_order_id,
                                                                                               trading_pair, params=params)
                                            print(f"tp order with id = {limit_buy_order_tp_order_id} has been canceled")
                                        external_while_loop_break_flag = True
                                        break
                                    else:
                                        print(f"there is no order called {type_of_sl}")

                                # neither sl nor tp has been reached
                                else:
                                    time.sleep(1)
                                    print("neither sl nor tp has been reached")
                                    continue
                            except ccxt.RequestTimeout:
                                traceback.print_exc()
                                continue
                        # stop waiting for the order to be filled because it has been already filled
                        external_while_loop_break_flag = True
                        break

                    elif stop_market_sell_order_status_on_isolated_margin in ["canceled", "cancelled", "canceled".upper(), "cancelled".upper()]:
                        print(
                            f"{order_id} order has been {stop_market_sell_order_status_on_isolated_margin} so i will no longer wait for tp or sp to be achieved")
                        # repay margin loan because the initial stop_market buy order has been cancelled
                        repay_margin_loan_when_base_currency_is_borrowed(margin_mode, trading_pair,
                                                                          exchange_object_without_api,
                                                                          amount_of_asset_for_entry,
                                                                          exchange_object_where_api_is_required, params)
                        external_while_loop_break_flag = True
                        break
                    else:
                        # keep waiting for the order to fill
                        print(
                            f"waiting for the order to fill because the status of {order_id} is still {stop_market_sell_order_status_on_isolated_margin}")
                        time.sleep(1)
                        continue


        else:
            print(f"unknown {side_of_stop_market_order} value")
        if external_while_loop_break_flag == True:
            print("external_while_loop_break_flag = True so while loop is breaking")
            break


if __name__=="__main__":
    output_file="place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    with open(output_file, "a") as file:
        # Retrieve the arguments passed to the script
        # print(f"\n1began writing to file at {datetime.now()}\n")
        for arg in sys.argv[1:] :
            print(arg+"\n")
        # print(sys.argv[1])
        # args = sys.argv[1:]  # Exclude the first argument, which is the script filename
        # print(sys.argv)
        # Print the arguments
        # print("Arguments:", args)
        exchange_id = sys.argv[1]
        file.write(exchange_id)

        trading_pair = sys.argv[2]
        price_of_sl = sys.argv[3]
        type_of_sl = sys.argv[4]
        amount_of_sl = sys.argv[5]
        price_of_tp = sys.argv[6]
        type_of_tp = sys.argv[7]
        amount_of_tp = sys.argv[8]
        post_only_for_limit_tp_bool = sys.argv[9]
        price_of_stop_market_order = sys.argv[10]
        amount_of_asset_for_entry_in_base_currency = sys.argv[11]
        side_of_stop_market_order = sys.argv[12]
        spot_cross_or_isolated_margin = sys.argv[13]
        # Print the values
        file.write(f"Exchange ID :{exchange_id}")
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
        # print("Price of stop_market Order:", price_of_stop_market_order)
        # print("Amount of Asset for Entry:", amount_of_asset_for_entry)
        # print("Side of stop_market Order:", side_of_stop_market_order)

        entry_price_is_between_sl_and_tp=\
            check_if_entry_price_is_between_sl_and_tp(price_of_sl, price_of_tp, price_of_stop_market_order, side_of_stop_market_order)
        if entry_price_is_between_sl_and_tp:
            if spot_cross_or_isolated_margin == "spot":
                place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_spot_account1(exchange_id,
                                                                                                  trading_pair,
                                                                                                  price_of_sl, type_of_sl,
                                                                                                  amount_of_sl,
                                                                                                  price_of_tp, type_of_tp,
                                                                                                  amount_of_tp,
                                                                                                  post_only_for_limit_tp_bool,
                                                                                                  price_of_stop_market_order,
                                                                                                  amount_of_asset_for_entry_in_base_currency,
                                                                                                  side_of_stop_market_order)
            elif spot_cross_or_isolated_margin == "cross":
                place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_cross_margin_account1(exchange_id,
                                                                                                                  trading_pair,
                                                                                                                  price_of_sl,
                                                                                                                  type_of_sl,
                                                                                                                  amount_of_sl,
                                                                                                                  price_of_tp,
                                                                                                                  type_of_tp,
                                                                                                                  amount_of_tp,
                                                                                                                  post_only_for_limit_tp_bool,
                                                                                                                  price_of_stop_market_order,
                                                                                                                  amount_of_asset_for_entry_in_base_currency,
                                                                                                                  side_of_stop_market_order)
            elif spot_cross_or_isolated_margin=="isolated":
                place_buy_or_sell_stop_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp_on_isolated_margin_account1(exchange_id,
                                                                                                                  trading_pair,
                                                                                                                  price_of_sl,
                                                                                                                  type_of_sl,
                                                                                                                  amount_of_sl,
                                                                                                                  price_of_tp,
                                                                                                                  type_of_tp,
                                                                                                                  amount_of_tp,
                                                                                                                  post_only_for_limit_tp_bool,
                                                                                                                  price_of_stop_market_order,
                                                                                                                  amount_of_asset_for_entry_in_base_currency,
                                                                                                                  side_of_stop_market_order)
