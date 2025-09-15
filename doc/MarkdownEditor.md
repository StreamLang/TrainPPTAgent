# Markdown 编辑器使用说明

## 功能概述

Markdown 编辑器允许用户通过 Markdown 语法创建内容，并将其转换为 PPT 演示文稿。该功能包括：

1. 实时 Markdown 编辑和预览
2. 与后端 AI 服务集成，将 Markdown 内容转换为 PPT
3. 轮询机制检查生成状态
4. 生成完成后在 PPTist 编辑器中展示结果

## 使用步骤

### 1. 访问 Markdown 编辑器

- 启动应用后，在首页点击"Markdown 编辑器"快捷访问按钮
- 或直接访问 `/markdown` 路由

### 2. 编写 Markdown 内容

在左侧编辑区域编写 Markdown 内容，例如：

```markdown
# 我的演示文稿

## 第一页标题

这是第一页的内容

## 第二页标题

这是第二页的内容
```

### 3. 实时预览

右侧区域会实时显示 Markdown 渲染效果。

### 4. 生成 PPT

点击"保存并生成PPT"按钮，系统将：

1. 将 Markdown 内容发送到后端处理
2. 创建一个异步任务并返回任务ID
3. 开始轮询任务状态（每2秒检查一次）
4. 任务完成后自动跳转到 PPT 输出页面

### 5. 查看和编辑生成的 PPT

在 PPT 输出页面，您可以：

- 查看生成的 PPT 演示文稿
- 使用完整的 PPTist 编辑器功能进行进一步编辑
- 导出 PPT 文件

## 技术实现

### 前端组件

1. `MarkdownEditor.vue` - Markdown 编辑和预览组件
2. `PPTOutput/index.vue` - PPT 结果展示和编辑组件

### 路由

- `/markdown` - Markdown 编辑器页面
- `/ppt/output` - PPT 输出页面

### API 接口

1. `POST /api/tools/aippt_rest` - 提交 Markdown 内容生成 PPT
2. `GET /api/tools/aippt_result` - 查询任务状态

### 数据流

1. 用户在 Markdown 编辑器中编写内容
2. 点击生成按钮后，内容通过 API 发送到后端
3. 后端处理完成后返回结果
4. 前端轮询检查状态，完成后跳转到输出页面
5. 输出页面使用 PPTist 初始化并展示生成的 PPT

## 注意事项

1. 请确保后端服务正常运行
2. Markdown 内容应遵循一定的结构以便更好地生成 PPT
3. 生成过程可能需要一些时间，请耐心等待
4. 生成的 PPT 可以在 PPTist 编辑器中进一步编辑和定制