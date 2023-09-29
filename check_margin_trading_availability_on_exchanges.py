import traceback
# from fetch_historical_USDT_pairs_for_1D_delete_first_primary_db_and_delete_low_volume_db import remove_values_from_list
import ccxt
from get_info_from_load_markets import get_exchange_object6
def get_margin_availability():
    # Get a list of all available exchanges
    exchanges = ccxt.exchanges

    exclusion_list = ["lbank", "huobi", "okex", "okx", "hitbtc", "mexc", "gate", "binanceusdm",
        "binanceus", "bitfinex", "binancecoinm", "huobijp"]
    exchanges=[value for value in exchanges if value not in exclusion_list]

    # Initialize an empty dictionary to store the margin availability
    margin_availability = {}

    # Loop through each exchange
    for exchange_name in exchanges:
        try:
            # Create an exchange object
            exchange = get_exchange_object6(exchange_name)

            # Check if the exchange supports spot trading
            spot_available = 'spot' in exchange.has

            # Check if the exchange supports cross margin trading
            cross_margin_available = (
                exchange.has['margin'] if 'margin' in exchange.has else False
            )

            # Check if the exchange supports isolated margin trading
            isolated_margin_available = (
                exchange.has['isolated'] if cross_margin_available else False
            )

            # Add the margin availability to the dictionary
            margin_availability[exchange_name] = {
                'spot_available': spot_available,
                'cross_margin_available': cross_margin_available,
                'isolated_margin_available': isolated_margin_available
            }


            print(f"margin_availability[{exchange_name}]")
            print(margin_availability[exchange_name])

        except Exception as e:
            # Handle any exceptions or errors that may occur
            print(f"Error checking margin availability for {exchange_name}: {str(e)}")
            traceback.print_exc()

    return margin_availability
if __name__ == "__main__":
    # Example usage:
    margin_availability = get_margin_availability()
    print(margin_availability)