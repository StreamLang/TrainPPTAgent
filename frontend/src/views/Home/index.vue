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
            输入您的PPT主题，AI将为您生成专业大纲
          </div>
        </div>
      </div>

      <!-- Setup Step -->
      <div class="setup-section">
        <div class="input-section">
          <div class="input-wrapper">
            <input
              ref="inputRef"
              v-model="keyword"
              :maxlength="50"
              class="main-input"
              placeholder="请输入PPT主题，如：大学生职业生涯规划"
              @keyup.enter="createOutline"
            />
            <div class="input-actions">
              <span class="character-count">{{ keyword.length }}/50</span>
              <button class="generate-btn" @click="createOutline" :disabled="!keyword.trim() || loading">
                <span class="btn-icon">✨</span>
                {{ loading ? '生成中...' : 'AI 生成' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Quick Access -->
        <div class="quick-access-section">
          <h3 class="section-title">⚡ 快速访问</h3>
          <div class="quick-access-grid">
            <button class="quick-access-item" @click="goToMarkdownEditor">
              <span class="access-icon">📝</span>
              <span class="access-label">Markdown 编辑器</span>
            </button>
            <button class="quick-access-item" @click="goToEditor">
              <span class="access-icon">✏️</span>
              <span class="access-label">空白演示文稿</span>
            </button>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations-section">
          <h3 class="section-title">💡 推荐主题</h3>
          <div class="recommendations-grid">
            <button
              v-for="(item, index) in recommends"
              :key="index"
              class="recommend-item"
              @click="setKeyword(item)"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <!-- Configuration -->
        <div class="config-section">
          <h3 class="section-title">⚙️ 高级配置</h3>
          <div class="config-grid">
            <div class="config-item">
              <label class="config-label">语言</label>
              <select v-model="language" class="config-select">
                <option value="中文">中文</option>
                <option value="English">English</option>
                <option value="日本語">日本語</option>
              </select>
            </div>
            <div class="config-item">
              <label class="config-label">AI模型</label>
              <div class="config-select-static">qwen3-235b (本地部署)</div>
              <input type="hidden" v-model="model" />
            </div>
          </div>
        </div>
      </div>

      <!-- History Section -->
      <div v-if="historySessions.length > 0" class="history-section">
        <h3 class="section-title">📚 历史记录</h3>
        <div class="history-grid">
          <div 
            v-for="session in historySessions" 
            :key="session.sessionId" 
            class="history-item"
            @click="continueSession(session)"
          >
            <div class="history-content">
              <div class="history-title">
                {{ getSessionTitle(session.data.outline) || '未命名PPT' }}
              </div>
              <div class="history-meta">
                <span class="history-time">{{ formatTime(session.data.updatedAt || session.sessionId) }}</span>
                <span class="history-language">{{ session.data.language }}</span>
                <span class="history-progress" :class="`progress-${SessionManager.getSessionProgress(session.sessionId)}`">
                  {{ getProgressLabel(SessionManager.getSessionProgress(session.sessionId)) }}
                </span>
              </div>
            </div>
            <div class="history-action">
              <span class="continue-btn">{{ getContinueButtonText(SessionManager.getSessionProgress(session.sessionId)) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Processing Modal -->
    <div v-if="loading" class="processing-modal-overlay">
      <div class="processing-modal">
        <div class="processing-content">
          <div class="processing-spinner"></div>
          <div class="processing-text">正在生成大纲，请稍候...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services'
import useAIPPT from '@/hooks/useAIPPT'
import message from '@/utils/message'
import SessionManager from '@/utils/sessionManager'

const router = useRouter()
const { getMdContent } = useAIPPT()

const language = ref('中文')
const keyword = ref('')
const loading = ref(false)
const model = ref('qwen3-235b')
const inputRef = ref<HTMLInputElement>()

const recommends = ref([
  '2025科技前沿动态',
  '大数据如何改变世界',
  '餐饮市场调查与研究',
  'AIGC在教育领域的应用',
  '社交媒体与品牌营销',
  '5G技术如何改变我们的生活',
  '年度工作总结与展望',
  '区块链技术及其应用',
  '大学生职业生涯规划',
  '公司年会策划方案',
])

const historySessions = ref<Array<{sessionId: string, data: any}>>([])

onMounted(() => {
  setTimeout(() => {
    inputRef.value?.focus()
  }, 500)
  loadHistorySessions()
})

const setKeyword = (value: string) => {
  keyword.value = value
  inputRef.value?.focus()
}

const createOutline = async () => {
  if (!keyword.value.trim()) {
    message.error('请先输入PPT主题')
    return
  }

  loading.value = true

  try {
    const stream = await api.AIPPT_Outline({
      content: keyword.value,
      language: language.value,
      model: model.value,
    })

    let outline = ''
    const reader: ReadableStreamDefaultReader = stream.body.getReader()
    const decoder = new TextDecoder('utf-8')

    const readStream = () => {
      return new Promise((resolve, reject) => {
        const readNext = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              outline = getMdContent(outline)
              outline = outline.replace(/<!--[\s\S]*?-->/g, '').replace(/<think[\s\S]*?<\/think>/g, '')
              
              // 存储大纲数据并跳转到大纲页面
              const sessionId = SessionManager.storeOutlineData({
                outline: outline,
                language: language.value,
                model: model.value
              })
              
              router.push({
                name: 'Outline',
                query: { session_id: sessionId }
              })
              
              resolve()
              return
            }

            const chunk = decoder.decode(value, { stream: true })
            
            // 检查是否为错误消息
            if (chunk.includes('"status":"error"') && chunk.includes('"code":"')) {
              try {
                const errorData = JSON.parse(chunk)
                if (errorData.status === 'error' && errorData.message) {
                  reject(new Error(errorData.message || '生成失败'))
                  return
                }
              } catch (e) {
                outline += chunk
              }
            } else {
              outline += chunk
            }

            readNext()
          }).catch(error => {
            reject(error)
          })
        }
        
        readNext()
      })
    }

    await readStream()
  } catch (error) {
    console.error(error)
    message.error(error.message || '生成失败，请重试')
  } finally {
    loading.value = false
  }
}

// 添加跳转到 Markdown 编辑器的方法
const goToMarkdownEditor = () => {
  router.push('/markdown')
}

// 添加跳转到空白编辑器的方法
const goToEditor = () => {
  // 创建一个新的空会话
  const sessionId = SessionManager.storeOutlineData({
    outline: '',
    language: '中文',
    model: 'qwen3-235b'
  })
  
  // 直接跳转到编辑器页面
  router.push({
    name: 'Editor',
    query: { session_id: sessionId }
  })
}

const loadHistorySessions = () => {
  historySessions.value = SessionManager.getAllSessions()
}

const continueSession = (session: {sessionId: string, data: any}) => {
  const progress = SessionManager.getSessionProgress(session.sessionId)
  
  // 根据进度跳转到不同的页面
  const routeConfig: Record<string, {name: string, query: any}> = {
    'outline': { name: 'Outline', query: { session_id: session.sessionId } },
    'ppt': { name: 'PPT', query: { session_id: session.sessionId } },
    'editor': { name: 'Editor', query: { session_id: session.sessionId } }
  }
  
  const targetRoute = routeConfig[progress] || routeConfig.outline
  router.push(targetRoute)
}

const getSessionTitle = (outline: string): string => {
  // 从大纲内容中提取第一行作为标题
  const firstLine = outline.split('\n')[0]?.trim()
  if (firstLine && firstLine.length > 0 && firstLine.length < 50) {
    return firstLine
  }
  return '未命名PPT'
}

const formatTime = (timestamp: string | number): string => {
  const date = new Date(typeof timestamp === 'string' ? parseInt(timestamp) : timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getProgressLabel = (progress: string): string => {
  const progressLabels: Record<string, string> = {
    'outline': '大纲编辑',
    'ppt': '模板选择',
    'editor': '最终编辑'
  }
  return progressLabels[progress] || '大纲编辑'
}

const getContinueButtonText = (progress: string): string => {
  const buttonTexts: Record<string, string> = {
    'outline': '继续编辑',
    'ppt': '选择模板',
    'editor': '最终编辑'
  }
  return buttonTexts[progress] || '继续编辑'
}
</script>

<style lang="scss" scoped>
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

/* Quick Access Section */
.quick-access-section {
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

  .quick-access-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .quick-access-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1.5rem 1rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: #667eea;
      color: white;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .access-icon {
      font-size: 1.5rem;
    }

    .access-label {
      font-weight: 500;
      font-size: 0.95rem;
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

/* History Section */
.history-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;

  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .history-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: #ffffff;
      border-color: #667eea;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
  }

  .history-content {
    flex: 1;
  }

  .history-title {
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.25rem;
    font-size: 0.95rem;
  }

  .history-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: #64748b;
  }

  .history-time {
    font-size: 0.8rem;
  }

  .history-language {
    background: #e2e8f0;
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.7rem;
  }

  .history-progress {
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.7rem;
    font-weight: 500;
  }

  .progress-outline {
    background: #dbeafe;
    color: #1e40af;
  }

  .progress-ppt {
    background: #fef3c7;
    color: #92400e;
  }

  .progress-editor {
    background: #dcfce7;
    color: #166534;
  }

  .history-action {
    .continue-btn {
      background: #667eea;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    .history-item:hover .continue-btn {
      background: #5a67d8;
    }
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

.processing-text {
  color: #475569;
  font-size: 1rem;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .aippt-dialog {
    padding: 1rem;
  }

  .setup-section {
    padding: 1.5rem;
  }

  .brand .title {
    font-size: 2.5rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .recommendations-grid,
  .quick-access-grid {
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
}

@media (max-width: 480px) {
  .brand .title {
    font-size: 2rem;
  }

  .brand .subtitle {
    font-size: 1rem;
  }

  .setup-section {
    padding: 1rem;
  }
}
</style>