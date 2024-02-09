import time
import sys
import os
from place_limit_order_on_exchange_with_sl_and_tp_margin_is_available_with_writing_to_output_file import get_exchange_object_where_api_is_required
def write_to_file(file_name, content):
    # Create the full file path by joining the current directory and the file name
    file_path = os.path.join(os.getcwd(), file_name)

    # Open the file in write mode, creating if it doesn't exist
    with open(file_path, 'a') as file:
        # Write the content to the file
        file.write(content)
def print_hello_world(phrase_to_print):
    output_file = "output_of_test_dot_py.txt"
    file_path = os.path.join(os.getcwd(), output_file)
    with open(file_path, "w") as file:
        file.write("\n" + "phrase_to_print1")
        while True:
            # print(f"{phrase_to_print}")
            file.write("\n" + "phrase_to_print")
            file.write("\n" +phrase_to_print)
            time.sleep(1)
def get_current_price_of_asset(exchange_object, symbol):
    ticker = exchange_object.fetch_ticker(symbol)
    last_close = ticker['close']
    return last_close
if __name__=="__main__":
    exchange_id ="mexc3"
    symbol = "SNEK/USDT"
    amount_of_asset_for_entry=6
    # price_of_limit_order=0.0019106
    # price_of_limit_order=0.0019106
    params={}
    exchange_object_where_api_is_required = get_exchange_object_where_api_is_required(exchange_id)
    # limit_buy_order = exchange_object_where_api_is_required.create_limit_buy_order(trading_pair,
    #                                                                                amount_of_asset_for_entry,
    #                                                                                price_of_limit_order,
    #                                                                                params=params)

    # Load available markets
    markets = exchange_object_where_api_is_required.load_markets()

    # Check if the specified symbol exists in the loaded markets
    if symbol in markets:
        # Retrieve the trading rules for the specified symbol
        market_for_symbol = markets[symbol]
        print(f"Trading rules for {symbol}: {market_for_symbol}")

        # Access the "orderTypes" list within the 'info' section of the dictionary
        order_types = market_for_symbol['info']['orderTypes']

        # Search if the word "MARKET" is present in the list
        if 'MARKET' in order_types:
            print("The word 'MARKET' is present in the orderTypes list.")
        else:
            print("The word 'MARKET' is not present in the orderTypes list.")
    else:
        print(f"The trading pair {symbol} is not available on MEXC exchange.")

