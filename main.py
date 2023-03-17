#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 12:22:05 2023

@author: welcome870117
"""

# import package
import torch
from tqdm import tqdm, trange
import numpy as np
import time
from datetime import datetime
from datetime import timedelta
import pytz
import pandas as pd
# import python file
from collect_text_from_twitter import connect_tweepy_client, get_starttime_endtime, get_user_tweet_info, connect_twarc2_client, get_reply_data, different_date_filter
from preprocessing import strip_emoji, strip_all_entities, clean_hashtags, filter_chars, remove_mult_spaces, delete_short_text, delete_same_text
from create_dataset import create_XLNet_dataset, create_RoBerta_dataset
from NN_model import english_classifer_model, english_classifier_predictions , sentiment_classifer_model, sentiment_classifier_prediction
from utils import drop_element, add_new_column
from price_data import current_crypto_price, history_crypto_price
from strategy import trading_strategy, optimized_dual_thrust_spot
from binance_api import binance_spot_trading, binance_future_perpetual_order, binance_future_perpetual_close_position, binance_future_check_position, binance_future_adjust_leverage
from sent_email import sent_mail


# perparameters
BINANCE_KEY = ''
BINANCE_SECRET = ''
BEAR_TOKEN = ''
TWITTER_COUNT_ID = '957716432430641152'
TIME_ZONE = pytz.timezone("utc")
ORDER_SIZE = 11
DEVICE = torch.device("cpu")
XLNET_BATCH_SIZE = 32
XLNET_MAX_LEN = 128
ROBERTA_BATCH_SZIE = 8
ROBERTA_MAX_LEN = 256
#%%

def _getting_twitter_daily(BEAR_TOKEN, TWARC2_BEARER_TOKEN, TWITTER_COUNT_ID):
    # print information
    print('-----get twitter reply data-----')
    # client initialized, you will be ready to start using the various functions in tweepy.
    tweepy_client = connect_tweepy_client(BEAR_TOKEN)   
    # Get the target time period for twitter data collection
    start_time , end_time = get_starttime_endtime()
    # print information
    print('start time:',start_time)
    print('end time:', end_time)
    # get user tweet&reply information
    user_all_tweet_info = get_user_tweet_info(tweepy_client, TWITTER_COUNT_ID, end_time)
    # 
    twarc2_client = connect_twarc2_client(TWARC2_BEARER_TOKEN)
    #
    reply_data = get_reply_data(twarc2_client, user_all_tweet_info, start_time, end_time) 
    #
    reply_data = different_date_filter(reply_data , start_time)
    print('-'*30)
    #reply_data = None
    return user_all_tweet_info, reply_data


def _return_preprocessing_data(dataset, text):
    print('-----data preprocessing-----')
    preprocess_text = []
    for i in trange(len(text)):
        preprocess_text.append(remove_mult_spaces(filter_chars(clean_hashtags(strip_all_entities(strip_emoji(text[i]))))))  
    dataset['preprocess_text'] = preprocess_text
    dataset = delete_short_text(dataset, dataset['preprocess_text'])
    dataset = delete_same_text(dataset,'preprocess_text')
    print('-'*30)
    return dataset


def _english_text_classification(df):
    dataloader_english_classifier = create_XLNet_dataset(df['conversation_text'], XLNET_MAX_LEN, XLNET_BATCH_SIZE)
    # classification of English text
    model = english_classifer_model()
    english_text_predictions = english_classifier_predictions(model, dataloader_english_classifier, DEVICE)
    # drop elements which class equal 0
    dataset_english = drop_element(df, list(english_text_predictions)) 
    return dataset_english


def _sentiment_analysis(df): 
    # sentiment analysis sentence 
    dataloader_sentiment_classifier = create_RoBerta_dataset(df, ROBERTA_BATCH_SZIE, ROBERTA_MAX_LEN)  
    model = sentiment_classifer_model()
    sentiment_text_predictions = sentiment_classifier_prediction(model, dataloader_sentiment_classifier, DEVICE)
    df = add_new_column(df, 'sentiment', list(sentiment_text_predictions))
    daily_sentiment_score = sum(sentiment_text_predictions)
    return df, daily_sentiment_score


def dual_thrust_spot_strategy():
    '''
    mode1 - dual thrust strategy (long-only)
    
    (version without sentiment(dual thrust only))
    2-layer of while loop
    * first - while 1 無窮迴圈 -> update price trigger 
    * second - while (when date change) -> detect wheather touch price trigger / trading 
    
    '''
    while True:
        # get AXS 1d history price 
        AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
        # get trigger price 
        long_price, short_price = trading_strategy(AXS_hist_price, 5, 0.7, 0.7)
        long_price, short_price = round(long_price, 3), round(short_price, 3)
        # get current time
        utc_time = datetime.now(TIME_ZONE)
        # 
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        while data_update_date==current_date:
            current_price = current_crypto_price('AXSUSDT')
            
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # buy signal 
                binance_spot_trading(True , False , current_price, ORDER_SIZE)
                long_price = long_price*100
                
            elif current_price < short_price:
                # sell signal
                binance_spot_trading(False , True , current_price, ORDER_SIZE)
                short_price = short_price/100

            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)


def optimized_dual_thrust_spot_strategy():
    '''
    mode2 - optimized dual thrust spot (long-only)
    '''
    
    while True:
        # get current time -> type: datetime
        utc_time = datetime.now(TIME_ZONE)
        # get the day before yesterday date -> type: str
        before_yest_date = (utc_time+timedelta(days=-2)).strftime("%Y-%m-%d")
        # get yesterday date -> type: str
        yest_date = (utc_time+timedelta(days=-1)).strftime("%Y-%m-%d")
        # data_update_date is used to tag the date which data updated 
        # current_date is used to keep update current time
        # use two variable to distingush weather date change
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        # get user reply text data
        user_all_tweet_info, reply_data = _getting_twitter_daily(BEAR_TOKEN, BEAR_TOKEN, TWITTER_COUNT_ID)
        # datapreprocessing 
        dataset = _return_preprocessing_data(reply_data, reply_data['conversation_text'])
        # use english text classifer to filter non-english text
        dataset_english = _english_text_classification(dataset)
        # sentiment analysis and calculate sentiment score
        dataset_english, daily_sentiment_score = _sentiment_analysis(dataset_english)
        # read_csv -> sentiment data
        sentiment_data = pd.read_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/daily_sentiment_data/{before_yest_date}_sentiment_score.csv', index_col=False)
        # sentiment write into csv
        updated_sentiment_data = sentiment_data.append({'date':yest_date, 'sentiment_score':daily_sentiment_score}, ignore_index=True, sort=False)
        # save csv file
        updated_sentiment_data.to_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/daily_sentiment_data/{yest_date}_sentiment_score.csv', index=False)
        dataset_english.to_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/text_data/{yest_date}_text_data.csv', index=False)
        # get AXS 1d history price 
        AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
        # get trigger price 
        long_price, short_price, adjusted_order_size = optimized_dual_thrust_spot(price_data = AXS_hist_price, sentiment_data = updated_sentiment_data, 
                                                                                  lookback_r = 5, lookback_s = 4, window_size_s=70, order_size=ORDER_SIZE, 
                                                                                  p1 = 0.05, p2 = 0.05, k1 = 0.75, k2 = 0.75)
        while data_update_date==current_date:
            current_price = current_crypto_price('AXSUSDT')
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # buy signal 
                binance_spot_trading(True , False , current_price, ORDER_SIZE)
                long_price = long_price*100
                
            elif current_price < short_price:
                # sell signal
                binance_spot_trading(False , True , current_price, ORDER_SIZE)
                short_price = short_price/100

            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)
            
            
def dual_thrust_future_strategy():
    while True:
        # get AXS 1d history price 
        AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
        # get trigger price 
        long_price, short_price = trading_strategy(AXS_hist_price, 5, 0.75, 0.75)
        long_price, short_price = round(long_price, 3), round(short_price, 3)
        # get current time
        utc_time = datetime.now(TIME_ZONE)
        # 
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        while data_update_date==current_date:
            current_price = current_crypto_price('AXSUSDT')
            
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # check position 
                position = binance_future_check_position(api_keys=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                if float(position[0]["positionAmt"])<0:
                    # if account has short position, close short position and place the long order
                    binance_future_perpetual_close_position(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                    # place the buy order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                side='BUY', leverage=None, price=None, stop_loss=None, take_profit=None)
                    long_price = long_price*100
                else:
                    # place the buy order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                side='BUY', leverage=None, price=None, stop_loss=None, take_profit=None)
                    long_price = long_price*100
                    
            # discreminate whether touch off trigger      
            elif current_price < short_price:
                if float(position[0]["positionAmt"])>0:
                    # if account has long position, close short position and place the short order
                    binance_future_perpetual_close_position(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                    # create sell order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                    side='SELL', leverage=None, price=None, stop_loss=None, take_profit=None)
                    short_price = short_price/100
                else:
                    # create sell order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                    side='SELL', leverage=None, price=None, stop_loss=None, take_profit=None)
                    short_price = short_price/100
    
            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)          
            

def optimize_dual_thrust_future_strategy():
    while True:
        # get current time -> type: datetime
        utc_time = datetime.now(TIME_ZONE)
        # get the day before yesterday date -> type: str
        before_yest_date = (utc_time+timedelta(days=-2)).strftime("%Y-%m-%d")
        # get yesterday date -> type: str
        yest_date = (utc_time+timedelta(days=-1)).strftime("%Y-%m-%d")
        # data_update_date is used to tag the date which data updated 
        # current_date is used to keep update current time
        # use two variable to distingush weather date change
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        # get user reply text data
        user_all_tweet_info, reply_data = _getting_twitter_daily(BEAR_TOKEN, BEAR_TOKEN, TWITTER_COUNT_ID)
        # datapreprocessing 
        dataset = _return_preprocessing_data(reply_data, reply_data['conversation_text'])
        # use english text classifer to filter non-english text
        dataset_english = _english_text_classification(dataset)
        # sentiment analysis and calculate sentiment score
        dataset_english, daily_sentiment_score = _sentiment_analysis(dataset_english)
        # read_csv -> sentiment data
        sentiment_data = pd.read_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/daily_sentiment_data/{before_yest_date}_sentiment_score.csv', index_col=False)
        # sentiment write into csv
        updated_sentiment_data = sentiment_data.append({'date':yest_date, 'sentiment_score':daily_sentiment_score}, ignore_index=True, sort=False)
        # save csv file
        updated_sentiment_data.to_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/daily_sentiment_data/{yest_date}_sentiment_score.csv', index=False)
        dataset_english.to_csv(f'/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/text_data/{yest_date}_text_data.csv', index=False)
        # get AXS 1d history price 
        AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
        # get trigger price 
        long_price, short_price, adjusted_order_size = optimized_dual_thrust_spot(price_data = AXS_hist_price, sentiment_data = updated_sentiment_data, 
                                                                                  lookback_r = 5, lookback_s = 4, window_size_s=70, order_size=ORDER_SIZE, 
                                                                                  p1 = 0.05, p2 = 0.05, k1 = 0.75, k2 = 0.75)
        
        while data_update_date==current_date:
            current_price = current_crypto_price('AXSUSDT')
            
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # check position 
                position = binance_future_check_position(api_keys=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                if float(position[0]["positionAmt"])<0:
                    # if account has short position, close short position and place the long order
                    binance_future_perpetual_close_position(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                    # place the buy order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                side='BUY', leverage=None, price=None, stop_loss=None, take_profit=None)
                    long_price = long_price*100
                else:
                    # place the buy order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                side='BUY', leverage=None, price=None, stop_loss=None, take_profit=None)
                    long_price = long_price*100
                    
            # discreminate whether touch off trigger      
            elif current_price < short_price:
                if float(position[0]["positionAmt"])>0:
                    # if account has long position, close short position and place the short order
                    binance_future_perpetual_close_position(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT')
                    # create sell order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                    side='SELL', leverage=None, price=None, stop_loss=None, take_profit=None)
                    short_price = short_price/100
                else:
                    # create sell order
                    binance_future_perpetual_order(api_key=BINANCE_KEY, api_secret=BINANCE_SECRET, symbol='AXSUSDT', order_size=ORDER_SIZE, 
                                                    side='SELL', leverage=None, price=None, stop_loss=None, take_profit=None)
                    short_price = short_price/100
    
            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)     
    
 #%%   
if __name__ == '__main__':   
    #dual_thrust_spot_strategy()
    #optimized_dual_thrust_spot_strategy()
    #optimize_dual_thrust_future_strategy()
    
    '''
    *** menu ***
    while True:
        print("Please select which trading strategy to use：")
        print("1. dual thrust strategy (long-only) for spot trading")
        print("2. optimized dual thrust strategy (long-only) for spot trading")
        print("3. leave")
        #print("4. 離開")
        choice = input("please enter selection（1-3）：")
        if choice == "1":
            dual_thrust_spot_strategy()
        elif choice == "2":
            optimized_dual_thrust_spot_strategy
        elif choice == "3":
            print("thanks for using！")
            #break
        else:
            print("Invalid selection, please enter again")
    '''