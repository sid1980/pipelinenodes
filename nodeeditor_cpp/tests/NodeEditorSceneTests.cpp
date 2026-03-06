#include "NodeEditorScene.h"

#include <gtest/gtest.h>

TEST(NodeEditorSceneTests, CreatesNodes)
{
    NodeEditorScene scene;
    const QString fileId = scene.addFileNode(QPointF(10.0, 20.0));
    const QString archiveId = scene.addArchiveNode(QPointF(30.0, 40.0));
    EXPECT_FALSE(fileId.isEmpty());
    EXPECT_FALSE(archiveId.isEmpty());
    EXPECT_EQ(2U, scene.nodes().size());
}

TEST(NodeEditorSceneTests, ConnectsNodes)
{
    NodeEditorScene scene;
    const QString fileId = scene.addFileNode(QPointF(0.0, 0.0));
    const QString archiveId = scene.addArchiveNode(QPointF(100.0, 0.0));
    const bool connected = scene.connectFileToArchive(fileId, archiveId, 0);
    EXPECT_TRUE(connected);
    EXPECT_EQ(1U, scene.connections().size());
}
