#include "MainWindow.h"

#include <QApplication>

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("NodeEditorCpp");

    MainWindow window;
    window.show();

    return app.exec();
}
