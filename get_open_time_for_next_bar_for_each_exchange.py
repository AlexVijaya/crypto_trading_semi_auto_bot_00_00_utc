import ccxt
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# from fetch_historical_USDT_pairs_for_1D_delete_first_primary_db_and_delete_low_volume_db import remove_values_from_list

def get_bar_open_times():
    # Initialize empty list to store data
    data = []

    # Get list of all available exchanges
    exchanges = ccxt.exchanges

    exclusion_list = ["lbank", "huobi", "okex", "okx", "hitbtc", "mexc", "gate", "binanceusdm",
        "binanceus", "bitfinex", "binancecoinm", "huobijp"]
    exchanges=[value for value in exchanges if value not in exclusion_list]

    # Iterate through each exchange
    for exchange in exchanges:
        try:
            # Initialize the exchange object
            exchange_obj = getattr(ccxt, exchange)()

            # Get the next candle open time for the exchange
            next_bar_time = exchange_obj.milliseconds()

            # Append data to list
            data.append({'exchange': exchange, 'time_when_next_bar_opens': next_bar_time})

        except:
            continue

    # Create DataFrame from data
    df = pd.DataFrame(data)

    # Add a new column for human-readable time
    df['time_when_next_bar_opens_human_readable'] =\
        pd.to_datetime(df['time_when_next_bar_opens'], unit='ms')
    print("df")
    print(df.to_string())
    return df

if __name__=="__main__":
    get_bar_open_times()