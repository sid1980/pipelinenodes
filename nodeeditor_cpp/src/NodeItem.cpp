#include "NodeItem.h"

#include <QBrush>
#include <QPen>

namespace
{
static const qreal k_width = 330.0;
static const qreal k_headerHeight = 30.0;
static const qreal k_portRadius = 6.0;
static const qreal k_portMargin = 9.0;
static const qreal k_contentInset = 22.0;
static const qreal k_contentTopInset = 10.0;
static const qreal k_contentBottomInset = 10.0;
static const qreal k_archivePortStep = 24.0;
}

NodeItem::NodeItem(const QString& id, NodeType type)
    : m_id(id)
    , m_nodeType(type)
    , m_proxy(new QGraphicsProxyWidget(this))
    , m_fileWidget(NULL)
    , m_archiveWidget(NULL)
{
    setRect(0.0, 0.0, k_width, 140.0);
    setFlag(QGraphicsItem::ItemIsMovable, true);
    setFlag(QGraphicsItem::ItemIsSelectable, true);
    setFlag(QGraphicsItem::ItemSendsGeometryChanges, true);

    if (m_nodeType == NodeType::File) {
        m_fileWidget = new FileNodeWidget();
        m_proxy->setWidget(m_fileWidget);
    }
    else {
        m_archiveWidget = new ArchiveNodeWidget();
        m_proxy->setWidget(m_archiveWidget);
    }

    refreshGeometry();
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
    const qreal y = k_headerHeight + k_contentTopInset + 18.0 + static_cast<qreal>(index) * k_archivePortStep;
    return mapToScene(QPointF(k_portMargin, y));
}

QPointF NodeItem::outputPortPosition() const
{
    return mapToScene(QPointF(rect().width() - k_portMargin, rect().height() / 2.0));
}

int NodeItem::inputPortAt(const QPointF& scenePosition) const
{
    if (m_nodeType != NodeType::Archive || m_archiveWidget == NULL) {
        return -1;
    }

    const int inputCount = m_archiveWidget->inputCount();
    for (int i = 0; i < inputCount; ++i) {
        const QPointF portCenter = inputPortPosition(i);
        const qreal distanceX = scenePosition.x() - portCenter.x();
        const qreal distanceY = scenePosition.y() - portCenter.y();
        const qreal distanceSquared = distanceX * distanceX + distanceY * distanceY;
        if (distanceSquared <= (k_portRadius + 3.0) * (k_portRadius + 3.0)) {
            return i;
        }
    }
    return -1;
}

bool NodeItem::isOutputPortAt(const QPointF& scenePosition) const
{
    if (m_nodeType != NodeType::File) {
        return false;
    }

    const QPointF portCenter = outputPortPosition();
    const qreal distanceX = scenePosition.x() - portCenter.x();
    const qreal distanceY = scenePosition.y() - portCenter.y();
    const qreal distanceSquared = distanceX * distanceX + distanceY * distanceY;
    return distanceSquared <= (k_portRadius + 3.0) * (k_portRadius + 3.0);
}

void NodeItem::refreshGeometry()
{
    qreal widgetHeight = 90.0;
    if (m_proxy->widget() != NULL) {
        widgetHeight = static_cast<qreal>(m_proxy->widget()->sizeHint().height());
    }

    qreal height = k_headerHeight + k_contentTopInset + widgetHeight + k_contentBottomInset;
    if (m_nodeType == NodeType::Archive && m_archiveWidget != NULL) {
        const qreal portsHeight = k_headerHeight + k_contentTopInset + 18.0 +
                                  static_cast<qreal>(m_archiveWidget->inputCount() - 1) * k_archivePortStep + 18.0;
        if (height < portsHeight + k_contentBottomInset) {
            height = portsHeight + k_contentBottomInset;
        }
    }

    setRect(0.0, 0.0, k_width, height);
    m_proxy->setPos(k_contentInset, k_headerHeight + k_contentTopInset);
    if (m_proxy->widget() != NULL) {
        m_proxy->widget()->setMinimumWidth(static_cast<int>(rect().width() - 2.0 * k_contentInset));
        m_proxy->widget()->setMaximumWidth(static_cast<int>(rect().width() - 2.0 * k_contentInset));
    }
}

void NodeItem::paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget)
{
    Q_UNUSED(option);
    Q_UNUSED(widget);

    const QColor borderColor = isSelected() ? QColor(252, 181, 72) : QColor(35, 35, 35);
    painter->setPen(QPen(borderColor, 2.0));
    painter->setBrush(QBrush(QColor(75, 75, 75)));
    painter->drawRoundedRect(rect(), 8.0, 8.0);

    QRectF headerRect(1.0, 1.0, rect().width() - 2.0, k_headerHeight);
    painter->setPen(QPen(QColor(30, 30, 30), 1.0));
    painter->setBrush(QBrush(QColor(48, 48, 48)));
    painter->drawRoundedRect(headerRect, 6.0, 6.0);

    painter->setPen(QPen(QColor(220, 220, 220), 1.0));
    const QString title = m_nodeType == NodeType::File ? QString::fromUtf8("Файл") : QString::fromUtf8("Архив");
    painter->drawText(QRectF(10.0, 0.0, rect().width() - 20.0, k_headerHeight), Qt::AlignVCenter | Qt::AlignLeft, title);

    painter->setPen(QPen(QColor(20, 20, 20), 1.0));
    painter->setBrush(QBrush(QColor(205, 95, 75)));
    const QPointF outputCenter = mapFromScene(outputPortPosition());
    painter->drawEllipse(outputCenter, k_portRadius, k_portRadius);

    if (m_nodeType == NodeType::Archive && m_archiveWidget != NULL) {
        painter->setBrush(QBrush(QColor(88, 188, 92)));
        const int inputCount = m_archiveWidget->inputCount();
        for (int i = 0; i < inputCount; ++i) {
            const QPointF inputCenter = mapFromScene(inputPortPosition(i));
            painter->drawEllipse(inputCenter, k_portRadius, k_portRadius);
        }
    }
}
