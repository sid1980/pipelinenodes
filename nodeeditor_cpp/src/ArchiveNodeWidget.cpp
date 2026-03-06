#include "ArchiveNodeWidget.h"

#include <QFormLayout>
#include <QLineEdit>
#include <QSpinBox>

ArchiveNodeWidget::ArchiveNodeWidget(QWidget* parent)
    : QWidget(parent)
    , m_archiveName(new QLineEdit(this))
    , m_inputCount(new QSpinBox(this))
    , m_saveDirectory(new QLineEdit(this))
{
    m_inputCount->setMinimum(1);
    m_inputCount->setMaximum(10);

    QFormLayout* layout = new QFormLayout(this);
    layout->addRow(QString::fromUtf8("Имя архива"), m_archiveName);
    layout->addRow(QString::fromUtf8("Входы"), m_inputCount);
    layout->addRow(QString::fromUtf8("Каталог"), m_saveDirectory);
    setLayout(layout);

    connect(m_archiveName, SIGNAL(textChanged(QString)), this, SIGNAL(signal_archiveChanged()));
    connect(m_inputCount, SIGNAL(valueChanged(int)), this, SIGNAL(signal_archiveChanged()));
    connect(m_saveDirectory, SIGNAL(textChanged(QString)), this, SIGNAL(signal_archiveChanged()));
}

ArchiveNodeWidget::~ArchiveNodeWidget()
{
}

QString ArchiveNodeWidget::archiveName() const
{
    return m_archiveName->text();
}

int ArchiveNodeWidget::inputCount() const
{
    return m_inputCount->value();
}

QString ArchiveNodeWidget::saveDirectory() const
{
    return m_saveDirectory->text();
}

void ArchiveNodeWidget::setArchiveName(const QString& value)
{
    m_archiveName->setText(value);
}

void ArchiveNodeWidget::setInputCount(int value)
{
    if (value < 1) {
        return;
    }
    m_inputCount->setValue(value);
}

void ArchiveNodeWidget::setSaveDirectory(const QString& value)
{
    m_saveDirectory->setText(value);
}
