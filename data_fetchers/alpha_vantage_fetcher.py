#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from utils.logger_manager import get_logger
from .base_fetcher import BaseFetcher


class AlphaVantageFetcher(BaseFetcher):
    """Alpha Vantage 数据源驱动"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = get_logger()
        self.base_url = "https://www.alphavantage.co/query"
        self.logger.warning(f"AlphaVantageFetcher 初始化完成; Alpha Vantage API Key [{self.api_key[-6:]}]")

    def fetch_data(self, ticker: str, years: int) -> pd.DataFrame:
        self.logger.info(f"[AlphaVantage] Fetching {years} years of data for {ticker}...")

        # url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "full",
            "apikey": self.api_key
        }

        resp = requests.get(self.base_url, params=params)
        data = resp.json()

        if "Time Series (Daily)" not in data:
            self.logger.error(f"Alpha Vantage API error: {data}")
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "6. volume": "volume"
        })
        df = df[["open", "high", "low", "close", "volume"]].sort_index()

        # 过滤N年数据
        start_date = datetime.now() - timedelta(days=years * 365)
        df = df[df.index >= start_date]

        df.reset_index(inplace=True)
        df.rename(columns={"index": "date"}, inplace=True)

        self.logger.info(f"[AlphaVantage] Got {len(df)} rows for {ticker}.")
        return df

    def GET_STOCK_DATA_BY_DATE_WINDOWS(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        """获取指定股票在指定日期范围内的历史数据

        Args:
            STOCK_CODE (str): 股票代码
            START_DATE (str): 起始日期 (格式: YYYY-MM-DD)
            END_DATE (str): 结束日期 (格式: YYYY-MM-DD)

        Returns:
            pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame。
        """
        self.logger.info(f"[AlphaVantage] Fetching data for {STOCK_CODE} from {START_DATE} to {END_DATE}...")

        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": STOCK_CODE,
            "outputsize": "full",  # 获取全部历史数据
            "apikey": self.api_key,
        }

        try:
            self.logger.debug(f"[AlphaVantage] Request params: {params}")
            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code != 200:
                self.logger.error(f"[AlphaVantage] Request failed with status {response.status_code}")
                response.raise_for_status()

            data = response.json()

            if "Time Series (Daily)" not in data:
                self.logger.error(f"[AlphaVantage] Invalid response: {data}")
                raise ValueError(f"Unexpected API response: {data}")

            self.logger.info("[AlphaVantage] Parsing data into DataFrame...")

            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            df = df.rename(columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "6. volume": "volume"
            })
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()  # 时间升序
            df = df.loc[START_DATE:END_DATE]  # 截取日期范围
            df = df.astype(float)

            self.logger.info(f"[AlphaVantage] Successfully fetched {len(df)} rows for {STOCK_CODE}.")
            self.logger.debug(f"[AlphaVantage] Sample data:\n{df.head()}")

            return df.reset_index().rename(columns={"index": "date"})

        except Exception as e:
            self.logger.exception(f"[AlphaVantage] Failed to fetch stock data for {STOCK_CODE}: {e}")
            return pd.DataFrame()


    def GET_FULL_STOCK_DATA(self, STOCK_CODE: str) -> pd.DataFrame:
        """获取指定股票的全部历史数据

        Args:
            STOCK_CODE (str): 股票代码

        Returns:
            pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame。
        """
        self.logger.info(f"[AlphaVantage] Fetching full data for {STOCK_CODE}...")

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": STOCK_CODE,
            "outputsize": "full",  # 获取全部历史数据
            "apikey": self.api_key,
        }

        try:
            self.logger.debug(f"[AlphaVantage] Request params: {params}")
            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code != 200:
                self.logger.error(f"[AlphaVantage] Request failed with status {response.status_code}")
                response.raise_for_status()

            data = response.json()

            if "Time Series (Daily)" not in data:
                self.logger.error(f"[AlphaVantage] Invalid response: {data}")
                raise ValueError(f"Unexpected API response: {data}")

            self.logger.info("[AlphaVantage] Parsing data into DataFrame...")

            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
            df = df.rename(columns={
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "6. volume": "volume"
            })
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()  # 时间升序
            df = df.astype(float)

            self.logger.info(f"[AlphaVantage] Successfully fetched {len(df)} rows for {STOCK_CODE}.")
            self.logger.debug(f"[AlphaVantage] Sample data:\n{df.head()}")

            return df.reset_index().rename(columns={"index": "date"})

        except Exception as e:
            self.logger.exception(f"[AlphaVantage] Failed to fetch stock data for {STOCK_CODE}: {e}")
            return pd.DataFrame()   
        
    def get_date_info_from_df(self, df: pd.DataFrame) -> tuple:
        """从 DataFrame 中获取起始和结束日期

        Args:
            df (pd.DataFrame): 包含日期列的 DataFrame

        Returns:
            tuple: (start_date, end_date) 格式为 (YYYY-MM-DD, YYYY-MM-DD)
        """
        if df.empty or "date" not in df.columns:
            self.logger.warning("[AlphaVantage] DataFrame is empty or missing 'date' column.")
            return None, None

        start_date = df["date"].min().strftime("%Y-%m-%d")
        end_date = df["date"].max().strftime("%Y-%m-%d")

        self.logger.info(f"[AlphaVantage] Data date range: {start_date} to {end_date}")
        return start_date, end_date
    
    def gen_cache_file_name(self, STOCK_CODE: str, DATES: tuple) -> str:
        """生成缓存文件名

        Args:
            STOCK_CODE (str): 股票代码
            DATES (tuple): (start_date, end_date) 格式为 (YYYY-MM-DD, YYYY-MM-DD)

        Returns:
            str: 缓存文件名，例如 "AAPL_2020-01-01_2025-01-01.csv"
        """
        start_date, end_date = DATES
        if not start_date or not end_date:
            self.logger.error("[AlphaVantage] Invalid dates provided for cache file name generation.")
            start_date = "unknown_start"
            end_date = "unknown_end"
        file_name = f"{STOCK_CODE}_{start_date}_{end_date}.csv"
        self.logger.info(f"[AlphaVantage] Generated cache file name: {file_name}")
        return file_name
       
    
    def save_data_to_csv(self, df: pd.DataFrame, file_path: str) -> bool:
        """将数据保存到 CSV 文件

        Args:
            df (pd.DataFrame): 要保存的数据
            file_path (str): 保存的文件路径
        """
        self.logger.info(f"[AlphaVantage] Saving data to {file_path}...")
        try:
            df.to_csv(file_path, index=False)
            self.logger.info(f"[AlphaVantage] Data saved to {file_path}")
        except Exception as e:
            self.logger.exception(f"[AlphaVantage] Failed to save data to {file_path}: {e}")
        # 检查是否保存成功，通过文件是否存在判断    
        return os.path.exists(file_path)
            
        
            
    def save(self, STOCK_CODE: str, df: pd.DataFrame) -> bool:
        """保存数据到缓存

        Args:
            STOCK_CODE (str): 股票代码
            df (pd.DataFrame): 要保存的数据
        """
        
        self.logger.info(f"[AlphaVantage] Saving data for {STOCK_CODE}...")
        if df.empty:
            self.logger.warning(f"[AlphaVantage] No data to save for {STOCK_CODE}.")
            return

        start_date, end_date = self.get_date_info_from_df(df)
        cache_file_name = self.gen_cache_file_name(STOCK_CODE, (start_date, end_date))
        cache_dir = "data_cache"
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        file_path = os.path.join(cache_dir, cache_file_name)
        save_status = self.save_data_to_csv(df, file_path)
        return save_status
        