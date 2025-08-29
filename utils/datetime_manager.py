#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from utils.logger_manager import get_logger


def get_target_start_date(years: int = 5) -> datetime:
    """
    获取目标起始日期：从当前年份向前推 N 年，返回该年份的1月1日。

    Args:
        year (int): 向前推的年份数，默认5年。

    Returns:
        datetime.datetime: 推算出来的起始日期。
    """
    today_ = date.today()
    target_year = today_.year - years
    start_date = datetime(target_year, 1, 1)
    logging = get_logger()
    logging.info(f"Today is {today_}. {years} years ago is {target_year}-01-01.")
    return start_date

def get_target_end_date() -> datetime:
    """
    获取今天日期

    Returns:
        datetime.datetime: 当天日期。
    """
    start_date = datetime.today()
    logging = get_logger()
    logging.info(f"Today is {str(start_date)}.")
    return start_date
