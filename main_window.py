# -*- coding: utf-8 -*-
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (
    QAction,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QGraphicsView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from archive_scene import ArchiveScene, NodeItem
from archive_node import ArchiveNode
from file_node import FileNode


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = ArchiveScene()
        self.view = QGraphicsView(self.scene)
        self.selected_node = None

        self.settings_stack = None
        self.empty_settings = None
        self.file_settings = None
        self.archive_settings = None

        self.file_path_edit = None
        self.archive_name_edit = None
        self.archive_inputs_spin = None
        self.archive_save_path_edit = None
        self.archive_execute_btn = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("NodeEditor Archive Tool (Python + Qt)")
        self.resize(1300, 800)

        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setCentralWidget(self.view)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_settings_panel()

        self.scene.selectionChanged.connect(self.on_scene_selection_changed)
        self.scene.execution_finished.connect(self.on_archive_execution_finished)

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

        delete_action = QAction("Удалить выбранное", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(self.on_delete_selected)
        toolbar.addAction(delete_action)

    def _setup_settings_panel(self):
        dock = QDockWidget("Настройки выбранной ноды", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.settings_stack = QStackedWidget()
        self.empty_settings = self._build_empty_settings()
        self.file_settings = self._build_file_settings()
        self.archive_settings = self._build_archive_settings()

        self.settings_stack.addWidget(self.empty_settings)
        self.settings_stack.addWidget(self.file_settings)
        self.settings_stack.addWidget(self.archive_settings)
        self.settings_stack.setCurrentWidget(self.empty_settings)

        container_layout.addWidget(self.settings_stack)
        dock.setWidget(container)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _build_empty_settings(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Выберите ноду, чтобы настроить параметры")
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch()
        return widget

    def _build_file_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)

        browse_btn = QPushButton("Открыть файл...")
        browse_btn.clicked.connect(self.on_browse_file)

        layout.addRow("Путь к файлу:", self.file_path_edit)
        layout.addRow("", browse_btn)
        return widget

    def _build_archive_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.archive_name_edit = QLineEdit()
        self.archive_name_edit.textChanged.connect(self.on_archive_name_changed)

        self.archive_inputs_spin = QSpinBox()
        self.archive_inputs_spin.setMinimum(1)
        self.archive_inputs_spin.setMaximum(10)
        self.archive_inputs_spin.valueChanged.connect(self.on_archive_inputs_changed)

        self.archive_save_path_edit = QLineEdit()
        self.archive_save_path_edit.setReadOnly(True)

        save_path_btn = QPushButton("Выбрать папку...")
        save_path_btn.clicked.connect(self.on_browse_save_path)

        self.archive_execute_btn = QPushButton("Выполнить")
        self.archive_execute_btn.clicked.connect(self.on_execute_selected_archive)

        layout.addRow("Имя архива:", self.archive_name_edit)
        layout.addRow("Кол-во входов:", self.archive_inputs_spin)
        layout.addRow("Папка сохранения:", self.archive_save_path_edit)
        layout.addRow("", save_path_btn)
        layout.addRow("", self.archive_execute_btn)

        return widget

    def on_scene_selection_changed(self):
        selected_items = self.scene.selectedItems()
        node_item = next((item for item in selected_items if isinstance(item, NodeItem)), None)
        self.selected_node = node_item

        if not node_item:
            self.settings_stack.setCurrentWidget(self.empty_settings)
            return

        if isinstance(node_item.widget, FileNode):
            self.settings_stack.setCurrentWidget(self.file_settings)
            self.file_path_edit.setText(node_item.widget.file_path)
            return

        if isinstance(node_item.widget, ArchiveNode):
            self.settings_stack.setCurrentWidget(self.archive_settings)
            self.archive_name_edit.blockSignals(True)
            self.archive_inputs_spin.blockSignals(True)
            self.archive_name_edit.setText(node_item.widget.archive_name_edit.text())
            self.archive_inputs_spin.setValue(node_item.widget.input_count_spin.value())
            self.archive_save_path_edit.setText(node_item.widget.save_path)
            self.archive_name_edit.blockSignals(False)
            self.archive_inputs_spin.blockSignals(False)
            return

        self.settings_stack.setCurrentWidget(self.empty_settings)

    def on_browse_file(self):
        if not self.selected_node or not isinstance(self.selected_node.widget, FileNode):
            return

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Все файлы (*.*);;Текстовые файлы (*.txt);;Изображения (*.png *.jpg *.bmp)",
        )
        if not file_name:
            return

        self.selected_node.widget.set_data(file_name)
        self.file_path_edit.setText(file_name)

    def on_browse_save_path(self):
        if not self.selected_node or not isinstance(self.selected_node.widget, ArchiveNode):
            return

        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения архива",
            "",
            QFileDialog.ShowDirsOnly,
        )
        if not path:
            return

        self.selected_node.widget.save_path = path
        self.selected_node.widget.path_label.setText(path)
        self.selected_node.widget.path_label.setToolTip(path)
        self.archive_save_path_edit.setText(path)

    def on_archive_name_changed(self, text):
        if not self.selected_node or not isinstance(self.selected_node.widget, ArchiveNode):
            return
        self.selected_node.widget.archive_name_edit.setText(text)

    def on_archive_inputs_changed(self, value):
        if not self.selected_node or not isinstance(self.selected_node.widget, ArchiveNode):
            return
        self.selected_node.widget.input_count_spin.setValue(value)

    def on_new_graph(self):
        for node_id in list(self.scene.nodes.keys()):
            self.scene.remove_node(node_id)
        self.selected_node = None
        self.settings_stack.setCurrentWidget(self.empty_settings)

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
            self.on_scene_selection_changed()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить граф: {exc}")

    def on_execute(self):
        success, message = self.scene.execute_archive()
        self.on_archive_execution_finished(success, message)

    def on_execute_selected_archive(self):
        if not self.selected_node or not isinstance(self.selected_node.widget, ArchiveNode):
            QMessageBox.warning(self, "Результат", "Выберите архивную ноду")
            return
        success, message = self.scene.execute_archive(self.selected_node.node_id)
        self.on_archive_execution_finished(success, message)

    def on_delete_selected(self):
        selected_nodes = [item for item in self.scene.selectedItems() if isinstance(item, NodeItem)]
        if not selected_nodes:
            return
        for node in selected_nodes:
            self.scene.remove_node(node.node_id)
        self.selected_node = None
        self.settings_stack.setCurrentWidget(self.empty_settings)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_delete_selected()
            event.accept()
            return
        super().keyPressEvent(event)

    def on_archive_execution_finished(self, success: bool, message: str):
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Результат", message)

    def on_add_file_node(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        node_id = self.scene.add_file_node(center)
        self._select_node(node_id)

    def on_add_archive_node(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        node_id = self.scene.add_archive_node(center)
        self._select_node(node_id)

    def _select_node(self, node_id: str):
        node = self.scene.nodes.get(node_id)
        if not node:
            return
        self.scene.clearSelection()
        node.setSelected(True)
        self.on_scene_selection_changed()
