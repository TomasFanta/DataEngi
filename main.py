from pipeline.load import StockIngestion
from pipeline.transformation import StockTransformation
from pipeline.output import plot_stock_signals

def run_pipeline():
    # 1️⃣ Load data
    ingestion = StockIngestion("PPTA","1y","1d")  # or ["PPTA", "AEM"]
    df = ingestion.run()

    # 2️⃣ Transform data
    transform = StockTransformation(periodSma=10, periodEma=10)
    df_transformed = transform.run(df)

    # 3️⃣ Output / visualize
    plot_stock_signals(df_transformed)

if __name__ == "__main__":
    run_pipeline()
