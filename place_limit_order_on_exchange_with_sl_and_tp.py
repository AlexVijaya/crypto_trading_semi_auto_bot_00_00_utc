import time
import traceback
import sys
import os
from datetime import datetime
# from verify_that_all_pairs_from_df_are_ready_for_bfr import convert_to_necessary_types_values_from_bfr_dataframe
from api_config import api_dict_for_all_exchanges
from create_order_on_crypto_exchange2 import get_exchange_object_when_api_is_used
import ccxt
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6

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
    # print("exchange_id_1")
    # print(exchange_id)
    public_api_key = api_dict_for_all_exchanges[exchange_id]['api_key']
    api_secret = api_dict_for_all_exchanges[exchange_id]['api_secret']
    trading_password = None

    if exchange_id == "kucoin":
        try:
            trading_password = api_dict_for_all_exchanges[exchange_id]['trading_password']
        except:
            traceback.print_exc()

    exchange_object_where_api_is_required = \
        get_exchange_object_with_api_key(exchange_name=exchange_id,
                                         public_api_key=public_api_key
                                         , api_secret=api_secret,
                                         trading_password=trading_password)
    return exchange_object_where_api_is_required
def get_order_id(order):
    return order['id']
def get_order_status(exchange_id,order_id):
    exchange_object_where_api_is_required=get_exchange_object_where_api_is_required(exchange_id)
    # Fetch the order from the exchange
    order = exchange_object_where_api_is_required.fetch_order(order_id)

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


def place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                       trading_pair,
                                                       price_of_sl, type_of_sl, amount_of_sl,
                                                       price_of_tp, type_of_tp, amount_of_tp, post_only_for_limit_tp_bool,
                                                       price_of_limit_order, amount_of_asset_for_entry,side_of_limit_order):
    output_file = "output_for_place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    exchange_object_where_api_is_required=None
    with open(file_path, "a") as file:
        # Retrieve the arguments passed to the script
        file.write(f"12began writing to {__file__} at {datetime.now()}\n")
        try:
            file.write(str(exchange_id))
            file.write("\n")
            exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
        except Exception as e:
            file.write(str(traceback.format_exc()))
        file.write("\n")
        file.write(str(exchange_object_where_api_is_required))
        exchange_object_without_api = get_exchange_object6(exchange_id)
        file.write("\n")
        # file.write(side_of_limit_order)

        if side_of_limit_order=="buy":
            file.write(f"placing buy limit order on {exchange_id}")
            try:
                limit_buy_order=exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,amount_of_asset_for_entry,price_of_limit_order)
            except:
                file.write(str(traceback.format_exc()))
            limit_buy_order_id=get_order_id(limit_buy_order)


            #wait till order is filled (that is closed)
            while True:
                file.write("waiting for the buy order to get filled")
                limit_buy_order_status = get_order_status(exchange_id, limit_buy_order_id)
                print("limit_buy_order_status")
                print(limit_buy_order_status)
                if limit_buy_order_status=="closed":
                    #keep looking at the price and wait till either sl or tp has been reached
                    while True:
                        current_price_of_trading_pair=get_price(exchange_object_without_api,trading_pair)
                        file.write("waiting for the price to reach either tp or sl")

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
            file.write(f"placing sell limit order on {exchange_id}")
            limit_sell_order = None
            try:
                limit_sell_order=exchange_object_where_api_is_required.create_limit_sell_order(trading_pair, amount_of_asset_for_entry,price_of_limit_order)
                file.write(f"placed sell limit order on {exchange_id}")
            except:
                file.write(str(traceback.format_exc()))
            limit_sell_order_id=get_order_id(limit_sell_order)

            # wait till order is filled (that is closed)
            while True:
                file.write("waiting for the sell order to get filled")
                limit_sell_order_status = get_order_status(exchange_id, limit_sell_order_id)
                if limit_sell_order_status == "closed":
                    # keep looking at the price and wait till either sl or tp has been reached
                    while True:
                        file.write("waiting for the price to reach either tp or sl")
                        current_price_of_trading_pair = get_price(exchange_object_without_api, trading_pair)
                        file.write(str(current_price_of_trading_pair))
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

if __name__=="__main__":
    output_file="output_for_place_limit_order_on_exchange_with_sl_and_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    with open(output_file, "a") as file:
        # Retrieve the arguments passed to the script
        # file.write(f"\n1began writing to file at {datetime.now()}\n")
        for arg in sys.argv[1:] :
            file.write(arg+"\n")
        # file.write(sys.argv[1])
        # args = sys.argv[1:]  # Exclude the first argument, which is the script filename
        # file.write(sys.argv)
        # Print the arguments
        # print("Arguments:", args)
        exchange_id=sys.argv[1]
        file.write(exchange_id)

        trading_pair=sys.argv[2]
        price_of_sl=sys.argv[3]
        type_of_sl=sys.argv[4]
        amount_of_sl=sys.argv[5]
        price_of_tp=sys.argv[6]
        type_of_tp=sys.argv[7]
        amount_of_tp=sys.argv[8]
        post_only_for_limit_tp_bool=sys.argv[9]
        price_of_limit_order=sys.argv[10]
        amount_of_asset_for_entry=sys.argv[11]
        side_of_limit_order=sys.argv[12]
        # Print the values
        file.write(f"Exchange ID :{exchange_id}" )


        # file.write("Trading Pair:", trading_pair)
        # file.write("Price of SL:", price_of_sl)
        # file.write("Type of SL:", type_of_sl)
        # file.write("Amount of SL:", amount_of_sl)
        # file.write("Price of TP:", price_of_tp)
        # file.write("Type of TP:", type_of_tp)
        # file.write("Amount of TP:", amount_of_tp)
        # file.write("Post Only for Limit TP (bool):", post_only_for_limit_tp_bool)
        # file.write("Price of Limit Order:", price_of_limit_order)
        # file.write("Amount of Asset for Entry:", amount_of_asset_for_entry)
        # file.write("Side of Limit Order:", side_of_limit_order)
        place_limit_order_with_sl_and_tp_with_constant_tracing_of_price_reaching_sl_or_tp(exchange_id,
                                                                                          trading_pair,
                                                                                          price_of_sl, type_of_sl,
                                                                                          amount_of_sl,
                                                                                          price_of_tp, type_of_tp,
                                                                                          amount_of_tp,
                                                                                          post_only_for_limit_tp_bool,
                                                                                          price_of_limit_order,
                                                                                          amount_of_asset_for_entry,
                                                                                          side_of_limit_order)
