from binance.client import Client
from binance.enums import KLINE_INTERVAL_1DAY, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceAPIException
import config
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math
import statistics
import time
import requests
import data_retrieval
import indicators
import indicator_testing
import indicator_calculations

multiplier = {
    "DAYS": 1,
    "HOURS": 24,
    "MINUTES" : 1440
}

# prints out a list of buy-sell pairs
def print_trade_list(trades):
    print("\nOrders:\n")

    if len(trades) == 0:
        print("No trade made\n")
    
    else:
        for trade in trades:
            if (len(trade[-1]) != 2):
                print("Coin traded: " + trade[-1])
            print("Buy Time: {time}, Buy Price: {price}".format(time=str(trade[0][0]), price=trade[0][1]))
            print("Low Time: {time}, Low Price: {price}".format(time=str(trade[1][0]), price=trade[1][1]))
            print("High Time: {time}, High Price: {price}".format(time=str(trade[2][0]), price=trade[2][1]))
            print("Sell Time: {time}, Sell Price: {price}".format(time=str(trade[3][0]), price=trade[3][1]))
            print("Net gain/loss from trade: " + str(trade[3][1] - trade[0][1]) + "\n")

# prints out the overal trend of the tested currency over the length of the dataset
# 
# paramters: data, set of closing_prices for the dataset
#
# returns: a float representing the overall trend for the tested currency
def print_plus_minus_overall(data):
    data = pd.Series.to_list(data)
    print("Overall trend: " + str((data[-1] - data[0])* 100 /data[0] )+ "%\n")
    return (data[-1] - data[0])* 100 /data[0] 

# creates a dummy array filled with the parameter "value"
# 
# parameters: length, size of the dummy array
# parameters: value, the value used to fill up the array
#
# returns, list filled with dummy values with length "length"
def create_array(length, value):
    dummy_list = []
    for i in range(length):
        dummy_list.append(value)
    return dummy_list

# tests and graphs 1std bollinger band strategy from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_BB(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)

    df_data = pd.DataFrame(klines, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    BB = indicators.bollinger_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    #print(df.tail(50))

    buy_sell_pairs = indicator_calculations.test_BB_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df.set_index("date",drop=True,inplace=True)
    df.plot()
    plt.show()

# tests and graphs 2std bollinger band strategy from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_double_deviation_bands(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)

    df_data = pd.DataFrame(klines, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    double_deviation_BB = indicators.double_deviation_bands_data(pd.Series.to_list(df_data['price']))
    
    df_Bollinger_Bands = pd.DataFrame(double_deviation_BB, columns = ['-2 SD', '-1 SD', '+1 SD', '+2 SD'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    buy_sell_pairs = indicator_calculations.test_double_deviation_band_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df.set_index("date",drop=True,inplace=True)
    df.plot()
    plt.show()

# tests and graphs relative strength index (RSI) strategy from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_RSI(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)

    df = pd.DataFrame(klines, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    #print(df['RSI'])

    buy_sell_pairs = indicator_calculations.test_RSI_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(2)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])

    plt.show()

# tests and graphs moving average convergence divergence (MACD) strategy from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_MACD(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']))
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values)
    df['Signal Line'] = signal_line_values

    buy_sell_pairs = indicator_calculations.test_MACD_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    MACD_vs_signal_line = indicators.MACD_signal_line_difference(pd.Series.to_list(df['MACD']), pd.Series.to_list(df['Signal Line']))
    df['MACD_vs_signal_line'] = MACD_vs_signal_line

    df['Baseline'] = np.zeros(len(df))

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['MACD'])
    axs[1].plot(df['date'], df['Signal Line'])
    axs[1].plot(df['date'], df['Baseline'])
    axs[2].plot(df['date'], df['MACD_vs_signal_line'])
    axs[2].plot(df['date'], df['Baseline'])

    plt.show()

# tests and graphs moving average convergence divergence (MACD) combined with 1std 
# bollinger bonds strategies from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_MACD_BB(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    BB = indicators.bollinger_bands_data(df['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df, df_Bollinger_Bands], axis=1)

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']))
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values)
    df['Signal Line'] = signal_line_values

    buy_sell_pairs = indicator_calculations.test_MACD_BB_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    MACD_vs_signal_line = indicators.MACD_signal_line_difference(pd.Series.to_list(df['MACD']), pd.Series.to_list(df['Signal Line']))
    df['MACD_vs_signal_line'] = MACD_vs_signal_line

    df['Baseline'] = np.zeros(len(df))

    fig, axs = plt.subplots(4)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['MACD'])
    axs[1].plot(df['date'], df['Signal Line'])
    axs[1].plot(df['date'], df['Baseline'])
    axs[2].plot(df['date'], df['MACD_vs_signal_line'])
    axs[2].plot(df['date'], df['Baseline'])
    axs[3].plot(df['date'], df['price'])
    axs[3].plot(df['date'], df['Bottom Band'])
    axs[3].plot(df['date'], df['Middle Band'])
    axs[3].plot(df['date'], df['Top Band'])

    plt.show()

# tests and graphs moving average convergence divergence (MACD) combined with 2std 
# bollinger bonds strategies from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_macd_two_sd_bb(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']))
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values)
    df['Signal Line'] = signal_line_values

    two_sd_bb = indicators.double_deviation_bands_data(df['price'])
    
    df_Bollinger_Bands = pd.DataFrame(two_sd_bb, columns = ['-2 SD', '-1 SD', '+1 SD', '+2 SD'])
    df = pd.concat([df, df_Bollinger_Bands], axis=1)

    buy_sell_pairs = indicator_calculations.test_macd_double_sd_bands_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    MACD_vs_signal_line = indicators.MACD_signal_line_difference(pd.Series.to_list(df['MACD']), pd.Series.to_list(df['Signal Line']))
    df['MACD_vs_signal_line'] = MACD_vs_signal_line

    df['Baseline'] = np.zeros(len(df))

    fig, axs = plt.subplots(4)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['MACD'])
    axs[1].plot(df['date'], df['Signal Line'])
    axs[1].plot(df['date'], df['Baseline'])
    axs[2].plot(df['date'], df['MACD_vs_signal_line'])
    axs[2].plot(df['date'], df['Baseline'])
    axs[3].plot(df['date'], df['price'])
    axs[3].plot(df['date'], df['-2 SD'])
    axs[3].plot(df['date'], df['-1 SD'])
    axs[3].plot(df['date'], df['+1 SD'])
    axs[3].plot(df['date'], df['+2 SD'])

    plt.show()

# tests and graphs moving average convergence divergence (MACD) combined with 
# relative strength index (RSI) strategies from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_MACD_RSI(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']))
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values)
    df['Signal Line'] = signal_line_values
    RSI_values = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI_values

    buy_sell_pairs = indicator_calculations.test_MACD_RSI_returns(pd.Series.to_list(df))

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    MACD_vs_signal_line = indicators.MACD_signal_line_difference(pd.Series.to_list(df['MACD']), pd.Series.to_list(df['Signal Line']))
    df['MACD_vs_signal_line'] = MACD_vs_signal_line

    df['Baseline'] = np.zeros(len(df))

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(4)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['MACD'])
    axs[1].plot(df['date'], df['Signal Line'])
    axs[1].plot(df['date'], df['Baseline'])
    axs[2].plot(df['date'], df['MACD_vs_signal_line'])
    axs[2].plot(df['date'], df['Baseline'])
    axs[3].plot(df['date'], df['RSI'])
    axs[3].plot(df['date'], df['30%'])
    axs[3].plot(df['date'], df['40%'])
    axs[3].plot(df['date'], df['45%'])
    axs[3].plot(df['date'], df['50%'])
    axs[3].plot(df['date'], df['55%'])
    axs[3].plot(df['date'], df['60%'])
    axs[3].plot(df['date'], df['70%'])

    plt.show()

# tests and graphs 1std bollinger bands combined with 
# relative strength index (RSI) strategies from "days" days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_BB_RSI_recent(symbol, time_interval, days):
    klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    data = np.array(klines)

    df_data = pd.DataFrame(data, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    BB = indicators.two_std_bollinger_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters(pd.Series.to_list(df), 47, 40)

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[2].plot(df['date'], df['price'])
    axs[2].plot(df['date'], df['Bottom Band'])
    axs[2].plot(df['date'], df['Middle Band'])
    axs[2].plot(df['date'], df['Top Band'])

    plt.show()

# optimizes and graphs 2std and 1std bollinger bands combined with 
# relative strength index (RSI) strategies from "days" days back to now OR from start_day to end_day 
#
# if using start_day to end_day,
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def optimize_double_bands_RSI_recent(symbol="BTC", time_interval="MINUTES", days=None, start_day=None, end_day=None):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)

    data = np.array(klines)

    df_data = pd.DataFrame(data, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    double_bands = indicators.double_deviation_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(double_bands, columns = ['-2 SD', '-1 SD', '+1 SD', '+2 SD'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    results = indicator_calculations.optimize_double_bands_rsi_returns(pd.Series.to_list(df))

    for i in range(1, 50):
        print(results[len(results) - i])

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[2].plot(df['date'], df['price'])
    axs[2].plot(df['date'], df['-2 SD'])
    axs[2].plot(df['date'], df['-1 SD'])
    axs[2].plot(df['date'], df['+1 SD'])
    axs[2].plot(df['date'], df['+2 SD'])

    plt.show()

# tests and graphs 2std and 1std bollinger bands combined with 
# relative strength index (RSI) strategies from "days" days back to now OR from start_day to end_day 
#
# if using start_day to end_day,
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_double_bands_RSI(symbol='BTC', time_interval='MINUTES', days=None, start_day=None, end_day=None, buy_rsi=40, sell_rsi=50):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        ("Invalid date entries")
        exit(0)

    df_data = pd.DataFrame(klines, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    double_bands = indicators.double_deviation_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(double_bands, columns = ['-2 SD', '-1 SD', '+1 SD', '+2 SD'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    buy_sell_pairs = indicator_calculations.test_double_deviation_band_RSI_returns_with_parameters(pd.Series.to_list(df), buy_rsi, sell_rsi)

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[2].plot(df['date'], df['price'])
    axs[2].plot(df['date'], df['-2 SD'])
    axs[2].plot(df['date'], df['-1 SD'])
    axs[2].plot(df['date'], df['+1 SD'])
    axs[2].plot(df['date'], df['+2 SD'])

    plt.show()

# optimizes and graphs 2std bollinger bands combined with 
# relative strength index (RSI) strategies from "days" days back to now OR from start_day to end_day 
#
# if using start_day to end_day,
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def optimize_BB_RSI(symbol="BTC", time_interval="MINUTES", days=None, start_day=None, end_day=None):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    
    df_data = pd.DataFrame(klines, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    BB = indicators.two_std_bollinger_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    results = indicator_calculations.optimize_simple_BB_RSI_returns(pd.Series.to_list(df))

    for i in range(1, 50):
        print(results[len(results) - i])

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[2].plot(df['date'], df['price'])
    axs[2].plot(df['date'], df['Bottom Band'])
    axs[2].plot(df['date'], df['Middle Band'])
    axs[2].plot(df['date'], df['Top Band'])

    plt.show()

# optimizes and graphs relative strength index (RSI) strategy from 
# "days" days back to now OR from start_day to end_day 
#
# if using start_day to end_day,
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def optimize_RSI(symbol="BTC", time_interval="MINUTES", days=None, start_day=None, end_day=None):
    def mergeSort(array):
        if len(array) > 1:

            # r is the point where the array is divided into two subarrays
            r = len(array)//2
            L = array[:r]
            M = array[r:]

            # Sort the two halves
            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            # Until we reach either end of either L or M, pick larger among
            # elements L and M and place them in the correct position at A[p..r]
            while i < len(L) and j < len(M):
                if L[i][2] < M[j][2]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            # When we run out of elements in either L or M,
            # pick up the remaining elements and put in A[p..r]
            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1
    
    def calculate_buy_statistics(array, buy_start, buy_end, sell_start, sell_end):
        def mergeSort(value):
            if len(value) > 1:

                # r is the point where the array is divided into two subarrays
                r = len(value)//2
                L = value[:r]
                M = value[r:]

                # Sort the two halves
                mergeSort(L)
                mergeSort(M)

                i = j = k = 0

                # Until we reach either end of either L or M, pick larger among
                # elements L and M and place them in the correct position at A[p..r]
                while i < len(L) and j < len(M):
                    if L[i][1] < M[j][1]:
                        value[k] = L[i]
                        i += 1
                    else:
                        value[k] = M[j]
                        j += 1
                    k += 1

                # When we run out of elements in either L or M,
                # pick up the remaining elements and put in A[p..r]
                while i < len(L):
                    value[k] = L[i]
                    i += 1
                    k += 1

                while j < len(M):
                    value[k] = M[j]
                    j += 1
                    k += 1

        x_len = buy_end - buy_start
        y_len = sell_end - sell_start

        buy_results = []
        for i in range(x_len):
            subset = []
            for j in range(y_len):
                subset.append(array[i*y_len + j][2])
            avg = (sum(subset)) / (len(subset))
            std = statistics.stdev(subset)
            buy_results.append([i + buy_start, avg, std])
        
        mergeSort(buy_results)
        return(buy_results)

    def calculate_sell_statistics(array, buy_start, buy_end, sell_start, sell_end):
        def mergeSort(value):
            if len(value) > 1:

                # r is the point where the array is divided into two subarrays
                r = len(value)//2
                L = value[:r]
                M = value[r:]

                # Sort the two halves
                mergeSort(L)
                mergeSort(M)

                i = j = k = 0

                # Until we reach either end of either L or M, pick larger among
                # elements L and M and place them in the correct position at A[p..r]
                while i < len(L) and j < len(M):
                    if L[i][1] < M[j][1]:
                        value[k] = L[i]
                        i += 1
                    else:
                        value[k] = M[j]
                        j += 1
                    k += 1

                # When we run out of elements in either L or M,
                # pick up the remaining elements and put in A[p..r]
                while i < len(L):
                    value[k] = L[i]
                    i += 1
                    k += 1

                while j < len(M):
                    value[k] = M[j]
                    j += 1
                    k += 1

        x_len = buy_end - buy_start
        y_len = sell_end - sell_start

        buy_results = []
        for i in range(y_len):
            subset = []
            for j in range(x_len):
                subset.append(array[i + j * y_len][2])
            avg = (sum(subset)) / (len(subset))
            std = statistics.stdev(subset)
            buy_results.append([i + buy_start, avg, std])
        
        mergeSort(buy_results)
        return(buy_results)

    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    
    df = pd.DataFrame(klines, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    results = indicator_calculations.optimize_RSI_returns(pd.Series.to_list(df))

    buy_stats = calculate_buy_statistics(results, 20, 60, 40, 70)

    print("\n\nBuy Value Averages: \n")
    for i in range(1, 20):
        print(buy_stats[len(buy_stats) - i])

    sell_stats = calculate_sell_statistics(results, 20, 60, 40, 70)

    print("\n\nBuy Sell Averages: \n")
    for i in range(1, 20):
        print(sell_stats[len(sell_stats) - i])
 
    print("\n\nBest Indicators: \n")

    mergeSort(results)
    for i in range(1, 20):
        print(results[len(results) - i])

    print_plus_minus_overall(df['price'])

# optimizes and graphs relative strength index (RSI) strategy from start_day to end_day 
#
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks
def test_BB_RSI_historical(symbol, time_interval, start_day, end_day):
    klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    data = np.array(klines)

    df_data = pd.DataFrame(data, columns=['date', 'price'])
    df_data['date'] = pd.to_datetime(df_data['date'])
    df_data['price'] = pd.to_numeric(df_data["price"], downcast="float")

    BB = indicators.two_std_bollinger_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters(pd.Series.to_list(df), 47, 35)

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results(buy_sell_pairs)

    print_plus_minus_overall(df['price'])

    df['30%'] = np.full([len(df), 1], 30, dtype=int)
    df['40%'] = np.full([len(df), 1], 40, dtype=int)
    df['45%'] = np.full([len(df), 1], 45, dtype=int)
    df['50%'] = np.full([len(df), 1], 50, dtype=int)
    df['55%'] = np.full([len(df), 1], 55, dtype=int)
    df['60%'] = np.full([len(df), 1], 60, dtype=int)
    df['70%'] = np.full([len(df), 1], 70, dtype=int)

    fig, axs = plt.subplots(3)
    axs[0].plot(df['date'], df['price'])
    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[2].plot(df['date'], df['price'])
    axs[2].plot(df['date'], df['Bottom Band'])
    axs[2].plot(df['date'], df['Middle Band'])
    axs[2].plot(df['date'], df['Top Band'])

    plt.show()

def test_BB_RSI_historical_whitelist(whitelisted_coins, time_interval, start_date, end_date):
    def mergeSort(array):
        if len(array) > 1:

            # r is the point where the array is divided into two subarrays
            r = len(array)//2
            L = array[:r]
            M = array[r:]

            # Sort the two halves
            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            # Until we reach either end of either L or M, pick larger among
            # elements L and M and place them in the correct position at A[p..r]
            while i < len(L) and j < len(M):
                if L[i][0][0] < M[j][0][0]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            # When we run out of elements in either L or M,
            # pick up the remaining elements and put in A[p..r]
            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1

    def select_valid_trades(trades):
        valid_trades = []
        valid_trades.append(trades[0])
        for i in range(1, len(trades)):
            if valid_trades[-1][-2][0] < trades[i][0][0]:
                valid_trades.append(trades[i])
        return valid_trades

    data = {}
    valid_coins = []
    for coin in whitelisted_coins:
        klines = data_retrieval.get_historical_klines(coin, time_interval, start_date, end_date)
        if type(klines) != list:
            print("Invalid coin abbreviation: " + coin)
        else:
            data[coin] = klines
            valid_coins.append(coin)

    dataframes = {}
    for coin in data:
        dataframes[coin] = pd.DataFrame(data[coin], columns=['date', 'price'])
        dataframes[coin]['date'] = pd.to_datetime(dataframes[coin]['date'])
        dataframes[coin]['price'] = pd.to_numeric(dataframes[coin]['price'], downcast="float")

        BB = indicators.bollinger_bands_data(dataframes[coin]['price'])
    
        df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
        dataframes[coin] = pd.concat([dataframes[coin], df_Bollinger_Bands], axis=1)

        RSI = indicators.RSI_data(pd.Series.to_list(dataframes[coin]['price']))
        dataframes[coin]['RSI'] = RSI

    all_trades = []
    for coin in dataframes:
        buy_sell_pairs = indicator_calculations.test_BB_RSI_returns(pd.Series.to_list(dataframes[coin]))
        for trade in buy_sell_pairs:
            trade.append(coin)
            all_trades.append(trade)
    
    mergeSort(all_trades)

    trading_list = select_valid_trades(all_trades)

    print_trade_list(trading_list)
    
    indicator_calculations.analyze_results_compounded(buy_sell_pairs)

def test_BB_RSI_recent_whitelist(whitelisted_coins, time_interval, days):
    def mergeSort(array):
        if len(array) > 1:

            # r is the point where the array is divided into two subarrays
            r = len(array)//2
            L = array[:r]
            M = array[r:]

            # Sort the two halves
            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            # Until we reach either end of either L or M, pick larger among
            # elements L and M and place them in the correct position at A[p..r]
            while i < len(L) and j < len(M):
                if L[i][0][0] < M[j][0][0]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            # When we run out of elements in either L or M,
            # pick up the remaining elements and put in A[p..r]
            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1

    def select_valid_trades(trades):
        valid_trades = []
        valid_trades.append(trades[0])
        for i in range(1, len(trades)):
            if valid_trades[-1][-2][0] < trades[i][0][0]:
                valid_trades.append(trades[i])
        return valid_trades

    data = {}
    valid_coins = []
    for coin in whitelisted_coins:
        klines = data_retrieval.get_recent_klines(coin, time_interval, days)
        if type(klines) != list:
            print("Invalid coin abbreviation: " + coin)
        else:
            data[coin] = klines
            valid_coins.append(coin)

    dataframes = {}
    for coin in data:
        dataframes[coin] = pd.DataFrame(data[coin], columns=['date', 'price'])
        dataframes[coin]['date'] = pd.to_datetime(dataframes[coin]['date'])
        dataframes[coin]['price'] = pd.to_numeric(dataframes[coin]['price'], downcast="float")

        BB = indicators.bollinger_bands_data(dataframes[coin]['price'])
    
        df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
        dataframes[coin] = pd.concat([dataframes[coin], df_Bollinger_Bands], axis=1)

        RSI = indicators.RSI_data(pd.Series.to_list(dataframes[coin]['price']))
        dataframes[coin]['RSI'] = RSI

    all_trades = []
    for coin in dataframes:
        buy_sell_pairs = indicator_calculations.test_BB_RSI_returns(pd.Series.to_list(dataframes[coin]))
        for trade in buy_sell_pairs:
            trade.append(coin)
            all_trades.append(trade)
    
    mergeSort(all_trades)

    trading_list = select_valid_trades(all_trades)

    print_trade_list(trading_list)
    
    indicator_calculations.analyze_results_compounded(buy_sell_pairs)

def test_MACD_recent_whitelist(whitelisted_coins, time_interval, days):
    def mergeSort(array):
        if len(array) > 1:

            # r is the point where the array is divided into two subarrays
            r = len(array)//2
            L = array[:r]
            M = array[r:]

            # Sort the two halves
            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            # Until we reach either end of either L or M, pick larger among
            # elements L and M and place them in the correct position at A[p..r]
            while i < len(L) and j < len(M):
                if L[i][0][0] < M[j][0][0]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            # When we run out of elements in either L or M,
            # pick up the remaining elements and put in A[p..r]
            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1

    def select_valid_trades(trades):
        valid_trades = []
        valid_trades.append(trades[0])
        for i in range(1, len(trades)):
            if valid_trades[-1][-2][0] < trades[i][0][0]:
                valid_trades.append(trades[i])
        return valid_trades

    data = {}
    valid_coins = []
    for coin in whitelisted_coins:
        klines = data_retrieval.get_recent_klines(coin, time_interval, days)
        if type(klines) != list:
            print("Invalid coin abbreviation: " + coin)
        else:
            data[coin] = klines
            valid_coins.append(coin)

    dataframes = {}
    for coin in data:
        dataframes[coin] = pd.DataFrame(data[coin], columns=['date', 'price'])
        dataframes[coin]['date'] = pd.to_datetime(dataframes[coin]['date'])
        dataframes[coin]['price'] = pd.to_numeric(dataframes[coin]['price'], downcast="float")

        MACD_values = indicators.MACD_data(pd.Series.tolist(dataframes[coin]['price']))
        dataframes[coin]['MACD'] = MACD_values
        signal_line_values = indicators.signal_line_data(MACD_values)
        dataframes[coin]['Signal Line'] = signal_line_values

    all_trades = []
    for coin in dataframes:
        buy_sell_pairs = indicator_calculations.test_MACD_returns(pd.Series.to_list(dataframes[coin]))
        for trade in buy_sell_pairs:
            trade.append(coin)
            all_trades.append(trade)
    
    mergeSort(all_trades)

    trading_list = select_valid_trades(all_trades)

    print_trade_list(trading_list)
    
    indicator_calculations.analyze_results_compounded(buy_sell_pairs)

if __name__ == '__main__':
    test_double_bands_RSI('BTC', 'MINUTES', days=2, buy_rsi=41, sell_rsi=43)