from fastapi import FastAPI
# from superrich.data.fetcher import get_stock_price_history
# from superrich.predict.predictor import predict_future

app = FastAPI()

@app.get("/api/stock/{symbol}/history")
def stock_history(symbol: str, start_date: str, end_date: str):
    # df = get_stock_price_history(symbol, start_date, end_date)
    # return df.to_dict(orient="records")
    pass

@app.get("/api/stock/{symbol}/predict")
def stock_predict(symbol: str, days: int = 5):
    # df = get_stock_price_history(symbol, "2023-01-01", "2025-01-01")  # 简化示例
    # pred = predict_future(df, days=days)
    # return pred.to_dict(orient="records")
    pass
