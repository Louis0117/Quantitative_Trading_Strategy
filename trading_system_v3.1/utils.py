#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:10:54 2023

@author: welcome870117
"""

import numpy as np
import requests
import json
import pandas as pd



def hist_crypto_price(tradingpair, period):
    '''

    Parameters
    ----------
    tradingpair : str
        cryptocurency trading pair
    period : str
        the time which create a candlestick
        
    Returns
    -------
    price_data : data
        crypto history price data

    ''' 
    
    # 設置 API endpoint 和參數
    endpoint = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': tradingpair,  # 設置要查詢的交易對
        'interval': period,    # 設置時間間隔 (1d = 1 day)
        'limit': 1000        # 設置獲取歷史價格的數量 (最多1000)
    }
    # 請求歷史價格數據
    response = requests.get(endpoint, params=params)
    data = json.loads(response.text)
    
    # 將數據轉換為 pandas DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time', 'quote_asset_volume', 'number_of_trades',
                                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                     'ignore'])
    # 轉換時間戳 (timestamp) 到日期格式
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.astype({'open':float, 'high':float, 'low':float, 'close':float, 'volume':float,
                                     'close_time':float, 'quote_asset_volume':float, 'number_of_trades':float,
                                     'taker_buy_base_asset_volume':float, 'taker_buy_quote_asset_volume':float,
                                     'ignore':float})
    # 列印 DataFrame
    #print(df)
    return df

    

# get current crypto price
def current_crypto_price(tradingpair):
    '''

    Parameters
    ----------
    tradingpair : str
        cryptocurency trading pair

    Returns
    -------
    current_price : float
        cryptocurrency current price

    '''
    
    # get current price from Binance
    current_price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+tradingpair)  
    current_price = float(current_price.json()['price'])
    return current_price