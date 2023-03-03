(繁體中文)  
# 量化交易系統
透過改良經典量化策略Dual Thrust, 作為本系統判斷交易訊號的依據,  並透過串接Binance API  實現交易, 針對使用者可以設置email通知, 讓用戶追蹤系統當前交易狀況   

## 實現  
(fig. system flow chart)  

* Trading strategy

* Data collection
1. price data:  
    使用binance api獲取current price, 每20秒請求一次價格資訊 -> (price_data.py)  
2. sentiment score  

    
