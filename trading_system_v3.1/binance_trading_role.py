# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 15:46:55 2023

@author: louis
"""

import pandas as pd




data1 = {
    'Symbol': ['BTCUSDT', 'ETHUSDT', 'BCHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.001', '0.001', '0.001', '0.1', '0.1', '0.001', '1', '0.01', '0.01', '1', '1', '0.001'],
    'Precision': ['0.01', '0.01', '0.01', '0.0001', '0.001', '0.01', '0.00001', '0.001', '0.001', '0.00001', '0.00001', '0.01']
}
                         



data2 = {
    'Symbol': ['THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT', 'SXPUSDT', 'KAVAUSDT', 'BANDUSDT', 'RLCUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '0.1', '1', '1', '0.1', '0.001', '0.1', '1', '0.1', '0.1', '0.1', '0.1'],
    'Precision': ['0.0001', '0.0001', '0.00001', '0.00001', '0.0001', '0.01', '0.0001', '0.000010', '0.0001', '0.0001', '0.0001', '0.0001'],
    }



data3 = {
    'Symbol': ['DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT', 'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.001', '0.001', '0.1', '0.01', '0.01', '0.1', '0.1', '0.1', '1', '0.01', '0.1', '1'],
    'Precision': ['0.01', '0.01', '0.001', '0.001', '0.001', '0.0001', '0.0001', '0.0001', '0.000001', '0.001', '0.001', '0.000001']
}           


data4 = {
    'Symbol': ['WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT', 'DEFIUSDT', 'YFIUSDT', 'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'EGLDUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '0.001', '0.1', '0.1', '0.001', '0.001', '0.1', '0.1', '0.1', '1', '1', '0.1'],
    'Precision': ['0.0001', '0.01', '0.001', '0.001', '0.1', '0.1', '0.001', '0.001', '0.001', '0.0001', '0.0001', '0.001']
}              


data5 = {
    'Symbol': ['SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT', 'AVAXUSDT', 'FTMUSDT', 'ENJUSDT', 'FLMUSDT', 'TOMOUSDT', 'RENUSDT', 'KSMUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '0.1'],
    'Precision': ['0.0001', '0.0001', '0.0001', '0.00001', '0.0001', '0.0001', '0.0001', '0.0001', '0.0001', '0.0001', '0.00001', '0.001']
}

data6 = {
    'Symbol': ['NEARUSDT', 'AAVEUSDT', 'FILUSDT', 'RSRUSDT', 'LRCUSDT', 'MATICUSDT', 'OCEANUSDT', 'BELUSDT', 'CTKUSDT', 'AXSUSDT', 'ALPHAUSDT', 'ZENUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '0.1', '0.1', '1', '1', '1', '1', '1', '1', '1', '1', '0.1'],
    'Precision': ['0.0001', '0.001', '0.001', '0.000001', '0.00001', '0.00001', '0.00001', '0.00001', '0.00001', '0.00001', '0.00001', '0.001']
}

data7 = {
    'Symbol': ['SKLUSDT', 'GRTUSDT', '1INCHUSDT', 'BTCBUSD', 'CHZUSDT', 'SANDUSDT', 'ANKRUSDT', 'LITUSDT', 'UNFIUSDT', 'REEFUSDT', 'RVNUSDT', 'SFPUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '0.001', '1', '1', '1', '0.1', '0.1', '1', '1', '1'],
    'Precision': ['0.00001', '0.00001', '0.0001', '0.1', '0.00001', '0.0001', '0.00001', '0.001', '0.001', '0.000001', '0.00001', '0.0001']
}


data8 = {
    'Symbol': ['XEMUSDT', 'COTIUSDT', 'CHRUSDT', 'MANAUSDT', 'ALICEUSDT', 'HBARUSDT', 'ONEUSDT', 'LINAUSDT', 'STMXUSDT', 'DENTUSDT', 'CELRUSDT', 'HOTUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '1', '0.1', '1', '1', '1', '1', '1', '1', '1'],
    'Precision': ['0.0001', '0.00001', '0.0001', '0.0001', '0.001', '0.00001', '0.00001', '0.00001', '0.00001', '0.000001', '0.00001', '0.000001']
}



data9 = {
    'Symbol': ['MTLUSDT', 'OGNUSDT', 'NKNUSDT', 'DGBUSDT', '1000SHIBUSDT', 'BAKEUSDT', 'GTCUSDT', 'ETHBUSD', 'BTCDOMUSDT', 'BNBBUSD', 'ADABUSD', 'XRPBUSD'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '1', '1', '1', '0.1', '0.001', '0.001', '0.01', '1', '0.1'],
    'Precision': ['0.0001', '0.0001', '0.00001', '0.00001', '0.000001', '0.0001', '0.001', '0.01', '0.1', '0.1', '0.0001', '0.0001']
}

data10 = {
    'Symbol': ['IOTXUSDT', 'DOGEBUSD', 'AUDIOUSDT', 'C98USDT', 'MASKUSDT', 'ATAUSDT', 'SOLBUSD', 'DYDXUSDT', '1000XECUSDT', 'GALAUSDT', 'CELOUSDT', 'ARUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '1', '1', '1', '1', '0.1', '1', '1', '0.1', '0.1'],
    'Precision': ['0.00001', '0.000001', '0.0001', '0.0001', '0.0010', '0.0001', '0.0001', '0.001', '0.00001', '0.00001', '0.001', '0.001']
}

data11 = {
    'Symbol': ['KLAYUSDT', 'ARPAUSDT', 'CTSIUSDT', 'LPTUSDT', 'ENSUSDT', 'PEOPLEUSDT', 'ANTUSDT', 'ROSEUSDT', 'DUSKUSDT', 'FLOWUSDT', 'IMXUSDT', 'API3USDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '1', '1', '0.1', '0.1', '1', '0.1', '1', '1', '0.1', '1', '0.1'],
    'Precision': ['0.0001', '0.00001', '0.0001', '0.001', '0.001', '0.00001', '0.001', '0.00001', '0.00001', '0.001', '0.0001', '0.001']
}


data12 = {
    'Symbol': ['GMTUSDT', 'APEUSDT', 'WOOUSDT', 'JASMYUSDT', 'DARUSDT', 'GALUSDT', 'FTMBUSD', 'DODOBUSD', 'GALABUSD', 'TRXBUSD', 'OPUSDT', 'LTCBUSD'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '1', '0.1', '1', '1', '1', '1', '1', '0.1', '0.01'],
    'Precision': ['0.00001', '0.0001', '0.00001', '0.000001', '0.0001', '0.00001', '0.0000001', '0.0000001', '0.0000001', '0.0000001', '0.0000001', '0.000001']
}

data13 = {
    'Symbol': ['MATICBUSD', 'LDOBUSD', 'INJUSDT', 'STGUSDT', 'FOOTBALLUSDT', 'SPELLUSDT', '1000LUNCUSDT', 'LUNA2USDT', 'LDOUSDT', 'CVXUSDT', 'ICPUSDT', 'APTUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '0.1', '0.1', '1', '0.01', '1', '1', '1', '1', '1', '1', '0.1'],
    'Precision': ['0.0000001', '0.000001', '0.000001', '0.0000001', '0.00001', '0.0000001', '0.0000001', '0.0000001', '0.0000001', '0.0000001', '0.0000001', '0.00001']
}

data14 = {
    'Symbol': ['QNTUSDT', 'APTBUSD', 'BLUEBIRDUSDT', 'FETUSDT', 'AGIXBUSD', 'FXSUSDT', 'HOOKUSDT', 'MAGICUSDT', 'TUSDT', 'RNDRUSDT', 'HIGHUSDT', 'MINAUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '0.1', '0.1', '1', '1', '0.1', '0.1', '0.1', '1', '0.1', '0.1', '1'],
    'Precision': ['0.000001', '0.00001', '0.00001', '0.0000001', '0.0000001', '0.000001', '0.000001', '0.000001', '0.0000001', '0.0000001', '0.0000001', '0.0000001']
}


data15 = {
    'Symbol': ['ASTRUSDT', 'AGIXUSDT', 'PHBUSDT', 'GMXUSDT', 'CFXUSDT', 'STXUSDT', 'BNXUSDT', 'ACHUSDT', 'SSVUSDT', 'CKBUSDT', 'PERPUSDT', 'TRUUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['1', '1', '1', '0.01', '1', '1', '0.1', '1', '0.01', '1', '0.1', '1'],
    'Precision': ['0.0000001', '0.0000001', '0.0000001', '0.000001', '0.0000001', '0.0000001', '0.000001', '0.0000001', '0.000001', '0.0000001', '0.0000001', '0.0000001']
}

data16 = {
    'Symbol': ['LQTYUSDT', 'USDCUSDT', 'IDUSDT', 'ARBUSDT', 'ETHUSDT', 'BTCUSDT', 'JOEUSDT', 'TLMUSDT', 'AMBUSDT', 'LEVERUSDT', 'RDNTUSDT', 'HFTUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', '0630', '0630', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '1', '1', '0.1', '0.001', '0.001', '1', '1', '1', '1', '1', '1'],
    'Precision': ['0.000001', '0.0000001', '0.0000001', '0.000001', '0.01', '0.1', '0.0000001', '0.0000001', '0.0000001', '0.000001', '0.0000001', '0.0000001']
}

data17 = {
    'Symbol': ['XVSUSDT', 'ETHBTC', 'BLURUSDT', 'EDUUSDT', 'IDEXUSDT', 'SUIUSDT', '1000PEPEUSDT', '1000FLOKIUSDT', 'UMAUSDT', 'RADUSDT', 'KEYUSDT', 'COMBOUSDT'],
    'Type': ['Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts', 'Perpetual contracts'],
    'Min_order_size': ['0.1', '0.01', '1', '1', '1', '0.1', '1', '1', '1', '1', '1', '0.1'],
    'Precision': ['0.000001', '0.000001', '0.0000001', '0.0000001', '0.0000001', '0.000001', '0.0000001', '0.0000001', '0.000001', '0.000001', '0.000001', '0.000001']
}

#dataset = pd.DataFrame(data1)
if __name__ == '__main__':
    merge_df = pd.DataFrame()
    
    for i in range(1, 18):
        data_dict = globals()[f"data{i}"]
        # convert dict -> df
        df = pd.DataFrame(data_dict)
        merge_df = pd.concat([merge_df, df])
    merge_df.reset_index(drop=True,inplace=True)
    merge_df.drop_duplicates(subset=['Symbol'], inplace=True)
    #print(dir(merge_df))
    #print(merge_df.columns)    
    # to csv
    merge_df.to_csv('/Users/welcome870117/Desktop/git_project/Quantitative_trading_strategy/trading_system_v3/binance_trading_role.csv', index=False)
    
    
    
