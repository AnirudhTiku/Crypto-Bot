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

# calculates a single set of one standard deviation bollinger band values for a given set of closing_prices
# 
# parameters: data, a list of 20 data points containing the closing_prices
# 
# returns: a list containing a single set of 1std bollinger bands [bottom_band, middle_band, and top_band]
def bollinger_bands(data):
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
def two_std_bollinger_bands_data(data):
    band_values = []
    for i in range(20):
        band_values.append([None, None, None])
    for i in range(len(data) - 20):
        band_values.append(two_std_bollinger_bands(data[i: i + 21]))
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
def double_deviation_bands_data(data):
    band_values = []
    for i in range(20):
        band_values.append([None, None, None, None])
    for i in range(len(data) - 20):
        band_values.append(double_deviation_bands(data[i: i + 21]))
    return band_values

# calculates one standard deviation bollinger band values for all len(20) subsets given set of closing_prices
# 
# parameters: data, a list (20+ values) of data points containing the closing_prices
# 
# returns: a list containing lists of 1std bands 
# [[-1std, MA, +1std], [-1std, MA, +1std], ... ,[-1std, MA, +1std]]
def bollinger_bands_data(data):
    band_values = []
    for i in range(20):
        band_values.append([None, None, None])
    for i in range(len(data) - 20):
        band_values.append(bollinger_bands(data[i: i + 21]))
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
        RS = ((positive_closings/(len(data) - 2)) * 13 + last_change)/(((negative_closings + 0.0001)/ (len(data) - 2))* 14)
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
    for i in range(14):
        RSI_values.append(50)
    for i in range(len(data) - 14):
        RSI_values.append(RSI(data[0: 14 + i]))
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
def MACD(data):
    return EMA(data[-51: -1]) - EMA(data[-201: -1])

# calculates a list of MACD(moving average convergence/divergence) values for a given set of closing_prices
# 
# parameters: data, set of closing_prices with 200+ closing_prices
# 
# returns: a list containing float values representing the value of the MACD over the subsets [n: n + 200], where n<len(data)-200
def MACD_data(data):
    MACD_values = []
    for i in range(200):
        MACD_values.append(0)
    for i in range(200, len(data)):
        MACD_value = MACD(data[i - 200: i + 1])
        MACD_values.append(MACD_value)
    return MACD_values


# calculates a signal line value for a given set of MACD values
# 
# parameters: data, set of MACD values with 20+ entires
# 
# returns: a float value representing the value of the MACD over the given period
def signal_line_data(MACD_values):
    signal_line_values = []
    for i in range(20):
        signal_line_values.append(0)
    for i in range(20, len(MACD_values)):
        if (MACD_values[i] == 0):
            signal_line_values.append(0)
        else:
            signal_line_values.append(EMA(MACD_values[i - 20: i + 1]))
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

