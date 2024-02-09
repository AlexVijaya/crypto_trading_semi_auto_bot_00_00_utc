import time
import traceback
import os
from datetime import datetime
from api_config import api_dict_for_all_exchanges
from create_order_on_crypto_exchange2 import get_exchange_object_when_api_is_used
import ccxt
# from verify_that_all_pairs_from_df_are_ready_for_bfr import convert_to_necessary_types_values_from_bfr_dataframe
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6
import toml

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


from create_order_on_crypto_exchange2 import create_market_buy_order,\
    create_order,\
    create_market_sell_order,\
    create_limit_sell_order,\
    create_limit_buy_order
def get_order_id(order):
    return order['id']

def convert_trading_pair_with_underscore_and_exchange_into_trading_pair_with_slash(trading_pair_with_underscore_and_exchange):
    trading_pair_with_underscore=trading_pair_with_underscore_and_exchange.split("_on_")[0]
    trading_pair_with_slash=trading_pair_with_underscore.replace("_","/")
    return trading_pair_with_slash
def get_price(exchange_object, trading_pair):
    if "_" in trading_pair:
        trading_pair=convert_trading_pair_with_underscore_and_exchange_into_trading_pair_with_slash(trading_pair)
    try:
        ticker = exchange_object.fetch_ticker(trading_pair)
        return ticker['last'] # Return the last price of the asset
    except:
        traceback.print_exc()
        
        
def place_limit_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_limit_sell_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    limit_sell_order_in_position_flag=False
    limit_sell_order_in_position_flag_place_sl_and_tp_manually=False
    post_only_for_limit_tp_bool=True
    market_buy_order_stop_loss=None
    limit_buy_order_take_profit=None
    limit_sell_order=None
    try:
        try:
            limit_sell_order=create_limit_sell_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_sell_order,params)
            print("func create_limit_sell_order has been executed")
            limit_sell_order_in_position_flag = True

            # set sl and tp
            if limit_sell_order_in_position_flag == True:

                # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                # print("current_price_of_asset")
                # print(current_price_of_asset)
                # if current_price_of_asset >= price_of_limit_tp:

                # sometimes order does not get filled because of some error but we need to place the order anyway
                market_buy_order_stop_loss_in_position = False

                while True:
                    #execute forever until order is placed
                    # for a stop loss order
                    if market_buy_order_stop_loss_in_position == True:
                        break
                    try:
                        params = {
                            'stopPrice': price_of_market_sl,  # your stop loss price
                        }
                        # params = {
                        #     'triggerPrice': price_of_market_sl,  # your stop loss price
                        # }
                        market_buy_order_stop_loss = create_market_buy_order(exchange_id, trading_pair, amount_of_sl,
                                                                               price_of_market_sl, params)
                        print(f"market buy_order_stop_loss was placed at {price_of_market_sl}")
                        print(market_buy_order_stop_loss)
                        market_buy_order_stop_loss_in_position = True
                    except:
                        traceback.print_exc()

                # sometimes order does not get filled because of some error but we need to place the order anyway
                limit_buy_order_take_profit_in_position = False
                while True:
                    # for a take profit order
                    if limit_buy_order_take_profit_in_position == True:
                        break
                    try:

                        # params_for_tp = {
                        #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                        # }
                        params_for_tp = {
                            'triggerPrice': price_of_limit_tp  # your take profit price
                        }
                        if post_only_for_limit_tp_bool == True:
                            params_for_tp['timeInForce'] = 'PO'
                            # params_for_tp = {'timeInForce':'PO',
                            #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                            # }
                        limit_buy_order_take_profit = create_limit_buy_order(exchange_id, trading_pair, amount_of_tp,
                                                                               price_of_limit_tp, params_for_tp)
                        print("limit_buy_order_take_profit has been placed")
                        limit_buy_order_take_profit_in_position = True
                    except:
                        traceback.print_exc()



        except:

            create_limit_sell_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_sell_order,params)
            limit_sell_order_in_position_flag_place_sl_and_tp_manually=True
    except:
        traceback.print_exc()

    if limit_sell_order_in_position_flag_place_sl_and_tp_manually==True:
        while True:
            current_price_of_asset=get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset>=price_of_limit_tp:
                create_limit_buy_order(exchange_id,trading_pair,amount_of_tp,price_of_limit_tp,params)
                break
            if current_price_of_asset<=price_of_market_sl:
                create_market_buy_order(exchange_id,trading_pair,amount_of_sl,price_of_market_sl,params)
                break

    return limit_sell_order, market_buy_order_stop_loss, limit_buy_order_take_profit
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
                                         ,api_secret=api_secret,
                                         trading_password=trading_password)
    return exchange_object_where_api_is_required


def get_order_status(exchange_id,order_id):
    exchange_object_where_api_is_required=get_exchange_object_where_api_is_required(exchange_id)
    # Fetch the order from the exchange
    order = exchange_object_where_api_is_required.fetch_order(order_id)

    # Return the order's status
    return order['status']
def place_stop_limit_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_stop_limit_sell_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    stop_limit_sell_order_in_position_flag=False
    stop_limit_sell_order_in_position_flag_place_sl_and_tp_manually=False
    post_only_for_limit_tp_bool=True
    market_buy_order_stop_loss=None
    limit_buy_order_take_profit=None
    stop_limit_sell_order=None
    try:
        try:
            params_for_stop_limit_sell_order = {
                'stoplossPrice': price_of_stop_limit_sell_order,  # your stop loss price
            }
            stop_limit_sell_order=create_limit_sell_order(
                exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_limit_sell_order,params_for_stop_limit_sell_order)
            print("func stop_limit_sell_order has been executed")
            print(stop_limit_sell_order)
            stop_limit_sell_order_id=get_order_id(stop_limit_sell_order)

            while True:
                order_status=get_order_status(exchange_id, stop_limit_sell_order_id)

                if order_status!='closed' and order_status!='canceled' and order_status!='cancelled':
                    time.sleep(1)
                    print("order_status")
                    print(order_status)
                    continue
                elif order_status=='canceled' or order_status=='cancelled':
                    break
                else:
                    print("order_status")
                    print(order_status)
                    stop_limit_sell_order_in_position_flag = True
                    break


            # set sl and tp
            if stop_limit_sell_order_in_position_flag == True:

                # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                # print("current_price_of_asset")
                # print(current_price_of_asset)
                # if current_price_of_asset >= price_of_limit_tp:

                # sometimes order does not get filled because of some error but we need to place the order anyway
                market_buy_order_stop_loss_in_position = False

                while True:
                    #execute forever until order is placed
                    # for a stop loss order
                    if market_buy_order_stop_loss_in_position == True:
                        break
                    try:
                        params = {
                            'stoplossPrice': price_of_market_sl,  # your stop loss price
                        }
                        # params = {
                        #     'triggerPrice': price_of_market_sl,  # your stop loss price
                        # }
                        market_buy_order_stop_loss = create_market_buy_order(exchange_id, trading_pair, amount_of_sl,
                                                                               price_of_market_sl, params)
                        print(f"market buy_order_stop_loss was placed at {price_of_market_sl}")
                        print(market_buy_order_stop_loss)
                        market_buy_order_stop_loss_in_position = True
                    except:
                        traceback.print_exc()

                # sometimes order does not get filled because of some error but we need to place the order anyway
                limit_buy_order_take_profit_in_position = False
                while True:
                    # for a take profit order
                    if limit_buy_order_take_profit_in_position == True:
                        break
                    try:

                        # params_for_tp = {
                        #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                        # }
                        params_for_tp = {
                            'triggerPrice': price_of_limit_tp  # your take profit price
                        }
                        if post_only_for_limit_tp_bool == True:
                            params_for_tp['timeInForce'] = 'PO'
                            # params_for_tp = {'timeInForce':'PO',
                            #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                            # }
                        limit_buy_order_take_profit = create_limit_buy_order(exchange_id, trading_pair, amount_of_tp,
                                                                               price_of_limit_tp, params_for_tp)
                        print("limit_buy_order_take_profit has been placed")
                        limit_buy_order_take_profit_in_position = True
                    except:
                        traceback.print_exc()



        except:

            create_limit_sell_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_limit_sell_order,params)
            stop_limit_sell_order_in_position_flag_place_sl_and_tp_manually=True
    except:
        traceback.print_exc()

    if stop_limit_sell_order_in_position_flag_place_sl_and_tp_manually==True:
        while True:
            current_price_of_asset=get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset>=price_of_limit_tp:
                create_limit_buy_order(exchange_id,trading_pair,amount_of_tp,price_of_limit_tp,params)
                break
            if current_price_of_asset<=price_of_market_sl:
                create_market_buy_order(exchange_id,trading_pair,amount_of_sl,price_of_market_sl,params)
                break

    return stop_limit_sell_order, market_buy_order_stop_loss, limit_buy_order_take_profit

def place_limit_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_limit_buy_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    limit_buy_order_in_position_flag=False
    limit_buy_order_in_position_flag_place_sl_and_tp_manually=False
    post_only_for_limit_tp_bool=True
    market_sell_order_stop_loss=None
    limit_sell_order_take_profit=None
    limit_buy_order=None
    try:
        try:
            limit_buy_order=create_limit_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_buy_order,params)
            print("func create_limit_buy_order has been executed")
            limit_buy_order_in_position_flag = True

            # set sl and tp
            if limit_buy_order_in_position_flag == True:

                # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                # print("current_price_of_asset")
                # print(current_price_of_asset)
                # if current_price_of_asset >= price_of_limit_tp:

                # sometimes order does not get filled because of some error but we need to place the order anyway
                market_sell_order_stop_loss_in_position = False

                while True:
                    #execute forever until order is placed
                    # for a stop loss order
                    if market_sell_order_stop_loss_in_position == True:
                        break
                    try:
                        params = {
                            'stopPrice': price_of_market_sl,  # your stop loss price
                        }
                        # params = {
                        #     'triggerPrice': price_of_market_sl,  # your stop loss price
                        # }
                        market_sell_order_stop_loss = create_market_sell_order(exchange_id, trading_pair, amount_of_sl,
                                                                               price_of_market_sl, params)
                        print(f"market sell_order_stop_loss was placed at {price_of_market_sl}")
                        print(market_sell_order_stop_loss)
                        market_sell_order_stop_loss_in_position = True
                    except:
                        traceback.print_exc()

                # sometimes order does not get filled because of some error but we need to place the order anyway
                limit_sell_order_take_profit_in_position = False
                while True:
                    # for a take profit order
                    if limit_sell_order_take_profit_in_position == True:
                        break
                    try:

                        # params_for_tp = {
                        #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                        # }
                        params_for_tp = {
                            'triggerPrice': price_of_limit_tp  # your take profit price
                        }
                        if post_only_for_limit_tp_bool == True:
                            params_for_tp['timeInForce'] = 'PO'
                            # params_for_tp = {'timeInForce':'PO',
                            #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                            # }
                        limit_sell_order_take_profit = create_limit_sell_order(exchange_id, trading_pair, amount_of_tp,
                                                                               price_of_limit_tp, params_for_tp)
                        limit_sell_order_take_profit_in_position = True
                    except:
                        traceback.print_exc()



        except:

            create_limit_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_buy_order,params)
            limit_buy_order_in_position_flag_place_sl_and_tp_manually=True
    except:
        traceback.print_exc()

    if limit_buy_order_in_position_flag_place_sl_and_tp_manually==True:
        while True:
            current_price_of_asset=get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset>=price_of_limit_tp:
                create_limit_sell_order(exchange_id,trading_pair,amount_of_tp,price_of_limit_tp,params)
                break
            if current_price_of_asset<=price_of_market_sl:
                create_market_sell_order(exchange_id,trading_pair,amount_of_sl,price_of_market_sl,params)
                break

    return limit_buy_order, market_sell_order_stop_loss, limit_sell_order_take_profit

def place_stop_limit_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_stop_limit_buy_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    stop_limit_buy_order_in_position_flag=False
    stop_limit_buy_order_in_position_flag_place_sl_and_tp_manually=False
    post_only_for_limit_tp_bool=True
    market_sell_order_stop_loss=None
    limit_sell_order_take_profit=None
    stop_limit_buy_order=None
    try:
        try:
            params_for_stop_limit_buy_order = {
                'stopPrice': price_of_stop_limit_buy_order,  # your stop loss price
            }
            stop_limit_buy_order=create_limit_buy_order(
                exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_limit_buy_order,params_for_stop_limit_buy_order)
            print("func create_limit_buy_order has been executed")
            stop_limit_buy_order_id = get_order_id(stop_limit_buy_order)

            while True:
                order_status=get_order_status(exchange_id, stop_limit_buy_order_id)

                if order_status!='closed' and order_status!='canceled' and order_status!='cancelled':
                    time.sleep(1)
                    print("order_status")
                    print(order_status)
                    continue
                elif order_status=='canceled'or order_status=='cancelled':
                    break
                else:
                    print("order_status")
                    print(order_status)
                    stop_limit_buy_order_in_position_flag = True
                    break
            # limit_buy_order_in_position_flag = True

            # set sl and tp
            if stop_limit_buy_order_in_position_flag == True:

                # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                # print("current_price_of_asset")
                # print(current_price_of_asset)
                # if current_price_of_asset >= price_of_limit_tp:

                # sometimes order does not get filled because of some error but we need to place the order anyway
                market_sell_order_stop_loss_in_position = False

                while True:
                    #execute forever until order is placed
                    # for a stop loss order
                    if market_sell_order_stop_loss_in_position == True:
                        break
                    try:
                        params = {
                            'stopPrice': price_of_market_sl,  # your stop loss price
                        }
                        # params = {
                        #     'triggerPrice': price_of_market_sl,  # your stop loss price
                        # }
                        print("params stopPrice")
                        print(params)
                        market_sell_order_stop_loss = create_market_sell_order(exchange_id, trading_pair, amount_of_sl,
                                                                               price_of_market_sl, params)
                        print(f"market sell_order_stop_loss was placed at {price_of_market_sl}")
                        print(market_sell_order_stop_loss)
                        market_sell_order_stop_loss_in_position = True
                    except:
                        traceback.print_exc()

                # sometimes order does not get filled because of some error but we need to place the order anyway
                limit_sell_order_take_profit_in_position = False
                while True:
                    # for a take profit order
                    if limit_sell_order_take_profit_in_position == True:
                        break
                    try:

                        # params_for_tp = {
                        #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                        # }
                        params_for_tp = {
                            'triggerPrice': price_of_limit_tp  # your take profit price
                        }
                        if post_only_for_limit_tp_bool == True:
                            params_for_tp['timeInForce'] = 'PO'
                            # params_for_tp = {'timeInForce':'PO',
                            #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                            # }
                        limit_sell_order_take_profit = create_limit_sell_order(exchange_id, trading_pair, amount_of_tp,
                                                                               price_of_limit_tp, params_for_tp)
                        limit_sell_order_take_profit_in_position = True
                    except:
                        traceback.print_exc()



        except:

            create_limit_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_limit_buy_order,params)
            stop_limit_buy_order_in_position_flag_place_sl_and_tp_manually=True
    except:
        traceback.print_exc()

    if stop_limit_buy_order_in_position_flag_place_sl_and_tp_manually==True:
        while True:
            current_price_of_asset=get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset>=price_of_limit_tp:
                create_limit_sell_order(exchange_id,trading_pair,amount_of_tp,price_of_limit_tp,params)
                break
            if current_price_of_asset<=price_of_market_sl:
                create_market_sell_order(exchange_id,trading_pair,amount_of_sl,price_of_market_sl,params)
                break

    return stop_limit_buy_order, market_sell_order_stop_loss, limit_sell_order_take_profit

def place_market_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl, amount_of_sl,
                                                      price_of_limit_tp, amount_of_tp,post_only_for_limit_tp_bool,
                                                      price_of_market_buy_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params = {}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    isolated_margin_bool=True
    cross_margin_bool=False
    # market_buy_order_in_position_flag = False
    market_buy_order_in_position_flag_place_sl_and_tp_manually = False
    market_buy_order, market_sell_order_stop_loss, limit_sell_order_take_profit="","",""

    #we need to make sure that the order is placed despite any errors
    while True:
        if market_buy_order_in_position_flag_place_sl_and_tp_manually==True:
            break
        try:
            # try:
            #     2/0
            #     # create_market_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_buy_order,
            #     #                        params)
            #     # market_buy_order_in_position_flag = True
            # except:
            if cross_margin_bool==True:

                params['type']='margin'
                # params['isCross']='TRUE'
                params['leverage']=2
                # exchange_object_with_api1=get_exchange_object_when_api_is_used(exchange_id)


            market_buy_order=\
                create_market_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_buy_order,
                                   params)
            market_buy_order_in_position_flag_place_sl_and_tp_manually = True
        except:
            traceback.print_exc()

    if market_buy_order_in_position_flag_place_sl_and_tp_manually == True:

        # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
        # print("current_price_of_asset")
        # print(current_price_of_asset)
        # if current_price_of_asset >= price_of_limit_tp:

        # sometimes order does not get filled because of some error but we need to place the order anyway
        market_sell_order_stop_loss_in_position = False
        
        while True:
            # for a stop loss order
            if market_sell_order_stop_loss_in_position == True:
                break
            try:
                params = {
                    'stopPrice': price_of_market_sl,  # your stop loss price
                }
                # params = {
                #     'triggerPrice': price_of_market_sl,  # your stop loss price
                # }
                market_sell_order_stop_loss = create_market_sell_order(exchange_id, trading_pair, amount_of_sl,
                                                                       price_of_market_sl, params)
                print(f"market sell_order_stop_loss was placed at {price_of_market_sl}")
                print(market_sell_order_stop_loss)
                market_sell_order_stop_loss_in_position = True
            except:
                traceback.print_exc()

        # sometimes order does not get filled because of some error but we need to place the order anyway
        limit_sell_order_take_profit_in_position=False
        while True:
            # for a take profit order
            if limit_sell_order_take_profit_in_position==True:
                break
            try:

                # params_for_tp = {
                #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                # }
                params_for_tp = {
                    'triggerPrice': price_of_limit_tp  # your take profit price
                }
                if post_only_for_limit_tp_bool==True:
                    params_for_tp['timeInForce']='PO'
                    # params_for_tp = {'timeInForce':'PO',
                    #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                    # }
                limit_sell_order_take_profit=create_limit_sell_order(exchange_id, trading_pair, amount_of_tp, price_of_limit_tp, params_for_tp)
                limit_sell_order_take_profit_in_position=True
            except:
                traceback.print_exc()

        # if current_price_of_asset <= price_of_market_sl:

    return market_buy_order,market_sell_order_stop_loss,limit_sell_order_take_profit


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order):
    exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)

    if side_of_limit_order=="buy":
        limit_buy_order=exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,amount_of_asset_for_entry,price_of_limit_order)
        limit_buy_order_id=get_order_id(limit_buy_order)


        #wait till order is filled (that is closed)
        while True:
            limit_buy_order_status = get_order_status(exchange_id, limit_buy_order_id)
            # print("limit_buy_order_status")
            # print(limit_buy_order_status)
            if limit_buy_order_status=="closed":
                #keep looking at the price and wait till either sl or tp has been reached
                while True:
                    current_price_of_trading_pair=get_price(exchange_object_where_api_is_required,trading_pair)


                    #take profit has been reached
                    if current_price_of_trading_pair>=price_of_tp:
                        if type_of_tp=="limit":
                            limit_sell_order_tp=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_tp,price_of_tp)
                            break
                        elif type_of_tp=="market":
                            market_sell_order_tp=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_tp)
                            break
                        elif type_of_tp=="stop":
                            stop_market_sell_order_tp=exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair,"sell",amount_of_tp,price_of_tp)
                            break
                        else:
                            print(f"there is no order called {type_of_tp}")


                    #stop loss has been reached
                    elif current_price_of_trading_pair<=price_of_sl:
                        if type_of_sl=="limit":
                            limit_sell_order_sl=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_sl,price_of_sl)
                            break
                        elif type_of_sl=="market":
                            market_sell_order_sl=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_sl)
                            break
                        elif type_of_sl=="stop":
                            stop_market_order_sl=exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair, "sell", amount_of_sl, price_of_sl)
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

            elif limit_buy_order_status=="canceled" or limit_buy_order_status=="cancelled":
                break
            else:
                #keep waiting for the order to fill
                print("waiting for the order to fill")
                time.sleep(1)
                continue



    elif side_of_limit_order=="sell":
        limit_sell_order=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair, amount_of_asset_for_entry,price_of_limit_order)
        limit_sell_order_id=get_order_id(limit_sell_order)

        # wait till order is filled (that is closed)
        while True:
            limit_sell_order_status = get_order_status(exchange_id, limit_sell_order_id)
            if limit_sell_order_status == "closed":
                # keep looking at the price and wait till either sl or tp has been reached
                while True:
                    current_price_of_trading_pair = get_price(exchange_object_where_api_is_required, trading_pair)

                    # take profit has been reached
                    if current_price_of_trading_pair <= price_of_tp:
                        if type_of_tp == "limit":
                            limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                                trading_pair, amount_of_tp, price_of_tp)
                            break
                        elif type_of_tp == "market":
                            market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_tp)
                            break
                        elif type_of_tp == "stop":
                            stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair, "buy", amount_of_tp, price_of_tp)
                            break
                        else:
                            print(f"there is no order called {type_of_tp}")

                    # stop loss has been reached
                    elif current_price_of_trading_pair >= price_of_sl:
                        if type_of_sl == "limit":
                            limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                trading_pair, amount_of_sl, price_of_sl)
                            break
                        elif type_of_sl == "market":
                            market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                trading_pair, amount_of_sl)
                            break
                        elif type_of_sl == "stop":
                            stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                trading_pair, "buy", amount_of_sl, price_of_sl)
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

            elif limit_sell_order_status=="canceled" or limit_sell_order_status=="cancelled":
                break
            else:
                # keep waiting for the order to fill
                print("waiting for the order to fill")
                time.sleep(1)
                continue


    else:
        print(f"unknown {side_of_limit_order} value")

def place_market_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp,
                                                       amount_of_asset_for_entry,side_of_market_order):
    exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    output_file = "output_for_func_place_market_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)

    with open(file_path, "a") as file:
        if side_of_market_order=="buy":
            market_buy_order=exchange_object_where_api_is_required.create_market_buy_order(trading_pair,amount_of_asset_for_entry)
            market_buy_order_id=get_order_id(market_buy_order)


            #wait till order is filled (that is closed)
            while True:
                market_buy_order_status = get_order_status(exchange_id, market_buy_order_id)
                if market_buy_order_status=="closed":
                    #keep looking at the price and wait till either sl or tp has been reached
                    while True:
                        current_price_of_trading_pair=get_price(exchange_object_where_api_is_required,trading_pair)


                        #take profit has been reached
                        if current_price_of_trading_pair>=price_of_tp:
                            if type_of_tp=="limit":
                                limit_sell_order_tp=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_tp,price_of_tp)
                                break
                            elif type_of_tp=="market":
                                market_sell_order_tp=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_tp)
                                break
                            elif type_of_tp=="stop":
                                stop_market_sell_order_tp=exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair,"sell",amount_of_tp,price_of_tp)
                                break
                            else:
                                file.write(f"there is no order called {type_of_tp}")

                        #stop loss has been reached
                        elif current_price_of_trading_pair<=price_of_sl:
                            if type_of_sl=="limit":
                                limit_sell_order_sl=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair,amount_of_sl,price_of_sl)
                                break
                            elif type_of_sl=="market":
                                market_sell_order_sl=exchange_object_where_api_is_required.create_market_sell_order(trading_pair,amount_of_sl)
                                break
                            elif type_of_sl=="stop":
                                stop_market_order_sl=exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "sell", amount_of_sl, price_of_sl)
                                break
                            else:
                                file.write(f"there is no order called {type_of_sl}")

                        #neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("neither sl nor tp has been reached")
                            continue

                    #stop waiting for the order to be filled because it has been already filled
                    break
                elif market_buy_order_status=="canceled" or market_buy_order_status=="cancelled":
                    break
                else:
                    #keep waiting for the order to fill
                    file.write("waiting for the order to fill")
                    time.sleep(1)
                    continue



        elif side_of_market_order=="sell":
            market_sell_order=exchange_object_where_api_is_required.create_market_sell_order(trading_pair, amount_of_asset_for_entry)
            market_sell_order_id=get_order_id(market_sell_order)
            market_sell_order_status=get_order_status(exchange_id, market_sell_order_id)
            # wait till order is filled (that is closed)
            while True:
                if market_sell_order_status == "closed":
                    # keep looking at the price and wait till either sl or tp has been reached
                    while True:
                        current_price_of_trading_pair = get_price(exchange_object_where_api_is_required, trading_pair)

                        # take profit has been reached
                        if current_price_of_trading_pair <= price_of_tp:
                            if type_of_tp == "limit":
                                limit_buy_order_tp = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_tp, price_of_tp)
                                break
                            elif type_of_tp == "market":
                                market_buy_order_tp = exchange_object_where_api_is_required.create_market_buy_order(
                                    trading_pair, amount_of_tp)
                                break
                            elif type_of_tp == "stop":
                                stop_market_buy_order_tp = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_tp, price_of_tp)
                                break
                            else:
                                file.write(f"there is no order called {type_of_tp}")

                        # stop loss has been reached
                        elif current_price_of_trading_pair >= price_of_sl:
                            if type_of_sl == "limit":
                                limit_buy_order_sl = exchange_object_where_api_is_required.create_limit_buy_order(
                                    trading_pair, amount_of_sl, price_of_sl)
                                break
                            elif type_of_sl == "market":
                                market_buy_order_sl = exchange_object_where_api_is_required.create_market_buy_order(
                                    trading_pair, amount_of_sl)
                                break
                            elif type_of_sl == "stop":
                                stop_market_buy_order_sl = exchange_object_where_api_is_required.create_stop_market_order(
                                    trading_pair, "buy", amount_of_sl, price_of_sl)
                                break
                            else:
                                file.write(f"there is no order called {type_of_sl}")

                        # neither sl nor tp has been reached
                        else:
                            time.sleep(1)
                            file.write("neither sl nor tp has been reached")
                            continue

                    # stop waiting for the order to be filled because it has been already filled
                    break
                else:
                    # keep waiting for the order to fill
                    time.sleep(1)
                    file.write("waiting for the order to get filled")
                    continue


        else:
            file.write(f"unknown {side_of_market_order} value")

def create_stop_market_order_programmatically(exchange_id,
                             trading_pair,
                             trigger_price_of_stop_order,
                             price_of_sl,
                             type_of_sl,
                             amount_of_sl,
                             price_of_tp,
                             type_of_tp,
                             amount_of_tp,
                             amount_of_asset_for_entry,
                             side_of_market_order):

    output_file = "output_for_create_stop_market_order_programmatically_function.txt"
    file_path = os.path.join(os.getcwd(), output_file)


    with open(file_path, "a") as file:
        file.write("\n______________________________\n")
        file.write(str(datetime.now()))
        file.write("i am inside place_order_sl_and_tp.py\n")
        # file.write(exchange_id)
        exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
        exchange_object_without_api = get_exchange_object6(exchange_id)
        while True:
            file.write("\nnow i am going to get the current price of the asset\n")
            #check for the price to reach trigger
            try:
                current_price_of_trading_pair=get_price(exchange_object_without_api,trading_pair)
            except Exception as e:
                file.write(str(e))
            file.write("current_price_of_trading_pair=")
            file.write(str(current_price_of_trading_pair))
            file.write(f"\n Waiting for the current price of {trading_pair} to be <= required price of {trigger_price_of_stop_order}. Current datetime={datetime.now()}\n\n")

            if side_of_market_order=="buy":
                file.write("\ni am hereeee1")
                if isinstance(trigger_price_of_stop_order,str):
                    file.write("\ni am hereeee2")
                    trigger_price_of_stop_order=float(trigger_price_of_stop_order)
                    file.write("\ni am hereeee3")
                    # print("type(trigger_price_of_stop_order)")
                    # print(type(trigger_price_of_stop_order))
                if current_price_of_trading_pair>=trigger_price_of_stop_order:
                    file.write("\ni am hereeee4")

                    place_market_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                                                                       trading_pair,
                                                                                                       price_of_sl, type_of_sl,
                                                                                                       amount_of_sl,
                                                                                                       price_of_tp, type_of_tp,
                                                                                                       amount_of_tp,
                                                                                                       amount_of_asset_for_entry,
                                                                                                     side_of_market_order)
                    file.write("\ni am hereeee5")
                    break
                else:
                    # print("current trigger price of market buy has not been reached")
                    file.write("\ni am hereeee6")
            elif side_of_market_order=="sell":
                file.write("\ni am hereeee7")
                if isinstance(trigger_price_of_stop_order,str):
                    file.write("\ni am hereeee8")
                    trigger_price_of_stop_order=float(trigger_price_of_stop_order)
                    file.write("\ni am hereeee9")
                    # print("type(trigger_price_of_stop_order)")
                    # print(type(trigger_price_of_stop_order))
                if current_price_of_trading_pair <= trigger_price_of_stop_order:
                    file.write("\ni am hereeee10")
                    place_market_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                                                                       trading_pair,
                                                                                                       price_of_sl,
                                                                                                       type_of_sl,
                                                                                                       amount_of_sl,
                                                                                                       price_of_tp,
                                                                                                       type_of_tp,
                                                                                                       amount_of_tp,
                                                                                                       amount_of_asset_for_entry,
                                                                                                       side_of_market_order)
                    file.write("\ni am hereeee11")
                    break
                else:
                    file.write("\ni am hereeee12")
                    # print("current trigger price of market sell has not been reached")

            time.sleep(1)

def create_stop_limit_order_programmatically(exchange_id,
                             trading_pair,
                             trigger_price_of_stop_order,
                             price_of_sl,
                             type_of_sl,
                             amount_of_sl,
                             price_of_tp,
                             type_of_tp,
                             amount_of_tp,
                             amount_of_asset_for_entry,
                             side_of_limit_order,price_of_limit_order):
    exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    post_only_for_limit_tp_bool=False



    while True:
        #check for the price to reach trigger
        current_price_of_trading_pair=get_price(exchange_object_where_api_is_required,trading_pair)
        print("current_price_of_trading_pair")
        print(current_price_of_trading_pair)

        if side_of_limit_order=="buy":
            if current_price_of_trading_pair<=trigger_price_of_stop_order:

                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order)
                break
            else:
                print("current trigger price of limit buy has not been reached")
        elif side_of_limit_order=="sell":
            if current_price_of_trading_pair >= trigger_price_of_stop_order:
                place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order)
                break
            else:
                print("current trigger price of limit sell has not been reached")

        time.sleep(1)



def place_market_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_market_sl, amount_of_sl,
                                                       price_of_limit_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_market_sell_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params = {}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    isolated_margin_bool = True
    cross_margin_bool = False
    # market_buy_order_in_position_flag = False
    market_sell_order_in_position_flag_place_sl_and_tp_manually = False
    market_sell_order, market_buy_order_stop_loss, limit_buy_order_take_profit = "", "", ""

    # we need to make sure that the order is placed despite any errors
    while True:
        if market_sell_order_in_position_flag_place_sl_and_tp_manually == True:
            break
        try:
            # try:
            #     2/0
            #     # create_market_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_buy_order,
            #     #                        params)
            #     # market_buy_order_in_position_flag = True
            # except:
            if cross_margin_bool == True:
                params['type'] = 'margin'
                # params['isCross']='TRUE'
                params['leverage'] = 2
                # exchange_object_with_api1=get_exchange_object_when_api_is_used(exchange_id)

            market_sell_order = \
                create_market_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_sell_order,
                                        params)
            market_sell_order_in_position_flag_place_sl_and_tp_manually = True
        except:
            traceback.print_exc()

    if market_sell_order_in_position_flag_place_sl_and_tp_manually == True:

        # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
        # print("current_price_of_asset")
        # print(current_price_of_asset)
        # if current_price_of_asset >= price_of_limit_tp:

        # sometimes order does not get filled because of some error but we need to place the order anyway
        market_buy_order_stop_loss_in_position = False

        while True:
            # for a stop loss order
            if market_buy_order_stop_loss_in_position == True:
                break
            try:
                params = {
                    'stopPrice': price_of_market_sl,  # your stop loss price
                }
                # params = {
                #     'triggerPrice': price_of_market_sl,  # your stop loss price
                # }
                market_buy_order_stop_loss = create_market_buy_order(exchange_id, trading_pair, amount_of_sl,
                                                                       price_of_market_sl, params)
                market_buy_order_stop_loss_in_position = True
            except:
                traceback.print_exc()

        # sometimes order does not get filled because of some error but we need to place the order anyway
        limit_buy_order_take_profit_in_position = False
        while True:
            # for a take profit order
            if limit_buy_order_take_profit_in_position == True:
                break
            try:

                # params_for_tp = {
                #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                # }
                params_for_tp = {
                    'takeprofitPrice': price_of_limit_tp  # your take profit price
                }
                if post_only_for_limit_tp_bool == True:
                    params_for_tp['timeInForce'] = 'PO'
                    # params_for_tp = {'timeInForce':'PO',
                    #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                    # }
                limit_buy_order_take_profit = create_limit_buy_order(exchange_id, trading_pair, amount_of_tp,
                                                                       price_of_limit_tp, params_for_tp)
                limit_buy_order_take_profit_in_position = True
            except:
                traceback.print_exc()

        # if current_price_of_asset <= price_of_market_sl:

    return market_sell_order, market_buy_order_stop_loss, limit_buy_order_take_profit

def place_market_sell_order_with_market_sl_and_limit_tp_sl_and_tp_attached(exchange_id,
                                                       trading_pair,
                                                       price_of_market_sl, amount_of_sl,
                                                       price_of_limit_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_market_sell_order, amount_of_asset_for_entry):
    type="market"
    side="sell"
    #
    #
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }
    exchange_object_where_api_is_required=get_exchange_object_where_api_is_required(exchange_id)
    market_sell_order = exchange_object_where_api_is_required.create_market_sell_order (trading_pair,amount_of_asset_for_entry)
    limit_buy_order_tp=exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,amount_of_tp,price_of_limit_tp)
    # stop_market_order_buy_sl=exchange_object_where_api_is_required.create_stop_market_order(trading_pair,'buy',amount_of_sl,price_of_market_sl)
    reduce_only_order=exchange_object_where_api_is_required.create_reduce_only_order(trading_pair,'market','buy',amount_of_sl,price_of_market_sl)

    return market_sell_order,reduce_only_order,limit_buy_order_tp


def place_limit_sell_order_with_market_sl_and_limit_tp_1(exchange_id,
                                                       trading_pair,
                                                       price_of_market_sl, amount_of_sl,
                                                       price_of_limit_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_sell_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'limit',  # or 'limit'
    #         # 'price': price_of_limit_sl,
    #         'stopPrice': price_of_limit_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params = {}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    isolated_margin_bool = True
    cross_margin_bool = False
    # limit_buy_order_in_position_flag = False
    limit_sell_order_in_position_flag_place_sl_and_tp_manually = False
    limit_sell_order, limit_buy_order_stop_loss, limit_buy_order_take_profit = "", "", ""
    market_buy_order_stop_loss=None

    # we need to make sure that the order is placed despite any errors
    while True:
        if limit_sell_order_in_position_flag_place_sl_and_tp_manually == True:
            break
        try:
            # try:
            #     2/0
            #     # create_limit_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_limit_buy_order,
            #     #                        params)
            #     # limit_buy_order_in_position_flag = True
            # except:
            if cross_margin_bool == True:
                params['type'] = 'margin'
                # params['isCross']='TRUE'
                params['leverage'] = 2
                # exchange_object_with_api1=get_exchange_object_when_api_is_used(exchange_id)

            limit_sell_order = \
                create_limit_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_limit_sell_order,
                                        params)
            limit_sell_order_in_position_flag_place_sl_and_tp_manually = True
        except:
            traceback.print_exc()

    if limit_sell_order_in_position_flag_place_sl_and_tp_manually == True:

        # current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
        # print("current_price_of_asset")
        # print(current_price_of_asset)
        # if current_price_of_asset >= price_of_limit_tp:

        # sometimes order does not get filled because of some error but we need to place the order anyway
        market_buy_order_stop_loss_in_position = False

        while True:
            # for a stop loss order
            if market_buy_order_stop_loss_in_position == True:
                break
            try:
                params = {
                    'stopPrice': price_of_market_sl,  # your stop loss price
                }
                # params = {
                #     'triggerPrice': price_of_market_sl,  # your stop loss price
                # }
                market_buy_order_stop_loss = create_market_buy_order(exchange_id, trading_pair, amount_of_sl,
                                                                       price_of_market_sl, params)
                market_buy_order_stop_loss_in_position = True
            except:
                traceback.print_exc()

        # sometimes order does not get filled because of some error but we need to place the order anyway
        limit_buy_order_take_profit_in_position = False
        while True:
            # for a take profit order
            if limit_buy_order_take_profit_in_position == True:
                break
            try:

                # params_for_tp = {
                #     'takeProfitPrice': price_of_limit_tp  # your take profit price
                # }
                params_for_tp = {
                    'triggerPrice': price_of_limit_tp  # your take profit price
                }
                if post_only_for_limit_tp_bool == True:
                    params_for_tp['timeInForce'] = 'PO'
                    # params_for_tp = {'timeInForce':'PO',
                    #     'takeProfitPrice': price_of_limit_tp,  # your take profit price
                    # }
                limit_buy_order_take_profit = create_limit_buy_order(exchange_id, trading_pair, amount_of_tp,
                                                                       price_of_limit_tp, params_for_tp)
                limit_buy_order_take_profit_in_position = True
            except:
                traceback.print_exc()

        # if current_price_of_asset <= price_of_market_sl:

    return limit_sell_order, market_buy_order_stop_loss, limit_buy_order_take_profit

def place_market_buy_order_with_market_sl_and_limit_tp1(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl, amount_of_sl,
                                                      price_of_limit_tp, amount_of_tp,
                                                      price_of_market_buy_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params = {}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    market_buy_order_in_position_flag = False
    market_buy_order_in_position_flag_place_sl_and_tp_manually = False
    try:
        try:
            2/0
            # create_market_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_buy_order,
            #                        params)
            # market_buy_order_in_position_flag = True
        except:

            create_market_buy_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_market_buy_order,
                                   params)
            market_buy_order_in_position_flag_place_sl_and_tp_manually = True
    except:
        traceback.print_exc()

    if market_buy_order_in_position_flag_place_sl_and_tp_manually == True:
        while True:
            current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset >= price_of_limit_tp:
                create_limit_sell_order(exchange_id, trading_pair, amount_of_tp, price_of_limit_tp, params)
                break
            if current_price_of_asset <= price_of_market_sl:
                create_market_sell_order(exchange_id, trading_pair, amount_of_sl, price_of_market_sl, params)
                break


def place_limit_sell_order_with_market_sl_and_limit_tp1(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_limit_sell_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         'price': price_of_market_sl,
    #         'stopPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    limit_sell_order_in_position_flag = False
    limit_sell_order_in_position_flag_place_sl_and_tp_manually = False
    try:
        try:
            print("creating conditional limit sell order")
            create_limit_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_limit_sell_order,params)
            limit_sell_order_in_position_flag = True
        except:
            traceback.print_exc()
            print("creating conditional limit sell order _place_sl_and_tp_manually")
            create_limit_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_limit_sell_order,params)
            limit_sell_order_in_position_flag = True
            limit_sell_order_in_position_flag_place_sl_and_tp_manually = True
    except:
        traceback.print_exc()

    if limit_sell_order_in_position_flag_place_sl_and_tp_manually==True:
        while True:
            current_price_of_asset=get_price(exchange_object_without_api, trading_pair)
            print("current_price_of_asset")
            print(current_price_of_asset)
            if current_price_of_asset<=price_of_limit_tp:
                create_limit_buy_order(exchange_id,trading_pair,amount_of_tp,price_of_limit_tp,params)
                break
            if current_price_of_asset>=price_of_market_sl:
                create_market_buy_order(exchange_id,trading_pair,amount_of_sl,price_of_market_sl,params)
                break
def place_stop_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_stop_buy_order,amount_of_asset_for_entry):
    params = {
        'stopLoss': {
            'type': 'market',  # or 'market'
            # 'price': price_of_market_sl,
            'triggerPrice': price_of_market_sl,
        },
        'takeProfit': {
            'type': 'limit',
            'takeProfitPrice': price_of_limit_tp,
        }
    }
    stop_buy_in_position_flag=False
    stop_buy_in_position_flag_place_sl_and_tp_manually=False
    exchange_object_without_api = get_exchange_object6(exchange_id)
    while True:

        current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
        print("current_price_of_asset")
        print(current_price_of_asset)
        if (current_price_of_asset>=price_of_stop_buy_order) and (stop_buy_in_position_flag==False):
            try:
                create_market_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_buy_order,params)
                stop_buy_in_position_flag = True
            except:
                traceback.print_exc()
                create_market_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_stop_buy_order,params)
                stop_buy_in_position_flag = True
                stop_buy_in_position_flag_place_sl_and_tp_manually = True

        if stop_buy_in_position_flag_place_sl_and_tp_manually == True:
            while True:
                current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_asset")
                print(current_price_of_asset)
                if current_price_of_asset >= price_of_limit_tp:
                    create_limit_sell_order(exchange_id, trading_pair, amount_of_tp, price_of_limit_tp,params)
                    break
                if current_price_of_asset <= price_of_market_sl:
                    create_market_sell_order(exchange_id, trading_pair, amount_of_sl, price_of_market_sl,params)
                    break


def place_stop_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_stop_sell_order,amount_of_asset_for_entry):
    params = {
        'stopLoss': {
            'type': 'market',  # or 'market'
            # 'price': price_of_market_sl,
            'triggerPrice': price_of_market_sl,
        },
        'takeProfit': {
            'type': 'limit',
            'takeProfitPrice': price_of_limit_tp,
        }
    }
    stop_sell_in_position_flag = False
    stop_sell_in_position_flag_place_sl_and_tp_manually=False
    exchange_object_without_api = get_exchange_object6(exchange_id)
    while True:

        current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
        print("current_price_of_asset")
        print(current_price_of_asset)
        if (current_price_of_asset <= price_of_stop_sell_order) and (stop_sell_in_position_flag == False):
            try:
                create_market_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_stop_sell_order,params)
            except:
                traceback.print_exc()

                create_market_sell_order(exchange_id, trading_pair, amount_of_asset_for_entry, price_of_stop_sell_order,params)
                stop_sell_in_position_flag = True
                stop_sell_in_position_flag_place_sl_and_tp_manually = True

        if stop_sell_in_position_flag_place_sl_and_tp_manually == True:
            while True:
                current_price_of_asset = get_price(exchange_object_without_api, trading_pair)
                print("current_price_of_asset")
                print(current_price_of_asset)
                if current_price_of_asset <= price_of_limit_tp:
                    create_limit_sell_order(exchange_id, trading_pair, amount_of_tp, price_of_limit_tp,params)
                    break
                if current_price_of_asset >= price_of_market_sl:
                    create_market_sell_order(exchange_id, trading_pair, amount_of_sl, price_of_market_sl,params)
                    break

if __name__=="__main__":
    exchange_id='kucoin'
    trading_pair="BTC/USDT"
    price_of_market_sl=0
    amount_of_sl=0
    price_of_limit_tp=0
    amount_of_tp=0
    price_of_limit_buy_order=25000
    amount_of_asset_for_entry=0
    place_stop_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl, amount_of_sl,
                                                      price_of_limit_tp, amount_of_tp,
                                                      price_of_limit_buy_order, amount_of_asset_for_entry)
