import pprint
from statistics import mean
import pandas as pd
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
import os
import time
import datetime
import traceback
import datetime as dt
import tzlocal
import numpy as np
from collections import Counter
from sqlalchemy_utils import create_database,database_exists
import db_config
# from sqlalchemy import MetaData
from sqlalchemy import inspect
import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import connect_to_postgres_db_without_deleting_it_first
from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_next_day import get_list_of_tables_in_db
from sqlalchemy import text

def count_number_of_values_between_underscores_in_a_string(string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges):
    string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges="empty_string"
    if string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges == "":
        string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = 0
    elif "_" not in string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges:
        string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = 1
    elif "_" in string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges:
        list_for_counting_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = \
            string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges.split("_")
        string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = \
            len(list_for_counting_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges)
    else:
        print(f"unknown case for {string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges}")

    return str(string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges)
def check_atl_breakout_df_is_argument(table_with_ohlcv_data_df,
                       number_of_days_where_atl_was_not_broken,
                       atl,
                       row_of_last_atl):
    table_with_ohlcv_data_df_slice_five_columns_only_df = table_with_ohlcv_data_df[
        ["Timestamp", "open", "high", "low", "close", "volume"]]
    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df_slice_five_columns_only_df.to_numpy()

    if np.isnan(row_of_last_atl):
        return True
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_atl - number_of_days_where_atl_was_not_broken)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_atl + 1]

    # Determine if the low was broken during the selected period
    atl_is_not_broken_for_a_long_time = True
    min_low_over_given_period = np.min(selected_rows[:, 3])
    if min_low_over_given_period < atl:
        atl_is_not_broken_for_a_long_time = False

    return atl_is_not_broken_for_a_long_time
def check_ath_breakout_df_is_argument(table_with_ohlcv_data_df,
                       number_of_days_where_ath_was_not_broken,
                       ath,
                       row_of_last_ath):
    table_with_ohlcv_data_df_slice_five_columns_only_df = table_with_ohlcv_data_df[
        ["Timestamp", "open", "high", "low", "close", "volume"]]
    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df_slice_five_columns_only_df.to_numpy()

    if np.isnan(row_of_last_ath):
        return True

    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_ath - number_of_days_where_ath_was_not_broken)
    # print("start_row_index")
    # print(start_row_index)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_ath + 1]
    # print("selected_rows")
    # print(selected_rows)

    # Determine if the high was broken during the selected period
    ath_is_not_broken_for_a_long_time = True
    max_high_over_given_perion = np.max(selected_rows[:, 2])
    # print("max_high_over_given_perion_when_true")
    # print(max_high_over_given_perion)
    if max_high_over_given_perion > ath:
        # print("max_high_over_given_perion_when_false")
        # print(max_high_over_given_perion)
        ath_is_not_broken_for_a_long_time = False

    return ath_is_not_broken_for_a_long_time
def find_row_number(df, timestamp_of_bsu_on_other_exchange):
    # Find the row number where "Timestamp" value matches the given timestamp
    # print("df123")
    # print(df.to_string())
    print("timestamp_of_bsu_on_other_exchange1234")
    print(timestamp_of_bsu_on_other_exchange)
    # print('''df[df["Timestamp"] == timestamp_of_bsu_on_other_exchange, "Timestamp"]''')
    # print(df.loc[df["Timestamp"] == timestamp_of_bsu_on_other_exchange, "Timestamp"].index.tolist())
    index_list=df.loc[df["Timestamp"] == timestamp_of_bsu_on_other_exchange, "Timestamp"].index.tolist()
    row_number=index_list[0]
    print("row_number123234")
    print(row_number)

    # if row_number==0:
    #     time.sleep(1000000)



    return row_number
def check_if_list_has_all_idential_values(list)->bool:
   return len(set(list)) == 1
def generate_correlation_matrices_df(dict_with_ohlcv_dataframes_for_tickers_with_low_volume):
    if len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume) > 1:
        # Initialize an empty correlation matrix
        correlation_matrix_pearson = np.zeros((len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume),
                                               len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)))
        # Initialize an empty correlation matrix
        correlation_matrix_mae = np.zeros((len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume),
                                           len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)))
        # Initialize an empty correlation matrix
        correlation_matrix_rmse = np.zeros((len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume),
                                            len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)))
        # Initialize an empty correlation matrix
        correlation_matrix_cosine_similarity = np.zeros((len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume),
                                                         len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)))
        # Initialize an empty correlation matrix
        correlation_matrix_euclidean_distance = np.zeros(
            (len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume),
             len(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)))
        print("reversed(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys())")
        print(reversed(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys()))
        print("reversed(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys())")
        print(reversed(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys()))

        # Calculate the correlation coefficient for each pair of dataframes
        for (i, df1_key) in enumerate(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys()):
            for (j, df2_key) in enumerate(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys()):
                print("df1_key")
                print(df1_key)
                print("df2_key")
                print(df2_key)

                print("dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df1_key].index")
                print(dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df1_key].index)
                print("dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df2_key].index")
                print(dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df2_key].index)

                d1 = dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df1_key].loc[::-1].reset_index(
                    drop=True)
                d2 = dict_with_ohlcv_dataframes_for_tickers_with_low_volume[df2_key].loc[::-1].reset_index(
                    drop=True)

                common_index = d1.index.intersection(d2.index)
                print("d1.index")
                print(d1.index)
                print("d2.index")
                print(d2.index)

                close1 = d1.loc[
                    common_index, 'close']
                close2 = d2.loc[
                    common_index, 'close']
                print("close1")
                print(close1)
                print("close2")
                print(close2)
                print(f"len({df1_key} df)={len(close1)}")
                print(f"len({df2_key} df)={len(close2)}")
                print("%%%%%%%%%%%%%%%%%%")

                correlation_matrix_pearson[i, j] = close1.corr(close2, method="pearson")
                correlation_matrix_pearson[j, i] = correlation_matrix_pearson[i, j]

                # Mean Absolute Error (MAE)
                correlation_matrix_mae[i, j] = np.mean(np.abs(close2 - close1))
                correlation_matrix_mae[j, i] = correlation_matrix_mae[i, j]

                # Root Mean Squared Error (RMSE)
                correlation_matrix_rmse[i, j] = np.sqrt((np.mean((close2 - close1) ** 2)))
                correlation_matrix_rmse[j, i] = correlation_matrix_rmse[i, j]

                # Cosine Similarity
                dot_product = np.dot(close1, close2)
                norm_close1 = np.linalg.norm(close1)
                norm_close2 = np.linalg.norm(close2)
                cosine_similarity = dot_product / (norm_close1 * norm_close2)
                correlation_matrix_cosine_similarity[i, j] = cosine_similarity
                correlation_matrix_cosine_similarity[j, i] = correlation_matrix_cosine_similarity[i, j]

                # Euclidean Distance
                correlation_matrix_euclidean_distance[i, j] = np.linalg.norm(close2 - close1)
                correlation_matrix_euclidean_distance[j, i] = correlation_matrix_euclidean_distance[i, j]

        threshold = 0.9

        # Find the indices of potential outliers
        outlier_indices = np.where(np.abs(correlation_matrix_pearson) < threshold)
        # Set the display options for the correlation matrix
        np.set_printoptions(precision=4, suppress=True, linewidth=np.inf)
        # print("np.abs(correlation_matrix_pearson)")
        # print(np.abs(correlation_matrix_pearson))

        # Create a list of keys from the dictionary
        keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume = \
            list(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys())

        # Create a DataFrame from the coefficient matrix with row and column names
        df_coefficients_pearson = pd.DataFrame(data=np.abs(correlation_matrix_pearson),
                                               index=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                               columns=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume)

        # Print the new DataFrame with row and column names
        print("df_coefficients_pearson")
        print(df_coefficients_pearson.to_string())

        # Create a DataFrame from the coefficient matrix with row and column names
        df_coefficients_mae = pd.DataFrame(data=np.abs(correlation_matrix_mae),
                                           index=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                           columns=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume)

        # Print the new DataFrame with row and column names
        print("df_coefficients_mae")
        print(df_coefficients_mae.to_string())

        # Create a DataFrame from the coefficient matrix with row and column names
        df_coefficients_rmse = pd.DataFrame(data=np.abs(correlation_matrix_rmse),
                                            index=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                            columns=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume)

        # Print the new DataFrame with row and column names
        print("df_coefficients_rmse")
        print(df_coefficients_rmse.to_string())

        # Create a DataFrame from the coefficient matrix with row and column names
        df_coefficients_cosine_similarity = pd.DataFrame(data=np.abs(correlation_matrix_cosine_similarity),
                                                         index=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                                         columns=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume)

        # Print the new DataFrame with row and column names
        print("df_coefficients_cosine_similarity")
        print(df_coefficients_cosine_similarity.to_string())

        # Create a DataFrame from the coefficient matrix with row and column names
        df_coefficients_euclidean_distance = pd.DataFrame(data=np.abs(correlation_matrix_euclidean_distance),
                                                          index=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                                          columns=keys_of_dict_with_ohlcv_dataframes_for_tickers_with_low_volume)

        # Print the new DataFrame with row and column names
        print("df_coefficients_euclidean_distance")
        print(df_coefficients_euclidean_distance.to_string())

        # # Print the indices of potential outliers
        # for i, j in zip(outlier_indices[0], outlier_indices[1]):
        #     print(
        #         f"Potential outlier: Dataframe {list(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys())[i]} "
        #         f"and Dataframe {list(dict_with_ohlcv_dataframes_for_tickers_with_low_volume.keys())[j]}")

        return df_coefficients_pearson, df_coefficients_mae, df_coefficients_rmse, df_coefficients_cosine_similarity, df_coefficients_euclidean_distance
def generate_dicts_of_low_and_normal_volume_dataframes(ticker_in_bfr_table,
                                                       base_underscore_quote_prev,
                                                       list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume,
                                                       engine_for_ohlcv_data_for_stocks_normal_volume,
                                                       list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                                                       engine_for_ohlcv_data_for_stocks_low_volume,
                                                       dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                                       dict_with_ohlcv_dataframes_for_tickers_with_normal_volume):
    base_underscore_quote = ticker_in_bfr_table.split("_on_")[0]

    print("base_underscore_quote1234")
    print(base_underscore_quote)
    if not base_underscore_quote_prev:
        # base_underscore_quote_prev is empty
        print("base_underscore_quote_prev is empty")
        base_underscore_quote_prev = base_underscore_quote
        # we need to generate two dictionaries of ohlcv dfs: from normal volume db and from low volume db
        dict_with_ohlcv_dataframes_for_tickers_with_low_volume = dict()
        dict_with_ohlcv_dataframes_for_tickers_with_normal_volume = dict()

        starts_with_this_trading_pair = base_underscore_quote
        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = []
        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = []
        joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker = []

        print("list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume123")
        print(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume)
        try:
            list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = \
                remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume,
                    starts_with_this_trading_pair)
        except:
            traceback.print_exc()

        print("list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker12")
        print(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker)

        if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker) > 0:
            for ticker_in_list_with_normal_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker:
                ohlcv_df_normal_volume = \
                    pd.read_sql_query(f'''select * from "{ticker_in_list_with_normal_volume}"''',
                                      engine_for_ohlcv_data_for_stocks_normal_volume)
                dict_with_ohlcv_dataframes_for_tickers_with_normal_volume[
                    ticker_in_list_with_normal_volume] = ohlcv_df_normal_volume

        print("list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume123")
        print(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume)
        print("starts_with_this_trading_pair")
        print(starts_with_this_trading_pair)
        try:
            list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = \
                remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                    starts_with_this_trading_pair)

        except:
            traceback.print_exc()

        print("list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker12")
        print(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker)

        if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker) > 0:
            for ticker_in_list_with_low_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker:
                ohlcv_df_low_volume = \
                    pd.read_sql_query(f'''select * from "{ticker_in_list_with_low_volume}"''',
                                      engine_for_ohlcv_data_for_stocks_low_volume)
                print("ticker_in_list_with_low_volume1")
                print(ticker_in_list_with_low_volume)
                print("ohlcv_df_low_volume2")
                print(ohlcv_df_low_volume)
                dict_with_ohlcv_dataframes_for_tickers_with_low_volume[
                    ticker_in_list_with_low_volume] = ohlcv_df_low_volume

        print("dict_with_ohlcv_dataframes_for_tickers_with_low_volume1")
        print(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)
        print("dict_with_ohlcv_dataframes_for_tickers_with_normal_volume1")
        print(dict_with_ohlcv_dataframes_for_tickers_with_normal_volume)
    else:
        # base_underscore_quote_prev is not empty
        if base_underscore_quote == base_underscore_quote_prev:
            # no need to select ohlcv from db agqin and again
            print("base_underscore_quote==base_underscore_quote_prev")
        else:
            print("base_underscore_quote_prev8")
            print(base_underscore_quote_prev)
            print("base_underscore_quote8")
            print(base_underscore_quote)
            print("base_underscore_quote!=base_underscore_quote_prev")
            # we need to generate two dictionaries of ohlcv dfs: from normal volume db and from low volume db
            dict_with_ohlcv_dataframes_for_tickers_with_low_volume = dict()
            dict_with_ohlcv_dataframes_for_tickers_with_normal_volume = dict()

            starts_with_this_trading_pair = base_underscore_quote.split("_on_")[0]
            list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = []
            list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = []
            joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker = []

            try:
                list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = \
                    remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume,
                        starts_with_this_trading_pair)
            except:
                traceback.print_exc()

            if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker):
                for ticker_in_list_with_normal_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker:
                    ohlcv_df_normal_volume = \
                        pd.read_sql_query(f'''select * from "{ticker_in_list_with_normal_volume}"''',
                                          engine_for_ohlcv_data_for_stocks_normal_volume)
                    dict_with_ohlcv_dataframes_for_tickers_with_normal_volume[
                        ticker_in_list_with_normal_volume] = ohlcv_df_normal_volume

            try:
                list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = \
                    remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                        starts_with_this_trading_pair)

            except:
                traceback.print_exc()

            if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker) > 0:
                for ticker_in_list_with_low_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker:
                    ohlcv_df_low_volume = \
                        pd.read_sql_query(f'''select * from "{ticker_in_list_with_low_volume}"''',
                                          engine_for_ohlcv_data_for_stocks_low_volume)
                    dict_with_ohlcv_dataframes_for_tickers_with_low_volume[
                        ticker_in_list_with_low_volume] = ohlcv_df_low_volume

            base_underscore_quote_prev = base_underscore_quote

    print("dict_with_ohlcv_dataframes_for_tickers_with_low_volume12345")
    print(dict_with_ohlcv_dataframes_for_tickers_with_low_volume)
    print("dict_with_ohlcv_dataframes_for_tickers_with_normal_volume12325")
    print(dict_with_ohlcv_dataframes_for_tickers_with_normal_volume)
    return base_underscore_quote_prev,\
        dict_with_ohlcv_dataframes_for_tickers_with_low_volume,\
        dict_with_ohlcv_dataframes_for_tickers_with_normal_volume
def get_volume_low_value(dataframe, timestamp):
    volume_low_value = dataframe.loc[dataframe["Timestamp"] == timestamp, "volume*low"].values
    if len(volume_low_value) > 0:
        return volume_low_value[0]
    else:
        return None

def remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(list_of_pairs,starts_with_this_trading_pair):
    filtered_strings = [s for s in list_of_pairs if s.startswith(f"{starts_with_this_trading_pair}")]
    return filtered_strings
def add_exchanges_where_pair_was_traded_to_column_in_bfr_tables():
    database_with_ohlcv_with_low_volume="ohlcv_1d_data_for_low_volume_usdt_pairs_0000_pagination"
    engine_for_ohlcv_data_for_stocks_low_volume, \
        connection_to_ohlcv_data_for_stocks_low_volume = \
        connect_to_postgres_db_without_deleting_it_first(database_with_ohlcv_with_low_volume)

    database_with_ohlcv_with_normal_volume="ohlcv_1d_data_for_usdt_pairs_0000_pagination"
    engine_for_ohlcv_data_for_stocks_normal_volume, \
        connection_to_ohlcv_data_for_stocks_normal_volume = \
        connect_to_postgres_db_without_deleting_it_first(database_with_ohlcv_with_normal_volume)

    database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = "levels_formed_by_highs_and_lows_for_cryptos_0000_hist"
    engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist, \
        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
        connect_to_postgres_db_without_deleting_it_first(database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

    list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_low_volume)

    list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_normal_volume)

    list_of_tables_in_database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
        get_list_of_tables_in_db(engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

    # cursor_for_connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist = \
    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.cursor()

    dict_with_ohlcv_dataframes_for_tickers_with_normal_volume=dict()
    dict_with_ohlcv_dataframes_for_tickers_with_low_volume=dict()

    for table_name_in_bfr_database in list_of_tables_in_database_with_levels_formed_by_highs_and_lows_for_cryptos_0000_hist:
        print("table_name_in_bfr_database")
        print(table_name_in_bfr_database)
        table_name_in_bfr_database_df = \
            pd.read_sql_query(f'''select * from "{table_name_in_bfr_database}" where number_of_exchanges_where_ath_or_atl_were_broken IS NULL order by ticker''',
                              engine_for_levels_formed_by_highs_and_lows_for_cryptos_0000_hist)

        base_underscore_quote_prev = ""
        print("table_name_in_bfr_database_df")
        print(table_name_in_bfr_database_df)
        if "timestamp_of_bsu" in table_name_in_bfr_database_df.columns:

            for index, row in table_name_in_bfr_database_df.iterrows():
                print(f"index={index} out of {len(table_name_in_bfr_database_df)}")

                ticker_in_bfr_table = row["ticker"]


                base_underscore_quote_prev, \
                    dict_with_ohlcv_dataframes_for_tickers_with_low_volume, \
                    dict_with_ohlcv_dataframes_for_tickers_with_normal_volume=\
                    generate_dicts_of_low_and_normal_volume_dataframes(ticker_in_bfr_table,
                                                                   base_underscore_quote_prev,
                                                                   list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume,
                                                                   engine_for_ohlcv_data_for_stocks_normal_volume,
                                                                   list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                                                                   engine_for_ohlcv_data_for_stocks_low_volume,
                                                                   dict_with_ohlcv_dataframes_for_tickers_with_low_volume,
                                                                   dict_with_ohlcv_dataframes_for_tickers_with_normal_volume)

                #############################################
                #############################################
                #############################################


                #######################################
                #######################################
                #######################################




                # timestamp_of_false_breakout_bar = row["timestamp_of_false_breakout_bar"]
                # timestamp_of_false_breakout_bar=int(timestamp_of_false_breakout_bar)
                # print(f"Ticker: {ticker}, Timestamp: {timestamp_of_false_breakout_bar}")
                timestamp_of_bsu = row["timestamp_of_bsu"]
                # timestamp_of_bsu = int(timestamp_of_bsu)
                print(f"Ticker: {ticker_in_bfr_table}, timestamp_of_bsu: {timestamp_of_bsu}")

                timestamp_of_bsu_left_edge=timestamp_of_bsu-86400
                timestamp_of_bsu_right_edge = timestamp_of_bsu + 86400

                # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges = "test_string2"
                # try:
                #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker}' '''
                #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                #
                # except:
                #     traceback.print_exc()

                print("ticker_in_bfr_table")
                print(ticker_in_bfr_table)
                # print("list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
                # print(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume)


                # checking if ticker is ohlcv database with normal volume
                if ticker_in_bfr_table in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume:
                    print(f"ticker={ticker_in_bfr_table} is in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
                    # ohlcv_df_normal_volume = \
                    #     pd.read_sql_query(f'''select * from "{ticker}"''',
                    #                       engine_for_ohlcv_data_for_stocks_normal_volume)

                    starts_with_this_trading_pair=ticker_in_bfr_table.split("_on_")[0]
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker=[]
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker=[]
                    joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker=[]



                    try:
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker=\
                            remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                            list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume, starts_with_this_trading_pair)
                    except:
                        traceback.print_exc()
                    try:
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = \
                            remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                                list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                                starts_with_this_trading_pair)
                    except:
                        traceback.print_exc()

                    joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker=\
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker+\
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker

                    print("joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker")
                    print(joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker)

                    exchanges_from_two_db_where_pair_is_traded=[]
                    for ticker in joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker:
                        exchange=ticker.split("_on_")[1]
                        exchanges_from_two_db_where_pair_is_traded.append(exchange)
                    string_of_exchanges_from_two_dbs_where_pair_is_traded="_".join(exchanges_from_two_db_where_pair_is_traded)
                    number_of_exchanges_from_two_dbs_where_pair_is_traded=len(exchanges_from_two_db_where_pair_is_traded)

                    # volume_by_low_value=get_volume_low_value(ohlcv_df_normal_volume, timestamp_of_false_breakout_bar)
                    print(f"normal volume string_of_exchanges_from_two_dbs_where_pair_is_traded1 for {table_name_in_bfr_database}")
                    print(string_of_exchanges_from_two_dbs_where_pair_is_traded)
                    print("number_of_exchanges_from_two_dbs_where_pair_is_traded1")
                    print(number_of_exchanges_from_two_dbs_where_pair_is_traded)

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET string_of_exchanges_from_two_dbs_where_pair_is_traded = '{string_of_exchanges_from_two_dbs_where_pair_is_traded}' WHERE ticker = '{ticker_in_bfr_table}' '''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_from_two_dbs_where_pair_is_traded = '{number_of_exchanges_from_two_dbs_where_pair_is_traded}' WHERE ticker = '{ticker_in_bfr_table}' '''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges = "test_string_normal_volume"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = ""
                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = ""
                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = 0
                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = 0
                    string_of_highs_for_this_bsu_on_normal_volume_exchanges = ""
                    string_of_highs_for_this_bsu_on_low_volume_exchanges = ""
                    string_of_lows_for_this_bsu_on_normal_volume_exchanges = ""
                    string_of_lows_for_this_bsu_on_low_volume_exchanges = ""

                    string_of_of_exchanges_where_ath_was_broken_low_volume=""
                    string_of_of_exchanges_where_atl_was_broken_low_volume=""
                    string_of_of_exchanges_where_ath_was_broken_normal_volume=""
                    string_of_of_exchanges_where_atl_was_broken_normal_volume=""

                    string_of_of_exchanges_where_ath_was_not_broken_low_volume = ""
                    string_of_of_exchanges_where_atl_was_not_broken_low_volume = ""
                    string_of_of_exchanges_where_ath_was_not_broken_normal_volume = ""
                    string_of_of_exchanges_where_atl_was_not_broken_normal_volume = ""

                    ###############################
                    # normal volume
                    ################################


                    if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker) > 0:
                        exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume = []
                        list_of_highs_on_normal_volume_exchanges = []
                        list_of_lows_on_normal_volume_exchanges = []
                        list_of_exchanges_where_ath_was_broken_normal_volume = []
                        list_of_exchanges_where_ath_was_not_broken_normal_volume = []
                        list_of_exchanges_where_atl_was_not_broken_normal_volume = []
                        list_of_exchanges_where_atl_was_broken_normal_volume = []
                        for ticker_with_normal_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker:
                            # ohlcv_df_normal_volume = \
                            #     pd.read_sql_query(f'''select * from "{ticker_with_normal_volume}"''',
                            #                       engine_for_ohlcv_data_for_stocks_normal_volume)

                            ohlcv_df_normal_volume=dict_with_ohlcv_dataframes_for_tickers_with_normal_volume[ticker_with_normal_volume]

                            # Find the necessary timestamp within the range
                            necessary_timestamps_list = ohlcv_df_normal_volume.loc[
                                ohlcv_df_normal_volume['Timestamp'].between(timestamp_of_bsu_left_edge,
                                                                            timestamp_of_bsu_right_edge,
                                                                            inclusive='neither'), 'Timestamp'].values
                            print("necessary_timestamps_list")
                            print(necessary_timestamps_list)

                            exchange="empty_string"
                            if len(necessary_timestamps_list) > 0:
                                exchange = ticker_with_normal_volume.split("_on_")[1]
                                exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume.append(
                                    exchange)

                            if "ath" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list) > 0:
                                list_of_possible_aths_on_other_exchanges = []
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    # print("ohlcv_df_normal_volume.to_string()")
                                    # print(ohlcv_df_normal_volume.to_string())
                                    possible_high_of_bsu = ohlcv_df_normal_volume.loc[ohlcv_df_normal_volume[
                                                                                          "Timestamp"] == possible_timestamp_of_bsu_on_other_exchanges, 'high'].values

                                    print("possible_high_of_bsu")
                                    print(possible_high_of_bsu)
                                    list_of_possible_aths_on_other_exchanges.append(possible_high_of_bsu)
                                    dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume[
                                        possible_high_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                high_on_other_exchange = max(list_of_possible_aths_on_other_exchanges)
                                high_on_other_exchange = high_on_other_exchange[0]
                                print('high_on_other_exchange')
                                print(high_on_other_exchange)
                                list_of_highs_on_normal_volume_exchanges.append(high_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_highs_on_normal_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume[
                                            high_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_ath = find_row_number(ohlcv_df_normal_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_ath")
                                print(row_number_of_ath)

                                number_of_days_where_ath_was_not_broken = 2 * 366
                                ath_is_not_broken_for_a_long_time = check_ath_breakout_df_is_argument(
                                    ohlcv_df_normal_volume,
                                    number_of_days_where_ath_was_not_broken,
                                    high_on_other_exchange,
                                    row_number_of_ath)

                                if ath_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_ath_was_not_broken_normal_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_ath_was_broken_normal_volume.append(exchange)


                            if "atl" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list) > 0:
                                list_of_possible_atls_on_other_exchanges = []
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume={}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    possible_low_of_bsu = ohlcv_df_normal_volume.loc[ohlcv_df_normal_volume[
                                                                                         "Timestamp"] == possible_timestamp_of_bsu_on_other_exchanges, 'low'].values
                                    list_of_possible_atls_on_other_exchanges.append(possible_low_of_bsu)
                                    dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume[
                                        possible_low_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                low_on_other_exchange = min(list_of_possible_atls_on_other_exchanges)
                                low_on_other_exchange = low_on_other_exchange[0]
                                list_of_lows_on_normal_volume_exchanges.append(low_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_lows_on_normal_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume[
                                            low_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_atl = find_row_number(ohlcv_df_normal_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_atl")
                                print(row_number_of_atl)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                atl_is_not_broken_for_a_long_time = check_atl_breakout_df_is_argument(
                                    ohlcv_df_normal_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    low_on_other_exchange,
                                    row_number_of_atl)

                                if atl_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_atl_was_not_broken_normal_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_atl_was_broken_normal_volume.append(exchange)

                        string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = "_".join(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume)
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = len(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume)
                        if "ath" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_highs_on_normal_volume_exchanges = [str(element) for element in
                                                                                      list_of_highs_on_normal_volume_exchanges]
                            string_of_highs_for_this_bsu_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_highs_on_normal_volume_exchanges)
                            print("list_string_values_of_highs_on_normal_volume_exchanges")
                            print(list_string_values_of_highs_on_normal_volume_exchanges)

                            list_string_values_of_exchanges_where_ath_was_broken_normal_volume = [str(element) for
                                                                                                  element
                                                                                                  in
                                                                                                  list_of_exchanges_where_ath_was_broken_normal_volume]
                            string_of_of_exchanges_where_ath_was_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_broken_normal_volume)

                            list_string_values_of_exchanges_where_ath_was_not_broken_normal_volume = [str(element) for
                                                                                                      element
                                                                                                      in
                                                                                                      list_of_exchanges_where_ath_was_not_broken_normal_volume]
                            string_of_of_exchanges_where_ath_was_not_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_not_broken_normal_volume)

                        if "atl" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_lows_on_normal_volume_exchanges = [str(element) for element in
                                                                                     list_of_lows_on_normal_volume_exchanges]
                            string_of_lows_for_this_bsu_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_lows_on_normal_volume_exchanges)
                            print("list_string_values_of_lows_on_normal_volume_exchanges")
                            print(list_string_values_of_lows_on_normal_volume_exchanges)

                            list_string_values_of_exchanges_where_atl_was_broken_normal_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_atl_was_broken_normal_volume]
                            string_of_of_exchanges_where_atl_was_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_broken_normal_volume)

                            list_string_values_of_exchanges_where_atl_was_not_broken_normal_volume = [str(element) for
                                                                                                   element
                                                                                                   in
                                                                                                   list_of_exchanges_where_atl_was_not_broken_normal_volume]
                            string_of_of_exchanges_where_atl_was_not_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_not_broken_normal_volume)

                        # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume3"
                        # try:
                        #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                        #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        # except:
                        #     traceback.print_exc()

                    #########################
                    # low volume
                    ###########################


                    if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker) > 0:

                        # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume7"
                        # try:
                        #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                        #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        # except:
                        #     traceback.print_exc()
                        exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume = []
                        list_of_highs_on_low_volume_exchanges = []
                        list_of_lows_on_low_volume_exchanges = []
                        list_of_exchanges_where_ath_was_not_broken_low_volume = []
                        list_of_exchanges_where_ath_was_broken_low_volume = []
                        list_of_exchanges_where_atl_was_not_broken_low_volume = []
                        list_of_exchanges_where_atl_was_broken_low_volume = []
                        for ticker_with_low_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker:
                            # ohlcv_df_low_volume = \
                            #     pd.read_sql_query(f'''select * from "{ticker_with_low_volume}"''',
                            #                       engine_for_ohlcv_data_for_stocks_low_volume)

                            ohlcv_df_low_volume = dict_with_ohlcv_dataframes_for_tickers_with_low_volume[
                                ticker_with_low_volume]

                            # Find the necessary timestamp within the range
                            necessary_timestamps_list = ohlcv_df_low_volume.loc[
                                ohlcv_df_low_volume['Timestamp'].between(timestamp_of_bsu_left_edge,
                                                                         timestamp_of_bsu_right_edge,
                                                                         inclusive='neither'), 'Timestamp'].values
                            print("necessary_timestamps_list")
                            print(necessary_timestamps_list)

                            # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume4"
                            # try:
                            #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                            #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                            # except:
                            #     traceback.print_exc()

                            exchange="empty_string"
                            if len(necessary_timestamps_list) > 0:
                                exchange = ticker_with_low_volume.split("_on_")[1]
                                exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume.append(
                                    exchange)

                            if "ath" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                list_of_possible_aths_on_other_exchanges = []
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume={}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    # print("ohlcv_df_low_volume3")
                                    # print(ohlcv_df_low_volume.to_string())
                                    print("necessary_timestamps_list2")
                                    print(necessary_timestamps_list)
                                    possible_high_of_bsu = ohlcv_df_low_volume.loc[
                                        ohlcv_df_low_volume[
                                            "Timestamp"] == possible_timestamp_of_bsu_on_other_exchanges, 'high'].values
                                    list_of_possible_aths_on_other_exchanges.append(possible_high_of_bsu)

                                    dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume[
                                        possible_high_of_bsu[0]]=possible_timestamp_of_bsu_on_other_exchanges
                                    print(" possible_high_of_bsu[0]")
                                    print( possible_high_of_bsu[0])
                                high_on_other_exchange = max(list_of_possible_aths_on_other_exchanges)
                                high_on_other_exchange = high_on_other_exchange[0]
                                list_of_highs_on_low_volume_exchanges.append(high_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange=0
                                if check_if_list_has_all_idential_values(list_of_highs_on_low_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange=min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange=\
                                        dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume[high_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_ath=find_row_number(ohlcv_df_low_volume, timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_ath")
                                print(row_number_of_ath)

                                number_of_days_where_ath_was_not_broken = 2 * 366
                                ath_is_not_broken_for_a_long_time = check_ath_breakout_df_is_argument(ohlcv_df_low_volume,
                                                                                                      number_of_days_where_ath_was_not_broken,
                                                                                                      high_on_other_exchange,
                                                                                                      row_number_of_ath)

                                if ath_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_ath_was_not_broken_low_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_ath_was_broken_low_volume.append(exchange)

                                # check if high on other exchange was broken for the last two years

                            if "atl" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                list_of_possible_atls_on_other_exchanges = []
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    possible_low_of_bsu = ohlcv_df_low_volume.loc[
                                        ohlcv_df_low_volume[
                                            "Timestamp"] == possible_timestamp_of_bsu_on_other_exchanges, 'low'].values
                                    list_of_possible_atls_on_other_exchanges.append(possible_low_of_bsu)
                                    dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume[
                                        possible_low_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                low_on_other_exchange = min(list_of_possible_atls_on_other_exchanges)
                                low_on_other_exchange = low_on_other_exchange[0]
                                list_of_lows_on_low_volume_exchanges.append(low_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_lows_on_low_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume[
                                            low_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_atl = find_row_number(ohlcv_df_low_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_atl")
                                print(row_number_of_atl)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                atl_is_not_broken_for_a_long_time = check_atl_breakout_df_is_argument(
                                    ohlcv_df_low_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    low_on_other_exchange,
                                    row_number_of_atl)

                                if atl_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_atl_was_not_broken_low_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_atl_was_broken_low_volume.append(exchange)

                        string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = "_".join(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume)
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = len(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume)

                        if "ath" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_highs_on_low_volume_exchanges = [str(element) for element in
                                                                                   list_of_highs_on_low_volume_exchanges]
                            string_of_highs_for_this_bsu_on_low_volume_exchanges = "_".join(
                                list_string_values_of_highs_on_low_volume_exchanges)
                            print("list_string_values_of_highs_on_low_volume_exchanges")
                            print(list_string_values_of_highs_on_low_volume_exchanges)

                            list_string_values_of_exchanges_where_ath_was_broken_low_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_ath_was_broken_low_volume]
                            string_of_of_exchanges_where_ath_was_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_broken_low_volume)

                            list_string_values_of_exchanges_where_ath_was_not_broken_low_volume = [str(element) for
                                                                                                   element
                                                                                                   in
                                                                                                   list_of_exchanges_where_ath_was_not_broken_low_volume]
                            string_of_of_exchanges_where_ath_was_not_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_not_broken_low_volume)


                        if "atl" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_lows_on_low_volume_exchanges = [str(element) for element in
                                                                                  list_of_lows_on_low_volume_exchanges]
                            string_of_lows_for_this_bsu_on_low_volume_exchanges = "_".join(
                                list_string_values_of_lows_on_low_volume_exchanges)

                            print("list_string_values_of_lows_on_low_volume_exchanges")
                            print(list_string_values_of_lows_on_low_volume_exchanges)

                            list_string_values_of_exchanges_where_atl_was_broken_low_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_atl_was_broken_low_volume]
                            string_of_of_exchanges_where_atl_was_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_broken_low_volume)

                            list_string_values_of_exchanges_where_atl_was_not_broken_low_volume = [str(element) for
                                                                                                   element
                                                                                                   in
                                                                                                   list_of_exchanges_where_atl_was_not_broken_low_volume]
                            string_of_of_exchanges_where_atl_was_not_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_not_broken_low_volume)

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume5"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_plus_normal_volume = \
                        "_".join(filter(None, [string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume,
                                           string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume]))

                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume = \
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume + \
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume
                    print("number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume")
                    print(number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume)



                    # string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges=\
                    #     string_of_lows_for_this_bsu_on_normal_volume_exchanges + "_" +\
                    #     string_of_lows_for_this_bsu_on_low_volume_exchanges
                    # string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges = \
                    #     string_of_highs_for_this_bsu_on_normal_volume_exchanges + "_" + \
                    #     string_of_highs_for_this_bsu_on_low_volume_exchanges
                    string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_lows_for_this_bsu_on_normal_volume_exchanges,
                                               string_of_lows_for_this_bsu_on_low_volume_exchanges]))
                    string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_highs_for_this_bsu_on_normal_volume_exchanges,
                                               string_of_highs_for_this_bsu_on_low_volume_exchanges]))

                    string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_atl_was_broken_low_volume,
                                               string_of_of_exchanges_where_atl_was_broken_normal_volume]))
                    string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_ath_was_broken_low_volume,
                                               string_of_of_exchanges_where_ath_was_broken_normal_volume]))

                    string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_atl_was_not_broken_low_volume,
                                               string_of_of_exchanges_where_atl_was_not_broken_normal_volume]))
                    string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_ath_was_not_broken_low_volume,
                                               string_of_of_exchanges_where_ath_was_not_broken_normal_volume]))

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume6"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_from_where_pair_was_traded_at_bsu_time = '{string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_plus_normal_volume}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_pair_was_traded_at_bsu_time = '{number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET highs_for_this_bsu_on_all_exchanges_from_two_dbs = '{string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        except:
                            traceback.print_exc()


                    ########--------------------##############



                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_broken = '{string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))

                            string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_broken =
                                 '{string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges}' 
                                 WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))

                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_broken = '{string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))

                            string_of_number_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_broken =
                                 '{string_of_number_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges}' 
                                 WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))

                        except:
                            traceback.print_exc()

                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_not_broken = '{string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_not_broken =
                                 '{string_of_number_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges}' 
                                 WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))


                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_not_broken = '{string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_not_broken =
                                 '{string_of_number_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges}' 
                                 WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))

                        except:
                            traceback.print_exc()


######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


                # check if ticker is in ohlcv database with low volume
                elif ticker_in_bfr_table in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                    # pair is in db with low volume
                    print(f"ticker={ticker_in_bfr_table} is in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume")

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume1"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    starts_with_this_trading_pair = ticker_in_bfr_table.split("_on_")[0]
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = []
                    list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = []
                    joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker = []

                    try:
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker = \
                            remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                                list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume,
                                starts_with_this_trading_pair)
                    except:
                        traceback.print_exc()
                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume8"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume10"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()
                    try:
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker = \
                            remove_other_pairs_from_the_list_of_trading_pair_and_leave_only_pairs_that_start_with_a_certain_pattern(
                                list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume,
                                starts_with_this_trading_pair)
                    except:
                        traceback.print_exc()

                    joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker = \
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker + \
                        list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker

                    print(
                        "joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker")
                    print(
                        joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker)

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume9"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    exchanges_from_two_db_where_pair_is_traded = []
                    for ticker in joint_list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_and_low_volume_starts_with_ticker:
                        exchange = ticker.split("_on_")[1]
                        exchanges_from_two_db_where_pair_is_traded.append(exchange)
                    string_of_exchanges_from_two_dbs_where_pair_is_traded = "_".join(
                        exchanges_from_two_db_where_pair_is_traded)
                    number_of_exchanges_from_two_dbs_where_pair_is_traded = len(
                        exchanges_from_two_db_where_pair_is_traded)


                    # volume_by_low_value=get_volume_low_value(ohlcv_df_normal_volume, timestamp_of_false_breakout_bar)
                    print(
                        f"low volume string_of_exchanges_from_two_dbs_where_pair_is_traded1 for {table_name_in_bfr_database}")
                    print(string_of_exchanges_from_two_dbs_where_pair_is_traded)
                    print("number_of_exchanges_from_two_dbs_where_pair_is_traded2")
                    print(number_of_exchanges_from_two_dbs_where_pair_is_traded)

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume2"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    print("ticker_in_bfr_table")
                    print(ticker_in_bfr_table)
                    print("table_name_in_bfr_database8")
                    print(table_name_in_bfr_database)
                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET string_of_exchanges_from_two_dbs_where_pair_is_traded = '{string_of_exchanges_from_two_dbs_where_pair_is_traded}' WHERE ticker = '{ticker_in_bfr_table}' '''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_from_two_dbs_where_pair_is_traded = '{number_of_exchanges_from_two_dbs_where_pair_is_traded}' WHERE ticker = '{ticker_in_bfr_table}' '''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume=""
                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume=""
                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume=0
                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume=0
                    string_of_highs_for_this_bsu_on_normal_volume_exchanges=""
                    string_of_highs_for_this_bsu_on_low_volume_exchanges=""
                    string_of_lows_for_this_bsu_on_normal_volume_exchanges=""
                    string_of_lows_for_this_bsu_on_low_volume_exchanges=""

                    string_of_of_exchanges_where_ath_was_broken_low_volume = ""
                    string_of_of_exchanges_where_atl_was_broken_low_volume = ""
                    string_of_of_exchanges_where_ath_was_broken_normal_volume = ""
                    string_of_of_exchanges_where_atl_was_broken_normal_volume = ""

                    string_of_of_exchanges_where_ath_was_not_broken_low_volume = ""
                    string_of_of_exchanges_where_atl_was_not_broken_low_volume = ""
                    string_of_of_exchanges_where_ath_was_not_broken_normal_volume = ""
                    string_of_of_exchanges_where_atl_was_not_broken_normal_volume = ""

                    #####################################
                    # normal volume
                    ####################################


                    if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker)>0:
                        exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume = []
                        list_of_highs_on_normal_volume_exchanges = []
                        list_of_lows_on_normal_volume_exchanges = []
                        list_of_exchanges_where_ath_was_broken_normal_volume = []
                        list_of_exchanges_where_ath_was_not_broken_normal_volume = []
                        list_of_exchanges_where_atl_was_not_broken_normal_volume = []
                        list_of_exchanges_where_atl_was_broken_normal_volume = []
                        for ticker_with_normal_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume_starts_with_ticker:
                            # ohlcv_df_normal_volume = \
                            #     pd.read_sql_query(f'''select * from "{ticker_with_normal_volume}"''',
                            #                       engine_for_ohlcv_data_for_stocks_normal_volume)

                            ohlcv_df_normal_volume = dict_with_ohlcv_dataframes_for_tickers_with_normal_volume[
                                ticker_with_normal_volume]
                            # Find the necessary timestamp within the range
                            necessary_timestamps_list = ohlcv_df_normal_volume.loc[
                                ohlcv_df_normal_volume['Timestamp'].between(timestamp_of_bsu_left_edge,
                                                                            timestamp_of_bsu_right_edge,
                                                                            inclusive='neither'), 'Timestamp'].values
                            print("necessary_timestamps_list")
                            print(necessary_timestamps_list)

                            exchange="empty_string"
                            if len(necessary_timestamps_list)>0:
                                exchange = ticker_with_normal_volume.split("_on_")[1]
                                exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume.append(exchange)


                            if "ath" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                list_of_possible_aths_on_other_exchanges=[]
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    # print("ohlcv_df_normal_volume.to_string()")
                                    # print(ohlcv_df_normal_volume.to_string())
                                    possible_high_of_bsu=ohlcv_df_normal_volume.loc[ohlcv_df_normal_volume["Timestamp"]==possible_timestamp_of_bsu_on_other_exchanges, 'high'].values

                                    print("possible_high_of_bsu")
                                    print(possible_high_of_bsu)
                                    list_of_possible_aths_on_other_exchanges.append(possible_high_of_bsu)
                                    dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume[
                                        possible_high_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                high_on_other_exchange=max(list_of_possible_aths_on_other_exchanges)
                                high_on_other_exchange=high_on_other_exchange[0]
                                print('high_on_other_exchange')
                                print(high_on_other_exchange)
                                list_of_highs_on_normal_volume_exchanges.append(high_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_highs_on_normal_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume[
                                            high_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_ath = find_row_number(ohlcv_df_normal_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_ath")
                                print(row_number_of_ath)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                ath_is_not_broken_for_a_long_time = check_ath_breakout_df_is_argument(
                                    ohlcv_df_normal_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    high_on_other_exchange,
                                    row_number_of_ath)

                                if ath_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_ath_was_not_broken_normal_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_ath_was_broken_normal_volume.append(exchange)

                            if "atl" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_normal_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume = {}
                                list_of_possible_atls_on_other_exchanges=[]
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    possible_low_of_bsu=ohlcv_df_normal_volume.loc[ohlcv_df_normal_volume["Timestamp"]==possible_timestamp_of_bsu_on_other_exchanges, 'low'].values
                                    list_of_possible_atls_on_other_exchanges.append(possible_low_of_bsu)
                                    dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume[
                                        possible_low_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                low_on_other_exchange=min(list_of_possible_atls_on_other_exchanges)
                                low_on_other_exchange=low_on_other_exchange[0]
                                list_of_lows_on_normal_volume_exchanges.append(low_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_lows_on_normal_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_normal_volume[
                                            low_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_atl = find_row_number(ohlcv_df_normal_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_atl")
                                print(row_number_of_atl)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                atl_is_not_broken_for_a_long_time = check_atl_breakout_df_is_argument(
                                    ohlcv_df_normal_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    low_on_other_exchange,
                                    row_number_of_atl)

                                if atl_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_atl_was_not_broken_normal_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_atl_was_broken_normal_volume.append(exchange)

                        string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = "_".join(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume)
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume = len(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_normal_volume)
                        if "ath" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_highs_on_normal_volume_exchanges = [str(element) for element in list_of_highs_on_normal_volume_exchanges]
                            string_of_highs_for_this_bsu_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_highs_on_normal_volume_exchanges)
                            print("list_string_values_of_highs_on_normal_volume_exchanges")
                            print(list_string_values_of_highs_on_normal_volume_exchanges)

                            list_string_values_of_exchanges_where_ath_was_broken = [str(element) for element in
                                                                                    list_of_exchanges_where_ath_was_broken_normal_volume]
                            string_of_exchanges_where_ath_was_broken_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_exchanges_where_ath_was_broken)

                            list_string_values_of_exchanges_where_ath_was_not_broken = [str(element) for element in
                                                                                    list_of_exchanges_where_ath_was_not_broken_normal_volume]
                            string_of_exchanges_where_ath_was_not_broken_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_exchanges_where_ath_was_not_broken)

                        if "atl" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_lows_on_normal_volume_exchanges = [str(element) for element in list_of_lows_on_normal_volume_exchanges]
                            string_of_lows_for_this_bsu_on_normal_volume_exchanges = "_".join(
                                list_string_values_of_lows_on_normal_volume_exchanges)
                            print("list_string_values_of_lows_on_normal_volume_exchanges")
                            print(list_string_values_of_lows_on_normal_volume_exchanges)

                            list_string_values_of_exchanges_where_atl_was_broken_normal_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_atl_was_broken_normal_volume]
                            string_of_of_exchanges_where_atl_was_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_broken_normal_volume)

                            list_string_values_of_exchanges_where_atl_was_not_broken_normal_volume = [str(element) for
                                                                                                   element
                                                                                                   in
                                                                                                   list_of_exchanges_where_atl_was_not_broken_normal_volume]
                            string_of_of_exchanges_where_atl_was_not_broken_normal_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_not_broken_normal_volume)

                        # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume3"
                        # try:
                        #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                        #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        # except:
                        #     traceback.print_exc()

                    ############################
                    # low_volume
                    ###############################



                    if len(list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker) > 0:

                        # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume7"
                        # try:
                        #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                        #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        # except:
                        #     traceback.print_exc()
                        exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume = []
                        list_of_highs_on_low_volume_exchanges = []
                        list_of_lows_on_low_volume_exchanges = []
                        list_of_exchanges_where_ath_was_not_broken_low_volume = []
                        list_of_exchanges_where_ath_was_broken_low_volume = []
                        list_of_exchanges_where_atl_was_not_broken_low_volume = []
                        list_of_exchanges_where_atl_was_broken_low_volume = []
                        for ticker_with_low_volume in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume_starts_with_ticker:
                            # ohlcv_df_low_volume = \
                            #     pd.read_sql_query(f'''select * from "{ticker_with_low_volume}"''',
                            #                       engine_for_ohlcv_data_for_stocks_low_volume)

                            ohlcv_df_low_volume = dict_with_ohlcv_dataframes_for_tickers_with_low_volume[
                                ticker_with_low_volume]

                            # Find the necessary timestamp within the range
                            necessary_timestamps_list = ohlcv_df_low_volume.loc[
                                ohlcv_df_low_volume['Timestamp'].between(timestamp_of_bsu_left_edge,
                                                                            timestamp_of_bsu_right_edge,
                                                                            inclusive='neither'), 'Timestamp'].values
                            print("necessary_timestamps_list")
                            print(necessary_timestamps_list)

                            # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume4"
                            # try:
                            #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                            #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                            # except:
                            #     traceback.print_exc()

                            exchange="empty_string"
                            if len(necessary_timestamps_list) > 0:
                                exchange = ticker_with_low_volume.split("_on_")[1]
                                exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume.append(
                                    exchange)

                            if "ath" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                list_of_possible_aths_on_other_exchanges = []
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    # print("ohlcv_df_low_volume3")
                                    # print(ohlcv_df_low_volume.to_string())
                                    print("necessary_timestamps_list2")
                                    print(necessary_timestamps_list)
                                    possible_high_of_bsu = ohlcv_df_low_volume.loc[
                                        ohlcv_df_low_volume["Timestamp"]==possible_timestamp_of_bsu_on_other_exchanges, 'high'].values
                                    list_of_possible_aths_on_other_exchanges.append(possible_high_of_bsu)
                                    dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume[
                                        possible_high_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                high_on_other_exchange = max(list_of_possible_aths_on_other_exchanges)
                                high_on_other_exchange=high_on_other_exchange[0]
                                list_of_highs_on_low_volume_exchanges.append(high_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_highs_on_low_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume[
                                            high_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_ath = find_row_number(ohlcv_df_low_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_ath")
                                print(row_number_of_ath)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                ath_is_not_broken_for_a_long_time = check_ath_breakout_df_is_argument(
                                    ohlcv_df_low_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    high_on_other_exchange,
                                    row_number_of_ath)

                                if ath_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_ath_was_not_broken_low_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_ath_was_broken_low_volume.append(exchange)

                            if "atl" in table_name_in_bfr_database_df.columns and len(necessary_timestamps_list)>0:
                                list_of_possible_atls_on_other_exchanges = []
                                dict_of_possible_aths_on_other_exchanges_ath_is_key_timestamp_is_value_low_volume = {}
                                dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume = {}
                                for possible_timestamp_of_bsu_on_other_exchanges in necessary_timestamps_list:
                                    possible_low_of_bsu = ohlcv_df_low_volume.loc[
                                        ohlcv_df_low_volume["Timestamp"]==possible_timestamp_of_bsu_on_other_exchanges, 'low'].values
                                    list_of_possible_atls_on_other_exchanges.append(possible_low_of_bsu)
                                    dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume[
                                        possible_low_of_bsu[0]] = possible_timestamp_of_bsu_on_other_exchanges
                                low_on_other_exchange = min(list_of_possible_atls_on_other_exchanges)
                                low_on_other_exchange=low_on_other_exchange[0]
                                list_of_lows_on_low_volume_exchanges.append(low_on_other_exchange)

                                timestamp_of_bsu_on_other_exchange = 0
                                if check_if_list_has_all_idential_values(list_of_lows_on_low_volume_exchanges):
                                    timestamp_of_bsu_on_other_exchange = min(necessary_timestamps_list)
                                else:
                                    timestamp_of_bsu_on_other_exchange = \
                                        dict_of_possible_atls_on_other_exchanges_atl_is_key_timestamp_is_value_low_volume[
                                            low_on_other_exchange]

                                print("timestamp_of_bsu_on_other_exchange")
                                print(timestamp_of_bsu_on_other_exchange)
                                row_number_of_atl = find_row_number(ohlcv_df_low_volume,
                                                                    timestamp_of_bsu_on_other_exchange)
                                print("row_number_of_atl")
                                print(row_number_of_atl)

                                number_of_days_where_atl_was_not_broken = 2 * 366
                                atl_is_not_broken_for_a_long_time = check_atl_breakout_df_is_argument(
                                    ohlcv_df_low_volume,
                                    number_of_days_where_atl_was_not_broken,
                                    low_on_other_exchange,
                                    row_number_of_atl)

                                if atl_is_not_broken_for_a_long_time:
                                    list_of_exchanges_where_atl_was_not_broken_low_volume.append(exchange)
                                else:
                                    list_of_exchanges_where_atl_was_broken_low_volume.append(exchange)

                        string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = "_".join(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume)
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume = len(
                            exchanges_from_two_db_where_pair_is_traded_for_this_bsu_list_low_volume)


                        if "ath" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_highs_on_low_volume_exchanges = [str(element) for element in list_of_highs_on_low_volume_exchanges]
                            string_of_highs_for_this_bsu_on_low_volume_exchanges = "_".join(
                                list_string_values_of_highs_on_low_volume_exchanges)
                            print("list_string_values_of_highs_on_low_volume_exchanges")
                            print(list_string_values_of_highs_on_low_volume_exchanges)

                            list_string_values_of_exchanges_where_ath_was_broken_low_volume = [str(element) for element in
                                                                                   list_of_exchanges_where_ath_was_broken_low_volume]
                            string_of_of_exchanges_where_ath_was_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_broken_low_volume)

                            print("list_of_exchanges_where_ath_was_not_broken_low_volume")
                            print(list_of_exchanges_where_ath_was_not_broken_low_volume)
                            list_string_values_of_exchanges_where_ath_was_not_broken_low_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_ath_was_not_broken_low_volume]
                            string_of_of_exchanges_where_ath_was_not_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_ath_was_not_broken_low_volume)

                        if "atl" in table_name_in_bfr_database_df.columns:
                            list_string_values_of_lows_on_low_volume_exchanges = [str(element) for element in list_of_lows_on_low_volume_exchanges]
                            string_of_lows_for_this_bsu_on_low_volume_exchanges = "_".join(
                                list_string_values_of_lows_on_low_volume_exchanges)

                            print("list_string_values_of_lows_on_low_volume_exchanges")
                            print(list_string_values_of_lows_on_low_volume_exchanges)

                            list_string_values_of_exchanges_where_atl_was_broken_low_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_atl_was_broken_low_volume]
                            string_of_of_exchanges_where_atl_was_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_broken_low_volume)

                            list_string_values_of_exchanges_where_atl_was_not_broken_low_volume = [str(element) for element
                                                                                               in
                                                                                               list_of_exchanges_where_atl_was_not_broken_low_volume]
                            string_of_of_exchanges_where_atl_was_not_broken_low_volume = "_".join(
                                list_string_values_of_exchanges_where_atl_was_not_broken_low_volume)

                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume5"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_plus_normal_volume=\
                        "_".join(filter(None, [string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume,
                                           string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume]))


                    number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume=\
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_volume+\
                        number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_volume
                    print("number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume")
                    print(number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume)

                    # string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges=\
                    #     string_of_lows_for_this_bsu_on_normal_volume_exchanges + "_" +\
                    #     string_of_lows_for_this_bsu_on_low_volume_exchanges
                    # string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges = \
                    #     string_of_highs_for_this_bsu_on_normal_volume_exchanges + "_" + \
                    #     string_of_highs_for_this_bsu_on_low_volume_exchanges
                    string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_lows_for_this_bsu_on_normal_volume_exchanges,
                                               string_of_lows_for_this_bsu_on_low_volume_exchanges]))
                    string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges=\
                        "_".join(filter(None, [string_of_highs_for_this_bsu_on_normal_volume_exchanges,
                                               string_of_highs_for_this_bsu_on_low_volume_exchanges]))

                    string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_atl_was_broken_low_volume,
                                               string_of_of_exchanges_where_atl_was_broken_normal_volume]))
                    string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_ath_was_broken_low_volume,
                                               string_of_of_exchanges_where_ath_was_broken_normal_volume]))

                    string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_atl_was_not_broken_low_volume,
                                               string_of_of_exchanges_where_atl_was_not_broken_normal_volume]))
                    string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges = \
                        "_".join(filter(None, [string_of_of_exchanges_where_ath_was_not_broken_low_volume,
                                               string_of_of_exchanges_where_ath_was_not_broken_normal_volume]))



                    # one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1 = "test_string_low_volume6"
                    # try:
                    #     query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{one_string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges1}' WHERE ticker = '{ticker}' '''
                    #     connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    # except:
                    #     traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_from_where_pair_was_traded_at_bsu_time = '{string_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_low_plus_normal_volume}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    try:
                        query = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_pair_was_traded_at_bsu_time = '{number_of_exchanges_from_two_dbs_where_pair_was_traded_for_this_bsu_normal_plus_low_volume}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                        connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                    except:
                        traceback.print_exc()

                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET highs_for_this_bsu_on_all_exchanges_from_two_dbs = '{string_of_highs_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET lows_for_this_bsu_on_all_exchanges_from_two_dbs = '{string_of_lows_for_this_bsu_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(query))
                        except:
                            traceback.print_exc()

                    # try:
                    #     select_query = f'''SELECT number_of_exchanges_where_pair_was_traded_at_bsu_time from public."{table_name_in_bfr_database}"  WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                    #     number_of_exchanges_where_pair_was_traded_at_bsu_time_cursor=\
                    #         connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(text(select_query))
                    #     print("number_of_exchanges_where_pair_was_traded_at_bsu_time_cursor")
                    #     print(number_of_exchanges_where_pair_was_traded_at_bsu_time_cursor)
                    #     number_of_exchanges_where_pair_was_traded_at_bsu_time_selected = number_of_exchanges_where_pair_was_traded_at_bsu_time_cursor.fetchone()[0]
                    #     print("number_of_exchanges_where_pair_was_traded_at_bsu_time_selected")
                    #     print(number_of_exchanges_where_pair_was_traded_at_bsu_time_selected)
                    #
                    #     if pd.isna(number_of_exchanges_where_pair_was_traded_at_bsu_time_selected):
                    #         print(f"{ticker_in_bfr_table} is NULL")
                    #         time.sleep(100000)
                    # except:
                    #     traceback.print_exc()

                    ##############------------------------#############
                    ########--------------------##############

                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_broken = '{string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges=\
                                count_number_of_values_between_underscores_in_a_string(
                                string_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_broken =
                             '{string_of_number_of_exchanges_where_ath_was_broken_on_normal_plus_low_volume_exchanges}' 
                             WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))


                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_broken = '{string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_broken =
                                                         '{string_of_number_of_exchanges_where_atl_was_broken_on_normal_plus_low_volume_exchanges}' 
                                                         WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))


                        except:
                            traceback.print_exc()

                    if "ath" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_not_broken = '{string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_not_broken =
                                                                                     '{string_of_number_of_exchanges_where_ath_was_not_broken_on_normal_plus_low_volume_exchanges}' 
                                                                                     WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))

                        except:
                            traceback.print_exc()

                    if "atl" in table_name_in_bfr_database_df.columns:
                        try:
                            query = f'''UPDATE public."{table_name_in_bfr_database}" SET exchanges_where_ath_or_atl_were_not_broken = '{string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges}' WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query))

                            string_of_number_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges = \
                                count_number_of_values_between_underscores_in_a_string(
                                    string_of_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges)
                            query2 = f'''UPDATE public."{table_name_in_bfr_database}" SET number_of_exchanges_where_ath_or_atl_were_not_broken =
                                                                                                                 '{string_of_number_of_exchanges_where_atl_was_not_broken_on_normal_plus_low_volume_exchanges}' 
                                                                                                                 WHERE ticker = '{ticker_in_bfr_table}' and timestamp_of_bsu={timestamp_of_bsu}'''
                            connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.execute(
                                text(query2))


                        except:
                            traceback.print_exc()




                elif  ticker_in_bfr_table in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume and \
                        ticker_in_bfr_table in list_of_tables_in_database_of_ohlcv_data_for_stocks_low_volume:
                        print(f"{ticker_in_bfr_table} is both in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                              f"and list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")
                else:
                    print(f"{ticker_in_bfr_table} is neither in list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume "
                          f"nor list_of_tables_in_database_of_ohlcv_data_for_stocks_normal_volume")


        else:
            continue
    connection_to_levels_formed_by_highs_and_lows_for_cryptos_0000_hist.close()
    connection_to_ohlcv_data_for_stocks_low_volume.close()
    connection_to_ohlcv_data_for_stocks_normal_volume.close()


if __name__=="__main__":
    start_time = time.time()  # start timer 
    
    add_exchanges_where_pair_was_traded_to_column_in_bfr_tables()
    
    end_time = time.time()  # end timer
    elapsed_time = end_time - start_time  # calculate elapsed time

    elapsed_time_seconds = int(elapsed_time)
    elapsed_time_minutes, elapsed_time_seconds = divmod(elapsed_time_seconds, 60)
    elapsed_time_hours, elapsed_time_minutes = divmod(elapsed_time_minutes, 60)

    print(f"Elapsed time: {elapsed_time_hours} hours, {elapsed_time_minutes} minutes, {elapsed_time_seconds} seconds")
