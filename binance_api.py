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
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import math 


# Dual Thrust strategy - long only
def binance_spot_trading(SYS_MAIL_ADDRESS,APP_PWD, api_key, api_secret, buying_signal , selling_signal , current_price, order_size):
    '''

    Parameters
    ----------
    api_key : TYPE
        DESCRIPTION.
    api_secret : TYPE
        DESCRIPTION.
    buying_signal : TYPE
        DESCRIPTION.
    selling_signal : TYPE
        DESCRIPTION.
    current_price : TYPE
        DESCRIPTION.
    order_size : TYPE
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    '''
    # build binance connect
    client = Client(api_key, api_secret)
    # Get the number of axs in account
    account_axs = float(client.get_asset_balance(asset = 'AXS')['free'])
    print('account axs:',account_axs)
    # Get the number of usdt in account
    account_usdt = float(client.get_asset_balance(asset = 'USDT')['free'])
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
            try:
                # calculate quantity of buying coins
                buying_quantity = math.floor((order_size/current_price)*100)/100.0
                # place a limit buying order
                order = client.order_limit_buy(symbol ='AXSUSDT', quantity = buying_quantity, price = current_price)
                print('buy axs spot.....')
                # The content of the system notification letter
                msg = f"Subject:Trading system notification email\nThe trading system place a buying order at the AXS cryptocurrency price {current_price} with a total value of {order_size} USDT"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')

            
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
            try:
                # calculate quantity of selling coins
                selling_quantity = math.floor(account_axs*100)/100.0
                # place a limit selling order
                client.order_limit_sell(symbol ='AXSUSDT', quantity = selling_quantity, price = current_price)
                print('sell axs spot.....')
                # the content of the system notification letter
                msg = f"Subject:Trading system notification email\nThe trading system place a selling order at the AXS cryptocurrency price {current_price} with a total value of {order_size} USDT"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')

            
            
# place perpetual contract order 
def binance_future_perpetual_order(SYS_MAIL_ADDRESS, APP_PWD, api_key, api_secret, symbol, order_size, side, leverage, price=None, stop_loss=None, take_profit=None):
    '''

    Parameters
    ----------
    api_key : TYPE
        DESCRIPTION.
    api_secret : TYPE
        DESCRIPTION.
    symbol : TYPE
        DESCRIPTION.
    order_size : TYPE
        DESCRIPTION.
    side : TYPE
        DESCRIPTION.
    leverage : TYPE
        DESCRIPTION.
    price : TYPE, optional
        DESCRIPTION. The default is None.
    stop_loss : TYPE, optional
        DESCRIPTION. The default is None.
    take_profit : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    '''
    # Create a Binance API client object
    client = Client(api_key, api_secret)    
    # Get the symbol's current price
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])
    quantity = math.floor(order_size/current_price)
    total_value = current_price*quantity
    # Set the order type based on the parameters provided
    if price is not None:
        order_type = Client.ORDER_TYPE_LIMIT
    else:
        order_type = Client.ORDER_TYPE_MARKET
    # Place the order
    if side == 'BUY':
        if order_type == Client.ORDER_TYPE_LIMIT:
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity,
                    price=price,
                    timeInForce=Client.TIME_IN_FORCE_GTC
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a long limit price futures order, at the price of one AXS {current_price} usdt, establish a position of {quantity} AXS with a total value of {total_value} usdt, and the leverage multiple is {leverage}"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')
        else:
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a long market price futures order, at the price of one AXS {current_price} usdt, establish a position of {quantity} AXS with a total value of {total_value} usdt, and the leverage multiple is {leverage}"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')
                
    elif side == 'SELL':
        if order_type == Client.ORDER_TYPE_LIMIT:
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity,
                    price=price,
                    timeInForce=Client.TIME_IN_FORCE_GTC
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a short limit price futures order, at the price of one AXS {current_price} usdt, establish a position of {quantity} AXS with a total value of {total_value} usdt, and the leverage multiple is {leverage}"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')
        else:
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a short market price futures order, at the price of one AXS {current_price} usdt, establish a position of {quantity} AXS with a total value of {total_value} usdt, and the leverage multiple is {leverage}"
                # sent mail to client
                sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
            except Exception as e:
                print(f'Unexpected error: {e}')   


# close position
def binance_future_perpetual_close_position(SYS_MAIL_ADDRESS, APP_PWD, api_key, api_secret, symbol):
    '''

    Parameters
    ----------
    api_keys : TYPE
        DESCRIPTION.
    api_secret : TYPE
        DESCRIPTION.
    symbol : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    client = Client(api_key, api_secret)
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker['price'])
    position = client.futures_position_information(symbol=symbol)
    realized_profit = float(position[0]["positionAmt"])*float(position[0]["unRealizedProfit"])*float(position[0]["entryPrice"])
    print('realized_profit:', realized_profit)
    realized_profit = round(realized_profit,2)
    print('realized_profit:', realized_profit)
    # Determine the current position direction
    if float(position[0]["positionAmt"])>0 :
        side = "SELL"
    else:
        side = "BUY"
    # place the order to close position
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=abs(float(position[0]["positionAmt"]))
        )
        print('close position successfully!')
        msg = f"Subject:Trading system notification email\nThe trading system close position, at the price of one AXS {current_price} usdt, total profit is {realized_profit} usdt"
        # sent mail to client
        sent_mail(SYS_MAIL_ADDRESS, APP_PWD, 'welcome870117@gmail.com', msg)
    except BinanceAPIException as e:
        print(f'Error message: {e.message}')
    except BinanceOrderException as e:
        print(f'Error code: {e.code}, message: {e.message}')
    except Exception as e:
        print(f'Unexpected error: {e}')


def binance_future_check_position(api_key, api_secret, symbol=None):
    '''

    Parameters
    ----------
    api_keys : TYPE
        DESCRIPTION.
    api_secret : TYPE
        DESCRIPTION.
    symbol : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    position : TYPE
        DESCRIPTION.

    '''
    client = Client(api_key, api_secret)
    if symbol is not None:
        position = client.futures_position_information(symbol=symbol)
    else:
        position = client.futures_position_information() 
    return position


def binance_future_adjust_leverage(api_key, api_secret, symbol, leverage):
    client = Client(api_key, api_secret)
    client.futures_change_leverage(symbol=symbol, leverage=leverage)