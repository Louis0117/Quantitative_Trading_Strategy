#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 21:30:45 2023

@author: welcome870117
"""

from binance_api_v3 import Binance_transaction
from utils import hist_crypto_price, current_crypto_price
import pandas as pd
from datetime import datetime
from datetime import timedelta
import pytz


# parameters
SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
#BINANCE_KEY = 'CtXnM8qTP6YejcpbbMLMplQyKgAjuxWHkSHBMPQA5jxwzDZNQ8n9N8ewlNAdPg5P'
#BINANCE_SECRET = 'FN7Xa1BhgIJWhfnSHWOznhQQPIAJ08IcoZHOw2wFg40PJNAbhNYyqSwUkrVHCvWg'
BINANCE_KEY = 'd6WYUJFQgaZEvHAP7vkveJqdvgI7F6Hj0PFLUnWcVdPtOpJdFz3DOfgaw0ekGUjt'
BINANCE_SECRET = 'trVJQjpNSE610xqEsfgYAmt4YmswzWBiUgshgYVa9KaHriOQTH4Y1BSy78Jaf4mk'
SYMBOL = 'AXSUSDT'
TIME_ZONE = pytz.timezone("utc")
LOG_FILE_DIR = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v3/turtle_strategy_log_file.csv'

'''
# client object
binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)
binance_transaction.future_perpetual_buy(SYMBOL, 'AXS', 'USDT', 20, order_price = None)
binance_transaction.future_perpetual_sell(SYMBOL, 'USDT', 'AXS', 40, order_price = None)
binance_transaction.future_perpetual_close_position(symbol='AXSUSDT')
'''

# calculate TR
def TR_value(df):
    TR_value_list = [0]
    for i in range(1,len(df)):
        TR_value_list.append(max(df['high'][i]-df['low'][i], df['close'][i-1]-df['low'][i], df['high'][i]-df['close'][i-1]))
    df['TR_value'] = TR_value_list
    return df

# calculate ATR
def ATR_value(df, lookback_day):
    # rolling window
    ATR_value_list = [0 for _ in range(lookback_day)]
    for i in range(lookback_day, len(df)):
        ATR_value_list.append(sum(df['TR_value'][i-lookback_day:i])/lookback_day)
    df['ATR_value'] = ATR_value_list
    return df 

def turtle_strategy_20day_high_low(df, lookback_day):
    long_entry_price = [0 for _ in range(lookback_day)]
    short_entry_price = [0 for _ in range(lookback_day)]
    for i in range(lookback_day, len(df)):
        long_entry_price.append(max(df['high'][i-lookback_day:i]))
        short_entry_price.append(min(df['low'][i-lookback_day:i]))
    df['20day_high'] = long_entry_price
    df['20day_low'] = short_entry_price
    return df

def turtle_strategy_10day_high_low(df, lookback_day):
    short_exit_price = [0 for _ in range(lookback_day)]
    long_exit_price = [0 for _ in range(lookback_day)]
    for i in range(lookback_day, len(df)):
        short_exit_price.append(max(df['high'][i-lookback_day:i]))
        long_exit_price.append(min(df['low'][i-lookback_day:i]))
    df['10day_high'] = short_exit_price
    df['10day_low'] = long_exit_price
    return df

# calculate unit

# check USDT avaliable balance
def _available_USDT(client):
    account_info = client.check_future_account()
    usdt_available_balance = round(float(account_info['assets'][8]['availableBalance']), 2)
    return usdt_available_balance
    
# check USDT wallet balance
def _wallet_USDT(client):
    account_info = client.check_future_account()
    usdt_wallet_balance = round(float(account_info['assets'][8]['walletBalance']), 2)
    return usdt_wallet_balance

def _calculate_order_size(history_data, account_value):
    N = history_data['ATR_value'].iloc[-1]
    order_size = account_value*0.01/N
    return round(order_size, 2)

# strategy 
def turtle_strategy(client, symbol, log_file, history_data, current_price):
    position_units = 0
    side = 0
    stop_loss = 0
    add_position = 0
    # read log file
    for i in range(len(log_file)):
        if log_file['symbol'][i] == symbol:
            position_units+=1
            side = log_file['side'][i]
            stop_loss = log_file['stop_loss_price'][i]
            add_position = log_file['add_position_price'][i]
            
    if position_units == 0:
        if current_price > history_data['20day_high'].iloc[-1]:
            # check account USDT balance 
            wallet_USDT = _wallet_USDT(client)
            # calculate order size
            order_size = _calculate_order_size(history_data, wallet_USDT)
            # check account avaliable USDT
            available_USDT = _available_USDT(client)
            # discreminate USDT is enough or not
            if order_size>available_USDT:
                print('USDT is not enough')
                return False
            else:
                # create long position ....
                quantity = client.future_perpetual_buy(SYMBOL, SYMBOL[:-4], 'USDT', order_size, order_price = None)
                if quantity == False:
                    return False
                else:
                    # update log file
                    utc_time = datetime.now(TIME_ZONE)
                    N = history_data['ATR_value'].iloc[-1]
                    stop_loss = current_price-2*N
                    add_position = current_price+0.5*N
                    transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'BUY', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                    log_file = log_file.append(transaction_record, ignore_index=True)
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    
        elif current_price < history_data['20day_low'].iloc[-1]:
            # check account USDT balance 
            wallet_USDT = _wallet_USDT(client)
            # calculate order size
            order_size = _calculate_order_size(history_data, wallet_USDT)
            # check account avaliable USDT
            available_USDT = _available_USDT(client)
            # discreminate USDT is enough or not
            if order_size>available_USDT:
                print('USDT is not enough')
                return False
            else:
                # create short position ....
                quantity = client.future_perpetual_sell(SYMBOL, SYMBOL[:-4], 'USDT', order_size, order_price = None)
                if quantity == False:
                    return False
                else:
                    # update log file
                    utc_time = datetime.now(TIME_ZONE)
                    N = history_data['ATR_value'].iloc[-1]
                    stop_loss = current_price+2*N
                    add_position = current_price-0.5*N
                    transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'SELL', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                    log_file = log_file.append(transaction_record, ignore_index=True)
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                
    else:
        if side == 'BUY':
            # add position 
            if current_price > add_position and position_units<4:
                # check account USDT balance 
                wallet_USDT = _wallet_USDT(client)
                # calculate order size
                order_size = _calculate_order_size(history_data, wallet_USDT)
                # check account avaliable USDT
                available_USDT = _available_USDT(client)
                # discreminate USDT is enough or not
                if order_size>available_USDT:
                    print('USDT is not enough')
                    return False
                else:
                    # create long position ....
                    quantity = client.future_perpetual_buy(SYMBOL, SYMBOL[:-4], 'USDT', order_size, order_price = None)
                    if quantity == False:
                        return False
                    else:
                        # update log file
                        utc_time = datetime.now(TIME_ZONE)
                        N = history_data['ATR_value'].iloc[-1]
                        stop_loss = current_price-2*N
                        add_position = current_price+0.5*N
                        transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'BUY', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                        log_file = log_file.append(transaction_record, ignore_index=True)
                        # save file
                        log_file.to_csv(LOG_FILE_DIR, index=False)
                    
            elif current_price < stop_loss:
                # close position                
                quantity = client.future_perpetual_close_position(symbol=symbol)
                if quantity == False:
                    return False
                else:
                    # update log file
                    for i in range(len(log_file)):
                        if log_file['symbol'][i] == symbol:
                            log_file.drop(i, axis=0, inplace=True)
                    log_file.reset_index(inplace=True, drop=True) 
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    
            elif current_price < history_data['10day_low'].iloc[-1]:
                # close position
                quantity = client.future_perpetual_close_position(symbol=symbol)
                if quantity == False:
                    return False
                else:
                    # update log file
                    for i in range(len(log_file)):
                        if log_file['symbol'][i] == symbol:
                            log_file.drop(i, axis=0, inplace=True)
                    log_file.reset_index(inplace=True, drop=True) 
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    
        else:
            # add position 
            if current_price < add_position and position_units<4:
                    # check account USDT balance 
                    wallet_USDT = _wallet_USDT(client)
                    # calculate order size
                    order_size = _calculate_order_size(history_data, wallet_USDT)
                    # check account avaliable USDT
                    available_USDT = _available_USDT(client)
                    # discreminate USDT is enough or not
                    if order_size>available_USDT:
                        print('USDT is not enough')
                        return False
                    else:
                        # create short position ....
                        quantity = client.future_perpetual_sell(SYMBOL, SYMBOL[:-4], 'USDT', order_size, order_price = None)
                        if quantity == False:
                            return False
                        else:
                            # update log file 
                            utc_time = datetime.now(TIME_ZONE)
                            N = history_data['ATR_value'].iloc[-1]
                            stop_loss = current_price+2*N
                            add_position = current_price-0.5*N
                            transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'SELL', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                            log_file = log_file.append(transaction_record, ignore_index=True)
                            # save file
                            log_file.to_csv(LOG_FILE_DIR, index=False)
                        
            elif current_price > stop_loss:
                # close position 
                quantity = client.future_perpetual_close_position(symbol=symbol)
                # update log file
                if quantity == False:
                    return False
                else:
                    # update log file
                    for i in range(len(log_file)):
                        if log_file['symbol'][i] == symbol:
                            log_file.drop(i, axis=0, inplace=True)
                    log_file.reset_index(inplace=True, drop=True) 
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    
            elif current_price > history_data['10day_high'].iloc[-1]:
                # close position 
                quantity = client.future_perpetual_close_position(symbol=symbol)
                # update log file
                if quantity == False:
                    return False
                else:
                    # update log file
                    for i in range(len(log_file)):
                        if log_file['symbol'][i] == symbol:
                            log_file.drop(i, axis=0, inplace=True)
                    log_file.reset_index(inplace=True, drop=True) 
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)

if __name__ == '__main__':
    # client object
    binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)
    
    while True:
        # get current time -> type: datetime
        #utc_time = datetime.now(TIME_ZONE)
        #data_update_date = utc_time.strftime("%Y-%m-%d")
        #current_date = utc_time.strftime("%Y-%m-%d")
        log_file = pd.DataFrame(columns=['timestamp', 'symbol', 'side', 'quantity', 'add_position_price', 'stop_loss_price'])
        
        # get history price
        hist_price = hist_crypto_price(SYMBOL, '1d')
        
        # caculate indicator
        hist_price = TR_value(hist_price)
        hist_price = ATR_value(hist_price, 20)
        hist_price = turtle_strategy_20day_high_low(hist_price, 20)
        hist_price = turtle_strategy_10day_high_low(hist_price, lookback_day=10)
        current_price = current_crypto_price(SYMBOL)
        # while same day
        # strategy 
        turtle_strategy(binance_transaction, SYMBOL, log_file, hist_price, current_price)
        # current price
        
        # decision 2
#%%
        # test block 
        #print(binance_transaction.check_future_account()['USDT'])
        account_info = binance_transaction.check_future_account()
        usdt_balance = round(float(account_info['assets'][8]['availableBalance']), 2)#['USDT'])#['availableBalance'])
        print("availableUSDT:", usdt_balance)
        print(round(float(account_info['assets'][8]['walletBalance']), 2))
        print(_available_USDT(binance_transaction))
        print(_wallet_USDT(binance_transaction))
        print(_calculate_order_size(hist_price, 1500))
        print(SYMBOL[:-4])
        utc_time = datetime.now(TIME_ZONE)
        print(utc_time)
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        row = {'timestamp':utc_time, 'symbol':SYMBOL, 'side':'BUY', 'quantity':10, 'add_position_price':100, 'stop_loss_price':100}
        log_file = log_file.append(row, ignore_index=True)
        q = binance_transaction.future_perpetual_buy(SYMBOL, 'AXS', 'USDT', 1, order_price = None)
        if q != False:
            print('t')
        else:
            print('q')

        test_drop = log_file.drop(1, axis=0, inplace=True)
        log_file.reset_index(drop=True, inplace=True)
        log_file.to_csv(LOG_FILE_DIR, index=False)
        read_csv = pd.read_csv(LOG_FILE_DIR, index_col=False)
