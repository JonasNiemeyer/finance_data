import datetime as dt
import pandas as pd
import numpy as np
import requests
from io import StringIO
import json
import pytz

class YahooReader:

    history_url = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
    company_url = "https://finance.yahoo.com/quote"

    def __init__(self, ticker):
        self._ticker = ticker.upper()

    def historical_data(
        self,
        frequency = '1mo',
        range = None,
        start = dt.date(1970, 1, 1),
        end = dt.date.today(),
        data = 'all',
        returns = True,
        timestamps = True
    ):

        """
        frequency : str
            1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            default: 1d

        range : str
            1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max, ytd
            default: None
        
        start : str, integer, datetime.date or datetime.datetime object
            str input has to be in ISO-format: YYYY-mm-dd
            default: dt.date(1970, 1, 1)

        end : str, integer, datetime.date or datetime.datetime object
            str input has to be in ISO-format: YYYY-mm-dd
            default: datetime.date.today()
        
        data : str
            Not Implemented
            prices, dividends, splits, all
            default: all

        returns : bool
            If True, computes simple and log returns of the adjusted closing price series
            default: True

        timestamps : bool
            If True, df.index has timestamps. If False, df.index has tz-aware datetime objects
            default: False
        """

        if isinstance(start, str):
            start = -int((dt.date(1970, 1, 1) - dt.date.fromisoformat(start)).total_seconds())
        elif isinstance(start, (dt.date, dt.datetime)):
            start = -int((dt.date(1970, 1, 1) - start).total_seconds())
        
        if isinstance(end, str):
            end = -int((dt.date(1970, 1, 1) - dt.date.fromisoformat(end)).total_seconds()) + 24 * 3600
        elif isinstance(end, (dt.date, dt.datetime)):
            end = -int((dt.date(1970, 1, 1) - end).total_seconds()) + 24 * 3600
        

        params = {
            "period1": start,
            "period2": end,
            "interval": frequency,
            "events": "dividends,splits",
            "includeAdjustedClose": True
        }

        data = requests.get(
            url = __class__.history_url.format(self.ticker),
            params = params
        ).json()

        meta_data = data["chart"]["result"][0]["meta"]
        timezone = meta_data["timezone"]

        ts = data["chart"]["result"][0]["timestamp"]
        if "events" in data["chart"]["result"][0]:
            events = data["chart"]["result"][0]["events"]
            if "dividends" in events:
                dividends = events["dividends"]
                dividends = [(div["date"], div["amount"]) for div in dividends.values()]
                dividends = list(zip(*dividends))
                df_div = pd.DataFrame(
                    data = dividends[1],
                    columns = ["Dividends"]
                )
                df_div.index = pd.to_datetime(dividends[0], unit="s")
            else:
                df_div = pd.DataFrame(columns = ["Dividends"])
            if "splits" in events:
                splits = events["splits"]
                splits = [(split["date"], split["numerator"]/split["denominator"]) for split in splits.values()]
                splits = list(zip(*splits))
                df_splits = pd.DataFrame(
                    data = splits[1],
                    columns = ["Splits"]
                )
                df_splits.index = pd.to_datetime(splits[0], unit="s")
            else:
                df_splits = pd.DataFrame(columns = ["Splits"])
        else:
            df_div = pd.DataFrame(columns = ["Dividends"])
            df_splits = pd.DataFrame(columns = ["Splits"])
        prices = data["chart"]["result"][0]["indicators"]["quote"][0]

        open_ = prices["open"]
        high = prices["high"]
        low = prices["low"]
        close = prices["close"]
        volume = prices["volume"]
        
        if "adjclose" in data["chart"]["result"][0]["indicators"]:
            adj_close = data["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"]
        else:
            adj_close = close

        df = pd.DataFrame(
            data = {
                "Open": open_,
                "High": high,
                "Low": low,
                "Close": close,
                "Adj Close": adj_close,
                "Volume": volume
            }
        )

        df.index = pd.to_datetime(ts, unit="s")

        df = pd.concat([df, df_div, df_splits], axis=1)

        if timestamps:
            df.index = [
                -int((dt.datetime(1970, 1, 1) - datetime).total_seconds())
                for datetime in df.index
            ]
        else:
            df.index = df.index.tz_localize("UTC").tz_convert(timezone)

        if returns:
            df['simple returns'] = (df['Adj Close'] + df['Dividends'].fillna(0)) / df['Adj Close'].shift(1) - 1
            df['log returns'] = np.log((df['Adj Close'] + df['Dividends'].fillna(0)) / df['Adj Close'].shift(1))
        
        if frequency in ("1m", "2m", "5m", "15m", "30m", "60m"):
            df.index.name = "datetime"
        else:
            df.index = pd.to_datetime(df.index.date)
            df.index.name = "date"

        return df

    @property
    def ticker(self):
        return self._ticker

    @property
    def isin(self):
        raise NotImplementedError
        return self._isin

if __name__ == "__main__":
    df = YahooReader("AAPL").historical_data(
        frequency="1d",
        start="2018-01-31"
    )
    print(df)