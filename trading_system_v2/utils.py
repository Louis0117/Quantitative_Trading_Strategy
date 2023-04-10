#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:44:24 2023

@author: welcome870117
"""

from tqdm import tqdm, trange
import datetime
from datetime import timedelta

# drop element according data
def drop_element(df, data):
    '''    

    Parameters
    ----------
    df : dataframe
        A dataframe which need to drop element
    data : list
        The basis for dataframe to delete element

    Returns
    -------
    new_df : dataframe
        A dataframe which have done drop element

    '''
    
    for i in trange(len(data)):
        if data[i] == 0 :
           df.drop(i, axis=0, inplace=False)
    df.reset_index(inplace=True, drop=True)
    return df


def add_new_column(df, column_name, data):
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    column_name : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    df[column_name] = data
    return df

# get start time, end time
def get_starttime_endtime():

    # print('UTC+0 time:',datetime.datetime.utcnow().isoformat())
    # getting current time, data type: str
    current_time = str(datetime.datetime.utcnow()+timedelta(days=-1))[:10]
    current_time = current_time.split('-')
    year = int(current_time[0])
    month = int(current_time[1])
    day = int(current_time[2])
    # get start time 
    start_time = datetime.datetime(year, month, day, 0, 0, 0, 0, datetime.timezone.utc)
    # get end time
    end_time = datetime.datetime(year, month, day, 23, 59, 59, 0, datetime.timezone.utc)
    return start_time, end_time
    
    '''
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
    '''

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




