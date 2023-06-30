#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 21:03:15 2023

@author: welcome870117
"""

# import python file
#from sent_email import sent_mail

# import python package
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import math 
import pandas as pd


BINANCE_ROLE_DIR = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v3/binance_trading_role.csv'


class Binance_transaction:
    def __init__(self, api_key, api_secret, sys_mail_address, app_pwd, clinet_mail_adress):
        self.sys_mail_address = sys_mail_address
        self.app_pwd = app_pwd
        self.api_key = api_key
        self.api_secret = api_secret
        self.clinet_mail_adress = clinet_mail_adress
        # build binance connect
        self.binance_client = Client(self.api_key, self.api_secret)
        
        
    ### The limit order function has not been tested
    ### XXXUSDT, XXXUSDC, XXXBUSD only!!!
    def future_perpetual_buy(self, symbol, coin_buy, coin_sell, order_size, order_price = None, quantity = None):
        # read Binance role csv
        binance_role_df = pd.read_csv(BINANCE_ROLE_DIR, index_col=False)
        # Get the symbol's current price
        ticker = self.binance_client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        quantitative_precision = float(binance_role_df['Min_order_size'][binance_role_df[binance_role_df['Symbol']==symbol].index])
        #print(quantitative_precision)
        q_p = 1/quantitative_precision
        #print(q_p)
        # Set the order type based on the parameters provided
        if order_price is not None:
            order_type = Client.ORDER_TYPE_LIMIT
            if quantity == None:##########################    
                quantity = math.floor((order_size/order_price)*int(q_p))/float(q_p)
            else:
                quantity = math.floor(quantity*int(q_p))/float(q_p)
            total_value = order_price*quantity
        else:
            order_type = Client.ORDER_TYPE_MARKET
            if quantity == None:
                quantity = math.floor((order_size/current_price)*int(q_p))/float(q_p)
            else:
                quantity = math.floor(quantity*int(q_p))/float(q_p)
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
                return quantity
                #msg = f"Subject:Trading system notification email\nThe trading system place a long limit price futures order, at the price of one {coin_buy} {order_price} usdt, establish a position of {quantity} {coin_buy} with a total value of {total_value} usdt"
                # sent mail to client
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                          
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            
            except Exception as e:
                print(f'Unexpected error: {e}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
        else:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                return quantity
                #msg = msg = f"Subject:Trading system notification email\nThe trading system place a long market price futures order, at the price of one {coin_buy} {order_price} usdt, establish a position of {quantity} {coin_buy} with a total value of {total_value} usdt"
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            
            except BinanceAPIException as e:
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                print(f'Unexpected error: {e}')
                return False
            
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
            
            except Exception as e:
                print(f'Unexpected error: {e}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                    
    def future_perpetual_sell(self, symbol, coin_buy, coin_sell, order_size, order_price = None, quantity = None):
        # read Binance role csv
        binance_role_df = pd.read_csv(BINANCE_ROLE_DIR, index_col=False)
        # Get the symbol's current price
        ticker = self.binance_client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        # different symbol quantity precision is different
        # given quantity precision
        quantitative_precision = float(binance_role_df['Min_order_size'][binance_role_df[binance_role_df['Symbol']==symbol].index])
        #print(quantitative_precision)
        q_p = 1/quantitative_precision
        # Set the order type based on the parameters provided
        if order_price is not None:
            order_type = Client.ORDER_TYPE_LIMIT
            if quantity == None:
                quantity = math.floor((order_size/order_price)*int(q_p))/float(q_p)
            else:
                quantity = math.floor(quantity*int(q_p))/float(q_p)
            total_value = order_price*quantity
        else:
            order_type = Client.ORDER_TYPE_MARKET
            if quantity == None:
                quantity = math.floor((order_size/current_price)*int(q_p))/float(q_p)
            else:
                quantity = math.floor(quantity*int(q_p))/float(q_p)
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
                return quantity
                #msg = f"Subject:Trading system notification email\nThe trading system place a short limit price futures order\n-------------------\n{coin_sell} market order price:${order_price}\n{coin_sell} order number:{quantity}\ntotal value:${total_value} usdt\n{coin_sell} current price:${current_price}"
                # sent mail to client
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
                
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                return False
                
            except Exception as e:
                print(f'Unexpected error: {e}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        else:
            try:
                order = self.binance_client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type=order_type,
                    quantity=quantity
                )
                print('Order executed successfully!')
                #msg = f"Subject:Trading system notification email\nThe trading system place a short market price futures order\n-------------------\n{coin_sell} market order price:${current_price}\n{coin_sell} order number:{quantity}\ntotal value:${total_value} usdt\n{coin_sell} current price:${current_price}"
                # sent mail to client
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                return quantity
                
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                return  False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                            
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                            
            except Exception as e:
                print(f'Unexpected error: {e}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                            
    def future_perpetual_close_position(self, symbol=None):
        if symbol == None:
            print('symbol = None')
            return False
        else:
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
                return True
                #msg = f"Subject:Trading system notification email\nThe trading system close position\n-------------------\ntotal profit: ${unrealized_profit} USDT"
                # sent mail to client
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
            except BinanceAPIException as e:
                print(f'Error message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
            except BinanceOrderException as e:
                print(f'Error code: {e.code}, message: {e.message}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
            except Exception as e:
                print(f'Unexpected error: {e}')
                return False
                #msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
                #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
    
    
    def future_perpetual_partial_close_position(self, symbol, quantity):
        # 判斷方向
        if quantity > 0:
            side = "SELL"
        else:
            side = "BUY"
        position = self.binance_client.futures_position_information(symbol=symbol)
        if abs(float(position[0]["positionAmt"]))< abs(quantity):
            quantity = abs(float(position[0]["positionAmt"]))
        # 建立訂單
        # 例外排除
        try:
            order = self.binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=abs(quantity)
            )
            
            print('close position successfully!')
            #msg = f"Subject:Trading system notification email\nThe trading system close position\n-------------------\ntotal profit: ${unrealized_profit} USDT"
            return quantity
            # sent mail to client
            #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceAPIException as e:
            print(f'Error message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError message: {e.message}'
            return False
            #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except BinanceOrderException as e:
            print(f'Error code: {e.code}, message: {e.message}')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nError code: {e.code}, message: {e.message}'
            return False
            #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
        except Exception as e:
            print(f'Unexpected error: {e}')
            if e == "Unexpected error: name 'unrealized_profit' is not defined":
                print('yes')
            msg = f'Subject:Trading system notification email\n--------------------------------------\nUnexpected error: {e}'
            return False
            #sent_mail(self.sys_mail_address, self.app_pwd, self.clinet_mail_adress, msg)
                
          
    def check_future_account(self):
        return self.binance_client.futures_account()
    
    
    def check_future_trade_history(self, symbol=None):
        if symbol is not None:
            return self.binance_client.futures_account_trades(symbol=symbol)
        else:
            return self.binance_client.futures_account_trades()    
        
        
    def future_check_position(self, symbol=None):
        if symbol is not None:
            position = self.binance_client.futures_position_information(symbol=symbol)
        else:
            position = self.binance_client.futures_position_information() 
        return position
