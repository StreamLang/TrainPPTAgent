# PPTAgent REST API 文档

## 概述
本文档描述了PPTAgent提供的REST API接口，专业用户可以直接通过这些接口提交完整的内容、大纲和素材来生成PPT。

## 基础URL
```
http://localhost:6800/api
```

## 接口列表

### 1. 生成PPT大纲
根据主题生成PPT大纲

**URL**: `/tools/aippt_outline`
**方法**: `POST`
**Content-Type**: `application/json`

**请求参数**:
```json
{
  "content": "PPT主题",
  "language": "中文",
  "model": "qwen3-235b",
  "stream": true
}
```

**响应**:
流式返回Markdown格式的大纲

### 2. 生成PPT内容
根据大纲和用户提供的内容生成PPT

**URL**: `/tools/aippt`
**方法**: `POST`
**Content-Type**: `application/json`

**请求参数**:
```json
{
  "content": "# 主题\n\n## 章节一\n### 小节1\n- 要点1\n- 要点2",
  "language": "中文",
  "style": "通用",
  "model": "qwen3-235b",
  "stream": true,
  "materials": [
    {
      "id": "material_1",
      "name": "图片1.jpg",
      "description": "相关图片描述"
    }
  ],
  "sections": [
    {
      "id": "section_1",
      "title": "章节一",
      "fields": [
        {
          "title": "小节1",
          "content": "用户提供的详细内容",
          "materials": ["material_1"]
        }
      ]
    }
  ]
}
```

**响应**:
流式返回JSON格式的PPT内容

### 3. 上传素材
上传图片素材

**URL**: `/upload_material`
**方法**: `POST`
**Content-Type**: `multipart/form-data`

**请求参数**:
- `file`: 文件对象
- `description`: 素材描述（可选）

**响应**:
```json
{
  "id": "唯一标识符",
  "name": "文件名",
  "path": "文件路径",
  "description": "素材描述",
  "size": 123456
}
```

### 4. 获取模板数据
获取PPT模板数据

**URL**: `/data/{filename}`
**方法**: `GET`

**响应**:
返回指定模板的JSON数据

## 使用示例

### Python示例
```python
import requests
import json

# 生成大纲
outline_data = {
    "content": "人工智能发展",
    "language": "中文",
    "model": "qwen3-235b",
    "stream": True
}

response = requests.post("http://localhost:6800/tools/aippt_outline", json=outline_data)
print(response.text)

# 上传素材
with open("image.jpg", "rb") as f:
    files = {"file": f}
    data = {"description": "AI相关图片"}
    response = requests.post("http://localhost:6800/upload_material", files=files, data=data)
    material_info = response.json()

# 生成PPT
ppt_data = {
    "content": "# 人工智能发展\n\n## 技术进展\n### 深度学习\n- 神经网络突破\n- 计算能力提升",
    "language": "中文",
    "style": "通用",
    "model": "qwen3-235b",
    "stream": True,
    "materials": [material_info],
    "sections": [
        {
            "id": "section_1",
            "title": "技术进展",
            "fields": [
                {
                    "title": "深度学习",
                    "content": "深度学习是机器学习的一个分支，它模仿人脑的工作方式来处理数据和创建模式，用于决策制定。",
                    "materials": [material_info["id"]]
                }
            ]
        }
    ]
}

response = requests.post("http://localhost:6800/tools/aippt", json=ppt_data)
print(response.text)
```

### JavaScript示例
```javascript
// 生成大纲
const outlineData = {
  content: "人工智能发展",
  language: "中文",
  model: "qwen3-235b",
  stream: true
};

fetch("http://localhost:6800/tools/aippt_outline", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(outlineData)
}).then(response => response.text()).then(data => {
  console.log(data);
});

// 上传素材
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("description", "AI相关图片");

fetch("http://localhost:6800/upload_material", {
  method: "POST",
  body: formData
}).then(response => response.json()).then(data => {
  console.log(data);
});

// 生成PPT
const pptData = {
  content: "# 人工智能发展\n\n## 技术进展\n### 深度学习\n- 神经网络突破\n- 计算能力提升",
  language: "中文",
  style: "通用",
  model: "qwen3-235b",
  stream: true,
  materials: [materialInfo],
  sections: [
    {
      id: "section_1",
      title: "技术进展",
      fields: [
        {
          title: "深度学习",
          content: "深度学习是机器学习的一个分支，它模仿人脑的工作方式来处理数据和创建模式，用于决策制定。",
          materials: [materialInfo.id]
        }
      ]
    }
  ]
};

fetch("http://localhost:6800/tools/aippt", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(pptData)
}).then(response => response.text()).then(data => {
  console.log(data);
});
```

## 错误处理
所有API接口在出错时会返回相应的HTTP状态码和错误信息：

- 400: 请求参数错误
- 500: 服务器内部错误

错误响应格式:
```json
{
  "error": "错误描述"
}
```