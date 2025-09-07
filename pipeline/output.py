import plotly.express as px
import pandas as pd

def plot_stock_signals(data: pd.DataFrame):
    periodSma = int([c for c in data.columns if "sma_" in c][0].split("_")[1])
    periodEma = int([c for c in data.columns if "ema_" in c and "shift" not in c][0].split("_")[1])

    fig = px.line(data, x="Date", y=["Close", f"sma_{periodSma}", f"ema_{periodEma}"])

    for _, row in data[data["signal"]==1].iterrows():
        fig.add_vline(x=row["Date"], line_color="green", opacity=0.3)  # Buy
    for _, row in data[data["signal"]==-1].iterrows():
        fig.add_vline(x=row["Date"], line_color="red", opacity=0.3)    # Sell

    fig.show()
