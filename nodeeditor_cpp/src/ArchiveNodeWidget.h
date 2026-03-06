#ifndef ARCHIVENODEWIDGET_H
#define ARCHIVENODEWIDGET_H

#include <QWidget>

class QLineEdit;
class QSpinBox;

/*!\brief Виджет архивной ноды.
 *
 * Хранит параметры архивации.
 * Пример: archiveNode->setArchiveName("result");
 */
class ArchiveNodeWidget : public QWidget
{
    Q_OBJECT
public:
    ArchiveNodeWidget(QWidget* parent = 0);
    ~ArchiveNodeWidget();

    QString archiveName() const;
    int inputCount() const;
    QString saveDirectory() const;

    void setArchiveName(const QString& value);
    void setInputCount(int value);
    void setSaveDirectory(const QString& value);

signals:
    void signal_archiveChanged();

private:
    QLineEdit* m_archiveName;
    QSpinBox* m_inputCount;
    QLineEdit* m_saveDirectory;
};

#endif
