#include "MainWindow.h"

#include <QAction>
#include <QDockWidget>
#include <QFileDialog>
#include <QFormLayout>
#include <QGraphicsView>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QMetaObject>
#include <QPushButton>
#include <QSpinBox>
#include <QStackedWidget>
#include <QToolBar>
#include <QVBoxLayout>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , m_scene(new NodeEditorScene(this))
    , m_view(new QGraphicsView(m_scene, this))
    , m_settingsStack(0)
    , m_emptyWidget(0)
    , m_fileWidget(0)
    , m_archiveWidget(0)
    , m_filePathEdit(0)
    , m_archiveNameEdit(0)
    , m_archiveInputSpin(0)
    , m_archiveDirectoryEdit(0)
{
    setupUi();
}

MainWindow::~MainWindow()
{
}

void MainWindow::slot_addFileNode()
{
    const QPointF center = m_view->mapToScene(m_view->viewport()->rect().center());
    m_scene->addFileNode(center);
}

void MainWindow::slot_addArchiveNode()
{
    const QPointF center = m_view->mapToScene(m_view->viewport()->rect().center());
    m_scene->addArchiveNode(center);
}

void MainWindow::slot_connectSelectedNodes()
{
    NodeItem* first = firstSelectedNode();
    NodeItem* second = secondSelectedNode();
    if (first == 0 || second == 0) {
        QMessageBox::warning(this, QString::fromUtf8("Связь"), QString::fromUtf8("Выберите две ноды"));
        return;
    }

    NodeItem* fileNode = 0;
    NodeItem* archiveNode = 0;
    if (first->nodeType() == NodeType::File && second->nodeType() == NodeType::Archive) {
        fileNode = first;
        archiveNode = second;
    }
    else if (second->nodeType() == NodeType::File && first->nodeType() == NodeType::Archive) {
        fileNode = second;
        archiveNode = first;
    }
    else {
        QMessageBox::warning(this, QString::fromUtf8("Связь"), QString::fromUtf8("Нужны File + Archive"));
        return;
    }

    if (!m_scene->connectFileToArchive(fileNode->id(), archiveNode->id(), 0)) {
        QMessageBox::warning(this, QString::fromUtf8("Связь"), QString::fromUtf8("Не удалось создать связь"));
    }
}

void MainWindow::slot_saveGraph()
{
    const QString path = QFileDialog::getSaveFileName(this, QString::fromUtf8("Сохранить граф"), QString(), "JSON (*.json)");
    if (path.isEmpty()) {
        return;
    }

    QString error;
    if (!m_scene->saveToJson(path, &error)) {
        QMessageBox::critical(this, QString::fromUtf8("Ошибка"), error);
    }
}

void MainWindow::slot_loadGraph()
{
    const QString path = QFileDialog::getOpenFileName(this, QString::fromUtf8("Загрузить граф"), QString(), "JSON (*.json)");
    if (path.isEmpty()) {
        return;
    }

    QString error;
    if (!m_scene->loadFromJson(path, &error)) {
        QMessageBox::critical(this, QString::fromUtf8("Ошибка"), error);
    }
}

void MainWindow::slot_execute()
{
    m_scene->slot_executeCurrent();
}

void MainWindow::slot_deleteSelected()
{
    QList<QGraphicsItem*> items = m_scene->selectedItems();
    for (int i = 0; i < items.size(); ++i) {
        NodeItem* node = dynamic_cast<NodeItem*>(items[i]);
        if (node != 0) {
            m_scene->removeNode(node->id());
        }
    }
}

void MainWindow::slot_selectionChanged()
{
    NodeItem* node = firstSelectedNode();
    if (node == 0) {
        m_settingsStack->setCurrentWidget(m_emptyWidget);
        return;
    }

    if (node->nodeType() == NodeType::File) {
        m_settingsStack->setCurrentWidget(m_fileWidget);
        m_filePathEdit->setText(node->fileWidget()->filePath());
    }
    else {
        m_settingsStack->setCurrentWidget(m_archiveWidget);
        m_archiveNameEdit->blockSignals(true);
        m_archiveInputSpin->blockSignals(true);
        m_archiveNameEdit->setText(node->archiveWidget()->archiveName());
        m_archiveInputSpin->setValue(node->archiveWidget()->inputCount());
        m_archiveDirectoryEdit->setText(node->archiveWidget()->saveDirectory());
        m_archiveNameEdit->blockSignals(false);
        m_archiveInputSpin->blockSignals(false);
    }
}

void MainWindow::slot_showExecutionResult(bool success, const QString& message)
{
    if (success) {
        QMessageBox::information(this, QString::fromUtf8("Результат"), message);
    }
    else {
        QMessageBox::warning(this, QString::fromUtf8("Результат"), message);
    }
}

void MainWindow::slot_selectFileForNode()
{
    NodeItem* node = firstSelectedNode();
    if (node == 0 || node->nodeType() != NodeType::File || node->fileWidget() == 0) {
        return;
    }

    const QString path = QFileDialog::getOpenFileName(this,
                                                      QString::fromUtf8("Выбор файла"),
                                                      QString(),
                                                      QString::fromUtf8("Все файлы (*.*)"));
    if (path.isEmpty()) {
        return;
    }

    node->fileWidget()->setFilePath(path);
    m_filePathEdit->setText(path);
}

void MainWindow::slot_selectDirectoryForNode()
{
    NodeItem* node = firstSelectedNode();
    if (node == 0 || node->nodeType() != NodeType::Archive || node->archiveWidget() == 0) {
        return;
    }

    const QString path = QFileDialog::getExistingDirectory(this,
                                                            QString::fromUtf8("Каталог архивации"),
                                                            QString(),
                                                            QFileDialog::ShowDirsOnly);
    if (path.isEmpty()) {
        return;
    }

    node->archiveWidget()->setSaveDirectory(path);
    m_archiveDirectoryEdit->setText(path);
}

void MainWindow::slot_executeSelectedArchive()
{
    NodeItem* node = firstSelectedNode();
    if (node == 0 || node->nodeType() != NodeType::Archive) {
        QMessageBox::warning(this, QString::fromUtf8("Результат"), QString::fromUtf8("Выберите архивную ноду"));
        return;
    }

    QString message;
    const bool success = m_scene->executeArchive(node->id(), &message);
    slot_showExecutionResult(success, message);
}

void MainWindow::slot_archiveNameChanged(const QString& value)
{
    NodeItem* node = firstSelectedNode();
    if (node == 0 || node->nodeType() != NodeType::Archive || node->archiveWidget() == 0) {
        return;
    }
    node->archiveWidget()->setArchiveName(value);
}

void MainWindow::slot_archiveInputChanged(int value)
{
    NodeItem* node = firstSelectedNode();
    if (node == 0 || node->nodeType() != NodeType::Archive || node->archiveWidget() == 0) {
        return;
    }
    node->archiveWidget()->setInputCount(value);
    node->refreshGeometry();
    QMetaObject::invokeMethod(m_scene, "slot_updateConnections", Qt::DirectConnection);
}

void MainWindow::setupUi()
{
    setWindowTitle(QString::fromUtf8("NodeEditor Archive Tool (C++/Qt5.15)"));
    resize(1280, 800);
    setCentralWidget(m_view);

    QToolBar* toolbar = addToolBar(QString::fromUtf8("Инструменты"));
    QAction* addFileAction = toolbar->addAction(QString::fromUtf8("Добавить файл"));
    QAction* addArchiveAction = toolbar->addAction(QString::fromUtf8("Добавить архив"));
    QAction* connectAction = toolbar->addAction(QString::fromUtf8("Связать выбранные"));
    QAction* saveAction = toolbar->addAction(QString::fromUtf8("Сохранить"));
    QAction* loadAction = toolbar->addAction(QString::fromUtf8("Загрузить"));
    QAction* executeAction = toolbar->addAction(QString::fromUtf8("Выполнить"));
    QAction* deleteAction = toolbar->addAction(QString::fromUtf8("Удалить"));

    connect(addFileAction, SIGNAL(triggered()), this, SLOT(slot_addFileNode()));
    connect(addArchiveAction, SIGNAL(triggered()), this, SLOT(slot_addArchiveNode()));
    connect(connectAction, SIGNAL(triggered()), this, SLOT(slot_connectSelectedNodes()));
    connect(saveAction, SIGNAL(triggered()), this, SLOT(slot_saveGraph()));
    connect(loadAction, SIGNAL(triggered()), this, SLOT(slot_loadGraph()));
    connect(executeAction, SIGNAL(triggered()), this, SLOT(slot_execute()));
    connect(deleteAction, SIGNAL(triggered()), this, SLOT(slot_deleteSelected()));

    QDockWidget* dock = new QDockWidget(QString::fromUtf8("Параметры"), this);
    QWidget* content = new QWidget(dock);
    QVBoxLayout* contentLayout = new QVBoxLayout(content);

    m_settingsStack = new QStackedWidget(content);
    m_emptyWidget = new QWidget(m_settingsStack);
    m_fileWidget = new QWidget(m_settingsStack);
    m_archiveWidget = new QWidget(m_settingsStack);

    QVBoxLayout* emptyLayout = new QVBoxLayout(m_emptyWidget);
    emptyLayout->addWidget(new QLabel(QString::fromUtf8("Выберите ноду"), m_emptyWidget));

    QFormLayout* fileLayout = new QFormLayout(m_fileWidget);
    m_filePathEdit = new QLineEdit(m_fileWidget);
    m_filePathEdit->setReadOnly(true);
    QPushButton* selectFileButton = new QPushButton(QString::fromUtf8("Выбрать файл..."), m_fileWidget);
    fileLayout->addRow(QString::fromUtf8("Путь"), m_filePathEdit);
    fileLayout->addRow(QString(), selectFileButton);

    QFormLayout* archiveLayout = new QFormLayout(m_archiveWidget);
    m_archiveNameEdit = new QLineEdit(m_archiveWidget);
    m_archiveInputSpin = new QSpinBox(m_archiveWidget);
    m_archiveInputSpin->setMinimum(1);
    m_archiveInputSpin->setMaximum(10);
    m_archiveDirectoryEdit = new QLineEdit(m_archiveWidget);
    m_archiveDirectoryEdit->setReadOnly(true);
    QPushButton* selectDirectoryButton = new QPushButton(QString::fromUtf8("Выбрать папку..."), m_archiveWidget);
    QPushButton* executeArchiveButton = new QPushButton(QString::fromUtf8("Архивировать"), m_archiveWidget);
    archiveLayout->addRow(QString::fromUtf8("Имя"), m_archiveNameEdit);
    archiveLayout->addRow(QString::fromUtf8("Входы"), m_archiveInputSpin);
    archiveLayout->addRow(QString::fromUtf8("Каталог"), m_archiveDirectoryEdit);
    archiveLayout->addRow(QString(), selectDirectoryButton);
    archiveLayout->addRow(QString(), executeArchiveButton);

    m_settingsStack->addWidget(m_emptyWidget);
    m_settingsStack->addWidget(m_fileWidget);
    m_settingsStack->addWidget(m_archiveWidget);
    contentLayout->addWidget(m_settingsStack);

    dock->setWidget(content);
    addDockWidget(Qt::RightDockWidgetArea, dock);

    connect(selectFileButton, SIGNAL(clicked()), this, SLOT(slot_selectFileForNode()));
    connect(selectDirectoryButton, SIGNAL(clicked()), this, SLOT(slot_selectDirectoryForNode()));
    connect(executeArchiveButton, SIGNAL(clicked()), this, SLOT(slot_executeSelectedArchive()));
    connect(m_archiveNameEdit, SIGNAL(textChanged(QString)), this, SLOT(slot_archiveNameChanged(QString)));
    connect(m_archiveInputSpin, SIGNAL(valueChanged(int)), this, SLOT(slot_archiveInputChanged(int)));

    connect(m_scene, SIGNAL(selectionChanged()), this, SLOT(slot_selectionChanged()));
    connect(m_scene, SIGNAL(signal_executionFinished(bool,QString)), this, SLOT(slot_showExecutionResult(bool,QString)));
}

NodeItem* MainWindow::firstSelectedNode() const
{
    QList<QGraphicsItem*> items = m_scene->selectedItems();
    for (int i = 0; i < items.size(); ++i) {
        NodeItem* node = dynamic_cast<NodeItem*>(items[i]);
        if (node != 0) {
            return node;
        }
    }
    return 0;
}

NodeItem* MainWindow::secondSelectedNode() const
{
    QList<QGraphicsItem*> items = m_scene->selectedItems();
    int found = 0;
    for (int i = 0; i < items.size(); ++i) {
        NodeItem* node = dynamic_cast<NodeItem*>(items[i]);
        if (node != 0) {
            ++found;
            if (found == 2) {
                return node;
            }
        }
    }
    return 0;
}
