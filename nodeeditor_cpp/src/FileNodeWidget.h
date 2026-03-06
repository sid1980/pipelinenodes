#ifndef FILENODEWIDGET_H
#define FILENODEWIDGET_H

#include <QWidget>

class QLabel;

/*!\brief Виджет файловой ноды.
 *
 * Класс отображает путь к входному файлу и хранит его.
 * Пример: fileNode->setFilePath("/tmp/a.txt");
 */
class FileNodeWidget : public QWidget
{
    Q_OBJECT
public:
    FileNodeWidget(QWidget* parent = 0);
    ~FileNodeWidget();

    QString filePath() const;
    void setFilePath(const QString& value);

signals:
    void signal_filePathChanged();

public slots:
    void slot_noop();

private:
    QString m_filePath;
    QLabel* m_label;
};

#endif
