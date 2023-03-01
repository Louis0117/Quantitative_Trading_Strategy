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
    df : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.

    Returns
    -------
    new_df : TYPE
        DESCRIPTION.

    '''
    for i in trange(len(data)):
        if data[i] == 0 :
           new_df  = df.drop(i, axis=0, inplace=False)
    new_df.reset_index(inplace=True, drop=True)
    return new_df