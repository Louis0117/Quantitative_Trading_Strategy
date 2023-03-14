#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 13:07:16 2023

@author: welcome870117
"""

import tweepy
import json
import pandas as pd
import datetime
import time
import calendar
from tqdm import tqdm, trange
from twarc import Twarc2, expansions



# client initialized, you will be ready to start using the various functions in tweepy.
def connect_tweepy_client(BEARER_TOKEN):   
    '''   
    Returns
    -------
    client: The client is initialized and used to call the twitter API
    
    '''
    client = tweepy.Client(bearer_token=BEARER_TOKEN) # input bearer_token is enough   
    return client


# client initialized, you will be ready to start using the various functions in twarc2.
def connect_twarc2_client(BEARER_TOKEN):
    '''   
    Returns
    -------
    client: The client is initialized and used to call the twitter API
    
    '''
    client = Twarc2(bearer_token=BEARER_TOKEN)  # input bearer_token is enough
    return client


# get start time, end time
def get_starttime_endtime():

    # print('UTC+0 time:',datetime.datetime.utcnow().isoformat())
    
    # getting current time, data type: str
    current_time = str(datetime.datetime.utcnow().isoformat())[:10]
    # split time str by '-'
    current_time = current_time.split('-')
    # Extract year data
    year = int(current_time[0])
    # Extract month data
    month = int(current_time[1])
    # Extract day data
    day = int(current_time[2])-1
    # get start time 
    start_time = datetime.datetime(year, month, day, 0, 0, 0, 0, datetime.timezone.utc)
    # get end time
    end_time = datetime.datetime(year, month, day, 23, 59, 59, 0, datetime.timezone.utc)
    return start_time , end_time


# get user id in twitter
def getting_user_id(client, screen_name):
    '''
    Get twitter user account id
    
    Parameters
    ----------
    client: created by function 'connect_tweepy_client' 
    screen_name: username in twitter, e.g., elonmusk
    Returns
    -------
    user_id: user id in twitter
    
    '''
    user = client.get_user(username=screen_name)  # getting user information
    user_id = user.data.id  # getting user id
    return user_id


# get user tweet&reply information
def get_user_tweet_info(client, user_id, end_time):

    '''
    get target user tweets&reply
    
    Parameters
    ----------
    client: created by function 'connect_tweepy_client' 
    user_id: twitter id of the target account, get from function 'getting_user_id'
    end_time: The newest or most recent UTC timestamp from which the Tweets will be provided. format->YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339)
    
    Returns
    -------
    dataset: a dataframe which contains each tweets create time, tweet content, language, conversation id, retweet count, reply count, like count, quote count
    '''
    # getting user tweet information
    user_all_tweet = client.get_users_tweets(id=user_id ,end_time = end_time ,tweet_fields=['lang','text','conversation_id','created_at','public_metrics'] , exclude = ['retweets'] , max_results=100)    
    
    conversation_id = []
    tweet_text = []
    time = []
    tweetinformation = []
    language = []
    retweet_count = []
    reply_count = []
    like_count = []
    quote_count = []
    
    for tweet in user_all_tweet.data:

        tweet_text.append(tweet.text)
        time.append(tweet.created_at)
        tweetinformation.append(tweet.public_metrics)
        conversation_id.append(tweet.conversation_id)
        language.append(tweet.lang)
            
    for tweet_info in tweetinformation:
        retweet_count.append(tweet_info['retweet_count'])
        reply_count.append(tweet_info['reply_count'])
        like_count.append(tweet_info['like_count'])
        quote_count.append(tweet_info['quote_count'])
        
    dataset = pd.DataFrame({'created_time':time,'text':tweet_text,'language':language,'conversation_id':conversation_id,'retweet_count':retweet_count,'reply_count':reply_count,'like_count':like_count,'quote_count':quote_count})
    return dataset


def _get_reply(client, start_time, end_time, conversation_id):
    '''
    get user reply under tweets
    Parameters
    ----------
    client: created by function 'connect_twarc2_client'
    start_time: Return all tweets after this time (UTC datetime).
    end_time: Return all tweets before this time (UTC datetime).
    conversation_id: Each tweet has its own unique id number, get from function 'get_user_tweet'
    Returns
    -------
    search_results: user reply information under tweets
    '''
    
    query = "conversation_id:"+conversation_id
    # get user comments information under tweets
    search_results = client.search_all(query=query, start_time=start_time, end_time=end_time, max_results=100) 
    return search_results


def get_reply_data(client, dataset, start_time, end_time):
    '''
    Take Twitter user reply data from json format and organize it into dataframe
    Parameters
    ----------
    client: created by function 'connect_twarc2_client'
    dataset: a dataframe which has consersation_id column
    start_time: Return all tweets after this time (UTC datetime).
    end_time: Return all tweets before this time (UTC datetime).
    Returns
    -------
    dataset: a dataframe which contains conversation time, conversation text column
    '''
    
    conversation_time = []
    conversation_text = []
    print('Get twitter user reply text')
    for i in trange(len(dataset)):
        # get conversation id from dataset
        conversation_id = str(dataset['conversation_id'][i])
        # get user reply information under tweets
        conversation_data = _get_reply(client, start_time, end_time, conversation_id)
        for page in conversation_data:
            #  function flatten() for "flattening" a result set, including all expansions inline.
            result = expansions.flatten(page)         
            for tweet in result:
                # json.dump() Serialize json format data to Python's related data types
                conversation_time.append(json.dumps(tweet['created_at']))
                conversation_text.append(json.dumps(tweet['text']))    
    
    dataset = pd.DataFrame({'conversation_time':conversation_time,'conversation_text':conversation_text})               
    return dataset

# filter different date data
def different_date_filter(dataset , start_time):
    '''

    Parameters
    ----------
    dataset : dataframe
        user reply dataset
    start_time : datetime.datetime
        today's  date
        
    Returns
    -------
    dataset : dataframe
        
    
    '''
    start_time = str(start_time)[:10]
    for i in range(len(dataset['conversation_time'])):
       date = str(dataset['conversation_time'][i])[1:11]
       if date!=start_time:
           dataset.drop(i,inplace=True)
    dataset.reset_index(drop=True, inplace=True)
    return dataset