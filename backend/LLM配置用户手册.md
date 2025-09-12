# LLM配置用户手册

## 1. 概述

本文档详细说明了如何配置PPT-Agent项目以使用您本地部署的大语言模型。根据您提供的信息，您的实际大模型配置如下：

- 模型名称: `qwen3-235b`
- API地址: `http://192.168.64.22:3001/v1/chat/completions`
- API密钥: `sk-kkAe3QB58hu7cSgiC386D5100dE54b1bBb77A208Ef015cBc`

## 2. 配置文件修改说明

### 2.1 simpleOutline服务配置

#### 2.1.1 环境变量文件 (.env)

文件路径: `backend/simpleOutline/.env`

主要修改内容:
```env
MODEL_PROVIDER=local
LLM_MODEL=qwen3-235b
LOCAL_API_URL=http://192.168.64.22:3001/v1/chat/completions
LOCAL_API_KEY=sk-kkAe3QB58hu7cSgiC386D5100dE54b1bBb77A208Ef015cBc
```

#### 2.1.2 模型创建逻辑 (create_model.py)

文件路径: `backend/simpleOutline/create_model.py`

关键修改点:
- 添加了对`LOCAL_API_KEY`环境变量的支持
- 当环境变量未设置时，默认使用`EMPTY`作为API密钥

### 2.2 slide_agent服务配置

#### 2.2.1 环境变量文件 (.env)

文件路径: `backend/slide_agent/.env`

主要修改内容:
```env
LOCAL_API_URL=http://192.168.64.22:3001/v1/chat/completions
LOCAL_API_KEY=sk-kkAe3QB58hu7cSgiC386D5100dE54b1bBb77A208Ef015cBc
```

#### 2.2.2 模型配置文件 (config.py)

文件路径: `backend/slide_agent/slide_agent/config.py`

主要修改内容:
```python
PPT_WRITER_AGENT_CONFIG = {
    "provider": "local_openai",
    "model": "qwen3-235b",
}

PPT_CHECKER_AGENT_CONFIG = {
    "provider": "local_openai",
    "model": "qwen3-235b",
}
```

#### 2.2.3 模型创建逻辑 (create_model.py)

文件路径: `backend/slide_agent/slide_agent/create_model.py`

关键修改点:
- 更新了`local_openai`提供者的实现，使用新的API地址和密钥配置
- 添加了对`LOCAL_API_KEY`环境变量的支持

## 3. 前端配置修改

### 3.1 Outline页面

文件路径: `frontend/src/views/Outline/index.vue`

主要修改:
- 默认模型值设置为`qwen3-235b`
- 模型选择显示文本更新为`qwen3-235b (本地部署)`

### 3.2 PPT页面

文件路径: `frontend/src/views/PPT/index.vue`

主要修改:
- 默认模型值设置为`qwen3-235b`

## 4. 验证配置

完成上述修改后，您可以通过以下步骤验证配置是否正确：

1. 启动simpleOutline服务:
   ```bash
   cd backend/simpleOutline
   python main_api.py
   ```

2. 启动slide_agent服务:
   ```bash
   cd backend/slide_agent
   python main_api.py
   ```

3. 启动前端服务:
   ```bash
   cd frontend
   npm run dev
   ```

4. 访问前端界面，创建PPT大纲并生成内容，观察是否正常调用您的本地大模型。

## 5. 故障排除

### 5.1 连接问题

如果出现连接问题，请检查:
- 确认API地址`http://192.168.64.22:3001/v1/chat/completions`可访问
- 确认网络连通性
- 检查防火墙设置

### 5.2 认证问题

如果出现认证问题，请检查:
- 确认API密钥正确无误
- 检查API密钥是否有足够的权限

### 5.3 模型问题

如果模型调用失败，请检查:
- 确认模型`qwen3-235b`在您的部署中可用
- 检查模型是否正确加载

## 6. 注意事项

1. 所有配置修改后需要重启相关服务才能生效
2. 请妥善保管您的API密钥，不要泄露给无关人员
3. 如果需要更换模型或API地址，请相应修改所有相关配置文件