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
BINANCE_KEY = ''
BINANCE_SECRET = ''

if len(sys.argv)!=5:
    print('input parameter number error')
  
POSITION_SIZE = int(sys.argv[1]) 
LEVERAGE = int(sys.argv[2])
J_VALUE = int(sys.argv[3]) # lookback days
K_VALUE = int(sys.argv[4]) # hold days
# profolio log file address
log_file_dir = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v2/long_short_strategy_log.csv'

# check account USDT balance  
def check_account_usdt_balance(client, position_size, leverage):
    '''

    Parameters
    ----------
    client : TYPE
        Binance clinet 
        
    position_size : float
        position size of each asset in the investment portfolio
        
    leverage : float
        leverage size

    Returns
    -------
    bool 
        Determine if the USDT balance in the account is sufficient to establish an investment portfolio.
        
    '''
    
    account_info = client.check_future_account()
    usdt_balance = round(float(account_info['assets'][8]['availableBalance']), 2) #['USDT'])#['availableBalance'])
    print('check account USDT balance')
    print("availableUSDT:", usdt_balance)
    ##########################################
    requirement_of_usdt = 21*position_size/leverage
    print("requirement of USDT", requirement_of_usdt)
    if requirement_of_usdt> usdt_balance:
        print("account doesn't have enough USDT")
        return False
    return True


# get top 100 market value coin
def _get_top100_crypto(url):
    '''

    Parameters
    ----------
    url : str       
        url of marketcap    
    
    Returns
    -------
    coins : list
        top 50 market value coin

    '''
    response = rq.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data= soup.find('script',id="__NEXT_DATA__",type="application/json")
    dataset = []
    coins = []
    coin_data=json.loads(data.contents[0])
    listings=json.loads(coin_data["props"]["initialState"])["cryptocurrency"]['listingLatest']['data']
    for i in listings[1:]: 
        coins.append(i[-4])
    # only return top 50
    return coins[:56]


# get top 100 market value coin history data
def _get_top100_crypto_hist_price(coin_list):
    '''

    Parameters
    ----------
    coin_list : list
        top 100 market value of coin.

    Returns
    -------
    top_100_hist_price : list
        list of top 100 market value history price data

    '''
    top_100_hist_price = {}
    for coin in coin_list:
        coin = coin+'USDT'
        hist_price = hist_crypto_price(coin, '1d')
        hist_price['timestamp'] = pd.to_datetime(hist_price['timestamp'])
        top_100_hist_price.update({coin:hist_price})
    return top_100_hist_price



def _split_hist_price(price_dict, window_size):
    '''

    Parameters
    ----------
    price_dict : dict
        key = Symbol, value = price data(df)
        
    window_size : int
        J value.

    Returns
    -------
    dataset : dict
        key = Symbol, value = price data(df) -> Data from the past J value days.

    '''
    dataset = {}  
    for crypto, price  in price_dict.items():
        if len(price)>window_size:
            dataset.update({crypto:price.iloc[-window_size:].reset_index(drop=True)})
    return dataset


def _calculate_daily_return(df):
    df['daily_return'] = df['close'].pct_change()


def _calculate_std(df):
    std_value = df['daily_return'].std()
    return std_value


def _build_long_position(client, price_list, pct=0.2):
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
        try:
            # not add USD in profolio
            if data[0][:-4]=='USDC':
                continue
            # create long future order
            quantitative_precision = client.future_perpetual_buy(data[0], data[0][:-4],'USDT', POSITION_SIZE)   
            #  different crypto have different quantitive precision, sometime need to adjust  
            if quantitative_precision is not None:
                for i in range(5): 
                    quantitative_precision = client.future_perpetual_buy(data[0], data[0][:-4], 'USDT', POSITION_SIZE, quantitative_precision)
                    if quantitative_precision is None:
                        count+=1
                        long_position.append(data[0])
                        print('----- long position -----')
                        print('symbol:', data[0])
                        print('----------')
                        break
            else:
                count+=1
                long_position.append(data[0])
                print('----- long position -----')
                print('symbol:', data[0])
                print('----------')
        except:
            pass
        
    return long_position
                           

def _build_short_position(client, price_list, pct=0.2):
    #number_of_target = int(len(price_list)*pct)
    number_of_target = 10
    count = 0
    short_position = []
    
    for i in range(len(price_list)-1, 0, -1):
        if count == number_of_target:
            break
        
        try:
            quantitative_precision = client.future_perpetual_sell(price_list[i][0],'USDT', price_list[i][0][:-4],POSITION_SIZE)
            #client.binance_future_adjust_leverage(price_list[i][0], leverage)
            if quantitative_precision is not None:
                for i in range(5):
                    quantitative_precision = client.future_perpetual_sell(price_list[i][0], 'USDT', price_list[i][0][:-4], POSITION_SIZE, quantitative_precision)
                    if quantitative_precision is None:
                        count+=1
                        print('----- short position -----')
                        print('symbol:', price_list[i][0])
                        print('----------')
                        break
            else:
                count+=1
                short_position.append(price_list[i][0])
                print('----- short position -----')
                print('symbol:', price_list[i][0])
                print('----------')
        except:
            pass
        
   
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


def add_trade_log(client, df, csv_dir, long_position, short_position):
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
        print('time:', pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
        print('quantity:', quantity)
        print('--------')
        
        timestamp = pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
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
        print('time:', pd.to_datetime(datetime.fromtimestamp(trade_info[-1]['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')))
        print('quantity:', quantity)
        print('--------')
        
        side = trade_info[-1]['side']
        new_row = {'timestamp': timestamp,'symbol':symbol, 'side':side, 'quantity':quantity, 'K_value':K_VALUE}
        df = df.append(new_row, ignore_index=True)
    df.to_csv(csv_dir, index=False)


# Determine if the closing conditions have been met.
def close_position_conditional_judgment(client, csv_dir):
    '''

    Parameters
    ----------
    client : TYPE
        Binance client.
        
    csv_dir : str
        log file dir

    Returns
    -------
    None.
    
    '''
    print('Determining whether to close position.....')
    log_file = pd.read_csv(csv_dir, index_col=False)
    # get current time
    current_time = pd.to_datetime(datetime.now())
    # traverse log file
    for i in range(len(log_file)):
        k_value = pd.Timedelta(weeks=0,days=log_file['K_value'][i],hours=0,minutes=0,seconds=0)
        timestamp = pd.to_datetime(log_file['timestamp'][i])
        # Determine if the holding period has exceeded.
        if timestamp + k_value < current_time:
            # close position
            print('close')
            res = client.future_perpetual_partial_close_position(log_file['symbol'][i], log_file['quantity'][i])
            if res == True:
                # remove log
                log_file.drop(i, inplace=True)
            if res == False:
                print('error in close_position_conditional_judgment')

    # reset index
    log_file.reset_index(inplace=True, drop=True)
    # save csv
    log_file.to_csv(csv_dir, index=False)   
 
    
# Determine if an investment portfolio has been established.
def open_position_conditional_judgment(client, csv_dir):
    print('Determining whether to establish an investment portfolio.....')
    log_file = pd.read_csv(csv_dir, index_col=False)
    if len(log_file)>0:
        # check last trade log, Determine if the latest transaction is separated by one month.
        last_trade = pd.to_datetime(log_file['timestamp'].iloc[-1])
        current_time = pd.to_datetime(datetime.now())
        one_month = pd.Timedelta(weeks=0, days=30,hours=0,minutes=0,seconds=0)
        if  last_trade + one_month < current_time:
            # open position signal 
            return True
        else:
            return False
    # if len(log file) = 0, create profolio
    return True


# long-short Strategy
def long_short_strategy(client):
    '''

    Parameters
    ----------
    client : TYPE
        Binance client.

    Returns
    -------
    long_positions : TYPE
        DESCRIPTION.
    short_positions : TYPE
        DESCRIPTION.

    '''
    # get top 100 crypto
    coins = _get_top100_crypto('https://coinmarketcap.com')  
    # get history price data
    top_100_hist_price = _get_top100_crypto_hist_price(coins)
    # Retrieve price data for J value days.
    dataset = _split_hist_price(top_100_hist_price, window_size=J_VALUE)
    # calculate daily return -> SD -> sort(ascending)
    for price_data in dataset.values():
        _calculate_daily_return(price_data)
    # calculate SD
    crypto_std = {}
    for crypto, price_data in dataset.items():
        crypto_std.update({crypto:_calculate_std(price_data.iloc[1:].reset_index(drop=True))})
    # sort crypto std
    sorted_dict = sorted(crypto_std.items(), key=lambda x: (x[1], x[0]))    
    # build profolio
    # set leverage
    _adject_leverage(binance_transaction, sorted_dict, LEVERAGE)
    # create long position
    long_positions = _build_long_position(binance_transaction, sorted_dict)
    # create short position
    short_positions = _build_short_position(binance_transaction, sorted_dict)
    return long_positions, short_positions

  
  
if __name__ == '__main__':
    # client object
    binance_transaction = Binance_transaction(BINANCE_KEY, BINANCE_SECRET, SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS)
    # Check if the portfolio log file exists.
    while(1):
        if os.path.exists(log_file_dir):
            print(f"CSV file {log_file_dir} exist")
            log_file = pd.read_csv(log_file_dir, index_col=False)
            # Determine if there is a need to close the position.
            close_position_conditional_judgment(binance_transaction, log_file_dir)
            # Determine if an investment portfolio has been established.
            create_profolio = open_position_conditional_judgment(binance_transaction, log_file_dir)
            if create_profolio == True:
                # check account USDT value
                sufficient_account_balance = check_account_usdt_balance(binance_transaction, POSITION_SIZE, LEVERAGE)
                if sufficient_account_balance:  
                    # create profolio
                    long_position, short_position = long_short_strategy(binance_transaction) 
                    # Waiting for the order to be created.
                    print('---- wait for create order ------')
                    time.sleep(60)
                    # add trade log
                    add_trade_log(binance_transaction, log_file, log_file_dir, long_position, short_position)
    
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
                long_position, short_position = long_short_strategy(binance_transaction) 
                # 等待訂單建立
                print('---- wait for create order ------')
                time.sleep(60)
                # add trade log
                add_trade_log(binance_transaction, log_file, log_file_dir, long_position, short_position)
        
        # sleep one day
        print('---- sleep one day ------')
        time.sleep(86200)


