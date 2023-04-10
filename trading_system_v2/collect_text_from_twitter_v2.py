#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 11:19:31 2023

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


class TwitterData :
    def __init__(self, bear_token, start_time, end_time):
        self.bear_token = bear_token
        self.start_time = start_time
        self.end_time = end_time
        self.tweepy_client = tweepy.Client(bearer_token=bear_token)
        self.twarc2_client = Twarc2(bearer_token=bear_token)
        
    # get user id in twitter
    def get_user_id(self, screen_name):
        user = self.tweepy_client.get_user(username=screen_name)  # getting user information
        user_id = user.data.id  # getting user id
        return user_id
    
    def get_user_tweet_info(self, user_id):     
        # getting user tweet information
        user_all_tweet = self.tweepy_client.get_users_tweets(id=user_id ,end_time = self.end_time ,tweet_fields=['lang','text','conversation_id','created_at','public_metrics'] , exclude = ['retweets'] , max_results=100)    
        
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
            
        df = pd.DataFrame({'created_time':time,'text':tweet_text,'language':language,'conversation_id':conversation_id,'retweet_count':retweet_count,'reply_count':reply_count,'like_count':like_count,'quote_count':quote_count})
        return df
    
    def _get_reply(self, conversation_id):
        query = "conversation_id:"+conversation_id
        # get user comments information under tweets
        search_results = self.twarc2_client.search_all(query=query, start_time=self.start_time, end_time=self.end_time, max_results=100) 
        return search_results
    
    def get_reply_data(self, df):     
        conversation_time = []
        conversation_text = []
        print('Get twitter user reply text')
        for i in trange(len(df)):
            # get conversation id from dataset
            conversation_id = str(df['conversation_id'][i])
            # get user reply information under tweets
            conversation_data = self._get_reply(conversation_id)
            for page in conversation_data:
                #  function flatten() for "flattening" a result set, including all expansions inline.
                result = expansions.flatten(page)         
                for tweet in result:
                    # json.dump() Serialize json format data to Python's related data types
                    conversation_time.append(json.dumps(tweet['created_at']))
                    conversation_text.append(json.dumps(tweet['text']))    
        
        df = pd.DataFrame({'conversation_time':conversation_time,'conversation_text':conversation_text})               
        return df