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

multiplier = {
    "DAYS": 1,
    "HOURS": 24,
    "MINUTES" : 1440
}

# gives candlesticks over a given period, according to the time_interval given
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: start_day and end_day, the start and end day of the period of candlesticks to be obtained
# formatting for start_day and end_day:
# Abbrievated_month zero-padded_day year zero-padded-analog-hour zero-padded minute zero-padded second
# eg. Jun 03 2021 21:23:33
#
# returns: list with the closing times and closing prices for the currency over the given period, in the form below
# [[closing_time, closing_price], [closing_time, closing_price],... ,[closing_time, closing_price]]
def get_historical_klines(symbol='BTC', time_interval='MINUTES', start_day=None, end_day=None, subset_length=None):

    days = datetime.strptime(end_day, '%b %d %Y %H:%M:%S') - datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
    days = days.days

    if (subset_length != None):
        if (days % subset_length != 0):
            print("Data cannot be partionned into even subsets of length " + str(subset_length))
            exit(0)

    client = Client(config.API_KEY, config.API_SECRET)
    print("Checking " + symbol + " prices...")

    try:
        closing_prices = []
        later_timestamp = datetime.strptime(end_day, '%b %d %Y %H:%M:%S')
        earlier_timestamp = None
        KLINES = []
        subset = []
        subset_entries = 0
        days_left = days
        if (time_interval == "DAYS"):
            while days_left > 1000:
                past_days = timedelta(1000)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES
                later_timestamp = earlier_timestamp
                time.sleep(1)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "HOURS"):
            while days_left > 41:
                past_days = timedelta(41)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                time.sleep(1)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES         
        else:
            for i in range(days):
                past_days = timedelta(1)
                earlier_timestamp = (later_timestamp - past_days)
                if subset_length == None:
                    KLINES = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp())) + KLINES
                else:
                    if (subset_length == None):
                        KLINES = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp())) + KLINES
                    else:
                        if (subset_entries == subset_length):
                            KLINES.insert(0, subset)
                            subset = []
                        else:
                            subset_entries += 1
                        subset = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp())) + subset
                later_timestamp = earlier_timestamp
                time.sleep(1)
        if (subset_length == None):
            for kline in KLINES:
                data_point = []
                data_point.append(str(datetime.fromtimestamp(int(kline[6]) / 1000)))
                data_point.append(kline[4])
                closing_prices.append(data_point)
        else:
            for subset in KLINES:
                data_subset = []
                for kline in subset:
                    data_point = []
                    data_point.append(str(datetime.fromtimestamp(int(kline[6]) / 1000)))
                    data_point.append(kline[4])
                    data_subset.append(data_point)
                closing_prices.append(subset)
        return closing_prices
    except BinanceAPIException as e:
        print(e.status_code)
        exit(0)
    except requests.exceptions.ReadTimeout as e:
        print("Timed out")
        exit(0)

# gives candlesticks from a specified number of days back to now
#
# parameters: symbol, the abbreivation of the coin that is being compared to the us dollar
# parameters: time_interval, the length of time that a single candlestick should cover
# parameters: days, the number of days back that is the starting period for candlesticks 
#
# returns: list with the closing times and closing prices for the currency over the given period, in the form below
# [[closing_time, closing_price], [closing_time, closing_price],... ,[closing_time, closing_price]]
def get_recent_klines(symbol='BTC', time_interval='MINUTES', days=1, subset_length=None):
    if (subset_length != None):
        if (days % subset_length != 0):
            print("Data cannot be partionned into even subsets of length " + str(subset_length))
            exit(0)

    client = Client(config.API_KEY, config.API_SECRET)
    print("Checking " + symbol + " prices...")

    try:
        closing_prices = []
        current_timestamp = datetime.now()
        previous_timestamp = datetime.now()
        KLINES = []
        subset = []
        subset_entries = 0
        days_left = days
        if (time_interval == "DAYS"):
            while days_left > 1000:
                past_days = timedelta(1000)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES
                current_timestamp = previous_timestamp
                time.sleep(1)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "HOURS"):
            while days_left > 41:
                past_days = timedelta(41)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                time.sleep(1)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES         
        else:
            for i in range(days):
                past_days = timedelta(1)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                if (subset_length == None):
                    KLINES = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp())) + KLINES
                else:
                    if (subset_entries == subset_length):
                        KLINES.insert(0, subset)
                        subset = []
                    else:
                        subset_entries += 1
                    subset = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp())) + subset
                current_timestamp = previous_timestamp
                time.sleep(1)
        if (subset_length == None):
            for kline in KLINES:
                data_point = []
                data_point.append(str(datetime.fromtimestamp(int(kline[6]) / 1000)))
                data_point.append(kline[4])
                closing_prices.append(data_point)
        else:
            for subset in KLINES:
                data_subset = []
                for kline in subset:
                    data_point = []
                    data_point.append(str(datetime.fromtimestamp(int(kline[6]) / 1000)))
                    data_point.append(kline[4])
                    data_subset.append(data_point)
                closing_prices.append(subset)
        return closing_prices
    except BinanceAPIException as e:
        print(e.status_code)
        exit(0)
    except requests.exceptions.ReadTimeout as e:
        print("Timed out")
        exit(0)