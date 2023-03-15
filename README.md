(English document)  

# Quantitative trading system
By improving the classic quantitative strategy Dual Thrust, it is used as the basis for the system to create trading signals, and through the connection of Binance API to realize transactions, email notifications can be set for users to allow users to track the current transaction status of the system.

## introduction
(incomplete)

## implementation 
![trading system flow chat](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/trading_system_flow_chart.png)
(fig. system flow chart) 

* Trading strategy  
    1. Dual Thrust Strategy introduction  
 
    The trading signal logic generated by Dual Trust Strategy is as shown in the figure below. When the price breaks through the cap line upwards, it is a long signal, and when it breaks through the floor line downwards, it is a short signal.
    
    $$cap  line = open+k1*Range$$   


    $$short  line = open-k2*Range$$ 

    ![Dual Thrust Strategy](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/dual_thrust.png)


    The figure below shows the method of calculating range value, find HH, HC, LC, LL in N-days, use the following formula to find range value $$Range value = Max(HH-LC, HC-LL)$$


    ![Dual Thrust Strategy- calculate range value](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/dual_thrust_range_value.png)


    2. optimization  
    Regarding the Dual Thrust strategy, this project considers the following disadvantages.  
 
    `a.` Trading strategies only consider price movements to generate trading signals.

    `b.` There is no specific rule for k1 and k2 parameters to adjust. Most of the time, a set of fixed k1 and k2 is given through backtesting historical data. However, the market is changing and it is difficult to adapt fixed k1 and k2 to the different states market.  

    `c.` Use a single order size. 

    This project wants to improve the Dual Thrust strategy. After the experiment, it is found that the sentiment of the user's message under the official twitter tweet of the research target is related to the price. Therefore, through the sentiment analysis of the twitter user reply, the quantified result is the sentiment score, which is used as an optimization One of the indicators of the strategy, the figure below is a visualization of price and sentiment score, the blue curve is the price of cryptocurrency, the green point is the top 5/15/25/35% of the highest sentiment score during the backtest period, and the red point is The 5/15/25/35% after the lowest sentiment score in the backtest time period, it can be seen from the figure that when the green dots are densely distributed, it can be regarded as a positive market sentiment, and there is a high probability that the price will rise. When the red dots are densely distributed, it can be seen Because the market sentiment is negative, the price has a higher probability of falling. When the distribution of red and green dots turns into an average, it is likely to be a price turning signal.
     
    ![Sentiment score in AXS 5%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_5%25.png)  
        
    ![Sentiment score in AXS 15%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_15%25.png)  

    ![Sentiment score in AXS 25%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_25%25.png)

    ![Sentiment score in AXS 35%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_35%25.png)
      
    `A.` For the above-mentioned a. trading strategy only considers price changes to generate trading signals, this project conducts sentiment analysis on twitter user replies, and quantifies the results as an indicator for judging market sentiment, so that trading strategies can not only consider price changes, but also refer to market sentiment , to enhance the dimension of trading strategies, the original simple buying and selling signals can be further split into finer-grained buying and selling states according to market sentiment, which can make decision-making more refined.
        
    `B.` For the above b., we can use market sentiment to optimize. When the market sentiment is positive, dynamically adjust the values ​​of k1 and k2, giving k1 a smaller value and k2 a larger value. Conversely, when the market sentiment is negative, give k1 a larger value. The smaller the value of k2, the logic is that when the market is judged to be positive, the system hopes to generate a long signal more easily and make it more difficult to generate a sell signal, and vice versa.
    
    `C.` For the above c, we can also use the analysis of market sentiment to optimize, we can simply arrange and combine market sentiment and buying and selling signals, set different order sizes for different situations, generate buying signals + positive market sentiment / generate buying signals + negative market sentiment/generate a sell signal + positive market sentiment/generate a sell signal + negative market sentiment, use the above logic to formulate different order sizes and optimize strategies.

    3. Algorithm    
    (incomplete)
        
* Data collection  
    1. price data:  
    Use the binance api to get the current price, and request price information every 20 seconds. -> (price_data.py)  
      
    2. Sentiment score: Obtaining the sentiment score is divided into the following steps.  

    `step1.` Obtain official twitter user reply text, the implementation method is to use python tweepy package to obtain official twitter tweets in the target time period, and then use twarc2 to obtain the user reply of each tweet. -> (collect_text_from_twitter.py)  
    
    `step2.` Pre-process the text to remove meaningless text and reduce text noise. -> (preprocessing.py)  
       
    `step3.` The English text classifier trained by fine-tune XLNet(https://github.com/Louis0117/XLNet) classifies texts into English texts and non-English texts, and filters out non-English texts. -> (NN_model.py)  
    
    `step4.` The sentiment classifier trained by fine-tune RoBerta(https://github.com/Louis0117/Bert) performs sentiment classification on the text, which is divided into positive, negative, neutral-> (NN_model.py)  
    
    `step5.` Sum up the daily user reply sentiment analysis results, give positive a weight of +1, negative give a weight of -1, and neutral give a weight of 0 to get the daily sentiment socre score 
  
* Trade in Binance  
(incomplete)
* Sent email to client  
(incomplete)


--------

(繁體中文文檔) 
 
# 量化交易系統
透過改良經典量化策略Dual Thrust, 作為本系統判斷交易訊號的依據,  並透過串接Binance API  實現交易, 針對使用者可以設置email通知, 讓用戶追蹤系統當前交易狀況   

## 介紹
(incomplete)

## 實現  
(fig. system flow chart) (incomplete)

* Trading strategy
    1. Dual Thrust Strategy introduction  
 
        Dual Trust Stratgy 產生交易訊號邏輯如下圖, 當價格像上突破cap line為看多訊號, 向下突破floor line為看空訊號 
    
        $$cap line = open+k1*Range$$   


        $$short line = open-k2*Range$$ 


        ![Dual Thrust Strategy](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/dual_thrust.png)



        下圖為計算Range的方法, 找N-days內的HH, HC, LC, LL, 用以下公式求Range value $$Range value = Max(HH-LC, HC-LL)$$


        ![Dual Thrust Strategy- calculate range value](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/dual_thrust_range_value.png)

    2. optimize  
    針對Dual Thrust策略, 本專案認為有以下缺點  
 
    `a.` 交易策略只考慮價格的變動來產生交易訊號  

    `b.` k1, k2參數沒有一個特定的規則去做調整, 大部分時間都是透過回測歷史數據去給定一組固定的k1, k2, 但市場變化萬千, 固定的k1, k2很難去適應市場不同的狀態   

    `c.` 採用單一個order size  

    本專案想對Dral Thrust策略進行改進, 進行實驗後發現研究標的的官方twitter  tweet底下的使用者留言情緒, 與價格存在關聯, 因此透過對twitter user reply 進行情感分析, 量化結果為情感分數, 作為優化策略的指標之一, 下圖為價格與情感分數的可視化圖,藍色曲線為加密貨幣的價格, 綠色點為回測時間段情感分數最高的前5/15/25/35%,紅色點為回測時間段內情感分數最低後的5/15/25/35% ,從圖中可以發現當綠點分佈密集時可以視為市場情緒正面有較高機率價格上漲, 當紅點分佈密集時可以視為市場情緒負面, 價格有較高的機率下跌, 當紅綠點分佈轉為平均時很有可能會是一個價格轉折訊號
     
    ![Sentiment score in AXS 5%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_5%25.png)  
        
    ![Sentiment score in AXS 15%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_15%25.png)  

    ![Sentiment score in AXS 25%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_25%25.png)

    ![Sentiment score in AXS 35%](https://github.com/Louis0117/Quantitative_Trading_Strategy/blob/main/IMG/sentiment_score_price_AXS_35%25.png)
      
    `A.` 針對上述a.交易策略只考慮價格變動來產生交易訊號, 本專案透過對twitter user reply進行情感分析, 將結果量化作為判斷市場情緒的指標, 使得交易策略不僅能夠考慮價格變化, 也能參考市場情緒, 提升交易策略的維度, 把原本簡單的買賣訊號,可以依照市場情緒(情感分數)再更進一步的拆分成更細粒度的買賣狀態, 可以讓決策更精細化
        
    `B.` 針對上述b.我們可以利用市場情緒(情感分數)做優化, 當市場情緒正面,動態調整k1, k2值,給予k1較小的值, k2較大的值, 反之當市場情緒負面, 給k1較大的值, k2較小的值, 其中邏輯為, 當市場判斷為正面, 系統希望能夠更容易的產生作多訊號, 並使得賣出訊號更困難產生, 反之同理
    
    `C.` 針對上述c. 我們也能夠利用分析市場情緒(情感分數)來優化, 可以簡單將市場情緒與買賣訊號做排列組合, 針對不同情況設置不同的order size, 產生買入訊號+市場情緒正面/產生買入訊號+市場情緒負面/產生賣出訊號+市場情緒正面/產生賣出訊號+市場情緒負面, 用上述邏輯制定不同的order size, 優化策略

    3. Algorithm    
    (incomplete)
        
* Data collection  
    1. price data:  
        使用binance api獲取current price, 每20秒請求一次價格資訊 -> (price_data.py)  
      
    2. sentiment score:獲取sentiment score 一共分為以下步驟 ->   

    `step1.` 獲取official twitter user reply text, 實現方法為使用python tweepy package 獲取目標時間段的official twitter 的tweet, 接著使用twarc2獲取每則tweet的user reply -> (collect_text_from_twitter.py)  
    
    `step2.` 對文本做前處理, 移除無意義的文字(e.g. emoji, hashtags...)降低文本雜訊 -> (preprocessing.py)  
       
    `step3.` 透過fine-tune XLNet(詳細內容https://github.com/Louis0117/XLNet) 所訓練出的英文文本分類器對文本做分類, 分為英文文本以及非英文文本兩類, 過濾掉非英文文本 -> (NN_model.py)  
    
    `step4.` 透過fine-tune RoBerta(詳細內容https://github.com/Louis0117/Bert) 所訓練出的情感分類器對文本做情感分類, 分為positive, negitive, neutral-> (NN_model.py)  
    
    `step5.` 對每天的user reply情感分析結果做加總, positive給予+1的權重, negative給予-1的權重, neutral給予0的權重,得到每日的sentiment score的分數 
  
* Trade in Binance  
(incomplete)
* Sent email to client  
(incomplete)
    
