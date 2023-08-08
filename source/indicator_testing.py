from binance.client import Client
from binance.enums import KLINE_INTERVAL_1DAY, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceAPIException
import source.config as config
from datetime import datetime, timedelta, date
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math
import statistics
import time
import requests
import source.data_retrieval as data_retrieval
import source.indicators as indicators
import source.indicator_testing as indicator_testing
import source.indicator_calculations as indicator_calculations
from mpl_toolkits.mplot3d import Axes3D
import os.path
from os import path
import pickle

multiplier = {
    "DAYS": 1,
    "HOURS": 24,
    "MINUTES" : 1440
}

# prints out a list of buy-sell pairs
def print_trade_list(trades):
    print("\nOrders:\n")

    if len(trades) == 0:
        print("No trades made\n")
    
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
def test_BB(symbol="BTC", time_interval="1 MINUTE", days=None, start_day=None, end_day=None, bb_std_value=1.5):
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

    BB = indicators.single_bollinger_bands_data(df_data['price'], std_value=bb_std_value)
    
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
def test_double_deviation_bands(symbol="BTC", time_interval="1 MINUTE", days=None, start_day=None, end_day=None):
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
def test_RSI(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, buy_rsi=40, sell_rsi=60):
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

    buy_sell_pairs = indicator_calculations.test_RSI_returns_with_parameters(pd.Series.to_list(df), buy_rsi, sell_rsi)

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
def test_MACD(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, shorter_EMA_length=50, longer_EMA_length=200, signal_line_length=20):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']), shorter_EMA_length, longer_EMA_length)
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values, signal_line_length)
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
def test_MACD_BB(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, shorter_EMA_length=50, longer_EMA_length=200, signal_line_length=20):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    BB = indicators.one_std_bollinger_bands_data(df['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df, df_Bollinger_Bands], axis=1)

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']), shorter_EMA_length, longer_EMA_length)
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values, signal_line_length)
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
def test_macd_two_sd_bb(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, shorter_EMA_length=50, longer_EMA_length=200, signal_line_length=20):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']), shorter_EMA_length, longer_EMA_length)
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values, signal_line_length)
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
def test_MACD_RSI(symbol='BTC', 
                  time_interval='1 MINUTE', 
                  days=None,
                  start_day=None,
                  end_day=None, 
                  shorter_EMA_length=50, 
                  longer_EMA_length=200, 
                  signal_line_length=20,
                  buy_rsi=40,
                  sell_rsi=60):
    klines = []
    if (days != None and start_day == None and end_day == None):
        klines = data_retrieval.get_recent_klines(symbol, time_interval, days)
    elif (days == None and start_day != None and end_day != None):
        klines = data_retrieval.get_historical_klines(symbol, time_interval, start_day, end_day)
    else:
        print("Invalid paramenters")
        exit(0)
    data = np.array(klines)

    df = pd.DataFrame(data, columns=['date', 'price'])
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df["price"], downcast="float")

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']), shorter_EMA_length, longer_EMA_length)
    df['MACD'] = MACD_values
    signal_line_values = indicators.signal_line_data(MACD_values, signal_line_length)
    df['Signal Line'] = signal_line_values
    RSI_values = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI_values

    buy_sell_pairs = indicator_calculations.test_MACD_RSI_returns(pd.Series.to_list(df), buy_rsi, sell_rsi)

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
def test_BB_RSI(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, buy_rsi=40, sell_rsi=60, bb_std_value=1.5, sma_length=20):
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

    BB = indicators.single_bollinger_bands_data(df_data['price'], sma_length=sma_length ,std_value=bb_std_value)
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns=['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters(pd.Series.to_list(df), buy_rsi, sell_rsi)

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
    for pair in buy_sell_pairs:
        axs[0].axvline(pair[0][0], c='g')
        axs[0].axvline(pair[3][0], c='r')

    axs[1].plot(df['date'], df['RSI'])
    axs[1].plot(df['date'], df['30%'])
    axs[1].plot(df['date'], df['40%'])
    axs[1].plot(df['date'], df['45%'])
    axs[1].plot(df['date'], df['50%'])
    axs[1].plot(df['date'], df['55%'])
    axs[1].plot(df['date'], df['60%'])
    axs[1].plot(df['date'], df['70%'])
    axs[0].plot(df['date'], df['Bottom Band'])
    axs[0].plot(df['date'], df['Middle Band'])
    axs[0].plot(df['date'], df['Top Band'])

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
def optimize_double_bands_RSI(symbol="BTC", time_interval="1 MINUTE", days=None, start_day=None, end_day=None):
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][2] < M[j][2]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1

    def print_best_paramters_formatted(results, number_of_prints):
        print("\n\nBest Indicators: \n")
        for i in range(1, number_of_prints):
            result = results[len(results) - i]
            print("{index:02}. buy rsi: {b}, sell rsi: {s}, returns: {r}".format(index=i, b=result[0], s=result[1], r=result[2]))
        print()

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

    mergeSort(results)

    print_best_paramters_formatted(results, 50)

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
def test_double_bands_RSI(symbol='BTC', time_interval='1 MINUTE', days=None, start_day=None, end_day=None, buy_rsi=40, sell_rsi=60):
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
def optimize_BB_RSI(symbol="BTC", time_interval="1 MINUTE", days=None, start_day=None, end_day=None, bb_std=2):
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][2] < M[j][2]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1
    
    def print_best_parameters_formatted(results, number_of_prints):
        mergeSort(results)
        print("\n\nBest Indicators: \n")
        for i in range(1, number_of_prints):
            result = results[len(results) - i]
            print("{index:02}. buy rsi: {b}, sell rsi: {s}, Returns: {r}%".format(index=i, b=result[0], s=result[1], r=result[2]))
        print()

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

    BB = indicators.single_bollinger_bands_data(df_data['price'], std_value=bb_std)
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    results = indicator_calculations.optimize_simple_BB_RSI_returns(pd.Series.to_list(df))

    #mergeSort(results)

    print_best_parameters_formatted(results, 50)

    print_plus_minus_overall(df['price'])
    
    #plotting price vs bollinger band vs rsi graphs for time interval
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

    #3d plot of returns vs buy_rsi and sell_rsi
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    data = np.array(results)
    x = data[:,0]
    y = data[:,1]
    z = data[:,2]
    ax.scatter(x,y,z, c=z)
    ax.set_xlabel('buy rsi')
    ax.set_ylabel('sell rsi')
    ax.set_zlabel('Returns (%)')
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
def optimize_RSI(symbol="BTC", time_interval="1 MINUTE", days=None, start_day=None, end_day=None):
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
 
    print("\n\nBest Indicators: \n")

    mergeSort(results)
    for i in range(1, 20):
        print(results[len(results) - i])

    print_plus_minus_overall(df['price'])

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

        BB = indicators.one_std_bollinger_bands_data(dataframes[coin]['price'])
    
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

        BB = indicators.one_std_bollinger_bands_data(dataframes[coin]['price'])
    
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

def test_TEMA(symbol='BTC', 
                    time_interval='1 MINUTE', 
                    days=None, 
                    start_day=None, 
                    end_day=None, 
                    fast_tema_length=20,
                    mid_tema_length=50,
                    slow_tema_length=None):
    
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

    fast_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), fast_tema_length)
    mid_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), mid_tema_length)
    slow_tema = None
    if (slow_tema_length != None):
        slow_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), slow_tema_length)
    
    buy_sell_pairs = indicator_calculations.test_TEMA_returns(pd.Series.to_list(df_data), fast_tema, mid_tema, slow_tema)

    print_trade_list(buy_sell_pairs)

    indicator_calculations.analyze_results_compounded(buy_sell_pairs)

    print_plus_minus_overall(df_data['price'])

    if (slow_tema == None):
        df_data['fast_tema'] = fast_tema
        df_data['mid_tema'] = mid_tema
        df_data.set_index("date",drop=True,inplace=True)
        df_data.plot()
        plt.show()
    else:
        df_data['fast_tema'] = fast_tema
        df_data['mid_tema'] = mid_tema
        df_data['slow_tema'] = slow_tema
        df_data.set_index("date",drop=True,inplace=True)
        df_data.plot()
        plt.show()

    

def test_BB_MACD_RSI(symbol='BTC', 
                    time_interval='1 MINUTE', 
                    days=None, 
                    start_day=None, 
                    end_day=None, 
                    buy_rsi=40, 
                    sell_rsi=60,
                    shorter_EMA_length=50,
                    longer_EMA_length=200,
                    signal_line_length=20):
    
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

    BB = indicators.two_std_bollinger_bands_data(df_data['price'])
    
    df_Bollinger_Bands = pd.DataFrame(BB, columns = ['Bottom Band', 'Middle Band', 'Top Band'])
    df = pd.concat([df_data, df_Bollinger_Bands], axis=1)

    RSI = indicators.RSI_data(pd.Series.to_list(df['price']))
    df['RSI'] = RSI

    MACD_values = indicators.MACD_data(pd.Series.tolist(df['price']), shorter_EMA_length, longer_EMA_length)
    df['MACD'] = MACD_values

    signal_line_values = indicators.signal_line_data(MACD_values, signal_line_length)
    df['Signal Line'] = signal_line_values

    buy_sell_pairs = indicator_calculations.test_BB_MACD_RSI_returns(pd.Series.to_list(df), buy_rsi, sell_rsi)

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

    MACD_vs_signal_line = indicators.MACD_signal_line_difference(pd.Series.to_list(df['MACD']), pd.Series.to_list(df['Signal Line']))
    df['MACD_vs_signal_line'] = MACD_vs_signal_line

    df['Baseline'] = np.zeros(len(df))

    fig, axs = plt.subplots(5)
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
    axs[3].plot(df['date'], df['MACD'])
    axs[3].plot(df['date'], df['Signal Line'])
    axs[3].plot(df['date'], df['Baseline'])
    axs[4].plot(df['date'], df['MACD_vs_signal_line'])
    axs[4].plot(df['date'], df['Baseline'])

    plt.show()

#don't use yet, function's use solely for ml
def optimize_MACD_buy_sell_diff(symbol="BTC", 
                  time_interval="1 MINUTE", 
                  days=None, 
                  start_day=None, 
                  end_day=None,
                  ema_lengths=[[50,200,20]],
                  display_graphs=False, 
                  print_position=False, 
                  store_results=True, 
                  csv_filename="",
                  pkl_filename=""):

    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][7] > M[j][7]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1
    
    def print_best_parameters(results=[], ema_length=None, num_printed=20):
        mergeSort(results)

        if ema_length == None:
            print("\nBest values: \n")
            for i in range(num_printed):
                short_ema = results[i][0]
                long_ema = results[i][1]
                sig_ema = results[i][2]
                buy_val = results[i][3]
                sell_val = results[i][4]
                returns = "{:.4f}".format(results[i][7])
                print("{index:02}. short_ema: {a}, long_ema: {b}, sig_ema: {c}, buy_diff: {d}, sell_diff: {e}, returns: {f}".format(
                    index=i+1,a=short_ema,b=long_ema,c=sig_ema,d=buy_val,e=sell_val,f=returns
                ))
        else:
            print("\nBest values for " + str(ema_length)+": \n")
            for i in range(num_printed):
                short_ema = results[i][0]
                long_ema = results[i][1]
                sig_ema = results[i][2]
                buy_val = results[i][3]
                sell_val = results[i][4]
                returns = "{:.4f}".format(results[i][7])
                print("{index:02}. short_ema: {a}, long_ema: {b}, sig_ema: {c}, buy_diff: {d}, sell_diff: {e}, returns: {f}".format(
                    index=i+1,a=short_ema,b=long_ema,c=sig_ema,d=buy_val,e=sell_val,f=returns
                ))
        
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

    total_results = []

    for lengths in ema_lengths:
        shorter_ema_len = lengths[0]
        longer_ema_len = lengths[1]
        signal_line_len = lengths[2]
        macd = indicators.MACD_data(pd.Series.to_list(df_data["price"]), shorter_ema_len, longer_ema_len)
        signal_line = indicators.signal_line_data(macd, signal_line_len)
        for i in range(-20, 20):
            for j in range(-20,20):
                buy_sell_pairs = indicator_calculations.test_MACD_returns_data_seperate(pd.Series.to_list(df_data),
                                                                                        macd, signal_line, i, j)
                returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
                results = []
                results.append(shorter_ema_len)
                results.append(longer_ema_len)
                results.append(signal_line_len)
                results.append(i)
                results.append(j)
                results.append(returns[2])
                results.append(returns[3])
                results.append(returns[4])
                if (print_position == True):
                    print("buy_diff: " + str(i) + " sell diff: " + str(j) + " returns: " + str(returns[4]))
                total_results.append(results)
    
    for i in range(len(ema_lengths)):
        batch_size = int(len(total_results)/ len(ema_lengths))
        print_best_parameters(total_results[i * batch_size: (i + 1) * batch_size], ema_lengths[i], 20)
    
    print_best_parameters(results=total_results, num_printed=50)

    print("\n")
    overall_trend = print_plus_minus_overall(df_data['price'])

    if (store_results == True and csv_filename != ""):
        exists = os.path.exists(csv_filename)
        with open(csv_filename, "a") as file:
            if exists == False:
                file.write("coin,start_date,end_date,days,short_ema,long_ema,sig_ema,buy_diff,sell_diff,positive_returns,negative_returns,net_returns,overall_trend\n")
            for result in total_results:
                shorter_ema = result[0]
                long_ema = result[1]
                sig_ema = result[2]
                buy_val = result[3]
                sell_val = result[4]
                p_returns = "{:.4f}".format(result[5])
                n_returns = "{:.4f}".format(result[6])
                returns = "{:.4f}".format(result[7])
                trend = "{:.4f}".format(overall_trend)
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(shorter_ema)+","+str(long_ema)+","+str(sig_ema)+","+str(buy_val)+","+str(sell_val)+","+p_returns+","+n_returns+","+returns+","+trend+"\n")
    
    if (pkl_filename != ""):
        outfile = open(pkl_filename, "wb")
        pickle.dump(total_results, outfile)
        outfile.close()

def optimize_TEMA_ema_lengths(symbol="BTC", 
                  time_interval="1 MINUTE", 
                  days=None, 
                  start_day=None, 
                  end_day=None,
                  fast_tema_range=[3,20],
                  mid_tema_range=[3,30],
                  slow_tema_range=[3,40],
                  display_graphs=False, 
                  print_position=False, 
                  store_results=True, 
                  csv_filename="",
                  pkl_filename=""):
    
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][5] > M[j][5]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1
    
    def print_best_parameters(results=[], num_printed=20):
        mergeSort(results)
        print("\nBest values: \n")
        for i in range(num_printed):
            fast_ema = results[i][0]
            mid_ema = results[i][1]
            slow_ema = results[i][2]
            returns = "{:.4f}".format(results[i][5])
            print("{index:02}. fast_ema: {a}, mid_ema: {b}, slow_ema: {c}, returns: {f}%".format(
                index=i+1,a=fast_ema,b=mid_ema,c=slow_ema,f=returns
            ))
        
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

    total_results = []

    for i in range(fast_tema_range[0], fast_tema_range[1]):
        for j in range(mid_tema_range[0], mid_tema_range[1]):
            for k in range(slow_tema_range[0], slow_tema_range[1]):
                if i < j <= k:
                    fast_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), i)
                    mid_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), j)
                    slow_tema = indicators.TEMA_data(pd.Series.to_list(df_data['price']), k)
                    buy_sell_pairs = indicator_calculations.test_TEMA_returns(pd.Series.to_list(df_data), fast_tema, mid_tema, slow_tema)
                    returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
                    results = []
                    results.append(i)
                    results.append(j)
                    results.append(k)
                    results.append(returns[2])
                    results.append(returns[3])
                    results.append(returns[4])
                    results.append(returns[5])
                    results.append(returns[6])
                    if (print_position == True):
                        print("fast_tema: " + str(i) + " mid_tema: " + str(j) + " slow_tema: " + str(k) + " returns: " + str(returns[4]))
                    total_results.append(results)
        
    print_best_parameters(total_results, num_printed=50)

    overall_trend = print_plus_minus_overall(df_data['price'])

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(total_results)
        x = data[:,0]
        y = data[:,1]
        z = data[:,2]
        c = data[:,5]
        ax.set_xlabel('fast ema')
        ax.set_ylabel('mid ema')
        ax.set_zlabel('slow ema')

        img = ax.scatter(x, y, z, c=c, cmap=plt.hot())
        
        fig.colorbar(img)
        plt.show()

    if (store_results == True and csv_filename != ""):
        exists = os.path.exists(csv_filename)
        with open(csv_filename, "a") as file:
            if exists == False:
                file.write("coin,start_date,end_date,days,fast_tema,mid_tema,slow_tema,positive_returns,negative_returns,net_returns,overall_trend,trades,captial_usage_percentage\n")
            for result in total_results:
                fast_tema = result[0]
                mid_tema = result[1]
                slow_tema = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage_percentage = "{:.4f}".format(results[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(fast_tema)+","+str(mid_tema)+","+str(slow_tema)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage_percentage+"\n")

def optimize_MACD_ema_lengths(symbol="BTC", 
                  time_interval="1 MINUTE", 
                  days=None, 
                  start_day=None, 
                  end_day=None,
                  short_ema_range=[2,10],
                  long_ema_range=[2,30],
                  sig_ema_range=[2,20],
                  display_graphs=False, 
                  print_position=False, 
                  store_results=True, 
                  csv_filename="",
                  pkl_filename=""):
    
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][5] > M[j][5]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1
    
    def print_best_parameters(results=[], num_printed=20):
        mergeSort(results)
        if (len(results) < num_printed):
            num_printed = len(results)
        print("\nBest values: \n")
        for i in range(num_printed):
            short_ema = results[i][0]
            long_ema = results[i][1]
            sig_ema = results[i][2]
            returns = "{:.4f}".format(results[i][5])
            print("{index:02}. short_ema: {a}, long_ema: {b}, sig_ema: {c}, returns: {f}%".format(
                index=i+1,a=short_ema,b=long_ema,c=sig_ema,f=returns
            ))
        
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

    total_results = []

    for i in range(short_ema_range[0], short_ema_range[1]):
        for j in range(long_ema_range[0], long_ema_range[1]):
            for k in range(sig_ema_range[0], sig_ema_range[1]):
                if i > j:
                    continue
                else:
                    macd = indicators.MACD_data(pd.Series.to_list(df_data['price']), i, j)
                    signal_line = indicators.signal_line_data(macd, k)
                    buy_sell_pairs = indicator_calculations.test_MACD_returns_data_seperate(pd.Series.to_list(df_data), macd, signal_line)
                    returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
                    results = []
                    results.append(i)
                    results.append(j)
                    results.append(k)
                    results.append(returns[2])
                    results.append(returns[3])
                    results.append(returns[4])
                    results.append(returns[5])
                    results.append(returns[6])
                    if (print_position == True):
                        print("short_ema: " + str(i) + " long_ema: " + str(j) + " sig_ema: " + str(k) + " returns: " + str(returns[4]))
                    total_results.append(results)
    
    print_best_parameters(total_results, num_printed=50)

    overall_trend = print_plus_minus_overall(df_data['price'])

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(total_results)
        x = data[:,0]
        y = data[:,1]
        z = data[:,2]
        c = data[:,5]
        ax.set_xlabel('short ema')
        ax.set_ylabel('long ema')
        ax.set_zlabel('sig ema')

        img = ax.scatter(x, y, z, c=c, cmap=plt.hot())
        
        fig.colorbar(img)
        plt.show()

    if (store_results == True and csv_filename != ""):
        exists = os.path.exists(csv_filename)
        with open(csv_filename, "a") as file:
            if exists == False:
                file.write("coin,start_date,end_date,days,fast_ema,slow_ema,sig_ema,positive_returns,negative_returns,net_returns,overall_trend,trades,captial_usage_percentage\n")
            for result in total_results:
                fast_ema = result[0]
                slow_ema = result[1]
                sig_ema = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage_percentage = "{:.4f}".format(results[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(fast_ema)+","+str(slow_ema)+","+str(sig_ema)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage_percentage+"\n")


def optimize_BB_optimize_RSI(symbol="BTC", 
                             time_interval="1 MINUTE", 
                             days=None, 
                             start_day=None, 
                             end_day=None, 
                             display_graphs=False, 
                             print_position=False, 
                             store_results=True, 
                             csv_filename="",
                             pkl_filename=""):
                
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][5] < M[j][5]:
                    array[k] = L[i]
                    i += 1
                else:
                    array[k] = M[j]
                    j += 1
                k += 1

            while i < len(L):
                array[k] = L[i]
                i += 1
                k += 1

            while j < len(M):
                array[k] = M[j]
                j += 1
                k += 1

    def print_best_parameters_formatted(results, number_of_prints, bb_std_value=None):
        mergeSort(results)
        if bb_std_value == None:
            print("\nBest Indicators: \n")
            for i in range(1, number_of_prints):
                result = results[len(results) - i]
                print("{index:02}. bollinger band stds: {sd}, buy rsi: {b}, sell rsi: {s}, positive returns: {p:.2f}, negative returns: {n:.2f}, returns: {r:.2f}%".format(index=i, sd=result[0], b=result[1], s=result[2], p=result[3], n=result[4], r=result[5]))
            print()
        else:
            print("\nBest Indicators For " + str(bb_std_value) + " STD Bollinger Bands: \n")
            for i in range(1, number_of_prints):
                result = results[len(results) - i]
                print("{index:02}. bollinger band stds: {sd}, buy rsi: {b}, sell rsi: {s}, positive returns: {p:.2f}, negative returns: {n:.2f}, returns: {r:.2f}%".format(index=i, sd=result[0], b=result[1], s=result[2], p=result[3], n=result[4], r=result[5]))
            print()

    exists = os.path.exists(pkl_filename)
    if exists != False:
        print("Pickle filename already in use, please rerun with new name")
        exit(0)

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

    total_pairs = []
    one_std_returns = []
    one_half_std_returns = []
    two_std_returns = []
    two_half_std_returns = []

    rsi_values = indicators.RSI_data(pd.Series.to_list(df_data['price']))

    one_std_bollinger_bands = indicators.single_bollinger_bands_data(df_data['price'], std_value=1)
    for j in range(30,60):
        for k in range(40,70):
            results = []
            results.append(1.0)
            results.append(j)
            results.append(k)
            buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters_data_seperate(pd.Series.to_list(df_data), j, k, one_std_bollinger_bands, rsi_values)
            returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
            results.append(returns[2])
            results.append(returns[3])
            results.append(returns[4])
            results.append(returns[5])
            results.append(returns[6])
            one_std_returns.append(results)
            if (print_position == True):
                print("bollinger_band_std: {sd}, buy_rsi: {br}, sell_rsi: {sr} returns: {returns}".format(sd=(1.0),br=j, sr=k, returns=returns[4]))

    one_half_std_bollinger_bands = indicators.single_bollinger_bands_data(df_data['price'], std_value=1.5)
    for j in range(30,60):
        for k in range(40,70):
            results = []
            results.append(1.5)
            results.append(j)
            results.append(k)
            buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters_data_seperate(pd.Series.to_list(df_data), j, k, one_half_std_bollinger_bands, rsi_values)
            returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
            results.append(returns[2])
            results.append(returns[3])
            results.append(returns[4])
            results.append(returns[5])
            results.append(returns[6])
            one_half_std_returns.append(results)
            if (print_position == True):
                print("bollinger_band_std: {sd}, buy_rsi: {br}, sell_rsi: {sr} returns: {returns}%".format(sd=(1.5),br=j, sr=k, returns=returns[4]))
    
    two_std_bollinger_bands = indicators.single_bollinger_bands_data(df_data['price'], std_value=2)
    for j in range(30,60):
        for k in range(40,70):
            results = []
            results.append(2.0)
            results.append(j)
            results.append(k)
            buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters_data_seperate(pd.Series.to_list(df_data), j, k, two_std_bollinger_bands, rsi_values)
            returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
            results.append(returns[2])
            results.append(returns[3])
            results.append(returns[4])
            results.append(returns[5])
            results.append(returns[6])
            two_std_returns.append(results)
            if (print_position == True):
                print("bollinger_band_std: {sd}, buy_rsi: {br}, sell_rsi: {sr} returns: {returns}".format(sd=(2.0),br=j, sr=k, returns=returns[4]))
    
    two_half_std_bollinger_bands = indicators.single_bollinger_bands_data(df_data['price'], std_value=2.5)
    for j in range(30,60):
        for k in range(40,70):
            results = []
            results.append(2.5)
            results.append(j)
            results.append(k)
            buy_sell_pairs = indicator_calculations.test_simple_BB_RSI_returns_with_parameters_data_seperate(pd.Series.to_list(df_data), j, k, two_half_std_bollinger_bands, rsi_values)
            returns = indicator_calculations.analyze_results(buy_sell_pairs, False)
            results.append(returns[2])
            results.append(returns[3])
            results.append(returns[4])
            results.append(returns[5])
            results.append(returns[6])
            two_half_std_returns.append(results)
            if (print_position == True):
                print("bollinger_band_std: {sd}, buy_rsi: {br}, sell_rsi: {sr} returns: {returns}".format(sd=(2.5),br=j, sr=k, returns=returns[4]))
    
    total_pairs = one_std_returns + one_half_std_returns + two_std_returns + two_half_std_returns

    if (start_day != None and end_day != None):
        print("Results for " + start_day + " to " + end_day + ": \n")
    else:
        print("Results for " + str((datetime.now() - timedelta(days=days)).date()) + " to " + str(datetime.now().date()) + ": \n")
    
    print_best_parameters_formatted(one_std_returns, 20, 1.0)

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(one_std_returns)
        x = data[:,1]
        y = data[:,2]
        z = data[:,5]

        ax.scatter(x,y,z, c=z)
        ax.set_xlabel('Buy RSI')
        ax.set_ylabel('Sell RSI')
        ax.set_zlabel('Returns (%)')
        ax.set_title("Returns for 1.0 std bollinger bands")
        
        plt.show()

    print_best_parameters_formatted(one_half_std_returns, 20, 1.5)

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(one_half_std_returns)
        x = data[:,1]
        y = data[:,2]
        z = data[:,5]
        ax.scatter(x,y,z, c=z)
        ax.set_xlabel('Buy RSI')
        ax.set_ylabel('Sell RSI')
        ax.set_zlabel('Returns (%)')
        ax.set_title("Returns for 1.5 std bollinger bands")
        plt.show()
    
    print_best_parameters_formatted(two_std_returns, 20, 2.0)

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(two_std_returns)
        x = data[:,1]
        y = data[:,2]
        z = data[:,5]
        ax.scatter(x,y,z, c=z)
        ax.set_xlabel('Buy RSI')
        ax.set_ylabel('Sell RSI')
        ax.set_zlabel('Returns (%)')
        ax.set_title("Returns for 2.0 std bollinger bands")
        plt.show()
        
    print_best_parameters_formatted(two_half_std_returns, 20, 2.5)

    if (display_graphs == True):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        data = np.array(two_half_std_returns)
        x = data[:,1]
        y = data[:,2]
        z = data[:,5]
        ax.scatter(x,y,z, c=z)
        ax.set_xlabel('Buy RSI')
        ax.set_ylabel('Sell RSI')
        ax.set_zlabel('Returns (%)')
        ax.set_title("Returns for 2.5 std bollinger bands")
        plt.show()

    print_best_parameters_formatted(total_pairs, 50)

    overall_trend = print_plus_minus_overall(df_data['price'])

    if (store_results == True and csv_filename != ""):
        exists = os.path.exists(csv_filename)
        with open(csv_filename, "a") as file:
            if exists == False:
                file.write("coin,start_date,end_date,days,std,buy_rsi,sell_rsi,positive_returns,negative_returns,net_returns,overall_trend,trades_made,captial_usage_percentage\n")
            for result in one_std_returns:
                std = result[0]
                buy_rsi = result[1]
                sell_rsi = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage = "{:.4f}".format(result[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(std)+","+str(buy_rsi)+","+str(sell_rsi)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage+"\n")
            for result in one_half_std_returns:
                std = result[0]
                buy_rsi = result[1]
                sell_rsi = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage = "{:.4f}".format(result[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(std)+","+str(buy_rsi)+","+str(sell_rsi)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage+"\n")
            for result in two_std_returns:
                std = result[0]
                buy_rsi = result[1]
                sell_rsi = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage = "{:.4f}".format(result[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(std)+","+str(buy_rsi)+","+str(sell_rsi)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage+"\n")
            for result in two_half_std_returns:
                std = result[0]
                buy_rsi = result[1]
                sell_rsi = result[2]
                p_returns = "{:.4f}".format(result[3])
                n_returns = "{:.4f}".format(result[4])
                returns = "{:.4f}".format(result[5])
                trend = "{:.4f}".format(overall_trend)
                trades = result[6]
                capital_usage = "{:.4f}".format(result[7])
                file.write(symbol+","+start_day+","+end_day+",")
                file.write(str((datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')).days))
                file.write(","+str(std)+","+str(buy_rsi)+","+str(sell_rsi)+","+p_returns+","+n_returns+","+returns+","+trend+","+str(trades)+","+capital_usage+"\n")
            
    if (pkl_filename != ""):
        outfile = open(pkl_filename, "wb")
        pickle.dump(total_pairs, outfile)
        outfile.close()
        

if __name__ == '__main__':
    test_BB_RSI(symbol="XRP", start_day="11/04/2020 00:00:00", end_day="11/06/2020 00:00:00")