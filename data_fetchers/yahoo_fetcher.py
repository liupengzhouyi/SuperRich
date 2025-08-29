#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from utils.logger_manager import get_logger
from utils.datetime_manager import get_target_start_date, get_target_end_date
from .base_fetcher import BaseFetcher

class YahooFetcher(BaseFetcher):
    """Yahoo Finance 数据源驱动"""

    def __init__(self):
        self.logger = get_logger()

    def fetch_data(self, ticker: str, years: int=5) -> pd.DataFrame:
        """        从 Yahoo Finance 获取指定股票的历史数据。

        Args:
            ticker (str): 股票代码，例如 "AAPL"。
            years (int, optional): 获取过去多少年的数据. Defaults to 5.

        Returns:
            pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame。
            如果没有数据，则返回空 DataFrame。
        """
        
        self.logger.info(f"[YahooFinance] Fetching {years} years of data for {ticker}...")

        # end = datetime.today()
        # start = end - timedelta(days=years * 365)
        
        end = get_target_end_date()
        start = get_target_start_date(years)
        
        self.logger.info(f"[YahooFinance] Start date: {start}, End date: {end}")
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)

        if hist.empty:
            self.logger.warning(f"[YahooFinance] No data found for {ticker}.")
            return pd.DataFrame()

        hist.reset_index(inplace=True)
        hist = hist.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        hist = hist[["date", "open", "high", "low", "close", "volume"]]

        self.logger.info(f"[YahooFinance] Got {len(hist)} rows for {ticker}.")
        return hist
