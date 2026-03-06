#include "NodeEditorScene.h"

#include <QFile>
#include <QGraphicsSceneMouseEvent>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPainter>
#include <QPainterPath>
#include <QPen>
#include <QProcess>

namespace
{
static const int k_fineGrid = 20;
static const int k_coarseGrid = 100;
}

NodeEditorScene::NodeEditorScene(QObject* parent)
    : QGraphicsScene(parent)
    , m_nodes()
    , m_connections()
    , m_nodeCounter(1)
    , m_connectionCounter(1)
    , m_dragFileNodeId()
    , m_tempConnection(NULL)
{
    setSceneRect(-2000.0, -2000.0, 4000.0, 4000.0);
    setBackgroundBrush(QBrush(QColor(53, 53, 53)));
}

NodeEditorScene::~NodeEditorScene()
{
}

QString NodeEditorScene::addFileNode(const QPointF& position)
{
    const QString id = createNodeId();
    NodeItem* item = new NodeItem(id, NodeType::File);
    addItem(item);
    item->setPos(position);
    m_nodes[id] = item;
    connect(item->fileWidget(), SIGNAL(signal_filePathChanged()), this, SLOT(slot_updateConnections()));
    return id;
}

QString NodeEditorScene::addArchiveNode(const QPointF& position)
{
    const QString id = createNodeId();
    NodeItem* item = new NodeItem(id, NodeType::Archive);
    addItem(item);
    item->setPos(position);
    m_nodes[id] = item;
    connect(item->archiveWidget(), SIGNAL(signal_archiveChanged()), this, SLOT(slot_updateConnections()));
    return id;
}

bool NodeEditorScene::connectFileToArchive(const QString& fileNodeId, const QString& archiveNodeId, int inputIndex)
{
    if (inputIndex < 0) {
        return false;
    }

    std::map<QString, NodeItem*>::const_iterator fileIt = m_nodes.find(fileNodeId);
    std::map<QString, NodeItem*>::const_iterator archiveIt = m_nodes.find(archiveNodeId);
    if (fileIt == m_nodes.end() || archiveIt == m_nodes.end()) {
        return false;
    }
    if (fileIt->second->nodeType() != NodeType::File || archiveIt->second->nodeType() != NodeType::Archive) {
        return false;
    }

    archiveIt->second->refreshGeometry();
    if (inputIndex >= archiveIt->second->archiveWidget()->inputCount()) {
        return false;
    }

    for (std::map<QString, ConnectionItem*>::const_iterator it = m_connections.begin(); it != m_connections.end(); ++it) {
        const ConnectionItem* existing = it->second;
        if (existing->archiveNodeId() == archiveNodeId && existing->archiveInputIndex() == inputIndex) {
            return false;
        }
    }

    const QString id = createConnectionId();
    ConnectionItem* line = new ConnectionItem(id, fileNodeId, archiveNodeId, inputIndex);
    addItem(line);
    m_connections[id] = line;
    slot_updateConnections();
    return true;
}

bool NodeEditorScene::removeNode(const QString& nodeId)
{
    std::map<QString, NodeItem*>::iterator nodeIt = m_nodes.find(nodeId);
    if (nodeIt == m_nodes.end()) {
        return false;
    }

    std::map<QString, ConnectionItem*>::iterator connIt = m_connections.begin();
    while (connIt != m_connections.end()) {
        ConnectionItem* connection = connIt->second;
        if (connection->fileNodeId() == nodeId || connection->archiveNodeId() == nodeId) {
            removeItem(connection);
            delete connection;
            std::map<QString, ConnectionItem*>::iterator eraseIt = connIt;
            ++connIt;
            m_connections.erase(eraseIt);
            continue;
        }
        ++connIt;
    }

    removeItem(nodeIt->second);
    delete nodeIt->second;
    m_nodes.erase(nodeIt);
    return true;
}

bool NodeEditorScene::saveToJson(const QString& path, QString* errorMessage)
{
    QJsonObject root;
    QJsonArray nodesArray;
    for (std::map<QString, NodeItem*>::const_iterator it = m_nodes.begin(); it != m_nodes.end(); ++it) {
        const NodeItem* node = it->second;
        QJsonObject object;
        object["id"] = node->id();
        object["x"] = node->pos().x();
        object["y"] = node->pos().y();
        object["type"] = node->nodeType() == NodeType::File ? "file" : "archive";
        if (node->nodeType() == NodeType::File) {
            object["file_path"] = node->fileWidget()->filePath();
        }
        else {
            object["archive_name"] = node->archiveWidget()->archiveName();
            object["input_count"] = node->archiveWidget()->inputCount();
            object["save_directory"] = node->archiveWidget()->saveDirectory();
        }
        nodesArray.append(object);
    }
    root["nodes"] = nodesArray;

    QJsonArray connectionsArray;
    for (std::map<QString, ConnectionItem*>::const_iterator it = m_connections.begin(); it != m_connections.end(); ++it) {
        const ConnectionItem* connection = it->second;
        QJsonObject object;
        object["id"] = connection->id();
        object["file_node"] = connection->fileNodeId();
        object["archive_node"] = connection->archiveNodeId();
        object["input_index"] = connection->archiveInputIndex();
        connectionsArray.append(object);
    }
    root["connections"] = connectionsArray;

    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        if (errorMessage != 0) {
            *errorMessage = QString::fromUtf8("Не удалось открыть файл для записи");
        }
        return false;
    }
    file.write(QJsonDocument(root).toJson());
    file.close();
    return true;
}

bool NodeEditorScene::loadFromJson(const QString& path, QString* errorMessage)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        if (errorMessage != 0) {
            *errorMessage = QString::fromUtf8("Не удалось открыть файл");
        }
        return false;
    }
    const QByteArray raw = file.readAll();
    file.close();

    const QJsonDocument document = QJsonDocument::fromJson(raw);
    if (!document.isObject()) {
        if (errorMessage != 0) {
            *errorMessage = QString::fromUtf8("Неверный формат JSON");
        }
        return false;
    }

    while (!m_nodes.empty()) {
        removeNode(m_nodes.begin()->first);
    }

    QJsonObject root = document.object();
    QJsonArray nodesArray = root["nodes"].toArray();
    std::map<QString, QString> idMap;
    for (int i = 0; i < nodesArray.size(); ++i) {
        QJsonObject object = nodesArray[i].toObject();
        QPointF position(object["x"].toDouble(), object["y"].toDouble());
        QString newId;
        if (object["type"].toString() == "file") {
            newId = addFileNode(position);
            m_nodes[newId]->fileWidget()->setFilePath(object["file_path"].toString());
        }
        else {
            newId = addArchiveNode(position);
            m_nodes[newId]->archiveWidget()->setArchiveName(object["archive_name"].toString());
            m_nodes[newId]->archiveWidget()->setInputCount(object["input_count"].toInt(1));
            m_nodes[newId]->archiveWidget()->setSaveDirectory(object["save_directory"].toString());
            m_nodes[newId]->refreshGeometry();
        }
        idMap[object["id"].toString()] = newId;
    }

    QJsonArray connectionsArray = root["connections"].toArray();
    for (int i = 0; i < connectionsArray.size(); ++i) {
        QJsonObject object = connectionsArray[i].toObject();
        const QString oldFile = object["file_node"].toString();
        const QString oldArchive = object["archive_node"].toString();
        if (idMap.find(oldFile) == idMap.end() || idMap.find(oldArchive) == idMap.end()) {
            continue;
        }
        connectFileToArchive(idMap[oldFile], idMap[oldArchive], object["input_index"].toInt());
    }

    return true;
}

bool NodeEditorScene::executeArchive(const QString& targetNodeId, QString* message)
{
    if (targetNodeId.isEmpty()) {
        for (std::map<QString, NodeItem*>::iterator it = m_nodes.begin(); it != m_nodes.end(); ++it) {
            if (it->second->nodeType() == NodeType::Archive) {
                return executeArchiveNode(it->second, message);
            }
        }
        if (message != 0) {
            *message = QString::fromUtf8("Архивная нода не найдена");
        }
        return false;
    }

    std::map<QString, NodeItem*>::iterator it = m_nodes.find(targetNodeId);
    if (it == m_nodes.end() || it->second->nodeType() != NodeType::Archive) {
        if (message != 0) {
            *message = QString::fromUtf8("Невалидная нода архива");
        }
        return false;
    }
    return executeArchiveNode(it->second, message);
}

const std::map<QString, NodeItem*>& NodeEditorScene::nodes() const
{
    return m_nodes;
}

const std::map<QString, ConnectionItem*>& NodeEditorScene::connections() const
{
    return m_connections;
}

void NodeEditorScene::slot_executeCurrent()
{
    QString message;
    const bool success = executeArchive(QString(), &message);
    emit signal_executionFinished(success, message);
}

void NodeEditorScene::slot_updateConnections()
{
    for (std::map<QString, NodeItem*>::iterator it = m_nodes.begin(); it != m_nodes.end(); ++it) {
        NodeItem* node = it->second;
        if (node->nodeType() == NodeType::Archive) {
            node->refreshGeometry();
            node->update();
        }
    }

    std::map<QString, ConnectionItem*>::iterator connIt = m_connections.begin();
    while (connIt != m_connections.end()) {
        ConnectionItem* connection = connIt->second;
        std::map<QString, NodeItem*>::iterator fileIt = m_nodes.find(connection->fileNodeId());
        std::map<QString, NodeItem*>::iterator archiveIt = m_nodes.find(connection->archiveNodeId());
        if (fileIt == m_nodes.end() || archiveIt == m_nodes.end()) {
            removeItem(connection);
            delete connection;
            std::map<QString, ConnectionItem*>::iterator eraseIt = connIt;
            ++connIt;
            m_connections.erase(eraseIt);
            continue;
        }

        NodeItem* fileNode = fileIt->second;
        NodeItem* archiveNode = archiveIt->second;
        if (archiveNode->archiveWidget() == NULL || connection->archiveInputIndex() >= archiveNode->archiveWidget()->inputCount()) {
            removeItem(connection);
            delete connection;
            std::map<QString, ConnectionItem*>::iterator eraseIt = connIt;
            ++connIt;
            m_connections.erase(eraseIt);
            continue;
        }

        const QPointF from = fileNode->outputPortPosition();
        const QPointF to = archiveNode->inputPortPosition(connection->archiveInputIndex());
        connection->setConnectionPath(buildConnectionPath(from, to));
        ++connIt;
    }

    update();
}

void NodeEditorScene::drawBackground(QPainter* painter, const QRectF& rect)
{
    painter->fillRect(rect, QColor(53, 53, 53));

    painter->setPen(QPen(QColor(63, 63, 63), 1.0));
    const int leftFine = static_cast<int>(rect.left()) - (static_cast<int>(rect.left()) % k_fineGrid);
    const int topFine = static_cast<int>(rect.top()) - (static_cast<int>(rect.top()) % k_fineGrid);
    for (int x = leftFine; x < static_cast<int>(rect.right()); x += k_fineGrid) {
        painter->drawLine(x, static_cast<int>(rect.top()), x, static_cast<int>(rect.bottom()));
    }
    for (int y = topFine; y < static_cast<int>(rect.bottom()); y += k_fineGrid) {
        painter->drawLine(static_cast<int>(rect.left()), y, static_cast<int>(rect.right()), y);
    }

    painter->setPen(QPen(QColor(78, 78, 78), 1.0));
    const int leftCoarse = static_cast<int>(rect.left()) - (static_cast<int>(rect.left()) % k_coarseGrid);
    const int topCoarse = static_cast<int>(rect.top()) - (static_cast<int>(rect.top()) % k_coarseGrid);
    for (int x = leftCoarse; x < static_cast<int>(rect.right()); x += k_coarseGrid) {
        painter->drawLine(x, static_cast<int>(rect.top()), x, static_cast<int>(rect.bottom()));
    }
    for (int y = topCoarse; y < static_cast<int>(rect.bottom()); y += k_coarseGrid) {
        painter->drawLine(static_cast<int>(rect.left()), y, static_cast<int>(rect.right()), y);
    }
}

void NodeEditorScene::mousePressEvent(QGraphicsSceneMouseEvent* event)
{
    if (event == NULL) {
        QGraphicsScene::mousePressEvent(event);
        return;
    }

    if (event->button() == Qt::LeftButton) {
        QGraphicsItem* item = itemAt(event->scenePos(), QTransform());
        NodeItem* node = findNodeItem(item);

        if (node != NULL && node->nodeType() == NodeType::File && node->isOutputPortAt(event->scenePos())) {
            m_dragFileNodeId = node->id();
            if (m_tempConnection != NULL) {
                removeItem(m_tempConnection);
                delete m_tempConnection;
            }
            m_tempConnection = new QGraphicsPathItem();
            m_tempConnection->setPen(QPen(QColor(130, 150, 250), 2.0));
            m_tempConnection->setBrush(Qt::NoBrush);
            m_tempConnection->setPath(buildConnectionPath(node->outputPortPosition(), event->scenePos()));
            m_tempConnection->setZValue(4.0);
            addItem(m_tempConnection);
            event->accept();
            return;
        }
    }

    QGraphicsScene::mousePressEvent(event);
}

void NodeEditorScene::mouseMoveEvent(QGraphicsSceneMouseEvent* event)
{
    if (event != NULL && m_tempConnection != NULL) {
        QPainterPath path = buildConnectionPath(m_tempConnection->path().pointAtPercent(0.0), event->scenePos());
        m_tempConnection->setPath(path);
        event->accept();
        return;
    }

    QGraphicsScene::mouseMoveEvent(event);
}

void NodeEditorScene::mouseReleaseEvent(QGraphicsSceneMouseEvent* event)
{
    if (event != NULL && event->button() == Qt::LeftButton && m_tempConnection != NULL) {
        NodeItem* archiveNode = NULL;
        int inputIndex = -1;

        for (std::map<QString, NodeItem*>::iterator it = m_nodes.begin(); it != m_nodes.end(); ++it) {
            NodeItem* node = it->second;
            if (node == NULL || node->nodeType() != NodeType::Archive) {
                continue;
            }
            const int index = node->inputPortAt(event->scenePos());
            if (index >= 0) {
                archiveNode = node;
                inputIndex = index;
                break;
            }
        }

        removeItem(m_tempConnection);
        delete m_tempConnection;
        m_tempConnection = NULL;

        if (archiveNode != NULL && inputIndex >= 0) {
            connectFileToArchive(m_dragFileNodeId, archiveNode->id(), inputIndex);
        }
        m_dragFileNodeId.clear();

        event->accept();
        return;
    }

    QGraphicsScene::mouseReleaseEvent(event);
}

NodeItem* NodeEditorScene::findNodeItem(QGraphicsItem* item) const
{
    QGraphicsItem* current = item;
    while (current != NULL) {
        NodeItem* node = dynamic_cast<NodeItem*>(current);
        if (node != NULL) {
            return node;
        }
        current = current->parentItem();
    }
    return NULL;
}


void NodeEditorScene::mouseDoubleClickEvent(QGraphicsSceneMouseEvent* event)
{
    if (event == NULL) {
        QGraphicsScene::mouseDoubleClickEvent(event);
        return;
    }

    QGraphicsItem* item = itemAt(event->scenePos(), QTransform());
    ConnectionItem* connection = dynamic_cast<ConnectionItem*>(item);
    if (connection == NULL && item != NULL && item->parentItem() != NULL) {
        connection = dynamic_cast<ConnectionItem*>(item->parentItem());
    }

    if (connection != NULL) {
        std::map<QString, ConnectionItem*>::iterator it = m_connections.find(connection->id());
        if (it != m_connections.end()) {
            removeItem(it->second);
            delete it->second;
            m_connections.erase(it);
            update();
            event->accept();
            return;
        }
    }

    QGraphicsScene::mouseDoubleClickEvent(event);
}

QPainterPath NodeEditorScene::buildConnectionPath(const QPointF& from, const QPointF& to) const
{
    QPainterPath path(from);
    const qreal dx = to.x() - from.x();
    qreal control = dx * 0.5;
    if (control < 60.0) {
        control = 60.0;
    }
    QPointF c1(from.x() + control, from.y());
    QPointF c2(to.x() - control, to.y());
    path.cubicTo(c1, c2, to);
    return path;
}

QString NodeEditorScene::createNodeId()
{
    const QString id = QString("n_%1").arg(m_nodeCounter);
    ++m_nodeCounter;
    return id;
}

QString NodeEditorScene::createConnectionId()
{
    const QString id = QString("c_%1").arg(m_connectionCounter);
    ++m_connectionCounter;
    return id;
}

bool NodeEditorScene::executeArchiveNode(NodeItem* archiveNode, QString* message)
{
    if (archiveNode == 0 || archiveNode->archiveWidget() == 0) {
        if (message != 0) {
            *message = QString::fromUtf8("Невалидная архивная нода");
        }
        return false;
    }

    QString archiveName = archiveNode->archiveWidget()->archiveName().trimmed();
    QString saveDir = archiveNode->archiveWidget()->saveDirectory().trimmed();
    if (archiveName.isEmpty() || saveDir.isEmpty()) {
        if (message != 0) {
            *message = QString::fromUtf8("Заполните имя и каталог архива");
        }
        return false;
    }

    QStringList files;
    for (std::map<QString, ConnectionItem*>::iterator it = m_connections.begin(); it != m_connections.end(); ++it) {
        ConnectionItem* connection = it->second;
        if (connection->archiveNodeId() != archiveNode->id()) {
            continue;
        }
        NodeItem* fileNode = m_nodes[connection->fileNodeId()];
        if (fileNode == 0 || fileNode->fileWidget() == 0) {
            continue;
        }
        const QString filePath = fileNode->fileWidget()->filePath();
        if (!filePath.isEmpty()) {
            files << filePath;
        }
    }

    if (files.isEmpty()) {
        if (message != 0) {
            *message = QString::fromUtf8("Нет входных файлов");
        }
        return false;
    }

    QString output = saveDir + "/" + archiveName;
    if (!output.endsWith(".tar.gz")) {
        output += ".tar.gz";
    }

    QStringList arguments;
    arguments << "-czf" << output;
    for (int i = 0; i < files.size(); ++i) {
        arguments << files[i];
    }

    int code = QProcess::execute("tar", arguments);
    if (code != 0) {
        if (message != 0) {
            *message = QString::fromUtf8("Команда tar завершилась с ошибкой");
        }
        return false;
    }

    if (message != 0) {
        *message = QString::fromUtf8("Архив успешно создан: ") + output;
    }
    return true;
}
