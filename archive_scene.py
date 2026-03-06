# -*- coding: utf-8 -*-
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide2.QtCore import QPointF, QRectF, Qt, QLineF, Signal
from PySide2.QtGui import QBrush, QColor, QPainterPath, QPen, QTransform
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsProxyWidget, QGraphicsScene

from archive_node import ArchiveNode
from file_node import FileNode


class NodeEditorStyle:
    """Минимальный загрузчик цветов из 3rdparty/nodeeditor/resources/DefaultStyle.json."""

    def __init__(self):
        self.background = QColor(53, 53, 53)
        self.fine_grid = QColor(60, 60, 60)
        self.coarse_grid = QColor(75, 75, 75)
        self.connection = QColor(120, 140, 240)
        self.connection_selected = QColor(180, 200, 255)
        self.node_bg = QColor(90, 90, 90)
        self.node_title = QColor(35, 35, 35)
        self.node_border = QColor(25, 25, 25)
        self.node_border_selected = QColor(255, 165, 0)
        self._load_default_style()

    def _load_default_style(self):
        style_path = Path(__file__).resolve().parent / "3rdparty" / "nodeeditor" / "resources" / "DefaultStyle.json"
        if not style_path.exists():
            return

        try:
            style_data = json.loads(style_path.read_text(encoding="utf-8"))
            scene = style_data.get("GraphicsViewStyle", {})
            connection = style_data.get("ConnectionStyle", {})
            node = style_data.get("NodeStyle", {})

            self.background = QColor(*scene.get("BackgroundColor", [53, 53, 53]))
            self.fine_grid = QColor(*scene.get("FineGridColor", [60, 60, 60]))
            self.coarse_grid = QColor(*scene.get("CoarseGridColor", [75, 75, 75]))
            self.connection = QColor(*connection.get("ConstructionColor", [120, 140, 240]))
            self.connection_selected = QColor(*connection.get("SelectedHaloColor", [180, 200, 255]))
            self.node_bg = QColor(*node.get("NormalBoundaryColor", [90, 90, 90]))
            self.node_title = QColor(*node.get("GradientColor0", [35, 35, 35]))
            self.node_border = QColor(*node.get("NormalBoundaryColor", [25, 25, 25]))
            self.node_border_selected = QColor(*node.get("SelectedBoundaryColor", [255, 165, 0]))
        except Exception:
            pass


class PortItem(QGraphicsItem):
    def __init__(self, port_type: str, index: int, parent=None):
        super().__init__(parent)
        self.port_type = port_type
        self.index = index
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(-7, -7, 14, 14)

    def paint(self, painter, option, widget=None):
        color = QColor(69, 190, 87) if self.port_type == "input" else QColor(220, 85, 65)
        if option.state & QGraphicsItem.ItemIsSelectable:
            color = color.lighter(120)
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(self.boundingRect())


class NodeItem(QGraphicsItem):
    def __init__(self, node_id: str, title: str, widget, style: NodeEditorStyle):
        super().__init__()
        self.node_id = node_id
        self.title = title
        self.widget = widget
        self.style = style
        self.width = 300
        self.height = 130
        self.input_ports: List[PortItem] = []
        self.output_ports: List[PortItem] = []
        self.input_connections: Dict[str, Tuple[str, int, int]] = {}
        self.output_connections: Dict[str, Tuple[str, int, int]] = {}

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(widget)
        self.proxy.setPos(10, 28)

        self.setup_ports()

    def setup_ports(self):
        self.input_ports.clear()
        self.output_ports.clear()

        if isinstance(self.widget, FileNode):
            output = PortItem("output", 0, self)
            output.setPos(self.width - 14, self.height / 2)
            self.output_ports.append(output)
            return

        count = self.widget.input_count_spin.value() if isinstance(self.widget, ArchiveNode) else 1
        self.height = 85 + count * 28
        for index in range(count):
            input_port = PortItem("input", index, self)
            input_port.setPos(14, 48 + index * 24)
            self.input_ports.append(input_port)

        output = PortItem("output", 0, self)
        output.setPos(self.width - 14, self.height / 2)
        self.output_ports.append(output)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        border_color = self.style.node_border_selected if self.isSelected() else self.style.node_border
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(self.style.node_bg))
        painter.drawRoundedRect(self.boundingRect(), 7, 7)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.style.node_title))
        painter.drawRoundedRect(QRectF(1, 1, self.width - 2, 24), 6, 6)

        painter.setPen(Qt.white)
        painter.drawText(QRectF(8, 1, self.width - 16, 24), Qt.AlignVCenter, self.title)

    def get_port_position(self, port_type: str, index: int) -> QPointF:
        ports = self.input_ports if port_type == "input" else self.output_ports
        if 0 <= index < len(ports):
            return ports[index].scenePos()
        return self.scenePos()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for conn_id in [*self.input_connections.keys(), *self.output_connections.keys()]:
                conn = self.scene().connections.get(conn_id)
                if conn:
                    conn.update_path()
        return super().itemChange(change, value)


class ConnectionItem(QGraphicsItem):
    def __init__(self, conn_id: str, start_node: NodeItem, end_node: NodeItem, start_port: int, end_port: int, style: NodeEditorStyle):
        super().__init__()
        self.conn_id = conn_id
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port
        self.style = style
        self.path = QPainterPath()
        self.setZValue(-1)
        self.update_path()

    def update_path(self):
        start = self.start_node.get_port_position("output", self.start_port)
        end = self.end_node.get_port_position("input", self.end_port)
        dx = abs(end.x() - start.x()) * 0.5
        self.prepareGeometryChange()
        self.path = QPainterPath(start)
        self.path.cubicTo(QPointF(start.x() + dx, start.y()), QPointF(end.x() - dx, end.y()), end)

    def boundingRect(self):
        return self.path.boundingRect().adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget=None):
        self.update_path()
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.style.connection, 2.0))
        painter.drawPath(self.path)


class ArchiveScene(QGraphicsScene):
    node_added = Signal(object)
    node_removed = Signal(str)
    connection_added = Signal(str, str, str, int, int)
    execution_finished = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.style = NodeEditorStyle()
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.setBackgroundBrush(QBrush(self.style.background))

        self.nodes: Dict[str, NodeItem] = {}
        self.connections: Dict[str, ConnectionItem] = {}
        self.next_node_id = 0
        self.temp_connection_start = None
        self.temp_connection_line: Optional[QGraphicsLineItem] = None

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        left = int(rect.left()) - (int(rect.left()) % 25)
        top = int(rect.top()) - (int(rect.top()) % 25)

        painter.setPen(QPen(self.style.fine_grid, 0.5))
        x = left
        while x <= rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += 25
        y = top
        while y <= rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += 25

        painter.setPen(QPen(self.style.coarse_grid, 1))
        x = left - (left % 100)
        while x <= rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += 100
        y = top - (top % 100)
        while y <= rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += 100

    def add_file_node(self, pos: QPointF) -> str:
        node_id = f"file_{self.next_node_id}"
        self.next_node_id += 1
        widget = FileNode()
        node = NodeItem(node_id, "Файл", widget, self.style)
        node.setPos(pos)
        self.addItem(node)
        self.nodes[node_id] = node
        self.node_added.emit(node)
        return node_id

    def add_archive_node(self, pos: QPointF) -> str:
        node_id = f"archive_{self.next_node_id}"
        self.next_node_id += 1
        widget = ArchiveNode()
        node = NodeItem(node_id, "Архив", widget, self.style)
        widget.ports_changed.connect(lambda: self.on_node_ports_changed(node_id))
        widget.execute_requested.connect(lambda: self.execute_archive_node(node_id))
        node.setPos(pos)
        self.addItem(node)
        self.nodes[node_id] = node
        self.node_added.emit(node)
        return node_id

    def on_node_ports_changed(self, node_id: str):
        node = self.nodes.get(node_id)
        if not node:
            return

        preserved_input_links = []
        new_input_count = node.widget.input_count_spin.value() if isinstance(node.widget, ArchiveNode) else 1
        for conn_id, (start_node_id, start_port, end_port) in list(node.input_connections.items()):
            if end_port < new_input_count:
                preserved_input_links.append((start_node_id, start_port, end_port))
            self.remove_connection(conn_id)

        for conn_id in list(node.output_connections.keys()):
            self.remove_connection(conn_id)

        node.setup_ports()
        node.update()

        for start_node_id, start_port, end_port in preserved_input_links:
            self.add_connection(start_node_id, node_id, start_port, end_port)

    def add_connection(self, start_node_id: str, end_node_id: str, start_port: int, end_port: int) -> Optional[str]:
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return None

        start_node = self.nodes[start_node_id]
        end_node = self.nodes[end_node_id]
        if not isinstance(start_node.widget, FileNode) or not isinstance(end_node.widget, ArchiveNode):
            return None

        conn_id = f"conn_{len(self.connections)}"
        connection = ConnectionItem(conn_id, start_node, end_node, start_port, end_port, self.style)
        self.addItem(connection)
        self.connections[conn_id] = connection

        start_node.output_connections[conn_id] = (end_node_id, start_port, end_port)
        end_node.input_connections[conn_id] = (start_node_id, start_port, end_port)
        self.connection_added.emit(conn_id, start_node_id, end_node_id, start_port, end_port)
        return conn_id

    def remove_connection(self, conn_id: str):
        conn = self.connections.pop(conn_id, None)
        if not conn:
            return
        conn.start_node.output_connections.pop(conn_id, None)
        conn.end_node.input_connections.pop(conn_id, None)
        self.removeItem(conn)

    def remove_node(self, node_id: str):
        node = self.nodes.pop(node_id, None)
        if not node:
            return
        for conn_id in list(node.input_connections.keys()) + list(node.output_connections.keys()):
            self.remove_connection(conn_id)
        self.removeItem(node)
        self.node_removed.emit(node_id)

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if isinstance(item, PortItem):
            self.temp_connection_start = (item.parentItem(), item.port_type, item.index)
            self.temp_connection_line = QGraphicsLineItem()
            self.temp_connection_line.setPen(QPen(self.style.connection, 2, Qt.DashLine))
            self.addItem(self.temp_connection_line)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection_start and self.temp_connection_line:
            start_node, start_type, start_index = self.temp_connection_start
            start_pos = start_node.get_port_position(start_type, start_index)
            self.temp_connection_line.setLine(QLineF(start_pos, event.scenePos()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.temp_connection_start:
            super().mouseReleaseEvent(event)
            return

        if self.temp_connection_line:
            self.removeItem(self.temp_connection_line)
            self.temp_connection_line = None

        target = self.itemAt(event.scenePos(), QTransform())
        if isinstance(target, PortItem):
            start_node, start_type, start_idx = self.temp_connection_start
            end_node, end_type, end_idx = target.parentItem(), target.port_type, target.index
            if start_type == "output" and end_type == "input":
                self.add_connection(start_node.node_id, end_node.node_id, start_idx, end_idx)
            elif start_type == "input" and end_type == "output":
                self.add_connection(end_node.node_id, start_node.node_id, end_idx, start_idx)

        self.temp_connection_start = None
        event.accept()

    def save_to_json(self, file_path: str):
        data = {"nodes": [], "connections": []}
        for node_id, node in self.nodes.items():
            payload = {
                "id": node_id,
                "type": "file" if isinstance(node.widget, FileNode) else "archive",
                "pos_x": node.pos().x(),
                "pos_y": node.pos().y(),
            }
            if isinstance(node.widget, FileNode):
                payload["file_path"] = node.widget.file_path
            else:
                payload["archive_name"] = node.widget.archive_name_edit.text()
                payload["input_count"] = node.widget.input_count_spin.value()
                payload["save_path"] = node.widget.save_path
            data["nodes"].append(payload)

        for conn_id, conn in self.connections.items():
            data["connections"].append(
                {
                    "id": conn_id,
                    "start_node": conn.start_node.node_id,
                    "end_node": conn.end_node.node_id,
                    "start_port": conn.start_port,
                    "end_port": conn.end_port,
                }
            )

        Path(file_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_from_json(self, file_path: str):
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        for node_id in list(self.nodes.keys()):
            self.remove_node(node_id)

        node_map: Dict[str, str] = {}
        for node_data in data.get("nodes", []):
            pos = QPointF(node_data.get("pos_x", 0.0), node_data.get("pos_y", 0.0))
            if node_data.get("type") == "file":
                new_id = self.add_file_node(pos)
                self.nodes[new_id].widget.set_data(node_data.get("file_path", ""))
            else:
                new_id = self.add_archive_node(pos)
                self.nodes[new_id].widget.set_data(
                    node_data.get("archive_name", ""),
                    node_data.get("input_count", 1),
                    node_data.get("save_path", ""),
                )
            node_map[node_data.get("id", new_id)] = new_id

        for conn_data in data.get("connections", []):
            start = node_map.get(conn_data.get("start_node"))
            end = node_map.get(conn_data.get("end_node"))
            if start and end:
                self.add_connection(start, end, conn_data.get("start_port", 0), conn_data.get("end_port", 0))

    def execute_archive_node(self, node_id: str):
        success, message = self.execute_archive(node_id)
        self.execution_finished.emit(success, message)

    def execute_archive(self, target_node_id: Optional[str] = None) -> Tuple[bool, str]:
        archive_nodes = [n for n in self.nodes.values() if isinstance(n.widget, ArchiveNode)]
        if target_node_id is not None:
            archive_nodes = [n for n in archive_nodes if n.node_id == target_node_id]
        if not archive_nodes:
            return False, "Нет нод архива для выполнения"

        successes = 0
        errors: List[str] = []
        for archive_node in archive_nodes:
            files = []
            for start_id, _, _ in archive_node.input_connections.values():
                src = self.nodes.get(start_id)
                if src and isinstance(src.widget, FileNode) and src.widget.file_path:
                    files.append((src.node_id, src.widget.file_path))

            if not files:
                errors.append(f"{archive_node.node_id}: Нет входных файлов")
                continue

            archive_name = archive_node.widget.archive_name_edit.text().strip()
            save_path = archive_node.widget.save_path
            if not archive_name:
                errors.append(f"{archive_node.node_id}: Не задано имя архива")
                continue
            if not save_path or not os.path.isdir(save_path):
                errors.append(f"{archive_node.node_id}: Не задана директория сохранения")
                continue

            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    for source_node_id, source_path in files:
                        if not os.path.exists(source_path):
                            continue
                        base_name = os.path.basename(source_path)
                        unique_name = f"{source_node_id}_{base_name}"
                        shutil.copy2(source_path, os.path.join(tmp_dir, unique_name))

                    full_name = archive_name if archive_name.endswith(".tar.gz") else f"{archive_name}.tar.gz"
                    output = os.path.join(save_path, full_name)
                    subprocess.run([
                        "tar",
                        "-czf",
                        output,
                        "-C",
                        tmp_dir,
                        ".",
                    ], check=True)
                successes += 1
            except Exception as exc:
                errors.append(str(exc))

        if successes:
            return True, f"Успешно создано архивов: {successes}"
        return False, "; ".join(errors) if errors else "Не удалось выполнить архивацию"
