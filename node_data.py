# -*- coding: utf-8 -*-
from PySide2.QtCore import QObject
from typing import Any, Optional

class NodeData:
    """Базовый класс для данных нод"""
    def __init__(self, data_type: str, data: Any = None):
        self.data_type = data_type
        self.data = data
    
    def type(self) -> str:
        return self.data_type


class FileNodeData(NodeData):
    """Данные для файловой ноды"""
    def __init__(self, file_path: str = ""):
        super().__init__("file", file_path)
        self.file_path = file_path


class ArchiveNodeData(NodeData):
    """Данные для ноды архива"""
    def __init__(self, archive_name: str = "", input_count: int = 1):
        super().__init__("archive", {
            "archive_name": archive_name,
            "input_count": input_count
        })
        self.archive_name = archive_name
        self.input_count = input_count
