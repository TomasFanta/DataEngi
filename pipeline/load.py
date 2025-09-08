from .base import PipelineStep
import yfinance as yf


class StockIngestion(PipelineStep):
    def __init__(self, stock_symbols, period="1mo", interval="1d"):
        """
        :param stock_symbols: str or list of str, stock tickers
        :param period: str, e.g. '1d', '5d', '1mo', '6mo', '1y'
        :param interval: str, e.g. '1m', '5m', '1h','4h','1d'
        """
        self.stock_symbols = stock_symbols
        self.period = period
        self.interval = interval

    def run(self, data=None):
        if isinstance(self.stock_symbols, str):
            ticket = yf.Ticker(self.stock_symbols)
            hist = ticket.history(period = self.period, interval = self.interval)
            hist.reset_index(inplace=True)
            hist["Ticker"] = self.stock_symbols
            return hist
        elif isinstance(self.stock_symbols, (list, tuple)):
            tickets = yf.Tickers(self.stock_symbols)
            hist = tickets.history(period = self.period, interval= self.interval)
            hist.reset_index(inplace=True)
            hist = hist.reset_index()
            return (hist)
        else:
            raise ValueError("stock_symbols must be str or list/tuple of str")
