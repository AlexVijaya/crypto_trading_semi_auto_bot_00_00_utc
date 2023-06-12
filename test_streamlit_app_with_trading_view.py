import streamlit as st
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import traceback
import asyncio
import numpy as np
import altair as alt
import ccxt
import time
import streamlit.components.v1 as components
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import connect_to_postgres_db_without_deleting_it_first
from get_info_from_load_markets import fetch_entire_ohlcv_without_exchange_name
from get_info_from_load_markets2 import get_exchange_object2
from get_info_from_load_markets import async_fetch_entire_ohlcv_without_exchange_name
from get_info_from_load_markets2 import get_exchange_object2_using_async_ccxt
import plotly.graph_objects as go
from constant_update_of_ohlcv_db_to_plot_later import async_get_list_of_tables_from_db
from constant_update_of_ohlcv_db_to_plot_later import get_async_connection_to_db_without_deleting_it_first

async def fetch_ticker_forever(symbol, exchange_object):
    # you can set enableRateLimit = True to enable the built-in rate limiter
    # this way you request rate will never hit the limit of an exchange
    # the library will throttle your requests to avoid that
    import ccxt.async_support as ccxt

    exchange = exchange_object
    while True:
        print('--------------------------------------------------------------')
        print(exchange.iso8601(exchange.milliseconds()), 'fetching', symbol, 'ticker from', exchange.name)
        # this can be any call instead of fetch_ticker, really
        try:
            ticker = await exchange.fetch_ticker(symbol)
            print(exchange.iso8601(exchange.milliseconds()), 'fetched', symbol, 'ticker from', exchange.name)
            print(ticker)

        except ccxt.RequestTimeout as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            # will retry
        except ccxt.DDoSProtection as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            # will retry
        except ccxt.ExchangeNotAvailable as e:
            print('[' + type(e).__name__ + ']')
            print(str(e.args)[0:200])
            # will retry
        except ccxt.ExchangeError as e:
            print('[' + type(e).__name__ + ']')
            print(str(e)[0:200])
            break  # won't retry




def plot_ohlcv(entire_ohlcv_df, crypto_ticker):

    print(f"entire_ohlcv_df_in_plot for {crypto_ticker}")
    print(entire_ohlcv_df)

    try:
        exchange=""
        try:
            exchange = entire_ohlcv_df.iloc[-1, entire_ohlcv_df.columns.get_loc("exchange")]
        except:
            traceback.print_exc()

        crypto_ticker=entire_ohlcv_df["trading_pair"].iat[0]
        st.subheader(f'{crypto_ticker.split("_on_")[0]} on {exchange} ')
        st.dataframe(entire_ohlcv_df)

        components.html('''<!-- TradingView Widget BEGIN -->
            <div class="tradingview-widget-container">
              <div id="tradingview_60343"></div>
              <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/BTCUSDT/?exchange=GATEIO" rel="noopener" target="_blank"><span class="blue-text">BTCUSDT chart</span></a> by TradingView</div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {
              "autosize": true,
              "symbol": "GATEIO:BTCUSDT",
              "interval": "D",
              "timezone": "Etc/UTC",
              "theme": "light",
              "style": "0",
              "locale": "en",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "withdateranges": true,
              "hide_side_toolbar": false,
              "allow_symbol_change": true,
              "details": true,
              "studies": [
                "STD;PSAR"
              ],
              "container_id": "tradingview_60343"
            }
              );
              </script>
            </div>
            <!-- TradingView Widget END -->''')



    except:
        traceback.print_exc()
    # fig.show()
#
# def get_price(exchange, trading_pair):
#     # Get the websocket instance
#     ws = ccxt.websocket[exchange]()
#     # Subscribe to the ticker
#     ws.subscribe_ticker(trading_pair)
#     # Continuously update the close price
#     while True:
#         # Get the last close price
#         data = ws.fetch_ticker(trading_pair)
#         last_close_price = data['info']['last']
#         print('Current Close Price: ', last_close_price)
#         # Delay before looping again
#         time.sleep(1)
#     # Close the websocket instance
#     ws.close()
#     return last_close_price
@st.cache_resource
def initialize_connection_and_engine(db_where_ohlcv_data_for_stocks_is_stored_0000):

    engine_for_ohlcv_data_for_stocks_0000, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_0000)
    return engine_for_ohlcv_data_for_stocks_0000,connection_to_ohlcv_data_for_stocks

@st.cache_data(ttl=30)
def return_df_from_postgres_sql_table(table_name,_engine_name):
    df_with_resulting_table_of_certain_models = \
        pd.read_sql_query(f'''select * from "{table_name}"''',
                          _engine_name)
    return df_with_resulting_table_of_certain_models

async def generate_tasks_in_async_fetch_entire_ohlcv(trading_pair,list_of_exchange_ids_where_pair_is_traded_on,asset_type):
    exchange_objects_list=[get_exchange_object2_using_async_ccxt(exchange_id) for exchange_id in list_of_exchange_ids_where_pair_is_traded_on ]

    database_name="db_with_trading_pair_statistics"
    conn=await get_async_connection_to_db_without_deleting_it_first(database_name)

    if asset_type=="spot":
        tasks_for_spot = [
            asyncio.create_task(async_fetch_entire_ohlcv_without_exchange_name(exchange_object,trading_pair,'1d',1000))
            for exchange_object in exchange_objects_list
        ]
        resulting_list_of_ohlcv_df = await asyncio.gather(*tasks_for_spot)
        # st.write(resulting_list_of_ohlcv_df)
        return resulting_list_of_ohlcv_df

    if asset_type == "swap":
        tasks_for_swap=[]
        tasks_for_swap_when_colon_removed=[]
        for exchange_object in exchange_objects_list:
            exchange_id=exchange_object.id
            table_where_columns_are_exchanges_and_values_are_available_pairs="available_trading_pairs_for_each_exchange"
            list_of_tickers_from_particular_exchange=await conn.fetch(f'''select {exchange_id} from {table_where_columns_are_exchanges_and_values_are_available_pairs};''')
            list_of_tickers_from_particular_exchange = [row[exchange_id] for row in list_of_tickers_from_particular_exchange]
            # print("list_of_tickers_from_particular_exchange")
            # print(list_of_tickers_from_particular_exchange)
            list_of_tickers_from_particular_exchange=list(set(list_of_tickers_from_particular_exchange))

            trading_pair_without_colon=trading_pair.split(":")[0]
            tasks_for_swap_when_colon_removed.append(asyncio.create_task(
                async_fetch_entire_ohlcv_without_exchange_name(exchange_object, trading_pair_without_colon, '1d', 1000)))


            if trading_pair not in list_of_tickers_from_particular_exchange:
                print(f'{trading_pair} is not in {list_of_tickers_from_particular_exchange}')
                continue
            tasks_for_swap.append(asyncio.create_task(
                    async_fetch_entire_ohlcv_without_exchange_name(exchange_object, trading_pair, '1d', 1000)))
        # trading_pair=trading_pair.split(":")[0]
        # tasks_for_spot=[
        #     asyncio.create_task(
        #         async_fetch_entire_ohlcv_without_exchange_name(exchange_object, trading_pair, '1d', 1000))
        #     for exchange_object in exchange_objects_list
        # ]
        #
        tasks_for_swap_and_when_colon_removed=tasks_for_swap+tasks_for_swap_when_colon_removed
        resulting_list_of_ohlcv_df = await asyncio.gather(*tasks_for_swap_and_when_colon_removed)
        # # st.write(resulting_list_of_ohlcv_df)
        return resulting_list_of_ohlcv_df


def generate_html_of_tv_widget_to_insert_into_streamlit(height,width, exchange_name,trading_pair,asset_type):
    if "/" in trading_pair:
        trading_pair=trading_pair.replace("/","")
    if exchange_name=="gate":
        exchange_name="gateio"
    if asset_type=="swap":
        trading_pair=trading_pair.split(":")[0]
        trading_pair=trading_pair+".P"

    st.write("trading_pair_in_func=",trading_pair)
    st.write("exchange_name_in_func=", exchange_name)
    html_of_trading_view_widget = f'''<!-- TradingView Widget BEGIN -->
                <div class="tradingview-widget-container">
                  <div id="tradingview_958b0"></div>
                  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/{trading_pair.upper()}/?exchange={exchange_name.upper()}" rel="noopener" target="_blank"><span class="blue-text">{trading_pair.upper()} chart</span></a> by TradingView</div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget(
                  {{
                  "width": {width},
                  "height": {height},
                  "symbol": "{exchange_name.upper()}:{trading_pair.upper()}",
                  "timezone": "Etc/UTC",
                  "theme": "light",
                  "style": "0",
                  "locale": "en",
                  "toolbar_bg": "#f1f3f6",
                  "enable_publishing": true,
                  "withdateranges": true,
                  "range": "YTD",
                  "hide_side_toolbar": false,
                  "allow_symbol_change": true,
                  "details": true,
                  "hotlist": true,
                  "calendar": true,
                  "studies": [
                    "STD;PSAR"
                  ],
                  "show_popup_button": true,
                  "popup_width": "{width}",
                  "popup_height": "{height}",
                  "container_id": "tradingview_958b0"
                }}
                  );
                  </script>
                </div>
                <!-- TradingView Widget END -->'''

    return html_of_trading_view_widget
# @st.exception
def streamlit_func():

    st.set_page_config(
        page_title="Screen shitcoins and stocks for breakouts, false breakouts and rebounds",
        page_icon="✅",
        layout="wide",
    )

    st.header("Screen shitcoins and stocks for breakouts, false breakouts and rebounds")




    db_where_ohlcv_data_for_stocks_is_stored_0000 = "ohlcv_1d_data_for_usdt_pairs_0000"
    engine_for_ohlcv_data_for_stocks_0000, \
        connection_to_ohlcv_data_for_stocks = \
        initialize_connection_and_engine(db_where_ohlcv_data_for_stocks_is_stored_0000)

    db_where_levels_formed_by_highs_and_lows_for_cryptos_0000="levels_formed_by_highs_and_lows_for_cryptos_0000"
    engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000, \
        connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000 = \
        initialize_connection_and_engine(db_where_levels_formed_by_highs_and_lows_for_cryptos_0000)


    model=st.selectbox("What is your model?",["Breakout of ATL with position entry next day after breakout",
                                        "Breakout of ATH with position entry next day after breakout",
                                        "Breakout of ATL with position entry on second day after breakout",
                                        "Breakout of ATH with position entry on second day after breakout",
                                        "False Breakout of ATL by one bar",
                                        "False Breakout of ATH by one bar",
                                        "False Breakout of ATL by two bars",
                                        "False Breakout of ATH by two bars",
                                        "Complex False Breakout of ATL",
                                        "Complex False Breakout of ATH",
                                        "Rebound off ATL",
                                        "Rebound off ATH",
                                        "New ATL within last two days",
                                        "New ATH within last two days",
                                        "Last close price is closer to ATL than 50%ATR",
                                        "Last close price is closer to ATH than 50%ATR",
                                        "Last close price is closer to ATL than 10% of price",
                                        "Last close price is closer to ATH than 10% of price"
                                        ])

    if model=="New ATL within last two days":
        table_name="current_asset_had_atl_within_two_last_days_period"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)

        df_with_resulting_table_of_certain_models.drop(columns="level_0",inplace=True)
        df_with_resulting_table_of_certain_models.reset_index(inplace=True)


        st.dataframe(df_with_resulting_table_of_certain_models)

        tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        trading_pair=trading_pair_to_select.split("_on_")[0]
        # exchange= df_with_resulting_table_of_certain_models.iloc[-1, df_with_resulting_table_of_certain_models.columns.get_loc("exchange")]


        series_of_exchanges_where_pair_is_traded=\
            df_with_resulting_table_of_certain_models.loc[
                df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select ,
                "exchange_id_string_where_trading_pair_is_traded"]


        row_of_pair_ready_for_model=df_with_resulting_table_of_certain_models.loc[
                df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select ,
                "exchange_id_string_where_trading_pair_is_traded"].index

        exchange = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'exchange']
        atl = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'atl'].iat[0]
        url_of_trading_pair_on_particular_exchange=df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'url_of_trading_pair'].iat[0]
        asset_type = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'asset_type'].iat[0]
        exchanges_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'exchange_id_string_where_trading_pair_is_traded'].iat[0]




        trading_pair = trading_pair.replace("_", "/")
        exchange_name=exchange.iat[0]
        st.write(exchange.iat[0])
        st.write(trading_pair)

        link = f'Click this link if you want to go to {exchange_name} website to see {trading_pair}  [link]({url_of_trading_pair_on_particular_exchange})'
        st.markdown(link, unsafe_allow_html=True)



        string_of_exchanges_where_pair_is_traded=series_of_exchanges_where_pair_is_traded.iat[0]
        st.write(f"{trading_pair} as spot or perpetual swap is traded on the following cryptocurrency exchanges")
        st.write(exchanges_where_pair_is_traded)
        list_of_exchange_ids_where_pair_is_traded_on=string_of_exchanges_where_pair_is_traded.split("_")




        resulting_list_of_ohlcv_dataframes=\
            asyncio.run(generate_tasks_in_async_fetch_entire_ohlcv(trading_pair,list_of_exchange_ids_where_pair_is_traded_on,asset_type))

        for ohlcv_dataframe in resulting_list_of_ohlcv_dataframes:
            print("ohlcv_dataframe_in_loop")
            print(ohlcv_dataframe)
            if ohlcv_dataframe.empty:
                print("The dataframe is empty")
                continue
            # Draw a horizontal line
            st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
            plot_ohlcv(ohlcv_dataframe,trading_pair_to_select)



    if model=="New ATH within last two days":
        table_name="current_asset_had_ath_within_two_last_days_period"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)

        trading_pair = trading_pair_to_select.split("_on_")[0]
        exchange = trading_pair_to_select.split("_on_")[1]
        trading_pair = trading_pair.replace("_", "/")
        st.write(trading_pair_to_select)
        st.write(exchange)
        st.write(trading_pair)

        # exchange_object=get_exchange_object2(exchange)
        # entire_ohlcv_df=fetch_entire_ohlcv_without_exchange_name(exchange_object,trading_pair,'1d',1000)
        # entire_ohlcv_df["Timestamp"] = (entire_ohlcv_df.index)
        #
        # try:
        #     entire_ohlcv_df["open_time"] = entire_ohlcv_df["Timestamp"].apply(
        #         lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
        # except Exception as e:
        #     print("error_message")
        #     traceback.print_exc()
        #
        # entire_ohlcv_df['Timestamp'] = entire_ohlcv_df["Timestamp"] / 1000.0
        #
        # # st.write(entire_ohlcv_df)

    if model=="Breakout of ATL with position entry next day after breakout":

        table_name="current_breakout_situations_of_atl_position_entry_next_day"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        # st.dataframe(df_with_resulting_table_of_certain_models)


        width=1300
        height=600

        st.write(df_with_resulting_table_of_certain_models.columns)
        if "level_0" in df_with_resulting_table_of_certain_models.columns:
            df_with_resulting_table_of_certain_models.drop(columns="level_0", inplace=True)
            df_with_resulting_table_of_certain_models.reset_index(inplace=True)

        st.dataframe(df_with_resulting_table_of_certain_models)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        trading_pair = trading_pair_to_select.split("_on_")[0]
        # exchange= df_with_resulting_table_of_certain_models.iloc[-1, df_with_resulting_table_of_certain_models.columns.get_loc("exchange")]

        series_of_exchanges_where_pair_is_traded = \
            df_with_resulting_table_of_certain_models.loc[
                df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select,
                "exchange_id_string_where_trading_pair_is_traded"]

        row_of_pair_ready_for_model = df_with_resulting_table_of_certain_models.loc[
            df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select,
            "exchange_id_string_where_trading_pair_is_traded"].index

        exchange = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'exchange']
        atl = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'atl'].iat[0]
        url_of_trading_pair_on_particular_exchange = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'url_of_trading_pair'].iat[0]
        asset_type = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'asset_type'].iat[0]
        exchange_ids_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'exchange_id_string_where_trading_pair_is_traded'].iat[0]

        exchange_names_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, "exchange_names_string_where_trading_pair_is_traded"].iat[0]

        trading_pair = trading_pair.replace("_", "/")
        exchange_name = exchange.iat[0]
        st.write(exchange.iat[0])
        st.write(trading_pair)

        link = f'Click this link if you want to go to {exchange_name} website to see {trading_pair}  [link]({url_of_trading_pair_on_particular_exchange})'
        st.markdown(link, unsafe_allow_html=True)

        string_of_exchanges_where_pair_is_traded = series_of_exchanges_where_pair_is_traded.iat[0]
        st.write(f"{trading_pair} as spot or perpetual swap is traded on the following cryptocurrency exchanges")
        st.write(exchange_ids_where_pair_is_traded)
        list_of_exchange_ids_where_pair_is_traded_on = string_of_exchanges_where_pair_is_traded.split("_")
        list_of_exchange_names_where_pair_is_traded_on = exchange_names_where_pair_is_traded.split("_")

        st.write(f"{trading_pair} as spot or perpetual swap is traded on the following cryptocurrency exchanges")
        st.write(list_of_exchange_names_where_pair_is_traded_on)
        st.write("if trading view widget does not load, try to use another browser and/or vpn")

        for exchange_name_in_list in list_of_exchange_names_where_pair_is_traded_on:
            # if exchange_name_in_list!="binance":
                # continue
            if exchange_name_in_list=="gate":
                exchange_name_in_list="gateio"
            st.write(exchange_name_in_list)
            try:


                html_of_trading_view_widget=\
                    generate_html_of_tv_widget_to_insert_into_streamlit(height, width, exchange_name_in_list, trading_pair,asset_type)
                components.html(html_of_trading_view_widget, height=height,width=width)
            except:
                traceback.print_exc()

        # html_of_trading_view_widget=f'''<!-- TradingView Widget BEGIN -->
        #     <div class="tradingview-widget-container">
        #       <div id="tradingview_460eb"></div>
        #       <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/GNSUSDT/?exchange=BINANCE" rel="noopener" target="_blank"><span class="blue-text">GNSUSDT chart</span></a> by TradingView</div>
        #       <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        #       <script type="text/javascript">
        #       new TradingView.widget(
        #       {{
        #       "width": {width},
        #       "height": {height},
        #       "symbol": "BINANCE:GNSUSDT",
        #       "timezone": "Etc/UTC",
        #       "theme": "light",
        #       "style": "0",
        #       "locale": "en",
        #       "toolbar_bg": "#f1f3f6",
        #       "enable_publishing": true,
        #       "withdateranges": true,
        #       "range": "YTD",
        #       "allow_symbol_change": true,
        #       "watchlist": [
        #         "BINANCE:BTCUSDT.P",
        #         "BYBIT:ETHUSDT.P",
        #         "BITSTAMP:BTCUSD"
        #       ],
        #       "details": true,
        #       "hotlist": true,
        #       "calendar": true,
        #       "show_popup_button": true,
        #       "popup_width": "1000",
        #       "popup_height": "650",
        #       "container_id": "tradingview_460eb"
        #     }}
        #       );
        #       </script>
        #     </div>
        #     <!-- TradingView Widget END -->'''
        # components.html(html_of_trading_view_widget,height=height,width=width)

    if model=="Breakout of ATH with position entry next day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_next_day"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="Breakout of ATL with position entry on second day after breakout":
        table_name="current_breakout_situations_of_atl_position_entry_on_day_two"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="Breakout of ATH with position entry on second day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_on_day_two"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="False Breakout of ATL by one bar":
        table_name="current_false_breakout_of_atl_by_one_bar"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="False Breakout of ATH by one bar":
        table_name="current_false_breakout_of_ath_by_one_bar"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="False Breakout of ATL by two bars":
        table_name="current_false_breakout_of_atl_by_two_bars"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="False Breakout of ATH by two bars":
        table_name="current_false_breakout_of_ath_by_two_bars"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="Rebound off ATL":
        table_name="current_rebound_situations_from_atl"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="Rebound off ATH":
        table_name="current_rebound_situations_from_ath"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model=="Last close price is closer to ATL than 50%ATR":
        table_name="current_asset_approaches_its_atl_closer_than_n_percent_atr"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)
        
    if model=="Last close price is closer to ATH than 50%ATR":
        table_name="current_asset_approaches_its_ath_closer_than_n_percent_atr"
        df_with_resulting_table_of_certain_models=\
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model == "Last close price is closer to ATL than 10% of price":
        table_name = "current_asset_approaches_its_atl"
        df_with_resulting_table_of_certain_models = \
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)

    if model == "Last close price is closer to ATH than 10% of price":
        table_name = "current_asset_approaches_its_ath"
        df_with_resulting_table_of_certain_models = \
            return_df_from_postgres_sql_table(table_name,
                                              engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
        st.dataframe(df_with_resulting_table_of_certain_models)





if __name__=="__main__":
    streamlit_func()