from binance.client import Client
from binance.enums import KLINE_INTERVAL_1DAY, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceAPIException
import matplotlib
import config
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math
import statistics
import time
import requests
from scipy import stats

# imitates bot using 1std bollinger bands to trade 
#  
# buy signal: if price is below bottom band
# sell signal: if price is above top band 
# 
# paramters: data, set of closing_times and closing_prices used to trade
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]

def test_BB_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        bottom_BB = data[i][2]
        middle_BB = data[i][3]
        top_BB = data[i][4]
        if (len(pair) == 1):
            if price < low_price[1]:
                low_price = [date, price]
            elif price > high_price[1]:
                high_price = [date, price]
        if price <= bottom_BB and len(pair) == 0:
            pair.append([date, price])
            low_price = [date, price]
            high_price = [date, price]
        if price >= top_BB and len(pair) == 1:
            pair.append(low_price)
            pair.append(high_price)
            pair.append([date, price])
            buy_sell_pairs.append(pair)
            pair = []
    return buy_sell_pairs

# imitates bot using 2std bollinger bands to trade 
# 
# paramters: data, set of closing_times and closing_prices used to trade
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]
def test_double_deviation_band_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    buy_ready = False
    sell_ready = False
    for i in range(20, len(data)):
        date = data[i][0]
        current_price = data[i][1]
        current_two_deviations_down = data[i][2]
        current_one_deviation_down = data[i][3]
        current_one_deviation_up = data[i][4]
        current_two_deviations_up = data[i][5]
        previous_price = data[i - 1][1]
        previous_two_deviations_down = data[i - 1][2]
        previous_one_deviation_down = data[i - 1][3]
        previous_one_deviation_up = data[i - 1][4]
        previous_two_deviations_up = data[i - 1][5]
        if (len(pair) == 1):
            if current_price < low_price[1]:
                low_price = [date, current_price]
            elif current_price > high_price[1]:
                high_price = [date, current_price]
        #buying signals
        if len(pair) == 0:
            if buy_ready == False:
                if current_price <= current_two_deviations_down:
                    buy_ready = True
            else:
                if current_price >= (current_one_deviation_down + current_one_deviation_up) / 2:
                    pair.append([date, current_price])
                    low_price = [date, current_price]
                    high_price = [date, current_price]
                    buy_ready = False
        #selling signals
        if len(pair) == 1:
            buy_price = pair[0][1]
            if (current_price <= buy_price * 0.95):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, current_price])
                buy_sell_pairs.append(pair)
                pair = []
                sell_ready = False
            elif sell_ready == False:
                if current_price >= current_two_deviations_up:
                    sell_ready = True
            else:
                if current_price <= current_one_deviation_down:
                    pair.append(low_price)
                    pair.append(high_price)
                    pair.append([date, current_price])
                    buy_sell_pairs.append(pair)
                    pair = []
                    sell_ready = False
    return buy_sell_pairs

# imitates bot using bollinger bands to trade 
# 
# paramters: data, set of closing_times and closing_prices used to trade 
# paramters: buy_RSI, the rsi value used for the buy signal 
# paramters: sell_RSI, the rsi value used for the sell signal
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]
def test_double_deviation_band_RSI_returns_with_parameters(data, buy_RSI, sell_RSI):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    buy_ready = False
    sell_ready = False
    for i in range(20, len(data)):
        date = data[i][0]
        current_price = data[i][1]
        current_two_deviations_down = data[i][2]
        current_one_deviation_down = data[i][3]
        current_one_deviation_up = data[i][4]
        current_two_deviations_up = data[i][5]
        current_RSI = data[i][6]
        previous_price = data[i - 1][1]
        previous_two_deviations_down = data[i - 1][2]
        previous_one_deviation_down = data[i - 1][3]
        previous_one_deviation_up = data[i - 1][4]
        previous_two_deviations_up = data[i - 1][5]
        previous_RSI = data[i - 1][6]
        if (len(pair) == 1):
            if current_price < low_price[1]:
                low_price = [date, current_price]
            elif current_price > high_price[1]:
                high_price = [date, current_price]
        #buying signals
        if len(pair) == 0:
            if buy_ready == False:
                if current_price <= current_two_deviations_down:
                    buy_ready = True
            else:
                if current_price >= (current_one_deviation_down + current_one_deviation_up) / 2 and current_RSI <= buy_RSI:
                    pair.append([date, current_price])
                    low_price = [date, current_price]
                    high_price = [date, current_price]
                    buy_ready = False
        #selling signals
        if len(pair) == 1:
            if sell_ready == False:
                if current_price >= current_two_deviations_up:
                    sell_ready = True
            else:
                if current_price <= current_one_deviation_down and current_RSI >= sell_RSI:
                    pair.append(low_price)
                    pair.append(high_price)
                    pair.append([date, current_price])
                    buy_sell_pairs.append(pair)
                    pair = []
                    sell_ready = False
    return buy_sell_pairs

# optimizes the values of the rsi buy and sell signals when using 2std bollinger bands with rsi
# 
# paramters: data, set of closing_times and closing_prices used to trade 
#  
# returns: a list (sorted in ascending order) of the most optimal rsi signals in the format below
#  
#      worst returns                   2nd worst returns                best returns
# [[buy_rsi, sell_rsi, returns], [buy_rsi, sell_rsi, returns], ... ,[buy_rsi, sell_rsi, returns]]
def optimize_double_bands_rsi_returns(data):
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
    total_pairs = []
    for i in range(30, 60):
        for j in range(40, 70):
            results = []
            results.append(i)
            results.append(j)
            buy_sell_pairs = test_double_deviation_band_RSI_returns_with_parameters(data, i, j)
            returns = analyze_results(buy_sell_pairs)
            results.append(returns[1])
            total_pairs.append(results)
            print("buy_RSI: {br}, sell_RSI: {sr} returns: {returns}".format(br=i, sr=j, returns=returns[1]))
    mergeSort(total_pairs)
    return total_pairs
    
# imitates bot using MACD and 2std bollinger bands to trade
# 
# buy signal: MACD - signal line > 0 and +1std < price < +2std
# sell signal: MACD - signal line < 0 and +1std > price 
# 
# paramters: data, set of closing_times and closing_prices used to trade
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]
def test_macd_double_sd_bands_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        macd = data[i][2]
        signal_line = data[i][3]
        two_deviations_down = data[i][4]
        one_deviation_down = data[i][5]
        one_deviation_up = data[i][6]
        two_deviations_up = data[i][7]
        if macd != 0 and signal_line != 0:
            if (len(pair) == 1):
                if price < low_price[1]:
                    low_price = [date, price]
                elif price > high_price[1]:
                    high_price = [date, price]
            if (macd > signal_line and price <= two_deviations_up and price >= one_deviation_up) and len(pair) == 0:
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
            if (macd < signal_line and price <= one_deviation_up) and len(pair) == 1:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

# imitates bot using RSI to trade
# 
# buy signal: RSI <= 40
# sell signal: RSI >= 60
# 
# paramters: data, set of closing_times and closing_prices used to trade
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]
def test_RSI_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        if (len(pair) == 1):
            if data[i][1] < low_price[1]:
                low_price = [data[i][0], data[i][1]]
            elif data[i][1] > high_price[1]:
                high_price = [data[i][0], data[i][1]]
        if data[i][2] <= 40 and len(pair) == 0:
            pair.append([data[i][0], data[i][1]])
            low_price = [data[i][0], data[i][1]]
            high_price = [data[i][0], data[i][1]]
        if data[i][2] >= 60 and len(pair) == 1:
            pair.append(low_price)
            pair.append(high_price)
            pair.append([data[i][0], data[i][1]])
            buy_sell_pairs.append(pair)
            pair = []
    return buy_sell_pairs

# imitates bot using RSI to trade
# 
# paramters: data, set of closing_times and closing_prices used to trade
# paramters buy_RSI, rsi value which triggers buy signal
# paramters sell_RSI, rsi value which triggers sell signal
#
# buy signal: RSI <= buy_signal
# sell signal: RSI >= sell_signal
#  
# returns: a list of buy_sell_pairs containing the buy time, buy price, lowest price between buy and sell, time of 
# lowest price, highest price between buy and sell, time of highest price, sell time, sell price, in the format below: 
#  
# [[[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]], 
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]],...,
# [[buy time, buy price], [lowest time, lowest price], [highest time, highest price], [sell time, sell price]]]
def test_RSI_returns_with_parameters(data, buy_signal, sell_signal):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        if (len(pair) == 1):
            if data[i][1] < low_price[1]:
                low_price = [data[i][0], data[i][1]]
            elif data[i][1] > high_price[1]:
                high_price = [data[i][0], data[i][1]]
        if data[i][2] <= buy_signal and len(pair) == 0:
            pair.append([data[i][0], data[i][1]])
            low_price = [data[i][0], data[i][1]]
            high_price = [data[i][0], data[i][1]]
        if data[i][2] >= sell_signal and len(pair) == 1:
            pair.append(low_price)
            pair.append(high_price)
            pair.append([data[i][0], data[i][1]])
            buy_sell_pairs.append(pair)
            pair = []
    return buy_sell_pairs

def optimize_RSI_returns(data):
    total_pairs = []
    for i in range(20, 60):
        for j in range(40, 70):
            results = []
            results.append(i)
            results.append(j)
            buy_sell_pairs = test_RSI_returns_with_parameters(data, i, j)
            returns = analyze_results(buy_sell_pairs)
            results.append(returns[1])
            total_pairs.append(results)
            print("buy_RSI: {br}, sell_RSI: {sr} returns: {returns}".format(br=i, sr=j, returns=returns[1]))
    return total_pairs


def test_BB_RSI_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        bottom_BB = data[i][2]
        middle_BB = data[i][3]
        top_BB = data[i][4]
        relative_strength_index = data[i][5]
        if (len(pair) == 1):
            if price < low_price[1]:
                low_price = [date, price]
            elif price > high_price[1]:
                high_price = [date, price]
        if len(pair) == 0:
            if ((price <= bottom_BB and relative_strength_index <= 40) or (price <= (middle_BB + top_BB)/2 and relative_strength_index <= 39)):
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
        if len(pair) == 1:
            buy_price = pair[0][1]
            if ((price >= top_BB and relative_strength_index >= 55) or (relative_strength_index >= 52 and price >= (middle_BB + top_BB)/2)):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
            elif (price < buy_price * 0.999):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

def test_BB_RSI_returns_with_parameters(data, buy_weak, buy_strong, sell_weak, sell_strong):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        bottom_BB = data[i][2]
        middle_BB = data[i][3]
        top_BB = data[i][4]
        relative_strength_index = data[i][5]
        if (len(pair) == 1):
            if price < low_price[1]:
                low_price = [date, price]
            elif price > high_price[1]:
                high_price = [date, price]
        if len(pair) == 0:
            if ((price <= bottom_BB and relative_strength_index <= buy_weak) or (price <= (middle_BB + top_BB)/2 and relative_strength_index <= buy_strong)):
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
        if len(pair) == 1:
            buy_price = pair[0][1]
            if ((price >= top_BB and relative_strength_index >= sell_weak) or (relative_strength_index >= sell_strong and price >= (middle_BB + top_BB)/2)):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
            elif (price < buy_price * 0.99):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

def test_simple_BB_RSI_returns_with_parameters(data, buy_RSI, sell_RSI):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        bottom_BB = data[i][2]
        middle_BB = data[i][3]
        top_BB = data[i][4]
        relative_strength_index = data[i][5]
        if (len(pair) == 1):
            if price < low_price[1]:
                low_price = [date, price]
            elif price > high_price[1]:
                high_price = [date, price]
        if len(pair) == 0:
            if price <= bottom_BB and relative_strength_index <= buy_RSI:
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
        if len(pair) == 1:
            buy_price = pair[0][1]
            if price >= top_BB and relative_strength_index >= sell_RSI:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
            elif (price < buy_price * 0.99):
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

def optimize_simple_BB_RSI_returns(data):
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

    total_pairs = []
    for i in range(30, 60):
        for j in range(30, 70):
            results = []
            results.append(i)
            results.append(j)
            buy_sell_pairs = test_simple_BB_RSI_returns_with_parameters(data, i, j)
            returns = analyze_results(buy_sell_pairs)
            results.append(returns[1])
            total_pairs.append(results)
            print("buy_RSI: {br}, sell_RSI: {sr}, returns: {returns}".format(br=i, sr=j, returns=returns[1]))
    mergeSort(total_pairs)
    return total_pairs

def optimize_BB_RSI_returns(data):
    def mergeSort(array):
        if len(array) > 1:

            r = len(array)//2
            L = array[:r]
            M = array[r:]

            mergeSort(L)
            mergeSort(M)

            i = j = k = 0

            while i < len(L) and j < len(M):
                if L[i][4] < M[j][4]:
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

    total_pairs = []
    for i in range(30, 45):
        for j in range(35, 45):
            for k in range(50, 60):
                for l in range(45, 70):
                    results = []
                    results.append(i)
                    results.append(j)
                    results.append(k)
                    results.append(l)
                    buy_sell_pairs = test_BB_RSI_returns_with_parameters(data, i, j, k, l)
                    returns = analyze_results(buy_sell_pairs)
                    results.append(returns[1])
                    total_pairs.append(results)
                    print("buy_weak: {bw}, buy_strong: {bs}, sell_weak:{sw}, sell_strong: {ss}, returns: {returns}".format(bw=i, bs=j, sw=k, ss=l, returns=returns[1]))
    mergeSort(total_pairs)
    return total_pairs

def test_double_deviation_bands_rsi_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    signal = 0
    for i in range(20, len(data)):
        date = data[i][0]
        price = data[i][1]
        two_deviations_down = data[i][2]
        one_deviation_down = data[i][3]
        one_deviation_up = data[i][4]
        two_deviations_up = data[i][5]
        relative_strength_index = data[i][6]
        previous_price = data[i - 1][1]
        previous_two_deviations_down = data[i - 1][2]
        previous_one_deviation_down = data[i - 1][3]
        previous_one_deviation_up = data[i - 1][4]
        previous_two_deviations_up = data[i - 1][5]
        previous_relative_strength_index = data[i - 1][6]
        if (len(pair) == 1):
            if price < low_price[1]:
                low_price = [date, price]
            elif price > high_price[1]:
                high_price = [date, price]
        if len(pair) == 0:
            if previous_price <= one_deviation_down and price >= one_deviation_down and relative_strength_index <= 55:
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
        if len(pair) == 1:
            buy_price = pair[0][1]
            if previous_price > previous_one_deviation_down and price < one_deviation_down and relative_strength_index >= 45:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
            elif previous_price > previous_one_deviation_up and price < one_deviation_up and relative_strength_index >= 45:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = [] 
            elif price <= buy_price * 0.95:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = [] 
    return buy_sell_pairs


def test_MACD_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(len(data)):
        if (data[i][2] != 0 and data[i][3] != 0):
            if (len(pair) == 1):
                if data[i][1] < low_price[1]:
                    low_price = [data[i][0], data[i][1]]
                elif data[i][1] > high_price[1]:
                    high_price = [data[i][0], data[i][1]]
            if data[i][2] > data[i][3] and len(pair) == 0:
                pair.append([data[i][0], data[i][1]])
                low_price = [data[i][0], data[i][1]]
                high_price = [data[i][0], data[i][1]]
            if data[i][2] < data[i][3] and len(pair) == 1:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([data[i][0], data[i][1]])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

def test_MACD_RSI_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(len(data)):
        date = data[i][0]
        price = data[i][1]
        macd = data[i][2]
        signal_line = data[i][3]
        relative_strength_index = data[i][4]
        if (macd != 0 and signal_line != 0):
            if (len(pair) == 1):
                if price < low_price[1]:
                    low_price = [date, price]
                elif price > high_price[1]:
                    high_price = [date, price]
            if macd > signal_line and len(pair) == 0:
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
            if macd < signal_line and len(pair) == 1:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

def test_MACD_BB_returns(data):
    buy_sell_pairs = []
    pair = []
    low_price = 0
    high_price = 0
    for i in range(len(data)):
        date = data[i][0]
        price = data[i][1]
        bottom_band = data[i][2]
        middle_band = data[i][3]
        top_band = data[i][4]
        macd = data[i][5]
        signal_line = data[i][6]
        if (macd != 0 and signal_line != 0):
            if (len(pair) == 1):
                if price < low_price[1]:
                    low_price = [date, price]
                elif price > high_price[1]:
                    high_price = [date, price]
            if macd > signal_line and (abs(price-middle_band) < min(abs(price-top_band), abs(price-bottom_band))) and len(pair) == 0:
                pair.append([date, price])
                low_price = [date, price]
                high_price = [date, price]
            if macd < signal_line and len(pair) == 1:
                pair.append(low_price)
                pair.append(high_price)
                pair.append([date, price])
                buy_sell_pairs.append(pair)
                pair = []
    return buy_sell_pairs

# prints and returns the uncompounded and compounded returns of a set of buy sell pairs
#  
# paramters: buy_sell_pairs, sets of buy_sell_pairs in the format shown in test_BB_returns function
# 
# returns: a list of return values in the form [uncompound returns, positive returns, negative returns, compounded returns]
def analyze_results(buy_sell_pairs):
    if (len(buy_sell_pairs) == 0):
        #print("No orders made\n")
        return [0,0,0,0]
    else:
        uncompound_returns = 0
        compounded_returns = 5000
        positive_returns = 0
        negative_returns = 0
        for pair in buy_sell_pairs:
            return_value = pair[3][1] - pair[0][1]
            uncompound_returns += return_value
            compounded_returns *= pair[3][1]/pair[0][1]
            if return_value > 0:
                positive_returns += return_value
            else:
                negative_returns += return_value
        returns = [(uncompound_returns/buy_sell_pairs[0][0][1]) * 100,
                ((compounded_returns - 5000)/5000) * 100,
                (positive_returns/buy_sell_pairs[0][0][1]) * 100, 
                (negative_returns/buy_sell_pairs[0][0][1]) * 100]
        print("Net Returns: " + str(returns[0]) + "%\n")
        print("Positive Returns: " + str(returns[2]) + "%\n")
        print("Negative Returns: " + str(returns[3]) + "%\n")
        print("Net Compounded Returns: " + str(returns[1]) + "%\n")
        return returns

# prints and returns the compounded returns of a set of buy sell pairs
#  
# paramters: buy_sell_pairs, sets of buy_sell_pairs in the format shown in test_BB_returns function
# 
# returns: returns a float representing compounded returns of a set of trades
def analyze_results_compounded(buy_sell_pairs):
    if (len(buy_sell_pairs) == 0):
        print("No orders made\n")
        return 0
    else:
        current_value = 5000
        for pair in buy_sell_pairs:
            current_value *= pair[3][1]/pair[0][1]
        compouned_returns = ((current_value - 5000)/5000) * 100
        print("Compounded Returns: " + str(compouned_returns) + "%")
        return compouned_returns
