import plotly.express as px
import plotly.graph_objects as go
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
def plot_MACD_stock_signal(data: pd.DataFrame):
    # Ensure we have a Date column from the index
    if "Date" not in data.columns:
        data = data.reset_index()

    # Plot MACD and Signal line
    fig = px.line(data, x="Date", y=["MACD", "MACD_signal"])

    # Add Histogram
    fig.add_trace(go.Bar(
        x=data["Date"],
        y=data["MACD_hist"],
        name="MACD Histogram",
        marker_color="gray",
        opacity=0.4
    ))

    # Make sure the x-axis is treated as dates
    fig.update_xaxes(title="Date", type="date")

    fig.show()


def plot_sma_ema_macd_cross(data: pd.DataFrame):
    # ------------------------
    # Ensure 'Date' column exists
    # ------------------------
    if "Date" not in data.columns:
        data = data.reset_index()  # index becomes 'Date'

    # Ensure numeric columns
    for col in ["Close", "sma_10", "ema_10", "MACD", "MACD_signal", "MACD_hist"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # ------------------------
    # Price chart with SMA/EMA
    # ------------------------
    fig_price = px.line(
        data,
        x="Date",
        y=["Close", "sma_10", "ema_10"],
        title="Price with SMA/EMA"
    )

    # Add vertical lines and annotations for buy and sell signals
    for _, row in data.iterrows():
        dt = row["Date"].to_pydatetime()
        if row.get("MyIndicator") == 1:  # Buy
            fig_price.add_vline(
                x=dt,
                line_color="green",
                opacity=0.3,
                line_dash="dash"
            )
            fig_price.add_annotation(
                x=dt,
                y=row["Close"],
                text="Buy",
                showarrow=True,
                arrowhead=2,
                arrowcolor="green",
                ax=0,
                ay=-30
            )
        elif row.get("MyIndicator") == -1:  # Sell
            fig_price.add_vline(
                x=dt,
                line_color="red",
                opacity=0.3,
                line_dash="dash"
            )
            fig_price.add_annotation(
                x=dt,
                y=row["Close"],
                text="Sell",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                ax=0,
                ay=30
            )

    fig_price.update_xaxes(title="Date", type="date")

    # ------------------------
    # MACD chart with histogram
    # ------------------------
    fig_macd = px.line(
        data,
        x="Date",
        y=["MACD", "MACD_signal"],
        title="MACD with Signal Line"
    )

    # Histogram
    if "MACD_hist" in data.columns:
        fig_macd.add_trace(go.Bar(
            x=data["Date"],
            y=data["MACD_hist"],
            name="MACD Histogram",
            marker_color="gray",
            opacity=0.4
        ))

    # Add vertical lines and annotations for buy and sell signals on MACD chart
    for _, row in data.iterrows():
        dt = row["Date"].to_pydatetime()
        if row.get("MyIndicator") == 1:  # Buy
            fig_macd.add_vline(
                x=dt,
                line_color="green",
                opacity=0.3,
                line_dash="dash"
            )
            fig_macd.add_annotation(
                x=dt,
                y=row["MACD"],
                text="Buy",
                showarrow=True,
                arrowhead=2,
                arrowcolor="green",
                ax=0,
                ay=-30
            )
        elif row.get("MyIndicator") == -1:  # Sell
            fig_macd.add_vline(
                x=dt,
                line_color="red",
                opacity=0.3,
                line_dash="dash"
            )
            fig_macd.add_annotation(
                x=dt,
                y=row["MACD"],
                text="Sell",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                ax=0,
                ay=30
            )

    fig_macd.update_xaxes(title="Date", type="date")

    # ------------------------
    # Show plots
    # ------------------------
    fig_price.show()
    fig_macd.show()