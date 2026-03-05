# -*- coding: utf-8 -*-
import json
import os
import shutil
import tarfile
import tempfile
from typing import Dict, List, Optional, Tuple

from PySide2.QtCore import QPointF, Signal, QObject, Qt, QRectF, QLineF
from PySide2.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsItem, 
    QGraphicsTextItem, QGraphicsProxyWidget, QWidget,
    QGraphicsRectItem, QGraphicsLineItem
)
from PySide2.QtGui import QPen, QBrush, QColor, QPainter, QFont, QLinearGradient, QPainterPath

from file_node import FileNode
from archive_node import ArchiveNode
from node_data import FileNodeData, ArchiveNodeData


class PortItem(QGraphicsItem):
    """Графический элемент для порта"""
    def __init__(self, port_type: str, index: int, parent=None):
        super().__init__(parent)
        self.port_type = port_type  # "input" или "output"
        self.index = index
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        
    def boundingRect(self):
        return QRectF(-8, -8, 16, 16)
    
    def paint(self, painter, option, widget=None):
        # Рисуем порт
        if self.port_type == "input":
            color = QColor(76, 175, 80)  # зеленый для входа
        else:
            color = QColor(244, 67, 54)  # красный для выхода
            
        # Подсветка при наведении
        if option.state & QGraphicsItem.ItemIsSelected:
            painter.setBrush(QBrush(color.lighter(150)))
            painter.setPen(QPen(Qt.white, 2))
        elif option.state & QGraphicsItem.ItemIsHovered:
            painter.setBrush(QBrush(color.lighter(130)))
            painter.setPen(QPen(Qt.white, 2))
        else:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.black, 1))
            
        painter.drawEllipse(-6, -6, 12, 12)


class NodeItem(QGraphicsItem):
    """Графический элемент для ноды"""
    def __init__(self, node_id: str, title: str, widget: QWidget, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.title = title
        self.widget = widget
        self.proxy = None
        self.input_ports = []
        self.output_ports = []
        self.input_connections = {}
        self.output_connections = {}
        
        # Настройка внешнего вида
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        
        # Устанавливаем размер ноды
        self.width = 280
        self.height = 120
        
        # Создаем прокси для виджета
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(widget)
        self.proxy.setPos(10, 30)
        self.proxy.setZValue(0)
        
        # Создаем порты
        self.setup_ports()
        
    def setup_ports(self):
        """Создает порты для ноды"""
        # Удаляем старые порты
        for port in self.input_ports + self.output_ports:
            if port.scene():
                self.scene().removeItem(port)
        
        self.input_ports.clear()
        self.output_ports.clear()
        
        # Определяем порты на основе типа ноды
        if isinstance(self.widget, FileNode):
            # Один выходной порт
            port = PortItem("output", 0, self)
            port.setPos(self.width - 15, 60)
            self.output_ports.append(port)
            
        elif isinstance(self.widget, ArchiveNode):
            # Входные порты
            count = self.widget.input_count_spin.value()
            for i in range(count):
                port = PortItem("input", i, self)
                port.setPos(15, 45 + i * 30)
                self.input_ports.append(port)
            
            # Выходной порт
            port = PortItem("output", 0, self)
            port.setPos(self.width - 15, 45 + (count * 15))
            self.output_ports.append(port)
            
            # Обновляем высоту ноды
            self.height = 70 + count * 30
            self.proxy.setPos(10, 30)
    
    def boundingRect(self):
        """Возвращает ограничивающий прямоугольник"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        """Отрисовывает ноду"""
        # Создаем градиент для фона
        gradient = QLinearGradient(0, 0, 0, self.height)
        if self.isSelected():
            gradient.setColorAt(0, QColor(220, 220, 250))
            gradient.setColorAt(1, QColor(200, 200, 230))
        elif option.state & QGraphicsItem.ItemIsHovered:
            gradient.setColorAt(0, QColor(250, 250, 250))
            gradient.setColorAt(1, QColor(230, 230, 230))
        else:
            gradient.setColorAt(0, QColor(240, 240, 240))
            gradient.setColorAt(1, QColor(220, 220, 220))
        
        # Рисуем фон
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)
        
        # Рисуем заголовок
        header_gradient = QLinearGradient(0, 0, 0, 25)
        header_gradient.setColorAt(0, QColor(100, 100, 150))
        header_gradient.setColorAt(1, QColor(80, 80, 130))
        
        painter.setBrush(QBrush(header_gradient))
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.drawRoundedRect(1, 1, self.width - 2, 24, 5, 5)
        
        # Рисуем текст заголовка
        painter.setPen(Qt.white)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(10, 18, self.title)
        
        # Рисуем разделительную линию
        painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
        painter.drawLine(5, 26, self.width - 5, 26)
    
    def get_port_position(self, port_type: str, index: int) -> QPointF:
        """Возвращает позицию порта в мировых координатах"""
        if port_type == "input" and index < len(self.input_ports):
            return self.input_ports[index].scenePos()
        elif port_type == "output" and index < len(self.output_ports):
            return self.output_ports[index].scenePos()
        return self.scenePos()
    
    def itemChange(self, change, value):
        """Обновляет соединения при перемещении"""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Обновляем все соединения
            for conn_id in list(self.input_connections.keys()) + list(self.output_connections.keys()):
                if conn_id in self.scene().connections:
                    self.scene().connections[conn_id].updatePath()
        return super().itemChange(change, value)


class ConnectionItem(QGraphicsItem):
    """Графический элемент для соединения"""
    def __init__(self, conn_id: str, start_node: NodeItem, end_node: NodeItem,
                 start_port: int, end_port: int, parent=None):
        super().__init__(parent)
        self.conn_id = conn_id
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port
        self.setZValue(-1)
        self.path = QPainterPath()
        
    def boundingRect(self):
        """Возвращает ограничивающий прямоугольник"""
        return self.path.boundingRect().adjusted(-10, -10, 10, 10)
    
    def updatePath(self):
        """Обновляет путь соединения"""
        if not self.start_node or not self.end_node:
            return
            
        start = self.start_node.get_port_position("output", self.start_port)
        end = self.end_node.get_port_position("input", self.end_port)
        
        self.prepareGeometryChange()
        
        self.path = QPainterPath()
        self.path.moveTo(start)
        
        # Контрольные точки для кривой
        dx = abs(end.x() - start.x()) * 0.5
        ctrl1 = QPointF(start.x() + dx, start.y())
        ctrl2 = QPointF(end.x() - dx, end.y())
        
        self.path.cubicTo(ctrl1, ctrl2, end)
        self.update()
    
    def paint(self, painter, option, widget=None):
        """Отрисовывает соединение"""
        self.updatePath()
        
        # Создаем градиент для линии
        gradient = QLinearGradient(self.path.pointAtPercent(0), self.path.pointAtPercent(1))
        gradient.setColorAt(0, QColor(100, 100, 255))
        gradient.setColorAt(1, QColor(50, 50, 200))
        
        pen = QPen(QBrush(gradient), 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Рисуем кривую
        painter.drawPath(self.path)


class ArchiveScene(QGraphicsScene):
    """Сцена для редактора нод"""
    node_added = Signal(object)
    node_removed = Signal(str)
    connection_added = Signal(str, str, str, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: Dict[str, NodeItem] = {}
        self.connections: Dict[str, ConnectionItem] = {}
        self.next_node_id = 0
        self.temp_connection_line = None
        self.temp_connection_start = None
        
        # Устанавливаем фон
        self.setBackgroundBrush(QBrush(QColor(50, 50, 50)))
        
        # Создаем сетку
        self.setSceneRect(-5000, -5000, 10000, 10000)
        
    def drawBackground(self, painter, rect):
        """Рисует фон с сеткой"""
        super().drawBackground(painter, rect)
        
        # Рисуем сетку
        painter.setPen(QPen(QColor(80, 80, 80), 0.5))
        
        left = int(rect.left()) - (int(rect.left()) % 50)
        top = int(rect.top()) - (int(rect.top()) % 50)
        
        # Вертикальные линии
        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += 50
        
        # Горизонтальные линии
        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += 50
        
        # Рисуем более темные линии каждые 250 пикселей
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        x = left - (left % 250)
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += 250
        
        y = top - (top % 250)
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += 250
    
    def add_file_node(self, pos: QPointF) -> str:
        """Добавляет ноду файла"""
        node_id = f"file_{self.next_node_id}"
        self.next_node_id += 1
        
        widget = FileNode()
        widget.data_updated.connect(lambda: self.on_node_updated(node_id))
        
        node = NodeItem(node_id, "Файл", widget)
        node.setPos(pos)
        
        self.addItem(node)
        self.nodes[node_id] = node
        self.node_added.emit(node)
        
        return node_id
    
    def add_archive_node(self, pos: QPointF) -> str:
        """Добавляет ноду архива"""
        node_id = f"archive_{self.next_node_id}"
        self.next_node_id += 1
        
        widget = ArchiveNode()
        widget.ports_changed.connect(lambda: self.on_node_ports_changed(node_id))
        
        node = NodeItem(node_id, "Архив", widget)
        node.setPos(pos)
        
        self.addItem(node)
        self.nodes[node_id] = node
        self.node_added.emit(node)
        
        return node_id
    
    def on_node_updated(self, node_id: str):
        """Обработчик обновления данных ноды"""
        node = self.nodes.get(node_id)
        if node:
            node.update()
    
    def on_node_ports_changed(self, node_id: str):
        """Обработчик изменения количества портов"""
        node = self.nodes.get(node_id)
        if node:
            # Удаляем все соединения с измененной нодой
            to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.start_node == node or conn.end_node == node:
                    to_remove.append(conn_id)
            
            for conn_id in to_remove:
                self.remove_connection(conn_id)
            
            # Обновляем порты ноды
            node.setup_ports()
            node.update()
    
    def add_connection(self, start_node_id: str, end_node_id: str,
                      start_port: int, end_port: int) -> Optional[str]:
        """Добавляет соединение между нодами"""
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return None
        
        start_node = self.nodes[start_node_id]
        end_node = self.nodes[end_node_id]
        
        # Проверяем совместимость типов
        if not isinstance(start_node.widget, FileNode) or not isinstance(end_node.widget, ArchiveNode):
            return None
        
        # Проверяем, не существует ли уже такое соединение
        for conn in self.connections.values():
            if (conn.start_node == start_node and conn.end_node == end_node and
                conn.start_port == start_port and conn.end_port == end_port):
                return None
        
        conn_id = f"conn_{len(self.connections)}"
        connection = ConnectionItem(conn_id, start_node, end_node, start_port, end_port)
        
        self.addItem(connection)
        self.connections[conn_id] = connection
        
        # Сохраняем информацию о соединении в нодах
        end_node.input_connections[conn_id] = (start_node_id, start_port, end_port)
        start_node.output_connections[conn_id] = (end_node_id, start_port, end_port)
        
        self.connection_added.emit(conn_id, start_node_id, end_node_id, start_port, end_port)
        
        return conn_id
    
    def remove_connection(self, conn_id: str):
        """Удаляет соединение"""
        if conn_id in self.connections:
            conn = self.connections[conn_id]
            
            # Удаляем информацию из нод
            if conn.start_node and conn.end_node:
                if conn_id in conn.start_node.output_connections:
                    del conn.start_node.output_connections[conn_id]
                if conn_id in conn.end_node.input_connections:
                    del conn.end_node.input_connections[conn_id]
            
            self.removeItem(conn)
            del self.connections[conn_id]
    
    def remove_node(self, node_id: str):
        """Удаляет ноду и все связанные соединения"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # Удаляем все соединения, связанные с этой нодой
            to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.start_node == node or conn.end_node == node:
                    to_remove.append(conn_id)
            
            for conn_id in to_remove:
                self.remove_connection(conn_id)
            
            self.removeItem(node)
            del self.nodes[node_id]
            self.node_removed.emit(node_id)
    
    def mousePressEvent(self, event):
        """Обработчик нажатия мыши для создания соединений"""
        item = self.itemAt(event.scenePos(), QTransform())
        
        if isinstance(item, PortItem):
            # Начинаем создание соединения
            self.temp_connection_start = (item.parentItem(), item.port_type, item.index)
            
            # Создаем временную линию
            self.temp_connection_line = QGraphicsLineItem()
            self.temp_connection_line.setPen(QPen(QColor(100, 100, 255), 2, Qt.DashLine))
            self.addItem(self.temp_connection_line)
            
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработчик движения мыши для отображения временного соединения"""
        if self.temp_connection_start and self.temp_connection_line:
            start_node, start_type, start_index = self.temp_connection_start
            start_pos = start_node.get_port_position(start_type, start_index)
            
            line = QLineF(start_pos, event.scenePos())
            self.temp_connection_line.setLine(line)
            
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обработчик отпускания мыши для завершения создания соединения"""
        if self.temp_connection_start:
            # Удаляем временную линию
            if self.temp_connection_line:
                self.removeItem(self.temp_connection_line)
                self.temp_connection_line = None
            
            item = self.itemAt(event.scenePos(), QTransform())
            
            if isinstance(item, PortItem):
                start_node, start_type, start_index = self.temp_connection_start
                end_node = item.parentItem()
                end_type = item.port_type
                end_index = item.index
                
                # Проверяем корректность соединения
                if (start_type == "output" and end_type == "input" and
                    isinstance(start_node.widget, FileNode) and
                    isinstance(end_node.widget, ArchiveNode)):
                    self.add_connection(start_node.node_id, end_node.node_id, start_index, end_index)
                elif (start_type == "input" and end_type == "output" and
                      isinstance(end_node.widget, FileNode) and
                      isinstance(start_node.widget, ArchiveNode)):
                    self.add_connection(end_node.node_id, start_node.node_id, end_index, start_index)
            
            self.temp_connection_start = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def save_to_json(self, file_path: str):
        """Сохраняет граф в JSON файл"""
        data = {
            "nodes": [],
            "connections": []
        }
        
        # Сохраняем ноды
        for node_id, node in self.nodes.items():
            node_data = {
                "id": node_id,
                "type": "file" if isinstance(node.widget, FileNode) else "archive",
                "pos_x": node.pos().x(),
                "pos_y": node.pos().y()
            }
            
            # Сохраняем данные виджета
            if isinstance(node.widget, FileNode):
                node_data["file_path"] = node.widget.file_path
            elif isinstance(node.widget, ArchiveNode):
                node_data["archive_name"] = node.widget.archive_name_edit.text()
                node_data["input_count"] = node.widget.input_count_spin.value()
                node_data["save_path"] = node.widget.save_path
            
            data["nodes"].append(node_data)
        
        # Сохраняем соединения
        for conn_id, conn in self.connections.items():
            conn_data = {
                "id": conn_id,
                "start_node": conn.start_node.node_id,
                "end_node": conn.end_node.node_id,
                "start_port": conn.start_port,
                "end_port": conn.end_port
            }
            data["connections"].append(conn_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_json(self, file_path: str):
        """Загружает граф из JSON файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Очищаем сцену
        for node_id in list(self.nodes.keys()):
            self.remove_node(node_id)
        
        # Загружаем ноды
        node_map = {}  # для маппинга старых ID на новые
        for node_data in data["nodes"]:
            pos = QPointF(node_data["pos_x"], node_data["pos_y"])
            
            if node_data["type"] == "file":
                new_id = self.add_file_node(pos)
                node = self.nodes[new_id]
                node.widget.set_data(node_data.get("file_path", ""))
            else:  # archive
                new_id = self.add_archive_node(pos)
                node = self.nodes[new_id]
                node.widget.set_data(
                    node_data.get("archive_name", ""),
                    node_data.get("input_count", 1),
                    node_data.get("save_path", "")
                )
            
            node_map[node_data["id"]] = new_id
        
        # Загружаем соединения
        for conn_data in data["connections"]:
            if conn_data["start_node"] in node_map and conn_data["end_node"] in node_map:
                self.add_connection(
                    node_map[conn_data["start_node"]],
                    node_map[conn_data["end_node"]],
                    conn_data["start_port"],
                    conn_data["end_port"]
                )
    
    def execute_archive(self) -> tuple:
        """Выполняет архивацию"""
        archive_nodes = []
        
        # Находим все ArchiveNode
        for node_id, node in self.nodes.items():
            if isinstance(node.widget, ArchiveNode):
                archive_nodes.append(node)
        
        if not archive_nodes:
            return False, "Нет нод архива для выполнения"
        
        success_count = 0
        errors = []
        
        for archive_node in archive_nodes:
            try:
                # Собираем файлы из подключенных FileNode
                files = []
                for conn_id, (start_node_id, start_port, end_port) in archive_node.input_connections.items():
                    start_node = self.nodes.get(start_node_id)
                    if start_node and isinstance(start_node.widget, FileNode):
                        if start_node.widget.file_path:
                            files.append(start_node.widget.file_path)
                
                if not files:
                    errors.append("Нет файлов для архивации")
                    continue
                
                archive_name = archive_node.widget.archive_name_edit.text()
                if not archive_name:
                    errors.append("Не указано имя архива")
                    continue
                
                save_path = archive_node.widget.save_path
                if not save_path:
                    errors.append("Не указан путь для сохранения архива")
                    continue
                
                # Создаем временную директорию
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Копируем файлы
                    for file_path in files:
                        if os.path.exists(file_path):
                            shutil.copy2(file_path, temp_dir)
                    
                    # Создаем архив
                    archive_filename = archive_name
                    if not archive_filename.endswith('.tar.gz'):
                        archive_filename += '.tar.gz'
                    
                    archive_path = os.path.join(save_path, archive_filename)
                    
                    with tarfile.open(archive_path, 'w:gz') as tar:
                        for file_name in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file_name)
                            tar.add(file_path, arcname=file_name)
                    
                    success_count += 1
                    
            except Exception as e:
                errors.append(str(e))
        
        if success_count > 0:
            return True, f"Успешно создано архивов: {success_count}"
        else:
            return False, "Ошибка: " + ", ".join(errors)
