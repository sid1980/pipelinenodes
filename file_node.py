# -*- coding: utf-8 -*-
import os  # Добавлен недостающий импорт

from PySide2.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
    QPushButton, QLabel, QFileDialog, QApplication
)
from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QFont

from node_data import FileNodeData


class FileNode(QWidget):
    """Виджет для ноды файла"""
    data_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 10)  # Отступ сверху для заголовка
        layout.setSpacing(5)
        
        # Метка с именем файла
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setWordWrap(True)
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
        """)
        
        # Кнопка выбора файла
        self.select_button = QPushButton("Выбрать файл...")
        self.select_button.setMinimumHeight(25)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.select_button.clicked.connect(self.on_select_file)
        
        # Добавляем виджеты в layout
        layout.addWidget(self.file_label)
        layout.addWidget(self.select_button)
        
        self.setLayout(layout)
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        self.setMinimumHeight(80)
        
    def on_select_file(self):
        """Открывает диалог выбора файла как отдельное окно"""
        # Сохраняем позицию главного окна для центрирования диалога
        main_window = None
        parent = self.parent()
        while parent:
            if isinstance(parent, QWidget):
                main_window = parent.window()
                break
            parent = parent.parent()
        
        # Открываем диалог выбора файла
        file_name, _ = QFileDialog.getOpenFileName(
            main_window or self,
            "Выберите файл",
            "",
            "Все файлы (*.*);;Текстовые файлы (*.txt);;Изображения (*.png *.jpg *.bmp)"
        )
        
        if file_name:
            self.file_path = file_name
            # Показываем только имя файла, а полный путь в tooltip
            self.file_label.setText(os.path.basename(file_name))
            self.file_label.setToolTip(file_name)
            self.file_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 1px solid #4CAF50;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 20px;
                    color: #2e7d32;
                }
            """)
            self.data_updated.emit()
    
    def get_data(self) -> FileNodeData:
        """Возвращает данные ноды"""
        return FileNodeData(self.file_path)
    
    def set_data(self, file_path: str):
        """Устанавливает данные ноды"""
        self.file_path = file_path
        if file_path:
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setToolTip(file_path)
            self.file_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f5e8;
                    border: 1px solid #4CAF50;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 20px;
                    color: #2e7d32;
                }
            """)
        else:
            self.file_label.setText("Файл не выбран")
            self.file_label.setToolTip("")
            self.file_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 20px;
                }
            """)
