#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 16:53:16 2023

@author: welcome870117
"""


# calculate range
def _calculate_range(df, n_day):
    '''

    Parameters
    ----------
    df : Dataframe
        AXS history price data (period = 1day)
    n_day : int 
        look back days

    Returns
    -------
    range_value : float
        range value

    '''
    # get HH, LC, HC, LL
    HH = max(df['high'][-1-n_day:-1])
    LC = min(df['close'][-1-n_day:-1])
    HC = max(df['close'][-1-n_day:-1])
    LL = min(df['low'][-1-n_day:-1])
    # range formula 
    range_value = max(HH-LC, HC-LL)
    return range_value


# dual thrust strategy
def trading_strategy(df, n_day, k1, k2):
    '''
    
    Parameters
    ----------
    df : Dataframe
        AXS history price data (period = 1day)
    n_day : int
        look back days
    k1 : float
        a parameter which adject cap line
    k2 : float
        a parameter which adject floor line 

    Returns
    -------
    long_price : float 
        cap line price (long price)
    short_price : float
        floor line price (short price)
                
    '''
    # calculate range value
    range_value = _calculate_range(df, n_day)
    # get open price
    open_price = df['open'][-1]
    # calculate long(cap line) price / short(floor line) price 
    long_price = open_price + k1*range_value
    short_price = open_price - k2*range_value
    return long_price, short_price


def _get_sentiment_threshold(df):
    df['sentiment_score']

# optimized_dual_thrust_spot
def optimized_dual_thrust_spot(price_data, sentiment_data, lookback_r, lookback_s, window_size_s,order_size, k1, k2):
    # df, lookback-day-range, lookback-day-sentiment, order-size
    # -> -> long / short price, order size
    # calculate range value
    range_value = _calculate_range(price_data, lookback_r)
    # get optimized k1, k2
    
    
    
    # get open price
    open_price = price_data['open'][-1]
    # calculate long(cap line) price / short(floor line) price 
    long_price = open_price + k1*range_value
    short_price = open_price - k2*range_value