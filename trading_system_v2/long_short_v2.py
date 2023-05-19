#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 19 01:47:04 2023

@author: welcome870117
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  7 02:26:30 2023

@author: welcome870117
""" 

import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import json
from price_data import current_crypto_price, hist_crypto_price
from binance_api_v2 import Binance_transaction
import sys
import time
from datetime import datetime
import os

# parameters
SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
BINANCE_KEY = 'vAj3USjwe4s1wZ9vR6fFW0xVzkujzsEqq8xWn7poUudVsbCejTYvIX220qcq0rh9'
BINANCE_SECRET = 'JIrDWhMoPmSTprOiiDgtwzED6JukUcLTkjlMf5aACRhiM6yiPLjf7ydpQlgLBWZ4'

if len(sys.argv)!=5:
    print('input error')
'''   
POSITION_SIZE = int(sys.argv[1])
LEVERAGE = int(sys.argv[2])
J_VALUE = int(sys.argv[3]) # lookback month
K_VALUE = int(sys.argv[4]) # hold month
'''

POSITION_SIZE = 10
J_VALUE = 90 # lookback month
K_VALUE = 90 # hold month
LEVERAGE = 3
log_file_dir = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v2/long_short_strategy_log.csv'

def check_account_usdt_balance(client, position_size, leverage):
    account_info = client.check_future_account()
    usdt_balance = round(float(account_info['assets'][8]['availableBalance']), 2)#['USDT'])#['availableBalance'])
    print("availableUSDT:", usdt_balance)
    requirement_of_usdt = 30*position_size/leverage
    print("requirement of USDT", requirement_of_usdt)
    if requirement_of_usdt> usdt_balance:
        print("account doesn't have enough USDT")
        return False
    return True

def get_top100_crypto(url):
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


def get_top100_crypto_hist_price(coin_list):
    top_100_hist_price = {}
    for coin in coin_list:
        coin = coin+'USDT'
        hist_price = hist_crypto_price(coin, '1d')
        hist_price['timestamp'] = pd.to_datetime(hist_price['timestamp'])
        top_100_hist_price.update({coin:hist_price})
    return top_100_hist_price


def split_hist_price(price_dict, window_size):
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


def build_long_position(client, price_list, pct):
    number_of_target = int(len(price_list)*pct)
    count = 0
    long_position = []
    
    for data in price_list:
        if count == number_of_target:
            break
        try:
            print('symbol:', data[0])
            print('crypto:', data[0][:-4])
            if data[0][:-4]=='USDC':
                continue
            
            quantitative_precision = client.future_perpetual_buy(data[0], data[0][:-4],'USDT',POSITION_SIZE)
            #client.binance_future_adjust_leverage(data[0], leverage)
            
            if quantitative_precision is not None:
                for i in range(5):
                    
                    quantitative_precision = client.future_perpetual_buy(data[0], data[0][:-4],'USDT',POSITION_SIZE,quantitative_precision)
                    #client.binance_future_adjust_leverage(data[0], leverage)
                    if quantitative_precision is None:
                        count+=1
                        long_position.append(data[0])
                        break
            else:
                count+=1
                long_position.append(data[0])
        except:
            print('error')
        print('----------')
    return long_position
                           

def build_short_position(client, price_list, pct):
    number_of_target = int(len(price_list)*pct)
    count = 0
    short_position = []
    
    for i in range(len(price_list)-1, 0, -1):
        print(i)
        if count == number_of_target:
            break
        
        try:
            
            print('symbol:', price_list[i][0])
            print('crypto:', price_list[i][0][:-4])
            
            quantitative_precision = client.future_perpetual_sell(price_list[i][0],'USDT', price_list[i][0][:-4],POSITION_SIZE)
            #client.binance_future_adjust_leverage(price_list[i][0], leverage)
            

            if quantitative_precision is not None:
                for i in range(5):
                    quantitative_precision = client.future_perpetual_sell(price_list[i][0], 'USDT', price_list[i][0][:-4], POSITION_SIZE, quantitative_precision)
                    if quantitative_precision is None:
                        count+=1
                        short_position.append(price_list[i][0])
                        break
            else:
                count+=1
                short_position.append(price_list[i][0])
        except:
            print('error')
        print('----------')
   
    return short_position


def close_all_position(client, long_positions, short_positions):
    for long_position, short_position in zip(long_positions, short_positions):
        client.future_perpetual_close_position(long_position)
        client.future_perpetual_close_position(short_position)

def adject_leverage(client, price_list, leverage):
    for data in price_list:
        try:
            client.binance_future_adjust_leverage(data[0], leverage)
        except:
             print("adj_leverage", data[0])

def add_trade_log(client, df, csv_dir, long_position, short_positions):
    #trade_info = binance_transaction.check_future_trade_history()
    #time_str = pd.to_datetime(datetime.fromtimestamp(trade_info[0]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
    #shift_time = pd.Timedelta(weeks=0,days=0,hours=0,minutes=5,seconds=0)
    #stander_time = current_time-shift_time
    for symbol in long_positions:
        quantity = 0
        print(symbol)
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
        
        print(pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
        print(trade_info[-1]['side'])
        print(quantity)
        
        
        timestamp = pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        side = trade_info[-1]['side']
        new_row = {'timestamp': timestamp,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
        df = df.append(new_row, ignore_index=True)
        
    for symbol in short_positions:
        quantity = 0
        print(symbol)
        trade_info = client.check_future_trade_history(symbol)
        position_info = binance_transaction.future_check_position(symbol)
        
        symbol_current_position = float(position_info[0]['positionAmt'])
        for i in range(len(df)):
            if df['symbol'][i] == symbol:
                quantity+= df['quantity'][i]
        quantity = symbol_current_position-quantity      
        
        print(pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
        print(trade_info[-1]['side'])
        print(quantity)
        timestamp = pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        side = trade_info[-1]['side']
        new_row = {'timestamp': timestamp,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
        df = df.append(new_row, ignore_index=True)
    df.to_csv(csv_dir, index=False)

#判斷是否達到關倉條件    
def close_position_conditional_judgment(client, csv_dir):
    log_file = pd.read_csv(log_file_dir, index_col=False)
    current_time = pd.to_datetime(datetime.now())
    for i in range(len(log_file)):
        
        k_value = pd.Timedelta(weeks=0,days=log_file['K_value'][i],hours=0,minutes=0,seconds=0)
        timestamp = pd.to_datetime(log_file['timestamp'][i])
        # 判斷否超過持倉時間
        if timestamp + k_value < current_time:
            # 平倉
            print('close')
            res = client.future_perpetual_partial_close_position(log_file['symbol'][i], log_file['quantity'][i])
            if res == True:
                # remove log
                log_file.drop(i, inplace=True)
            if res == False:
                print('error')
        else:
            print('pass')

    # reset index
    log_file.reset_index(inplace=True, drop=True)
    # save csv
    log_file.to_csv(csv_dir, index=False)   
    
# 判斷是否開倉
def open_position_conditional_judgment(client, csv_dir):
    log_file = pd.read_csv(log_file_dir, index_col=False)
    # 判斷最新交易是否隔一個月
    # check last trade log 
    last_trade = pd.to_datetime(log_file['timestamp'].iloc[-1])
    current_time = pd.to_datetime(datetime.now())
    one_month = pd.Timedelta(weeks=0, days=30,hours=0,minutes=0,seconds=0)
    if  last_trade + one_month < current_time:
        # open position signal 
        return True
    else:
        return False
    
if __name__ == '__main__':
    
    # 检查文件是否存在
    if os.path.exists(log_file_dir):
        print(f"CSV file {log_file_dir} exist")
        df = pd.read_csv(log_file_dir, index_col=False)
    else:
        # 不存在新增log file
        print(f"CSV flie {log_file_dir} not exist")
        df = pd.DataFrame(columns=['timestamp', 'symbol', 'side', 'quantity', 'K_value'])
        df.to_csv(log_file_dir, index=True)
        print("create csv file")
        
    # 判斷是否平倉
    
    # 判斷是否開倉
        # 檢查餘額
        # 開倉
        # 紀錄
    
        

    coins = get_top100_crypto('https://coinmarketcap.com')   
    top_100_hist_price = get_top100_crypto_hist_price(coins)
    dataset = split_hist_price(top_100_hist_price, window_size=J_VALUE)
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
    binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)    
    adject_leverage(binance_transaction, sorted_dict, LEVERAGE)
    long_positions = build_long_position(binance_transaction, sorted_dict, 0.2)
    short_positions = build_short_position(binance_transaction, sorted_dict, 0.2)
    time.sleep(60)
    add_trade_log(binance_transaction, df,  log_file_dir, long_positions, short_positions)    
    # define hoding period
    #time.sleep(K_VALUE*86400)
    # close position
    #close_all_position(binance_transaction, long_positions, short_positions)    
    
    #binance_transaction.binance_future_adjust_leverage('LINKUSDT', 3)
    #binance_transaction.future_perpetual_buy('BNBUSDT', 'BNB','USDT',20)
    
    
    
    
    
    
    
    
    
#%%
check_account_usdt_balance(binance_transaction, POSITION_SIZE, LEVERAGE)
# trade history

trade_info = binance_transaction.check_future_trade_history('IMXUSDT')
print(pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')))   
currentDateAndTime = pd.to_datetime(datetime.now())
shift_time = pd.Timedelta(weeks=0,days=0,hours=0,minutes=5,seconds=0)
test = currentDateAndTime-shift_time
print(currentDateAndTime-shift_time)
print(test>currentDateAndTime)    
#%%
position_info = binance_transaction.future_check_position('NEOUSDT')
type(df['timestamp'][0])
df['symbol'][3]
float(position_info[0]['positionAmt'])
print(df.index[0])
print(df)
test_df = close_position_conditional_judgment(log_file_dir)
open_position_conditional_judgment(binance_transaction, log_file_dir)
