import datetime as dt
import pandas as pd
import numpy as np
import requests
from io import StringIO

class YahooPriceReader:

    url_format = "https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval={}&events={}&includeAdjustedClose=true"

    def __init__(
        self,
        ticker,
        start = '1970-01-01',
        end = dt.date.today().isoformat(),
        interval = 'd',
        data = 'all',
        returns = True,
        timestamps = False
    ):

        self.ticker = ticker
        self.start = -int((dt.date(1970, 1, 1) - dt.date.fromisoformat(start)).total_seconds())
        self.end = -int((dt.date(1970, 1, 1) - dt.date.fromisoformat(end)).total_seconds()) + 24 * 3600

        if interval in ('day', 'daily', 'd'):
            self.interval = '1d'
        elif interval in ('week', 'weekly', 'w'):
            self.interval = '1wk'
        elif interval in ('month', 'monthly', 'm'):
            self.interval = '1mo'
        else:
            self.interval = interval

        if data == 'prices':
            self.data = 'history'
        elif data == 'dividends':
            self.data = 'div'
        elif data == 'splits':
            self.data = 'split'
        elif data == 'all':
            self.data = data
        else:
            raise ValueError('data argument has to be "prices", "dividends", "splits" or "all"')

        self.returns = returns
        self.timestamps = timestamps

    def get_data(self) -> pd.DataFrame:
        if self.data == 'all':
            df = pd.DataFrame()
            for data in ('history', 'div', 'split'):

                url = self.url_format.format(self.ticker, self.start, self.end, self.interval, data)
                df_temp = requests.get(url).text
                df_temp = pd.read_csv(StringIO(df_temp))
                df_temp.set_index('Date', inplace=True)
                if 'Stock Splits' in df_temp.columns:
                    df_temp['Stock Splits'] = df_temp['Stock Splits'].apply(
                        lambda string: np.NaN if int(string.split(':')[1]) == 0 or int(string.split(':')[0]) / int(string.split(':')[1]) == 1
                        else int(string.split(':')[0]) / int(string.split(':')[1])
                    )
                df_temp.index = pd.to_datetime(df_temp.index)
                df = pd.concat((df, df_temp), axis=1)
        else:
            url = self.url_format.format(self.ticker, self.start, self.end, self.interval, self.data)
            df = requests.get(url).text
            df = pd.read_csv(StringIO(df))
            df.set_index('Date', inplace=True)
            if 'Stock Splits' in df.columns:
                df['Stock Splits'] = df['Stock Splits'].apply(lambda string: int(string.split(':')[0])/int(string.split(':')[1]))
            df.index = pd.to_datetime(df.index)

        if self.returns is True and 'Dividends' in df.columns:
            df['simple returns'] = (df['Close'] + df['Dividends'].fillna(0)) / df['Close'].shift(1).replace(0, np.NaN) - 1
            df['log returns'] = np.log((df['Close'] + df['Dividends'].fillna(0)) / df['Close'].shift(1).replace(0, np.NaN))
        df = df.sort_values(df.index.name)

        if self.timestamps:
            df.index = [
                -int((dt.date(1970, 1, 1) - date.date()).total_seconds())
                for date in df.index
            ]
        return df

