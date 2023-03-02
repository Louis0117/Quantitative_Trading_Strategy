#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 16:53:16 2023

@author: welcome870117
"""
# calculate range
def _calculate_range(df, n_day):
    # get HH, LC, HC, LL
    HH = max(df['high'][-1-n_day:-1])
    LC = min(df['close'][-1-n_day:-1])
    HC = max(df['close'][-1-n_day:-1])
    LL = min(df['low'][-1-n_day:-1])
    range_value = max(HH-LC, HC-LL)
    return range_value

# dual thrust strategy
def trading_strategy(df, n_day, k1, k2):
    range_value = _calculate_range(df, n_day)
    open_price = df['open'][-1]
    long_price = open_price + k1*range_value
    short_price = open_price - k2*range_value
    return long_price, short_price