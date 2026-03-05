# -*- coding: utf-8 -*-
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QSpinBox, QLabel, QPushButton, QFileDialog
)
from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QFont

from node_data import ArchiveNodeData


class ArchiveNode(QWidget):
    """Виджет для ноды архива"""
    ports_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 10)  # Отступ сверху для заголовка
        layout.setSpacing(8)
        
        # Поле для имени архива
        name_layout = QHBoxLayout()
        name_label = QLabel("Имя:")
        name_label.setFixedWidth(40)
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.archive_name_edit = QLineEdit()
        self.archive_name_edit.setPlaceholderText("имя_архива")
        self.archive_name_edit.textChanged.connect(self.on_name_changed)
        self.archive_name_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.archive_name_edit)
        
        # Поле для количества входов
        count_layout = QHBoxLayout()
        count_label = QLabel("Входов:")
        count_label.setFixedWidth(40)
        count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.input_count_spin = QSpinBox()
        self.input_count_spin.setMinimum(1)
        self.input_count_spin.setMaximum(10)
        self.input_count_spin.setValue(1)
        self.input_count_spin.valueChanged.connect(self.on_input_count_changed)
        self.input_count_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.input_count_spin)
        
        # Кнопка выбора места сохранения
        self.path_button = QPushButton("Выбрать папку...")
        self.path_button.setMinimumHeight(25)
        self.path_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.path_button.clicked.connect(self.on_select_path)
        
        # Метка для отображения выбранного пути
        self.path_label = QLabel("Путь не выбран")
        self.path_label.setWordWrap(True)
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
                font-size: 10px;
            }
        """)
        
        layout.addLayout(name_layout)
        layout.addLayout(count_layout)
        layout.addWidget(self.path_button)
        layout.addWidget(self.path_label)
        
        self.setLayout(layout)
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        self.setMinimumHeight(150)
        
        self.save_path = ""
        
    def on_name_changed(self, text):
        """Обработчик изменения имени архива"""
        self.ports_changed.emit()
    
    def on_input_count_changed(self, value):
        """Обработчик изменения количества входов"""
        self.ports_changed.emit()
    
    def on_select_path(self):
        """Открывает диалог выбора папки для сохранения"""
        main_window = None
        parent = self.parent()
        while parent:
            if isinstance(parent, QWidget):
                main_window = parent.window()
                break
            parent = parent.parent()
        
        # Открываем диалог выбора папки
        path = QFileDialog.getExistingDirectory(
            main_window or self,
            "Выберите папку для сохранения архива",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if path:
            self.save_path = path
            self.path_label.setText(path)
            self.path_label.setToolTip(path)
            self.path_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    border: 1px solid #2196F3;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 20px;
                    color: #0d47a1;
                }
            """)
    
    def get_data(self) -> ArchiveNodeData:
        """Возвращает данные ноды"""
        return ArchiveNodeData(
            self.archive_name_edit.text(),
            self.input_count_spin.value()
        )
    
    def set_data(self, archive_name: str, input_count: int, save_path: str = ""):
        """Устанавливает данные ноды"""
        self.archive_name_edit.setText(archive_name)
        self.input_count_spin.setValue(input_count)
        
        if save_path:
            self.save_path = save_path
            self.path_label.setText(save_path)
            self.path_label.setToolTip(save_path)
            self.path_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    border: 1px solid #2196F3;
                    border-radius: 3px;
                    padding: 5px;
                    min-height: 20px;
                    color: #0d47a1;
                }
            """)
