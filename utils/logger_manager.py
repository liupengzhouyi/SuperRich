#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import json
import os
from typing import Optional, Dict, Any

_logger: Optional[logging.Logger] = None  # 全局 logger 对象


def _setup_logger(config: Dict[str, Any]):
    """
    核心日志初始化逻辑。
    
    Args:
        config (dict): 日志配置字典
    """
    global _logger

    log_config = config.get("logging", {})

    enable_console = log_config.get("enable_console", True)
    enable_file = log_config.get("enable_file", False)
    log_file_path = log_config.get("file_path", "logs/app.log")
    log_level = log_config.get("level", "INFO").upper()
    log_format = log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    log_datefmt = log_config.get("datefmt", "%Y-%m-%d %H:%M:%S")

    # 创建 logger
    logger = logging.getLogger("SuperRichLogger")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.handlers.clear()  # 避免重复添加 handler

    formatter = logging.Formatter(fmt=log_format, datefmt=log_datefmt)

    # 控制台输出
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件输出
    if enable_file:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    _logger.info("Logger initialized successfully.")


def init_logger_from_file(config_path: str):
    """从 JSON 配置文件初始化日志模块。"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    _setup_logger(config)


def init_logger_from_dict(config_dict: Dict[str, Any]):
    """从字典配置初始化日志模块。"""
    
    if not isinstance(config_dict, dict):
        raise ValueError("Config must be a dictionary.")
    try:
        _ = config_dict["logging"]
    except KeyError:
        raise ValueError("Config dictionary must contain a 'logging' key.")
    
    _setup_logger(config_dict)


def get_logger() -> logging.Logger:
    """获取全局 logger 对象。"""
    if _logger is None:
        raise RuntimeError("Logger not initialized. Call init_logger_from_file() or init_logger_from_dict() first.")
    return _logger
