#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 17:36:57 2023

@author: welcome870117
"""

# trade on Binance
# SDK document: https://python-binance.readthedocs.io/en/latest/account.html(unofficial)
# round(): return float 四捨五入值 

from binance.client import Client


# long only
def binance_trading(buying_signal , selling_signal , current_price, order_size):
    '''

    Parameters
    ----------
    buying_price : TYPE
        DESCRIPTION.
    selling_price : TYPE
        DESCRIPTION.
    order_size : TYPE
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    '''
    KEY = ''
    SECRET = ''
    # build binance connect
    client = Client(KEY, SECRET)
    # 
    account_axs = round(float(client.get_asset_balance(asset = 'AXS')['free']),2)
    print('account axs:',account_axs)
    # get usdt in account
    account_usdt = round(float(client.get_asset_balance(asset = 'USDT')['free']),2)
    print('account usdt:',account_usdt)
    
    if buying_signal:
        if account_usdt<order_size:
            print('please buy usdt.....')
            return 0
        else:
            # calculate quantity of coins
            buying_quantity = round(order_size/current_price)
            # place a limit buying order
            order = client.order_limit_buy(symbol ='AXSUSDT', quantity = buying_quantity, price = current_price)
            print('buy axs.....')
            
    elif selling_signal:
        if account_axs*current_price<10:
            print('please buy axs.....')
            return 0
        else:
            #
            selling_quantity = round(account_axs*0.999,2)
            # place a limit selling order
            client.order_limit_sell(symbol ='AXSUSDT', quantity = selling_quantity, price = current_price)
            print('sell axs.....')
    