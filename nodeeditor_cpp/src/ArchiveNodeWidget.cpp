#include "ArchiveNodeWidget.h"

#include <QFileDialog>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QSpinBox>
#include <QVBoxLayout>

ArchiveNodeWidget::ArchiveNodeWidget(QWidget* parent)
    : QWidget(parent)
    , m_archiveName(new QLineEdit(this))
    , m_inputCount(new QSpinBox(this))
    , m_saveDirectory(new QLineEdit(this))
    , m_selectDirectoryButton(new QPushButton(QString::fromUtf8("Выбрать папку..."), this))
    , m_archiveButton(new QPushButton(QString::fromUtf8("Архивировать"), this))
{
    m_inputCount->setMinimum(1);
    m_inputCount->setMaximum(10);

    QFormLayout* layout = new QFormLayout();
    layout->addRow(QString::fromUtf8("Имя архива"), m_archiveName);
    layout->addRow(QString::fromUtf8("Входы"), m_inputCount);
    layout->addRow(QString::fromUtf8("Каталог"), m_saveDirectory);

    QHBoxLayout* buttonLayout = new QHBoxLayout();
    buttonLayout->addWidget(m_selectDirectoryButton);
    buttonLayout->addWidget(m_archiveButton);

    QVBoxLayout* rootLayout = new QVBoxLayout(this);
    rootLayout->addLayout(layout);
    rootLayout->addLayout(buttonLayout);
    setLayout(rootLayout);

    connect(m_archiveName, SIGNAL(textChanged(QString)), this, SIGNAL(signal_archiveChanged()));
    connect(m_inputCount, SIGNAL(valueChanged(int)), this, SIGNAL(signal_archiveChanged()));
    connect(m_saveDirectory, SIGNAL(textChanged(QString)), this, SIGNAL(signal_archiveChanged()));
    connect(m_selectDirectoryButton, SIGNAL(clicked()), this, SLOT(slot_selectDirectory()));
    connect(m_archiveButton, SIGNAL(clicked()), this, SLOT(slot_requestArchive()));
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

void ArchiveNodeWidget::slot_selectDirectory()
{
    const QString path = QFileDialog::getExistingDirectory(this,
                                                            QString::fromUtf8("Каталог архивации"),
                                                            QString(),
                                                            QFileDialog::ShowDirsOnly);
    if (path.isEmpty()) {
        return;
    }
    m_saveDirectory->setText(path);
    emit signal_archiveChanged();
}

void ArchiveNodeWidget::slot_requestArchive()
{
    emit signal_archiveRequested();
}
