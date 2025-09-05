#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd

from utils.logger_manager import init_logger_from_file
from utils.logger_manager import init_logger_from_dict
from utils.logger_manager import get_logger
from utils.file_reader import FileReader


# 读取配置文件
config_file_path = "config/config.json"
my_config = FileReader.load_config(path=config_file_path)

# 初始化日志
# init_logger_from_file(config_path=config_file_path)
init_logger_from_dict(config_dict=my_config)
logger = get_logger()
logger.info("日志初始化完成")

# 读取数据源配置
data_source = my_config.get("data_source", {})
if isinstance(data_source, dict) and 0 != len(data_source.keys()):
    logger.info(f"数据源配置: {json.dumps(data_source, ensure_ascii=False, indent=2)}")
else:
    logger.warning("数据源配置为空，请检查配置文件。")

from data_fetchers.data_factory import DataFactory
data_factory = DataFactory(config=my_config)
data_factory.info()

STOCK_CODE = "NVDA"
stock_data = data_factory.GET_STOCK_DATA(STOCK_CODE, "2024-01-01", "2025-01-01")

print(type(stock_data))
print(stock_data.head())
print(stock_data.tail())

# print(stock_data.describe())
# 生成一个缓存路径
# print(data_factory._cache_file_path("TSLA", "2020-01-01", "2025-01-01"))

from views.base_stock_visualizer import visualize_stock_candlestick
visualize_stock_candlestick(stock_data, title=STOCK_CODE, save_path="output/HOOD_candlestick.png")