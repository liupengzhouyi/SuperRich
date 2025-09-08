#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import json
from datetime import datetime, timedelta
import pandas as pd

from utils.logger_manager import get_logger
from data_fetchers.alpha_vantage_fetcher import AlphaVantageFetcher
from data_fetchers.yahoo_fetcher import YahooFetcher


logger = get_logger()

class DataFactory:
    """
    股票数据工厂类：根据配置决定使用缓存还是API驱动来获取数据
    """

    def __init__(self, config: dict):
        """
        初始化数据工厂
        :param config: dict 配置参数，包含数据源、缓存策略等
        """
        self.config = config.get("data_source", {})
        self.cache_config = self.config.get("data_cache", {})
        self.data_driver = self.config.get("data_driver", "yahoo_finance")
        self.data_drivers = self.config.get("data_drivers", [])
        self.first_data_drive = self.config.get("frist_data_drive", "data_cache")
        self.years = self.config.get("years", 5)
        self.alpha_vantage_api_keys = self.get_alpha_vantage_api_keys()

        logger.info("DataFactory 初始化完成")

    def _cache_file_path(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        生成缓存文件路径
        :param ticker: 股票代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 缓存文件完整路径
        """
        file_name_style = self.cache_config.get("file_name_style", "{ticker}_{start}_{end}.csv")
        file_name = file_name_style.format(ticker=ticker, start_date=start_date, end_date=end_date)
        cache_dir = self.cache_config.get("cache_dir", "data_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, file_name)

    def _is_cache_valid(self, file_path: str) -> bool:
        """
        判断缓存是否有效
        :param file_path: 缓存文件路径
        :return: True / False
        """
        if not os.path.exists(file_path):
            return False

        expiration_days = self.cache_config.get("expiration_days", 7)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        if datetime.now() - file_mtime > timedelta(days=expiration_days):
            logger.info(f"缓存文件 {file_path} 已过期")
            return False
        logger.info(f"缓存文件 {file_path} 有效，直接使用")
        return True

    def info(self) -> str:
        """
        打印数据工厂的运行逻辑
        """
        info_str = "\n"
        info_str = info_str + "=== DataFactory 信息 ===" + "\n"
        info_str = info_str + f"数据优先级 (frist_data_drive): {self.first_data_drive}" + "\n"
        info_str = info_str + f"当前使用的数据驱动: {self.data_driver}" + "\n"
        info_str = info_str + f"可选数据驱动列表: {self.data_drivers}" + "\n"
        info_str = info_str + f"缓存配置: {json.dumps(self.cache_config, indent=4, ensure_ascii=False)}" + "\n"
        info_str = info_str + f"默认获取数据年限: {self.years} 年" + "\n"
        info_str = info_str + "=======================" + "\n"
        print(info_str)
        return info_str

    def get_all_cache_files_name(self) -> list:
        """获取所有缓存文件名

        Returns:
            list: 缓存文件名列表
        """
        
        logger.info("获取所有缓存文件名")
        cache_dir = self.cache_config.get("cache_dir", "data_cache")
        if not os.path.exists(cache_dir):
            logger.warning(f"缓存目录 {cache_dir} 不存在")
            return []
        all_stock_cache_file_names = [f for f in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir, f))]
        logger.info(f"找到 {len(all_stock_cache_file_names)} 个缓存文件")
        return all_stock_cache_file_names
    
    def get_target_cache_files_name(self, STOCK_CODE: str) -> list:
        """获取指定股票的缓存文件名

        Args:
            STOCK_CODE (str): 股票代码

        Returns:
            list: 缓存文件名列表
        """
        
        logger.info(f"获取 {STOCK_CODE} 的缓存文件列表")
        all_cache_files = self.get_all_cache_files_name()
        target_cache_files = [f for f in all_cache_files if f.startswith(STOCK_CODE)]
        logger.info(f"找到 {len(target_cache_files)} 个 {STOCK_CODE} 的缓存文件")
        return target_cache_files
    
    def check_date_windows(self, START_DATE: str, END_DATE: str) -> bool:
        """检查日期范围是否合法

        Args:
            START_DATE (str): 起始日期 (格式: YYYY-MM-DD)
            END_DATE (str): 结束日期 (格式: YYYY-MM-DD)

        Returns:
            bool: True 合法, False 不合法
        """
        check_status = False
        logger.info(f"检查日期范围是否合法: {START_DATE} 到 {END_DATE}")
        try:
            today_dt = datetime.now()
            start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
            end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")
            if start_dt > today_dt or end_dt > today_dt:
                logger.error("日期不能晚于今天")
                return check_status
            if start_dt >= end_dt:
                logger.error("起始日期必须早于结束日期")
                return check_status
            check_status = True
        except ValueError as ve:
            logger.error(f"日期格式错误: {ve}")
        return check_status
    
    def check_cache_data(self, STOCK_CODE: str, START_DATE: str, END_DATE: str, cache_files: list=[]) -> bool:
        """检查指定股票在指定日期范围内是否有有效的缓存数据

        Args:
            STOCK_CODE (str): 股票代码
            START_DATE (str): 开始日期
            END_DATE (str): 结束日期
            cache_files (list, optional): 缓存文件名列表. Defaults to [].

        Returns:
            bool: True 有效缓存, False 无效缓存
        """
        check_status = False
        logger.info(f"检查 {STOCK_CODE} 在 {START_DATE} 到 {END_DATE} 之间是否有有效的缓存数据")
        for index, cache_file_name in enumerate(cache_files):
            if not cache_file_name.startswith(STOCK_CODE):
                continue
            parts = cache_file_name.replace(".csv", "").split("_")
            if len(parts) < 3:
                logger.warning(f"{str(index)}. 缓存文件名格式不正确: {cache_file_name}")
                continue
            try:
                file_start_date = parts[1]
                file_end_date = parts[2]
                if file_start_date <= START_DATE and file_end_date >= END_DATE:
                    file_path = os.path.join(self.cache_config.get("cache_dir", "data_cache"), cache_file_name)
                    if os.path.exists(file_path):
                        logger.info(f"{str(index)}. 找到有效缓存文件: {cache_file_name}")
                        check_status = True
                        break
                    else:
                        logger.warning(f"{str(index)}. 缓存文件不存在: {cache_file_name}")
            except Exception as e:
                logger.error(f"{str(index)}. 解析缓存文件名时出错: {e}")
        return check_status
    
    def get_alpha_vantage_api_keys(self) -> list:
        """获取 Alpha Vantage API Key 列表

        Returns:
            list: API Key 列表
        """
        api_key_info = self.config.get("alpha_vantage_api_key_info", {})
        api_keys = []
        api_key_file_path = api_key_info.get("api_key_file_path", "")
        if api_key_file_path and os.path.exists(api_key_file_path):
            try:
                with open(api_key_file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "Alpha Vantage" in data.keys():
                        utrus_api_keys = data.get("Alpha Vantage", [])
                        for item in utrus_api_keys:
                            if isinstance(item, dict) and "ALPHA_VANTAGE_API_KEY" in item.keys():
                                key = item.get("ALPHA_VANTAGE_API_KEY", "")
                                if key and key not in api_keys:
                                    api_keys.append(key)
                    elif isinstance(data, list):
                        api_keys = data
                logger.info(f"从文件 {api_key_file_path} 读取到 {len(api_keys)} 个 API Key")
            except Exception as e:
                logger.error(f"读取 API Key 文件时出错: {e}")
        else:
            single_api_key = api_key_info.get("api_key", "")
            if single_api_key:
                api_keys.append(single_api_key)
                logger.info("从配置中读取到单个 API Key")
            else:
                logger.warning("未配置任何 Alpha Vantage API Key")
        return api_keys
    
    
    def GET_STOCK_DATA(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        
        logger.info(f"请求股票数据: {STOCK_CODE}, 从 {START_DATE} 到 {END_DATE}")
        logger.info(f"先检查数据优先级: {self.first_data_drive}")
        used_api_get_data = False
        if self.first_data_drive == "data_cache" and self.cache_config.get("enabled", False):
            logger.info("优先使用缓存数据")
            # 获取指定股票的缓存文件名
            target_cache_files_name = self.get_target_cache_files_name(STOCK_CODE)
            # 查看缓存是否存在且有效
            if self.check_cache_data(STOCK_CODE, START_DATE, END_DATE, target_cache_files_name):
                logger.info("找到有效缓存，使用缓存数据")
                return self.GET_STOCK_DATA_FROM_CACHE(STOCK_CODE, START_DATE, END_DATE)
            else:
                logger.warning("未找到有效缓存，使用API数据驱动")
                used_api_get_data = True
        else:
            logger.info("跳过缓存，直接使用API数据驱动")
            used_api_get_data = True
        if used_api_get_data:
            logger.info(f"使用数据驱动: {self.data_driver} 获取数据")
            data_driver = self.data_driver
            if data_driver == "yahoo_finance":
                return self.GET_STOCK_DATA_FROM_yahoo_finance(STOCK_CODE, START_DATE, END_DATE)
            elif data_driver == "alpha_vantage":
                return self.GET_STOCK_DATA_FROM_alpha_vantage(STOCK_CODE, START_DATE, END_DATE)
            else:
                logger.error(f"未知的数据驱动: {data_driver}, 无法获取数据;可以支持的配置有: {self.data_drivers}")
                return None
        else:
            logger.error("不使用缓存且不使用API数据驱动，无法获取数据")
            return None
    
    
    def GET_STOCK_DATA_FROM_CACHE_V0(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        
        log_info = f"从缓存获取 {STOCK_CODE} 在 {START_DATE} 到 {END_DATE} 之间的数据"
        logger.info(log_info)
        
        cache_file_path = self._cache_file_path(STOCK_CODE, START_DATE, END_DATE)
        cache_file_path = "data_cache/AAPL_1999-11-01_2025-08-28.csv"
        if not os.path.exists(cache_file_path):
            logger.error(f"缓存文件不存在: {cache_file_path}")
            return pd.DataFrame()
        try:
            df = pd.read_csv(cache_file_path)
            if df.empty:
                logger.warning(f"缓存文件为空: {cache_file_path}")
                return pd.DataFrame()
            logger.info(f"成功从缓存文件读取数据: {cache_file_path}, 共 {len(df)} 行")
            return df
        except Exception as e:
            logger.error(f"读取缓存文件时出错: {e}")
            return pd.DataFrame()
        
    def GET_STOCK_DATA_FROM_CACHE(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        log_info = f"从缓存获取 {STOCK_CODE} 在 {START_DATE} 到 {END_DATE} 之间的数据"
        logger.info(log_info)

        cache_file_path = self._cache_file_path(STOCK_CODE, START_DATE, END_DATE)
        cache_file_path = "data_cache/AAPL_1999-11-01_2025-08-28.csv"

        if not os.path.exists(cache_file_path):
            logger.error(f"缓存文件不存在: {cache_file_path}")
            return pd.DataFrame()

        try:
            # ✅ 读取时直接解析日期并设为索引
            df = pd.read_csv(cache_file_path, parse_dates=["date"], index_col="date")

            if df.empty:
                logger.warning(f"缓存文件为空: {cache_file_path}")
                return pd.DataFrame()

            # 确认索引是 DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            logger.info(f"成功从缓存文件读取数据: {cache_file_path}, 共 {len(df)} 行")
            return df

        except Exception as e:
            logger.error(f"读取缓存文件时出错: {e}")
            return pd.DataFrame()

    
    def GET_STOCK_DATA_FROM_alpha_vantage(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        """获取指定股票在指定日期范围内的历史数据 by Alpha Vantage

        Args:
            STOCK_CODE (str): 股票代码
            START_DATE (str): 起始日期 (格式: YYYY-MM-DD)
            END_DATE (str): 结束日期 (格式: YYYY-MM-DD)

        Returns:
            pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame。
        """
        
        log_info = f"从 Alpha Vantage 获取 {STOCK_CODE} 在 {START_DATE} 到 {END_DATE} 之间的数据"
        logger.info(log_info)
        
        for api_key in self.alpha_vantage_api_keys:
            if not api_key:
                continue
            logger.info(f"使用 Alpha Vantage API Key: {api_key[-6:]} 获取数据")
            try:
                alpha_vantage_fetcher = AlphaVantageFetcher(api_key=api_key)
                stock_data = alpha_vantage_fetcher.GET_FULL_STOCK_DATA(STOCK_CODE)
                need_save = True
                if need_save:
                    save_status = alpha_vantage_fetcher.save(STOCK_CODE, stock_data)
                    if save_status:
                        logger.info(f"数据保存成功")
                    else:
                        logger.warning(f"数据保存失败")
                return stock_data
            except Exception as e:
                logger.error(f"使用 API Key {api_key[-6:]} 获取数据时出错: {e}")
                continue
        return None
    
    def GET_STOCK_DATA_FROM_yahoo_finance(self, STOCK_CODE: str, START_DATE: str, END_DATE: str) -> pd.DataFrame:
        """获取指定股票在指定日期范围内的历史数据 by Yahoo Finance
        Args:
            STOCK_CODE (str): 股票代码
            START_DATE (str): 起始日期 (格式: YYYY-MM-DD)
            END_DATE (str): 结束日期 (格式: YYYY-MM-DD)
        Returns:
            pd.DataFrame: 包含日期、开盘价、最高价、最低价、收盘价和成交量的 DataFrame。
        """
        
        log_info = f"从 Yahoo Finance 获取 {STOCK_CODE} 在 {START_DATE} 到 {END_DATE} 之间的数据"
        logger.info(log_info)
        
        pass
    