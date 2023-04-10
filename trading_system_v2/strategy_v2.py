#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:43:01 2023

@author: welcome870117
"""

# import package
import numpy as np


class Strategy:
    def __init__(self):
        pass
    
    
    # calculate range
    def _calculate_range(self, df, lookback_day):
        '''
    
        Parameters
        ----------
        df : Dataframe
            AXS history price data (period = 1day)
        lookback_day : int 
            look back days
    
        Returns
        -------
        range_value : float
            range value
    
        '''
        # get HH, LC, HC, LL
        HH = max(df['high'][-1-lookback_day:-1])
        LC = min(df['close'][-1-lookback_day:-1])
        HC = max(df['close'][-1-lookback_day:-1])
        LL = min(df['low'][-1-lookback_day:-1])
        # range formula 
        range_value = max(HH-LC, HC-LL)
        return range_value

    
    def _get_sentiment_threshold(self, df, window_size_s, p1, p2):
        '''
    
        Parameters
        ----------
        df : TYPE
            DESCRIPTION.
        window_size_s : TYPE
            DESCRIPTION.
        p1 : TYPE
            DESCRIPTION.
        p2 : TYPE
            DESCRIPTION.
    
        Returns
        -------
        small_threshold : TYPE
            DESCRIPTION.
        large_threshold : TYPE
            DESCRIPTION.
    
        '''
        # turn sentiment socre from type Series to np.array
        sentiment_score_array = np.array(df['sentiment_score'].iloc[-window_size_s:])
        # sort sentiemt score small > big
        sort_sentiment_score = np.argsort(sentiment_score_array)
        # get index value 
        index_small = int(p1*window_size_s)
        index_big = int((1-p2)*window_size_s)
        # get threshold value
        small_threshold = sentiment_score_array[sort_sentiment_score[index_small]]
        # last 25% value, k = 45
        large_threshold = sentiment_score_array[sort_sentiment_score[index_big]]
        return small_threshold, large_threshold
    
    def _adject_k1_k2_order_size(self, df_sentiment, small_threshold, large_threshold, lookback_s, order_size, k1, k2):  
        '''
    
        Parameters
        ----------
        df_sentiment : TYPE
            DESCRIPTION.
        small_threshold : TYPE
            DESCRIPTION.
        large_threshold : TYPE
            DESCRIPTION.
        lookback_s : TYPE
            DESCRIPTION.
        order_size : TYPE
            DESCRIPTION.
        k1 : TYPE
            DESCRIPTION.
        k2 : TYPE
            DESCRIPTION.
    
        Returns
        -------
        adjusted_k1 : TYPE
            DESCRIPTION.
        adjusted_k2 : TYPE
            DESCRIPTION.
        adjusted_order_size : TYPE
            DESCRIPTION.
    
        '''
        lookback_day_sentiment = list(df_sentiment['sentiment_score'].iloc[-lookback_s:])
        adjusted_value = 0
        for sentiment_score in lookback_day_sentiment:
            if sentiment_score > large_threshold:
                adjusted_value+=1
            elif sentiment_score < small_threshold:
                adjusted_value-=1
        adjusted_k1 = (k1-(adjusted_value/lookback_s)*0.15)
        adjusted_k2 = (k2+(adjusted_value/lookback_s)*0.15)
        adjusted_order_size = (1+adjusted_value/lookback_s)*order_size
        return adjusted_k1, adjusted_k2, adjusted_order_size
            
    # dual thrust strategy
    def dual_thrust_strategy(self, df, lookback_day, k1, k2):
        '''
        
        Parameters
        ----------
        df : Dataframe
            AXS history price data (period = 1day)
        lookback_day : int
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
        range_value = self._calculate_range(df, lookback_day)
        # get open price
        open_price = df['open'][-1]
        # calculate long(cap line) price / short(floor line) price 
        long_price = open_price + k1*range_value
        short_price = open_price - k2*range_value
        return long_price, short_price
    
    # optimized_dual_thrust_spot
    def optimized_dual_thrust_strategy(self, df_price, df_sentiment, lookback_r, lookback_s, window_size_s,order_size, p1, p2, k1, k2):
        '''
    
        Parameters
        ----------
        df_price : TYPE
            DESCRIPTION.
        df_sentiment : TYPE
            DESCRIPTION.
        lookback_r : TYPE
            DESCRIPTION.
        lookback_s : TYPE
            DESCRIPTION.
        window_size_s : TYPE
            DESCRIPTION.
        order_size : TYPE
            DESCRIPTION.
        p1 : TYPE
            DESCRIPTION.
        p2 : TYPE
            DESCRIPTION.
        k1 : TYPE
            DESCRIPTION.
        k2 : TYPE
            DESCRIPTION.
    
        Returns
        -------
        long_price : TYPE
            DESCRIPTION.
        short_price : TYPE
            DESCRIPTION.
        adjusted_order_size : TYPE
            DESCRIPTION.
    
        '''
        # df, lookback-day-range, lookback-day-sentiment, order-size
        # -> -> long / short price, order size
        # calculate range value
        range_value = self._calculate_range(df_price, lookback_r)
        # get optimized k1, k2
        small_threshold, large_threshold = self._get_sentiment_threshold(df_sentiment, window_size_s, p1, p2)
        #print('small threshold:', small_threshold)
        #print('large threshold:', large_threshold)
        adjusted_k1, adjusted_k2, adjusted_order_size = self._adject_k1_k2_order_size(df_sentiment, small_threshold, large_threshold, lookback_s, order_size, k1, k2)
        #print('adj k1:', adjusted_k1)
        #print('adj k2:', adjusted_k2)
        #print('odsize:', adjusted_order_size)
        # get open price
        open_price = df_price['open'][-1]
        # calculate long(cap line) price / short(floor line) price 
        long_price = round(open_price + adjusted_k1*range_value, 3)
        short_price = round(open_price - adjusted_k2*range_value, 3)
        adjusted_order_size = round(adjusted_order_size, 1)
        return long_price, short_price, adjusted_order_size
    



    
