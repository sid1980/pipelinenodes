#include "ConnectionItem.h"

#include <QBrush>
#include <QColor>
#include <QPen>

ConnectionItem::ConnectionItem(const QString& id,
                               const QString& fileNodeId,
                               const QString& archiveNodeId,
                               int archiveInputIndex)
    : m_id(id)
    , m_fileNodeId(fileNodeId)
    , m_archiveNodeId(archiveNodeId)
    , m_archiveInputIndex(archiveInputIndex)
{
    setPen(QPen(QColor(120, 140, 240), 2.0));
    setBrush(Qt::NoBrush);
    setZValue(2.0);
}

ConnectionItem::~ConnectionItem()
{
}

QString ConnectionItem::id() const
{
    return m_id;
}

QString ConnectionItem::fileNodeId() const
{
    return m_fileNodeId;
}

QString ConnectionItem::archiveNodeId() const
{
    return m_archiveNodeId;
}

int ConnectionItem::archiveInputIndex() const
{
    return m_archiveInputIndex;
}

void ConnectionItem::setConnectionPath(const QPainterPath& path)
{
    setPath(path);
}
