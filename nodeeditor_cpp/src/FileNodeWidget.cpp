#include "FileNodeWidget.h"

#include <QLabel>
#include <QVBoxLayout>

FileNodeWidget::FileNodeWidget(QWidget* parent)
    : QWidget(parent)
    , m_filePath()
    , m_label(new QLabel(QString::fromUtf8("Файл не выбран"), this))
{
    QVBoxLayout* layout = new QVBoxLayout(this);
    layout->addWidget(m_label);
    setLayout(layout);
}

FileNodeWidget::~FileNodeWidget()
{
}

QString FileNodeWidget::filePath() const
{
    return m_filePath;
}

void FileNodeWidget::setFilePath(const QString& value)
{
    m_filePath = value;
    if (m_filePath.isEmpty()) {
        m_label->setText(QString::fromUtf8("Файл не выбран"));
    }
    else {
        m_label->setText(m_filePath);
    }
    emit signal_filePathChanged();
}

void FileNodeWidget::slot_noop()
{
}
