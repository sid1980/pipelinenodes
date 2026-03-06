#ifndef NODEITEM_H
#define NODEITEM_H

#include "ArchiveNodeWidget.h"
#include "FileNodeWidget.h"

#include <QGraphicsProxyWidget>
#include <QGraphicsRectItem>
#include <QPainter>
#include <QPointF>
#include <QString>

/*!\brief Тип ноды в графе редактора. */
enum class NodeType
{
    File = 0,
    Archive
};

/*!\brief Визуальный контейнер ноды.
 *
 * Класс хранит виджет ноды внутри QGraphicsProxyWidget и предоставляет
 * унифицированный доступ к типу, идентификатору и позициям портов.
 * Пример: NodeItem* item = new NodeItem("n1", NodeType::File);
 */
class NodeItem : public QGraphicsRectItem
{
public:
    NodeItem(const QString& id, NodeType type);
    ~NodeItem();

    QString id() const;
    NodeType nodeType() const;

    FileNodeWidget* fileWidget() const;
    ArchiveNodeWidget* archiveWidget() const;

    QPointF inputPortPosition(int index) const;
    QPointF outputPortPosition() const;
    int inputPortAt(const QPointF& scenePosition) const;
    bool isOutputPortAt(const QPointF& scenePosition) const;
    void refreshGeometry();

protected:
    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget);

private:
    QString m_id;
    NodeType m_nodeType;
    QGraphicsProxyWidget* m_proxy;
    FileNodeWidget* m_fileWidget;
    ArchiveNodeWidget* m_archiveWidget;
};

#endif
