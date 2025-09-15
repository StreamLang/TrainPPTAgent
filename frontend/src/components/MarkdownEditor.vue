<template>
  <div class="markdown-editor-container">
    <div class="editor-header">
      <h2>Markdown 编辑器</h2>
      <button 
        @click="handleSave" 
        :disabled="isSaving"
        class="save-button"
      >
        {{ isSaving ? '生成中...' : '保存并生成PPT' }}
      </button>
    </div>
    
    <div class="editor-columns">
      <div class="editor-area">
        <textarea
          v-model="markdownContent"
          placeholder="输入Markdown内容...
示例格式：
# 我的演示文稿

## 第一页标题

这是第一页的内容

## 第二页标题

这是第二页的内容"
          class="md-editor"
          @input="updatePreview"
        ></textarea>
      </div>
      <div 
        class="preview-area"
        v-html="renderedMarkdown"
      ></div>
    </div>
    
    <!-- 模板选择区域 -->
    <div class="template-selection" v-if="templates.length > 0">
      <h3>选择模板</h3>
      <div class="templates-container">
        <div class="templates">
          <div
            class="template-card"
            :class="{ selected: selectedTemplate === template.id }"
            v-for="template in templates"
            :key="template.id"
            @click="selectedTemplate = template.id"
          >
            <div class="template-image">
              <img :src="template.cover" :alt="template.name" />
              <div class="overlay">
                <div class="check-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20,6 9,17 4,12"></polyline>
                  </svg>
                </div>
              </div>
            </div>
            <div class="template-info">
              <span class="template-name">{{ template.name || '经典模板' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="instructions">
      <h3>使用说明</h3>
      <ul>
        <li>在左侧编辑 Markdown 内容</li>
        <li>右侧会实时预览渲染效果</li>
        <li>选择一个模板用于生成PPT</li>
        <li>点击"保存并生成PPT"按钮将内容发送到后端处理</li>
        <li>系统会轮询处理状态，完成后自动跳转到PPT展示页面</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import { useRouter } from 'vue-router'

export default {
  name: 'MarkdownEditor',
  setup() {
    const router = useRouter()
    
    return {
      router
    }
  },
  data() {
    return {
      markdownContent: localStorage.getItem('markdownContent') || '',
      renderedMarkdown: '',
      isSaving: false,
      pollInterval: null,
      // 模板相关数据
      templates: [
        { name: '红色通用', id: 'template_1', cover: '/api/data/template_1.jpg' },
        { name: '蓝色通用', id: 'template_2', cover: '/api/data/template_2.jpg' },
        { name: '紫色通用', id: 'template_3', cover: '/api/data/template_3.jpg' },
        { name: '莫兰迪配色', id: 'template_4', cover: '/api/data/template_4.jpg' },
      ],
      selectedTemplate: 'template_1' // 默认选择第一个模板
    }
  },
  mounted() {
    this.updatePreview()
  },
  methods: {
    updatePreview() {
      this.renderedMarkdown = marked(this.markdownContent)
      // 保存到本地存储
      localStorage.setItem('markdownContent', this.markdownContent)
    },
    
    async handleSave() {
      if (!this.markdownContent.trim()) {
        alert('请输入Markdown内容')
        return
      }
      
      try {
        this.isSaving = true
        
        // 调用后端API生成PPT
        const response = await fetch('/api/tools/aippt_rest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            markdown: this.markdownContent
          }),
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        const taskId = data.task_id
        
        if (!taskId) {
          throw new Error('未能获取任务ID')
        }
        
        // 轮询检查任务状态
        this.pollTaskStatus(taskId)
      } catch (error) {
        console.error('生成PPT失败:', error)
        alert('生成PPT失败: ' + error.message)
        this.isSaving = false
      }
    },
    
    pollTaskStatus(taskId) {
      // 清除之前的轮询（如果有的话）
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
      }
      
      // 开始轮询
      this.pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`/api/tools/aippt_result?task_id=${taskId}`)
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const data = await response.json()
          
          if (data.status === 'completed') {
            // 任务完成，跳转到output页面
            clearInterval(this.pollInterval)
            this.isSaving = false
            
            // 生成一个临时的session_id
            const sessionId = 'session_' + Date.now()
            
            // 将结果存储到本地存储中，供output页面使用
            localStorage.setItem(`pptResult_${sessionId}`, JSON.stringify({
              ...data.result,
              template: this.selectedTemplate // 传递选中的模板
            }))
            
            // 跳转到output页面
            this.router.push({
              path: '/ppt/output',
              query: { session_id: sessionId }
            })
          } else if (data.status === 'failed') {
            // 任务失败
            clearInterval(this.pollInterval)
            this.isSaving = false
            alert('PPT生成失败: ' + (data.error || '未知错误'))
          }
          // 如果是processing状态，继续轮询
        } catch (error) {
          console.error('检查任务状态失败:', error)
          clearInterval(this.pollInterval)
          this.isSaving = false
          alert('检查任务状态失败: ' + error.message)
        }
      }, 2000) // 每2秒检查一次
    }
  },
  
  beforeUnmount() {
    // 清除轮询
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
  }
}
</script>

<style scoped>
.markdown-editor-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.editor-header h2 {
  margin: 0;
  color: #333;
}

.save-button {
  padding: 10px 20px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.save-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.editor-columns {
  display: flex;
  gap: 20px;
  height: 70vh;
}

.editor-area,
.preview-area {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: auto;
}

.md-editor {
  width: 100%;
  height: 100%;
  padding: 12px;
  border: none;
  resize: none;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

.preview-area {
  padding: 12px;
  background-color: white;
}

.preview-area :deep(h1) {
  font-size: 2em;
  margin: 0.67em 0;
}

.preview-area :deep(h2) {
  font-size: 1.5em;
  margin: 0.83em 0;
}

.preview-area :deep(h3) {
  font-size: 1.17em;
  margin: 1em 0;
}

.preview-area :deep(p) {
  margin: 1em 0;
}

.preview-area :deep(ul),
.preview-area :deep(ol) {
  margin: 1em 0;
  padding-left: 40px;
}

.preview-area :deep(li) {
  margin: 0.5em 0;
}

.preview-area :deep(code) {
  background-color: #f4f4f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
}

.preview-area :deep(pre) {
  background-color: #f4f4f4;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.preview-area :deep(pre code) {
  background: none;
  padding: 0;
}

.preview-area :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 1em 0;
  color: #666;
}

.preview-area :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.preview-area :deep(th),
.preview-area :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.preview-area :deep(th) {
  background-color: #f8f8f8;
  font-weight: bold;
}

/* 模板选择区域样式 */
.template-selection {
  margin: 20px 0;
}

.template-selection h3 {
  margin-bottom: 15px;
  color: #333;
}

.templates-container {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
}

.templates {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.template-card {
  position: relative;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px -4px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.template-card.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15), 0 12px 28px -6px rgba(59, 130, 246, 0.25);
}

.template-card.selected .overlay {
  opacity: 1;
  visibility: visible;
}

.template-card.selected .template-info {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: #fff;
}

.template-image {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
}

.template-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.template-card:hover .template-image img {
  transform: scale(1.045);
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(59, 130, 246, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transition: all 0.25s ease;
}

.check-icon {
  width: 32px;
  height: 32px;
  color: #fff;
  background: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
}

.check-icon svg {
  width: 16px;
  height: 16px;
}

.template-info {
  padding: 12px 14px;
  background: #f8fafc;
  transition: all 0.25s ease;
}

.template-name {
  font-size: 14px;
  font-weight: 700;
  color: inherit;
}

.instructions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f8ff;
  border-radius: 4px;
  border: 1px solid #cce6ff;
}

.instructions h3 {
  margin-top: 0;
  color: #333;
}

.instructions ul {
  padding-left: 20px;
}

.instructions li {
  margin: 8px 0;
}

@media (max-width: 768px) {
  .editor-columns {
    flex-direction: column;
    height: auto;
  }
  
  .templates-container {
    padding: 16px;
  }
  
  .templates {
    grid-template-columns: 1fr;
    gap: 14px;
  }
}
</style>