#include <QColor>
#include <QPen>
#include "ConnectionItem.h"

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
    setZValue(-1.0);
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
