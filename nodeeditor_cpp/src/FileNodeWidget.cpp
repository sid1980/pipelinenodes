#include "FileNodeWidget.h"

#include <QFileDialog>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>

FileNodeWidget::FileNodeWidget(QWidget* parent)
    : QWidget(parent)
    , m_filePath()
    , m_label(new QLabel(QString::fromUtf8("Файл не выбран"), this))
    , m_selectButton(new QPushButton(QString::fromUtf8("Выбрать файл..."), this))
{
    m_label->setWordWrap(true);
    QVBoxLayout* layout = new QVBoxLayout(this);
    layout->addWidget(m_label);
    layout->addWidget(m_selectButton);
    setLayout(layout);

    connect(m_selectButton, SIGNAL(clicked()), this, SLOT(slot_selectFile()));
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

void FileNodeWidget::slot_selectFile()
{
    const QString path = QFileDialog::getOpenFileName(this,
                                                      QString::fromUtf8("Выбор файла"),
                                                      QString(),
                                                      QString::fromUtf8("Все файлы (*.*)"));
    if (path.isEmpty()) {
        return;
    }
    setFilePath(path);
}
