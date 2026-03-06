#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "NodeEditorScene.h"

#include <QMainWindow>

class QAction;
class QGraphicsView;
class QLineEdit;
class QSpinBox;
class QStackedWidget;
class QWidget;

/*!\brief Главное окно приложения NodeEditor.
 *
 * Класс создает меню, тулбар и панель параметров для выбранной ноды.
 * Пример: MainWindow w; w.show();
 */
class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    MainWindow(QWidget* parent = 0);
    ~MainWindow();

public slots:
    void slot_addFileNode();
    void slot_addArchiveNode();
    void slot_connectSelectedNodes();
    void slot_saveGraph();
    void slot_loadGraph();
    void slot_execute();
    void slot_deleteSelected();
    void slot_selectionChanged();
    void slot_showExecutionResult(bool success, const QString& message);

private:
    void setupUi();
    NodeItem* firstSelectedNode() const;
    NodeItem* secondSelectedNode() const;

    NodeEditorScene* m_scene;
    QGraphicsView* m_view;

    QStackedWidget* m_settingsStack;
    QWidget* m_emptyWidget;
    QWidget* m_fileWidget;
    QWidget* m_archiveWidget;

    QLineEdit* m_filePathEdit;
    QLineEdit* m_archiveNameEdit;
    QSpinBox* m_archiveInputSpin;
    QLineEdit* m_archiveDirectoryEdit;
};

#endif
