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
from transformers import XLNetForSequenceClassification, RobertaModel, RobertaTokenizer


# Roberta model architecture
class RobertaClass(torch.nn.Module):
    def __init__(self):
        super(RobertaClass, self).__init__()
        self.l1 = RobertaModel.from_pretrained("roberta-base")
        self.pre_classifier = torch.nn.Linear(768, 768)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768, 3)

    def forward(self, input_ids, attention_mask, token_type_ids):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


# load english text classifier
def english_classifer_model():
    # load XLNet pretrain model
    model = XLNetForSequenceClassification.from_pretrained("xlnet-base-cased", num_labels=2)
    # Load the trained model parameters
    model.load_state_dict(torch.load('/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/english_classifer.pth', map_location=torch.device('cpu')))
    return model

# load sentiment analysis model
def sentiment_classifer_model():
    # load Roberta pretrain model
    model = RobertaClass()
    # Load the trained model parameters
    model.load_state_dict(torch.load('/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/sentiment_analysis_classifier.pth', map_location=torch.device('cpu')))
    return model


# English, non-English text classification
def english_classifier_predictions(model, dataloader, device):
    # Put model in evaluation mode
    model.eval() 
    predictions = []
    for batch in  dataloader:
        b_input_ids, b_input_mask, b_labels = batch
        # Telling the model not to compute or store gradients, saving memory and speeding up prediction
        with torch.no_grad():
          # Forward pass, calculate logit predictions
          outputs = model(b_input_ids, token_type_ids=None, attention_mask=b_input_mask)
          logits = outputs[0]
          # Move logits and labels to CPU
          logits = logits.detach().cpu().numpy() 
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


# sentiment analysis
def sentiment_classifier_prediction(model, dataloader, device):
    prediction = None
    # Put model in evaluation mode
    model.eval()
    with torch.no_grad():
        for _, data in tqdm(enumerate(dataloader, 0)):
            ids = data['ids'].to(device, dtype = torch.long)
            mask = data['mask'].to(device, dtype = torch.long)
            token_type_ids = data['token_type_ids'].to(device, dtype=torch.long)
            outputs = model(ids, mask, token_type_ids).squeeze()
            # get prediction result
            big_val, big_idx = torch.max(outputs.data, dim=1)
            if prediction == None:
               prediction = big_idx          
            else:
              prediction = torch.cat((prediction, big_idx))
    prediction = list(prediction.detach().cpu().numpy() )
    # convert label 2 to -1
    # * I think it has better code to implement 
    for i in range(len(prediction)):
        if prediction[i] == 2:
            prediction[i] = -1   
    return prediction           