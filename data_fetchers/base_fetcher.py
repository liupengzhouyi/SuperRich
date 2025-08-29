#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """所有数据源驱动的抽象基类"""

    @abstractmethod
    def fetch_data(self, ticker: str, years: int) -> pd.DataFrame:
        """
        获取股票历史数据
        Args:
            ticker (str): 股票代码
            years (int): 向前获取多少年数据
        Returns:
            pd.DataFrame: 包含统一列的数据
        """
        pass
