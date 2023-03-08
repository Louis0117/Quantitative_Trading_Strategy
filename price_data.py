#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 14:31:21 2023

@author: welcome870117
"""

import finlab_crypto
import numpy as np
import requests


# get history crypto price
def history_crypto_price(tradingpair, period):
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
    # get crypto price from Binance
    price_data = finlab_crypto.crawler.get_all_binance(tradingpair, period)
    return price_data

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