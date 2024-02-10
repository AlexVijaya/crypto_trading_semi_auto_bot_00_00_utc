import random
import threading
import datetime
from sqlalchemy.exc import ProgrammingError
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
import psycopg2
from psycopg2 import errors, errorcodes
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import connect_to_postgres_db_without_deleting_it_first
from get_info_from_load_markets import fetch_entire_ohlcv_without_exchange_name
from get_info_from_load_markets2 import get_exchange_object2
from get_info_from_load_markets import async_fetch_entire_ohlcv_without_exchange_name
from get_info_from_load_markets2 import get_exchange_object2_using_async_ccxt
import plotly.graph_objects as go
from constant_update_of_ohlcv_db_to_plot_later import async_get_list_of_tables_from_db
from constant_update_of_ohlcv_db_to_plot_later import get_async_connection_to_db_without_deleting_it_first
# from test_streamlit_app_with_trading_view import generate_html_of_tv_widget_to_insert_into_streamlit
from async_update_historical_USDT_pairs_for_1D import get_list_of_tables_in_db
from constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db import constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db
import dash
from dash import html
import dash_tvlwc
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_base_of_trading_pair
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import get_quote_of_trading_pair
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.express as px
def add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange):
    plots_per_page = 50
    # Define the total number of plots
    total_plots = len(tuple_of_trading_pairs_with_exchange)
    # Calculate the number of pages
    total_pages = max(1, (total_plots + plots_per_page - 1) // plots_per_page)
    # Get the current page from user input or set a default value
    current_page = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, value=1)
    # Calculate the start and end indices for the current page
    start_index = (current_page - 1) * plots_per_page
    end_index = min(start_index + plots_per_page, total_plots)
    # Display pagination controls
    st.sidebar.write("Page:", current_page, "of", total_pages)
    st.sidebar.write("Plots_per_page:", plots_per_page)
    tuple_of_trading_pairs_with_exchange = tuple_of_trading_pairs_with_exchange[start_index:end_index]
    return tuple_of_trading_pairs_with_exchange
def scroll_to_top():
    """Add a scroll-to-top button to the Streamlit app."""
    st.markdown("""
    <style>
        #scroll-to-top-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            height: 40px;
            width: 40px;
            border-radius: 50%;
            border: none;
            background-color: #007bff;
            color: white;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s, background-color 0.3s;
        }

        #scroll-to-top-button:hover {
            background-color: #0056b3;
        }

        #scroll-to-top-button.active {
            background-color: #e63946;
        }

        #scroll-to-top-button.show {
            opacity: 1;
            visibility: visible;
        }
    </style>

    <button id="scroll-to-top-button" onclick="scrollToTop()" title="Scroll to Top">&#8679;</button>

    <script>
        var scrollButton = document.getElementById("scroll-to-top-button");
        window.addEventListener("scroll", scrollFunction);

        function scrollFunction() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                scrollButton.classList.add("show");
            } else {
                scrollButton.classList.remove("show");
            }
        }

        function scrollToTop() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
    </script>
    """, unsafe_allow_html=True)

def return_list_of_options_for_today_that_are_available_and_not_all_possible_options(engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000):
    list_of_tables_in_db_with_bfr_models = get_list_of_tables_in_db(
        engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000)
    # list_of_all_possible_options_for_choosing_of_different_bfr_models_in_streamlit_app = [
    #     "Breakout of ATL with position entry next day after breakout",
    #     "Breakout of ATH with position entry next day after breakout",
    #     "Breakout of ATL with position entry on second day after breakout",
    #     "Breakout of ATH with position entry on second day after breakout",
    #     "False Breakout of ATL by one bar",
    #     "False Breakout of ATH by one bar",
    #     "False Breakout of ATL by two bars",
    #     "False Breakout of ATH by two bars",
    #     "Complex False Breakout of ATL",
    #     "Complex False Breakout of ATH",
    #     "Rebound off ATL",
    #     "Rebound off ATH",
    #     "New ATL within last two days",
    #     "New ATH within last two days",
    #     "Last close price is closer to ATL than n %ATR",
    #     "Last close price is closer to ATH than n %ATR",
    #     "Last close price is closer to ATL than N % of ATR(30)",
    #     "Last close price is closer to ATH than N % of ATR(30)"
    #     ]
    list_of_options_for_today_that_are_available_and_not_all_possible_options = []

    list_of_all_possible_table_names_in_bfr_db = ["current_asset_had_atl_within_two_last_days_period",
                                                  "current_asset_had_ath_within_two_last_days_period",
                                                  "current_breakout_situations_of_atl_position_entry_next_day",
                                                  "current_breakout_situations_of_ath_position_entry_next_day",
                                                  "current_breakout_situations_of_atl_position_entry_on_day_two",
                                                  "current_breakout_situations_of_ath_position_entry_on_day_two",
                                                  "current_false_breakout_of_atl_by_one_bar",
                                                  "current_false_breakout_of_ath_by_one_bar",
                                                  "current_false_breakout_of_atl_by_two_bars",
                                                  "current_false_breakout_of_ath_by_two_bars",
                                                  "current_rebound_situations_from_atl",
                                                  "current_rebound_situations_from_ath",
                                                  "current_asset_approaches_its_atl_closer_than_n_percent_atr",
                                                  "current_asset_approaches_its_ath_closer_than_n_percent_atr"]

    for table_name in list_of_all_possible_table_names_in_bfr_db:
        if table_name in list_of_tables_in_db_with_bfr_models:
            if table_name == "current_asset_had_atl_within_two_last_days_period":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "New ATL within last two days")
            if table_name == "current_asset_had_ath_within_two_last_days_period":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "New ATH within last two days")
            if table_name == "current_breakout_situations_of_atl_position_entry_next_day":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Breakout of ATL with position entry next day after breakout")
            if table_name == "current_breakout_situations_of_ath_position_entry_next_day":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Breakout of ATH with position entry next day after breakout")
            if table_name == "current_breakout_situations_of_atl_position_entry_on_day_two":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Breakout of ATL with position entry on second day after breakout")
            if table_name == "current_breakout_situations_of_ath_position_entry_on_day_two":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Breakout of ATH with position entry on second day after breakout")
            if table_name == "current_false_breakout_of_atl_by_one_bar":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "False Breakout of ATL by one bar")
            if table_name == "current_false_breakout_of_ath_by_one_bar":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "False Breakout of ATH by one bar")
            if table_name == "current_false_breakout_of_atl_by_two_bars":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "False Breakout of ATL by two bars")
            if table_name == "current_false_breakout_of_ath_by_two_bars":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "False Breakout of ATH by two bars")
            if table_name == "current_rebound_situations_from_atl":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Rebound off ATL")
            if table_name == "current_rebound_situations_from_ath":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Rebound off ATH")
            if table_name == "current_asset_approaches_its_atl_closer_than_n_percent_atr":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Last close price is closer to ATL than n %ATR")
            if table_name == "current_asset_approaches_its_ath_closer_than_n_percent_atr":
                list_of_options_for_today_that_are_available_and_not_all_possible_options.append(
                    "Last close price is closer to ATH than n %ATR")

    return list_of_options_for_today_that_are_available_and_not_all_possible_options
def get_date_with_and_without_time_from_timestamp(timestamp):
    open_time = \
        datetime.datetime.fromtimestamp ( timestamp  )
    # last_timestamp = historical_data_for_crypto_ticker_df["Timestamp"].iloc[-1]
    # last_date_with_time = historical_data_for_crypto_ticker_df["open_time"].iloc[-1]
    # print ( "type(last_date_with_time)\n" , type ( last_date_with_time ) )
    # print ( "last_date_with_time\n" , last_date_with_time )
    date_with_time = open_time.strftime ( "%Y/%m/%d %H:%M:%S" )
    date_without_time = date_with_time.split ( " " )
    print ( "date_with_time\n" , date_without_time[0] )
    date_without_time = date_without_time[0]
    print ( "date_without_time\n" , date_without_time )
    date_without_time = date_without_time.replace ( "/" , "_" )
    date_with_time = date_with_time.replace ( "/" , "_" )
    date_with_time = date_with_time.replace ( " " , "__" )
    date_with_time = date_with_time.replace ( ":" , "_" )
    return date_with_time,date_without_time
def generate_html_of_tv_widget_to_insert_into_streamlit(height, width, exchange_name, trading_pair, asset_type):
    if "/" in trading_pair:
        trading_pair = trading_pair.replace("/", "")
    if exchange_name == "gate":
        exchange_name = "gateio"
    if asset_type == "swap":
        trading_pair = trading_pair.split(":")[0]
        trading_pair = trading_pair + ".P"

    # st.write("trading_pair_in_func=", trading_pair)
    # st.write("exchange_name_in_func=", exchange_name)
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


def add_horizontal_draggable_line(fig,leftmost_x,rightmost_x):
    """Adds a horizontal line to a Plotly figure that can be dragged up and down by clicking and holding.

    Args:
        fig: A Plotly figure object.

    Returns:
        The modified Plotly figure object.
    """
    if fig.layout is None or fig.layout.xaxis is None:
        raise ValueError('The figure does not have a valid layout or x-axis.')

    fig.update_layout(dragmode='pan')  # Set the drag mode to 'pan' to enable dragging

    # Create a new shape object representing the horizontal line
    print( "fig.layout.xaxis")
    print(fig.layout.xaxis)
    line_shape = {
        'type': 'line',
        'x0': leftmost_x,  # Set the line's x-coordinates to the full range of the x-axis
        'y0': 0.5,  # Set the line's y-coordinate to the middle of the y-axis
        'x1': rightmost_x,
        'y1': 0.5,
        'xref': 'x',
        'yref': 'y',
        'line': {
            'color': 'red',
            'width': 2,
        },
        'editable': True,  # Enable editing of the shape (i.e., dragging)
    }

    # Add the line shape to the figure's shapes list
    fig.update_layout(shapes=[line_shape])

    # Define a callback function that adds a horizontal line shape to the figure when the user clicks on the chart
    def add_line_on_click(trace, points, state):
        if len(points.point_inds) == 0:  # Ignore clicks with no points selected
            return

        # Get the x-coordinate of the clicked point (i.e., the timestamp of the candlestick)
        x = trace.x[points.point_inds[0]]

        # Create a new shape object representing the horizontal line
        line_shape = {
            'type': 'line',
            'x0': fig.layout.xaxis.range[0],  # Set the line's x-coordinates to the full range of the x-axis
            'y0': points.y,  # Set the line's y-coordinate to the y-coordinate of the clicked point
            'x1': fig.layout.xaxis.range[1],
            'y1': points.y,
            'xref': 'x',
            'yref': 'y',
            'line': {
                'color': 'red',
                'width': 2,
            },
            'editable': True,  # Enable editing of the shape (i.e., dragging)
        }

        # Add the line shape to the figure's shapes list
        fig.add_shape(line_shape)

    return fig

def add_horizontal_line_on_click(fig,leftmost_x,rightmost_x):
    """Adds a horizontal line to a Plotly candlestick chart when the user clicks on the chart.

    Args:
        fig: A Plotly figure object containing a candlestick trace.

    Returns:
        The modified Plotly figure object.
    """
    # if fig.data is None or len(fig.data) == 0 or fig.data[0].type != 'candlestick':
    #     raise ValueError('The figure does not have a valid candlestick trace.')

    # fig.update_layout(dragmode='pan')  # Set the drag mode to 'pan' to enable panning

    # Define a callback function that adds a horizontal line shape to the figure when the user clicks on the chart
    def add_line_on_click(trace, points, state):
        if len(points.point_inds) == 0:  # Ignore clicks with no points selected
            return

        # Get the x-coordinate of the clicked point (i.e., the timestamp of the candlestick)
        x = trace.x[points.point_inds[0]]

        # Create a new shape object representing the horizontal line
        line_shape = {
            'type': 'line',
            'x0': leftmost_x,  # Set the line's x-coordinates to the full range of the x-axis
            'y0': points.y,  # Set the line's y-coordinate to the y-coordinate of the clicked point
            'x1': rightmost_x,
            'y1': points.y,
            'xref': 'x',
            'yref': 'y',
            'line': {
                'color': 'red',
                'width': 2,
            },
            'editable': True,  # Enable editing of the shape (i.e., dragging)
        }

        # Add the line shape to the figure's shapes list
        fig.add_shape(line_shape)

    # Add the callback function to the candlestick trace's 'click' event
    fig.data[0].on_click(add_line_on_click)

    return fig
def get_column_value_by_ticker(dataframe, ticker,column_name):

    return dataframe.loc[dataframe['ticker'] == ticker,column_name]
def add_plot_of_order_sl_and_tp(index_of_trading_pair_to_select,ticker,df_with_models,fig,entire_ohlcv_df):

    if "technical_stop_loss" in df_with_models.columns:
        column_name="technical_stop_loss"
        technical_stop_loss=df_with_models[column_name].iat[index_of_trading_pair_to_select]

        fig.add_hline(y=technical_stop_loss, line_color="green", opacity=0.5)
    if "calculated_stop_loss" in df_with_models.columns:
        column_name = "calculated_stop_loss"
        calculated_stop_loss = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=calculated_stop_loss, line_color="magenta", opacity=0.5)
    if "buy_order" in df_with_models.columns:
        column_name = "buy_order"
        buy_order = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=buy_order, line_color="blue", opacity=0.5)
    if "sell_order" in df_with_models.columns:
        column_name = "sell_order"
        sell_order = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=sell_order, line_color="blue", opacity=0.5)

    if "take_profit_when_sl_is_calculated_3_to_1" in df_with_models.columns:
        column_name = "take_profit_when_sl_is_calculated_3_to_1"
        take_profit_when_sl_is_calculated_3_to_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_when_sl_is_calculated_3_to_1, line_color="magenta", opacity=0.5)
    if "take_profit_when_sl_is_calculated_4_to_1" in df_with_models.columns:
        column_name = "take_profit_when_sl_is_calculated_4_to_1"
        take_profit_when_sl_is_calculated_4_to_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_when_sl_is_calculated_4_to_1, line_color="magenta", opacity=0.5)

    if "take_profit_when_sl_is_technical_3_to_1" in df_with_models.columns:
        column_name = "take_profit_when_sl_is_technical_3_to_1"
        take_profit_when_sl_is_technical_3_to_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_when_sl_is_technical_3_to_1, line_color="green", opacity=0.5)
    if "take_profit_when_sl_is_technical_4_to_1" in df_with_models.columns:
        column_name = "take_profit_when_sl_is_technical_4_to_1"
        take_profit_when_sl_is_technical_4_to_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_when_sl_is_technical_4_to_1, line_color="green", opacity=0.5)

    if "take_profit_3_1" in df_with_models.columns:
        column_name = "take_profit_3_1"
        take_profit_3_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_3_1, line_color="green", opacity=0.5)
    if "take_profit_4_1" in df_with_models.columns:
        column_name = "take_profit_4_1"
        take_profit_4_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        fig.add_hline(y=take_profit_4_1, line_color="green", opacity=0.5)

    min_timestamp=0
    if "human_date_of_bsu" in df_with_models.columns:
        column_name = "timestamp_of_bsu"
        timestamp_of_bsu = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        min_timestamp=timestamp_of_bsu
        column_name = "human_date_of_bsu"
        human_date_of_bsu = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        human_date_of_bsu=human_date_of_bsu.replace("/","-")
        # fig.add_vline(x=human_date_of_bsu, line_color="yellow", opacity=0.5)
        if "atl" in df_with_models.columns:
            column_name = "atl"
            atl = df_with_models[column_name].iat[index_of_trading_pair_to_select]
            fig.add_trace(go.Scatter(x=(human_date_of_bsu,),
                                     y=(atl,),
                                     mode='markers', marker=dict(
                    color='yellow'  # Set the marker color to yellow
                ),
                                     name=f"bsu"  # Assign a name to the trace
                                     ))
        if "ath" in df_with_models.columns:
            column_name = "ath"
            ath = df_with_models[column_name].iat[index_of_trading_pair_to_select]
            fig.add_trace(go.Scatter(x=(human_date_of_bsu,),
                                     y=(ath,),
                                     mode='markers', marker=dict(
                    color='yellow'  # Set the marker color to yellow
                ),
                                     name=f"bsu"  # Assign a name to the trace
                                     ))

    timestamp_of_tp_n_to_one_is_reached_sl_calculated = 0
    timestamp_of_tp_n_to_one_is_reached_sl_technical = 0
    timestamp_when_calculated_stop_loss_was_reached = 0
    timestamp_when_technical_stop_loss_was_reached = 0
    if "human_date_of_breakout_bar" in df_with_models.columns:
        column_name = "human_date_of_breakout_bar"
        human_date_of_breakout_bar = df_with_models[column_name].iat[index_of_trading_pair_to_select]
        human_date_of_breakout_bar=human_date_of_breakout_bar.replace("/","-")
        fig.add_vline(x=human_date_of_breakout_bar, line_color="blue", opacity=0.5)

    if "max_profit_target_multiple_when_sl_calculated" in df_with_models.columns:
        column_name = "max_profit_target_multiple_when_sl_calculated"
        max_profit_target_multiple_when_sl_calculated = df_with_models[column_name].iat[index_of_trading_pair_to_select]

        #process tp 3 to 1
        if "take_profit_when_sl_is_calculated_3_to_1_is_reached" in df_with_models.columns:
            column_name = f"take_profit_when_sl_is_calculated_3_to_1_is_reached"
            take_profit_when_sl_is_calculated_3_to_1_is_reached = df_with_models[column_name].iat[index_of_trading_pair_to_select]
            take_profit_when_sl_is_calculated_3_to_1_is_reached=bool(take_profit_when_sl_is_calculated_3_to_1_is_reached)

            if take_profit_when_sl_is_calculated_3_to_1_is_reached==True:

                column_name = f"take_profit_when_sl_is_calculated_3_to_1"
                take_profit_when_sl_is_calculated_3_to_1 = df_with_models[column_name].iat[index_of_trading_pair_to_select]


                column_name = "datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached"
                datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached = df_with_models[column_name].iat[
                    index_of_trading_pair_to_select]
                datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached = datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached.strftime(
                    "%Y-%m-%d")
                # Add traces
                fig.add_trace(go.Scatter(x=(datetime_take_profit_when_sl_is_calculated_3_to_1_was_reached,),
                                         y=(take_profit_when_sl_is_calculated_3_to_1,),
                                         mode='markers', marker=dict(
                        color='magenta'  # Set the marker color to silver
                    ),
                                         name=f"tp_3_to_1_sl_calculated"  # Assign a name to the trace
                                         ))


        if max_profit_target_multiple_when_sl_calculated!=0:
            for n in range(4,int(max_profit_target_multiple_when_sl_calculated)+1):
                column_name = f"take_profit_{n}_to_one_sl_calculated"
                take_profit_n_to_one_sl_calculated = df_with_models[column_name].iat[index_of_trading_pair_to_select]


                column_name = f"datetime_of_tp_{n}_to_one_is_reached_sl_calculated"
                datetime_of_tp_n_to_one_is_reached_sl_calculated = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                datetime_of_tp_n_to_one_is_reached_sl_calculated = datetime_of_tp_n_to_one_is_reached_sl_calculated.strftime("%Y-%m-%d")
                # st.write("type(datetime_of_tp_n_to_one_is_reached_sl_calculated)")
                # st.write(type(datetime_of_tp_n_to_one_is_reached_sl_calculated))

                column_name = f"timestamp_of_tp_{n}_to_one_is_reached_sl_calculated"
                timestamp_of_tp_n_to_one_is_reached_sl_calculated = df_with_models[column_name].iat[
                    index_of_trading_pair_to_select]

                # Add traces
                fig.add_trace(go.Scatter(x=(datetime_of_tp_n_to_one_is_reached_sl_calculated,), y=(take_profit_n_to_one_sl_calculated,),
                                        mode='markers',marker=dict(
                                                                        color='magenta'  # Set the marker color to magenta
                                                                    ),
                                        name=f"tp_{n}_to_1_sl_calculated"  # Assign a name to the trace
                                         ))


        if max_profit_target_multiple_when_sl_calculated==0:
            if "calculated_stop_loss" in df_with_models.columns:
                column_name = f"calculated_stop_loss"
                calculated_stop_loss = df_with_models[column_name].iat[index_of_trading_pair_to_select]

                column_name = f"calculated_stop_loss_is_reached"
                calculated_stop_loss_is_reached = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                calculated_stop_loss_is_reached=bool(calculated_stop_loss_is_reached)
                if calculated_stop_loss_is_reached==True:
                    # column_name = f"calculated_stop_loss_is_reached"
                    # calculated_stop_loss_is_reached = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                    column_name="datetime_when_calculated_stop_loss_was_reached"
                    datetime_when_calculated_stop_loss_was_reached = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                    datetime_when_calculated_stop_loss_was_reached = datetime_when_calculated_stop_loss_was_reached.strftime(
                        "%Y-%m-%d")

                    column_name = "timestamp_when_calculated_stop_loss_was_reached"
                    timestamp_when_calculated_stop_loss_was_reached = df_with_models[column_name].iat[
                        index_of_trading_pair_to_select]
                    # Add traces
                    fig.add_trace(go.Scatter(x=(datetime_when_calculated_stop_loss_was_reached,),
                                             y=(calculated_stop_loss,),
                                             mode='markers', marker=dict(
                            color='cyan'  # Set the marker color
                        ),
                                             name=f"calculated_stop_loss"  # Assign a name to the trace
                                             ))

    if "max_profit_target_multiple_when_sl_technical" in df_with_models.columns:
        column_name = "max_profit_target_multiple_when_sl_technical"
        max_profit_target_multiple_when_sl_technical = df_with_models[column_name].iat[index_of_trading_pair_to_select]

        # process tp 3 to 1
        if "take_profit_when_sl_is_technical_3_to_1_is_reached" in df_with_models.columns and\
                "take_profit_when_sl_is_technical_3_to_1" in df_with_models.columns:
            column_name = f"take_profit_when_sl_is_technical_3_to_1_is_reached"
            take_profit_when_sl_is_technical_3_to_1_is_reached = df_with_models[column_name].iat[
                index_of_trading_pair_to_select]
            take_profit_when_sl_is_technical_3_to_1_is_reached = bool(
                take_profit_when_sl_is_technical_3_to_1_is_reached)

            if take_profit_when_sl_is_technical_3_to_1_is_reached == True:
                column_name = f"take_profit_when_sl_is_technical_3_to_1"
                take_profit_when_sl_is_technical_3_to_1 = df_with_models[column_name].iat[
                    index_of_trading_pair_to_select]

                column_name = "datetime_take_profit_when_sl_is_technical_3_to_1_was_reached"
                datetime_take_profit_when_sl_is_technical_3_to_1_was_reached = df_with_models[column_name].iat[
                    index_of_trading_pair_to_select]



                datetime_take_profit_when_sl_is_technical_3_to_1_was_reached = datetime_take_profit_when_sl_is_technical_3_to_1_was_reached.strftime(
                    "%Y-%m-%d")
                # Add traces
                fig.add_trace(go.Scatter(x=(datetime_take_profit_when_sl_is_technical_3_to_1_was_reached,),
                                         y=(take_profit_when_sl_is_technical_3_to_1,),
                                         mode='markers', marker=dict(
                        color='lime'  # Set the marker color to lime
                    ),
                                         name=f"tp_3_to_1_sl_technical"  # Assign a name to the trace
                                         ))


        if max_profit_target_multiple_when_sl_technical!=0:
            for n in range(4,int(max_profit_target_multiple_when_sl_technical)+1):
                column_name = f"take_profit_{n}_to_one_sl_technical"
                take_profit_n_to_one_sl_technical = df_with_models[column_name].iat[index_of_trading_pair_to_select]

                column_name = f"timestamp_of_tp_{n}_to_one_is_reached_sl_technical"
                timestamp_of_tp_n_to_one_is_reached_sl_technical = df_with_models[column_name].iat[
                    index_of_trading_pair_to_select]


                column_name = f"datetime_of_tp_{n}_to_one_is_reached_sl_technical"
                datetime_of_tp_n_to_one_is_reached_sl_technical = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                datetime_of_tp_n_to_one_is_reached_sl_technical = datetime_of_tp_n_to_one_is_reached_sl_technical.strftime("%Y-%m-%d")
                # st.write("type(datetime_of_tp_n_to_one_is_reached_sl_technical)")
                # st.write(type(datetime_of_tp_n_to_one_is_reached_sl_technical))

                # Add traces
                fig.add_trace(go.Scatter(x=(datetime_of_tp_n_to_one_is_reached_sl_technical,), y=(take_profit_n_to_one_sl_technical,),
                                        mode='markers',marker=dict(
                                                                        color='lime'  # Set the marker color
                                                                    ),
                                        name=f"tp_{n}_to_1_sl_technical"  # Assign a name to the trace
                                         ))


        if max_profit_target_multiple_when_sl_technical == 0:
            st.write("max_profit_target_multiple_when_sl_technical == 0")
            if "technical_stop_loss" in df_with_models.columns:
                column_name = f"technical_stop_loss"
                technical_stop_loss = df_with_models[column_name].iat[index_of_trading_pair_to_select]

                column_name = f"technical_stop_loss_is_reached"
                technical_stop_loss_is_reached = df_with_models[column_name].iat[index_of_trading_pair_to_select]
                technical_stop_loss_is_reached = bool(technical_stop_loss_is_reached)
                if technical_stop_loss_is_reached == True:
                    # column_name = f"technical_stop_loss_is_reached"
                    # technical_stop_loss_is_reached = df_with_models[column_name].iat[
                    #     index_of_trading_pair_to_select]
                    column_name = "datetime_when_technical_stop_loss_was_reached"
                    datetime_when_technical_stop_loss_was_reached = df_with_models[column_name].iat[
                        index_of_trading_pair_to_select]
                    datetime_when_technical_stop_loss_was_reached = datetime_when_technical_stop_loss_was_reached.strftime(
                        "%Y-%m-%d")

                    column_name = "timestamp_when_technical_stop_loss_was_reached"
                    timestamp_when_technical_stop_loss_was_reached = df_with_models[column_name].iat[
                        index_of_trading_pair_to_select]

                    # Add traces
                    fig.add_trace(go.Scatter(x=(datetime_when_technical_stop_loss_was_reached,),
                                             y=(technical_stop_loss,),
                                             mode='markers', marker=dict(
                            color='#808000'  # Set the marker color to olive
                        ),
                                             name=f"technical_stop_loss"  # Assign a name to the trace
                                             ))
    max_timestamp=max(timestamp_of_tp_n_to_one_is_reached_sl_calculated,
        timestamp_of_tp_n_to_one_is_reached_sl_technical,
        timestamp_when_calculated_stop_loss_was_reached,
        timestamp_when_technical_stop_loss_was_reached)
    max_timestamp=max_timestamp+5*86400
    min_timestamp=min_timestamp-5*86400
    min_datetime_str=datetime.datetime.fromtimestamp(min_timestamp).strftime('%Y-%m-%d')
    max_datetime_str=datetime.datetime.fromtimestamp(max_timestamp).strftime('%Y-%m-%d')

    # Slice the DataFrame to extract rows within the specified range
    sliced_df = entire_ohlcv_df[
        (entire_ohlcv_df["Timestamp"] > min_timestamp) & (entire_ohlcv_df["Timestamp"] < max_timestamp)]

    # Extract the lists of highs and lows from the sliced DataFrame
    highs_list = sliced_df["high"].tolist()
    lows_list = sliced_df["low"].tolist()
    max_high=max(highs_list)
    min_low=min(lows_list)

    fig.update_xaxes(type="date", range=[min_datetime_str, max_datetime_str])
    fig.update_yaxes(range=[min_low, max_high])

def plot_ohlcv(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000,
               table_name,row_of_pair_ready_for_model,
               index_of_trading_pair_to_select,
               ticker_with_exchange_where_model_was_found,
               df_with_resulting_table_of_certain_models,
               entire_ohlcv_df,
               crypto_ticker,
               asset_type,
               height,width,key_for_placeholder):

    # st.write("row_of_pair_ready_for_model")
    # st.write(row_of_pair_ready_for_model)

    print(f"entire_ohlcv_df_in_plot for {crypto_ticker}")
    print(entire_ohlcv_df.tail(5).to_string())
    # placeholder=st.empty()

    try:
        # with placeholder.container():


        exchange=""
        trading_pair_is_traded_with_margin_bool=False
        url_of_trading_pair=""
        try:
            exchange = entire_ohlcv_df.iloc[-1, entire_ohlcv_df.columns.get_loc("exchange")]
            # st.write("exchange11")
            # st.write(exchange)
        except:
            traceback.print_exc()

        # ticker=entire_ohlcv_df["ticker"]
        # crypto_ticker=ticker.replace("/","_")+"_on_"+exchange

        if "trading_pair" in entire_ohlcv_df.columns:
            crypto_ticker=entire_ohlcv_df["trading_pair"].iat[0]
        else:
            crypto_ticker=entire_ohlcv_df["ticker"].iat[0]+"_on_"+exchange

        if "trading_pair_is_traded_with_margin" in entire_ohlcv_df.columns:
            trading_pair_is_traded_with_margin_bool=entire_ohlcv_df["trading_pair_is_traded_with_margin"].iat[0]

        if "url_of_trading_pair" in entire_ohlcv_df.columns:
            url_of_trading_pair = entire_ohlcv_df["url_of_trading_pair"].iat[0]


        # st.dataframe(entire_ohlcv_df)
        create_button_show_or_hide_dataframe(entire_ohlcv_df,key_for_placeholder)
        st.write(f"Number of all available days in database for {crypto_ticker} is {len(entire_ohlcv_df)}")
        st.write(f"\n If this number is too much round, for example, 1000 or 100 \nthis is suspicious and you'd better check the exchange webside itself"
                 f"\n to verify that the chart in this app has all available days")

        exchange_name_in_list=exchange

        # st.write(f"{crypto_ticker} outside create button function")
        create_button_show_or_hide_trading_view_chart(crypto_ticker, exchange, exchange_name_in_list, height, width,
                                                      asset_type,key_for_placeholder+10000000)

        crypto_ticker_for_tv=crypto_ticker.split("_on_")[0]
        #add link to trading view markets (where trading pair is traded)
        url_of_trading_pair_on_trading_view_markets=f'''https://www.tradingview.com/symbols/{crypto_ticker_for_tv.replace("_","")}/markets/'''
        if asset_type=="swap":
            url_of_trading_pair_on_trading_view_markets = f'''https://www.tradingview.com/symbols/{crypto_ticker_for_tv.split(":")[0].replace("_", "")+".P"}/markets/'''
        link = f'Click [go to Trading View]({url_of_trading_pair_on_trading_view_markets}) if you want to go to Trading View to see all markets where {crypto_ticker_for_tv} is traded '
        st.markdown(link, unsafe_allow_html=True)

        url_of_trading_pair_link=f'Click [{crypto_ticker}]({url_of_trading_pair})  if you want to go to {exchange} website and see the trading pair yourself'
        st.markdown(url_of_trading_pair_link, unsafe_allow_html=True)

        # st.button(label=f"View chart of {crypto_ticker} on Trading View",key=np.random.random(100)
        #           ,on_click=generate_html_of_tv_widget_to_insert_into_streamlit,
        #           args=(height, width, exchange, crypto_ticker,asset_type))

        # st.write(f"If you see 'Invalid symbol' on the Trading View chart below it means "
        #          f"Trading View does not have {crypto_ticker} on {exchange} chart available")
        # html_of_trading_view_widget=generate_html_of_tv_widget_to_insert_into_streamlit(height, width, exchange, crypto_ticker, asset_type)
        # components.html(html_of_trading_view_widget, height=height, width=width)

        fig = go.Figure(go.Ohlc(x=entire_ohlcv_df["open_time"], open=entire_ohlcv_df['open'], high=entire_ohlcv_df['high'],
            low=entire_ohlcv_df['low'], close=entire_ohlcv_df['close'], increasing_line_color= 'green',
            decreasing_line_color='red'),layout={'dragmode': 'pan'})

        config = dict({'scrollZoom': True,'displaylogo': False,
                       'modeBarButtonsToAdd':['drawline','eraseshape']})
        # annotations = [
        #     {
        #         'x': xVal,
        #         'y': yVal,
        #         'xref': 'x',
        #         'yref': 'y',
        #         'xaxis': 'x',
        #         'yaxis': 'y',
        #         'axref': 'pixel',
        #         'ayref': 'pixel',
        #         'ax': xPixel,
        #         'ay': yPixel,
        #         'showarrow': True,
        #         'arrowhead': 0,
        #         'arrowwidth': 2,
        #         'arrowcolor': '#000000'
        #     }
        # ]
        # leftmost_x=entire_ohlcv_df["open_time"].iat[0]
        # rightmost_x = entire_ohlcv_df["open_time"].iat[-1]
        #
        # fig = add_horizontal_line_on_click(fig,leftmost_x,rightmost_x)

        # # Add the line shape to the figure's shapes list
        # fig.update_layout(shapes=[line_shape])

        #add horizontal line with the level of the first day in dataframe
        fig.add_hline(y=entire_ohlcv_df['low'].iat[0], line_color="black",
                      line_dash='dash',opacity=0.1)

        # add horizontal line with the level of the first day in dataframe
        fig.add_hline(y=entire_ohlcv_df['high'].iat[0], line_color="black",
                      line_dash='dash', opacity=0.1)

        exchange_where_model_was_found=df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'exchange'].iat[0]

        # st.write("row_of_pair_ready_for_model1")
        # st.write(row_of_pair_ready_for_model)

        if exchange==exchange_where_model_was_found:

            if "atl" in df_with_resulting_table_of_certain_models.columns:
                atl=df_with_resulting_table_of_certain_models.loc[
                    row_of_pair_ready_for_model, 'atl'].iat[0]
                fig.add_hline(y=atl, line_color="black",
                              line_dash='dash', opacity=1)
            if "ath" in df_with_resulting_table_of_certain_models.columns:
                atl=df_with_resulting_table_of_certain_models.loc[
                    row_of_pair_ready_for_model, 'ath'].iat[0]
                fig.add_hline(y=atl, line_color="black",
                              line_dash='dash', opacity=1)

        # add horizontal lines with sl , tp and order
        if crypto_ticker==ticker_with_exchange_where_model_was_found:
            add_plot_of_order_sl_and_tp(index_of_trading_pair_to_select,crypto_ticker, df_with_resulting_table_of_certain_models, fig,entire_ohlcv_df)


            # if st.button(label="start tracing this asset and on next bar print enter position ",
            #              key=key_for_placeholder + 200 + 4):
            #     column_name="ticker_will_be_traced_and_position_entered"
            #     value=True
            #
            #     set_value_in_sql_table(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000,
            #                            crypto_ticker, table_name, column_name, value)
            #     st.write("on next bar print i will enter the position")



            #

        fig.update_xaxes(rangeslider={'visible': False})
        # st.write("all time low for",f'{crypto_ticker.split("_on_")[0]} on {exchange} =',entire_ohlcv_df["low"].min())
        # st.write("all time high for",f'{crypto_ticker.split("_on_")[0]} on {exchange} =', entire_ohlcv_df["high"].max())
        fig.update_layout(height=height ,
                          width=width,
                          title_text=f'{crypto_ticker.split("_on_")[0]} on {exchange} ',
                                     # f'with level formed by atl={atl}',
                          font=dict(
                              family="Courier New, monospace",
                              size=40,
                              color="RebeccaPurple"
                          ))
        fig.update_layout(hovermode="x unified")
        fig.update_layout(hoverlabel=dict(bgcolor='rgba(255,255,255,0.3)',font=dict(color='black')))

        # fig.update_layout(hoverlabel.xanchor='right', hoverlabel.yanchor='right')
        fig.update_xaxes(showspikes=True,spikesnap ='cursor',spikemode="across+marker",spikethickness=1)
        fig.update_yaxes(showspikes=True,spikesnap ='cursor',spikemode="across+marker",spikethickness=1)
        fig.update_layout(modebar_add=["toggleHover","toggleSpikelines"])

        # # fig.update_layout(hoverlabel_distance=10)
        # if st.button(label="disable info about open,high,low,close,volume on mouse hover",key=key_for_placeholder+10000):
        #     fig.update_layout(hovermode=False)
        # if st.button(label="enable info about open,high,low,close,volume on mouse hover",key=key_for_placeholder+1000000+1):
        #     fig.update_layout(hovermode="x unified")

        # # Enable drawing tools with specific configuration
        # fig.update_layout({
        #     'clickmode': 'event+select',
        #     'dragmode': 'select',
        #     'selectdirection': 'h',
        #     'modebar': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect',
        #                             'eraseshape']
        # })

        # fig.update_layout(hover_data=['open', 'high', 'low', 'close', 'volume'])
        # fig.update_traces(hovertext=entire_ohlcv_df["volume"] )
        # fig.update_traces(hovertext=[f"volume: {volume}" for volume in entire_ohlcv_df["volume"]])
        # fig.update_traces(hovertext=[f"volume*low: {volume_times_low} $" for volume_times_low in entire_ohlcv_df["volume*low"]])

        # fig.update_traces(hovertext = [f"volume: {volume}  volume*low: {volume_times_low} $" for volume, volume_times_low in zip(entire_ohlcv_df["volume"], entire_ohlcv_df["volume*low"] )])
        fig.update_traces(
            hovertext=[f"volume: {volume}<br>volume*low: {volume_times_low} $<br>volume*close: {volume_times_close} $" for volume, volume_times_low,volume_times_close in
                       zip(entire_ohlcv_df["volume"], entire_ohlcv_df["volume*low"], entire_ohlcv_df["volume*close"])])

        fig.update_layout(showlegend=True)

        ##########################

        ######################################

        st.plotly_chart(fig,config=config)

        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------
        #---------------------------------------------



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
# @st.cache_resource

# Set value in PostgreSQL database table
def set_value_in_sql_table(conn, crypto_ticker, table_name, column_name, value):
    # Create cursor to execute PostgreSQL queries
    # cursor = conn.cursor()

    # Set value in table
    print("table_name")
    print(table_name)
    print("value")
    print(value)
    print("column_name")
    print(column_name)
    query=''
    if value=="market" or value=="limit":
        print(f"value_is_equal_to_{value}")
        query = f'''UPDATE public."{table_name}" SET {column_name} = '{value}' WHERE ticker = '{crypto_ticker}'; '''
    # value=False
    else:
        query = f'''UPDATE public."{table_name}" SET {column_name} = {value} WHERE ticker = '{crypto_ticker}'; '''
    result = conn.execute(query)
    print(f'Value set to {value} in {table_name} table.')

    # Commit changes and close connection
    # conn.commit()
    return conn

def initialize_connection_and_engine(db_where_ohlcv_data_for_stocks_is_stored_0000):

    engine_for_ohlcv_data_for_stocks_0000, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_0000)
    return engine_for_ohlcv_data_for_stocks_0000,connection_to_ohlcv_data_for_stocks

# @st.cache_data(ttl=30)
def return_df_from_postgres_sql_table_original(table_name,_engine_name):
    query=f'''select * from "{table_name}"'''
    df_with_resulting_table_of_certain_models = \
        pd.read_sql_query(query,
                          _engine_name)
    return df_with_resulting_table_of_certain_models
@st.cache_data(experimental_allow_widgets=True)
def return_df_from_postgres_sql_table(table_name,_engine_name):
    df_with_resulting_table_of_certain_models=pd.DataFrame()
    exchanges = ["binance", "gateio", "huobi", "mexc3", "huobipro", "kucoin", "okex5",
                 "bybit", "lbank2", "bitfinex2", "bingx", "whitebit", "bigone"]
    exchange_conditions = ", ".join([f"'{exchange}'" for exchange in exchanges])

    try:

        query = f'''SELECT *
            FROM public."{table_name}" order by timestamp_of_order_placement_bar;'''
        df_with_resulting_table_of_certain_models = \
            pd.read_sql_query(query,
                              _engine_name)
    finally:
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

def plot_trading_view_charts_on_okex_and_bitstamp_in_front_of_plotly_charts(trading_pair,height,width,asset_type):
    st.write(f"Maybe {trading_pair} is available on the OKEX exchange."
             f"\n\nLook at the Trading View chart to find out."
             f"\n\nIf you see 'Invalid symbol' it means {trading_pair} cannot be found on OKEX exchange via Trading View")
    html_of_trading_view_widget = generate_html_of_tv_widget_to_insert_into_streamlit(height=height,
                                                                                      width=width,
                                                                                      exchange_name="okx",
                                                                                      trading_pair=trading_pair
                                                                                      , asset_type=asset_type)
    components.html(html_of_trading_view_widget, height=height, width=width)

    st.write(f"Maybe {trading_pair} is available on the BITSTAMP exchange."
             f" Look at the Trading View chart to find out")
    html_of_trading_view_widget = generate_html_of_tv_widget_to_insert_into_streamlit(height=height,
                                                                                      width=width,
                                                                                      exchange_name="bitstamp",
                                                                                      trading_pair=trading_pair
                                                                                      , asset_type=asset_type)
    components.html(html_of_trading_view_widget, height=height, width=width)

def create_button_show_dataframe(entire_ohlcv_df):
    if st.button("Show table with open, high, low, close, volume info"):
        st.dataframe(entire_ohlcv_df)


def create_button_show_or_hide_dataframe(entire_ohlcv_df,key_for_placeholder):
    placeholder = st.empty()
    if st.checkbox(label="Click to show/hide table with open, high, low, close, volume info",key=key_for_placeholder):
        placeholder.dataframe(entire_ohlcv_df)

def create_button_show_or_hide_trading_view_chart(trading_pair,exchange,exchange_name_in_list,height,width,asset_type,key_for_placeholder):

    exchange_name = trading_pair.split("_on_")[1]
    trading_pair=trading_pair.split("_on_")[0]

    trading_pair=trading_pair.replace("_","/")
    # st.write(f"{trading_pair} inside create button function for tv")
    if st.checkbox(label=f"Click to show/hide TRADING VIEW CHART of {trading_pair} on {exchange_name}",key=key_for_placeholder):
        st.write(f"If you see 'Invalid symbol' on the Trading View chart below it means "
                 f"Trading View does not have {trading_pair} on {exchange} chart available")
        html_of_trading_view_widget = generate_html_of_tv_widget_to_insert_into_streamlit(height, width,
                                                                                          exchange_name_in_list,
                                                                                          trading_pair, asset_type)
        with st.container():
            components.html(html_of_trading_view_widget, height=height, width=width)


        # components.html(html_of_trading_view_widget)


    # if st.button("Show/Hide table with open, high, low, close, volume info"):
    #     df_visible = not df_visible  # toggle value
    #
    #     if df_visible:
    #         st.dataframe(entire_ohlcv_df)
@st.cache_data(experimental_allow_widgets=True,persist=True)
def get_data_ohlcv_data_for_low_volume(table_with_ohlcv_table,_engine_for_ohlcv_low_volume_data_for_stocks_0000):
    table_with_ohlcv_data_df = \
        pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                          _engine_for_ohlcv_low_volume_data_for_stocks_0000)
    return table_with_ohlcv_data_df
@st.cache_data(experimental_allow_widgets=True,persist=True)
def get_data_ohlcv_data_for_normal_volume(table_with_ohlcv_table,_engine_for_ohlcv_data_for_stocks_0000):
    table_with_ohlcv_data_df = \
        pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                          _engine_for_ohlcv_data_for_stocks_0000)
    return table_with_ohlcv_data_df
def plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000,
                                     table_name,
                                     index_of_trading_pair_to_select,trading_pair_to_select,
                                     df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                     engine_for_ohlcv_low_volume_data_for_stocks_0000,height,width):
    ticker_with_exchange_where_model_was_found=trading_pair_to_select
    trading_pair_first_part_without_exchange = trading_pair_to_select.split("_on_")[0]
    trading_pair = trading_pair_to_select.split("_on_")[0]
    # exchange= df_with_resulting_table_of_certain_models.iloc[-1, df_with_resulting_table_of_certain_models.columns.get_loc("exchange")]

    # st.write("1index_of_trading_pair_to_select")
    # st.write(index_of_trading_pair_to_select)

    series_of_exchanges_where_pair_is_traded = \
        df_with_resulting_table_of_certain_models.loc[
            df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select,
            "exchange_id_string_where_trading_pair_is_traded"]

    # row_of_pair_ready_for_model = df_with_resulting_table_of_certain_models.loc[
    #     df_with_resulting_table_of_certain_models["ticker"] == trading_pair_to_select,
    #     "exchange_id_string_where_trading_pair_is_traded"].index

    row_of_pair_ready_for_model=pd.Series(index_of_trading_pair_to_select)

    exchange = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'exchange']

    # atl = df_with_resulting_table_of_certain_models.loc[
    #     row_of_pair_ready_for_model, 'atl'].iat[0]
    url_of_trading_pair_on_particular_exchange = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'url_of_trading_pair'].iat[0]
    asset_type = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'asset_type'].iat[0]
    exchanges_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'exchange_id_string_where_trading_pair_is_traded'].iat[0]

    ####################3
    exchanges_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, 'exchange_id_string_where_trading_pair_is_traded'].iat[0]
    ########################


    trading_pair = trading_pair.replace("_", "/")
    exchange_name = exchange.iat[0]
    # st.write(exchange.iat[0])
    # st.write(trading_pair)

    # Draw a horizontal line
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True)
    st.subheader(f'{trading_pair_to_select.split("_on_")[0]} on {exchange_name} ')

    # link = f'Click this link if you want to go to {exchange_name} website to see {trading_pair}  [link]({url_of_trading_pair_on_particular_exchange})'
    # link = f'[Go to {exchange_name.upper()} website]({url_of_trading_pair_on_particular_exchange}) to see {trading_pair} '
    # st.markdown(link, unsafe_allow_html=True)

    string_of_exchanges_where_pair_is_traded = series_of_exchanges_where_pair_is_traded.iat[0]
    st.write(f"{trading_pair} as spot or perpetual swap is traded on the following cryptocurrency exchanges")

    list_of_exchange_ids_where_pair_is_traded_on = string_of_exchanges_where_pair_is_traded.split("_")

    exchange_names_where_pair_is_traded = df_with_resulting_table_of_certain_models.loc[
        row_of_pair_ready_for_model, "exchange_names_string_where_trading_pair_is_traded"].iat[0]
    list_of_exchange_names_where_pair_is_traded_on = exchange_names_where_pair_is_traded.split("_")

    st.write(exchanges_where_pair_is_traded)

    # resulting_list_of_ohlcv_dataframes=\
    #     asyncio.run(generate_tasks_in_async_fetch_entire_ohlcv(trading_pair,list_of_exchange_ids_where_pair_is_traded_on,asset_type))

    if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        max_profit_target_multiple_when_sl_calculated = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'max_profit_target_multiple_when_sl_calculated'].iat[0]
        st.write(f"max_profit_target_multiple_when_sl_calculated for"
                 f" {ticker_with_exchange_where_model_was_found}={max_profit_target_multiple_when_sl_calculated}")
    if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        max_profit_target_multiple_when_sl_technical = df_with_resulting_table_of_certain_models.loc[
            row_of_pair_ready_for_model, 'max_profit_target_multiple_when_sl_technical'].iat[0]
        st.write(f"max_profit_target_multiple_when_sl_technical for"
                 f" {ticker_with_exchange_where_model_was_found}={max_profit_target_multiple_when_sl_technical}")

    # st.write(f"Maybe {trading_pair} is available on the OKEX exchange."
    #          f" Look at the Trading View chart to find out")
    # html_of_trading_view_widget = generate_html_of_tv_widget_to_insert_into_streamlit(height=height,
    #                                                                                   width=width,
    #                                                                                   exchange_name="okx",
    #                                                                                   trading_pair=trading_pair
    #                                                                                   , asset_type=asset_type)
    # components.html(html_of_trading_view_widget, height=height, width=width)
    #
    # st.write(f"Maybe {trading_pair} is available on the BITSTAMP exchange."
    #          f" Look at the Trading View chart to find out")
    # html_of_trading_view_widget = generate_html_of_tv_widget_to_insert_into_streamlit(height=height,
    #                                                                                   width=width,
    #                                                                                   exchange_name="bitstamp",
    #                                                                                   trading_pair=trading_pair
    #                                                                                   , asset_type=asset_type)
    # components.html(html_of_trading_view_widget, height=height, width=width)

    list_of_tables_in_low_volume_ohlcv_db = get_list_of_tables_in_db(engine_for_ohlcv_low_volume_data_for_stocks_0000)
    list_of_tables_in_normal_volume_ohlcv_db = get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_0000)
    # st.write("list_of_tables_in_low_volume_ohlcv_db")
    # st.write(list_of_tables_in_low_volume_ohlcv_db)

    # for exchange_id in list_of_exchange_ids_where_pair_is_traded_on:
    # st.write("exchange_name")
    # st.write(exchange_name)

    exchange_id=exchange_name
    # key_for_placeholder = get_index_of_exchange_id(list_of_exchange_ids_where_pair_is_traded_on, exchange_id)
    key_for_placeholder=index_of_trading_pair_to_select

    try:


        # if exchange_id=="btcex":
            # st.write("If the exchange is BTCEX then there might be a ONE-MINUTE timeframe chart instead of DAILY."
            #          " Be careful")

        # print(f"starting thread for {exchange}")
        # timeframe="1d"
        # t = threading.Thread(target=constant_update_of_ohlcv_for_one_pair_on_many_exchanges_in_todays_db,
        #                      args=(engine_for_ohlcv_low_volume_data_for_stocks_0000, trading_pair, exchange_id, timeframe))
        # t.start()



        table_with_ohlcv_table = trading_pair_first_part_without_exchange + "_on_" + exchange_id
        # for table_with_ohlcv_table in tuple_of_trading_pairs_with_exchange:
        table_with_ohlcv_data_df=pd.DataFrame()
        if table_with_ohlcv_table in list_of_tables_in_low_volume_ohlcv_db:
            st.write(f"{table_with_ohlcv_table} is in list_of_tables_in_low_volume_ohlcv_db")

        if table_with_ohlcv_table in list_of_tables_in_normal_volume_ohlcv_db:
            st.write(f"{table_with_ohlcv_table} is in list_of_tables_in_normal_volume_ohlcv_db")

        if table_with_ohlcv_table in list_of_tables_in_low_volume_ohlcv_db:
            # st.write(f"{table_with_ohlcv_table} is in db with today's pairs")
            # st.write(f"{list_of_tables_in_low_volume_ohlcv_db} is in db with today's pairs")
            try:
                table_with_ohlcv_data_df=get_data_ohlcv_data_for_low_volume(table_with_ohlcv_table,
                                                   engine_for_ohlcv_low_volume_data_for_stocks_0000)
                # table_with_ohlcv_data_df = \
                #     pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                #                       engine_for_ohlcv_low_volume_data_for_stocks_0000)

            except ProgrammingError:
                table_with_ohlcv_data_df = \
                    pd.read_sql_query(f'''select * from "{table_with_ohlcv_table.replace(":USDT","")}"''',
                                      engine_for_ohlcv_low_volume_data_for_stocks_0000)

            plot_ohlcv(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000,
                       table_name,
                       row_of_pair_ready_for_model,
                       index_of_trading_pair_to_select,
                       ticker_with_exchange_where_model_was_found,
                       df_with_resulting_table_of_certain_models,
                       table_with_ohlcv_data_df,
                       trading_pair_to_select,
                       asset_type,
                       height,
                       width,
                       key_for_placeholder)
        else:
            st.write(f"{table_with_ohlcv_table} NOT in list_of_tables_in_low_volume_ohlcv_db")
            try:
                table_with_ohlcv_data_df=get_data_ohlcv_data_for_normal_volume(table_with_ohlcv_table, engine_for_ohlcv_data_for_stocks_0000)

                # table_with_ohlcv_data_df = \
                #     pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                #                       engine_for_ohlcv_data_for_stocks_0000)
            except ProgrammingError:
                table_with_ohlcv_data_df = \
                    pd.read_sql_query(f'''select * from "{table_with_ohlcv_table.replace(":USDT", "")}"''',
                                      engine_for_ohlcv_low_volume_data_for_stocks_0000)
            plot_ohlcv(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000,
                       table_name,
                       row_of_pair_ready_for_model,
                       index_of_trading_pair_to_select,
                       ticker_with_exchange_where_model_was_found,
                       df_with_resulting_table_of_certain_models,
                       table_with_ohlcv_data_df,
                       trading_pair_to_select,
                       asset_type,
                       height,
                       width,
                       key_for_placeholder)




    except:
        traceback.print_exc()

    # st.write("------------------------------------")
    # plot_trading_view_charts_on_okex_and_bitstamp_in_front_of_plotly_charts(trading_pair, height, width, asset_type)



#######################################
####################################
###################################

def get_index_of_exchange_id(list_of_exchange_ids_where_pair_is_traded_on, exchange_id):
    try:
        index = list_of_exchange_ids_where_pair_is_traded_on.index(exchange_id)
    except ValueError:
        index = -1
    return index


def add_scroll_to_top_button():
    # Create a button with the label "Scroll to top"

    scroll_button = st.button("Scroll to top")
    if scroll_button:
        # Scroll to the top of the page
        js_code = 'window.scrollTo(0,0);'
        html_code = f"<script>{js_code}</script>"


def drop_column_called_index(df_with_resulting_table_of_certain_models):
    try:
        if "index" in df_with_resulting_table_of_certain_models.columns:
            df_with_resulting_table_of_certain_models.drop(columns="index", inplace=True)
        else:
            print("there is no index in df1")
    except:
        print("there is no index in df2")
        traceback.print_exc()
    df_with_resulting_table_of_certain_models.reset_index(inplace=True)
# @st.exception
def streamlit_func():
    st.set_page_config(
        page_title="Screen shitcoins and stocks for breakouts, false breakouts and rebounds",
        page_icon="✅",
        layout="wide",
    )

    st.header("Screen shitcoins and stocks for breakouts, false breakouts and rebounds")
    # st.header("Screen shitcoins and stocks for breakouts, false breakouts and rebounds")



    db_where_ohlcv_data_for_stocks_is_stored_0000 = "ohlcv_1d_data_for_usdt_pairs_0000_pagination"
    engine_for_ohlcv_data_for_stocks_0000, \
        connection_to_ohlcv_data_for_stocks = \
        initialize_connection_and_engine(db_where_ohlcv_data_for_stocks_is_stored_0000)

    db_where_ohlcv_low_volume_data_for_stocks_is_stored_0000 = "ohlcv_1d_data_for_low_volume_usdt_pairs_0000_pagination"
    engine_for_ohlcv_low_volume_data_for_stocks_0000, \
        connection_to_ohlcv_low_volume_data_for_stocks = \
        initialize_connection_and_engine(db_where_ohlcv_low_volume_data_for_stocks_is_stored_0000)

    db_where_ohlcv_data_for_stocks_is_stored_0000_todays_pairs = "ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    engine_for_ohlcv_data_for_stocks_0000_todays_pairs, \
        connection_to_ohlcv_data_for_stocks_todays_pairs = \
        initialize_connection_and_engine(db_where_ohlcv_data_for_stocks_is_stored_0000_todays_pairs)

    db_intermediate_db_for_storing_selected_pairs_from_form = "intermediate_db_for_storing_selected_pairs_from_form"
    engine_for_db_intermediate_db_for_storing_selected_pairs_from_form, \
        connection_to_db_intermediate_db_for_storing_selected_pairs_from_form = \
        initialize_connection_and_engine(db_intermediate_db_for_storing_selected_pairs_from_form)

    db_intermediate_db_for_storing_selected_pairs_from_form="intermediate_db_for_storing_selected_pairs_from_form"
    engine_for_db_intermediate_db_for_storing_selected_pairs_from_form, \
        connection_to_db_intermediate_db_for_storing_selected_pairs_from_form = \
        initialize_connection_and_engine(db_intermediate_db_for_storing_selected_pairs_from_form)


    list_of_options_for_today_that_are_available_and_not_all_possible_options=\
        return_list_of_options_for_today_that_are_available_and_not_all_possible_options(
            engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)



    model=st.selectbox("What is your model?",list_of_options_for_today_that_are_available_and_not_all_possible_options)

    height = 500
    width = 900

    if model=="New ATL within last two days":
        table_name="current_asset_had_atl_within_two_last_days_period"

        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()

        drop_column_called_index(df_with_resulting_table_of_certain_models)
        st.dataframe(df_with_resulting_table_of_certain_models)

        # -------------------------
        #add select box with trading pair selection
        tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # index_of_trading_pair_to_select = trading_pair_to_select.index
        # st.write("index_of_trading_pair_to_select")
        # st.write(index_of_trading_pair_to_select)
        # button = st.button("Next trading pair")
        container = st.empty()
        # -------------------------
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

            plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                             table_name,
                                             index_of_trading_pair_to_select,
                                             trading_pair_to_select,
                                             df_with_resulting_table_of_certain_models,
                                             engine_for_ohlcv_data_for_stocks_0000,
                                             engine_for_ohlcv_low_volume_data_for_stocks_0000,height,width)



    if model=="New ATH within last two days":
        table_name="current_asset_had_ath_within_two_last_days_period"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()

        st.dataframe(df_with_resulting_table_of_certain_models)
        #-------------------------
        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        #-------------------------
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

            plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                             table_name,
                                             index_of_trading_pair_to_select,
                                             trading_pair_to_select,
                                             df_with_resulting_table_of_certain_models,
                                             engine_for_ohlcv_data_for_stocks_0000,
                                             engine_for_ohlcv_low_volume_data_for_stocks_0000,height,width)


    if model=="Breakout of ATL with position entry next day after breakout":
        table_name="current_breakout_situations_of_atl_position_entry_next_day"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        st.dataframe(df_with_resulting_table_of_certain_models)

        #
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models,  names='exchange', title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # -------------------------

        tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select=\
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                                                label="Select a trading pair to plot")

        index_of_trading_pair_to_select1=string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1=int(index_of_trading_pair_to_select1)

        trading_pair_to_select2=string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)


    if model=="Breakout of ATH with position entry next day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_next_day"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange=\
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        #
        #
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Breakout of ATL with position entry on second day after breakout":
        table_name="current_breakout_situations_of_atl_position_entry_on_day_two"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Breakout of ATH with position entry on second day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_on_day_two"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="False Breakout of ATL by one bar":
        table_name="current_false_breakout_of_atl_by_one_bar"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="False Breakout of ATH by one bar":
        table_name="current_false_breakout_of_ath_by_one_bar"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="False Breakout of ATL by two bars":
        table_name="current_false_breakout_of_atl_by_two_bars"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="False Breakout of ATH by two bars":
        table_name="current_false_breakout_of_ath_by_two_bars"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Rebound off ATL":
        table_name="current_rebound_situations_from_atl"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        #     st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        #     st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Rebound off ATH":
        table_name="current_rebound_situations_from_ath"
        df_with_resulting_table_of_certain_models=pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models=\
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        # # plot piechart with exchange share
        # fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
        #              title="Share of exchanges where this bfr model is found")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_technical
        # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_technical',
        #                  title="max_profit_target_multiple_when_sl_technical")
        # st.plotly_chart(fig)
        # # plot piechart with max_profit_target_multiple_when_sl_calculated
        # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        #     fig = px.pie(df_with_resulting_table_of_certain_models,
        #                  names='max_profit_target_multiple_when_sl_calculated',
        #                  title="max_profit_target_multiple_when_sl_calculated")
        # st.plotly_chart(fig)
        # # -------------------------
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        # ##############################3
        # # -------------------------
        # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
        #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        #     plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                      engine_for_ohlcv_data_for_stocks_0000,
        #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Last close price is closer to ATL than n %ATR":
        table_name="current_asset_approaches_its_atl_closer_than_n_percent_atr"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        #
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        # plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
        #                                  table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                  engine_for_ohlcv_data_for_stocks_0000,
        #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model=="Last close price is closer to ATH than n %ATR":
        table_name="current_asset_approaches_its_ath_closer_than_n_percent_atr"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        #
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        # plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                  engine_for_ohlcv_data_for_stocks_0000,
        #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model == "Last close price is closer to ATL than N % of ATR(30)":
        table_name = "from_close_to_atl_less_than_n_of_atr_and_has_less_than_n_days"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        #
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        # plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
        #                                  table_name,
        #                                  index_of_trading_pair_to_select,
        #                                  trading_pair_to_select,
        #                                  df_with_resulting_table_of_certain_models,
        #                                  engine_for_ohlcv_data_for_stocks_0000,
        #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
    if model == "Last close price is closer to ATH than N % of ATR(30)":
        table_name = "from_close_to_ath_less_than_n_of_atr_and_has_less_than_n_days"
        df_with_resulting_table_of_certain_models = pd.DataFrame()
        try:
            df_with_resulting_table_of_certain_models = \
                return_df_from_postgres_sql_table(table_name,
                                                  engine_for_db_intermediate_db_for_storing_selected_pairs_from_form)
        except ProgrammingError:
            st.write(f"There is no '{model}' for today")
            st.stop()
        # st.dataframe(df_with_resulting_table_of_certain_models)
        #
        # # -------------------------
        # #add select box with trading pair selection
        # tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
        # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
        # # -------------------------
        # # -------------------------
        # # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
        #
        # plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
        #                                  table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
        #                                  engine_for_ohlcv_data_for_stocks_0000,
        #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
        # -------------------------
        # tuple_of_trading_pairs_with_exchange = \
        #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
        ##############################3
        string_index_in_tuple_double_underscore_trading_pair_to_select_list = []
        # number_of_items_in_tuple_of_trading_pairs_with_exchange=len(tuple_of_trading_pairs_with_exchange)
        for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            string_index_in_tuple_double_underscore_trading_pair_to_select = f"{index_of_trading_pair_to_select}__{trading_pair_to_select}"
            string_index_in_tuple_double_underscore_trading_pair_to_select_list.append(
                string_index_in_tuple_double_underscore_trading_pair_to_select)

        string_index_in_tuple_double_underscore_trading_pair_to_select = \
            st.sidebar.radio(options=string_index_in_tuple_double_underscore_trading_pair_to_select_list,
                             label="Select a trading pair to plot")

        index_of_trading_pair_to_select1 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[0]
        index_of_trading_pair_to_select1 = int(index_of_trading_pair_to_select1)

        trading_pair_to_select2 = string_index_in_tuple_double_underscore_trading_pair_to_select.split("__")[1]

        df_with_resulting_table_of_certain_models.index = range(len(df_with_resulting_table_of_certain_models))
        plot_multiple_charts_on_one_page(connection_to_db_intermediate_db_for_storing_selected_pairs_from_form,
                                         table_name,
                                         index_of_trading_pair_to_select1,
                                         trading_pair_to_select2,
                                         df_with_resulting_table_of_certain_models,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)




if __name__=="__main__":
    streamlit_func()