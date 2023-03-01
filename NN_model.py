#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 11:01:37 2023

@author: welcome870117
"""

# import package
import torch
import numpy as np
from tqdm import tqdm, trange
from transformers import XLNetForSequenceClassification



# load english text classifier
def English_classifer_model():
    model = XLNetForSequenceClassification.from_pretrained("xlnet-base-cased", num_labels=2)
    model.load_state_dict(torch.load('/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/English_classifer.pth', map_location=torch.device('cpu')))
    return model

# load sentiment analysis model



# sentiment analysis
def get_predictions(model, dataloader, device):
    # Put model in evaluation mode
    model.eval() 
    # 
    predictions = []
    #
    for batch in  dataloader:
        #batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        # Telling the model not to compute or store gradients, saving memory and speeding up prediction
        with torch.no_grad():
          # Forward pass, calculate logit predictions
          outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
          logits = outputs[0]
          # Move logits and labels to CPU
          logits = logits.detach().cpu().numpy() 
          #
          #print('logits', logits)
          #print('logit_type:', type(logits))
          pred = np.argmax(logits, axis=1)
          # Store predictions and true labels
          predictions.append(pred)
    
    # traverse English text prediction
    for i in trange(len(predictions)):
        if i == 0:
            predictions_stack = predictions[0]
        else:
            predictions_stack = np.hstack((predictions_stack, predictions[i]))
    return predictions_stack
             





