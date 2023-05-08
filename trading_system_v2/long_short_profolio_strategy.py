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

# parameters
SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
BINANCE_KEY = ''
BINANCE_SECRET = ''

POSITION_SIZE = sys.argv[0]
J_VALUE = sys.argv[1] # lookback month
K_VALUE = sys.argv[2] # hold month


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
            count+=1
            long_position.append(data[0])
            if quantitative_precision is not None:
                for i in range(5):
                    quantitative_precision = client.future_perpetual_buy(data[0], data[0][:-4],'USDT',POSITION_SIZE,quantitative_precision)
                    if quantitative_precision is None:
                        break
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
            count+=1
            short_position.append(price_list[i][0])

            if quantitative_precision is not None:
                for i in range(5):
                    quantitative_precision = client.future_perpetual_sell(price_list[i][0], 'USDT', price_list[i][0][:-4], POSITION_SIZE, quantitative_precision)
                    if quantitative_precision is None:
                        break
        except:
            print('error')
        print('----------')
   
    return short_position


def close_all_position(client, long_positions, short_positions):
    for long_position, short_position in zip(long_positions, short_positions):
        client.future_perpetual_close_position(long_position)
        client.future_perpetual_close_position(short_position)
        

if __name__ == '__main__':
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
    long_positions = build_long_position(binance_transaction, sorted_dict, 0.2)
    short_positions = build_short_position(binance_transaction, sorted_dict, 0.2)
    # define hoding period
    time.sleep(K_VALUE*86400)
    # close position
    close_all_position(binance_transaction, long_positions, short_positions)    