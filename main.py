#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 12:22:05 2023

@author: welcome870117
"""

# import package

# import python file
from collect_text_from_twitter import connect_tweepy_client, get_starttime_endtime, get_user_tweet_info, connect_twarc2_client, get_reply_data, different_date_filter



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
    

if __name__ == '__main__':
    #pass
    # test
    user_all_tweet_info, reply_data = getting_twitter_daily(BEAR_TOKEN, TWARC2_BEARER_TOKEN, TWITTER_COUNT_ID)