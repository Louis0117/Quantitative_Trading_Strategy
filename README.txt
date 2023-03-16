(繁體中文)
* 量化交易系統 -> 

* 構想

* 工具

* 實現
(fig. system flow chart)
1. Trading strategy


2. Data collection -> a. price data / b. sentiment score

a. price data: 使用binance api獲取current price, 每20秒請求一次價格資訊 -> (price_data.py)

b. sentiment score: 獲取sentiment score 一共分為以下步驟 

step1. 獲取official twitter user reply text, 實現方法為使用python tweepy package 獲取目標時間段的official twitter 的tweet, 接著使用twarc2獲取每則tweet的user reply -> (collect_text_from_twitter.py)

step2. 對文本做前處理, 移除無意義的文字(e.g. emoji, hashtags...)降低文本雜訊 -> (preprocessing.py)

step3. 透過fine-tune XLNet(詳細內容https://github.com/Louis0117/XLNet) 所訓練出的英文文本分類器對文本做分類, 分為英文文本以及非英文文本兩類, 過濾掉非英文文本 -> (NN_model.py)

step4. 透過fine-tune RoBerta(詳細內容https://github.com/Louis0117/Bert) 所訓練出的情感分類器對文本做情感分類, 分為positive, negitive, neutral-> (NN_model.py)

step5. 對每天的user reply情感分析結果做加總, positive給予+1的權重, negative給予-1的權重, neutral給予0的權重,得到每日的sentiment socre的分數 


3. Trade in Binance

4. Sent email to client








(English)