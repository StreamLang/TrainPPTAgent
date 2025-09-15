<template>
  <div class="aippt-page">
    <!-- 全局背景：渐变 + 网格 -->
    <div class="page-bg" aria-hidden="true">
      <div class="bg-blob b1"></div>
      <div class="bg-blob b2"></div>
      <div class="grid"></div>
    </div>

    <div class="aippt-dialog">
      <!-- Header Section -->
      <div class="header-section">
        <div class="brand">
          <h1 class="title">
            <span class="title-icon">🤖</span>
            PPTAgent
          </h1>
          <div class="subtitle">
            确认下方内容大纲，开始选择模板
          </div>
        </div>
      </div>

      <!-- Outline Section -->
      <div class="outline-section">
        <div class="outline-header">
          <h3 class="section-title">📄 内容大纲</h3>
          <div class="outline-actions-top">
            <button class="secondary-btn" @click="toggleEditMode">
              <span class="btn-icon">{{ isEditMode ? '👁️' : '✏️' }}</span>
              {{ isEditMode ? '预览模式' : '编辑模式' }}
            </button>
            <button class="secondary-btn" @click="saveOutline" :disabled="!isEditMode">
              <span class="btn-icon">💾</span>
              保存大纲
            </button>
            <button class="secondary-btn" @click="goBackToHome">
              <span class="btn-icon">↩️</span>
              返回首页
            </button>
          </div>
        </div>

        <div class="outline-content">
          <div class="outline-editor">
            <div v-if="isEditMode">
              <textarea
                v-model="outline"
                class="outline-textarea"
                placeholder="在此编辑Markdown大纲内容..."
                rows="20"
              ></textarea>
            </div>
            <div v-else>
              <div class="outline-preview-content" v-html="renderedOutline"></div>
            </div>
          </div>
        </div>

        <div class="outline-actions">
          <button class="primary-btn" @click="goPPT">
            <span class="btn-icon">🎨</span>
            进一步完善
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import message from '@/utils/message'
import { marked } from 'marked'
import SessionManager from '@/utils/sessionManager'

const router = useRouter()
const route = useRoute()

// 从sessionStorage读取大纲数据
const sessionIdFromQuery = route.query.session_id as string
let outlineData = { outline: '', language: '中文', model: 'qwen3-235b' }

if (sessionIdFromQuery) {
  const storedData = SessionManager.getOutlineData(sessionIdFromQuery)
  if (storedData) {
    outlineData = storedData
  }
}

const language = ref(outlineData.language)
const outline = ref(outlineData.outline)
const model = ref(outlineData.model)
const outlineRef = ref<HTMLElement>()
const isEditMode = ref(false)

// 渲染Markdown为HTML
const renderedOutline = computed(() => {
  return marked(outline.value)
})

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value
}

const goBackToHome = () => {
  router.push({ name: 'Home' })
}




// 保存大纲数据
const saveOutline = () => {
  const currentOutline = outline.value
  
  // 使用SessionManager存储outline数据
  const sessionId = SessionManager.storeOutlineData({
    outline: currentOutline,
    language: language.value,
    model: model.value
  }, sessionIdFromQuery)
  
  message.success('已缓存当前内容至本地')
  console.log('大纲数据已保存，sessionId:', sessionId)
}

const goPPT = () => {
  // 确保保存最新的编辑内容
  saveOutline()
  
  // 通过sessionId跳转到PPT页面
  router.push({
    name: 'PPT',
    query: {
      session_id: sessionIdFromQuery
    }
  })
}

// 设置自动保存和快捷键
const setupAutoSave = () => {
  if (!sessionIdFromQuery) return
  
  // 监听大纲内容变化，实现自动保存
  let saveTimeout: number | null = null
  const autoSave = () => {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    saveTimeout = setTimeout(() => {
      if (outline.value.trim() && isEditMode.value) {
        saveOutline()
        console.log('大纲内容已自动保存')
      }
    }, 3000) // 3秒后自动保存
  }
  
  // 设置Ctrl+S快捷键
  const handleKeyDown = (event: KeyboardEvent) => {
    // Ctrl+S 保存
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault() // 阻止浏览器默认保存行为
      saveOutline()
    }
  }
  
  // 监听大纲内容变化
  const unwatch = watch(() => outline.value, autoSave, { deep: true })
  
  // 添加快捷键监听
  window.addEventListener('keydown', handleKeyDown)
  
  // 页面卸载时清除监听
  onUnmounted(() => {
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    unwatch()
    window.removeEventListener('keydown', handleKeyDown)
  })
}

// 页面加载时设置自动保存
onMounted(() => {
  // 页面加载时自动进入编辑模式
  isEditMode.value = true
  setupAutoSave()
})
</script>

<style lang="scss" scoped>
/* 与大纲页保持同样的页面骨架与背景 */
  /* 页面容器，提供稳定的全屏背景承载 */
.aippt-page {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
}

/* 背景层 */
.page-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: radial-gradient(1200px 600px at 10% -10%, rgba(102, 126, 234, 0.12), rgba(0, 0, 0, 0) 60%),
    radial-gradient(1000px 600px at 90% 110%, rgba(118, 75, 162, 0.12), rgba(0, 0, 0, 0) 60%),
    linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  pointer-events: none;
}
.page-bg .grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(15, 23, 42, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 23, 42, 0.04) 1px, transparent 1px);
  background-size: 32px 32px, 32px 32px;
  mask-image: radial-gradient(60% 50% at 50% 50%, #000 60%, transparent 100%);
}
.bg-blob {
  position: absolute;
  filter: blur(40px);
  opacity: 0.6;
}
.bg-blob.b1 { width: 520px; height: 520px; left: -160px; top: -160px; background: #c7d2fe; }
.bg-blob.b2 { width: 420px; height: 420px; right: -120px; bottom: -120px; background: #e9d5ff; }

/* 主内容卡片 */
.aippt-dialog {
  position: relative;
  z-index: 1;
  margin: 0 auto;
  padding: 40px 24px 32px;
  max-width: 1160px;
  box-sizing: border-box;
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 3rem;
  color: #475569;
}

.brand {
  margin-bottom: 2rem;

  .title {
    font-size: 3rem;
    font-weight: 800;
    margin: 0 0 1rem 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 3s ease infinite;

    .title-icon {
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
  }

  .subtitle {
    font-size: 1.1rem;
    line-height: 1.6;
    max-width: 600px;
    margin: 0 auto;
    color: #475569;
  }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;

  .progress-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    opacity: 0.6;
    transition: opacity 0.3s ease;
    color: #475569;

    &.active {
      opacity: 1;
      font-weight: 600;
    }

    .step-circle {
      width: 2rem;
      height: 2rem;
      border-radius: 50%;
      background: #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      border: 2px solid #cbd5e1;
      transition: all 0.3s ease;
    }

    &.active .step-circle {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      transform: scale(1.1);
      border-color: transparent;
    }
  }

  .progress-line {
    width: 4rem;
    height: 2px;
    background: #e2e8f0;
    transition: background 0.3s ease;

    &.completed {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  }
}

/* Setup Section */
.setup-section {
  background: white;
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

.input-section {
  margin-bottom: 2rem;

  .input-wrapper {
    position: relative;
    background: #f8fafc;
    border-radius: 1rem;
    border: 2px solid #e2e8f0;
    transition: all 0.3s ease;
    overflow: hidden;

    &:focus-within {
      border-color: #667eea;
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }

    .main-input {
      width: 100%;
      padding: 1.25rem 1.5rem;
      border: none;
      background: transparent;
      font-size: 1.1rem;
      outline: none;
      resize: none;

      &::placeholder {
        color: #94a3b8;
      }
    }

    .input-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem 1.25rem;
      gap: 1rem;

      .character-count {
        font-size: 0.875rem;
        color: #64748b;
      }

      .generate-btn {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
        font-size: 0.95rem;

        &:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-icon {
          font-size: 1.1rem;
        }
      }
    }
  }
}

/* Recommendations Section */
.recommendations-section {
  margin-bottom: 2rem;

  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;

    .recommend-item {
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      padding: 0.75rem 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 0.9rem;
      text-align: left;

      &:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      }
    }
  }
}

/* Configuration Section */
.config-section {
  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .config-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;

    .config-item {
      .config-label {
        display: block;
        font-weight: 500;
        margin-bottom: 0.5rem;
        color: #475569;
        font-size: 0.9rem;
      }

      .config-select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        background: white;
        font-size: 0.9rem;
        cursor: pointer;
        transition: border-color 0.3s ease;

        &:focus {
          outline: none;
          border-color: #667eea;
        }
      }
      
      .config-select-static {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        background: #f9fafb;
        color: #475569;
        font-size: 0.9rem;
      }
    }
  }
}

/* Outline Section */
.outline-section {
  background: white;
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);

  .outline-header {
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .section-title {
      font-size: 1.3rem;
      font-weight: 600;
      margin: 0;
      color: #334155;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .outline-actions-top {
      display: flex;
      gap: 0.75rem;
    }
  }

  .outline-content {
    margin-bottom: 2rem;

    .outline-preview {
      position: relative;

      .typing-indicator {
        display: flex;
        gap: 0.25rem;
        margin-bottom: 1rem;
        align-items: center;

        &::before {
          content: 'AI正在生成大纲';
          margin-right: 0.5rem;
          color: #64748b;
          font-size: 0.9rem;
        }

        .typing-dot {
          width: 0.5rem;
          height: 0.5rem;
          background: #667eea;
          border-radius: 50%;
          animation: typingBounce 1.4s infinite;

          &:nth-child(2) { animation-delay: 0.2s; }
          &:nth-child(3) { animation-delay: 0.4s; }
        }
      }

      .outline-text {
        max-height: 400px;
        padding: 1.5rem;
        background: #f8fafc;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        overflow-y: auto;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }

    .outline-editor {
      max-height: 600px;
      padding: 1.5rem;
      background: #f8fafc;
      border-radius: 1rem;
      border: 1px solid #e2e8f0;
      overflow-y: auto;

      .outline-textarea {
        width: 100%;
        min-height: 300px;
        padding: 1rem;
        border: 1px solid #cbd5e1;
        border-radius: 0.5rem;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        resize: vertical;
        box-sizing: border-box;

        &:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
      }

      /* 大纲工具栏 */
      .outline-toolbar {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;

        .toolbar-btn {
          background: #667eea;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          transition: all 0.3s ease;
          font-size: 0.9rem;

          &:hover {
            background: #5a67d8;
            transform: translateY(-1px);
          }
        }
      }

      /* 大纲条目编辑器 */
      .outline-items-editor {
        .outline-item {
          margin-bottom: 1rem;
          padding: 1rem;
          background: white;
          border-radius: 0.5rem;
          border: 1px solid #e2e8f0;
          transition: all 0.3s ease;

          &:hover {
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
          }

          &.child {
            margin-top: 0.5rem;
            background: #f8fafc;
          }

          .item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;

            .item-title {
              flex: 1;
              min-width: 0;

              .title-input {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #cbd5e1;
                border-radius: 0.25rem;
                font-size: 1rem;
                font-weight: 600;

                &:focus {
                  outline: none;
                  border-color: #667eea;
                }
              }

              .title-text {
                font-size: 1rem;
                font-weight: 600;
                color: #334155;
                cursor: pointer;
                padding: 0.25rem 0;
                display: inline-block;

                &:hover {
                  color: #667eea;
                }
              }
            }

            .item-actions {
              display: flex;
              gap: 0.5rem;

              .action-btn {
                background: #f1f5f9;
                border: 1px solid #d1d5db;
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.8rem;

                &:hover {
                  background: #e2e8f0;
                  transform: translateY(-1px);
                }

                &.danger:hover {
                  background: #fef2f2;
                  border-color: #f87171;
                  color: #dc2626;
                }
              }
            }
          }

          .item-content {
            width: 100%;
            min-height: 60px;
            padding: 0.75rem;
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            font-family: inherit;
            font-size: 0.9rem;
            line-height: 1.5;
            resize: vertical;
            box-sizing: border-box;

            &:focus {
              outline: none;
              border-color: #667eea;
              box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
          }
        }
      }

      .outline-preview-content {
        h1 {
          font-size: 1.5rem;
          font-weight: bold;
          margin: 1rem 0;
          color: #334155;
        }

        h2 {
          font-size: 1.3rem;
          font-weight: 600;
          margin: 0.8rem 0;
          color: #475569;
        }

        h3 {
          font-size: 1.1rem;
          font-weight: 500;
          margin: 0.6rem 0;
          color: #64748b;
        }

        ul {
          margin: 0.5rem 0;
          padding-left: 1.5rem;

          li {
            margin: 0.3rem 0;
          }
        }

        p {
          margin: 0.5rem 0;
          line-height: 1.6;
        }
      }





      .outline-textarea {
        width: 100%;
        min-height: 400px;
        padding: 1.5rem;
        border: 2px solid #e2e8f0;
        border-radius: 1rem;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        resize: vertical;
        background: #f8fafc;
        box-sizing: border-box;
        transition: all 0.3s ease;

        &:focus {
          outline: none;
          border-color: #667eea;
          background: white;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        &::placeholder {
          color: #94a3b8;
        }
      }
    }
  }

  .outline-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;

    .primary-btn {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      border: none;
      padding: 1rem 2rem;
      border-radius: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
      font-size: 1rem;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
      }

      .btn-icon {
        font-size: 1.2rem;
      }
    }

    .secondary-btn {
      background: #f1f5f9;
      color: #475569;
      border: 1px solid #d1d5db;
      padding: 1rem 2rem;
      border-radius: 0.75rem;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
      font-size: 1rem;

      &:hover {
        background: #e2e8f0;
        transform: translateY(-2px);
      }

      .btn-icon {
        font-size: 1.2rem;
      }
    }
  }
}

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-0.5rem); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .aippt-dialog {
    padding: 1rem;
  }

  .setup-section,
  .outline-section {
    padding: 1.5rem;
  }

  .brand .title {
    font-size: 2.5rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .progress-indicator {
    flex-direction: column;
    gap: 1rem;

    .progress-line {
      width: 2px;
      height: 2rem;
    }
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .config-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch !important;

    .generate-btn {
      justify-content: center;
    }
  }

  .outline-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .outline-actions {
    flex-direction: column;

    .primary-btn,
    .secondary-btn {
      justify-content: center;
    }
  }
}

@media (max-width: 480px) {
  .brand .title {
    font-size: 2rem;
  }

  .brand .subtitle {
    font-size: 1rem;
  }

  .setup-section,
  .outline-section {
    padding: 1rem;
  }
}

/* Processing Modal Styles */
.processing-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.processing-modal {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 300px;
  width: 90%;
  text-align: center;
}

.processing-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.processing-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

.processing-text {
  color: #475569;
  font-size: 1rem;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}