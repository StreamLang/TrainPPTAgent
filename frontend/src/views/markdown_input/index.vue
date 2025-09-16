<template>
  <div class="markdown-editor-container">
    <div class="editor-header">
      <h2>Markdown 编辑器</h2>
      <div class="header-controls">
        <!-- 添加模型选择 -->
        <select v-model="selectedModel" class="model-select">
          <option value="qwen3-235b">Qwen3-235b</option>
          <option value="gpt-4">GPT-4</option>
          <option value="claude-3">Claude-3</option>
        </select>
        <button
            @click="handleSave"
            :disabled="isSaving"
            class="save-button"
        >
          {{ isSaving ? '生成中...' : '保存并生成PPT' }}
        </button>
      </div>
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
              <img :src="template.cover" :alt="template.name"/>
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
        <li>系统会使用 aippt_rest 创建异步任务并获取 task_id</li>
        <li>然后使用 aippt_rest_result 轮询获取任务结果</li>
        <li>处理完成后自动跳转到PPT展示页面，使用与PPT页面相同的逻辑渲染PPT</li>
      </ul>
    </div>
  </div>
</template>

<script>
import {marked} from 'marked'
import {useRouter} from 'vue-router'
import {generateAIPPT, getAIPPTResult} from '@/services/aippt-rest'
import useAIPPT from '@/hooks/useAIPPT'
import {useSlidesStore} from '@/store'
import api from '@/services'
import SessionManager from '@/utils/sessionManager'

export default {
  name: 'MarkdownEditor',
  setup() {
    const router = useRouter()
    const slidesStore = useSlidesStore()
    // 使用AIPPT hook来处理模板应用
    const {AIPPTGenerator} = useAIPPT()

    return {
      router,
      slidesStore,
      AIPPTGenerator
    }
  },
  data() {
    return {
      markdownContent: localStorage.getItem('markdownContent') || '',
      renderedMarkdown: '',
      isSaving: false,
      // 模型选择相关数据
      selectedModel: 'qwen3-235b', // 默认模型
      // 模板相关数据
      templates: [
        {name: '红色通用', id: 'template_1', cover: '/api/data/template_1.jpg'},
        {name: '蓝色通用', id: 'template_2', cover: '/api/data/template_2.jpg'},
        {name: '紫色通用', id: 'template_3', cover: '/api/data/template_3.jpg'},
        {name: '莫兰迪配色', id: 'template_4', cover: '/api/data/template_4.jpg'},
      ],
      selectedTemplate: 'template_1', // 默认选择第一个模板
      loading: false
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

      if (!this.selectedTemplate) {
        alert('请选择一个模板')
        return
      }

      try {
        this.isSaving = true

        // 使用 aippt_rest 创建异步任务并获取 task_id
        const taskResponse = await generateAIPPT(this.markdownContent, this.selectedModel)

        if (taskResponse.status === 'processing') {
          // 异步处理，轮询获取结果
          const taskId = taskResponse.task_id
          let result = null
          let attempts = 0
          const maxAttempts = 30 // 最多尝试30次，每次间隔2秒，总共60秒超时

          while (attempts < maxAttempts) {
            attempts++
            // 等待2秒后查询结果
            await new Promise(resolve => setTimeout(resolve, 2000))

            // 使用 aippt_rest_result 获取任务结果
            const taskResult = await getAIPPTResult(taskId)

            if (taskResult.status === 'completed') {
              result = taskResult
              break
            }
            else if (taskResult.status === 'failed') {
              throw new Error(taskResult.error || 'PPT生成失败')
            }
            // 如果还在处理中，继续轮询
          }

          if (!result) {
            throw new Error('PPT生成超时')
          }

          // 生成成功，开始渲染PPT
          await this.renderPPT(result.result)
        }
        else if (taskResponse.status === 'failed') {
          // 生成失败
          this.isSaving = false
          alert('PPT生成失败: ' + (taskResponse.error || '未知错误'))
        }
      }
      catch (error) {
        console.error('生成PPT失败:', error)
        alert('生成PPT失败: ' + error.message)
        this.isSaving = false
      }
    },

    // 渲染PPT的函数，与PPT页面的逻辑保持一致
    async renderPPT(aipptResult) {
      this.loading = true
      this.slidesStore.resetSlides()

      try {
        // 获取模板数据
        const templateData = await api.getFileData(this.selectedTemplate)
        const templateSlides = templateData.slides
        const templateTheme = templateData.theme
        this.slidesStore.setTheme(templateTheme)

        // 使用AIPPTGenerator渲染幻灯片
        const slides = []
        for (const slideData of aipptResult.slides) {
          const slideGenerator = this.AIPPTGenerator(templateSlides, [slideData], [])
          for (const generatedSlide of slideGenerator) {
            slides.push(generatedSlide)
            this.slidesStore.addSlide(generatedSlide)
          }
        }

        // 生成session_id并保存数据
        const sessionId = 'session_' + Date.now()

        // 保存PPT数据到SessionManager
        const pptData = {
          slides: this.slidesStore.slides,
          theme: this.slidesStore.theme
        }
        SessionManager.storePPTData(pptData, sessionId, 'ppt')

        // 跳转到编辑器页面
        this.loading = false
        this.isSaving = false
        this.router.push(`/editor?session_id=${sessionId}`)
      }
      catch (error) {
        console.error('渲染PPT失败:', error)
        this.loading = false
        this.isSaving = false
        alert('渲染PPT失败: ' + error.message)
      }
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

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.model-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
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

/* 进度提示样式 */
.progress-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease;
}

.progress-spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.progress-text {
  font-size: 0.9rem;
  color: #475569;
  font-weight: 500;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: translateY(-10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
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