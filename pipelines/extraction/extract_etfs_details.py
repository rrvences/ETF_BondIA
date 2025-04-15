import yfinance as yf
import pandas as pd
import traceback


def get_etf_daily_prices(ticker, period = 'max') -> pd.DataFrame:
    try:
        yticker = yf.Ticker(ticker)
        df_prices = yticker.history(period = period)
        df_prices["date"] = df_prices.index
        df_prices["ticker"] = ticker
        df_prices.reset_index(drop=True, inplace = True)
    except Exception as e:
        print(ticker,e)
        print(traceback.format_exc())
        df_prices = pd.DataFrame([],columns=["Open","High","Low","Close","Volume","Dividends","Stock Splits","Capital Gains","date","ticker"])
    
    return df_prices


def get_etf_dividends_issued(ticker, period = 'max') -> pd.DataFrame:
    try:
        yticker = yf.Ticker(ticker)
        df_dividends = pd.DataFrame(yticker.get_dividends())
        df_dividends["date"] = df_dividends.index
        df_dividends["date"] = df_dividends["date"].dt.floor('D')
        df_dividends["ticker"] = ticker
        df_dividends.reset_index(drop=True, inplace = True)
    except Exception as e:
        print(ticker,e)
        print(traceback.format_exc())
        df_dividends = pd.DataFrame([],columns=["Dividends","date","ticker"])
    
    return df_dividends

def get_etf_info(ticker) -> pd.DataFrame:
    try:
        yticker = yf.Ticker(ticker)
        info_dict = yticker.get_info()
        if isinstance(info_dict, dict):
            info_dict["ticker"] = ticker
        df_info = pd.DataFrame([info_dict])
    except Exception as e:
        print(ticker,e)
        print(traceback.format_exc())
        df_info = pd.DataFrame([],
                               columns=['phone', 'longBusinessSummary', 'companyOfficers', 'executiveTeam',
       'maxAge', 'priceHint', 'previousClose', 'open', 'dayLow', 'dayHigh',
       'regularMarketPreviousClose', 'regularMarketOpen',
       'regularMarketDayLow', 'regularMarketDayHigh', 'volume',
       'regularMarketVolume', 'averageVolume', 'averageVolume10days',
       'averageDailyVolume10Day', 'bid', 'ask', 'bidSize', 'askSize', 'yield',
       'totalAssets', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'fiftyDayAverage',
       'twoHundredDayAverage', 'navPrice', 'currency', 'tradeable', 'category',
       'ytdReturn', 'beta3Year', 'fundFamily', 'fundInceptionDate',
       'legalType', 'threeYearAverageReturn', 'fiveYearAverageReturn',
       'quoteType', 'symbol', 'language', 'region', 'typeDisp',
       'quoteSourceName', 'triggerable', 'customPriceAlertConfidence',
       'corporateActions', 'regularMarketChangePercent', 'regularMarketPrice',
       'shortName', 'longName', 'marketState', 'exchange', 'messageBoardId',
       'exchangeTimezoneName', 'exchangeTimezoneShortName',
       'gmtOffSetMilliseconds', 'market', 'esgPopulated', 'postMarketTime',
       'regularMarketTime', 'dividendYield', 'trailingThreeMonthReturns',
       'trailingThreeMonthNavReturns', 'netAssets', 'fiftyDayAverageChange',
       'fiftyDayAverageChangePercent', 'twoHundredDayAverageChange',
       'twoHundredDayAverageChangePercent', 'netExpenseRatio',
       'sourceInterval', 'exchangeDataDelayedBy', 'cryptoTradeable',
       'hasPrePostMarketData', 'firstTradeDateMilliseconds',
       'postMarketChangePercent', 'postMarketPrice', 'postMarketChange',
       'regularMarketChange', 'regularMarketDayRange', 'fullExchangeName',
       'averageDailyVolume3Month', 'fiftyTwoWeekLowChange',
       'fiftyTwoWeekLowChangePercent', 'fiftyTwoWeekRange',
       'fiftyTwoWeekHighChange', 'fiftyTwoWeekHighChangePercent',
       'fiftyTwoWeekChangePercent', 'dividendDate', 'trailingPegRatio','ticker'])
    
    return df_info

#df_info = get_etf_daily_prices("TLT")
#result_dict = df_info.head(5).groupby('ticker').apply(lambda x: x.to_dict(orient='records')).to_dict()
#print(result_dict)