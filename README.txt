(繁體中文)
### 量化交易系統 -> 根據Strategy交易邏輯, 執行可靠的交易, 並且設置email通知, 讓用戶追蹤系統當前交易情況 

* 實現
1. Data collection -> a. price data / b. sentiment score

a. price data: 使用binance api獲取current price (price_data.py), 每20秒請求一次價格資訊

b. sentiment score: 獲取sentiment score 一共分為以下步驟 

step1. 獲取official twitter user reply text, 實現方法為使用python tweepy package 獲取目標時間段的official twitter 的tweet, 接著使用twarc2獲取每則tweet的user reply (collect_text_from_twitter.py)

step2. 對文本做前處理, 移除不必要的








(English)