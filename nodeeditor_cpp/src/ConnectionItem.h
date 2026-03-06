#ifndef CONNECTIONITEM_H
#define CONNECTIONITEM_H

#include <QGraphicsLineItem>
#include <QString>

/*!\brief Линия связи между нодами.
 *
 * Класс хранит связи на уровне идентификаторов узлов и порта назначения.
 */
class ConnectionItem : public QGraphicsLineItem
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

private:
    QString m_id;
    QString m_fileNodeId;
    QString m_archiveNodeId;
    int m_archiveInputIndex;
};

#endif
