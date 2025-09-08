from pipeline.load import StockIngestion
from pipeline.transformation import StockTransformation
from pipeline.indicatorMACD import indicatorMACD
from pipeline.output import plot_stock_signals, plot_MACD_stock_signal, plot_sma_ema_macd_cross

def run_pipeline():
    # 1️⃣ Load data
    ingestion = StockIngestion("PPTA","1y","1D")  # or ["PPTA", "AEM"]
    df = ingestion.run()

    # 2️⃣ Transform data
    transform = StockTransformation(periodSma=10, periodEma=10,shiftNumber=2,shiftConfirm=3)
    df = transform.run(df)

    # 2️⃣. 2️⃣Transform data, Add MACD analysis
    macd_analysis = indicatorMACD(slowEma=26,fastEma= 12)
    df_macd_analysis = macd_analysis.run(df)

    # 3️⃣ Output / visualize
    plot_stock_signals(df)
    plot_MACD_stock_signal(df_macd_analysis)
    plot_sma_ema_macd_cross(df_macd_analysis)

if __name__ == "__main__":
    run_pipeline()
