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
import pytz
# import python file
from collect_text_from_twitter import connect_tweepy_client, get_starttime_endtime, get_user_tweet_info, connect_twarc2_client, get_reply_data, different_date_filter
from preprocessing import strip_emoji, strip_all_entities, clean_hashtags, filter_chars, remove_mult_spaces, delete_short_text
from create_dataset import create_XLNet_dataset, create_RoBerta_dataset
from NN_model import english_classifer_model, english_classifier_predictions , sentiment_classifer_model, sentiment_classifier_prediction
from utils import drop_element
from price_data import current_crypto_price, history_crypto_price
from strategy import trading_strategy
from binance_api import binance_trading
from sent_email import sent_mail

# perparameters
API_KEY = ''
API_KEY_SECRET = ''
BEAR_TOKEN = ''
ACCESS_TOKEN =''
ACCESS_TOKEN_SECRET= ''
# Axie infinity official twitter
TWITTER_COUNT_ID = '957716432430641152'
TWARC2_BEARER_TOKEN = ''
PRETRAINED_MODEL_NAME = "bert-base-cased"
TIME_ZONE = pytz.timezone("utc")
ORDER_SIZE = 11
device = torch.device("cpu")


def getting_twitter_daily(BEAR_TOKEN, TWARC2_BEARER_TOKEN, TWITTER_COUNT_ID):
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


def return_preprocessing_data(dataset, text):
    print('-----data preprocessing-----')
    preprocess_text = []
    for i in trange(len(text)):
        preprocess_text.append(remove_mult_spaces(filter_chars(clean_hashtags(strip_all_entities(strip_emoji(text[i]))))))  
    dataset['preprocess_text'] = preprocess_text
    dataset = delete_short_text(dataset, dataset['preprocess_text'])
    print('-'*30)
    return dataset

if __name__ == '__main__':

    user_all_tweet_info, reply_data = getting_twitter_daily(BEAR_TOKEN, TWARC2_BEARER_TOKEN, TWITTER_COUNT_ID)
    dataset = return_preprocessing_data(reply_data, reply_data['conversation_text'])
    #%%
    dataloader_english_classifier = create_XLNet_dataset(dataset['conversation_text'], 128, 32)
    #%%
    # classification of English text
    english_classifer_model = english_classifer_model()
    english_text_predictions = english_classifier_predictions(english_classifer_model, dataloader_english_classifier, device)
    #%%
    # drop elements which class equal 0
    dataset_english = drop_element(dataset, list(english_text_predictions)) 
    #%%
    # sentiment analysis sentence 
    dataloader_sentiment_classifier = create_RoBerta_dataset(dataset, 8, 256)
    #%%    
    sentiment_classifer = sentiment_classifer_model()
    #%%
    sentiment_text_predictions = sentiment_classifier_prediction(sentiment_classifer, dataloader_sentiment_classifier, device)
    # calculate sentiment analysis score
    # 
    #%%
    #info = current_crypto_price('AXSUSDT')
    #info_data = info.json() # type dict
    AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
    #%%
    # 10.328 / 8.872
    long_price, short_price = trading_strategy(AXS_hist_price, 5, 0.7, 0.7)
    #%%
    #binance_trading(long_price, short_price, 11)
    
    #UTC +0 get sentiment score / calculate trigger price long price, short price
    # set loop update current price 
    '''
    count = 0
    while count!=100:
        current_price = float(current_crypto_price('AXSUSDT').json()['price'])
        print('AXS current price:', current_price)
        print(type(current_price))
        print('-'*30)
        time.sleep(10)
        count+=1 
    '''
        
    #%%
    '''
    mode1 - dual thrust strategy (long-only)
    
    (version without sentiment(dual thrust only))
    2-layer of while loop
    * first - while 1 無窮迴圈 -> update price trigger 
    * second - while (when date change) -> detect wheather touch price trigger / trading 
    
    (version combine sentiment & dual thrust strategy)
    2-layer of while loop
    * first - while 1 無窮迴圈 ->  get sentiment score -> use score adject parameter (k1, k2, order size) / update price trigger
    * second - while (when date change) -> detect wheather touch price trigger / trading
    '''
    while True:
        AXS_hist_price = history_crypto_price('AXSUSDT', '1d')
        long_price, short_price = trading_strategy(AXS_hist_price, 5, 0.7, 0.7)
        long_price, short_price = round(long_price, 3), round(short_price, 3)
        utc_time = datetime.now(TIME_ZONE)
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        while data_update_date==current_date:
            current_price = current_crypto_price('AXSUSDT')
            
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # buy signal 
                binance_trading(True , False , current_price, ORDER_SIZE)
                long_price = long_price*100
                
            elif current_price < short_price:
                # sell signal
                binance_trading(False , True , current_price, ORDER_SIZE)
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
    '''
    # test block
    current_price = float(current_crypto_price('AXSUSDT').json()['price'])
    print('current price:', current_price)
    binance_trading(False , True , current_price, ORDER_SIZE)
    '''
#%%
    '''
    # test block
    system_mail_address, app_pwd, client_mail_address , msg
    交易系統以xxx一顆的價格買入xxx顆AXS加密貨幣,一共價值xxxUSDT/ 
    
    The trading system place a buying order at the AXS cryptocurrencies price {current price}, 
    with a total value of {order size} USDT 
    
    The trading system buys xxx AXS cryptocurrencies at the price of xxx one, 
    with a total value of xxxUSDT
    '''    
    #msg = "Subject:Trading system complete transaction notification email\nThe trading system buys xxx AXS cryptocurrencies at the price of xxx one, with a total value of xxxUSDT"
    #sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
    #msg = f"Subject:Trading system complete transaction notification email\nThe trading system place a buying order at the AXS cryptocurrency price {current_price} with a total value of {ORDER_SIZE} USDT"
    #sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)