cmake_minimum_required(VERSION 3.16)
project(NodeEditorCpp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

enable_testing()

find_package(Qt5 5.15 REQUIRED COMPONENTS Widgets)
find_package(GTest QUIET)

add_executable(nodeeditor_cpp
    src/main.cpp
    src/MainWindow.cpp
    src/NodeEditorScene.cpp
    src/NodeItem.cpp
    src/ConnectionItem.cpp
    src/FileNodeWidget.cpp
    src/ArchiveNodeWidget.cpp
)

target_include_directories(nodeeditor_cpp PRIVATE src)

target_link_libraries(nodeeditor_cpp PRIVATE Qt5::Widgets)

if (GTest_FOUND)
    add_executable(nodeeditor_cpp_tests
        tests/NodeEditorSceneTests.cpp
        src/NodeEditorScene.cpp
        src/NodeItem.cpp
        src/ConnectionItem.cpp
        src/FileNodeWidget.cpp
        src/ArchiveNodeWidget.cpp
    )
    target_include_directories(nodeeditor_cpp_tests PRIVATE src)
    target_link_libraries(nodeeditor_cpp_tests PRIVATE Qt5::Widgets GTest::gtest GTest::gtest_main)
    add_test(NAME nodeeditor_cpp_tests COMMAND nodeeditor_cpp_tests)
endif()
