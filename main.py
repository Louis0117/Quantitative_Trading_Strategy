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
# import python file
from collect_text_from_twitter import connect_tweepy_client, get_starttime_endtime, get_user_tweet_info, connect_twarc2_client, get_reply_data, different_date_filter
from preprocessing import strip_emoji, strip_all_entities, clean_hashtags, filter_chars, remove_mult_spaces, delete_short_text
from create_dataset import create_XLNet_dataset, create_RoBerta_dataset
from NN_model import English_classifer_model, get_predictions
from utils import drop_element


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
    english_classifer_model = English_classifer_model()
    english_text_predictions = get_predictions(english_classifer_model, dataloader_english_classifier, device)
    #%%
    # drop elements which class equal 0
    dataset_english = drop_element(dataset, list(english_text_predictions)) 
    #%%
    # sentiment analysis sentence 
    dataloader_english_classifier = create_RoBerta_dataset(dataset, 8, 256)
        
    