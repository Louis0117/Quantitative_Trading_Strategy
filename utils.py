#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:44:24 2023

@author: welcome870117
"""

from tqdm import tqdm, trange

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