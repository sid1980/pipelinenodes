#ifndef NODEEDITORSCENE_H
#define NODEEDITORSCENE_H

#include "ConnectionItem.h"
#include "NodeItem.h"

#include <QGraphicsPathItem>
#include <QPainterPath>
#include <QGraphicsScene>
#include <QObject>
#include <QPointF>
#include <QString>

#include <map>

/*!\brief Сцена редактора графа файлов и архивов.
 *
 * Сцена управляет нодами, связями, сериализацией JSON и запуском tar.
 * Пример: scene->addFileNode(QPointF(100.0, 100.0));
 */
class NodeEditorScene : public QGraphicsScene
{
    Q_OBJECT
public:
    NodeEditorScene(QObject* parent = 0);
    ~NodeEditorScene();

    QString addFileNode(const QPointF& position);
    QString addArchiveNode(const QPointF& position);
    bool connectFileToArchive(const QString& fileNodeId, const QString& archiveNodeId, int inputIndex);
    bool removeNode(const QString& nodeId);

    bool saveToJson(const QString& path, QString* errorMessage);
    bool loadFromJson(const QString& path, QString* errorMessage);
    bool executeArchive(const QString& targetNodeId, QString* message);

    const std::map<QString, NodeItem*>& nodes() const;
    const std::map<QString, ConnectionItem*>& connections() const;

signals:
    void signal_executionFinished(bool success, const QString& message);

public slots:
    void slot_executeCurrent();

private slots:
    void slot_updateConnections();

protected:
    void drawBackground(QPainter* painter, const QRectF& rect);
    void mousePressEvent(QGraphicsSceneMouseEvent* event);
    void mouseMoveEvent(QGraphicsSceneMouseEvent* event);
    void mouseReleaseEvent(QGraphicsSceneMouseEvent* event);
    void mouseDoubleClickEvent(QGraphicsSceneMouseEvent* event);

private:
    QString createNodeId();
    QString createConnectionId();
    bool executeArchiveNode(NodeItem* archiveNode, QString* message);
    QPainterPath buildConnectionPath(const QPointF& from, const QPointF& to) const;

    std::map<QString, NodeItem*> m_nodes;
    std::map<QString, ConnectionItem*> m_connections;
    int m_nodeCounter;
    int m_connectionCounter;

    QString m_dragFileNodeId;
    QGraphicsPathItem* m_tempConnection;

    NodeItem* findNodeItem(QGraphicsItem* item) const;
};

#endif
