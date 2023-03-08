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
from sent_email import sent_mail

SYS_MAIL_ADDRESS = ''
APP_PWD = ''

# Dual Thrust strategy - long only
def binance_trading(buying_signal , selling_signal , current_price, order_size):
    '''

    Parameters
    ----------
    buying_signal : bool
        True -> buy cryptocurrencies / False -> do nothing
    selling_signal : bool
        True -> sell cryptocurrencies / False -> do nothing
    current_price : float
        current cryptocurrencies price
    order_size : float
        The size of the transaction required

    Returns
    -------
    int
        Unexecuted transaction, return 0

    '''
    # Binance API key
    KEY = ''
    SECRET = ''
    # build binance connect
    client = Client(KEY, SECRET)
    # Get the number of axs in account
    account_axs = round(float(client.get_asset_balance(asset = 'AXS')['free']),2)
    print('account axs:',account_axs)
    # Get the number of usdt in account
    account_usdt = round(float(client.get_asset_balance(asset = 'USDT')['free']),2)
    print('account usdt:',account_usdt)
    
    
    if buying_signal:
        # Determine whether the amount of usdt in the account is greater than the order size
        if account_usdt<order_size:
            print('please buy usdt.....')
            # The content of the system notification letter
            msg = "Subject:Trading system notification email\nA buy signal is generated, but USDT is insufficient to buy"
            # sent mail to client
            sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            return 0
        else:
            # calculate quantity of buying coins
            buying_quantity = round(order_size/current_price)
            # place a limit buying order
            order = client.order_limit_buy(symbol ='AXSUSDT', quantity = buying_quantity, price = current_price)
            print('buy axs.....')
            # The content of the system notification letter
            msg = f"Subject:Trading system notification email\nThe trading system place a buying order at the AXS cryptocurrency price {current_price} with a total value of {order_size} USDT"
            # sent mail to client
            sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            
    elif selling_signal:
        # Determine whether the AXS value in the account is greater than 10 usdt (the minima transation value = 10)
        if account_axs*current_price<10:
            print('please buy axs.....')
            # the content of the system notification letter
            msg = "Subject:Trading system notification email\nA sell signal is generated, but the AXS is insufficient and cannot be sold"
            # sent mail to client
            sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            return 0
        else:
            # calculate quantity of selling coins
            selling_quantity = round(account_axs*0.999,2)
            # place a limit selling order
            client.order_limit_sell(symbol ='AXSUSDT', quantity = selling_quantity, price = current_price)
            print('sell axs.....')
            # the content of the system notification letter
            msg = f"Subject:Trading system notification email\nThe trading system place a selling order at the AXS cryptocurrency price {current_price} with a total value of {order_size} USDT"
            # sent mail to client
            sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)