#ifndef FILENODEWIDGET_H
#define FILENODEWIDGET_H

#include <QWidget>

class QLabel;

/*!\brief Виджет файловой ноды.
 *
 * Класс отображает путь к входному файлу.
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

private:
    QString m_filePath;
    QLabel* m_label;
};

#endif
