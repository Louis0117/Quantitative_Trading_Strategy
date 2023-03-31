#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 13:59:46 2023

@author: welcome870117
"""

# import python file
from sent_email import sent_mail

# import python package
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import math 


class Binance_transaction:
    def __init__(self, api_key, api_secret, sys_mail_address, app_pwd, clinet_mail_adress):
        self.sys_mail_address = sys_mail_address
        self.app_pwd = app_pwd
        self.api_key = api_key
        self.api_secret = api_secret
        self.clinet_mail_adress = clinet_mail_adress
        # build binance connect
        self.binance_client = Client(self.api_key, self.api_secret)
    
    #### only limit order!!!        
    def spot_buy(self, symbol, coin_buy, coin_sell, order_size, order_price):
        # (ps. only usdt, busd, usdc -> other crypto)
        # Get the number of axs in account
        account_coin_buy = float(self.binance_client.get_asset_balance(asset = coin_buy)['free'])
        print(f'account {coin_buy}:',account_coin_buy)
        # Get the number of usdt in account
        account_coin_sell = float(self.binance_client.get_asset_balance(asset = coin_sell)['free'])
        print(f'account {coin_sell}:',account_coin_sell)
        
        try:
            # calculate quantity of buying coins
            buying_quantity = math.floor((order_size/order_price)*100)/100.0
            # place a limit buying order
            order = self.binance_client.order_limit_buy(symbol = symbol, quantity = buying_quantity, price = order_price)
            print(f'place {coin_buy} spot buying order.....')
            # The content of the system notification letter
            msg = f"Subject:Trading system notification email\nThe trading system place a buying order at the {coin_buy} cryptocurrency price {order_price} with a total value of {order_size} {coin_sell}"
            # sent mail to client
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceAPIException as e:
            print(f'Error message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceOrderException as e:
            print(f'Error code: {e.code}, message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except Exception as e:
            print(f'Unexpected error: {e}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
    
    #### only limit order!!!
    def spot_sell(self, symbol, coin_buy, coin_sell, order_size, order_price):
        # Get the number of axs in account
        account_coin_buy = float(self.binance_client.get_asset_balance(asset = coin_buy)['free'])
        print(f'account {coin_buy}:',account_coin_buy)
        # Get the number of usdt in account
        account_coin_sell = float(self.binance_client.get_asset_balance(asset = coin_sell)['free'])
        print(f'account {coin_sell}:',account_coin_sell)
        # Determine whether the AXS value in the account is greater than 10 usdt (the minima transation value = 10)
        
        try:
            if order_size == -1:
                # calculate quantity of selling coins
                selling_quantity = math.floor(account_coin_sell*100)/100.0
                print('selling_quantity:', selling_quantity)
            else:
                selling_quantity = math.floor(order_size*100)/100.0
            # place a limit selling order
            self.binance_client.order_limit_sell(symbol =symbol, quantity = selling_quantity, price = order_price)
            print('place {coin_sell} spot selling order.....')
            # the content of the system notification letter
            msg = f"Subject:Trading system notification email\nThe trading system place a selling order at the {coin_sell} cryptocurrency price {order_price} USDT"
            # sent mail to client
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceAPIException as e:
            print(f'Error message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceOrderException as e:
            print(f'Error code: {e.code}, message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except Exception as e:
            print(f'Unexpected error: {e}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
    
    ### The limit order function has not been tested
    ### XXXUSDT, XXXUSDC, XXXBUSD only!!!
    def future_perpetual_buy(self, symbol, coin_buy, coin_sell, order_size, quantitative_precision, order_price = None):
        # Create a Binance API client object
        #client = Client(api_key, api_secret)    
        # Get the symbol's current price
        ticker = self.binance_client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        # different symbol quantity precision is different
        # given quantity precision
        q_p = pow(10,quantitative_precision)
        # Set the order type based on the parameters provided
        if order_price is not None:
            order_type = Client.ORDER_TYPE_LIMIT
            quantity = math.floor((order_size/order_price)*int(q_p))/float(q_p)
            total_value = order_price*quantity
        else:
            order_type = Client.ORDER_TYPE_MARKET
            quantity = math.floor((order_size/current_price)*int(q_p))/float(q_p)
            total_value = current_price*quantity
            
        # Place the order
        if order_type == Client.ORDER_TYPE_LIMIT:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type=order_type,
                    quantity=quantity,
                    price=order_price,
                    timeInForce=Client.TIME_IN_FORCE_GTC
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a long limit price futures order, at the price of one {coin_buy} {order_price} usdt, establish a position of {quantity} {coin_buy} with a total value of {total_value} usdt"
                # sent mail to client
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except Exception as e:
                print(f'Unexpected error: {e}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        else:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                msg = msg = f"Subject:Trading system notification email\nThe trading system place a long market price futures order, at the price of one {coin_buy} {order_price} usdt, establish a position of {quantity} {coin_buy} with a total value of {total_value} usdt"
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except Exception as e:
                print(f'Unexpected error: {e}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
    
    def future_perpetual_sell(self, symbol, coin_buy, coin_sell, order_size, quantitative_precision, order_price = None):
        # Create a Binance API client object
        #client = Client(api_key, api_secret)    
        # Get the symbol's current price
        ticker = self.binance_client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        # different symbol quantity precision is different
        # given quantity precision
        q_p = pow(10,quantitative_precision)
        # Set the order type based on the parameters provided
        if order_price is not None:
            order_type = Client.ORDER_TYPE_LIMIT
            quantity = math.floor((order_size/order_price)*int(q_p))/float(q_p)
            total_value = order_price*quantity
        else:
            order_type = Client.ORDER_TYPE_MARKET
            quantity = math.floor((order_size/current_price)*int(q_p))/float(q_p)
            total_value = current_price*quantity
        if order_type == Client.ORDER_TYPE_LIMIT:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type=order_type,
                    quantity=quantity,
                    price=order_price,
                    timeInForce=Client.TIME_IN_FORCE_GTC
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a short limit price futures order\n-------------------\n{coin_sell} market order price:${order_price}\n{coin_sell} order number:{quantity}\ntotal value:${total_value} usdt\n{coin_sell} current price:${current_price}"
                # sent mail to client
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except Exception as e:
                print(f'Unexpected error: {e}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        else:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                msg = f"Subject:Trading system notification email\nThe trading system place a short market price futures order\n-------------------\n{coin_sell} market order price:${current_price}\n{coin_sell} order number:{quantity}\ntotal value:${total_value} usdt\n{coin_sell} current price:${current_price}"
                # sent mail to client
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            except Exception as e:
                print(f'Unexpected error: {e}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        
    def future_perpetual_close_position(self, symbol):
        position = self.binance_client.futures_position_information(symbol=symbol)
        unrealized_profit = round(float(position[0]["unRealizedProfit"]), 2)
        # Determine the current position direction
        if float(position[0]["positionAmt"])>0 :
            side = "SELL"
        else:
            side = "BUY"
        # place the order to close position
        try:
            order = self.binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=abs(float(position[0]["positionAmt"]))
            )
            print('close position successfully!')
            msg = f"Subject:Trading system notification email\nThe trading system close position\n-------------------\ntotal profit: ${unrealized_profit} USDT"
            # sent mail to client
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceAPIException as e:
            print(f'Error message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceOrderException as e:
            print(f'Error code: {e.code}, message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except Exception as e:
            print(f'Unexpected error: {e}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
            sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            
    def future_check_position(self, symbol):
        if symbol is not None:
            position = self.binance_client.futures_position_information(symbol=symbol)
        else:
            position = self.binance_client.futures_position_information() 
        return position