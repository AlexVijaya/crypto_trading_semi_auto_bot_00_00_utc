import traceback

import ccxt
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6
from create_order_on_crypto_exchange2 import create_market_buy_order,\
    create_order,\
    create_market_sell_order,\
    create_limit_sell_order,\
    create_limit_buy_order

def get_price(exchange_object, trading_pair):
    try:
        ticker = exchange_object.fetch_ticker(trading_pair)
        return ticker['last'] # Return the last price of the asset
    except:
        traceback.print_exc()
def place_limit_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_limit_buy_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopLossPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params={}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    limit_buy_order_in_position_flag=False
    limit_sell_order_in_position_flag_place_sl_and_tp_manually=False
    try:
        try:
            create_limit_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_buy_order,params)
            limit_buy_order_in_position_flag = True
        except:

            create_limit_buy_order(exchange_id,trading_pair,amount_of_asset_for_entry,price_of_limit_buy_order,params)
            limit_sell_order_in_position_flag_place_sl_and_tp_manually=True
    except:
        traceback.print_exc()

    if limit_sell_order_in_position_flag_place_sl_and_tp_manually==True:
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

def place_market_buy_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl, amount_of_sl,
                                                      price_of_limit_tp, amount_of_tp,post_only_for_limit_tp_bool,
                                                      price_of_market_buy_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopLossPrice': price_of_market_sl,
    #     },
    #     'takeProfit': {
    #         'type': 'limit',
    #         'takeProfitPrice': price_of_limit_tp,
    #     }
    # }

    params = {}
    exchange_object_without_api = get_exchange_object6(exchange_id)
    isolated_margin_bool=True
    cross_margin_bool=True
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
                params['isCross']='TRUE'
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
                    'stopLossPrice': price_of_market_sl,  # your stop loss price
                }
                market_sell_order_stop_loss = create_market_sell_order(exchange_id, trading_pair, amount_of_sl,
                                                                       price_of_market_sl, params)
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

                params_for_tp = {
                    'takeProfitPrice': price_of_limit_tp  # your take profit price
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

def place_market_buy_order_with_market_sl_and_limit_tp1(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl, amount_of_sl,
                                                      price_of_limit_tp, amount_of_tp,
                                                      price_of_market_buy_order, amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         # 'price': price_of_market_sl,
    #         'stopLossPrice': price_of_market_sl,
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


def place_limit_sell_order_with_market_sl_and_limit_tp(exchange_id,
                                                      trading_pair,
                                                      price_of_market_sl,amount_of_sl,
                                                      price_of_limit_tp,amount_of_tp,
                                                      price_of_limit_sell_order,amount_of_asset_for_entry):
    # params = {
    #     'stopLoss': {
    #         'type': 'market',  # or 'market'
    #         'price': price_of_market_sl,
    #         'stopLossPrice': price_of_market_sl,
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
            'stopLossPrice': price_of_market_sl,
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
            'stopLossPrice': price_of_market_sl,
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
