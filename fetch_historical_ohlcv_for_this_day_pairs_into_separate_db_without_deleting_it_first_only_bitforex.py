# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
import asyncio
import os
import sys
import time
import traceback
import db_config
import sqlalchemy
import psycopg2
import pandas as pd
# from current_search_for_tickers_with_breakout_situations_of_atl_position_entry_on_day_two import get_bool_if_asset_is_traded_with_margin
# import talib
import datetime
import ccxt
# import ccxt.async_support as ccxt  # noqa: E402

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from pytz import timezone
import pprint
from verify_that_asset_has_enough_volume import check_volume
from get_info_from_load_markets import get_asset_type2
from get_info_from_load_markets import if_margin_true_for_an_asset
# from fetch_historical_USDT_pairs_for_1D_delete_first_primary_db_and_delete_low_volume_db import remove_values_from_list
from get_info_from_load_markets import get_fees
from get_info_from_load_markets import fetch_huobipro_ohlcv
from get_info_from_load_markets import get_active_trading_pairs_from_huobipro
from get_info_from_load_markets import get_exchange_object_and_limit_of_daily_candles
from get_info_from_load_markets import get_exchange_object
from get_info_from_load_markets import get_exchange_url
from get_info_from_load_markets import get_maker_taker_fees_for_huobi
from get_info_from_load_markets import get_limit_of_daily_candles_original_limits
from get_info_from_load_markets import fetch_entire_ohlcv
from get_info_from_load_markets import get_perpetual_swap_url
from constant_update_of_ohlcv_db_to_plot_later import get_list_of_exchange_ids_for_todays_pairs
from constant_update_of_ohlcv_db_to_plot_later import get_list_of_todays_trading_pairs
from get_info_from_load_markets import get_exchange_object6
from async_update_historical_USDT_pairs_for_1D import get_list_of_tables_in_db
from async_update_historical_USDT_pairs_for_1D import connect_to_postgres_db_without_deleting_it_first

def get_maker_and_taker_fees_and_is_shortable(exchange, trading_pair):

    maker_fee=np.nan
    taker_fee=np.nan
    is_shortable=np.nan

    # Get the symbol for the specified trading pair
    symbol = exchange.markets[trading_pair]['symbol']

    # Check if API keys are required for the exchange
    if exchange.apiKey is None or exchange.secret is None:
        return maker_fee, taker_fee, is_shortable
    
    # Retrieve the exchange info for the specified symbol
    exchange_info = exchange.load_trading_limits(symbol)
    print(f"exchange_info_for_{symbol}")
    pprint.pprint(exchange_info)
    #
    # print("exchange.markets[symbol]")
    # pprint.pprint(exchange.markets[symbol])

    # Extract the maker and taker fees
    maker_fee = exchange_info['maker']
    taker_fee = exchange_info['taker']



    # Check if the symbol is shortable
    is_shortable = exchange.markets[symbol].get('short', False)


    # Return the results as a tuple
    return maker_fee, taker_fee, is_shortable

def connect_to_postgres_db_with_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database
    connection=None

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )
        try:
            connection=engine.connect ()
        except:
            traceback.print_exc()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )

    try:
        connection = engine.connect ()
    except:
        traceback.print_exc()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def add_time_of_next_candle_print_to_df(data_df):
    try:
        # Set the timezone for Moscow
        moscow_tz = timezone('Europe/Moscow')
        almaty_tz = timezone('Asia/Almaty')
        data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
        data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
        # Convert the "open_time" column from UTC to Moscow time
        data_df['open_time_msk'] =\
            data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)

        data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')

        # Convert the "open_time_datatime_format" column from UTC to Almaty time
        data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')

        # Create a new column called "open_time_almaty_time" that contains the time in string format
        data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
    except:
        traceback.print_exc()

def connect_to_postgres_db_with_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        create_database ( engine.url )
        print ( f'new database created for {engine}' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def check_if_stable_coin_is_the_first_part_of_ticker(trading_pair):
    trading_pair_has_stable_coin_name_as_its_first_part=False
    stablecoin_tickers = [
    "USDT_","USDC_","BUSD_","DAI_","FRAX_","TUSD_","USDP_","USDD_",
    "GUSD_","XAUT_","USTC_","EURT_","LUSD_","ALUSD_","EURS_","USDX_",
    "MIM_","sEUR_","WBTC_","sGBP_","sJPY_","sKRW_","sAUD_","GEM_",
    "sXAG_","sXAU_","sXDR_","sBTC_","sETH_","sCNH_","sCNY_","sHKD_",
    "sSGD_","sCHF_","sCAD_","sNZD_","sLTC_","sBCH_","sBNB_","sXRP_",
    "sADA_","sLINK_","sXTZ_","sDOT_","sFIL_","sYFI_","sCOMP_","sAAVE_",
    "sSNX_","sMKR_","sUNI_","sBAL_","sCRV_","sLEND_","sNEXO_","sUMA_",
    "sMUST_","sSTORJ_","sREN_","sBSV_","sDASH_","sZEC_","sEOS_","sXTZ_",
    "sATOM_","sVET_","sTRX_","sADA_","sDOGE_","sDGB_"
]

    for first_part_in_trading_pair in stablecoin_tickers:
        if first_part_in_trading_pair in trading_pair:
            trading_pair_has_stable_coin_name_as_its_first_part=True
            break
        else:
            continue
    return trading_pair_has_stable_coin_name_as_its_first_part




new_counter=0
not_active_pair_counter = 0
list_of_inactive_pairs=[]

def get_hisorical_data_from_exchange_for_many_symbols(last_bitcoin_price,exchange,
                                                            engine,
                                                      timeframe,
                                                      list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db):
    print("exchange=",exchange)
    global new_counter
    global list_of_inactive_pairs
    global not_active_pair_counter
    exchange_object=""
    limit_of_daily_candles=1000
    active_trading_pairs_list=[]
    # active_trading_pairs_list_from_huobipro=[]
    try:
        # active_trading_pairs_list_from_huobipro=[]
        # if exchange in ["huobipro"]:
        #     active_trading_pairs_list_from_huobipro = get_active_trading_pairs_from_huobipro()
        exchange_object=get_exchange_object6(exchange)
        exchange_object.enableRateLimit=True
        # exchange_object.fetch_markets()
        # exchange_object_huobipro=np.nan

        # if exchange in ['huobipro']:
        #     exchange_object_huobipro= ccxt.huobipro()
        # shortable_markets=''
        # try:
        #     # shortable_markets = [market['symbol'] for market in markets if market.get('margin', {}).get('short', False)]
        #     # shortable_markets = [market['symbol'] for market in markets if
        #     #                      'margin' in market and market['margin'].get('short', False)]
        #     shortable_markets = [market['symbol'] for market in markets if
        #                          'margin_enabled' in market and market['margin_enabled']]
        # except:
        #     traceback.print_exc()
        # print(f"shortable_markets for {exchange}")
        # print(shortable_markets)
    except:
        traceback.print_exc()

    try:
        # connection_to_usdt_trading_pairs_ohlcv = \
        #     sqlite3.connect ( os.path.join ( os.getcwd () ,
        #                                      "datasets" ,
        #                                      "sql_databases" ,
        #                                      "all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )
        markets=np.nan
        try:
            markets=exchange_object.load_markets ()
        except:
                        traceback.print_exc()
        # print("markets___")
        # pprint.pprint(markets)
        # time.sleep(10000)





        list_of_all_symbols_from_exchange=exchange_object.symbols
        print(f"list_of_all_symbols_from_exchange={exchange}")
        print(list_of_all_symbols_from_exchange)

        list_of_trading_pairs_with_USDT = []
        list_of_trading_pairs_with_USD = []
        list_of_trading_pairs_with_BTC = []


        # if exchange in ["huobipro"]:
        #     list_of_all_symbols_from_exchange=active_trading_pairs_list_from_huobipro

        database_name1 = 'levels_formed_by_highs_and_lows_for_cryptos_0000'
        list_of_todays_trading_pairs_in_db_with_models=get_list_of_todays_trading_pairs(database_name1)

        print("list_of_todays_trading_pairs_in_db_with_models")
        print(list_of_todays_trading_pairs_in_db_with_models)


        print(f"list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db ")
        print(list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db)


        for trading_pair in list_of_all_symbols_from_exchange:
            # for item in counter_gen():
            #     print ("item=",item)

            # print("trading_pair1")
            # print(trading_pair)

            # if trading_pair!="MONG/USDT":
            #     continue

            if trading_pair not in list_of_todays_trading_pairs_in_db_with_models:
                continue
            print("program_got_here21")

            # check if the list of already downloaded pairs in ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs has any pairs
            # from the database levels_formed_by_highs_and_lows_for_cryptos_0000
            string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000=trading_pair.replace("/","_")+"_on_"+exchange
            print("string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000")
            print(string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000)

            if string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000 in list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db:
                continue

            print(f"{string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000} is not in db")




            try:
                print ( "exchange=" , exchange )
                print ( "usdt_pair=" , trading_pair )
                if "UP/" in trading_pair or "DOWN/" in trading_pair or "BEAR/" in \
                        trading_pair or "BULL/" in trading_pair:
                    continue
                # if ("/USDT" in trading_pair) or ("/USDC" in trading_pair) \
                #         or( "/BUSD" in trading_pair) or ( "/BTC" in trading_pair) or\
                #         ( "/HT" in trading_pair)  :
                if "/USDT" in trading_pair:
                    print("usdt_pair1=", trading_pair)
                    new_counter = new_counter + 1
                    print("new_counter=",new_counter)
                    list_of_trading_pairs_with_USDT.append(trading_pair)
                    # print ( f"list_of_trading_pairs_with_USDT_on_{exchange}\n" ,
                    #         list_of_trading_pairs_with_USDT )

                    # if ('active' in exchange_object.markets[trading_pair]) or (exchange_object.markets[trading_pair]['active']):

                    # #collect data from 5 years ago
                    # data = exchange_object.fetch_ohlcv ( trading_pair , timeframe, since=1516147200000)
                    #
                    # collect data from 2011 years ago
                    data_df=pd.DataFrame()

                    # if exchange in ["exmo"]:
                    #     try:
                    #         data = exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=3000)
                    #         # print ( f"counter_for_{exchange}=" , counter )
                    #         header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #         data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    #     except:
                    #         traceback.print_exc()
                    # elif exchange in ["huobipro"]:
                    #     data_df=fetch_huobipro_ohlcv(trading_pair,
                    #                                  exchange_object_huobipro,
                    #                                  timeframe='1d')


                    # elif exchange in ["gateio"]:
                    #     try:
                    #         data = exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=1000)
                    #         # print ( f"counter_for_{exchange}=" , counter )
                    #         header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #         data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    #     except:
                    #         traceback.print_exc()

                    # else:
                    #data = exchange_object.fetch_ohlcv(trading_pair, timeframe, since=1293829200000)
                    asset_type=''
                    if_margin_true_for_an_asset_bool=''
                    spot_asset_is_also_available_as_swap_contract_on_the_same_exchange = False
                    try:
                        asset_type=get_asset_type2(markets, trading_pair.replace("_", "/"))
                        try:
                            if_margin_true_for_an_asset_bool=if_margin_true_for_an_asset(markets, trading_pair.replace("_", "/"))
                        except:
                            traceback.print_exc()
                        print(f"asset_type for {trading_pair} on {exchange}")

                        print(asset_type)


                        if asset_type=="spot":
                            try:
                                from fetch_additional_historical_USDT_pairs_for_1D_without_deleting_primary_db_and_without_deleting_db_with_low_volume import insert_into_df_whether_swap_contract_is_also_available_for_swap
                                spot_asset_is_also_available_as_swap_contract_on_the_same_exchange=insert_into_df_whether_swap_contract_is_also_available_for_swap(data_df,
                                                                                                exchange_object,
                                                                                                markets,
                                                                                                trading_pair)
                            except:
                                traceback.print_exc()

                        if asset_type=="option":
                            continue
                        if asset_type=="future":
                            continue
                        if asset_type=="swap":
                            continue
                    except:
                        traceback.print_exc()



                    # try:
                    #     data = exchange_object.fetch_ohlcv(trading_pair, timeframe,
                    #                                        limit=limit_of_daily_candles)
                    #     # print ( f"counter_for_{exchange}=" , counter )
                    #     header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #     data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    # except:
                    #     traceback.print_exc()

                    # Fetch the most recent 100 days of data for latoken exchange
                    try:
                        # exchange latoken has a specific limit of one request number of candles
                        if isinstance(exchange_object, ccxt.latoken):
                            print("exchange is latoken")
                            limit_of_daily_candles = 100
                    except:
                        traceback.print_exc()

                    # Fetch the most recent 200 days of data bybit exchange
                    try:
                        # exchange bybit has a specific limit of one request number of candles
                        if isinstance(exchange_object, ccxt.bybit):
                            print("exchange is bybit")
                            limit_of_daily_candles = 200
                    except:
                        traceback.print_exc()



                    try:
                        data_df=fetch_entire_ohlcv(exchange_object,exchange,trading_pair,timeframe,limit_of_daily_candles)
                    except:
                        traceback.print_exc()

                    # if exchange in ["huobi", "huobipro"]:
                    #     try:
                    #         data_df=fetch_huobipro_ohlcv(trading_pair, timeframe='1d')
                    #     except:
                    #         traceback.print_exc()

                    # try:
                    #     data_4h = await exchange_object.fetch_ohlcv ( trading_pair , '1d' )
                    #
                    #     data_df_4h = pd.DataFrame ( data_4h , columns = header ).set_index ( 'Timestamp' )
                    #     print(f"data_df_4h_for_{trading_pair} on exchange {exchange}\n",
                    #           data_df_4h)
                    #     data_df_4h['open_time'] = \
                    #         [dt.datetime.fromtimestamp ( x / 1000.0 ) for x in data_df_4h.index]
                    #     data_df_4h.set_index ( 'open_time' )
                    #     # print ( "list_of_dates=\n" , list_of_dates )
                    #     # time.sleep(5)
                    #     data_df_4h['psar'] = talib.SAR ( data_df_4h.high ,
                    #                                   data_df_4h.low ,
                    #                                   acceleration = 0.02 ,
                    #                                   maximum = 0.2 )
                    #     print ( "data_df_4h\n" , data_df_4h )
                    #
                    #     data_df_4h.to_sql ( f"{trading_pair}_on_{exchange}" ,
                    #                      connection_to_usdt_trading_pairs_4h_ohlcv ,
                    #                      if_exists = 'replace' )
                    #
                    #
                    # except Exception as e:
                    #     print("something is wrong with 4h timeframe"
                    #           f"for {trading_pair} on exchange {exchange}\n",e)
                    print ( "=" * 80 )
                    print ( f'ohlcv for {trading_pair} on exchange {exchange}\n' )
                    print ( data_df )

                    # if trading_pair!="BTC/USDT":
                    #     continue





                    trading_pair=trading_pair.replace("/","_")

                    data_df['ticker'] = trading_pair
                    data_df['exchange'] = exchange
                    data_df['trading_pair']=trading_pair+"_on_"+exchange
                    # print("markets[trading_pair]")

                    # print(markets[trading_pair])


                    #if trading pair is traded with margin
                    try:
                        data_df['trading_pair_is_traded_with_margin'] = if_margin_true_for_an_asset_bool
                    except:
                        data_df['trading_pair_is_traded_with_margin'] = np.nan

                    # add asset type to df
                    try:
                        data_df['asset_type'] = asset_type
                    except:
                        data_df['asset_type'] = np.nan
                        traceback.print_exc()

                    # add maker and taker fees
                    try:
                        if exchange!='huobipro':
                            maker_fee, taker_fee=get_fees(markets, trading_pair.replace("_","/"))
                            data_df['maker_fee'] = maker_fee
                            data_df['taker_fee'] = taker_fee

                    except:
                        data_df['maker_fee'] = np.nan
                        data_df['taker_fee'] = np.nan
                        traceback.print_exc()

                    try:
                        if exchange == "huobipro":
                            maker_fee, taker_fee = get_maker_taker_fees_for_huobi(exchange_object)
                            data_df['maker_fee'] = maker_fee
                            data_df['taker_fee'] = taker_fee
                            print("fees for huobi pro")
                            print("maker_fee for huobi")
                            print(maker_fee)
                            print("taker_fee for huobi")
                            print(taker_fee)
                    except:
                        data_df['maker_fee'] = np.nan
                        data_df['taker_fee'] = np.nan
                        traceback.print_exc()

                    # add asset type to df
                    # try:
                    #     data_df['asset_type'] = asset_type
                    # except:
                    #     data_df['asset_type'] = np.nan
                    #     traceback.print_exc()




                    # get info if asset is shortable , get maker and taker fees
                    # try:
                    #     trading_pair_initial = trading_pair.replace("_", "/")
                    #     maker_fee, taker_fee, is_shortable = \
                    #         get_maker_and_taker_fees_and_is_shortable(exchange_object, trading_pair_initial)
                    #     data_df['maker_fee'] = maker_fee
                    #     data_df['taker_fee'] = taker_fee
                    #     data_df['is_shortable'] = is_shortable
                    # except:
                    #     traceback.print_exc()

                    #exclude levereged tockens
                    if "3L" in trading_pair:
                        continue
                    if "3S" in trading_pair:
                        continue

                    if "4L" in trading_pair:
                        continue
                    if "4S" in trading_pair:
                        continue

                    if "5L" in trading_pair:
                        continue
                    if "5S" in trading_pair:
                        continue

                    # add url of trading pair to df
                    try:
                        # market = markets[trading_pair.replace("_", "/")]
                        # market_id = market['id']
                        url_of_trading_pair =\
                            get_exchange_url(exchange, exchange_object, trading_pair.replace("_", "/"))
                        data_df['url_of_trading_pair'] = url_of_trading_pair
                    except:
                        data_df['url_of_trading_pair'] = np.nan
                        traceback.print_exc()

                    try:
                        data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = spot_asset_is_also_available_as_swap_contract_on_the_same_exchange
                    except:
                        data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = np.nan
                        traceback.print_exc()

                    try:
                        if spot_asset_is_also_available_as_swap_contract_on_the_same_exchange:
                            data_df["url_of_swap_contract_if_it_exists"]=get_perpetual_swap_url(exchange, trading_pair.replace("_", "/"))
                            print("url_swap_added")
                        else:
                            data_df["url_of_swap_contract_if_it_exists"] = "swap_of_spot_asset_does_not_exist"
                    except:
                        traceback.print_exc()

                    # add url of trading pair to df
                    if asset_type=='swap':
                        try:

                            url_of_trading_pair = \
                                get_perpetual_swap_url(exchange, trading_pair.replace("_", "/"))
                            data_df['url_of_trading_pair'] = url_of_trading_pair
                            data_df['trading_pair_is_traded_with_margin'] = True
                        except:
                            data_df['url_of_trading_pair'] = np.nan
                            traceback.print_exc()

                    try:
                        data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = spot_asset_is_also_available_as_swap_contract_on_the_same_exchange
                    except:
                        data_df['spot_asset_also_available_as_swap_contract_on_same_exchange'] = np.nan
                        traceback.print_exc()

                    try:
                        if spot_asset_is_also_available_as_swap_contract_on_the_same_exchange:
                            data_df["url_of_swap_contract_if_it_exists"]=get_perpetual_swap_url(exchange, trading_pair.replace("_", "/"))
                            print("url_swap_added")
                        else:
                            data_df["url_of_swap_contract_if_it_exists"] = "swap_of_spot_asset_does_not_exist"
                    except:
                        traceback.print_exc()





                    # #если  в крипе мало данных , то ее не добавляем
                    # if len(data_df)<10:
                    #     continue

                    # # slice last 30 days for volume calculation
                    # min_volume_over_these_many_last_days=7
                    # data_df_n_days_slice=data_df.iloc[:-1].tail(min_volume_over_these_many_last_days).copy()
                    # data_df_n_days_slice["volume_by_close"]=\
                    #     data_df_n_days_slice["volume"]*data_df_n_days_slice["close"]
                    # print("data_df_n_days_slice")
                    # print(data_df_n_days_slice)
                    # min_volume_over_last_n_days_in_dollars=min(data_df_n_days_slice["volume_by_close"])
                    # print("min_volume_over_last_n_days_in_dollars")
                    # print(min_volume_over_last_n_days_in_dollars)
                    #
                    # #проверить, что объем за последние n дней не меньше, чем 2 цены биткойна
                    # if "_BTC" not in trading_pair:
                    #     if min_volume_over_last_n_days_in_dollars<1*last_bitcoin_price:
                    #         print(f"{trading_pair} discarded due to low volume")
                    #         continue
                    # else:
                    #     if min_volume_over_last_n_days_in_dollars<1:
                    #         print(f"{trading_pair} discarded due to low volume")
                    #         continue

                    # #проверить, что объем за последние n дней не меньше, чем 1 цены биткойна
                    # min_volume_over_these_many_last_days = 7
                    # min_volume_in_bitcoin=4
                    # asset_has_enough_volume=True
                    # asset_has_enough_volume=check_volume(trading_pair,
                    #                                      min_volume_over_these_many_last_days,
                    #                                      data_df,
                    #                                      min_volume_in_bitcoin,
                    #                                      last_bitcoin_price)
                    # if not asset_has_enough_volume:
                    #     continue



                    current_timestamp=time.time()
                    last_timestamp_in_df=data_df.tail(1).index.item()/1000.0
                    print("current_timestamp=",current_timestamp)
                    print("data_df.tail(1).index.item()=",data_df.tail(1).index.item()/1000.0)

                    # if not trading_pair['active']:
                    #     continue

                    #check if the pair is active
                    timeframe_in_seconds=convert_string_timeframe_into_seconds(timeframe)
                    if not abs(current_timestamp-last_timestamp_in_df)<(timeframe_in_seconds):
                        print(f"not quite active trading pair {trading_pair} on {exchange}")
                        not_active_pair_counter=not_active_pair_counter+1
                        print("not_active_pair_counter=",not_active_pair_counter)
                        list_of_inactive_pairs.append(f"{trading_pair}_on_{exchange}")
                        data_df["pair_is_inactive"]=True


                    print("1program got here")
                    # try:
                    #     data_df['Timestamp'] = \
                    #         [datetime.datetime.timestamp(float(x)) for x in data_df.index]
                    #
                    # except Exception as e:
                    #     print("error_message")
                    #     traceback.print_exc()
                    #     time.sleep(3000000)
                    data_df["Timestamp"] = (data_df.index)

                    try:
                        data_df["open_time"] = data_df["Timestamp"].apply(lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
                    except Exception as e:
                        print("error_message")
                        traceback.print_exc()

                    data_df['Timestamp'] = data_df["Timestamp"] / 1000.0
                        # time.sleep(3000000)
                    print("2program got here")
                    # data_df["open_time"] = data_df.index
                    print("3program got here")
                    data_df.index = range(0, len(data_df))
                    print("4program got here")
                    # data_df = populate_dataframe_with_td_indicator ( data_df )

                    data_df["exchange"] = exchange
                    # print("5program got here")
                    # data_df["short_name"] = np.nan
                    # print("6program got here")
                    # data_df["country"] = np.nan
                    # data_df["long_name"] = np.nan
                    # data_df["sector"] = np.nan
                    # # data_df["long_business_summary"] = long_business_summary
                    # data_df["website"] = np.nan
                    # data_df["quote_type"] = np.nan
                    # data_df["city"] = np.nan
                    # data_df["exchange_timezone_name"] = np.nan
                    # data_df["industry"] = np.nan
                    # data_df["market_cap"] = np.nan

                    data_df.set_index("open_time")
                    # try:
                    #     # Set the timezone for Moscow
                    #     moscow_tz = timezone('Europe/Moscow')
                    #     almaty_tz = timezone('Asia/Almaty')
                    #     data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
                    #     data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
                    #     # Convert the "open_time" column from UTC to Moscow time
                    #     data_df['open_time_msk'] =\
                    #         data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)
                    #
                    #     data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')
                    #
                    #     # Convert the "open_time_datatime_format" column from UTC to Almaty time
                    #     data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')
                    #
                    #     # Create a new column called "open_time_almaty_time" that contains the time in string format
                    #     data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
                    # except:
                    #     traceback.print_exc()
                    add_time_of_next_candle_print_to_df(data_df)
                    print("2program got here")
                    trading_pair_has_stablecoin_as_first_part=\
                        check_if_stable_coin_is_the_first_part_of_ticker(trading_pair)

                    # if "BUSD/" in trading_pair:
                    #     time.sleep(3000000)
                    if trading_pair_has_stablecoin_as_first_part:
                        print(f"discarded pair due to stable coin being the first part is {trading_pair}")
                        continue

                    print(f"{trading_pair} was added to df")

                    print(
                        f"{string_to_compare_with_pair_from_levels_formed_by_highs_and_lows_for_cryptos_0000} added to db")


                    data_df.to_sql ( f"{trading_pair}_on_{exchange}" ,
                                     engine ,
                                     if_exists = 'replace' )



                # elif "/USD" in trading_pair and "/USDT" not in trading_pair:
                #     #print(trading_pair)
                #     list_of_trading_pairs_with_USD.append(trading_pair)

                # elif "/BTC" in trading_pair:
                #     #print(trading_pair)
                #     list_of_trading_pairs_with_BTC.append(trading_pair)


                else:
                    continue






                    #print ( "data=" , data )
            except ccxt.base.errors.RequestTimeout:
                print("found ccxt.base.errors.RequestTimeout error inner")
                continue


            except ccxt.RequestTimeout:
                print("found ccxt.RequestTimeout error inner")
                continue


            except Exception as e:
                print(f"problem with {trading_pair} on {exchange}\n", e)
                traceback.print_exc ()
                continue
            finally:

                continue

        # connection_to_usdt_trading_pairs_ohlcv.close()

    # except Exception as e:
    #     print ( f"found {e} error outer" )
    #     traceback.print_exc ()
    #
    #     traceback.print_exc()



    except Exception as e:
        print(f"problem with {exchange}\n", e)
        traceback.print_exc()

        #await exchange_object.close ()

    finally:

        print("exchange object is closed")

def convert_string_timeframe_into_seconds(timeframe):
    timeframe_in_seconds=0
    if timeframe=='1d':
        timeframe_in_seconds=86400
    if timeframe == '12h':
        timeframe_in_seconds = 86400/2
    if timeframe == '6h':
        timeframe_in_seconds = 86400/4
    if timeframe == '4h':
        timeframe_in_seconds = 86400/6
    if timeframe == '8h':
        timeframe_in_seconds = 86400/3
    return timeframe_in_seconds

def get_real_time_bitcoin_price():
    binance = ccxt.binance()
    btc_ticker = binance.fetch_ticker('BTC/USDT')
    last_bitcoin_price=btc_ticker['close']
    return last_bitcoin_price

def fetch_historical_usdt_pairs_asynchronously(last_bitcoin_price,engine,exchanges_list,timeframe,list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db):
    start=time.perf_counter()
    # exchanges_list=['aax', 'ascendex', 'bequant', 'bibox', 'bigone',
    #                 'binance', 'binancecoinm', 'binanceus', 'binanceusdm',
    #                 'bit2c', 'bitbank', 'bitbay', 'bitbns', 'bitcoincom',
    #                 'bitfinex', 'bitfinex2', 'bitflyer', 'bitforex', 'bitget',
    #                 'bithumb', 'bitmart', 'bitmex', 'bitopro', 'bitpanda', 'bitrue',
    #                 'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bkex',
    #                 'bl3p', 'blockchaincom', 'btcalpha', 'btcbox', 'btcmarkets',
    #                 'btctradeua', 'btcturk', 'buda', 'bw', 'bybit', 'bytetrade',
    #                 'cdax', 'cex', 'coinbase', 'coinbaseprime', 'coinbasepro',
    #                 'coincheck', 'coinex', 'coinfalcon', 'coinflex', 'coinmate',
    #                 'coinone', 'coinspot', 'crex24', 'cryptocom', 'currencycom',
    #                 'delta', 'deribit', 'digifinex', 'eqonex', 'exmo', 'flowbtc',
    #                 'fmfwio', 'ftx', 'ftxus', 'gateio', 'gemini', 'hitbtc', 'hitbtc3',
    #                 'hollaex', 'huobi', 'huobijp', 'huobipro', 'idex',
    #                 'independentreserve', 'indodax', 'itbit', 'kraken', 'kucoin',
    #                 'kucoinfutures', 'kuna', 'latoken', 'lbank', 'lbank2', 'liquid',
    #                 'luno', 'lykke', 'mercado', 'mexc', 'mexc3', 'ndax', 'novadax',
    #                 'oceanex', 'okcoin', 'okex', 'okex5', 'okx', 'paymium', 'phemex',
    #                 'poloniex', 'probit', 'qtrade', 'ripio', 'stex', 'therock',
    #                 'tidebit', 'tidex', 'timex', 'upbit', 'vcc', 'wavesexchange',
    #                 'wazirx', 'whitebit', 'woo', 'xena', 'yobit', 'zaif', 'zb',
    #                 'zipmex', 'zonda']


    # connection_to_usdt_trading_pairs_daily_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )

    # connection_to_usdt_trading_pairs_4h_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs_4h.db" ) )

    # coroutines = [await get_hisorical_data_from_exchange_for_many_symbols(exchange ) for exchange in  exchanges_list]
    # await asyncio.gather(*coroutines, return_exceptions = True)
    #
    database_name = 'levels_formed_by_highs_and_lows_for_cryptos_0000'
    list_of_exchanges_for_todays_pairs = get_list_of_exchange_ids_for_todays_pairs(database_name)
    print("list_of_exchanges_for_todays_pairs2")
    print(list_of_exchanges_for_todays_pairs)

    for exchange in exchanges_list:
        if exchange not in list_of_exchanges_for_todays_pairs:
            continue

        # if exchange!="btcex" :
        #     continue

        if exchange!="bitforex":
            continue

        get_hisorical_data_from_exchange_for_many_symbols(last_bitcoin_price, exchange,
                                                          engine, timeframe,list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db)
    #connection_to_usdt_trading_pairs_daily_ohlcv.close()
    # connection_to_usdt_trading_pairs_4h_ohlcv.close ()
    print("list_of_inactive_pairs\n",list_of_inactive_pairs)
    print("len(list_of_inactive_pairs=",len(list_of_inactive_pairs))
    end = time.perf_counter ()
    print("time in seconds is ", end-start)
    print ( "time in minutes is " , (end - start)/60.0 )
    print ( "time in hours is " , (end - start) / 60.0/60.0 )

def fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price):

    # engine , connection_to_ohlcv_for_usdt_pairs =\
    #     connect_to_postgres_db_with_deleting_it_first(database_name)

    engine_for_db_with_todays_ohlcv , connection_to_ohlcv_for_usdt_pairs=\
        connect_to_postgres_db_without_deleting_it_first(database_name)


    

    exchanges_list = ccxt.exchanges

    exclusion_list = [ "okex", "hitbtc",  "gate", "binanceusdm",
        "binanceus", "bitfinex", "binancecoinm", "huobijp"]
    exchanges_list=[value for value in exchanges_list if value not in exclusion_list]
    how_many_exchanges = len ( exchanges_list )
    step_for_exchanges = 50

    # database_name_with_ohlcv_of_todays_pairs="ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db=get_list_of_tables_in_db(engine_for_db_with_todays_ohlcv)

    # fetch_historical_usdt_pairs_asynchronously(engine,exchanges_list)

    process_list = []
    for exchange_counter in \
            range ( 0 , len ( exchanges_list ) ,
                    step_for_exchanges ):
        print ( "exchange_counter=" , exchange_counter )
        print (
            f"exchanges[{exchange_counter}:{exchange_counter} + {step_for_exchanges}]" )
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        # for number_of_exchange , exchange \
        #         in enumerate ( exchanges_list[exchange_counter:exchange_counter +
        #                                                               how_many_separate_processes_to_spawn_each_corresponding_to_one_exchange] ):
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        p = multiprocessing.Process ( target =
                                      fetch_historical_usdt_pairs_asynchronously ,
                                      args = (last_bitcoin_price,engine_for_db_with_todays_ohlcv , exchanges_list[
                                                       exchange_counter:exchange_counter + step_for_exchanges],
                                              timeframe,list_of_tables_in_usdt_pairs_0000_for_todays_pairs_db) )
        p.start ()
        process_list.append ( p )
    for process in process_list:
        process.join ()

    try:
        connection_to_ohlcv_for_usdt_pairs.close ()
    except:
        traceback.print_exc()


if __name__=="__main__":
    timeframe='1d'
    # last_bitcoin_price=get_real_time_bitcoin_price()
    last_bitcoin_price=30000
    print("last_bitcoin_price")
    print(last_bitcoin_price)
    database_name="ohlcv_1d_data_for_usdt_pairs_0000_for_todays_pairs"
    fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price)
#asyncio.run(get_hisorical_data_from_exchange_for_many_symbols_and_exchanges())
