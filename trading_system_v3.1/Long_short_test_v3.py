#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri May 19 01:47:04 2023

@author: welcome870117
"""

import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import json
from utils import current_crypto_price, hist_crypto_price
from binance_api_v3 import Binance_transaction
import sys
import time
from datetime import datetime
import os

# parameters
SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
BINANCE_KEY = 'd6WYUJFQgaZEvHAP7vkveJqdvgI7F6Hj0PFLUnWcVdPtOpJdFz3DOfgaw0ekGUjt'
BINANCE_SECRET = 'trVJQjpNSE610xqEsfgYAmt4YmswzWBiUgshgYVa9KaHriOQTH4Y1BSy78Jaf4mk'
#BINANCE_KEY = ''
#BINANCE_SECRET = ''

if len(sys.argv)!=7:
    print('input error')
  
POSITION_SIZE = int(sys.argv[1])
LEVERAGE = int(sys.argv[2])
J_VALUE = int(sys.argv[3]) # lookback month
K_VALUE = int(sys.argv[4]) # hold month
day = int(sys.argv[5]) 
MODE = str(sys.argv[6])

log_file_dir = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v3/long_short_strategy_test_log.csv'

#POSITION_SIZE = 10
#J_VALUE = 90 # lookback month
#K_VALUE = 90 # hold month
#LEVERAGE = 3

def check_account_usdt_balance(client, position_size, leverage):
    account_info = client.check_future_account()
    usdt_balance = round(float(account_info['assets'][8]['availableBalance']), 2)#['USDT'])#['availableBalance'])
    print("availableUSDT:", usdt_balance)
    requirement_of_usdt = 21*position_size/leverage
    print("requirement of USDT", requirement_of_usdt)
    if requirement_of_usdt> usdt_balance:
        print("account doesn't have enough USDT")
        return False
    return True

def _get_top100_crypto(url):
    #url = 'https://coinmarketcap.com'
    response = rq.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data= soup.find('script',id="__NEXT_DATA__",type="application/json")
    dataset = []
    coins = []
    coin_data=json.loads(data.contents[0])
    listings=json.loads(coin_data["props"]["initialState"])["cryptocurrency"]['listingLatest']['data']
    for i in listings[1:]: 
        coins.append(i[-4])
    return coins


def _get_top100_crypto_hist_price(coin_list):
    top_100_hist_price = {}
    for coin in coin_list:
        coin = coin+'USDT'
        hist_price = hist_crypto_price(coin, '1d')
        hist_price['timestamp'] = pd.to_datetime(hist_price['timestamp'])
        top_100_hist_price.update({coin:hist_price})
    return top_100_hist_price


def _split_hist_price(price_dict, window_size):
    dataset = {}
    
    for crypto, price  in price_dict.items():
        if len(price)>window_size:
            dataset.update({crypto:price.iloc[-window_size:].reset_index(drop=True)})
    return dataset


def calculate_daily_return(df):
    df['daily_return'] = df['close'].pct_change()


def calculate_std(df):
    std_value = df['daily_return'].std()
    return std_value


def build_long_position(client, price_list, date, pct):
    '''

    Parameters
    ----------
    client : TYPE
        Binance client.
        
    price_list : list
        DESCRIPTION.
        
    pct : float
        DESCRIPTION.

    Returns
    -------
    long_position : list 
        The long-position established in Binance.

    '''
    #number_of_target = int(len(price_list)*pct)
    number_of_target = 10
    count = 0
    long_position = []
    
    # traverse price_list
    for data in price_list:
        if count == number_of_target:
            break
        # not add USD in profolio
        if data[0][:-4]=='USDC':
            continue
        # create long future order
        try:
            print('----- long position -----')
            print('symbol:', data[0])
            #client.future_perpetual_buy(self, symbol, coin_buy, coin_sell, order_size, order_price = None, quantity = None)
            quantity = client.future_perpetual_buy(data[0], data[0][:-4],'USDT', POSITION_SIZE)   
            #  different crypto have different quantitive precision, sometime need to adjust  
            if quantity != False:
                count+=1
                long_position.append(data[0])
                #####
                update_trade_log(data[0], date, 'BUY', quantity)
        except Exception as e:
                print("error", str(e))
        print('----------')
    return long_position
                           

def build_short_position(client, price_list, date, pct):
    #number_of_target = int(len(price_list)*pct)
    number_of_target = 10
    count = 0
    short_position = []
    
    for i in range(len(price_list)-1, 0, -1):
        if count == number_of_target:
            break
        
        try:
            print('----- short position -----')
            print('symbol:', price_list[i][0])
            quantity = client.future_perpetual_sell(price_list[i][0],'USDT', price_list[i][0][:-4],POSITION_SIZE)
            #client.binance_future_adjust_leverage(price_list[i][0], leverage)
            if quantity != None:
                    count+=1
                    short_position.append(price_list[i][0])
                    update_trade_log(price_list[i][0], date, 'SELL', quantity)
                    print('----------')
        except Exception as e:
                print("error", str(e))
                
    return short_position


def close_all_position(client, long_positions, short_positions):
    for long_position, short_position in zip(long_positions, short_positions):
        client.future_perpetual_close_position(long_position)
        client.future_perpetual_close_position(short_position)


def _adject_leverage(client, price_list, leverage):
    print('----- adject leverage -----')
    for data in price_list:
        try:
            client.binance_future_adjust_leverage(data[0], leverage)
        except:
             pass


def update_trade_log(symbol, date, side, quantity):
    df = pd.read_csv(log_file_dir, index_col = False)
    new_row = {'timestamp': date,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(log_file_dir, index = False)


#判斷是否達到關倉條件    
def close_position_conditional_judgment(client, current_time, csv_dir):
    print('Determining whether to close position.....')
    log_file = pd.read_csv(csv_dir, index_col=False)
    for i in range(len(log_file)):
        
        k_value = pd.Timedelta(weeks=0,days=log_file['K_value'][i],hours=0,minutes=0,seconds=0)
        timestamp = pd.to_datetime(log_file['timestamp'][i])
        # 判斷否超過持倉時間
        if timestamp + k_value < current_time:
            # 平倉
            '''
            res = client.future_perpetual_partial_close_position(log_file['symbol'][i], log_file['quantity'][i])
            if res != False:
                # remove log
                print('close successfully!!')
                log_file.drop(i, inplace=True)
            else:
                print('error in close_position_conditional_judgment')
            '''
            if log_file['side'][i] == 'BUY':
                res = client.future_perpetual_sell(log_file['symbol'][i], 'USDT', log_file['symbol'][i][:-4],0, quantity = log_file['quantity'][i])
                if res != False:
                    # remove log
                    print('close successfully!!')
                    log_file.drop(i, inplace=True)
            elif log_file['side'][i] == 'SELL':
                res = client.future_perpetual_buy(log_file['symbol'][i],  log_file['symbol'][i][:-4], 'USDT', 0, quantity = log_file['quantity'][i])
                if res != False:
                    # remove log
                    print('close successfully!!')
                    log_file.drop(i, inplace=True)
    # reset index
    log_file.reset_index(inplace=True, drop=True)
    # save csv
    log_file.to_csv(csv_dir, index=False)   
    
    
# 判斷是否開倉
def open_position_conditional_judgment(client, current_time, csv_dir):
    print('Determining whether to establish an investment portfolio.....')
    log_file = pd.read_csv(log_file_dir, index_col=False)
    # 判斷log file have data
    if len(log_file)>0:
        # 判斷最新交易是否隔一個月
        # check last trade log 
        last_trade = pd.to_datetime(log_file['timestamp'].iloc[-1])
        one_month = pd.Timedelta(weeks=0, days=30,hours=0,minutes=0,seconds=0)
        if  last_trade + one_month < current_time:
            # open position signal 
            return True
        else:
            return False
    else:
        return True


def long_short_strategy(client, date):
    # strategy
    ###########################################################################################
    coins = _get_top100_crypto('https://coinmarketcap.com')   
    top_100_hist_price = _get_top100_crypto_hist_price(coins)
    dataset = _split_hist_price(top_100_hist_price, window_size=J_VALUE)
    # calculate daily return -> SD -> sort(ascending)
    for price_data in dataset.values():
        calculate_daily_return(price_data)
    # calculate SD
    crypto_std = {}
    for crypto, price_data in dataset.items():
        crypto_std.update({crypto:calculate_std(price_data.iloc[1:].reset_index(drop=True))})
    sorted_dict = sorted(crypto_std.items(), key=lambda x: (x[1], x[0]))    
    # build profolio
    # create order
    _adject_leverage(binance_transaction, sorted_dict, LEVERAGE)
    long_positions = build_long_position(binance_transaction, sorted_dict, date, 0.2)
    short_positions = build_short_position(binance_transaction, sorted_dict, date, 0.2)
    ##########################################################################################
    return long_positions, short_positions


def test_data(day):
    test_dataset = []
    # current time 
    current_time = pd.to_datetime(datetime.now())
    #day = pd.Timedelta(weeks=0, days=1,hours=0,minutes=0,seconds=0)
    # create datset
    for i in range(day):
        shift_day = pd.Timedelta(weeks=0, days=i,hours=0,minutes=0,seconds=0)
        test_dataset.append(current_time+shift_day)
    return test_dataset

'''
def add_trade_log(client, current_time, df, csv_dir, long_position, short_position):
    #trade_info = binance_transaction.check_future_trade_history()
    #time_str = pd.to_datetime(datetime.fromtimestamp(trade_info[0]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
    #shift_time = pd.Timedelta(weeks=0,days=0,hours=0,minutes=5,seconds=0)
    #stander_time = current_time-shift_time
    print('----- trade log -----')
    for symbol in long_position:
        quantity = 0
        
        # get trade history record
        trade_info = client.check_future_trade_history(symbol)
        # get position info
        position_info = binance_transaction.future_check_position(symbol)
        # current symbol position 
        symbol_current_position = float(position_info[0]['positionAmt'])
        
        for i in range(len(df)):
            if df['symbol'][i] == symbol:
                quantity+= df['quantity'][i]
                
        quantity = symbol_current_position-quantity      
        
        print('symbol:', symbol) 
        print('side:', trade_info[-1]['side'])
        print('time:', current_time)
        print('quantity:', quantity)
        print('--------')
        
        timestamp = current_time
        side = trade_info[-1]['side']
        new_row = {'timestamp': timestamp,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
        df = df.append(new_row, ignore_index=True)
        
    for symbol in short_position:
        quantity = 0
        trade_info = client.check_future_trade_history(symbol)
        position_info = binance_transaction.future_check_position(symbol)       
        symbol_current_position = float(position_info[0]['positionAmt'])
        for i in range(len(df)):
            if df['symbol'][i] == symbol:
                quantity+= df['quantity'][i]
        quantity = symbol_current_position-quantity      
        
        print('symbol:', symbol) 
        print('side:', trade_info[-1]['side'])
        print('time:', current_time)
        print('quantity:', quantity)
        print('--------')
        
        side = trade_info[-1]['side']
        new_row = {'timestamp': current_time,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
        df = df.append(new_row, ignore_index=True)
    df.to_csv(csv_dir, index=False)
'''



if __name__ == '__main__':
    
    # create dataset
    test_dataset = test_data(day)
    # for loop dataset
    if MODE == 'normal':
        for date in test_dataset:
            # client object
            binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)
            # 检查文件是否存在
            if os.path.exists(log_file_dir):
                print(f"CSV file {log_file_dir} exist")
                log_file = pd.read_csv(log_file_dir, index_col=False)
                # 判斷是否平倉
                close_position_conditional_judgment(binance_transaction, date, log_file_dir)
                # 判斷是否開倉
                create_profolio = open_position_conditional_judgment(binance_transaction, date, log_file_dir)
                if create_profolio == True:
                    sufficient_account_balance = check_account_usdt_balance(binance_transaction, POSITION_SIZE, LEVERAGE)
                    if sufficient_account_balance:  
                        # 建立profolio
                        long_position, short_position = long_short_strategy(binance_transaction, date) 
                        # 等待訂單建立
                        print('---- wait for create order ------')
                        time.sleep(20)
                        # add trade log
                        #add_trade_log(binance_transaction, date, log_file, log_file_dir, long_position, short_position)
        
            else:
                # 不存在新增log file
                print(f"CSV flie {log_file_dir} not exist")
                log_file = pd.DataFrame(columns=['timestamp', 'symbol', 'side', 'quantity', 'K_value'])
                log_file.to_csv(log_file_dir, index=False)
                print("create csv file")
                # 檢查餘額
                sufficient_account_balance = check_account_usdt_balance(binance_transaction, POSITION_SIZE, LEVERAGE)
                if sufficient_account_balance:  
                    # 建立profolio
                    long_position, short_position =  long_short_strategy(binance_transaction, date) 
                    # 等待訂單建立
                    print('---- wait for create order ------')
                    #time.sleep(60)
                    # add trade log
                    #add_trade_log(binance_transaction, date, log_file, log_file_dir, long_position, short_position)
            
            # sleep one day
            print('---- sleep one day ------')
            #time.sleep(86200)
            
    elif MODE == 'close':
        for date in test_dataset:
            # client object
            binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)
            # 检查文件是否存在
            if os.path.exists(log_file_dir):
                print(f"CSV file {log_file_dir} exist")
                log_file = pd.read_csv(log_file_dir, index_col=False)
                # 判斷是否平倉
                close_position_conditional_judgment(binance_transaction, date, log_file_dir)
                # sleep.....
            else:
                print(f"CSV file {log_file_dir} not exist")
        