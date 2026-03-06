#include "NodeItem.h"

#include <QBrush>
#include <QPen>

namespace
{
static const qreal k_width = 280.0;
static const qreal k_height = 140.0;
}

NodeItem::NodeItem(const QString& id, NodeType type)
    : m_id(id)
    , m_nodeType(type)
    , m_proxy(new QGraphicsProxyWidget(this))
    , m_fileWidget(NULL)
    , m_archiveWidget(NULL)
{
    setRect(0.0, 0.0, k_width, k_height);
    setPen(QPen(QColor(40, 40, 40), 2.0));
    setBrush(QBrush(QColor(70, 70, 70)));
    setFlag(QGraphicsItem::ItemIsMovable, true);
    setFlag(QGraphicsItem::ItemIsSelectable, true);

    if (m_nodeType == NodeType::File) {
        m_fileWidget = new FileNodeWidget();
        m_proxy->setWidget(m_fileWidget);
    }
    else {
        m_archiveWidget = new ArchiveNodeWidget();
        m_proxy->setWidget(m_archiveWidget);
    }
    m_proxy->setPos(10.0, 10.0);
}

NodeItem::~NodeItem()
{
}

QString NodeItem::id() const
{
    return m_id;
}

NodeType NodeItem::nodeType() const
{
    return m_nodeType;
}

FileNodeWidget* NodeItem::fileWidget() const
{
    return m_fileWidget;
}

ArchiveNodeWidget* NodeItem::archiveWidget() const
{
    return m_archiveWidget;
}

QPointF NodeItem::inputPortPosition(int index) const
{
    if (index < 0) {
        return scenePos();
    }
    const qreal y = 50.0 + static_cast<qreal>(index) * 24.0;
    return mapToScene(QPointF(0.0, y));
}

QPointF NodeItem::outputPortPosition() const
{
    return mapToScene(QPointF(rect().width(), rect().height() / 2.0));
}
