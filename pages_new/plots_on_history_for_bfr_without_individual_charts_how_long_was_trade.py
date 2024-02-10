import threading
import random
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
import uuid
from plotly.subplots import make_subplots
import plotly.express as px

def number_of_trades_in_max_drawdown_longest_drawdown_start_and_longest_drawdown_end(df_with_resulting_table_of_certain_models,
                                                                         longest_drawdown_start,
                                                                         longest_drawdown_end):
    # Count the values falling between the start and end timestamps
    number_of_trades_in_max_drawdown = df_with_resulting_table_of_certain_models[
        (df_with_resulting_table_of_certain_models['timestamp_of_order_placement_bar'] >= longest_drawdown_start) &
        (df_with_resulting_table_of_certain_models['timestamp_of_order_placement_bar'] <= longest_drawdown_end)
        ].shape[0]
    return number_of_trades_in_max_drawdown
def calculate_max_drawdown_drawdown_beginning_and_end_dates_num_trades_in_drawdown_sl_technical(
        df_with_resulting_table_of_certain_models,
        risk_percent_value,
        tp_value):
    # Calculate the cumulative maximum of the deposit values
    df_with_resulting_table_of_certain_models['cumulative_max'] = df_with_resulting_table_of_certain_models[
        'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_technical'.format(risk_percent_value,
                                                                                      tp_value)].cummax()

    # st.write("df_with_resulting_table_of_certain_models['cumulative_max']")
    # st.write(df_with_resulting_table_of_certain_models['cumulative_max'])
    # print("df_with_resulting_table_of_certain_models['cumulative_max']")
    # print(df_with_resulting_table_of_certain_models['cumulative_max'])
    # print("risk_percent_value")
    # print(risk_percent_value)
    # print("tp_value")
    # print(tp_value)

    # Calculate the drawdown as the difference between the deposit value and the cumulative maximum
    df_with_resulting_table_of_certain_models['drawdown'] = df_with_resulting_table_of_certain_models[
                                                                'cumulative_max'] - \
                                                            df_with_resulting_table_of_certain_models[
                                                                'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_technical'.format(
                                                                    risk_percent_value, tp_value)]

    # Creating a new column for percentage drawdown
    df_with_resulting_table_of_certain_models['percentage_drawdown'] = \
        (df_with_resulting_table_of_certain_models['cumulative_max'] -
         df_with_resulting_table_of_certain_models[
             'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_technical'.format(risk_percent_value, tp_value)]
         ) / df_with_resulting_table_of_certain_models['cumulative_max'] * 100


    st.write("df_with_resulting_table_of_certain_models['drawdown']_sl_technical")
    st.write(df_with_resulting_table_of_certain_models['drawdown'])
    st.write("df_with_resulting_table_of_certain_models['cumulative_max']_sl_technical")
    st.write(df_with_resulting_table_of_certain_models['cumulative_max'])
    print("df_with_resulting_table_of_certain_models['drawdown']")
    print(df_with_resulting_table_of_certain_models['drawdown'])

    # Identify the maximum drawdown and its related details
    max_drawdown = df_with_resulting_table_of_certain_models['drawdown'].max()
    abs_max_drawdown = abs(max_drawdown)
    max_drawdown_percentage = (abs_max_drawdown / df_with_resulting_table_of_certain_models[
        'cumulative_max'].max()) * 100

    # Find start and end dates of the drawdown
    drawdown_date_when_drawdawn_is_max_unix_timestamp = df_with_resulting_table_of_certain_models.loc[
        df_with_resulting_table_of_certain_models['drawdown'].idxmax(), 'timestamp_of_order_placement_bar']
    drawdown_begin_date_unix_timestamp = df_with_resulting_table_of_certain_models.loc[
        df_with_resulting_table_of_certain_models['cumulative_max'].idxmax(), 'timestamp_of_order_placement_bar']

    drawdown_begin_date = datetime.datetime.fromtimestamp(drawdown_begin_date_unix_timestamp)
    drawdown_date_when_drawdawn_is_max = datetime.datetime.fromtimestamp(drawdown_date_when_drawdawn_is_max_unix_timestamp)

    # Count number of trades in the drawdown
    num_trades_in_drawdowns = \
    df_with_resulting_table_of_certain_models.loc[df_with_resulting_table_of_certain_models['drawdown'] > 0].shape[0]

    # Print the results
    print("Absolute Maximum Drawdown when sl_technical:", abs_max_drawdown)
    print("Percentage Maximum Drawdown when sl_technical:", max_drawdown_percentage)
    print("Drawdown Begin Date when sl_technical:", drawdown_begin_date)
    print("drawdown_date_when_drawdawn_is_max when sl_technical:", drawdown_date_when_drawdawn_is_max)
    print("Number of Trades in all Drawdowns when sl_technical:", num_trades_in_drawdowns)

    # Step 1: Create a mask to identify consecutive zeros in the drawdown column
    mask = ((df_with_resulting_table_of_certain_models['drawdown'] == 0) &
            (df_with_resulting_table_of_certain_models['drawdown'].shift(-1) > 0))

    # Step 2: Find the indices of consecutive zeros
    consecutive_zero_indices = df_with_resulting_table_of_certain_models[mask].index.tolist()

    # Step 3: Calculate the periods of consecutive zeros
    drawdown_periods = []
    for i in range(1, len(consecutive_zero_indices)):
        start_date = df_with_resulting_table_of_certain_models.loc[
            consecutive_zero_indices[i - 1], 'timestamp_of_order_placement_bar']
        end_date = df_with_resulting_table_of_certain_models.loc[
            consecutive_zero_indices[i], 'timestamp_of_order_placement_bar']
        drawdown_period_length = (end_date - start_date) / (60 * 60 * 24)  # Convert to days
        drawdown_periods.append((start_date, end_date, drawdown_period_length))

    # Step 4: Determine the longest drawdown period
    longest_drawdown=np.nan
    longest_drawdown_days=np.nan
    if len(drawdown_periods)>0:
        longest_drawdown = max(drawdown_periods, key=lambda x: x[2])
        longest_drawdown_start, longest_drawdown_end, longest_drawdown_days = longest_drawdown
    else:
        # longest_drawdown=len((df_with_resulting_table_of_certain_models['drawdown']))
        longest_drawdown_start=df_with_resulting_table_of_certain_models.loc[0, 'timestamp_of_order_placement_bar']
        longest_drawdown_end=df_with_resulting_table_of_certain_models.loc[len(df_with_resulting_table_of_certain_models)-1, 'timestamp_of_order_placement_bar']
        longest_drawdown_days=len((df_with_resulting_table_of_certain_models['drawdown']))

    number_of_trades_in_max_drawdown = number_of_trades_in_max_drawdown_longest_drawdown_start_and_longest_drawdown_end(
        df_with_resulting_table_of_certain_models,
        longest_drawdown_start,
        longest_drawdown_end)
    st.write(f"number_of_trades_in_max_drawdown when sl is technical={number_of_trades_in_max_drawdown}")

    # Output the results
    print(
        f"The longest drawdown period when sl_technical starts from {pd.to_datetime(longest_drawdown_start, unit='s')}, ends on {pd.to_datetime(longest_drawdown_end, unit='s')}, and lasts {longest_drawdown_days} days.")

    # Output the results
    st.write(f"The longest drawdown period when sl_technical starts from {pd.to_datetime(longest_drawdown_start, unit='s')}, ends on {pd.to_datetime(longest_drawdown_end, unit='s')}, and lasts {longest_drawdown_days} days.")

    return df_with_resulting_table_of_certain_models, abs_max_drawdown,max_drawdown_percentage,drawdown_begin_date,drawdown_date_when_drawdawn_is_max,num_trades_in_drawdowns
def calculate_max_drawdown_drawdown_beginning_and_end_dates_num_trades_in_drawdown_sl_calculated(
        df_with_resulting_table_of_certain_models,
        risk_percent_value,
        tp_value):
    # Calculate the cumulative maximum of the deposit values
    df_with_resulting_table_of_certain_models['cumulative_max'] = df_with_resulting_table_of_certain_models[
        'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_calculated'.format(risk_percent_value,
                                                                                     tp_value)].cummax()

    st.write("df_with_resulting_table_of_certain_models['cumulative_max']_sl_calculated")
    st.write(df_with_resulting_table_of_certain_models['cumulative_max'])
    st.write("df_with_resulting_table_of_certain_models['drawdown']_sl_calculated")
    st.write(df_with_resulting_table_of_certain_models['drawdown'])
    print("df_with_resulting_table_of_certain_models['cumulative_max']")
    print(df_with_resulting_table_of_certain_models['cumulative_max'])
    print("risk_percent_value")
    print(risk_percent_value)
    print("tp_value")
    print(tp_value)

    # Calculate the drawdown as the difference between the deposit value and the cumulative maximum
    df_with_resulting_table_of_certain_models['drawdown'] = df_with_resulting_table_of_certain_models[
                                                                'cumulative_max'] - \
                                                            df_with_resulting_table_of_certain_models[
                                                                'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_calculated'.format(
                                                                    risk_percent_value, tp_value)]

    # Creating a new column for percentage drawdown
    df_with_resulting_table_of_certain_models['percentage_drawdown'] = \
        (df_with_resulting_table_of_certain_models['cumulative_max'] -
         df_with_resulting_table_of_certain_models[
             'deposit_by_end_of_period_with_risk_{}_and_tp_{}_to_one_sl_calculated'.format(risk_percent_value, tp_value)]
         ) / df_with_resulting_table_of_certain_models['cumulative_max'] * 100

    # st.write("df_with_resulting_table_of_certain_models['drawdown']")
    # st.write(df_with_resulting_table_of_certain_models['drawdown'])
    print("df_with_resulting_table_of_certain_models['drawdown']")
    print(df_with_resulting_table_of_certain_models['drawdown'])

    # Identify the maximum drawdown and its related details
    max_drawdown = df_with_resulting_table_of_certain_models['drawdown'].max()
    abs_max_drawdown = abs(max_drawdown)
    max_drawdown_percentage = (abs_max_drawdown / df_with_resulting_table_of_certain_models[
        'cumulative_max'].max()) * 100

    # Find start and end dates of the drawdown
    drawdown_date_when_drawdawn_is_max_unix_timestamp = df_with_resulting_table_of_certain_models.loc[
        df_with_resulting_table_of_certain_models['drawdown'].idxmax(), 'timestamp_of_order_placement_bar']
    drawdown_begin_date_unix_timestamp = df_with_resulting_table_of_certain_models.loc[
        df_with_resulting_table_of_certain_models['cumulative_max'].idxmax(), 'timestamp_of_order_placement_bar']

    drawdown_begin_date = datetime.datetime.fromtimestamp(drawdown_begin_date_unix_timestamp)
    drawdown_date_when_drawdawn_is_max = datetime.datetime.fromtimestamp(
        drawdown_date_when_drawdawn_is_max_unix_timestamp)

    # Count number of trades in the drawdown
    num_trades_in_drawdowns = \
        df_with_resulting_table_of_certain_models.loc[df_with_resulting_table_of_certain_models['drawdown'] > 0].shape[
            0]



    # Print the results
    print("Absolute Maximum Drawdown when sl_calculated:", abs_max_drawdown)
    print("Percentage Maximum Drawdown when sl_calculated:", max_drawdown_percentage)
    print("Drawdown Begin Date when sl_calculated:", drawdown_begin_date)
    print("drawdown_date_when_drawdawn_is_max when sl_calculated:", drawdown_date_when_drawdawn_is_max)
    print("Number of Trades in all Drawdowns when sl_calculated:", num_trades_in_drawdowns)

    # Step 1: Create a mask to identify consecutive zeros in the drawdown column
    mask = ((df_with_resulting_table_of_certain_models['drawdown'] == 0) &
            (df_with_resulting_table_of_certain_models['drawdown'].shift(-1) > 0))

    # Step 2: Find the indices of consecutive zeros
    consecutive_zero_indices = df_with_resulting_table_of_certain_models[mask].index.tolist()
    st.write("consecutive_zero_indices")
    st.write(consecutive_zero_indices)

    # Step 3: Calculate the periods of consecutive zeros
    drawdown_periods = []
    for i in range(1, len(consecutive_zero_indices)):
        start_date = df_with_resulting_table_of_certain_models.loc[
            consecutive_zero_indices[i - 1], 'timestamp_of_order_placement_bar']
        end_date = df_with_resulting_table_of_certain_models.loc[
            consecutive_zero_indices[i], 'timestamp_of_order_placement_bar']
        drawdown_period_length = (end_date - start_date) / (60 * 60 * 24)  # Convert to days
        drawdown_periods.append((start_date, end_date, drawdown_period_length))

    # Step 4: Determine the longest drawdown period
    longest_drawdown = np.nan
    longest_drawdown_days = np.nan
    if len(drawdown_periods) > 0:
        longest_drawdown = max(drawdown_periods, key=lambda x: x[2])
        longest_drawdown_start, longest_drawdown_end, longest_drawdown_days = longest_drawdown
    else:
        # longest_drawdown=len((df_with_resulting_table_of_certain_models['drawdown']))
        longest_drawdown_start = df_with_resulting_table_of_certain_models.loc[
            0, 'timestamp_of_order_placement_bar']
        longest_drawdown_end = df_with_resulting_table_of_certain_models.loc[
            len(df_with_resulting_table_of_certain_models) - 1, 'timestamp_of_order_placement_bar']
        longest_drawdown_days = len((df_with_resulting_table_of_certain_models['drawdown']))


    number_of_trades_in_max_drawdown = number_of_trades_in_max_drawdown_longest_drawdown_start_and_longest_drawdown_end(
        df_with_resulting_table_of_certain_models,
        longest_drawdown_start,
        longest_drawdown_end)
    st.write(f"number_of_trades_in_max_drawdown when sl is calculated={number_of_trades_in_max_drawdown}")

    # Output the results
    print(
        f"The longest drawdown period when sl_calculated starts from {pd.to_datetime(longest_drawdown_start, unit='s')}, ends on {pd.to_datetime(longest_drawdown_end, unit='s')}, and lasts {longest_drawdown_days} days.")

    # Output the results
    st.write(
        f"The longest drawdown period when sl_calculated starts from {pd.to_datetime(longest_drawdown_start, unit='s')}, ends on {pd.to_datetime(longest_drawdown_end, unit='s')}, and lasts {longest_drawdown_days} days.")

    return df_with_resulting_table_of_certain_models, abs_max_drawdown, max_drawdown_percentage, drawdown_begin_date, drawdown_date_when_drawdawn_is_max, num_trades_in_drawdowns


@st.cache_data
def get_ohlcv_df_for_btc_usdt_on_gateio(_engine_for_ohlcv_data_for_stocks_0000):
    entire_ohlcv_df = \
        pd.read_sql_query(f'''select * from "BTC_USDT_on_gateio"''',
                          _engine_for_ohlcv_data_for_stocks_0000)
    return entire_ohlcv_df

def create_column_in_df_called_number_of_order_placement_within_next_and_prev_n_days(df_with_resulting_table_of_certain_models,
                                                                                     number_of_prev_and_next_days):
    # Assuming the column 'timestamp_of_order_placement_bar' contains Unix timestamps in seconds
    # Convert the timestamp to datetime
    df_with_resulting_table_of_certain_models['human_datetime_of_order_placement_bar'] = pd.to_datetime(
        df_with_resulting_table_of_certain_models['timestamp_of_order_placement_bar'], unit='s')

    # Sort the dataframe by the timestamp column (in case it's not already sorted)
    df_with_resulting_table_of_certain_models = df_with_resulting_table_of_certain_models.sort_values(
        'human_datetime_of_order_placement_bar')

    # Define a function to calculate the number of orders within the previous and next 15 days
    def calculate_orders_within_n_days(timestamp, df):
        prev_n_days = timestamp - pd.Timedelta(days=number_of_prev_and_next_days)
        next_n_days = timestamp + pd.Timedelta(days=number_of_prev_and_next_days)
        return ((df['human_datetime_of_order_placement_bar'] >= prev_n_days) &
                (df['human_datetime_of_order_placement_bar'] <= next_n_days)).sum()

    # st.write("df_with_resulting_table_of_certain_models1")
    # st.dataframe(df_with_resulting_table_of_certain_models)

    # Apply the function to each row to calculate the number of orders within the previous and next 15 days
    df_with_resulting_table_of_certain_models[
        'number_of_order_placement_within_next_and_prev_n_days'] = df_with_resulting_table_of_certain_models.apply(
        lambda row: calculate_orders_within_n_days(row['human_datetime_of_order_placement_bar'],
                                                    df_with_resulting_table_of_certain_models), axis=1)

    # st.write("df_with_resulting_table_of_certain_models2")
    # st.dataframe(df_with_resulting_table_of_certain_models)

    # Now the new column 'number_of_order_placement_within_next_and_prev_n_days' contains the desired values

    return df_with_resulting_table_of_certain_models

def convert_unix_timestamp_to_date(unix_timestamp):
    # Convert the unix timestamp to a datetime object
    date = datetime.datetime.utcfromtimestamp(unix_timestamp)

    # Format the datetime object as a string in a desired format
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date
def plot_for_each_period_separate_charts(sql_query_part_whether_to_consider_suppression_by_highs_or_lows,table_name,
                                                 min_volume_in_usd_over_last_n_days,
                                                 buy_or_sell_order_was_touched,
                                                 max_distance_between_technical_sl_order_in_atr,
                                                 min_distance_between_technical_sl_order_in_atr,
                                                 sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available,
                                                 max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched,
                                                 exchange_conditions,
                                                 number_of_exchanges_where_ath_or_atl_were_broken,
                                                 engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 how_many_months_for_plotting_and_calculating_of_stats,
                                         initial_funds_for_performance_calculation_over_given_period,
                                         take_profit_for_performance_calculation_over_given_period,
                                         risk_for_one_trade_in_usd,
                                         model,
                                         engine_for_ohlcv_data_for_stocks_0000,
                                         engine_for_ohlcv_low_volume_data_for_stocks_0000,
                                         connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,number_of_split_periods_to_plot):

    half_year_periods_dict=get_dict_with_timestamps_with_equal_duration(table_name,
                                                 min_volume_in_usd_over_last_n_days,
                                                 buy_or_sell_order_was_touched,
                                                 max_distance_between_technical_sl_order_in_atr,
                                                 min_distance_between_technical_sl_order_in_atr,
                                                 sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available,
                                                 max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched,
                                                 exchange_conditions,
                                                 number_of_exchanges_where_ath_or_atl_were_broken,
                                                 engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 how_many_months_for_plotting_and_calculating_of_stats)

    for number_of_time_period_one_means_the_most_recent in half_year_periods_dict:
        # Draw a wide horizontal line using HTML
        st.markdown("<hr style='border: 2px solid #42f5ef'>", unsafe_allow_html=True)
        st.write(number_of_time_period_one_means_the_most_recent)
        st.write(convert_unix_timestamp_to_date(half_year_periods_dict[number_of_time_period_one_means_the_most_recent][1]))
        st.write(convert_unix_timestamp_to_date(half_year_periods_dict[number_of_time_period_one_means_the_most_recent][0]))


        if number_of_time_period_one_means_the_most_recent>number_of_split_periods_to_plot:
            continue


        query = f'''SELECT *
                                    FROM public."{table_name}"
                                    WHERE (base, timestamp_of_bsu, min_volume_in_usd_over_last_n_days) IN (
                                        SELECT base, timestamp_of_bsu, MAX(min_volume_in_usd_over_last_n_days)
                                        FROM public."{table_name}"
                                        GROUP BY base, timestamp_of_bsu
                                    )
                                    AND min_volume_in_usd_over_last_n_days >= {min_volume_in_usd_over_last_n_days}
                                    AND distance_between_technical_sl_order_in_atr<= {max_distance_between_technical_sl_order_in_atr}
                                    AND distance_between_technical_sl_order_in_atr>= {min_distance_between_technical_sl_order_in_atr}
                                    AND buy_or_sell_order_was_touched = {buy_or_sell_order_was_touched}
                                    {sql_query_part_whether_to_consider_suppression_by_highs_or_lows}
                                    {sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available} AND
                                    max_distance_from_level_price_in_this_bar_in_atr <= {max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched}
                                    and exchange IN ({exchange_conditions}) and number_of_exchanges_where_ath_or_atl_were_broken_int <= {number_of_exchanges_where_ath_or_atl_were_broken}
                                    and timestamp_of_order_placement_bar BETWEEN {half_year_periods_dict[number_of_time_period_one_means_the_most_recent][1]} AND {half_year_periods_dict[number_of_time_period_one_means_the_most_recent][0]};'''

        # st.write("half_year_periods")
        # st.write(half_year_periods)

        # print("query1")
        # print(query)
        #
        # st.write(query)

        width = 1500
        height = 1000

        width_of_pie_chart=700
        height_of_pie_chart=700

        if model == "New ATL within last two days":
            table_name = "current_asset_had_atl_within_two_last_days_period"

            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()

            drop_column_called_index(df_with_resulting_table_of_certain_models)
            st.dataframe(df_with_resulting_table_of_certain_models)

            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # index_of_trading_pair_to_select = trading_pair_to_select.index
            # st.write("index_of_trading_pair_to_select")
            # st.write(index_of_trading_pair_to_select)
            # button = st.button("Next trading pair")

            # -------------------------
            for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 table_name,
                                                 index_of_trading_pair_to_select,
                                                 trading_pair_to_select,
                                                 df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        if model == "New ATH within last two days":
            table_name = "current_asset_had_ath_within_two_last_days_period"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()

            st.dataframe(df_with_resulting_table_of_certain_models)
            # -------------------------
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 table_name, index_of_trading_pair_to_select, trading_pair_to_select,
                                                 df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        if model == "Breakout of ATL with position entry next day after breakout":
            table_name = "current_breakout_situations_of_atl_position_entry_next_day"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)

            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

            # -------------------------

            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,
            #                                      trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)

        if model == "Breakout of ATH with position entry next day after breakout":
            table_name = "current_breakout_situations_of_ath_position_entry_next_day"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            # #############################3
            # # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            #
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "Breakout of ATL with position entry on second day after breakout":
            table_name = "current_breakout_situations_of_atl_position_entry_on_day_two"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "Breakout of ATH with position entry on second day after breakout":
            table_name = "current_breakout_situations_of_ath_position_entry_on_day_two"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "False Breakout of ATL by one bar":
            table_name = "current_false_breakout_of_atl_by_one_bar"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "False Breakout of ATH by one bar":
            table_name = "current_false_breakout_of_ath_by_one_bar"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "False Breakout of ATL by two bars":
            table_name = "current_false_breakout_of_atl_by_two_bars"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "False Breakout of ATH by two bars":
            table_name = "current_false_breakout_of_ath_by_two_bars"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "Rebound off ATL":
            table_name = "current_rebound_situations_from_atl"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.write("df_with_resulting_table_of_certain_models")
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart)

                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
        if model == "Rebound off ATH":
            table_name = "current_rebound_situations_from_ath"
            df_with_resulting_table_of_certain_models = pd.DataFrame()
            try:
                df_with_resulting_table_of_certain_models = \
                    return_df_from_postgres_sql_table(query, table_name,
                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                              initial_funds_for_performance_calculation_over_given_period,
                                              take_profit_for_performance_calculation_over_given_period,
                                              risk_for_one_trade_in_usd)
            except ProgrammingError:
                st.write(f"There is no '{model}' for today")
                st.stop()
            st.dataframe(df_with_resulting_table_of_certain_models)
            # plot piechart with exchange share
            fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                         title="Share of exchanges where this bfr model is found")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                autosize=False,
                width=width_of_pie_chart,
                height=height_of_pie_chart
            )
            st.plotly_chart(fig)
            # plot piechart with max_profit_target_multiple_when_sl_technical
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_technical',
                             title="max_profit_target_multiple_when_sl_technical")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

            # plot piechart with max_profit_target_multiple_when_sl_calculated
            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                fig = px.pie(df_with_resulting_table_of_certain_models,
                             names='max_profit_target_multiple_when_sl_calculated',
                             title="max_profit_target_multiple_when_sl_calculated")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)

                filtered_df = df_with_resulting_table_of_certain_models.loc[
                    df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                fig = px.pie(filtered_df, names='exchange',
                             title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=width_of_pie_chart,
                    height=height_of_pie_chart
                )
                st.plotly_chart(fig)
            # -------------------------
            # -------------------------
            # add select box with trading pair selection
            tuple_of_trading_pairs_with_exchange = tuple(df_with_resulting_table_of_certain_models['ticker'])
            # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
            # -------------------------
            # -------------------------
            # tuple_of_trading_pairs_with_exchange = \
            #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
            ##############################3
            # -------------------------
            # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
            #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
            #
            #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
def get_dict_with_timestamps_with_equal_duration(table_name,
                                                 min_volume_in_usd_over_last_n_days,
                                                 buy_or_sell_order_was_touched,
                                                 max_distance_between_technical_sl_order_in_atr,
                                                 min_distance_between_technical_sl_order_in_atr,
                                                 sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available,
                                                 max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched,
                                                 exchange_conditions,
                                                 number_of_exchanges_where_ath_or_atl_were_broken,
                                                 engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 how_many_months_for_plotting_and_calculating_of_stats):
    query_for_plotting_charts_with_separate_periods_of_time = f'''SELECT *
                                            FROM public."{table_name}"
                                            WHERE (base, timestamp_of_bsu, min_volume_in_usd_over_last_n_days) IN (
                                                SELECT base, timestamp_of_bsu, MAX(min_volume_in_usd_over_last_n_days)
                                                FROM public."{table_name}"
                                                GROUP BY base, timestamp_of_bsu
                                            )
                                            AND min_volume_in_usd_over_last_n_days >= {min_volume_in_usd_over_last_n_days}
                                            AND buy_or_sell_order_was_touched = {buy_or_sell_order_was_touched}
                                            AND distance_between_technical_sl_order_in_atr<= {max_distance_between_technical_sl_order_in_atr}
                                            AND distance_between_technical_sl_order_in_atr>= {min_distance_between_technical_sl_order_in_atr}
                                            {sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available} AND
                                            max_distance_from_level_price_in_this_bar_in_atr <= {max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched}
                                            and exchange IN ({exchange_conditions}) and number_of_exchanges_where_ath_or_atl_were_broken_int <= {number_of_exchanges_where_ath_or_atl_were_broken};'''
    df_with_resulting_table_of_certain_models_for_plotting_charts_with_separate_periods_of_time = \
        return_df_from_postgres_sql_table(query_for_plotting_charts_with_separate_periods_of_time, table_name,
                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
    min_timestamp = df_with_resulting_table_of_certain_models_for_plotting_charts_with_separate_periods_of_time[
        'timestamp_of_order_placement_bar'].min()
    max_timestamp = df_with_resulting_table_of_certain_models_for_plotting_charts_with_separate_periods_of_time[
        'timestamp_of_order_placement_bar'].max()

    # Convert the Unix timestamps to datetime objects
    min_datetime = pd.to_datetime(min_timestamp, unit='s')
    max_datetime = pd.to_datetime(max_timestamp, unit='s')

    # Initialize the dictionary to hold the results
    half_year_periods = {}

    # Calculate the range of half-year periods
    num_half_years = (max_datetime.year - min_datetime.year) * 2 + (
            max_datetime.month - min_datetime.month) // how_many_months_for_plotting_and_calculating_of_stats
    num_half_years = max(1, num_half_years)  # Ensure there's at least one half-year period

    # Calculate and store the half-year periods in the dictionary
    for i in range(1, num_half_years + 1):
        key = i
        period_start = max_datetime - pd.DateOffset(months=how_many_months_for_plotting_and_calculating_of_stats * i)
        previous_period_start = max_datetime - pd.DateOffset(
            months=how_many_months_for_plotting_and_calculating_of_stats * (i + 1))
        half_year_periods[key] = [int(period_start.timestamp()), int(previous_period_start.timestamp())]

    return half_year_periods

def plot_three_charts(number_of_time_period_one_means_the_most_recent,half_year_periods_dict,engine_for_ohlcv_data_for_stocks_0000,
                                  df_with_resulting_table_of_certain_models,
                                  initial_funds_for_performance_calculation_over_given_period,
                                  initial_take_profit_for_performance_calculation_over_given_period,
                                  risk_for_one_trade_in_usd):
    # Draw a wide horizontal line using HTML
    st.markdown("<hr style='border: 2px solid #42f5ef'>", unsafe_allow_html=True)

    deposit_by_the_end_of_the_given_period_if_sl_is_technical=initial_funds_for_performance_calculation_over_given_period
    deposit_by_the_end_of_the_given_period_if_sl_is_calculated=initial_funds_for_performance_calculation_over_given_period
    # deposit_by_the_end_of_the_given_period_if_sl_is_technical_and_calculated_df=pd.DataFrame(columns=["deposit_by_the_end_of_the_given_period_if_sl_is_technical",
    #                                                                                    "deposit_by_the_end_of_the_given_period_if_sl_is_calculated"])
    # Create an empty list to store the dictionaries

    left_date=convert_unix_timestamp_to_date(half_year_periods_dict[number_of_time_period_one_means_the_most_recent][1])
    right_date=convert_unix_timestamp_to_date(half_year_periods_dict[number_of_time_period_one_means_the_most_recent][0])


    width_of_line_chart=1000
    height_of_line_chart=800
    data_sl_technical = []
    data_sl_calculated = []
    risk_percent_list =[5,4,3,2,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1]
    # Define the number of rows
    num_rows = 101
    # Initialize empty DataFrames
    deposit_by_the_end_of_the_given_period_if_sl_is_technical_df = pd.DataFrame()
    deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df = pd.DataFrame()
    # Create DataFrames for the specified number of rows
    for risk_percent_value in risk_percent_list:
        df_technical = pd.DataFrame({f"deposit_risk_{risk_percent_value}%_sl_is_technical": [np.nan] * num_rows})
        df_calculated = pd.DataFrame({f"deposit_risk_{risk_percent_value}%_sl_is_calculated": [np.nan] * num_rows})
        deposit_by_the_end_of_the_given_period_if_sl_is_technical_df = pd.concat(
            [deposit_by_the_end_of_the_given_period_if_sl_is_technical_df, df_technical], axis=1)
        deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df = pd.concat(
            [deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df, df_calculated], axis=1)

    # # Create the DataFrame from the list of dictionaries
    # deposit_by_the_end_of_the_given_period_if_sl_is_technical_df = pd.DataFrame(data_sl_technical)
    # deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df = pd.DataFrame(data_sl_calculated)
    deposit_by_the_end_of_the_given_period_if_sl_is_technical_df["take_profit_value"]=\
        list(range(0,len(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df)))
    deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df["take_profit_value"] = \
        list(range(0, len(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df)))
    for risk_percent_value in risk_percent_list:
        risk_for_one_trade_in_usd=initial_funds_for_performance_calculation_over_given_period*risk_percent_value/100.0

        for take_profit_for_performance_calculation_over_given_period in range(initial_take_profit_for_performance_calculation_over_given_period,num_rows):
            if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                count_of_values_greater_than_or_equal_to_take_profit_for_performance_calculation_over_given_period = (
                            df_with_resulting_table_of_certain_models[
                                'max_profit_target_multiple_when_sl_technical'] >= take_profit_for_performance_calculation_over_given_period).sum()
                count_of_values_technical_stop_loss_is_reached = df_with_resulting_table_of_certain_models.technical_stop_loss_is_reached.sum()

                # Use conditional indexing to filter rows based on the value of technical_stop_loss_is_reached and then calculate the sum of taker_fee
                sum_of_taker_fees_where_stop_loss_is_reached = df_with_resulting_table_of_certain_models[
                    df_with_resulting_table_of_certain_models['technical_stop_loss_is_reached'] == True][
                    'taker_fee'].sum()

                # Define the condition for filtering
                condition1 = df_with_resulting_table_of_certain_models[
                                'max_profit_target_multiple_when_sl_technical'] >= take_profit_for_performance_calculation_over_given_period

                # Use conditional indexing to filter rows based on the defined condition and then calculate the sum of maker_fee
                sum_of_maker_fees_for_target_profit = df_with_resulting_table_of_certain_models[condition1][
                    'maker_fee'].sum()

                # st.write("sum_of_maker_fees_for_target_profit")
                # st.write(sum_of_maker_fees_for_target_profit)
                # st.write("sum_of_taker_fees_where_stop_loss_is_reached")
                # st.write(sum_of_taker_fees_where_stop_loss_is_reached)

                deposit_by_the_end_of_the_given_period_if_sl_is_technical = \
                    initial_funds_for_performance_calculation_over_given_period + \
                    count_of_values_greater_than_or_equal_to_take_profit_for_performance_calculation_over_given_period * \
                    take_profit_for_performance_calculation_over_given_period * \
                    risk_for_one_trade_in_usd - \
                    (count_of_values_technical_stop_loss_is_reached * risk_for_one_trade_in_usd) -\
                    sum_of_maker_fees_for_target_profit*risk_for_one_trade_in_usd-sum_of_taker_fees_where_stop_loss_is_reached*risk_for_one_trade_in_usd
                # st.write(f"deposit_by_the_end_of_the_given_period_if_sl_is_technical with risk={risk_for_one_trade_in_usd*100/initial_funds_for_performance_calculation_over_given_period}% from initial deposit")
                # st.write(deposit_by_the_end_of_the_given_period_if_sl_is_technical)

                condition = deposit_by_the_end_of_the_given_period_if_sl_is_technical_df[
                                'take_profit_value'] == take_profit_for_performance_calculation_over_given_period
                deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.loc[
                    condition, f"deposit_risk_{risk_percent_value}%_sl_is_technical"] = deposit_by_the_end_of_the_given_period_if_sl_is_technical
                # deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.loc[
                #     take_profit_for_performance_calculation_over_given_period, f"deposit_risk_{risk_percent_value}%_sl_is_technical"
                # ] = deposit_by_the_end_of_the_given_period_if_sl_is_technical



            if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                count_of_values_greater_than_or_equal_to_take_profit_for_performance_calculation_over_given_period = (
                            df_with_resulting_table_of_certain_models[
                                'max_profit_target_multiple_when_sl_calculated'] >= take_profit_for_performance_calculation_over_given_period).sum()
                count_of_values_calculated_stop_loss_is_reached = df_with_resulting_table_of_certain_models.calculated_stop_loss_is_reached.sum()

                # Use conditional indexing to filter rows based on the value of calculated_stop_loss_is_reached and then calculate the sum of taker_fee
                sum_of_taker_fees_where_stop_loss_is_reached = df_with_resulting_table_of_certain_models[
                    df_with_resulting_table_of_certain_models['calculated_stop_loss_is_reached'] == True][
                    'taker_fee'].sum()

                # Define the condition for filtering
                condition2 = df_with_resulting_table_of_certain_models[
                                 'max_profit_target_multiple_when_sl_calculated'] >= take_profit_for_performance_calculation_over_given_period

                # Use conditional indexing to filter rows based on the defined condition and then calculate the sum of maker_fee
                sum_of_maker_fees_for_target_profit = df_with_resulting_table_of_certain_models[condition2][
                    'maker_fee'].sum()

                # st.write("sum_of_maker_fees_for_target_profit")
                # st.write(sum_of_maker_fees_for_target_profit)
                # st.write("sum_of_taker_fees_where_stop_loss_is_reached")
                # st.write(sum_of_taker_fees_where_stop_loss_is_reached)

                deposit_by_the_end_of_the_given_period_if_sl_is_calculated = \
                    initial_funds_for_performance_calculation_over_given_period + \
                    count_of_values_greater_than_or_equal_to_take_profit_for_performance_calculation_over_given_period * \
                    take_profit_for_performance_calculation_over_given_period * \
                    risk_for_one_trade_in_usd - \
                    (count_of_values_calculated_stop_loss_is_reached * risk_for_one_trade_in_usd)-\
                    sum_of_maker_fees_for_target_profit*risk_for_one_trade_in_usd-sum_of_taker_fees_where_stop_loss_is_reached*risk_for_one_trade_in_usd

                deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df.loc[
                    take_profit_for_performance_calculation_over_given_period, f"deposit_risk_{risk_percent_value}%_sl_is_calculated"
                ] = deposit_by_the_end_of_the_given_period_if_sl_is_calculated

    # deposit_by_the_end_of_the_given_period_if_sl_is_technical_df["take_profit_value_new"] = \
    #     deposit_by_the_end_of_the_given_period_if_sl_is_technical_df["take_profit_value"]
    deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.set_index('take_profit_value',
                         inplace=True)
    deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df.set_index('take_profit_value',
                                                                           inplace=True)

    # fig1=None
    # for risk_percent_value in risk_percent_list:
    #     # st.line_chart(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df,
    #     #
        #               y=f"deposit_risk_{risk_percent_value}%_sl_is_technical")





    config = dict({'scrollZoom': True, 'displaylogo': False,
                   'modeBarButtonsToAdd': ['drawline', 'eraseshape']})
    # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
    #     # st.dataframe(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df)
    #     st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")
    #     fig = px.line(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df,
    #                       x=deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.index,
    #                       y=[deposit_by_the_end_of_the_given_period_if_sl_is_technical_df[f"deposit_risk_{risk_percent_value}%_sl_is_technical"] for risk_percent_value in risk_percent_list],
    #                   width=width_of_line_chart,height=height_of_line_chart,markers=True,title="deposit by end of given period when sl is technical")
    #
    #     st.plotly_chart(fig,config=config,use_container_width=True)
    #     # fig.show(config=config)
    # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
    #     # st.dataframe(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df)
    #     st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")
    #     fig1 = px.line(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df,
    #                       x=deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df.index,
    #                       y=[deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df[f"deposit_risk_{risk_percent_value}%_sl_is_calculated"] for risk_percent_value in risk_percent_list],
    #                   width=width_of_line_chart,height=height_of_line_chart,markers=True,title="deposit by end of given period when sl is calculated")
    #     st.plotly_chart(fig1,config=config,use_container_width=True)

    entire_ohlcv_df = \
        pd.read_sql_query(f'''select * from "BTC_USDT_on_gateio"''',
                          engine_for_ohlcv_data_for_stocks_0000)

    if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns or\
            "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=("BTC_USDT_on_gatio", "When SL is Technical", "When SL is Calculated"),vertical_spacing = 0.01,)

        # Add line chart for close price in the third subplot
        fig.add_trace(go.Scatter(x=entire_ohlcv_df["open_time"], y=entire_ohlcv_df['close'], mode='lines',
                                 name='Close Price of BTC'),
                      row=1, col=1)
        # Add vertical lines
        fig.add_trace(
            go.Scatter(x=[left_date, left_date], y=[min(entire_ohlcv_df['close']), max(entire_ohlcv_df['close'])],
                       mode='lines', name='Vertical Line 1', line=dict(color='red', width=3)), row=1, col=1)

        fig.add_trace(
            go.Scatter(x=[right_date, right_date], y=[min(entire_ohlcv_df['close']), max(entire_ohlcv_df['close'])],
                       mode='lines', name='Vertical Line 2', line=dict(color='blue', width=3)), row=1, col=1)

        for risk_percent_value in risk_percent_list:
            fig.add_trace(go.Scatter(x=deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.index,
                                     y=deposit_by_the_end_of_the_given_period_if_sl_is_technical_df[
                                         f"deposit_risk_{risk_percent_value}%_sl_is_technical"],
                                     mode='lines+markers',
                                     name=f"{risk_percent_value}% SL Technical"),
                          row=2, col=1)
            fig.add_trace(go.Scatter(x=deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df.index,
                                     y=deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df[
                                         f"deposit_risk_{risk_percent_value}%_sl_is_calculated"],
                                     mode='lines+markers',
                                     name=f"{risk_percent_value}% SL Calculated"),
                          row=3, col=1)


        fig.update_layout(height=height_of_line_chart * 3, width=width_of_line_chart,
                          title="Deposit by end of given period")

        # Narrow the gap between subplots

        st.plotly_chart(fig, use_container_width=True)




        # fig1.show(config=config)



    # st.bar_chart(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df,
    #              x=deposit_by_the_end_of_the_given_period_if_sl_is_technical_df['take_profit_value_new'],
    #               y=f"deposit_risk_0.2%_sl_is_technical")
    # st.dataframe(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df)
    return deposit_by_the_end_of_the_given_period_if_sl_is_technical,deposit_by_the_end_of_the_given_period_if_sl_is_calculated


def add_columns_to_dataframe(df, columns_to_create):
    for column_name in columns_to_create:
        # st.write("column_name")
        # st.write(column_name[0])
        # column_name=column_name
        df[f"{column_name}"] = None  # You can replace None with any default value you prefer
    return df

def add_columns_to_dataframe_without_performance_warning(df, columns_to_create):
    new_columns = {column_name: None for column_name in columns_to_create if column_name not in df.columns}
    df = pd.concat([df, pd.DataFrame(new_columns, index=df.index)], axis=1)
    return df
def plot_performance_for_each_risk_amount_percent_and_tp(table_name,
                                                         engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                         dict_of_identical_queries_for_each_table,
                                                         number_of_prev_and_next_days,
                                                         engine_for_ohlcv_data_for_stocks_0000,
                                  df_with_resulting_table_of_certain_models,
                                  initial_funds_for_performance_calculation_over_given_period,
                                  risk_for_one_trade_in_usd):
    width_of_line_chart = 1000
    height_of_line_chart = 800
    number_of_take_profits=list(range(3,5))

    risk_percent_list = [5, 4, 3, 2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    list_of_columns_to_create=[]
    for risk_percent_value in risk_percent_list:
        for tp_value in number_of_take_profits:
            column_to_create=[f"deposit_by_end_of_period_with_risk_{risk_percent_value}_and_tp_{tp_value}_to_one_sl_technical"]
            list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)

    for risk_percent_value in risk_percent_list:
        for tp_value in number_of_take_profits:
            column_to_create=[f"deposit_by_end_of_period_with_risk_{risk_percent_value}_and_tp_{tp_value}_to_one_sl_calculated"]
            list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)

    df_with_resulting_table_of_certain_models=df_with_resulting_table_of_certain_models.sort_values(by='timestamp_of_order_placement_bar')
    # Assuming df_with_resulting_table_of_certain_models is your DataFrame
    # Create a new index using range
    new_index = range(0, len(df_with_resulting_table_of_certain_models))

    # Set the new index for the DataFrame
    df_with_resulting_table_of_certain_models.index = new_index

    # st.write('df_with_resulting_table_of_certain_models_enhanced')
    # st.dataframe(df_with_resulting_table_of_certain_models)


    # Iterating over each row and selecting each row as a DataFrame
    for tp_value in number_of_take_profits:
        print("tp_value1")
        print(tp_value)
        for risk_percent_value1 in risk_percent_list:
            initial_deposit_for_this_risk_and_tp_sl_technical=initial_funds_for_performance_calculation_over_given_period
            initial_deposit_for_this_risk_and_tp_sl_calculated=initial_funds_for_performance_calculation_over_given_period
            risk_for_one_trade_in_usd=initial_funds_for_performance_calculation_over_given_period*risk_percent_value1/100.0
            for index, row in df_with_resulting_table_of_certain_models.iterrows():

                try:
                    # Convert the row data to a DataFrame if necessary
                    row_df = pd.DataFrame(row).transpose()

                    taker_fee = 0
                    if "taker_fee" in row_df.columns:
                        taker_fee = \
                            row_df.loc[index, "taker_fee"]
                        if pd.isna(taker_fee):
                            taker_fee=0

                    maker_fee = 0
                    if "maker_fee" in row_df.columns:
                        maker_fee = \
                            row_df.loc[index, "maker_fee"]
                        if pd.isna(maker_fee):
                            maker_fee=0

                    max_profit_target_multiple_when_sl_technical=np.nan
                    if "max_profit_target_multiple_when_sl_technical" in row_df.columns:
                        max_profit_target_multiple_when_sl_technical = \
                        row_df.loc[index, "max_profit_target_multiple_when_sl_technical"]
                        deposit_for_this_trade_sl_technical=np.nan
                        if max_profit_target_multiple_when_sl_technical >= tp_value:
                            deposit_for_this_trade_sl_technical = \
                                initial_deposit_for_this_risk_and_tp_sl_technical + tp_value * risk_for_one_trade_in_usd - maker_fee * risk_for_one_trade_in_usd
                            df_with_resulting_table_of_certain_models.loc[index,
                                f"deposit_by_end_of_period_with_risk_{risk_percent_value1}_and_tp_{tp_value}_to_one_sl_technical"] = deposit_for_this_trade_sl_technical


                        else:
                            deposit_for_this_trade_sl_technical=\
                                initial_deposit_for_this_risk_and_tp_sl_technical-risk_for_one_trade_in_usd - taker_fee * risk_for_one_trade_in_usd
                            df_with_resulting_table_of_certain_models.loc[index,
                            f"deposit_by_end_of_period_with_risk_{risk_percent_value1}_and_tp_{tp_value}_to_one_sl_technical"] = deposit_for_this_trade_sl_technical

                        initial_deposit_for_this_risk_and_tp_sl_technical = deposit_for_this_trade_sl_technical
                        print(f"deposit_for_this_trade_sl_technical for {index}")
                        print(deposit_for_this_trade_sl_technical)


                    max_profit_target_multiple_when_sl_calculated = np.nan
                    if "max_profit_target_multiple_when_sl_calculated" in row_df.columns:
                        max_profit_target_multiple_when_sl_calculated = \
                            row_df.loc[index, "max_profit_target_multiple_when_sl_calculated"]
                        deposit_for_this_trade_sl_calculated = np.nan
                        if max_profit_target_multiple_when_sl_calculated >= tp_value:
                            deposit_for_this_trade_sl_calculated = \
                                initial_deposit_for_this_risk_and_tp_sl_calculated + tp_value * risk_for_one_trade_in_usd - maker_fee * risk_for_one_trade_in_usd
                            df_with_resulting_table_of_certain_models.loc[index,
                            f"deposit_by_end_of_period_with_risk_{risk_percent_value1}_and_tp_{tp_value}_to_one_sl_calculated"] = deposit_for_this_trade_sl_calculated

                        else:
                            deposit_for_this_trade_sl_calculated=\
                                initial_deposit_for_this_risk_and_tp_sl_calculated-risk_for_one_trade_in_usd - taker_fee * risk_for_one_trade_in_usd
                            df_with_resulting_table_of_certain_models.loc[index,
                            f"deposit_by_end_of_period_with_risk_{risk_percent_value1}_and_tp_{tp_value}_to_one_sl_calculated"] = deposit_for_this_trade_sl_calculated

                        initial_deposit_for_this_risk_and_tp_sl_calculated=deposit_for_this_trade_sl_calculated
                except:
                    traceback.print_exc()
                    continue

    # st.write('df_with_resulting_table_of_certain_models_enhanced_final')
    # st.dataframe(df_with_resulting_table_of_certain_models)
    return df_with_resulting_table_of_certain_models

def add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(table_name,
                                                         engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                         dict_of_identical_queries_for_each_table,
                                                         number_of_prev_and_next_days,
                                                         engine_for_ohlcv_data_for_stocks_0000,
                                  df_with_resulting_table_of_certain_models,
                                  initial_funds_for_performance_calculation_over_given_period,
                                  risk_for_one_trade_in_usd):
    width_of_line_chart = 1000
    height_of_line_chart = 800
    number_of_take_profits=list(range(3,101))


    list_of_columns_to_create=[]

    for tp_value in number_of_take_profits:
        column_to_create=f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_tp_reached"
        list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)
    for tp_value in number_of_take_profits:
        column_to_create=f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_sl_reached"
        list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)

    for tp_value in number_of_take_profits:
        column_to_create = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_tp_reached"
        list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)
    for tp_value in number_of_take_profits:
        column_to_create = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_sl_reached"
        list_of_columns_to_create.append(column_to_create)
    df_with_resulting_table_of_certain_models = add_columns_to_dataframe(df_with_resulting_table_of_certain_models,
                                                                         list_of_columns_to_create)

    df_with_resulting_table_of_certain_models=df_with_resulting_table_of_certain_models.sort_values(by='timestamp_of_order_placement_bar')
    # Assuming df_with_resulting_table_of_certain_models is your DataFrame
    # Create a new index using range
    new_index = range(0, len(df_with_resulting_table_of_certain_models))

    # Set the new index for the DataFrame
    df_with_resulting_table_of_certain_models.index = new_index

    # st.write('df_with_resulting_table_of_certain_models_enhanced')
    # st.dataframe(df_with_resulting_table_of_certain_models)

    timestamp_when_technical_stop_loss_was_reached_ndarray = np.empty(len(df_with_resulting_table_of_certain_models))
    if "timestamp_when_technical_stop_loss_was_reached" in df_with_resulting_table_of_certain_models.columns:
        timestamp_when_technical_stop_loss_was_reached_ndarray = df_with_resulting_table_of_certain_models[
            f"timestamp_when_technical_stop_loss_was_reached"].to_numpy()

    timestamp_when_calculated_stop_loss_was_reached_ndarray = np.empty(len(df_with_resulting_table_of_certain_models))
    if "timestamp_when_calculated_stop_loss_was_reached" in df_with_resulting_table_of_certain_models.columns:
        timestamp_when_calculated_stop_loss_was_reached_ndarray = df_with_resulting_table_of_certain_models[
            f"timestamp_when_calculated_stop_loss_was_reached"].to_numpy()

    timestamp_of_order_placement_bar_ndarray= np.empty(len(df_with_resulting_table_of_certain_models))
    if "timestamp_of_order_placement_bar" in df_with_resulting_table_of_certain_models.columns:
        timestamp_of_order_placement_bar_ndarray = df_with_resulting_table_of_certain_models[
            f"timestamp_of_order_placement_bar"].to_numpy()

    # Iterating over each row and selecting each row as a DataFrame
    for tp_value in number_of_take_profits:
        print("tp_value1")
        print(tp_value)


        # for index, row in df_with_resulting_table_of_certain_models.iterrows():




        max_profit_target_multiple_when_sl_calculated_ndarray=np.empty(len(df_with_resulting_table_of_certain_models))
        max_profit_target_multiple_when_sl_technical_ndarray=np.empty(len(df_with_resulting_table_of_certain_models))
        timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray=np.empty(len(df_with_resulting_table_of_certain_models))
        timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray=np.empty(len(df_with_resulting_table_of_certain_models))
        if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
            max_profit_target_multiple_when_sl_technical_ndarray = df_with_resulting_table_of_certain_models[
                "max_profit_target_multiple_when_sl_technical"].to_numpy()
            if f"timestamp_of_tp_{tp_value}_to_one_is_reached_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray=df_with_resulting_table_of_certain_models[
                f"timestamp_of_tp_{tp_value}_to_one_is_reached_sl_technical"].to_numpy()



        if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
            max_profit_target_multiple_when_sl_calculated_ndarray = df_with_resulting_table_of_certain_models[
                "max_profit_target_multiple_when_sl_calculated"].to_numpy()
            if f"timestamp_of_tp_{tp_value}_to_one_is_reached_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray=df_with_resulting_table_of_certain_models[
                f"timestamp_of_tp_{tp_value}_to_one_is_reached_sl_calculated"].to_numpy()

        # Initialize trade_duration_for_this_trade_sl_technical with NaN values
        trade_duration_for_this_trade_sl_technical_ndarray_sl_reached = np.empty_like(
            max_profit_target_multiple_when_sl_technical_ndarray)
        trade_duration_for_this_trade_sl_technical_ndarray_tp_reached = np.empty_like(
            max_profit_target_multiple_when_sl_technical_ndarray)
        # Convert the array to a float data type to accommodate NaN values
        trade_duration_for_this_trade_sl_technical_ndarray_sl_reached = trade_duration_for_this_trade_sl_technical_ndarray_sl_reached.astype(
            float)
        trade_duration_for_this_trade_sl_technical_ndarray_tp_reached = trade_duration_for_this_trade_sl_technical_ndarray_tp_reached.astype(
            float)
        timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray=timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray.astype(int)
        timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray=timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray.astype(int)

        # Set NaN values in the array
        trade_duration_for_this_trade_sl_technical_ndarray_sl_reached[:] = np.nan
        trade_duration_for_this_trade_sl_technical_ndarray_tp_reached[:] = np.nan

        # Initialize trade_duration_for_this_trade_sl_calculated with NaN values
        trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached = np.empty_like(
            max_profit_target_multiple_when_sl_calculated_ndarray)
        trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached = np.empty_like(
            max_profit_target_multiple_when_sl_calculated_ndarray)
        # Convert the array to a float data type to accommodate NaN values
        trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached = trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached.astype(
            float)
        trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached = trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached.astype(
            float)
        timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray = timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray.astype(
            int)
        timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray = timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray.astype(
            int)

        # Set NaN values in the array
        trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached[:] = np.nan
        trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached[:] = np.nan



        # condition = max_profit_target_multiple_when_sl_technical >= tp_value
        # trade_duration_for_this_trade_sl_technical = np.where(
        #     condition,
        #     (
        #                 initial_trade_duration_this_risk_and_tp_sl_technical + tp_value * risk_for_one_trade_in_usd - maker_fees * risk_for_one_trade_in_usd),
        #     (
        #                 initial_trade_duration_this_risk_and_tp_sl_technical - risk_for_one_trade_in_usd - taker_fees * risk_for_one_trade_in_usd)
        # )


        for idx, max_profit_target_multiple_when_sl_technical_value in np.ndenumerate(max_profit_target_multiple_when_sl_technical_ndarray):
            trade_duration_for_this_trade_sl_technical = np.nan
            if max_profit_target_multiple_when_sl_technical_value >= tp_value:
                trade_duration_for_this_trade_sl_technical = timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray[idx]-timestamp_of_order_placement_bar_ndarray[idx]
                trade_duration_for_this_trade_sl_technical=trade_duration_for_this_trade_sl_technical/86400
                trade_duration_for_this_trade_sl_technical_ndarray_tp_reached[idx] = trade_duration_for_this_trade_sl_technical

                if trade_duration_for_this_trade_sl_technical==0:
                    print("max_profit_target_multiple_when_sl_technical_value")
                    print(max_profit_target_multiple_when_sl_technical_value)
                    print("idx")
                    print(idx)
                    print("timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray[idx]")
                    print(timestamp_of_tp_n_to_one_is_reached_sl_technical_ndarray[idx])
                    print("timestamp_of_order_placement_bar_ndarray[idx]")
                    print(timestamp_of_order_placement_bar_ndarray[idx])
                    # time.sleep(100000)


            else:
                trade_duration_for_this_trade_sl_technical = timestamp_when_technical_stop_loss_was_reached_ndarray[
                                                                 idx] - timestamp_of_order_placement_bar_ndarray[idx]
                trade_duration_for_this_trade_sl_technical = trade_duration_for_this_trade_sl_technical / 86400
                trade_duration_for_this_trade_sl_technical_ndarray_sl_reached[idx] = trade_duration_for_this_trade_sl_technical
            

        # Update the DataFrame column with the technical deposit values
        column_name = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_tp_reached"
        df_with_resulting_table_of_certain_models[column_name] = trade_duration_for_this_trade_sl_technical_ndarray_tp_reached
        column_name = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_sl_reached"
        df_with_resulting_table_of_certain_models[
            column_name] = trade_duration_for_this_trade_sl_technical_ndarray_sl_reached


        ##################################
        ##################################
        ##################################

        for idx, max_profit_target_multiple_when_sl_calculated_value in np.ndenumerate(
                max_profit_target_multiple_when_sl_calculated_ndarray):
            trade_duration_for_this_trade_sl_calculated = np.nan
            if max_profit_target_multiple_when_sl_calculated_value >= tp_value:
                trade_duration_for_this_trade_sl_calculated = timestamp_of_tp_n_to_one_is_reached_sl_calculated_ndarray[
                                                                 idx] - timestamp_of_order_placement_bar_ndarray[idx]
                trade_duration_for_this_trade_sl_calculated=trade_duration_for_this_trade_sl_calculated/86400
                trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached[idx] = trade_duration_for_this_trade_sl_calculated


            else:
                trade_duration_for_this_trade_sl_calculated = timestamp_when_calculated_stop_loss_was_reached_ndarray[
                                                                     idx] - timestamp_of_order_placement_bar_ndarray[
                                                                     idx]
                trade_duration_for_this_trade_sl_calculated = trade_duration_for_this_trade_sl_calculated / 86400
                trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached[idx] = trade_duration_for_this_trade_sl_calculated

        # Update the DataFrame column with the calculated deposit values
        column_name = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_tp_reached"
        df_with_resulting_table_of_certain_models[
            column_name] = trade_duration_for_this_trade_sl_calculated_ndarray_tp_reached
        column_name = f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_sl_reached"
        df_with_resulting_table_of_certain_models[
            column_name] = trade_duration_for_this_trade_sl_calculated_ndarray_sl_reached







    st.write('df_with_resulting_table_of_certain_models_enhanced_final')
    st.dataframe(df_with_resulting_table_of_certain_models)

    return df_with_resulting_table_of_certain_models

def get_unique_exchanges(dataframe):
    unique_exchanges = dataframe['exchange'].unique().tolist()
    return unique_exchanges


def add_order_counts_by_exchange(dataframe, unique_exchanges, number_of_days_before_and_after_to_count_exchanges_where_order_was_placed):
    dataframe.sort_values(by='timestamp_of_order_placement_bar')
    for exchange in unique_exchanges:
        mask = dataframe['exchange'] == exchange
        for i, timestamp in enumerate(dataframe['timestamp_of_order_placement_bar']):
            # Define time window for each timestamp
            prev_window = timestamp - number_of_days_before_and_after_to_count_exchanges_where_order_was_placed * 24 * 3600  # number_of_days_before_and_after_to_count_exchanges_where_order_was_placed days in seconds
            next_window = timestamp + number_of_days_before_and_after_to_count_exchanges_where_order_was_placed * 24 * 3600  # number_of_days_before_and_after_to_count_exchanges_where_order_was_placed days in seconds

            # Count orders within the defined time window for the current exchange
            count = ((dataframe['timestamp_of_order_placement_bar'].between(prev_window, timestamp, inclusive='neither') |
                      dataframe['timestamp_of_order_placement_bar'].between(timestamp, next_window, inclusive='neither')) &
                     mask).sum()

            # Assign the count to the corresponding exchange column
            dataframe.at[i, f'orders_{exchange}_{number_of_days_before_and_after_to_count_exchanges_where_order_was_placed}d_back_and_forth_window'] = count

    return dataframe
def plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,
        number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,
        table_name,
        engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
        dict_of_identical_queries_for_each_table,
        number_of_prev_and_next_days,
        engine_for_ohlcv_data_for_stocks_0000,
                                  df_with_resulting_table_of_certain_models,
                                  initial_funds_for_performance_calculation_over_given_period,
                                  initial_take_profit_for_performance_calculation_over_given_period,
                                  risk_for_one_trade_in_usd):




    # deposit_by_the_end_of_the_given_period_if_sl_is_technical_and_calculated_df=pd.DataFrame(columns=["deposit_by_the_end_of_the_given_period_if_sl_is_technical",
    #                                                                                    "deposit_by_the_end_of_the_given_period_if_sl_is_calculated"])
    # Create an empty list to store the dictionaries
    width_of_line_chart=1000
    height_of_line_chart=800




    config = dict({'scrollZoom': True, 'displaylogo': False,
                   'modeBarButtonsToAdd': ['drawline', 'eraseshape']})
    # if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
    #     # st.dataframe(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df)
    #     st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")
    #     fig = px.line(deposit_by_the_end_of_the_given_period_if_sl_is_technical_df,
    #                       x=deposit_by_the_end_of_the_given_period_if_sl_is_technical_df.index,
    #                       y=[deposit_by_the_end_of_the_given_period_if_sl_is_technical_df[f"deposit_risk_{risk_percent_value}%_sl_is_technical"] for risk_percent_value in risk_percent_list],
    #                   width=width_of_line_chart,height=height_of_line_chart,markers=True,title="deposit by end of given period when sl is technical")
    #
    #     st.plotly_chart(fig,config=config,use_container_width=True)
    #     # fig.show(config=config)
    # if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
    #     # st.dataframe(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df)
    #     st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")
    #     fig1 = px.line(deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df,
    #                       x=deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df.index,
    #                       y=[deposit_by_the_end_of_the_given_period_if_sl_is_calculated_df[f"deposit_risk_{risk_percent_value}%_sl_is_calculated"] for risk_percent_value in risk_percent_list],
    #                   width=width_of_line_chart,height=height_of_line_chart,markers=True,title="deposit by end of given period when sl is calculated")
    #     st.plotly_chart(fig1,config=config,use_container_width=True)



    entire_ohlcv_df=get_ohlcv_df_for_btc_usdt_on_gateio(engine_for_ohlcv_data_for_stocks_0000)

    df_with_resulting_table_of_certain_models['human_datetime_of_order_placement_bar'] = pd.to_datetime(
        df_with_resulting_table_of_certain_models['timestamp_of_order_placement_bar'], unit='s')

    # Sort the dataframe by the timestamp column (in case it's not already sorted)
    df_with_resulting_table_of_certain_models = df_with_resulting_table_of_certain_models.sort_values(
        'human_datetime_of_order_placement_bar')


    if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns or\
            "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
        st.write(f"number_of_positions={len(df_with_resulting_table_of_certain_models)}")





        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Time in days spent in each trade When SL is Technical",
                                            "Time in days spent in each trade When SL is Calculated"),
                            vertical_spacing = 0.01,specs=[[{"secondary_y": True}],
                                                           [{"secondary_y": True}]])

        if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
            fig.add_trace(go.Scatter(x=entire_ohlcv_df["open_time"], y=entire_ohlcv_df['close'], mode='lines',
                                     name='Close Price of BTC'),
                          row=1, col=1)

            st.write('''df_with_resulting_table_of_certain_models[
                                     f"trade_duration_in_days_and_tp_3_to_one_sl_technical_tp_reached"]''')
            st.write(df_with_resulting_table_of_certain_models[
                                                 f"trade_duration_in_days_and_tp_3_to_one_sl_technical_tp_reached"])

            st.write('''df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"]''')
            st.write(df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"])
            st.write('''entire_ohlcv_df["open_time"]''')
            st.write(entire_ohlcv_df["open_time"])
            for tp_value in range(3,101):
                fig.add_trace(go.Scatter(x=df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"],
                                             y=df_with_resulting_table_of_certain_models[
                                                 f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_tp_reached"],
                                             mode='markers', yaxis='y2', visible='legendonly',marker=dict(size=3),
                                             name=f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_technical_tp_reached"), secondary_y=True,
                                  row=1, col=1)
            fig.add_trace(
                go.Scatter(x=df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"],
                           y=df_with_resulting_table_of_certain_models[
                               f"trade_duration_in_days_and_tp_3_to_one_sl_technical_sl_reached"],
                           mode='markers', yaxis='y2',
                           # visible='legendonly',
                           marker=dict(size=3),
                           name=f"trade_duration_in_days_and_tp_3_to_one_sl_technical_sl_reached"), secondary_y=True,
                row=1, col=1)

        if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
            fig.add_trace(go.Scatter(x=entire_ohlcv_df["open_time"], y=entire_ohlcv_df['close'], mode='lines',
                                     name='Close Price of BTC'),
                          row=2, col=1)
            for tp_value in range(3, 101):
                fig.add_trace(
                    go.Scatter(x=df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"],
                               y=df_with_resulting_table_of_certain_models[
                                   f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_tp_reached"],
                               mode='markers', yaxis='y2', visible='legendonly',marker=dict(size=3),
                               name=f"trade_duration_in_days_and_tp_{tp_value}_to_one_sl_calculated_tp_reached"), secondary_y=True,
                    row=2, col=1)
            fig.add_trace(
                go.Scatter(x=df_with_resulting_table_of_certain_models["human_datetime_of_order_placement_bar"],
                           y=df_with_resulting_table_of_certain_models[
                               f"trade_duration_in_days_and_tp_3_to_one_sl_calculated_sl_reached"],
                           mode='markers', yaxis='y2',
                           # visible='legendonly',
                           marker=dict(size=3),
                           name=f"trade_duration_in_days_and_tp_3_to_one_sl_calculated_sl_reached"), secondary_y=True,
                row=2, col=1)



        # Updating the layout to ensure the full on-hover text is displayed
        fig.update_layout(hoverlabel=dict(namelength=-1))

        # To show all data points on hover, without requiring to interpolate between points
        fig.update_layout(hovermode='x unified')
        fig.update_layout(hoverdistance=-1)
        fig.update_layout(dragmode="pan")

        # # Create axis objects
        # fig.update_layout(
        #     # pass the y-axis 2 title, titlefont, color and
        #     # tickfont as a dictionary and store it an
        #     # variable yaxis 2
        #     yaxis2=dict(
        #         title="yaxis 2",
        #         titlefont=dict(
        #             color="#FF0000"
        #         ),
        #         tickfont=dict(
        #             color="#FF0000"
        #         ),
        #         anchor="free",  # specifying x - axis has to be the fixed
        #         overlaying="y",  # specifyinfg y - axis has to be separated
        #         side="right",  # specifying the side the axis should be present
        #         position=0.2  # specifying the position of the axis
        #     ),
        #
        # )
        # # Update layout to display the secondary y-axis
        # fig.update_layout(
        #     yaxis2=dict(
        #         title="Secondary Y Axis Title",
        #         overlaying="y",
        #         side="right"
        #     )
        # )

        # # settings for the new y axis
        # y2 = go.YAxis(overlaying='y', side='right')
        #
        # # adding the second y axis
        #

        fig.update_layout(height=height_of_line_chart * 2, width=width_of_line_chart,
                          title="Time in days spent in each trade")

        # Narrow the gap between subplots

        st.plotly_chart(fig, use_container_width=True)

        # Define a function that reacts to relayout events
        # def on_relayout(trace, points, state):
        #     xaxis_range = state["xaxis.range"]
        #     yaxis_range = state["yaxis.range"]
        #
        # # Attach the on_relayout function to the relayout event
        # fig.data[0].on('relayout', on_relayout)




        # fig1.show(config=config)




def add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange):
    plots_per_page = 10
    # Define the total number of plots
    total_plots = len(tuple_of_trading_pairs_with_exchange)
    # Calculate the number of pages
    total_pages = max(1, (total_plots + plots_per_page - 1) // plots_per_page)
    # Get the current page from user input or set a default value
    random_number = random.randint(1, 1000000)
    current_page = st.sidebar.number_input("Page", min_value=1, max_value=total_pages, value=1,key=random_number)
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

def return_df_from_postgres_sql_table(query,table_name,_engine_name):
    df_with_resulting_table_of_certain_models=pd.DataFrame()
    exchanges = ["binance", "gateio", "huobi", "mexc3", "huobipro", "kucoin", "okex5",
                 "bybit", "lbank2", "bitfinex2", "bingx", "whitebit", "bigone"]
    # exchanges = ["mexc3",]
    exchange_conditions = ", ".join([f"'{exchange}'" for exchange in exchanges])

    try:

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
            st.write(f"{table_with_ohlcv_table} is in db with today's pairs")
            # st.write(f"{list_of_tables_in_low_volume_ohlcv_db} is in db with today's pairs")
            try:

                table_with_ohlcv_data_df = \
                    pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                                      engine_for_ohlcv_low_volume_data_for_stocks_0000)

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
                table_with_ohlcv_data_df = \
                    pd.read_sql_query(f'''select * from "{table_with_ohlcv_table}"''',
                                      engine_for_ohlcv_data_for_stocks_0000)
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

    db_where_levels_formed_by_highs_and_lows_for_cryptos_0000_hist="levels_formed_by_highs_and_lows_for_cryptos_0000_hist"
    engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist, \
        connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
        initialize_connection_and_engine(db_where_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)


    list_of_options_for_today_that_are_available_and_not_all_possible_options=\
        return_list_of_options_for_today_that_are_available_and_not_all_possible_options(
            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)



    model=st.selectbox("What is your model?",list_of_options_for_today_that_are_available_and_not_all_possible_options)


    table_name = ""

    ################################
    ##############################
    ###############################
    if model=="New ATL within last two days":
        table_name="current_asset_had_atl_within_two_last_days_period"

    if model=="New ATH within last two days":
        table_name="current_asset_had_ath_within_two_last_days_period"


    if model=="Breakout of ATL with position entry next day after breakout":
        table_name="current_breakout_situations_of_atl_position_entry_next_day"

    if model=="Breakout of ATH with position entry next day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_next_day"

    if model=="Breakout of ATL with position entry on second day after breakout":
        table_name="current_breakout_situations_of_atl_position_entry_on_day_two"

    if model=="Breakout of ATH with position entry on second day after breakout":
        table_name="current_breakout_situations_of_ath_position_entry_on_day_two"

    if model=="False Breakout of ATL by one bar":
        table_name="current_false_breakout_of_atl_by_one_bar"

    if model=="False Breakout of ATH by one bar":
        table_name="current_false_breakout_of_ath_by_one_bar"

    if model=="False Breakout of ATL by two bars":
        table_name="current_false_breakout_of_atl_by_two_bars"

    if model=="False Breakout of ATH by two bars":
        table_name="current_false_breakout_of_ath_by_two_bars"

    if model=="Rebound off ATL":
        table_name="current_rebound_situations_from_atl"

    if model=="Rebound off ATH":
        table_name="current_rebound_situations_from_ath"


    ###############################
    ###############################
    ###############################
    ###############################

    df_with_resulting_table_of_certain_models=pd.DataFrame()

    query=""
    with st.form("bfr_criteria_selection_form"):
        st.write("select criteria for bfr model selection".upper())
        min_volume_in_usd_over_last_n_days=st.number_input(label="minimum volume in USD over last 7 days before bfr (must be integer)",min_value=0,value=100000,step=1)
        buy_or_sell_order_was_touched=st.checkbox(label="buy or sell order was touched",value=True)
        max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched=st.number_input(label="max distance from level price in this bar in ATR until order was touched",min_value=0,value=4)
        number_of_exchanges_where_ath_or_atl_were_broken=st.number_input(label="number of exchanges where ath or atl were broken less or equal than",value=200)

        sql_query_part_whether_to_consider_suppression_by_highs_or_lows=""
        suppression_by_highs_or_lows = st.radio(options=[True,False,"any"],label="suppression by highs or lows",horizontal=True,index=2)
        if suppression_by_highs_or_lows==True:
            sql_query_part_whether_to_consider_suppression_by_highs_or_lows=f" and suppression_by_highs_or_lows=True"
        if suppression_by_highs_or_lows==False:
            sql_query_part_whether_to_consider_suppression_by_highs_or_lows=f" and suppression_by_highs_or_lows=False"
        if suppression_by_highs_or_lows=="any":
            sql_query_part_whether_to_consider_suppression_by_highs_or_lows=f""


        max_distance_between_technical_sl_order_in_atr = st.number_input(
            label="max distance between technical sl order in atr", value=2,min_value=0)
        min_distance_between_technical_sl_order_in_atr = st.number_input(
            label="min distance between technical sl order in atr", value=0, min_value=0)
        # Get unique exchanges from the DataFrame
        unique_exchanges = list(set(ccxt.exchanges))
        unique_exchanges.sort()
        # Default selected exchanges
        default_exchanges = [
            "binance", "gateio", "huobi", "mexc3", "huobipro",
            "kucoin", "okex5", "bybit", "lbank2", "bitfinex2",
            "bingx", "whitebit", "bigone", "tokocrypto", "bitget"
        ]
        selected_exchanges=[]
        selected_exchanges_from_expander=[]
        # Create an expander
        with st.expander("Select Exchanges"):
            selected_exchanges_from_expander = st.multiselect(
                "Choose exchanges", unique_exchanges, default=default_exchanges

            )

        choose_all = st.checkbox("Choose all exchanges")
        if choose_all:
            selected_exchanges = unique_exchanges  # Select all exchanges
        else:
            selected_exchanges = selected_exchanges_from_expander


        exchange_conditions = ", ".join([f"'{exchange}'" for exchange in selected_exchanges])

        sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available=""
        if table_name=="current_breakout_situations_of_atl_position_entry_next_day":
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available=\
                f"and (trading_pair_is_traded_with_margin=True or spot_asset_also_available_as_swap_contract_on_same_exchange=True)"
        elif table_name=="current_breakout_situations_of_atl_position_entry_on_day_two":
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available=\
                f"and (trading_pair_is_traded_with_margin=True or spot_asset_also_available_as_swap_contract_on_same_exchange=True)"
        elif table_name == "current_false_breakout_of_ath_by_one_bar":
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available = \
                f"and (trading_pair_is_traded_with_margin=True or spot_asset_also_available_as_swap_contract_on_same_exchange=True)"
        elif table_name == "current_false_breakout_of_ath_by_two_bars":
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available = \
                f"and (trading_pair_is_traded_with_margin=True or spot_asset_also_available_as_swap_contract_on_same_exchange=True)"
        elif table_name == "current_rebound_situations_from_ath":
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available = \
                f"and (trading_pair_is_traded_with_margin=True or spot_asset_also_available_as_swap_contract_on_same_exchange=True)"
        else:
            sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available = ""

        # Define the range of datetime values
        start_date = st.date_input(
            "Select the FIRST date for bfr models bsu ",
            value=datetime.datetime(2013,3,31),
            key='dateselect'
            ) # Start date and time
        end_date = st.date_input(
            "Select the LAST date for bfr models bsu ",
            value=datetime.datetime.now(),
            key='dateselect1'
            ) # end date and time

        # # Create a range slider using timestamp representation of the datetime values
        # selected_date = st.slider(
        #     "Select a date and time",
        #     value=(start_date, end_date),
        #     format="MM/DD/YYYY",  # Optional: Format for displaying the date
        #     step=datetime.timedelta(days=1)  # Optional: Step size for the slider movement
        # )

        # Convert the selected date to Unix timestamps
        # Create a datetime object with a specific time (e.g., midnight)
        full_date_start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
        full_date_end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        left_selected_timestamp = int(datetime.datetime.timestamp(full_date_start_date))
        right_selected_timestamp = int(datetime.datetime.timestamp(full_date_end_date))

        take_profit_for_performance_calculation_over_given_period=\
            st.number_input(label="take profit for performance calculation over given period (must be integer)",min_value=3,value=3,step=1)
        initial_funds_for_performance_calculation_over_given_period=\
            st.number_input(label="initial funds for performance calculation over given period (must be integer)",min_value=1,value=1000,step=1)
        risk_for_one_trade_in_usd=st.number_input(label="risk for one trade in usd (must be integer)",min_value=1,value=10,step=1)

        how_many_months_for_plotting_and_calculating_of_stats = st.number_input(label="how_many_months_for_plotting_and_calculating_of_stats (must be integer)",
                                                                                min_value=1,value=6, step=1)
        number_of_split_periods_to_plot = st.number_input(label="number_of_split_periods_to_plot", value=4, step=1)
        number_of_prev_and_next_days=st.number_input(label="number_of_prev_and_next_days for plotting number of trades with this time window", value=15,min_value=1, step=1)
        number_of_days_before_and_after_to_count_exchanges_where_order_was_placed=\
            st.number_input(label="number_of_days_before_and_after_to_count_exchanges_where_order_was_placed", value=15,min_value=1, step=1)

        risk_percent_value1=0.5
        with st.expander("Select risk_percent_value for drawdown_calculation"):
            risk_percent_value_for_drawdown_calculation = st.selectbox("Select risk_percent_value",
                                               [5, 4, 3, 2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], index=9)
        tp_value_for_drawdown_calculation = st.number_input("Select take profit N value (tp is N/1)", min_value=3, max_value=100, step=1,
                                    value=9)

        # # Display the selected Unix timestamps
        # st.write("Unix timestamp of the left selected date:", left_selected_timestamp)
        # st.write("Unix timestamp of the right selected date:", right_selected_timestamp)

        # # Display the selected date and time
        # st.write("Selected datetime range:", selected_date)

        form_submit_button_is_pressed = st.form_submit_button('Submit my picks right now')

        if form_submit_button_is_pressed:


            query=f'''SELECT *
                            FROM public."{table_name}"
                            WHERE (base, timestamp_of_bsu, min_volume_in_usd_over_last_n_days) IN (
                                SELECT base, timestamp_of_bsu, MAX(min_volume_in_usd_over_last_n_days)
                                FROM public."{table_name}"
                                GROUP BY base, timestamp_of_bsu
                            )
                            AND min_volume_in_usd_over_last_n_days >= {min_volume_in_usd_over_last_n_days}
                            AND distance_between_technical_sl_order_in_atr<= {max_distance_between_technical_sl_order_in_atr}
                            AND distance_between_technical_sl_order_in_atr>= {min_distance_between_technical_sl_order_in_atr}
                            AND buy_or_sell_order_was_touched = {buy_or_sell_order_was_touched}
                            {sql_query_part_whether_to_consider_suppression_by_highs_or_lows}
                            {sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available} AND
                            max_distance_from_level_price_in_this_bar_in_atr <= {max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched}
                            and exchange IN ({exchange_conditions}) and number_of_exchanges_where_ath_or_atl_were_broken_int <= {number_of_exchanges_where_ath_or_atl_were_broken}
                            and timestamp_of_order_placement_bar BETWEEN {left_selected_timestamp} AND {right_selected_timestamp};'''

            list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist=\
                get_list_of_tables_in_db(engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
            dict_of_identical_queries_for_each_table = {}
            for table_name_in_list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist in\
                    list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist:
                dict_of_identical_queries_for_each_table[table_name_in_list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist]=f'''SELECT *
                            FROM public."{table_name_in_list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist}"
                            WHERE (base, timestamp_of_bsu, min_volume_in_usd_over_last_n_days) IN (
                                SELECT base, timestamp_of_bsu, MAX(min_volume_in_usd_over_last_n_days)
                                FROM public."{table_name_in_list_of_tables_in_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist}"
                                GROUP BY base, timestamp_of_bsu
                            )
                            AND min_volume_in_usd_over_last_n_days >= {min_volume_in_usd_over_last_n_days}
                            AND distance_between_technical_sl_order_in_atr<= {max_distance_between_technical_sl_order_in_atr}
                            AND distance_between_technical_sl_order_in_atr>= {min_distance_between_technical_sl_order_in_atr}
                            AND buy_or_sell_order_was_touched = {buy_or_sell_order_was_touched}
                            {sql_query_part_whether_to_consider_suppression_by_highs_or_lows}
                            {sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available} AND
                            max_distance_from_level_price_in_this_bar_in_atr <= {max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched}
                            and exchange IN ({exchange_conditions}) and number_of_exchanges_where_ath_or_atl_were_broken_int <= {number_of_exchanges_where_ath_or_atl_were_broken}
                            and timestamp_of_order_placement_bar BETWEEN {left_selected_timestamp} AND {right_selected_timestamp};'''

            # st.write("dict_of_identical_queries_for_each_table")
            # st.write(dict_of_identical_queries_for_each_table)

            # st.write("half_year_periods")
            # st.write(half_year_periods)


            print("query1")
            print(query)



            st.write(query)

            height = 1000
            width = 1500

            if model=="New ATL within last two days":
                table_name="current_asset_had_atl_within_two_last_days_period"

                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                  dict_of_identical_queries_for_each_table,
                                                  number_of_prev_and_next_days,
                                                  engine_for_ohlcv_data_for_stocks_0000,
                                                  df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
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

                # -------------------------
                for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                    # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                    plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
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
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
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

                    plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                                                     engine_for_ohlcv_data_for_stocks_0000,
                                                     engine_for_ohlcv_low_volume_data_for_stocks_0000,height,width)


            if model=="Breakout of ATL with position entry next day after breakout":
                table_name="current_breakout_situations_of_atl_position_entry_next_day"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models=\
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                        table_name,
                        engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                        dict_of_identical_queries_for_each_table,
                        number_of_prev_and_next_days,
                        engine_for_ohlcv_data_for_stocks_0000,
                        df_with_resulting_table_of_certain_models,
                        initial_funds_for_performance_calculation_over_given_period,
                        risk_for_one_trade_in_usd)



                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,
                        table_name,
                        engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                        dict_of_identical_queries_for_each_table,
                        number_of_prev_and_next_days,
                        engine_for_ohlcv_data_for_stocks_0000,
                        df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                    # plot_performance_for_each_risk_amount_percent_and_tp_using_numpy(table_name,
                    #                                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                    #                                                      dict_of_identical_queries_for_each_table,
                    #                                                      number_of_prev_and_next_days,
                    #                                                      engine_for_ohlcv_data_for_stocks_0000,
                    #                                                      df_with_resulting_table_of_certain_models,
                    #                                                      initial_funds_for_performance_calculation_over_given_period,
                    #                                                      risk_for_one_trade_in_usd)

                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                # st.write("df_with_resulting_table_of_certain_models_outer")
                # st.dataframe(df_with_resulting_table_of_certain_models)


                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models,  names='exchange', title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                # -------------------------

                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                #     table_name,index_of_trading_pair_to_select,
                #                                      trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)


            if model=="Breakout of ATH with position entry next day after breakout":
                table_name="current_breakout_situations_of_ath_position_entry_next_day"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # tuple_of_trading_pairs_with_exchange=\
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)


                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Breakout of ATL with position entry on second day after breakout":
                table_name="current_breakout_situations_of_atl_position_entry_on_day_two"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Breakout of ATH with position entry on second day after breakout":
                table_name="current_breakout_situations_of_ath_position_entry_on_day_two"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="False Breakout of ATL by one bar":
                table_name="current_false_breakout_of_atl_by_one_bar"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="False Breakout of ATH by one bar":
                table_name="current_false_breakout_of_ath_by_one_bar"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)


                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="False Breakout of ATL by two bars":
                table_name="current_false_breakout_of_atl_by_two_bars"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)


                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="False Breakout of ATH by two bars":
                table_name="current_false_breakout_of_ath_by_two_bars"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                  engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Rebound off ATL":
                table_name="current_rebound_situations_from_atl"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.write("df_with_resulting_table_of_certain_models")
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000)

                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Rebound off ATH":
                table_name="current_rebound_situations_from_ath"
                df_with_resulting_table_of_certain_models=pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models=\
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    df_with_resulting_table_of_certain_models = \
                        add_columns_like_deposit_by_end_of_period_with_risk_and_tp_n_to_one_sl_technical_or_calculated(
                            table_name,
                            engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                            dict_of_identical_queries_for_each_table,
                            number_of_prev_and_next_days,
                            engine_for_ohlcv_data_for_stocks_0000,
                            df_with_resulting_table_of_certain_models,
                            initial_funds_for_performance_calculation_over_given_period,
                            risk_for_one_trade_in_usd)

                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)
                # plot piechart with exchange share
                fig = px.pie(df_with_resulting_table_of_certain_models, names='exchange',
                             title="Share of exchanges where this bfr model is found")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    autosize=False,
                    width=1000,
                    height=1000
                )
                st.plotly_chart(fig)
                # plot piechart with max_profit_target_multiple_when_sl_technical
                if "max_profit_target_multiple_when_sl_technical" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_technical',
                                 title="max_profit_target_multiple_when_sl_technical")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_technical'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_technical=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                # plot piechart with max_profit_target_multiple_when_sl_calculated
                if "max_profit_target_multiple_when_sl_calculated" in df_with_resulting_table_of_certain_models.columns:
                    fig = px.pie(df_with_resulting_table_of_certain_models,
                                 names='max_profit_target_multiple_when_sl_calculated',
                                 title="max_profit_target_multiple_when_sl_calculated")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)

                    filtered_df = df_with_resulting_table_of_certain_models.loc[
                        df_with_resulting_table_of_certain_models['max_profit_target_multiple_when_sl_calculated'] == 0]
                    fig = px.pie(filtered_df, names='exchange',
                                 title="Share of exchanges where this bfr model is found <br>but max_profit_target_multiple_when_sl_calculated=0")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(
                        autosize=False,
                        width=1000,
                        height=1000
                    )
                    st.plotly_chart(fig)
                # -------------------------
                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # tuple_of_trading_pairs_with_exchange = \
                #     add_sidebar_and_return_tuple_of_trading_pairs_with_exchange(tuple_of_trading_pairs_with_exchange)
                ##############################3
                # -------------------------
                # for index_of_trading_pair_to_select, trading_pair_to_select in enumerate(tuple_of_trading_pairs_with_exchange):
                #     # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)
                #
                #     plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                #                                      engine_for_ohlcv_data_for_stocks_0000,
                #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Last close price is closer to ATL than n %ATR":
                table_name="current_asset_approaches_its_atl_closer_than_n_percent_atr"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)

                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model=="Last close price is closer to ATH than n %ATR":
                table_name="current_asset_approaches_its_ath_closer_than_n_percent_atr"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)

                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                # index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model == "Last close price is closer to ATL than N % of ATR(30)":
                table_name = "from_close_to_atl_less_than_n_of_atr_and_has_less_than_n_days"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,dict_of_identical_queries_for_each_table,number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)

                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 table_name,
                                                 index_of_trading_pair_to_select,
                                                 trading_pair_to_select,
                                                 df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)
            if model == "Last close price is closer to ATH than N % of ATR(30)":
                table_name = "from_close_to_ath_less_than_n_of_atr_and_has_less_than_n_days"
                df_with_resulting_table_of_certain_models = pd.DataFrame()
                try:
                    df_with_resulting_table_of_certain_models = \
                        return_df_from_postgres_sql_table(query, table_name,
                                                          engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)
                    plot_deposit_by_end_of_period_for_calc_and_tech_sl_and_plot_number_of_trades_within_n_days(risk_percent_value_for_drawdown_calculation,tp_value_for_drawdown_calculation,number_of_days_before_and_after_to_count_exchanges_where_order_was_placed,
                        table_name, engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                  dict_of_identical_queries_for_each_table,
                                                  number_of_prev_and_next_days,engine_for_ohlcv_data_for_stocks_0000,df_with_resulting_table_of_certain_models,
                                                  initial_funds_for_performance_calculation_over_given_period,
                                                  take_profit_for_performance_calculation_over_given_period,
                                                  risk_for_one_trade_in_usd)
                except ProgrammingError:
                    st.write(f"There is no '{model}' for today")
                    st.stop()
                st.dataframe(df_with_resulting_table_of_certain_models)

                # -------------------------
                #add select box with trading pair selection
                tuple_of_trading_pairs_with_exchange=tuple(df_with_resulting_table_of_certain_models['ticker'])
                # trading_pair_to_select = st.selectbox("Choose your cryptocurrency", tuple_of_trading_pairs_with_exchange)
                # -------------------------
                # -------------------------
                index_of_trading_pair_to_select = tuple_of_trading_pairs_with_exchange.index(trading_pair_to_select)

                plot_multiple_charts_on_one_page(connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
                                                 table_name,index_of_trading_pair_to_select,trading_pair_to_select, df_with_resulting_table_of_certain_models,
                                                 engine_for_ohlcv_data_for_stocks_0000,
                                                 engine_for_ohlcv_low_volume_data_for_stocks_0000, height, width)


            # Draw a wide horizontal line using HTML
            st.markdown("<hr style='border: 2px solid #42f5ef'>", unsafe_allow_html=True)

            # plot_for_each_period_separate_charts(sql_query_part_whether_to_consider_suppression_by_highs_or_lows,table_name,
            #                                      min_volume_in_usd_over_last_n_days,
            #                                      buy_or_sell_order_was_touched,
            #                                      max_distance_between_technical_sl_order_in_atr,
            #                                      min_distance_between_technical_sl_order_in_atr,
            #                                      sql_query_part_if_pair_is_traded_with_margin_or_swap_is_available,
            #                                      max_distance_from_level_price_in_this_bar_in_atr_until_order_was_touched,
            #                                      exchange_conditions,
            #                                      number_of_exchanges_where_ath_or_atl_were_broken,
            #                                      engine_for_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
            #                                      how_many_months_for_plotting_and_calculating_of_stats,
            #                                      initial_funds_for_performance_calculation_over_given_period,
            #                                      take_profit_for_performance_calculation_over_given_period,
            #                                      risk_for_one_trade_in_usd,
            #                                      model,
            #                                      engine_for_ohlcv_data_for_stocks_0000,
            #                                      engine_for_ohlcv_low_volume_data_for_stocks_0000,
            #                                      connection_to_db_levels_formed_by_highs_and_lows_for_cryptos_0000_hist,
            #                                      number_of_split_periods_to_plot)

    # df_with_resulting_table_of_certain_models
    # st.write("df_with_resulting_table_of_certain_models")
    # st.dataframe(df_with_resulting_table_of_certain_models)
    #
    # # Creating an expander
    # # risk_percent_value1 = 1
    # # with st.expander("Choose a Value"):
    # risk_percent_value1 = st.selectbox("Select risk_percent_value",
    #                                    [5, 4, 3, 2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], index=9)
    # tp_value1 = st.number_input("Select take profit N value (tp is N/1)", min_value=3, max_value=100, step=1, value=9)
    # st.write("Calculate abs_max_drawdown, max_drawdown_percentage, drawdown_begin_date, drawdown_end_date, num_trades_in_drawdown ")



    # df_with_resulting_table_of_certain_models, abs_max_drawdown, max_drawdown_percentage, drawdown_begin_date, drawdown_end_date, num_trades_in_drawdown = \
    #     calculate_max_drawdown_drawdown_beginning_and_end_dates_num_trades_in_drawdown_sl_technical(
    #         df_with_resulting_table_of_certain_models,
    #         risk_percent_value1,
    #         tp_value1)

    # st.write("df_with_resulting_table_of_certain_models")
    # st.dataframe(df_with_resulting_table_of_certain_models)
    # st.write("Absolute Maximum Drawdown:", abs_max_drawdown)
    # st.write("Percentage Maximum Drawdown:", max_drawdown_percentage)
    # st.write("Drawdown Begin Date:", drawdown_begin_date)
    # st.write("Drawdown End Date:", drawdown_end_date)
    # st.write("Number of Trades in the Drawdown:", num_trades_in_drawdown)



if __name__=="__main__":
    streamlit_func()