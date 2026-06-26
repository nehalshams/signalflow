import pandas as pd
import numpy as np


class FeatureEngineer:

    def __init__(self, sma_windows=(20, 50), rsi_period=14, bb_window=20):
        self.sma_windows = sma_windows
        self.rsi_period = rsi_period
        self.bb_window = bb_window

    def add_all_features(self, df):
        df = df.copy()
        self._add_moving_averages(df)
        self._add_rsi(df)
        self._add_macd(df)
        self._add_bollinger_bands(df)
        self._add_volume_features(df)
        self._add_price_features(df)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def _add_moving_averages(self, df):
        for w in self.sma_windows:
            sma = df['Close'].rolling(window=w).mean()
            df[f'sma_{w}_ratio'] = df['Close'] / sma

    def _add_rsi(self, df):
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1 / self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / self.rsi_period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))

    def _add_macd(self, df):
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()

        df['macd'] = macd_line / df['Close']
        df['macd_signal'] = macd_signal / df['Close']
        df['macd_hist'] = (macd_line - macd_signal) / df['Close']

    def _add_bollinger_bands(self, df):
        sma = df['Close'].rolling(window=self.bb_window).mean()
        std = df['Close'].rolling(window=self.bb_window).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        width = upper - lower

        df['bb_width'] = width / sma
        df['bb_pct'] = (df['Close'] - lower) / width.replace(0, np.nan)

    def _add_volume_features(self, df):
        vol_sma = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / vol_sma.replace(0, np.nan)

    def _add_price_features(self, df):
        df['daily_return'] = df['Close'].pct_change()
        df['high_low_range'] = (df['High'] - df['Low']) / df['Close']
        df['close_open_pct'] = (df['Close'] - df['Open']) / df['Open']