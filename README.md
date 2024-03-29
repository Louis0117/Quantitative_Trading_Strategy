# Trading System
  ## Version   
  * current version: trading_system_v3.1  

    ( If you want to trade spot markets using the Turtle strategy, please use trading_system_v3.2 )
  * version update:   
  
                    1. Resolve system trading failures caused by Binance's different trading precision restrictions on different trading pairs.  
                    2. add turtle strategy   
                    3. optimized system code   

  ## Strategy  
  ### Long_Short_Strategy_v3.py ( Long-Short Strategy )  
  #### Introduction
    Introduction to strategy and detailed experiments can be found in the Long-short_strategy_research.pdf.
  #### Requirement   
  (python package)   
  * numpy   

  * pandas  
  * requests  
  * bs4  
  * json  
  * binance  
  * math  
  * smtplib  
    
  (API)  
  * Binance API  

  * Gmail API (Not necessary)  

#### Execute program
`step1.`  
  
If the mentioned package is not installed.
```
pip install (package)  
```    
  
`step2.`  
  
download this repository code  
  
  
`step3.`  
  
   change "log_file_dir" in file long_short_v3.py to your dir  
```  
log_file_dir = '(your directory path)/long_short_strategy_log.csv'
```  

`step4.`  
   
change "BINANCE_ROLE_DIR" in file binance_api_v3.py to your dir  
    
```  
BINANCE_ROLE_DIR = '(your directory path)/binance_trading_role.csv'  
```   

  
`step5.`
  
  add your Binance API key  
```
BINANCE_KEY = ''  
BINANCE_SECRET = ''  
```
  
  
`step6.`  
  
run python code
  
  there five parameters:    
  1. position size (USDT) of each asset in the investment portfolio, This strategy will generate a portfolio of 20 cryptocurrencies at once, so constructing the portfolio will require a total of $position size * 20 / leverage$ USDT. Please ensure that you have sufficient margin to cover it.  
    
  2. leverage size  
    
  3. J_value (days) -> number of days referencing past historical data. Typically set to three months, six months, nine months, and twelve months. To convert the number of months to days, you can multiply the number of months by 30.  
  
  4. k_value (days) -> portfolio holding period. Typically set to three months, six months, nine months, and twelve months. To convert the number of months to days, you can multiply the number of months by 30.  
  
  5. mode -> there are two mode 'normal' and 'close', 'normal' mode is used to execute the regular version of the long-short strategy. 'close' mode is used to allow the original investment portfolio to be held until the specified K_value time expires without generating new investment portfolios.
   
```
python long_short_v3.py 10 1 90 90 normal  
```

  ### turtle_strategy_spot_final.py ( Turtle Strategy for spot )   
  * in file trading_system_v3.2  
  #### Requirement  
  (python package)  
   * pandas   

   * numpy  
   * argparse  
   * os 
   * time  
   * datetime  
   * pytz  
   * python-binance  
   * math  
   * requests  
   * json  
     
  (API)  
   * binance API Key / Secret Key   
    
  (python file)  
   * binance_api_v3_2    
   * utils.py  
     
   #### Execute program  
     
`step1.`  
      
If the mentioned package is not installed.  
  
```  
pip install (python package)   
``` 
    
`step2.`  
     
download this repository code 
   
  
`step3.`  
  
add your Binance API key / Secret Key (in turtle_strategy_spot_final.py)  
    
```  
BINANCE_KEY = ''   
BINANCE_SECRET = ''  
```  

  
`step4.`   
   
run python code  
  
   
   there is two parameters:  
   
  * *symbol* : The trading pairs of USDT (Tether) against cryptocurrencies.  
  * *asset_value* : The asset_value parameter is used to set how much USDT allocation should be allocated for trading the target cryptocurrency. ( Please ensure that you have sufficient USDT, as insufficient funds may result in failed orders when generating trading signals. It is recommended to set at least 150 USDT.)  
  
   
```
turtle_strategy_spot_final.py --symbol XXXUSDT --asset_value 200  
```  

  ### Turtle_Strategy_v3.py ( Turtle Strategy for future)
  #### Requirement  
  (python package)  
   * pandas   

   * numpy  
   * argparse  
   * os 
   * time  
   * datetime  
   * pytz  
   * binance  
   * math  
   * requests  
   * json  
               
  (API KEY)  
   * binance API Key  
    
  (python file)  
   * binance_api_v3  

   * utils.py  
   #### Execute program  
     
`step1.`  
      
If the mentioned package is not installed.  
  
```  
pip install (python package)   
``` 
    
`step2.`  
     
download this repository code 
   
   
`step3.`   
    
change "LOG_FILE_DIR" in file turtle_strategy_v3.py to your dir   
  
    
```
LOG_FILE_DIR = '(your directory path)/turtle_strategy_log_file.csv'   
```  

`step4.`  
    
change "BINANCE_ROLE_DIR" in file binance_api_v3.py to your dir  
    
```  
BINANCE_ROLE_DIR = '(your directory path)/binance_trading_role.csv'  
```   
  
`step5.`  
  
add your Binance API key   
    
```  
BINANCE_KEY = ''   
BINANCE_SECRET = ''  
```  

  
`step6.`   
   
run python code  
  
   
   there is one parameter:  
   
  *symbol* : The trading pairs of USDT (Tether) against cryptocurrencies.

  
```
python Turtle_Strategy_v3.py --symbol XXXUSDT
```


    
## System Test
  + Turtle_Strategy_test.py ( Turtle Strategy )

  + Long_short_test_v3.py ( Long-Short Strategy )  
  
## Test Log txt  
  + Turtle Strategy ->  turtle_strategy_test_ADA_log.txt  ( strategy test )  

    turtle_strategy_test_ADA_order_log.txt ( order test )  
                         

  + Long Short Strategy ->  long_short_test_mode_normal.txt ( strategy normal mode test )  

    long_short_test_mode_close.txt ( strategy close mode test ) 