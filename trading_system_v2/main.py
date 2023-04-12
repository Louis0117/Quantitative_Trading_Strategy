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
#from binance.client import Client
#from binance.enums import *
# import python file
from strategy_v2 import Strategy
from collect_text_from_twitter_v2 import TwitterData
from binance_api_v2 import Binance_transaction
from preprocessing import strip_emoji, strip_all_entities, clean_hashtags, filter_chars, remove_mult_spaces, delete_short_text, delete_same_text
from create_dataset import create_XLNet_dataset, create_RoBerta_dataset
from nn_model import english_classifer_model, english_classifier_predictions , sentiment_classifer_model, sentiment_classifier_prediction
from utils import drop_element, add_new_column, get_starttime_endtime, different_date_filter
from price_data import current_crypto_price, hist_crypto_price
from sent_email import sent_mail


SYS_MAIL_ADDRESS = ''
CLINET_MAIL_ADDRESS = ''
APP_PWD = ''
BINANCE_KEY = ''
BINANCE_SECRET = ''
BEAR_TOKEN = ''
TWITTER_ACCOUNT_ID = '957716432430641152'
TIME_ZONE = pytz.timezone("utc")
ORDER_SIZE = 11 # usdt
DEVICE = torch.device("cpu")
XLNET_BATCH_SIZE = 32
XLNET_MAX_LEN = 128
ROBERTA_BATCH_SZIE = 8
ROBERTA_MAX_LEN = 256
# dir
SENTIMENT_DATA_DIR = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/daily_sentiment_data/'
#dir
TEXT_DATA_DIR = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/system_data/text_data/'


def _get_twitter_reply(bear_token = BEAR_TOKEN, twarc2_bear_token = BEAR_TOKEN, twitter_account_id = TWITTER_ACCOUNT_ID):
    '''

    Parameters
    ----------
    bear_token : TYPE, optional
        DESCRIPTION. The default is BEAR_TOKEN.
    twarc2_bear_token : TYPE, optional
        DESCRIPTION. The default is TWARC2_BEARER_TOKEN.
    twitter_account_id : TYPE, optional
        DESCRIPTION. The default is TWITTER_ACCOUNT_ID.

    Returns
    -------
    user_all_tweet_info : TYPE
        DESCRIPTION.
    reply_data : TYPE
        DESCRIPTION.

    '''
    # print information
    print('-----get twitter reply data-----')
    start_time , end_time = get_starttime_endtime()
    twitter_data = TwitterData(bear_token, start_time, end_time)
    # print information
    print('start time:',start_time)
    print('end time:', end_time)
    user_all_tweet_info = twitter_data.get_user_tweet_info(TWITTER_ACCOUNT_ID)
    reply_data = twitter_data.get_reply_data(user_all_tweet_info) 
    print('-'*30)
    return user_all_tweet_info, reply_data


def _text_preprocessing(df, text):
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    text : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    print('-----data preprocessing-----')
    preprocessing_text = []
    for i in trange(len(text)):
        preprocessing_text.append(remove_mult_spaces(filter_chars(clean_hashtags(strip_all_entities(strip_emoji(text[i]))))))  
    df['preprocess_text'] = preprocessing_text
    df = delete_short_text(df, df['preprocess_text'])
    df = delete_same_text(df,'preprocess_text')
    df.reset_index(drop=True, inplace=True)
    print('-'*30)
    return df


def _english_text_classification(df):
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    dataset_english : TYPE
        DESCRIPTION.

    '''
    dataloader_english_classifier = create_XLNet_dataset(df['conversation_text'], XLNET_MAX_LEN, XLNET_BATCH_SIZE)
    # classification of English text
    model = english_classifer_model()
    english_text_predictions = english_classifier_predictions(model, dataloader_english_classifier, DEVICE)
    # drop elements which class equal 0
    dataset_english = drop_element(df, list(english_text_predictions)) 
    return dataset_english


def _sentiment_analysis(df): 
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.
    daily_sentiment_score : TYPE
        DESCRIPTION.

    '''
    # sentiment analysis sentence 
    dataloader_sentiment_classifier = create_RoBerta_dataset(df, ROBERTA_BATCH_SZIE, ROBERTA_MAX_LEN)  
    model = sentiment_classifer_model()
    sentiment_text_predictions = sentiment_classifier_prediction(model, dataloader_sentiment_classifier, DEVICE)
    df = add_new_column(df, 'sentiment', list(sentiment_text_predictions))
    daily_sentiment_score = sum(sentiment_text_predictions)
    return df, daily_sentiment_score


### for single object of target!!!
def dual_thrust_spot_trading_system(binance_client, strategy, object_of_target, coin1, coin2, k1, k2, order_size = ORDER_SIZE, order_price = None):
    
    while True:
        # get AXS 1d history price 
        hist_price = hist_crypto_price(object_of_target, '1d')
        # get current price
        current_price = current_crypto_price(object_of_target)
        # get trigger price 
        long_price, short_price = strategy.dual_thrust_strategy(hist_price, order_size, k1, k2)
        long_price, short_price = round(long_price, 3), round(short_price, 3)
        # get current time
        utc_time = datetime.now(TIME_ZONE)
        # 
        trigger_price_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        # current time UTC+0 0:00:00, AXS trigger price : long price is {long_price} / short price is {short_price}, current price is {current_price} 
        # sent system mail
        msg = f"Subject:Trading system notification email\nUsing dual thrust spot trading system\n-----------------------\n{object_of_target} trigger long price: ${long_price}\n{object_of_target} trigger short price: ${short_price}\n{object_of_target} current price: ${current_price}" 
        # sent mail to client
        sent_mail(SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS, msg)

        while trigger_price_update_date==current_date:
            current_price = current_crypto_price(object_of_target)
            # discreminate whether touch off trigger 
            if current_price > long_price:
                if order_price == None:
                    order_price = current_price
                # buy signal 
                binance_client.spot_buy(object_of_target, coin1, coin2, order_size, order_price)
                long_price = long_price*100
            
            elif current_price < short_price:
                if order_price == None:
                    order_price = current_price
                # sell signal
                binance_client.spot_sell(object_of_target, coin2, coin1, order_size, order_price)
                short_price = short_price/100
            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            ###############################################################
            print('trigger price update date:', trigger_price_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)
            ###############################################################
            

# single object of target !!!            
def dual_thrust_future_trading_system(binance_client, strategy, object_of_target, coin1, coin2, k1, k2, quantitative_precision = 2, order_size = ORDER_SIZE, order_price = None):
    
    while True:
        # get AXS 1d history price 
        hist_price = hist_crypto_price(object_of_target, '1d')
        # get current price 
        current_price = current_crypto_price(object_of_target)
        # get trigger price 
        long_price, short_price = strategy.dual_thrust_strategy(hist_price, order_size, k1, k2)
        long_price, short_price = round(long_price, 3), round(short_price, 3)
        # get current time
        utc_time = datetime.now(TIME_ZONE)
        # 
        data_update_date = utc_time.strftime("%Y-%m-%d")
        current_date = utc_time.strftime("%Y-%m-%d")
        # system message
        msg = f"Subject:Trading system notification email\nUsing dual thrust future trading system\n-----------------------\n{object_of_target} trigger long price: ${long_price}\n{object_of_target} trigger short price: ${short_price}\n{object_of_target} current price: ${current_price}" 
        # sent mail to client
        sent_mail(SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS, msg)
        
        while data_update_date==current_date:
            current_price = current_crypto_price(object_of_target)
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # check position 
                position = binance_client.future_check_position(symbol= object_of_target)
                if float(position[0]["positionAmt"])<0:
                    # if account has short position, close short position and place the long order
                    binance_client.future_perpetual_close_position(symbol=object_of_target)
                    # place the buy order
                    binance_client.future_perpetual_buy(object_of_target, coin1, coin2, order_size, quantitative_precision, order_price = None)
                    long_price = long_price*100
                else:
                    # place the buy order
                    binance_client.future_perpetual_buy(object_of_target, coin1, coin2, order_size, quantitative_precision, order_price = None)
                    long_price = long_price*100
                    
            # discreminate whether touch off trigger      
            elif current_price < short_price:
                position = binance_client.future_check_position(symbol= object_of_target)
                if float(position[0]["positionAmt"])>0:
                    # if account has long position, close short position and place the short order
                    binance_client.future_perpetual_close_position(symbol=object_of_target)
                    # create sell order
                    binance_client.future_perpetual_sell(object_of_target, coin2, coin1, order_size, quantitative_precision, order_price = None)
                    short_price = short_price/100
                else:
                    # create sell order
                    binance_client.future_perpetual_sell(object_of_target, coin2, coin1, order_size, quantitative_precision, order_price = None)
                    short_price = short_price/100
    
            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            ####################################################################
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)          
            ####################################################################
            
            
def optimized_dual_thrust_future_trading_system(binance_client, strategy, object_of_target, coin1, coin2, quantitative_precision = 0,lookback_r = 5, lookback_s = 4, window_size_s=70, order_size=ORDER_SIZE, p1 = 0.05, p2 = 0.05, k1 = 0.001, k2 = 0.5, order_price = None):
    
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
        user_all_tweet_info, reply_data = _get_twitter_reply()
        # datapreprocessing 
        dataset = _text_preprocessing(reply_data, reply_data['conversation_text'])
        # use english text classifer to filter non-english text
        dataset_english = _english_text_classification(dataset)
        # sentiment analysis and calculate sentiment score
        dataset_english, daily_sentiment_score = _sentiment_analysis(dataset_english)
        # read_csv -> sentiment data
        sentiment_data = pd.read_csv(SENTIMENT_DATA_DIR+f'{before_yest_date}_sentiment_score.csv', index_col=False)
        # sentiment write into csv
        updated_sentiment_data = sentiment_data.append({'date':yest_date, 'sentiment_score':daily_sentiment_score}, ignore_index=True, sort=False)
        # save csv file
        updated_sentiment_data.to_csv(SENTIMENT_DATA_DIR+f'{yest_date}_sentiment_score.csv', index=False)
        dataset_english.to_csv(TEXT_DATA_DIR+f'{yest_date}_text_data.csv', index=False)
        # get AXS 1d history price 
        hist_price = hist_crypto_price(object_of_target, '1d')
        # get current price
        current_price = current_crypto_price(object_of_target)
        # get trigger price 
        long_price, short_price, adjusted_order_size = strategy.optimized_dual_thrust_strategy(hist_price, updated_sentiment_data, 
                                                                                  lookback_r, lookback_s, window_size_s, order_size, 
                                                                                  p1, p2, k1, k2)
        msg = f"Subject:Trading system notification email\nUsing optimize dual thrust future trading system\n-----------------------\n{object_of_target} trigger long price: ${long_price}\n{object_of_target} trigger short price: ${short_price}\n{object_of_target} current price: ${current_price}" 
        # sent mail to client
        sent_mail(SYS_MAIL_ADDRESS, APP_PWD, CLINET_MAIL_ADDRESS, msg)    
        while data_update_date==current_date:
            current_price = current_crypto_price(object_of_target)
            # discreminate whether touch off trigger 
            if current_price > long_price:
                # check position 
                position = binance_client.future_check_position(symbol= object_of_target)
                if float(position[0]["positionAmt"])<0:
                    # if account has short position, close short position and place the long order
                    binance_client.future_perpetual_close_position(symbol=object_of_target)
                    # place the buy order
                    binance_client.future_perpetual_buy(object_of_target, coin1, coin2, adjusted_order_size, quantitative_precision, order_price = None)
                    long_price = long_price*100
                else:
                    # place the buy order
                    binance_client.future_perpetual_buy(object_of_target, coin1, coin2, adjusted_order_size, quantitative_precision, order_price = None)
                    long_price = long_price*100 
            # discreminate whether touch off trigger      
            elif current_price < short_price:
                position = binance_client.future_check_position(symbol= object_of_target)
                if float(position[0]["positionAmt"])>0:
                    # if account has long position, close short position and place the short order
                    binance_client.future_perpetual_close_position(symbol=object_of_target)
                    # create sell order
                    binance_client.future_perpetual_sell(object_of_target, coin2, coin1, adjusted_order_size, quantitative_precision, order_price = None)
                    short_price = short_price/100
                else:
                    # create sell order
                    binance_client.future_perpetual_sell(object_of_target, coin2, coin1, adjusted_order_size, quantitative_precision, order_price = None)
                    short_price = short_price/100
    
            time.sleep(20)
            utc_time = datetime.now(TIME_ZONE)
            current_date = utc_time.strftime("%Y-%m-%d")
            #####################################################################
            print('data update date:', data_update_date)
            print('current date:', current_date)
            print('long trigger price:', long_price)
            print('short trigger price:', short_price)
            print('current time:', utc_time.strftime("%Y-%m-%d %H:%M:%S"))
            print('AXS current price:', current_price)
            print('-'*30)     
            #####################################################################

    
if __name__ == '__main__':   
    binance_transaction = Binance_transaction(api_key = BINANCE_KEY, api_secret = BINANCE_SECRET, sys_mail_address = SYS_MAIL_ADDRESS, app_pwd = APP_PWD, clinet_mail_adress = CLINET_MAIL_ADDRESS)
    strategy = Strategy()
    #dual_thrust_spot_trading_system(binance_transaction, strategy, 'AXSUSDT', 'AXS', "USDT", 0.5, 0.5, order_size = ORDER_SIZE, order_price = None)
    #dual_thrust_future_trading_system(binance_transaction, strategy, 'AXSUSDT', 'AXS', "USDT", 0.001, 0.1, 0, order_size = ORDER_SIZE, order_price = None)
    optimized_dual_thrust_future_trading_system(binance_transaction, strategy, 'AXSUSDT', 'AXS', 'USDT')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    