#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

from utils.logger_manager import get_logger


logger = get_logger()

def filter_stock_data(
    df: pd.DataFrame,
    last_n: int = None,
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
    """
    根据指定条件过滤股票数据 (支持最近N个交易日 或者 指定日期范围)

    Args:
        df (pd.DataFrame): 股票历史数据，index 必须是 DatetimeIndex
        last_n (int, optional): 最近的 N 个交易日，例如 5, 10, 20...
        start_date (str, optional): 起始日期 (YYYY-MM-DD)
        end_date (str, optional): 结束日期 (YYYY-MM-DD)

    Returns:
        pd.DataFrame: 过滤后的股票数据
    """
    if df.empty:
        logger.warning("输入的 DataFrame 为空，直接返回")
        return df

    if not isinstance(df.index, pd.DatetimeIndex):
        logger.error("DataFrame.index 必须是 DatetimeIndex，请检查数据")
        return pd.DataFrame()

    result = df.copy()

    try:
        if last_n is not None:
            result = result.tail(last_n)
            logger.info(f"已获取最近 {last_n} 个交易日的数据，共 {len(result)} 行")

        elif start_date is not None or end_date is not None:
            if start_date:
                start_date = pd.to_datetime(start_date)
            if end_date:
                end_date = pd.to_datetime(end_date)

            result = result.loc[start_date:end_date]
            logger.info(f"已获取 {start_date} 到 {end_date} 之间的数据，共 {len(result)} 行")

        else:
            logger.info("未指定过滤条件，返回完整数据")

    except Exception as e:
        logger.error(f"过滤股票数据时出错: {e}")
        return pd.DataFrame()

    return result
