#！/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json


class FileReader:
    def __init__(self, filepath):
        self.filepath = filepath

    def exists(self):
        return os.path.isfile(self.filepath)

    def read(self, encoding='utf-8'):
        try:
            if not self.exists():
                return None
            with open(self.filepath, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败: {self.filepath}, 错误: {e}")
            return None

    def read_lines(self, encoding='utf-8'):
        try:
            if not self.exists():
                return None
            with open(self.filepath, 'r', encoding=encoding) as f:
                return f.readlines()
        except Exception as e:
            print(f"读取文件行失败: {self.filepath}, 错误: {e}")
            return None
        
    @staticmethod
    def load_config(path: str="config/config.json"):
        """加载配置文件。

        Args:
            path (str, optional): 配置文件路径, Defaults to "config/config.json".

        Returns:
            _type_: 返回配置字典。
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {path}, 错误: {e}")
            return {}