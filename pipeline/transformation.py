from .base import PipelineStep
import pandas as pd

class StockTransformation(PipelineStep):
    def __init__(self,periodEma= 10,periodSma = 10,shiftNumber = 1,shiftConfirm=1):
        """
            :param periodSma: int, Number of Days for Simple Moving Average (Default=10), e.g. 10, 20, 30
            :param periodEma: int, Number of Days for Exponential Moving Average (Default=10), e.g. 10, 20, 30
            :param shiftNumber: int, Max Number of shifts (Default=1), e.g. 1, 2, 3
            :param shiftConfirm: int, Max Number of confirmation trend (Default=1), eg. 1, 2, 3
        """
        self.periodSma = periodSma
        self.periodEma = periodEma
        self.shiftNumber = shiftNumber
        self.shiftConfirma = shiftConfirm


    def sma(self, data: pd.DataFrame)-> pd.DataFrame:
        data[f"sma_{self.periodSma}"] = data["Close"].rolling(self.periodSma).mean()
        return data

    def ema(self,data: pd.DataFrame)-> pd.DataFrame:
        data[f"ema_{self.periodEma}"] = data["Close"].ewm(span=self.periodEma, min_periods=self.periodEma).mean()
        return data

    def shiftData(self, data: pd.DataFrame, shiftNumber: int = 1) -> pd.DataFrame:
        """
        Method is shifting data per number of requests from parameter.

        :param data: DataFrame with SMA, EMA, and shifted columns
        :param shiftNumber: int, number of shifts to go from today (default=1) 1 - yesterday, 2 - the day before yesterday...
        :return: DataFrame with "sma/ema_period_shift i" column added
        """

        for i in range(1, shiftNumber + 1):  # loop from 1 to shiftNumber
            data[f"sma_{self.periodSma}_shift{i}"] = data[f"sma_{self.periodSma}"].shift(i)
            data[f"ema_{self.periodEma}_shift{i}"] = data[f"ema_{self.periodEma}"].shift(i)
        return data

    def sma_ema_cross(self, data: pd.DataFrame, shiftConfirm: int = 1) -> pd.DataFrame:
        """
        Detects Golden Cross (buy) and Death Cross (sell) signals.
        A signal is valid only if confirmed across all shifts up to shiftConfirm.

        :param data: DataFrame with SMA, EMA, and shifted columns
        :param shiftConfirm: int, number of past days to confirm the trend (default=1)
        :return: DataFrame with "signal" column added
        """

        # Start with today's condition
        long_signal = (data[f"ema_{self.periodEma}"] > data[f"sma_{self.periodSma}"])
        short_signal = (data[f"ema_{self.periodEma}"] < data[f"sma_{self.periodSma}"])

        # Enforce confirmation from shift1 ... shiftConfirm
        for i in range(1, shiftConfirm + 1):
            ema_shift = f"ema_{self.periodEma}_shift{i}"
            sma_shift = f"sma_{self.periodSma}_shift{i}"

            long_signal &= data[ema_shift] <= data[sma_shift]
            short_signal &= data[ema_shift] >= data[sma_shift]

        # Add "signal" column
        data["signal"] = 0
        data.loc[long_signal, "signal"] = 1  # Buy
        data.loc[short_signal, "signal"] = -1  # Sell

        return data

    def rsi_compute(self,data:pd.DataFrame,rsi_period: int = 14) -> pd.DataFrame:
        # RSI relative strength index
        ## Oversold / overbought
        rsi_period = rsi_period
        data["gain"] = (data["Close"] - data["Open"]).apply(lambda x: x if x > 0 else 0)
        data["loss"] = (data["Close"] - data["Open"]).apply(lambda x: -x if x < 0 else 0)

        data["ema_gain"] = data["gain"].ewm(span=rsi_period, min_periods=rsi_period).mean()
        data["ema_loss"] = data["loss"].ewm(span=rsi_period, min_periods=rsi_period).mean()
        # rs
        data["rs"] = data["ema_loss"] / data["ema_gain"]

        data[f"rsi_{rsi_period}"] = 100 - (100 / (data["rs"] + 1))
        return data

    def run(self, data:pd.DataFrame) -> pd.DataFrame:
        data = self.sma(data)
        data = self.ema(data)
        data = self.shiftData(data,shiftNumber=3)
        data = self.sma_ema_cross(data,shiftConfirm=3)
        data = self.rsi_compute(data,rsi_period=14)
        return data

