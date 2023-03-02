#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 11:59:04 2023

@author: welcome870117
"""
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler, Dataset
from keras.utils import pad_sequences
from transformers import XLNetTokenizer, RobertaModel, RobertaTokenizer


class RoBertaData(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.text = dataframe.preprocess_text
        self.targets = [0 for _ in range(len(self.data))]
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            truncation=True,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]


        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'targets': torch.tensor(self.targets[index], dtype=torch.float)
        }    


def create_RoBerta_dataset(df, batch_size, MAX_LEN):
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base', truncation=True, do_lower_case=True)
    dataset = RoBertaData(df, tokenizer, MAX_LEN)
    params = {'batch_size': batch_size,
                    'shuffle': False,
                    'num_workers': 0
                    }
    dataloader = DataLoader(dataset, **params)
    return dataloader
    

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


