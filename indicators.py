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
import collections

# calculates a single set of bollinger band values, with standard deviation of your choice,
# for a given set of closing_prices
# 
# parameters: data, a list of 20 data points containing the closing_prices 
# parameters: std_value, float used to denote the number of standard deviations the top
# and bottom band should be away from the middle band
# 
# returns: a list containing a single set of std_value std bollinger bands 
# [bottom_band, middle_band, and top_band]
def single_bollinger_bands(data=[], std_value=1.5):
    if std_value < 1:
        print("Invalid parameters, see documentation for details")
        exit(0)
    MB = math.fsum(data) / len(data)
    SD = statistics.stdev(data)
    TB = MB + (SD * std_value)
    BB = MB - (SD * std_value)
    #print("BB: {BB}, MB: {MB}, TB: {TB}, SD: {SD}".format(BB=BB, MB=MB, TB=TB, SD=SD))
    value = [BB, MB, TB]
    return value

# calculates a single set of bollinger band values, with standard deviation of your choice,
# for a given set of closing_prices. Gets bollinger bands of x standard deviation from 
# the starting value, to the end value, increasing in increments of increment_numerator/increment_denominator 
# 
# parameters: data, a list of 20 data points containing the closing_prices 
# parameters: start_numerator and start_denominator, integers used to denote the number of standard deviations the first
# set of top and bottom bands should be should be away from the middle band
# parameters: end_numerator and end_denominator, integers used to denote the number of standard deviations the last
# set of top and bottom bands should be should be away from the middle band
# parameters: increment_numerator and increment_denominator, integers used to denote the size of increments that
# standard deviations should be increasing from the first to last set of bollinger bands
# 
# returns: a list containing a single set of (std_numerator/std_denominator)std bollinger bands 
# [negative_largest_deviation_band,..., negative_smallest_deviation_band, middle_band, 
# smallest_deviation_band,..., largest_deviation_band]
def all_bollinger_bands(data=[], 
                        start_numerator=1,
                        start_denominator=1,
                        end_numerator=1,
                        end_denominator=1,
                        increment_numerator=1,
                        increment_denominator=1):

    if increment_denominator < 1 or start_denominator < 1 or end_denominator < 1:
        print("Invalid parameters, see documentation for details")
        exit(0)

    MB = math.fsum(data) / len(data)
    SD = statistics.stdev(data)
    starting_std = start_numerator/start_denominator
    ending_std = end_numerator/end_denominator
    increment = increment_numerator/increment_denominator
    bollinger_bands = []
    bollinger_bands.append(MB)
    while (starting_std < ending_std):
        bollinger_bands.insert(0, MB + (SD * -1 * starting_std))
        bollinger_bands.insert(len(bollinger_bands), MB + (SD * starting_std))
        starting_std += increment
    return bollinger_bands

# calculates a single set of bollinger band values, with standard deviation of your choice,
# for a given set of closing_prices. Gets bollinger bands of x standard deviation from 
# the starting value, to the end value, increasing in increments of increment_numerator/increment_denominator 
# 
# parameters: data, a list of 20 data points containing the closing_prices 
# parameters: std_band_values, set of std_values for which you wish to get the bollinger bands of,
# must be in ascending order 
# 
# returns: a list containing a single set of bollinger bands 
# [negative_largest_deviation_band,..., negative_smallest_deviation_band, middle_band, 
# smallest_deviation_band,..., largest_deviation_band]  
def select_bollinger_bands(data=[],std_band_values=[1,2]):
    if data == [] or std_band_values==[]:
        print("Please enter valid set of data")
        exit(0)
    MB = math.fsum(data) / len(data)
    SD = statistics.stdev(data)
    bollinger_bands = []
    for std in std_band_values:
        bollinger_bands.insert(0, MB + (SD * -1 * std))
        bollinger_bands.insert(len(bollinger_bands), MB + (SD * std))
    return bollinger_bands


# calculates a single set of one standard deviation bollinger band values for a given set of closing_prices
# 
# parameters: data, a list of 20 data points containing the closing_prices
# 
# returns: a list containing a single set of 1std bollinger bands [bottom_band, middle_band, and top_band]
def bollinger_bands_one_std(data):
    MB = math.fsum(data) / len(data)
    SD = math.sqrt(statistics.variance(data))
    TB = MB + SD 
    BB = MB - SD 
    #print("BB: {BB}, MB: {MB}, TB: {TB}, SD: {SD}".format(BB=BB, MB=MB, TB=TB, SD=SD))
    value = [BB, MB, TB]
    return value


# calculates a single set of two standard deviation bollinger band values for a given set of closing_prices
# 
# parameters: data, a list of 20 data points containing the closing_prices
# 
# returns: a list containing a single set of 2std bollinger bands [bottom_band, middle_band, and top_band]
def two_std_bollinger_bands(data):
    MB = math.fsum(data) / len(data)
    SD = math.sqrt(statistics.variance(data))
    TB = MB + SD * 2
    BB = MB - SD * 2
    #print("BB: {BB}, MB: {MB}, TB: {TB}, SD: {SD}".format(BB=BB, MB=MB, TB=TB, SD=SD))
    value = [BB, MB, TB]
    return value

# calculates two standard deviation bollinger band values for all len(20) subsets given set of closing_prices
# 
# parameters: data, a list (20+ values) of data points containing the closing_prices
# 
# returns: a list containing lists of 2std bands 
# [[-2std, MA, +2std], [-2std, MA, +2std], ... ,[-2std, MA, +2std]]
def two_std_bollinger_bands_data(data=[], sma_length=20):
    band_values = []
    for i in range(sma_length):
        band_values.append([None, None, None])
    for i in range(len(data) - sma_length):
        band_values.append(two_std_bollinger_bands(data[i: i + sma_length + 1]))
    return band_values

# calculates a single set of two and one standard deviation bollinger band values for a given set of closing_prices
# 
# parameters: data, a list of 20 data points containing the closing_prices
# 
# returns: a list containing a single set of 2std and 1std bollinger bands [-2std, -1std, +1std, +2std]
def double_deviation_bands(data):
    middle_band = math.fsum(data) / len(data)
    standard_deviation = math.sqrt(statistics.variance(data))
    two_deviations_down = middle_band - (standard_deviation * 2)
    one_deviation_down = middle_band - standard_deviation
    one_deviation_up = middle_band + standard_deviation
    two_deviations_up = middle_band + (standard_deviation * 2)
    value = [two_deviations_down, one_deviation_down, one_deviation_up, two_deviations_up]
    return value

# calculates two and one standard deviation bollinger band values for all len(20) subsets given set of closing_prices
# 
# parameters: data, a list (20+ values) of data points containing the closing_prices
# 
# returns: a list containing lists of 2std and 1std bollinger bands 
# [[-2std, -1std, +1std, +2std], [-2std, -1std, +1std, +2std], ... ,[-2std, -1std, +1std, +2std]]
def double_deviation_bands_data(data=[], sma_length=20):
    band_values = []
    for i in range(sma_length):
        band_values.append([None, None, None, None])
    for i in range(len(data) - sma_length):
        band_values.append(double_deviation_bands(data[i: i + sma_length + 1]))
    return band_values

# calculates one standard deviation bollinger band values for all len(20) subsets given set of closing_prices
# 
# parameters: data, a list (20+ values) of data points containing the closing_prices
# 
# returns: a list containing lists of 1std bands 
# [[-1std, MA, +1std], [-1std, MA, +1std], ... ,[-1std, MA, +1std]]
def one_std_bollinger_bands_data(data=[], sma_length=20):
    band_values = []
    for i in range(sma_length):
        band_values.append([None, None, None])
    for i in range(len(data) - sma_length):
        band_values.append(bollinger_bands_one_std(data[i: i + sma_length + 1]))
    return band_values

# calculates bollinger band values for all len(20) subsets given set of closing_prices
# 
# parameters: data, a list (20+ values) of data points containing the closing_prices
# parameters: std_numerator and std_denominator, integers used to denote the number of standard deviations the top
# and bottom band should be away from the middle band
# 
# returns: a list containing lists of x_std bands 
# [[-x_std, MA, +x_std], [-x_std, MA, +x_std], ... ,[-x_std, MA, +x_std]]
def single_bollinger_bands_data(data=[], sma_length=20, std_value=1.5):
    band_values = []
    for i in range(sma_length):
        band_values.append([None, None, None])
    for i in range(len(data) - sma_length):
        band_values.append(single_bollinger_bands(data[i: i + sma_length + 1], std_value))
    return band_values


# calculates a single RSI value for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 14+ closing_prices
# 
# returns: a single float denoting the RSI value of a given set of closing_prices
def RSI(data):
    positive_closings = 0
    negative_closings = 0
    for i in range(1, len(data) - 1):
        percentage_change = (data[i] - data[i - 1])
        if (percentage_change > 0):
            positive_closings += percentage_change
        else:
            negative_closings -= percentage_change
    last_change = (data[-1] - data[-2])
    if (last_change >= 0):
        RS = ((positive_closings/(len(data) - 2)) * 13 + last_change)/(((negative_closings + 0.00001)/ (len(data) - 2))* 14)
        return 100 - (100/(1 + RS))
    else:
        RS = ((positive_closings/(len(data) - 2)) * 14)/((negative_closings/ (len(data) - 2)) * 13 - last_change)
        return 100 - (100/(1 + RS))

# calculates a list RSI values for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 14+ closing_prices
# 
# returns: a list of floats denoting the RSI values of the subsets [0:n], where 14<n<len(data)
def RSI_data(data):
    RSI_values = []
    postive_sum = 0
    negative_sum = 0
    days_tracked = 0
    RSI_values.append(50)
    for i in range(1, 15):
        RSI_values.append(50)
        change = data[i]-data[i-1]
        if change > 0:
            postive_sum += change
        else:
            negative_sum -= change
        days_tracked += 1
    for i in range(15, len(data)):
        change = data[i]-data[i-1]
        rsi = 0
        if change >= 0:
            rs = ((postive_sum/days_tracked) * 13 + change)/(((negative_sum + 0.000001)/days_tracked) * 13)
            rsi = 100 - (100/(1+rs))
            postive_sum += change
        else:
            rs = ((postive_sum/days_tracked) * 13)/(((negative_sum + 0.000001)/days_tracked) * 13 - change)
            rsi = 100 - (100/(1+rs))
            negative_sum -= change
        RSI_values.append(rsi)
        days_tracked += 1
    return RSI_values

# calculates an EMA(exponential moving average) value for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 2+ closing_prices
# 
# returns: a float value representing the value of the EMA over the given period
def EMA(data):
    EMA_previous = sum(data[0:-2]) / (len(data) - 1)
    multiplier = (2 / len(data))
    return (data[-1] * multiplier) + (EMA_previous * (1 - multiplier))

# calculates an SMA(simple moving average) value for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 2+ closing_prices
# 
# returns: a float value representing the value of the SMA over the given period
def SMA(data):
    return sum(data)/len(data)

# calculates an MACD(moving average convergence/divergence) value for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 200+ closing_prices
# 
# returns: a float value representing the value of the MACD over the given period
def MACD(data=[], lower_EMA_length=50, longer_EMA_length=200):
    return EMA(data[(lower_EMA_length + 1) * -1: -1]) - EMA(data[-1 * (longer_EMA_length + 1): -1])

# calculates a list of MACD(moving average convergence/divergence) values for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 200+ closing_prices
# 
# returns: a list containing float values representing the value of the MACD over the subsets [n: n + 200], where n<len(data)-200
def MACD_data(data, lower_EMA_length, longer_EMA_length):
    short_ema_q = collections.deque(maxlen=lower_EMA_length - 1)
    short_sum = 0
    short_multiplier = 2 / (lower_EMA_length + 1)
    long_ema_q = collections.deque(maxlen=longer_EMA_length - 1)
    long_sum = 0
    long_multiplier = 2 / (longer_EMA_length + 1)
    MACD_values = []
    for i in range(longer_EMA_length - 1):
        MACD_values.append(0)
        if i > longer_EMA_length - lower_EMA_length:
            short_ema_q.append(data[i])
            short_sum += data[i]
        long_ema_q.append(data[i])
        long_sum += data[i]
    for i in range(longer_EMA_length - 1, len(data)):
        current_value = data[i]
        short_ema = (current_value * short_multiplier) + ((short_sum/(lower_EMA_length-1)) * (1-short_multiplier))
        long_ema = (current_value * long_multiplier) + ((long_sum/(longer_EMA_length-1)) * (1-long_multiplier))
        MACD_value = short_ema - long_ema
        MACD_values.append(MACD_value)
        short_sum += current_value - short_ema_q.popleft()
        long_sum += current_value - long_ema_q.popleft()
        short_ema_q.append(current_value)
        long_ema_q.append(current_value)
    return MACD_values


# calculates a signal line value for a given set of MACD values
# 
# parameters: data, set of MACD values with 20+ entires
# 
# returns: a float value representing the value of the MACD over the given period
def signal_line_data(MACD_values=[], EMA_length=20):
    signal_line_values = []
    for i in range(EMA_length):
        signal_line_values.append(0)
    for i in range(EMA_length, len(MACD_values)):
        if (MACD_values[i] == 0):
            signal_line_values.append(0)
        else:
            signal_line_values.append(EMA(MACD_values[i - EMA_length: i + 1]))
    return signal_line_values

# calculates a signal line value for a given set of MACD values
# 
# parameters: data, set of MACD values with 20+ entires
# 
# returns: a float value representing the value of the MACD over the given period
def MACD_signal_line_difference(MACD, signal_line):
    differences = []
    for i in range(len(MACD)):
        if MACD[i] == 0 or signal_line[i] == 0:
            differences.append(0)
        else:
            differences.append(MACD[i] - signal_line[i])
    return differences

def TEMA(data):
    look_back_period = int(len(data)/3)
    ema1 = []
    for i in range(look_back_period * 2):
        ema1.append(EMA(data[i: i + look_back_period + 1]))
    ema2 = []
    for j in range(look_back_period):
        ema2.append(EMA(ema1[j: j + look_back_period + 1]))
    ema3 = EMA(ema2)

    return (3 * ema1[-1]) - (3 * ema2[-1]) + ema3

def TEMA_data(data, look_back):
    tema = []
    look_back_period = look_back * 3
    if (len(data) < look_back_period):
        print("Invalid look back period")
        exit(0)
    else:
        ema1 = collections.deque(maxlen=look_back - 1)
        ema1_sum = 0
        ema2 = collections.deque(maxlen=look_back - 1)
        ema2_sum = 0
        ema3 = collections.deque(maxlen=look_back - 1)
        ema3_sum = 0
        multiplier = 2/(look_back + 1)
        ema1_value = 0
        ema2_value = 0
        ema3_value = 0

        for j in range(look_back_period - 3):
            tema.append(None)
            current_value = data[j]
            if j > look_back - 1:
                ema1_value = current_value * multiplier + (ema1_sum/(look_back - 1) * (1-multiplier))
                ema1_sum -= ema1.popleft()
            ema1_sum += current_value
            ema1.append(current_value)
            if j > look_back - 1:
                if j > (look_back - 1) * 2:
                    ema2_value = ema1_value * multiplier + (ema2_sum/(look_back - 1) * (1-multiplier))
                    ema2_sum -= ema2.popleft()
                ema2_sum += ema1_value
                ema2.append(ema1_value)
            if j > (look_back - 1) * 2:
                ema3_sum += ema2_value
                ema3.append(ema2_value)
        
        for i in range(look_back_period - 3, len(data)):
            current_value = data[i]
            ema1_value = current_value * multiplier + (ema1_sum/(look_back - 1) * (1-multiplier))
            ema2_value = ema1_value * multiplier + (ema2_sum/(look_back - 1) * (1-multiplier))
            ema3_value = ema2_value * multiplier + (ema3_sum/(look_back - 1) * (1-multiplier))
            tema.append((3 * ema1_value) - (3 * ema2_value) + ema3_value)

            ema1_sum += current_value - ema1.popleft()
            ema1.append(current_value)
            ema2_sum += ema1_value - ema2.popleft()
            ema2.append(ema1_value)
            ema3_sum += ema2_value - ema3.popleft()
            ema3.append(ema2_value)
        return tema


