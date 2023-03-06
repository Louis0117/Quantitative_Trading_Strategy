(繁體中文)  
# 量化交易系統
透過改良經典量化策略Dual Thrust, 作為本系統判斷交易訊號的依據,  並透過串接Binance API  實現交易, 針對使用者可以設置email通知, 讓用戶追蹤系統當前交易狀況   

## 構想


## 實現  
(fig. system flow chart)  

* Trading strategy
1. Dual Thrust Strategy introduction  
 
    Dual Trust Stratgy 判斷交易訊號邏輯如下圖, 當價格像上突破cap line為看多訊號, 向下突破floor line為看空訊號 
$$cap line = open+k1*Range$$   

$$short line = open-k2*Range$$ 


![Dual Thrust Strategy](https://cdn.quantconnect.com/tutorials/i/Tutorial05-dual-thrust-trading.png)

下圖為計算Range的方法, 找N-days內的HH, HC, LC, LL, 用以下公式求Range value $$Range value = Max(HH-LC, HC-LL)$$

![Dual Thrust Strategy- calculate range value](https://cdn.quantconnect.com/tutorials/i/Tutorial05-dual-thrust-price-range.png)


2. optimize  
針對Dual Thrust策略, 本專案認為有以下缺點  
 
    `a.` 交易策略只考慮價格的變動作為判斷訊號  

    `b.` k1, k2參數沒有一個特定的規則去做調整, 大部分時間都是透過回測歷史數據去給定一組固定的k1, k2, 但市場變化萬千, 固定的k1, k2很難去適應市場不同的狀態   

    `c.` 採用單一個order size  

    本專案想對Dral Thrust策略進行改進, 進行實驗後發現研究標的的官方twitter  tweet底下的使用者留言情緒, 與價格存在關聯, 因此透過對twitter user reply 進行情感分析, 量化結果為情感分數, 作為優化策略的指標之一, 下圖為價格與情感分數的可視化圖,藍色曲線為加密貨幣的價格, 綠色點為回測時間段情感分數最高的前5/15/25/35%,紅色點為回測時間段內情感分數最低後的5/15/25/35%
             ![Sentiment score in AXS](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_5%25.png)  
             
             ![Sentiment score in AXS](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_15%25.png)  
      
    `A.` 針對上述a.交易策略只考慮價格變動作為判斷交易訊號部分, 本專案透過對twitter user reply進行情感分析, 將結果量化作為判斷市場情緒的指標, 使得交易策略不僅能夠考慮價格變化, 參考市場情緒作為判斷, 提升交易策略的維度, 把原本簡單的買賣訊號,可以依照情感分數再更進一步的拆分成更細粒度的買賣狀態, 可以讓決策更精細化
        
        
        本專案想透過

       
    
        


* Data collection
1. price data:  
    使用binance api獲取current price, 每20秒請求一次價格資訊 -> (price_data.py)  
      
2. sentiment score:獲取sentiment score 一共分為以下步驟 ->   

    `step1.` 獲取official twitter user reply text, 實現方法為使用python tweepy package 獲取目標時間段的official twitter 的tweet, 接著使用twarc2獲取每則tweet的user reply -> (collect_text_from_twitter.py)  
    
    `step2.` 對文本做前處理, 移除無意義的文字(e.g. emoji, hashtags...)降低文本雜訊 -> (preprocessing.py)  
       
    `step3.` 透過fine-tune XLNet(詳細內容https://github.com/Louis0117/XLNet) 所訓練出的英文文本分類器對文本做分類, 分為英文文本以及非英文文本兩類, 過濾掉非英文文本 -> (NN_model.py)  
    
    `step4.` 透過fine-tune RoBerta(詳細內容https://github.com/Louis0117/Bert) 所訓練出的情感分類器對文本做情感分類, 分為positive, negitive, neutral-> (NN_model.py)  
    
    `step5.` 對每天的user reply情感分析結果做加總, positive給予+1的權重, negative給予-1的權重, neutral給予0的權重,得到每日的sentiment socre的分數 
  
* Trade in Binance  

* Sent email to client  

    
(English)
