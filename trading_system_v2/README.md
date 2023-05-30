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
Gmail API 

### Execute program
`step1.`
```
git clone https://github.com/Louis0117/Quantitative_Trading_Strategy.git
```  
`step2.`  
change "log_file_dir" in file long_short_v2.py to your dir  
```  
log_file_dir = '/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v2/long_short_strategy_log.csv'
```  
`step3.`
run python code
  
  there four parameters:    
  1. position size of each asset in the investment portfolio  
  2. leverage size  
  3. J_value -> number of days referencing past historical data. typically set to three months, six months, nine months, and twelve months.
To convert the number of months to days, you can multiply the number of months by 30.  
  4. k_value -> portfolio holding period. typically set to three months, six months, nine months, and twelve months.
To convert the number of months to days, you can multiply the number of months by 30.  

```
python long_short_v2.py 10 3 90 90 
```
