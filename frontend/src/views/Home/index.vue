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

onMounted(() => {
  setTimeout(() => {
    inputRef.value?.focus()
  }, 500)
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