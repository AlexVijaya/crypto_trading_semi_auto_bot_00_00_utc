import time
import traceback
import sys
import os
from datetime import datetime
from api_config import api_dict_for_all_exchanges
from create_order_on_crypto_exchange2 import get_exchange_object_when_api_is_used
import ccxt
from create_order_on_crypto_exchange2 import get_exchange_object_with_api_key
from create_order_on_crypto_exchange2 import get_public_api_private_api_and_trading_password
from get_info_from_load_markets import get_exchange_object6
from place_order_sl_and_tp import create_stop_market_order_programmatically
from place_order_sl_and_tp import create_stop_limit_order_programmatically
import toml

def correct_str_to_bool(string_value):
    if string_value == 'False' or string_value == 'false':
        return False
    elif string_value == 'True' or string_value == 'true':
        return True
    else:
        return 'What the fuck to do with your input?'
def convert_to_necessary_types_values_from_bfr_dataframe(stop_loss_is_calculated,
                                                         stop_loss_is_technical,
                                                         price_of_sl,
                                                         amount_of_sl,
                                                         post_only_for_limit_tp_bool,
                                                         price_of_buy_or_sell_market_stop_order,
                                                         amount_of_asset_for_entry):
    stop_loss_is_calculated=correct_str_to_bool(stop_loss_is_calculated)
    stop_loss_is_technical=correct_str_to_bool(stop_loss_is_technical)
    price_of_sl=float(price_of_sl)
    amount_of_sl=float(amount_of_sl)
    post_only_for_limit_tp_bool=correct_str_to_bool(post_only_for_limit_tp_bool)
    price_of_buy_or_sell_market_stop_order=float(price_of_buy_or_sell_market_stop_order)
    amount_of_asset_for_entry=float(amount_of_asset_for_entry)
    return stop_loss_is_calculated,stop_loss_is_technical,price_of_sl,\
        amount_of_sl,post_only_for_limit_tp_bool,\
        price_of_buy_or_sell_market_stop_order,amount_of_asset_for_entry
def get_exchange_object_where_api_is_required(exchange_id):
    # Load the secrets from the toml file
    secrets = toml.load("secrets_with_api_private_and_public_keys_for_exchanges.toml")
    # print("exchange_id_1")
    # print(exchange_id)
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

def place_stop_buy_or_stop_sell_market_order_with_constant_tracing_of_sl_and_tp(
        exchange_id,
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
        side_of_buy_or_sell_market_stop_order):
    output_file = "output_for_place_stop_buy_or_stop_sell_market_order_with_constant_tracing_of_sl_and_tp_func1.txt"
    file_path = os.path.join(os.getcwd(), output_file)

    with open(file_path, "a") as file:
        file.write("\n\n")
        file.write("_"*80)
        file.write(str(datetime.now()))
        file.write(f"\n\ntype of stop loss is technical = {type(stop_loss_is_technical)}")
        file.write(f"\n\nstop loss is technical = {stop_loss_is_technical}")
        file.write(f"\n\ntype of stop loss is calculated = {type(stop_loss_is_calculated)}")
        file.write(f"\n\nstop loss is calculated = {stop_loss_is_calculated}")
        file.write(f"\n\ntype_of_sl = {type_of_sl}")
        file.write(f"\n\ntype_of_tp = {type_of_tp}")
        amount_of_sl = amount_of_asset_for_entry
        amount_of_tp = amount_of_asset_for_entry
        sell_order=price_of_buy_or_sell_market_stop_order
        side_of_market_order=side_of_buy_or_sell_market_stop_order

        if stop_loss_is_calculated:
            file.write("above type_of_sl == 'market'")
            if type_of_sl == 'market':
                file.write("above type_of_tp == 'limit'")
                if type_of_tp == "limit":
                    # price_of_sl = calculated_stop_loss_from_db
                    # type_of_tp = "limit"
                    # price_of_tp = take_profit_size_with_x_to_one
                    price_of_limit_order = sell_order
                    side_of_limit_order = "sell"
                    trigger_price_of_stop_order = sell_order
                    file.write("\ni_am_here_2")
                    # try:
                    file.write("\ni am above create_stop_market_order_programmatically")
                    create_stop_market_order_programmatically(exchange_id,
                                                              trading_pair,
                                                              trigger_price_of_stop_order,
                                                              price_of_sl,
                                                              type_of_sl,
                                                              amount_of_sl,
                                                              price_of_tp,
                                                              type_of_tp,
                                                              amount_of_tp,
                                                              amount_of_asset_for_entry,
                                                              side_of_market_order)
                    # except Exception as e:
                    #     file.write("error")
                        # file.write("\nproblem in place_buy_or_sell_stop_order_with_sl_and_tp.py")
                        # file.write(str(e))
                        # file.write(traceback.format_exc())
        #         if type_of_tp == "market":
        #             # price_of_sl = calculated_stop_loss_from_db
        #             # type_of_tp = "market"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_3")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #     if type_of_sl == 'limit':
        #         # type_of_sl = "limit"
        #         if type_of_tp == "limit":
        #             # price_of_sl = calculated_stop_loss_from_db
        #             # type_of_tp = "limit"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_4")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #
        #         if type_of_tp == "market":
        #             # price_of_sl = calculated_stop_loss_from_db
        #             # type_of_tp = "market"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_5")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        # if stop_loss_is_technical:
        #     file.write(str(type(stop_loss_is_technical)))
        #     file.write("\n\ni_am_here_6\n\n")
        #     if type_of_sl == 'market':
        #         # type_of_sl = "market"
        #         if type_of_tp == "limit":
        #             # price_of_sl = technical_stop_loss_from_db
        #             # type_of_tp = "limit"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_7")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #         if type_of_tp == "market":
        #             # price_of_sl = technical_stop_loss_from_db
        #             # type_of_tp = "market"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_8")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #     if type_of_sl == 'limit':
        #         # type_of_sl = "limit"
        #         if type_of_tp == "limit":
        #             # price_of_sl = technical_stop_loss_from_db
        #             # type_of_tp = "limit"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_9")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #
        #         if type_of_tp == "market":
        #             # price_of_sl = technical_stop_loss_from_db
        #             # type_of_tp = "market"
        #             # price_of_tp = take_profit_size_with_x_to_one
        #             price_of_limit_order = sell_order
        #             side_of_limit_order = "sell"
        #             trigger_price_of_stop_order = sell_order
        #             file.write("\ni_am_here_10")
        #             create_stop_market_order_programmatically(exchange_id,
        #                                                       trading_pair,
        #                                                       trigger_price_of_stop_order,
        #                                                       price_of_sl,
        #                                                       type_of_sl,
        #                                                       amount_of_sl,
        #                                                       price_of_tp,
        #                                                       type_of_tp,
        #                                                       amount_of_tp,
        #                                                       amount_of_asset_for_entry,
        #                                                       side_of_market_order)
        #
        #


if __name__=="__main__":
    output_file = "1output_for_place_buy_or_sell_stop_order_with_sl_and_tp.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    with open(file_path, "a") as file:
        # Retrieve the arguments passed to the script
        # print("sys.argv")
        # print(sys.argv)
        # args = sys.argv[1:]  # Exclude the first argument, which is the script filename
        file.write(f"\n\n3began writing to file output_for_place_buy_or_sell_stop_order_with_sl_and_tp at {datetime.now()}\n")
        try:
            file.write(
                f"\n\n4began writing to file output_for_place_buy_or_sell_stop_order_with_sl_and_tp at {datetime.now()}\n")
            # # Print the arguments
            # print("Arguments:", args)
            exchange_id=sys.argv[1]
            file.write(exchange_id)
            file.write("\n")
            trading_pair=sys.argv[2]
            stop_loss_is_calculated=sys.argv[3]
            stop_loss_is_technical=sys.argv[4]

            file.write("\n")
            file.write(str(type(stop_loss_is_calculated)))
            file.write("\n")
            file.write(stop_loss_is_calculated)
            file.write("\n")
            file.write(str(type(stop_loss_is_technical)))
            file.write("\n")
            file.write(stop_loss_is_technical)

            price_of_sl=sys.argv[5]
            type_of_sl=sys.argv[6]
            amount_of_sl=sys.argv[7]
            price_of_tp=sys.argv[8]
            type_of_tp=sys.argv[9]
            amount_of_tp=sys.argv[10]
            post_only_for_limit_tp_bool=sys.argv[11]
            price_of_buy_or_sell_market_stop_order=sys.argv[12]
            amount_of_asset_for_entry=sys.argv[13]
            side_of_buy_or_sell_market_stop_order=sys.argv[14]
            # file.write(side_of_buy_or_sell_market_stop_order)

            # # Print the values
            # # print("Exchange ID:", exchange_id)
            # # print("Trading Pair:", trading_pair)
            # # print("Price of SL:", price_of_sl)
            # # print("Type of SL:", type_of_sl)
            # # print("Amount of SL:", amount_of_sl)
            # # print("Price of TP:", price_of_tp)
            # # print("Type of TP:", type_of_tp)
            # # print("Amount of TP:", amount_of_tp)
            # # print("Post Only for Limit TP (bool):", post_only_for_limit_tp_bool)
            # # print("price_of_buy_or_sell_market_stop_order:", price_of_buy_or_sell_market_stop_order)
            # # print("Amount of Asset for Entry:", amount_of_asset_for_entry)
            # # print("side_of_buy_or_sell_market_stop_order:", side_of_buy_or_sell_market_stop_order)
            file.write(f"\n I am one line above place_stop_buy_or_stop_sell_market_order_with_constant_tracing_of_sl_and_tp at {datetime.now()}\n")
            #
            #convert back to bool and float after string have been passed via popen
            stop_loss_is_calculated, stop_loss_is_technical, price_of_sl, \
                amount_of_sl, post_only_for_limit_tp_bool, \
                price_of_buy_or_sell_market_stop_order, amount_of_asset_for_entry=\
            convert_to_necessary_types_values_from_bfr_dataframe(stop_loss_is_calculated,
                                                                 stop_loss_is_technical,
                                                                 price_of_sl,
                                                                 amount_of_sl,
                                                                 post_only_for_limit_tp_bool,
                                                                 price_of_buy_or_sell_market_stop_order,
                                                                 amount_of_asset_for_entry)
            file.write("\n\n------------------------------")
            file.write(str(type(stop_loss_is_calculated)))
            file.write("\n")
            file.write(str(stop_loss_is_calculated))
            file.write("\n")
            file.write(str(type(stop_loss_is_technical)))
            file.write("\n")
            file.write(str(stop_loss_is_technical))


            place_stop_buy_or_stop_sell_market_order_with_constant_tracing_of_sl_and_tp(
                exchange_id,
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
                side_of_buy_or_sell_market_stop_order)
        except:
            file.write(str(traceback.format_exc()))
