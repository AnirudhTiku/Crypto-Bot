from binance.client import Client
from binance.enums import KLINE_INTERVAL_1DAY, KLINE_INTERVAL_1HOUR, KLINE_INTERVAL_1MINUTE, KLINE_INTERVAL_15MINUTE, KLINE_INTERVAL_30MINUTE 
from binance.enums import KLINE_INTERVAL_5MINUTE, KLINE_INTERVAL_2HOUR, KLINE_INTERVAL_4HOUR, KLINE_INTERVAL_3MINUTE, KLINE_INTERVAL_6HOUR
from binance.exceptions import BinanceAPIException
import source.config as config
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math
import statistics
import time
import requests

multiplier = {
    "1 DAYS": 1,
    "6 HOURS": 4,
    "4 HOURS": 6,
    "2 HOURS": 12,
    "1 HOURS": 24,
    "30 MINUTES": 48,
    "15 MINUTES": 96,
    "5 MINUTES": 288,
    "3 MINUTES": 480,
    "1 MINUTES" : 1440
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
def get_historical_klines(symbol='BTC', time_interval='1 MINUTES', start_day=None, end_day=None, subset_length=None):
    if (type(time_interval) != str):
        print("Please enter string for time_interval parameter")
        exit()
    time_interval = time_interval.strip()
    time_interval = time_interval.upper()
    if (time_interval[-1] != "S"):
        time_interval+= "S"

    days = datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S') - datetime.strptime(start_day, '%m/%d/%Y %H:%M:%S')
    days = days.days

    if (subset_length != None):
        if (days % subset_length != 0):
            print("Data cannot be partionned into even subsets of length " + str(subset_length))
            exit(0)

    client = Client(config.API_KEY, config.API_SECRET)
    print("\nChecking " + symbol + " prices...\n")

    try:
        closing_prices = []
        later_timestamp = datetime.strptime(end_day, '%m/%d/%Y %H:%M:%S')
        earlier_timestamp = None
        KLINES = []
        subset = []
        subset_entries = 0
        days_left = days
        if (time_interval == "1 DAYS"):
            while days_left > 1000:
                past_days = timedelta(1000)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES
                later_timestamp = earlier_timestamp
                days_left -= 1000
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "6 HOURS"):
            while days_left > 250:
                past_days = timedelta(500)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_6HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 250
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_6HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "4 HOURS"):
            while days_left > 167:
                past_days = timedelta(167)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_4HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 167
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_4HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "2 HOURS"):
            while days_left > 82:
                past_days = timedelta(82)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_2HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 82
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_2HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "1 HOURS"):
            while days_left > 41:
                past_days = timedelta(41)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 41
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "30 MINUTES"):
            while days_left > 20:
                past_days = timedelta(20)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_30MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 20
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_30MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "15 MINUTES"):
            while days_left > 10:
                past_days = timedelta(10)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 10
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES   
        elif (time_interval == "5 MINUTES"):
            while days_left > 4:
                past_days = timedelta(4)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_5MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 4
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_5MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "3 MINUTES"):
            while days_left > 3:
                past_days = timedelta(3)
                earlier_timestamp = (later_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_3MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                later_timestamp = earlier_timestamp
                days_left -= 3
                time.sleep(0.25)
            earlier_timestamp = datetime.strptime(start_day, '%b %d %Y %H:%M:%S')
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_3MINUTE, str(earlier_timestamp.timestamp()), str(later_timestamp.timestamp()))
            KLINES = current_klines + KLINES     
        elif (time_interval == "1 MINUTES"):
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
                time.sleep(0.25)
        else: 
            print("Please enter valid time_interval")
            exit(0)
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
        print("Retrieved " + symbol + " prices\n")
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
def get_recent_klines(symbol='BTC', time_interval='1 MINUTES', days=1, subset_length=None):
    if (type(time_interval) != str):
        print("Please enter string for time_interval parameter")
        exit()
    time_interval = time_interval.strip()
    time_interval = time_interval.upper()
    if (time_interval[-1] != "S"):
        time_interval+= "S"
        
    if (subset_length != None):
        if (days % subset_length != 0):
            print("Data cannot be partionned into even subsets of length " + str(subset_length))
            exit(0)

    client = Client(config.API_KEY, config.API_SECRET)
    print("\nChecking " + symbol + " prices...\n")

    try:
        closing_prices = []
        current_timestamp = datetime.now()
        previous_timestamp = datetime.now()
        KLINES = []
        subset = []
        subset_entries = 0
        days_left = days
        if (time_interval == "1 DAYS"):
            while days_left > 1000:
                past_days = timedelta(1000)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES
                current_timestamp = previous_timestamp
                days_left -= 1000
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1DAY, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "6 HOURS"):
            while days_left > 250:
                past_days = timedelta(250)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_6HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 250
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_6HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "4 HOURS"):
            while days_left > 166:
                past_days = timedelta(166)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_4HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 166
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_4HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "2 HOURS"):
            while days_left > 82:
                past_days = timedelta(82)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_2HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 82
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_2HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "1 HOURS"):
            while days_left > 41:
                past_days = timedelta(41)
                previous_timestamp = (current_timestamp - past_days)
                current_timestamp = current_timestamp
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 41
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_1HOUR, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES      
        elif (time_interval == "30 MINUTES"):
            while days_left > 20:
                past_days = timedelta(20)
                previous_timestamp = (current_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_30MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 20
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_30MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "15 MINUTES"):
            while days_left > 10:
                past_days = timedelta(10)
                previous_timestamp = (current_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 10
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "15 MINUTES"):
            while days_left > 10:
                past_days = timedelta(10)
                previous_timestamp = (current_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 10
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_15MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES 
        elif (time_interval == "5 MINUTES"):
            while days_left > 4:
                past_days = timedelta(4)
                previous_timestamp = (current_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_5MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 4
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_5MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES
        elif (time_interval == "3 MINUTES"):
            while days_left > 3:
                past_days = timedelta(3)
                previous_timestamp = (current_timestamp - past_days)
                current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_3MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
                KLINES = current_klines + KLINES                
                current_timestamp = previous_timestamp
                days_left -= 3
                time.sleep(0.25)
            past_days = timedelta(days_left)
            previous_timestamp = (current_timestamp - past_days)
            current_timestamp = current_timestamp
            current_klines = client.get_historical_klines(symbol + "BUSD", KLINE_INTERVAL_3MINUTE, str(previous_timestamp.timestamp()), str(current_timestamp.timestamp()))
            KLINES = current_klines + KLINES       
        elif (time_interval == "1 MINUTES"):
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
                time.sleep(0.25)
        else:
            print("Please interval valid time_interval")
            exit(0)
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
        print("Retrieved " + symbol + " prices\n")
        return closing_prices
    except BinanceAPIException as e:
        print(e.status_code)
        exit(0)
    except requests.exceptions.ReadTimeout as e:
        print("Timed out")
        exit(0)
