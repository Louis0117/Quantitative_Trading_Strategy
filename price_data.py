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
    tradingpair : TYPE
        DESCRIPTION.
    period : TYPE
        DESCRIPTION.

    Returns
    -------
    price_data : TYPE
        DESCRIPTION.

    ''' 
    price_data = finlab_crypto.crawler.get_all_binance(tradingpair, period)
    return price_data

# get current crypto price
def current_crypto_price(tradingpair):
    '''

    Parameters
    ----------
    tradingpair : TYPE
        DESCRIPTION.

    Returns
    -------
    current_price : TYPE
        DESCRIPTION.

    '''
    current_price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol='+tradingpair)
    return current_price