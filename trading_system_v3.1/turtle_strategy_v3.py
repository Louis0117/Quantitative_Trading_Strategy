#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 13:53:07 2023

@author: welcome870117
"""

# import python file
from binance_api_v3 import Binance_transaction
from utils import hist_crypto_price, current_crypto_price
# import package
import pandas as pd
import argparse
import os
import time
from datetime import datetime
from datetime import timedelta
import pytz

# parameters
SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
BINANCE_KEY = ''
BINANCE_SECRET = ''
LOG_FILE_DIR = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v3/turtle_strategy_log_file.csv'
TIME_ZONE = pytz.timezone("utc")

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', type=str, help ='Symbol')
args = parser.parse_args()
SYMBOL = args.symbol



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

def _calculate_order_units(history_data, account_value):
    N = history_data['ATR_value'].iloc[-1]
    units = account_value*0.01/N
    return round(units, 2)

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
    
    print('date:', history_data['timestamp'].iloc[-1])
    print('position units:', position_units)
    print('side:', side)
    print('stop loss:', stop_loss)  
    print('add position:', add_position)    
    print('current price:', current_price)
    print('20day high:', history_data['20day_high'].iloc[-1])
    print('20day low:', history_data['20day_low'].iloc[-1])
    print('10day high:', history_data['10day_high'].iloc[-1])
    print('10day low:', history_data['10day_low'].iloc[-1])
    
    
    if position_units == 0:
        if current_price > history_data['20day_high'].iloc[-1]: 
            # check account USDT balance 
            wallet_USDT = _wallet_USDT(client)
            # calculate order size
            units = _calculate_order_units(history_data, wallet_USDT)
            # check account avaliable USDT
            available_USDT = _available_USDT(client)
            print('create long position.....')
            print('check available USDT balance.....')
            print('available USDT:', available_USDT)
            print('USDT requirement:', units*current_price)
            # discreminate USDT is enough or not
            if units*current_price>available_USDT:
                print('USDT is not enough')
                return False
            else:
                # create long position ....
                quantity = client.future_perpetual_buy(SYMBOL, SYMBOL[:-4], 'USDT', order_size=0, order_price = None, quantity=units)####
                if quantity == False:
                    return False
                else:
                    # update log file
                    #utc_time = datetime.now(TIME_ZONE)
                    utc_time = history_data['timestamp'].iloc[-1]
                    N = history_data['ATR_value'].iloc[-1]
                    stop_loss = current_price-2*N
                    add_position = current_price+0.5*N
                    transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'BUY', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                    log_file = log_file.append(transaction_record, ignore_index=True)
                    #test_log_file = test_log_file.append(transaction_record, ignore_index=True)
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    #test_log_file.to_csv(TEST_LILE_DIR, index=False)
                    #print('quantity:', quantity)
                    
        elif current_price < history_data['20day_low'].iloc[-1]:
            # check account USDT balance 
            wallet_USDT = _wallet_USDT(client)
            # calculate order size
            units = _calculate_order_units(history_data, wallet_USDT)
            # check account avaliable USDT
            available_USDT = _available_USDT(client)
            print('create long position.....')
            print('check available USDT balance.....')
            print('available USDT:', available_USDT)
            print('USDT requirement:', units*current_price)
            # discreminate USDT is enough or not
            if units*current_price>available_USDT:
                print('USDT is not enough')
                return False
            else:
                # create short position ....
                quantity = client.future_perpetual_sell(SYMBOL, SYMBOL[:-4], 'USDT', order_size=0, order_price = None, quantity=units)
                if quantity == False:
                    return False
                else:
                    # update log file
                    #utc_time = datetime.now(TIME_ZONE)
                    utc_time = history_data['timestamp'].iloc[-1]
                    N = history_data['ATR_value'].iloc[-1]
                    stop_loss = current_price+2*N
                    add_position = current_price-0.5*N
                    transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'SELL', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                    log_file = log_file.append(transaction_record, ignore_index=True)
                    #test_log_file = test_log_file.append(transaction_record, ignore_index=True)
                    # save file
                    log_file.to_csv(LOG_FILE_DIR, index=False)
                    #test_log_file.to_csv(TEST_LILE_DIR, index=False)
                    #print('quantity:', quantity)
    else:
        if side == 'BUY':
            # add position 
            if current_price > add_position and position_units<4:
                # check account USDT balance 
                wallet_USDT = _wallet_USDT(client)
                # calculate order size
                units = _calculate_order_units(history_data, wallet_USDT)
                # check account avaliable USDT
                available_USDT = _available_USDT(client)
                print('create long position.....')
                print('check available USDT balance.....')
                print('available USDT:', available_USDT)
                print('USDT requirement:', units*current_price)
                # discreminate USDT is enough or not
                if units*current_price>available_USDT:
                    print('USDT is not enough')
                    return False
                else:
                    # create long position ....
                    quantity = client.future_perpetual_buy(SYMBOL, SYMBOL[:-4], 'USDT', order_size=0, order_price = None, quantity=units)
                    if quantity == False:
                        return False
                    else:
                        # update log file
                        #utc_time = datetime.now(TIME_ZONE)
                        utc_time = history_data['timestamp'].iloc[-1]
                        N = history_data['ATR_value'].iloc[-1]
                        stop_loss = current_price-2*N
                        add_position = current_price+0.5*N
                        transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'BUY', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                        log_file = log_file.append(transaction_record, ignore_index=True)
                        #test_log_file = test_log_file.append(transaction_record, ignore_index=True)
                        # save file
                        log_file.to_csv(LOG_FILE_DIR, index=False)
                        #test_log_file.to_csv(TEST_LILE_DIR, index=False)
                        #print('quantity:', quantity)
                        
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
                    #print('quantity:', quantity)
                    
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
                    #print('quantity:', quantity)
        else:
            # add position 
            if current_price < add_position and position_units<4:
                    # check account USDT balance 
                    wallet_USDT = _wallet_USDT(client)
                    # calculate order size
                    units = _calculate_order_units(history_data, wallet_USDT)
                    # check account avaliable USDT
                    available_USDT = _available_USDT(client)
                    print('create long position.....')
                    print('check available USDT balance.....')
                    print('available USDT:', available_USDT)
                    print('USDT requirement:', units*current_price)
                    # discreminate USDT is enough or not
                    if units*current_price>available_USDT:
                        print('USDT is not enough')
                        return False
                    else:
                        # create short position ....
                        quantity = client.future_perpetual_sell(SYMBOL, SYMBOL[:-4], 'USDT', order_size=0, order_price = None, quantity=units)
                        if quantity == False:
                            return False
                        else:
                            # update log file 
                            #utc_time = datetime.now(TIME_ZONE)
                            utc_time = history_data['timestamp'].iloc[-1]
                            N = history_data['ATR_value'].iloc[-1]
                            stop_loss = current_price+2*N
                            add_position = current_price-0.5*N
                            transaction_record = {'timestamp':utc_time, 'symbol':symbol, 'side':'SELL', 'quantity':quantity, 'add_position_price':add_position, 'stop_loss_price':stop_loss}
                            log_file = log_file.append(transaction_record, ignore_index=True)
                            #test_log_file = test_log_file.append(transaction_record, ignore_index=True)
                            # save file
                            log_file.to_csv(LOG_FILE_DIR, index=False)
                            #test_log_file.to_csv(TEST_LILE_DIR, index=False)
                            #print('quantity:', quantity)
                            
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
                    #print('quantity:', quantity)
                    
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
                    #print('quantity:', quantity)
    #print('-----------------------------------')
                    
if __name__ == '__main__':
        # client object
        binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS) 
        
        while 1:
           # get hist price data
           hist_price = hist_crypto_price(SYMBOL, '1d')
           # calculate indicator
           hist_data = turtle_strategy_10day_high_low(turtle_strategy_20day_high_low(ATR_value(TR_value(hist_price), 10), 20), lookback_day=10)
           
           if not os.path.exists(LOG_FILE_DIR):
               log_file = pd.DataFrame(columns=['timestamp', 'symbol', 'side', 'quantity', 'add_position_price', 'stop_loss_price'])
               log_file.to_csv(LOG_FILE_DIR, index=False)
           update_date = str(datetime.now(TIME_ZONE))[:10]
           current_date = str(datetime.now(TIME_ZONE))[:10]
           # determine to UTC tomorrow
           while current_date == update_date:
               current_price = current_crypto_price(SYMBOL)
               # print
               print('current time:', str(datetime.now(TIME_ZONE))[:19])
               print('check trading signal .....')
               # read  file
               log_file = pd.read_csv(LOG_FILE_DIR, index_col = False)
               # strategy 
               turtle_strategy(binance_transaction, SYMBOL, log_file, hist_data, current_price)
               # sleep 30s
               print('sleep 30s ...')
               time.sleep(30)
               # update current date
               current_date = str(datetime.now(TIME_ZONE))[:10]
               print('========================================')