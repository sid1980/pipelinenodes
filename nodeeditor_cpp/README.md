# nodeeditor_cpp

Переписанная C++17/Qt5.15 версия проекта NodeEditor Archive Tool.

## Зависимости

Установите следующие пакеты/инструменты:

- C++17 совместимый компилятор (GCC 9+, Clang 10+, MSVC 2019+)
- CMake 3.16+
- Qt 5.15 (модуль Widgets)
- qmake (обычно ставится вместе с Qt)
- googletest (для тестов)
- tar (для архивации при выполнении графа)

## Сборка

```bash
cmake -S nodeeditor_cpp -B build/nodeeditor_cpp
cmake --build build/nodeeditor_cpp -j
```

## Запуск

```bash
./build/nodeeditor_cpp/nodeeditor_cpp
```

## Тесты

```bash
ctest --test-dir build/nodeeditor_cpp --output-on-failure
```
