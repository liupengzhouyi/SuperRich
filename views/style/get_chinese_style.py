import mplfinance as mpf
import matplotlib.font_manager as fm
import os
import platform

from utils.logger_manager import get_logger


def get_chinese_style(font_path: str = None):
    """
    获取支持中文显示的 mplfinance 风格样式
    自动识别操作系统并选择默认中文字体
    
    Args:
        font_path (str, optional): 字体文件路径。
            - 如果为 None，函数会自动根据操作系统选择默认字体：
              * macOS: /System/Library/Fonts/STHeiti Light.ttc
              * Windows: C:/Windows/Fonts/simhei.ttf
              * Linux: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
    
    Returns:
        mpf.mpf_style: 可直接用于 mpf.plot 的 style
    """
    if font_path is None:
        system_name = platform.system()
        print("检测到操作系统:", system_name)
        if system_name == "Darwin":  # macOS
            font_path = "/System/Library/Fonts/STHeiti Light.ttc"
        elif system_name == "Windows":
            font_path = "C:/Windows/Fonts/simhei.ttf"
        elif system_name == "Linux":
            font_path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
        else:
            raise RuntimeError(f"未知系统: {system_name}，请手动传入字体路径。")

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"未找到字体文件: {font_path}，请手动传入字体路径。")

    # 加载字体
    my_font = fm.FontProperties(fname=font_path)

    # 创建 mplfinance style
    style = mpf.make_mpf_style(
        rc={
            "font.family": my_font.get_name(),
            "axes.unicode_minus": False  # 避免负号显示问题
        }
    )

    return style

