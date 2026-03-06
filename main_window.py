# -*- coding: utf-8 -*-
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QAction, QFileDialog, QGraphicsView, QMainWindow, QMessageBox

from archive_scene import ArchiveScene


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = ArchiveScene()
        self.view = QGraphicsView(self.scene)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("NodeEditor Archive Tool (Python + Qt)")
        self.resize(1200, 800)

        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setCentralWidget(self.view)

        self._setup_menu()
        self._setup_toolbar()

    def _setup_menu(self):
        file_menu = self.menuBar().addMenu("&Файл")

        new_action = QAction("&Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_graph)
        file_menu.addAction(new_action)

        save_action = QAction("&Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_graph)
        file_menu.addAction(save_action)

        load_action = QAction("&Загрузить", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.on_load_graph)
        file_menu.addAction(load_action)

        file_menu.addSeparator()
        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _setup_toolbar(self):
        toolbar = self.addToolBar("Инструменты")

        add_file_action = QAction("Добавить файл", self)
        add_file_action.triggered.connect(self.on_add_file_node)
        toolbar.addAction(add_file_action)

        add_archive_action = QAction("Добавить архив", self)
        add_archive_action.triggered.connect(self.on_add_archive_node)
        toolbar.addAction(add_archive_action)

        toolbar.addSeparator()
        execute_action = QAction("Выполнить", self)
        execute_action.triggered.connect(self.on_execute)
        toolbar.addAction(execute_action)

    def on_new_graph(self):
        for node_id in list(self.scene.nodes.keys()):
            self.scene.remove_node(node_id)

    def on_save_graph(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить граф", "", "JSON (*.json)")
        if not file_name:
            return
        try:
            self.scene.save_to_json(file_name)
            QMessageBox.information(self, "Успех", "Граф сохранен")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить граф: {exc}")

    def on_load_graph(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Загрузить граф", "", "JSON (*.json)")
        if not file_name:
            return
        try:
            self.scene.load_from_json(file_name)
            QMessageBox.information(self, "Успех", "Граф загружен")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить граф: {exc}")

    def on_execute(self):
        success, message = self.scene.execute_archive()
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Результат", message)

    def on_add_file_node(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.scene.add_file_node(center)

    def on_add_archive_node(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.scene.add_archive_node(center)
