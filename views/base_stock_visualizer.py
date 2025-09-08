import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
from utils.logger_manager import get_logger
import os
import pandas as pd
from typing import Optional
import matplotlib.font_manager as fm
from IPython.display import display


font_path = "/System/Library/Fonts/STHeiti Light.ttc"  # macOS 示例
my_font = fm.FontProperties(fname=font_path)

# 初始化日志
logger = get_logger()

import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import os
from typing import Optional

def plot_stock_chart(
    df: pd.DataFrame,
    title: str = "股票K线图",
    save_path: str = None,
    style: Optional[mpf.make_mpf_style] = None,
    figsize: tuple = (12, 8),
):
    """
    使用 mplfinance 绘制股票K线图，并返回图像对象。
    - df: 必须包含 open, high, low, close, volume 列
    - title: 图表标题
    - save_path: 保存路径（如果为 None，则不保存）
    - figsize: 图表大小
    """

    # 自动尝试将 index 转为 DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            logger.info("⚠️ 无法将索引转为时间格式，绘图可能出错。")

    # 确保列名符合 mplfinance 要求
    rename_map = {
        "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume",
        "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume",
    }
    df = df.rename(columns=rename_map)

    # 只保留需要的列
    df = df[["open", "high", "low", "close", "volume"]]

    # 选择默认样式
    if style is None:
        style = mpf.make_mpf_style(base_mpf_style="yahoo")

    # 绘制
    fig, axlist = mpf.plot(
        df,
        type="candle",
        volume=True,
        title=title,
        style=style,
        figsize=figsize,
        returnfig=True
    )

    # 保存图片
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info(f"✅ 已保存图片到: {os.path.abspath(save_path)}")

    return fig
