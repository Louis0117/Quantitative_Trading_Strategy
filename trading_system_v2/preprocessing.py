#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 21:19:46 2023

@author: welcome870117
"""

import re , string
import emoji


# Clean emojis from text
def strip_emoji(text):
    '''

    Parameters
    ----------
    text : str
        The text which need to remove emoji

    Returns
    -------
    str
        the text without emoji.

    '''
       
    '''
    re : A module for regular expressions. / re is the abbreviation of regular expression, which means regular expression.
    re.sub : Sub is an abbreviation for substitute / re.sub(replace object, replace target, string)
    emoji.get_emoji_regexp() : get the regular expression of emoji
    '''
    
    return re.sub(emoji.get_emoji_regexp(), r"", text) # remove emoji


# Remove punctuations, links, mentions and \r\n new line characters
def strip_all_entities(text): 
    '''

    Parameters
    ----------
    text : str
        The text which need to remove punctuations, links, mentions and \r\n new line characters.

    Returns
    -------
    text : str
        The text without punctuations, links, mentions, \r\n new line characters.

    '''
    
    #remove \n and \r and lowercase
    text = text.replace('\r', '').replace('\n', ' ').replace('\n', ' ').lower() 
    #remove links and mentions
    text = re.sub(r"(?:\@|https?\://)\S+", "", text) 
    #remove non utf8/ascii characters such as '\x9a\x91\x97\x9a\x97' 
    text = re.sub(r'\\[a-z0-9][a-z0-9][a-z0-9][a-z0-9][a-z0-9]',r'', text) 
    banned_list= string.punctuation + 'Ã'+'±'+'ã'+'¼'+'â'+'»'+'§'
    table = str.maketrans('', '', banned_list)
    text = text.translate(table)
    return text


# clean hashtags at the end of the sentence, and keep those in the middle of the sentence by removing just the # symbol
def clean_hashtags(text):
    '''
    
    Parameters
    ----------
    text : str
        The text which need to remove hashtag.

    Returns
    -------
    text : str
        The text without hashtag.
    
    '''
    
    # remove last hashtags
    text = " ".join(word.strip() for word in re.split('#(?!(?:hashtag)\b)[\w-]+(?=(?:\s+#[\w-]+)*\s*$)', text)) 
    # remove hashtags symbol from words in the middle of the sentence
    text = " ".join(word.strip() for word in re.split('#|_', text)) 
    return text


#Filter special characters such as & and $ present in some words
def filter_chars(text):
    '''
    
    Parameters
    ----------
    text : str
        The text which need to remove special characters such as & and $ present in some words.

    Returns
    -------
    text : str
        The text without hashtag.
        
    '''
    
    sent = []
    for word in text.split(' '):
        if ('$' in word) | ('&' in word):
            sent.append('')
        else:
            sent.append(word)
    return ' '.join(sent)


# remove multiple spaces
def remove_mult_spaces(text): 
    return re.sub("\s\s+" , " ", text)


# delete sentence length short than 5 words
def delete_short_text(dataset, data):
    '''

    Parameters
    ----------
    dataset : dataframe
        complete text dataset  
    data : Series
        text data which have done data preprocessing 

    Returns
    -------
    dataset : dataframe
        complete text dataset 

    '''
    
    for i in range(len(data)):
       text = data[i].split(" ")
       if len(text)<5:
         dataset = dataset.drop(i,axis=0)
    dataset.reset_index(inplace=True, drop=True)
    return dataset


def delete_same_text(df, subset):
    '''

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    subset : TYPE
        DESCRIPTION.
    Returns

    -------
    new_df : TYPE
        DESCRIPTION.

    '''

    new_df = df.drop_duplicates(subset = [subset])
    return new_df