import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def _get_date_column(data: pd.DataFrame) -> str:
    """Helper to detect correct date column name."""
    if "Date" in data.columns:
        return "Date"
    elif "Datetime" in data.columns:
        return "Datetime"
    else:
        # Reset index if neither is present
        data.reset_index(inplace=True)
        # After reset, assume index column is Date
        return "Date"


def plot_stock_signals(data: pd.DataFrame):
    date_col = _get_date_column(data)
    periodSma = int([c for c in data.columns if "sma_" in c][0].split("_")[1])
    periodEma = int([c for c in data.columns if "ema_" in c and "shift" not in c][0].split("_")[1])

    fig = px.line(data, x=date_col, y=["Close", f"sma_{periodSma}", f"ema_{periodEma}"],
                  title="SMA/EMA Stock Signals")

    for _, row in data[data["signal"] == 1].iterrows():
        fig.add_vline(x=row[date_col], line_color="green", opacity=0.3)
    for _, row in data[data["signal"] == -1].iterrows():
        fig.add_vline(x=row[date_col], line_color="red", opacity=0.3)

    fig.update_xaxes(title="Date", type="date")
    fig.show()


def plot_MACD_stock_signal(data: pd.DataFrame):
    date_col = _get_date_column(data)

    fig = px.line(data, x=date_col, y=["MACD", "MACD_signal"], title="MACD with Signal Line")

    # Add Histogram
    fig.add_trace(go.Bar(
        x=data[date_col],
        y=data["MACD_hist"],
        name="MACD Histogram",
        marker_color="gray",
        opacity=0.4
    ))

    fig.update_xaxes(title="Date", type="date")
    fig.show()


def plot_sma_ema_macd_cross(data: pd.DataFrame):
    # ------------------------
    # Identify correct columns dynamically
    # ------------------------
    date_col = _get_date_column(data)

    # Automatically detect SMA/EMA periods from column names
    periodSma = int([c for c in data.columns if "sma_" in c and "shift" not in c][0].split("_")[1])
    periodEma = int([c for c in data.columns if "ema_" in c and "shift" not in c][0].split("_")[1])

    sma_col = f"sma_{periodSma}"
    ema_col = f"ema_{periodEma}"

    # ------------------------
    # Ensure numeric columns
    # ------------------------
    for col in ["Close", sma_col, ema_col, "MACD", "MACD_signal", "MACD_hist"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # ------------------------
    # Price chart with SMA/EMA
    # ------------------------
    fig_price = px.line(
        data,
        x=date_col,
        y=["Close", sma_col, ema_col],
        title=f"Price with SMA ({periodSma}) / EMA ({periodEma}) and Buy/Sell Signals"
    )

    for _, row in data.iterrows():
        dt = pd.to_datetime(row[date_col])
        if row.get("MyIndicator") == 1:  # Buy
            fig_price.add_vline(x=dt, line_color="green", opacity=0.3, line_dash="dash")
            fig_price.add_annotation(x=dt, y=row["Close"], text="Buy",
                                     showarrow=True, arrowhead=2, arrowcolor="green", ax=0, ay=-30)
        elif row.get("MyIndicator") == -1:  # Sell
            fig_price.add_vline(x=dt, line_color="red", opacity=0.3, line_dash="dash")
            fig_price.add_annotation(x=dt, y=row["Close"], text="Sell",
                                     showarrow=True, arrowhead=2, arrowcolor="red", ax=0, ay=30)

    fig_price.update_xaxes(title="Date", type="date")

    # ------------------------
    # MACD chart with histogram
    # ------------------------
    fig_macd = px.line(
        data,
        x=date_col,
        y=["MACD", "MACD_signal"],
        title="MACD with Signal Line and Buy/Sell Signals"
    )

    # Add Histogram
    if "MACD_hist" in data.columns:
        fig_macd.add_trace(go.Bar(
            x=data[date_col],
            y=data["MACD_hist"],
            name="MACD Histogram",
            marker_color="gray",
            opacity=0.4
        ))

    for _, row in data.iterrows():
        dt = pd.to_datetime(row[date_col])
        if row.get("MyIndicator") == 1:
            fig_macd.add_vline(x=dt, line_color="green", opacity=0.3, line_dash="dash")
            fig_macd.add_annotation(x=dt, y=row["MACD"], text="Buy",
                                    showarrow=True, arrowhead=2, arrowcolor="green", ax=0, ay=-30)
        elif row.get("MyIndicator") == -1:
            fig_macd.add_vline(x=dt, line_color="red", opacity=0.3, line_dash="dash")
            fig_macd.add_annotation(x=dt, y=row["MACD"], text="Sell",
                                    showarrow=True, arrowhead=2, arrowcolor="red", ax=0, ay=30)

    fig_macd.update_xaxes(title="Date", type="date")

    # ------------------------
    # Show Plots
    # ------------------------
    fig_price.show()
    fig_macd.show()


def plot_rsi_index(data: pd.DataFrame):
    # Detect date column automatically
    date_col = _get_date_column(data)

    # Automatically detect RSI column
    rsi_col = [c for c in data.columns if c.startswith("rsi_")]
    if not rsi_col:
        raise ValueError("No RSI column found in the DataFrame.")
    rsi_col = rsi_col[0]

    overbought_level = 70
    oversold_level = 30

    # Base RSI line
    fig = px.line(
        data,
        x=date_col,
        y=rsi_col,
        title=f"RSI ({rsi_col.split('_')[1]}) with Overbought/Oversold Levels",
        labels={rsi_col: "RSI Value", date_col: "Date"}
    )

    # Add horizontal reference lines as traces with legend
    fig.add_trace(go.Scatter(
        x=data[date_col],
        y=[overbought_level] * len(data),
        mode="lines",
        name=f"Overbought ({overbought_level})",
        line=dict(color="green", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=data[date_col],
        y=[oversold_level] * len(data),
        mode="lines",
        name=f"Oversold ({oversold_level})",
        line=dict(color="red", dash="dash")
    ))

    # Improve readability
    fig.update_layout(
        legend_title_text="Legend",
        yaxis_title="RSI Value",
        xaxis_title="Date",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    fig.show()