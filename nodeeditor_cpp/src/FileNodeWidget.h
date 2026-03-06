#ifndef FILENODEWIDGET_H
#define FILENODEWIDGET_H

#include <QWidget>

class QLabel;
class QPushButton;

/*!\brief Виджет файловой ноды.
 *
 * Класс отображает путь к входному файлу и позволяет выбрать файл кнопкой.
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
    void slot_selectFile();

private:
    QString m_filePath;
    QLabel* m_label;
    QPushButton* m_selectButton;
};

#endif
