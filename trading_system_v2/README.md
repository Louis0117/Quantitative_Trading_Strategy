# Trading strategy

## `long-short strategy`

### introduction

### requirement
(python package)  
numpy  
pandas  
requests  
bs4  
json  
binance  
math  
smtplib  

(API)  
Binance API  
Gmail API (Not necessary)

### Execute program
`step1.`
If the mentioned package is not installed.
```
pip install (package)  
```    
  
`step2.`  
download this repository code  
  
  
`step3.`  
  
   change "log_file_dir" in file long_short_v2.py to your dir  
```  
log_file_dir = '(your directory path)/long_short_strategy_log.csv'
```  
  
`step4.`
  
  add your Binance API key  
```
BINANCE_KEY = ''  
BINANCE_SECRET = ''  
```
  
  
`step5.`
run python code
  
  there four parameters:    
  1. position size(USDT) of each asset in the investment portfolio, This strategy will generate a portfolio of 20 cryptocurrencies at once, so constructing the portfolio will require a total of $position size * 20 / leverage$ USDT. Please ensure that you have sufficient margin to cover it.  
    
  2. leverage size  
    
  3. J_value -> number of days referencing past historical data. Typically set to three months, six months, nine months, and twelve months. To convert the number of months to days, you can multiply the number of months by 30.  
  
  4. k_value -> portfolio holding period. Typically set to three months, six months, nine months, and twelve months. To convert the number of months to days, you can multiply the number of months by 30.  

```
python long_short_v2.py 10 3 90 90 
```
