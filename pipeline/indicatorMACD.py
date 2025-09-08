from .base import PipelineStep
import pandas as pd

class indicatorMACD(PipelineStep):
    def __init__(self, slowEma: int = 26, fastEma: int = 12, periodSignal: int = 9):
        """
        :param fastEma: int, Number of days for fast Exponential Moving Average (default=12)
        :param slowEma: int, Number of days for slow Exponential Moving Average (default=26)
        :param periodSignal: int, Number of days for MACD signal line (default=9)
        """
        self.slowEma = slowEma
        self.fastEma = fastEma
        self.periodSignal = periodSignal

    def emaCompute(self, data: pd.DataFrame) -> pd.DataFrame:
        data[f"ema_{self.fastEma}"] = data["Close"].ewm(
            span=self.fastEma, min_periods=self.fastEma
        ).mean()
        data[f"ema_{self.slowEma}"] = data["Close"].ewm(
            span=self.slowEma, min_periods=self.slowEma
        ).mean()
        return data

    def macdSignalLine(self, data: pd.DataFrame) -> pd.DataFrame:
        # MACD line
        data["MACD"] = data[f"ema_{self.fastEma}"] - data[f"ema_{self.slowEma}"]

        # Signal line
        data["MACD_signal"] = data["MACD"].ewm(
            span=self.periodSignal, min_periods=self.periodSignal
        ).mean()

        # Previous signal line for cross detection
        data["MACD_signal_prev"] = data["MACD_signal"].shift(1)

        # Histogram
        data["MACD_hist"] = data["MACD"] - data["MACD_signal"]
        return data

    def sma_ema_macd_cross(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Custom strategy:
        - Buy when MACD < Signal, Signal declining, EMA10 below SMA10,
          and both EMA10/SMA10 below Close
        """
        def _row_logic(row):
            cross = (
                (row["MACD_signal"] <= row["MACD_signal_prev"]) and
                (row["MACD"] <= row["MACD_signal"]) and
                ("ema_10" in row and "sma_10" in row) and
                (row["ema_10"] <= row["sma_10"]) and
                (row["ema_10"] < row["Close"]) and
                (row["sma_10"] < row["Close"])
            )
            return 1 if cross else 0

        data["MyIndicator"] = data.apply(_row_logic, axis=1)
        return data

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.emaCompute(data)
        data = self.macdSignalLine(data)
        data = self.sma_ema_macd_cross(data)
        return data
