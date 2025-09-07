from .base import PipelineStep
import pandas as pd

class StockTransformation(PipelineStep):
    def __init__(self,periodEma= 10,periodSma = 10):
        """
            :param periodSma: int, Number of Days for Simple Moving Average, e.g. 10, 20, 30
            :param periodEma: int, Number of Days for Exponential Moving Average, e.g. 10, 20, 30
            :param tail: int, Number of
        """
        self.periodSma = periodSma
        self.periodEma = periodEma


    def sma(self, data: pd.DataFrame)-> pd.DataFrame:
        data[f"sma_{self.periodSma}"] = data["Close"].rolling(self.periodSma).mean()
        return data

    def ema(self,data: pd.DataFrame)-> pd.DataFrame:
        data[f"ema_{self.periodEma}"] = data["Close"].ewm(span=self.periodEma, min_periods=self.periodEma).mean()
        return data

    def shiftData(self,data:pd.DataFrame) -> pd.DataFrame:
        data[f"sma_{self.periodSma}shift"] = data[f"sma_{self.periodSma}"].shift(1)
        data[f"ema_{self.periodEma}shift"] = data[f"ema_{self.periodEma}"].shift(1)
        return data

    def sma_ema_cross(self,data:pd.DataFrame)->pd.DataFrame:
        # Long signal (Golden Cross)
        long_signal = (
                (data[f"ema_{self.periodEma}"] > data[f"sma_{self.periodSma}"])
                &
                (data[f"ema_{self.periodEma}shift"] <= data[f"sma_{self.periodSma}shift"])
        ) # Buy
        # Short signal (Death Cross)
        short_signal = (
            (data[f"ema_{self.periodEma}"] < data[f"sma_{self.periodSma}"])
            &
            (data[f"ema_{self.periodEma}shift"] >= data[f"sma_{self.periodSma}shift"])
        )# Sell

        # Add new column "signal" to DataFrame
        data["signal"] = 0
        data.loc[long_signal, "signal"] = 1
        data.loc[short_signal, "signal"] = -1

        return data

    def run(self, data:pd.DataFrame) -> pd.DataFrame:
        data = self.sma(data)
        data = self.ema(data)
        data = self.shiftData(data)
        data = self.sma_ema_cross(data)
        return data

