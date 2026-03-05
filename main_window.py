# -*- coding: utf-8 -*-
from PySide2.QtWidgets import (
    QMainWindow, QMenuBar, QToolBar, QAction, 
    QGraphicsView, QFileDialog, QMessageBox, QVBoxLayout, QWidget
)
from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QPainter

from archive_scene import ArchiveScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.view = None
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("NodeEditor Archive Tool")
        self.resize(1024, 768)
        
        self.setup_menu()
        self.setup_toolbar()
        self.setup_scene()
        
    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&Файл")
        
        # Новый граф
        new_action = QAction("&Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_graph)
        file_menu.addAction(new_action)
        
        # Сохранить
        save_action = QAction("&Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_graph)
        file_menu.addAction(save_action)
        
        # Загрузить
        load_action = QAction("&Загрузить", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.on_load_graph)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_toolbar(self):
        """Настройка панели инструментов"""
        toolbar = self.addToolBar("Инструменты")
        
        # Добавить файл
        add_file_action = QAction("Добавить файл", self)
        add_file_action.triggered.connect(self.on_add_file_node)
        toolbar.addAction(add_file_action)
        
        # Добавить архив
        add_archive_action = QAction("Добавить архив", self)
        add_archive_action.triggered.connect(self.on_add_archive_node)
        toolbar.addAction(add_archive_action)
        
        toolbar.addSeparator()
        
        # Выполнить
        execute_action = QAction("Выполнить", self)
        execute_action.triggered.connect(self.on_execute)
        toolbar.addAction(execute_action)
    
    def setup_scene(self):
        """Настройка сцены и представления"""
        self.scene = ArchiveScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        
        self.setCentralWidget(self.view)
    
    def on_new_graph(self):
        """Обработчик создания нового графа"""
        # Очищаем сцену
        for node_id in list(self.scene.nodes.keys()):
            self.scene.remove_node(node_id)
    
    def on_save_graph(self):
        """Обработчик сохранения графа"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить граф", "", "JSON файлы (*.json)"
        )
        
        if file_name:
            try:
                self.scene.save_to_json(file_name)
                QMessageBox.information(self, "Успех", "Граф успешно сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить граф: {str(e)}")
    
    def on_load_graph(self):
        """Обработчик загрузки графа"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Загрузить граф", "", "JSON файлы (*.json)"
        )
        
        if file_name:
            try:
                self.scene.load_from_json(file_name)
                QMessageBox.information(self, "Успех", "Граф успешно загружен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить граф: {str(e)}")
    
    def on_execute(self):
        """Обработчик выполнения архивации"""
        success, message = self.scene.execute_archive()
        
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Результат", message)
    
    def on_add_file_node(self):
        """Обработчик добавления ноды файла"""
        # Получаем центр текущего вида
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.scene.add_file_node(center)
    
    def on_add_archive_node(self):
        """Обработчик добавления ноды архива"""
        center = self.view.mapToScene(self.view.viewport().rect().center())
        # Смещаем немного, чтобы ноды не накладывались
        center += QPointF(250, 0)
        self.scene.add_archive_node(center)
    
    def wheelEvent(self, event):
        """Обработчик колесика мыши для масштабирования"""
        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            
            # Сохраняем позицию под курсором
            if event.angleDelta().y() > 0:
                self.view.scale(zoom_in_factor, zoom_in_factor)
            else:
                self.view.scale(zoom_out_factor, zoom_out_factor)
        else:
            super().wheelEvent(event)
