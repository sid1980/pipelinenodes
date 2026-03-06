#ifndef CONNECTIONITEM_H
#define CONNECTIONITEM_H

#include <QGraphicsPathItem>
#include <QPainterPath>
#include <QString>

/*!\brief Линия связи между нодами.
 *
 * Класс хранит связи на уровне идентификаторов узлов и порта назначения.
 */
class ConnectionItem : public QGraphicsPathItem
{
public:
    ConnectionItem(const QString& id,
                   const QString& fileNodeId,
                   const QString& archiveNodeId,
                   int archiveInputIndex);
    ~ConnectionItem();

    QString id() const;
    QString fileNodeId() const;
    QString archiveNodeId() const;
    int archiveInputIndex() const;

    void setConnectionPath(const QPainterPath& path);

private:
    QString m_id;
    QString m_fileNodeId;
    QString m_archiveNodeId;
    int m_archiveInputIndex;
};

#endif
