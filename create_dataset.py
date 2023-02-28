#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 11:59:04 2023

@author: welcome870117
"""
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from keras.utils import pad_sequences
from transformers import XLNetTokenizer


def create_XLNet_dataset(data, max_len, batch_size):
    '''

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    max_len : TYPE
        DESCRIPTION.
    batch_size : TYPE
        DESCRIPTION.

    Returns
    -------
    dataloader : TYPE
        DESCRIPTION.

    '''
    
    data = data.values
    # add special token
    data = [sentence + " [SEP] [CLS]" for sentence in data]
    # 
    tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased', do_lower_case=True)
    tokenized_data = [tokenizer.tokenize(sent) for sent in data]
    
    # Use the XLNet tokenizer to convert the tokens to their index numbers in the XLNet vocabulary
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_data]
    #
    input_ids = pad_sequences(input_ids, maxlen=max_len, dtype="long", truncating="post", padding="post")
    # Create attention masks
    attention_masks = []
    # Create a mask of 1s for each token followed by 0s for padding
    for seq in input_ids:
      seq_mask = [float(i>0) for i in seq]
      attention_masks.append(seq_mask)
    label = [0 for i in range(len(attention_masks))]  
    # Convert all of our data into torch tensors, the required datatype for our model
    tensor_input_ids = torch.tensor(input_ids)
    tensor_test_masks = torch.tensor(attention_masks)
    label = torch.tensor(label)
    # create dataset
    dataset = TensorDataset(tensor_input_ids, tensor_test_masks, label)
    dataset_sampler = SequentialSampler(dataset)
    dataloader = DataLoader(dataset, sampler=dataset_sampler, batch_size=batch_size)
    return dataloader

    