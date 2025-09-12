<template>
  <div class="aippt-page">
    <!-- 全局背景：渐变 + 网格 -->
    <div class="page-bg" aria-hidden="true">
      <div class="bg-blob b1"></div>
      <div class="bg-blob b2"></div>
      <div class="grid"></div>
    </div>

    <div class="aippt-dialog">
      <!-- 头部：标题/说明 居中、层级清晰 -->
      <header class="header" role="banner">
        <div class="header-content">
          <h1 class="title">PPTAgent</h1>
          <p class="subtitle">专业PPT制作工具</p>
          <div class="header-decoration" aria-hidden="true">
            <div class="decoration-dot"></div>
            <div class="decoration-dot"></div>
            <div class="decoration-dot"></div>
          </div>
        </div>
        

      </header>

      <!-- 内容填充区域 -->
      <ContentEditor 
        :outline="outline" 
        :materials="[]"
        @content-change="handleContentChange"
        ref="contentEditor"
      />

      <section class="select-template" aria-label="模板选择">
        <div class="templates-container">
          <div class="templates">
            <div
              class="template-card"
              :class="{ selected: selectedTemplate === template.id }"
              v-for="template in templates"
              :key="template.id"
              @click="!loading && (selectedTemplate = template.id)"
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

        <div class="actions">
          <!-- 进度提示 -->
          <div class="progress-indicator" v-if="loading">
            <div class="progress-spinner"></div>
            <span class="progress-text">正在生成PPT内容，这可能需要几分钟时间...</span>
          </div>
          
          <Button class="btn btn-primary" type="primary" :disabled="loading || !selectedTemplate" @click="createPPT()">
            <span>{{ loading ? '正在生成…' : '生成PPT' }}</span>
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12,6 12,12 16,14"></polyline>
            </svg>
          </Button>
          <Button class="btn btn-secondary" :disabled="loading" @click="$router.back()">
            <span>返回大纲</span>
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15,18 9,12 15,6"></polyline>
            </svg>
          </Button>
        </div>
      </section>
    </div>

    
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import api from '@/services'
import useAIPPT from '@/hooks/useAIPPT'
import type { AIPPTSlide } from '@/types/AIPPT'
import type { Slide, SlideTheme } from '@/types/slides'
import { useMainStore, useSlidesStore } from '@/store'
import Button from '@/components/Button.vue'
import ContentEditor from '@/components/ContentEditor.vue'
import SessionManager from '@/utils/sessionManager'

const route = useRoute()
const router = useRouter()
const mainStore = useMainStore()
const slideStore = useSlidesStore()
const { templates } = storeToRefs(slideStore)
const { sessionId } = storeToRefs(mainStore)
const { AIPPTGenerator } = useAIPPT()

const contentEditor = ref<InstanceType<typeof ContentEditor> | null>(null)

// 从SessionManager中读取outline数据（包含图片）
const sessionIdFromQuery = route.query.session_id as string
let outlineData = { outline: '', language: '中文', model: 'qwen3-235b', images: [] }

if (sessionIdFromQuery) {
  const storedData = SessionManager.getOutlineData(sessionIdFromQuery)
  if (storedData) {
    outlineData = storedData
    // 可选：清除已使用的sessionStorage数据
    // SessionManager.clearSessionData(sessionIdFromQuery, 'outline')
  }
}

const outline = ref(outlineData.outline)
const language = ref(outlineData.language)
const model = ref(outlineData.model)
const userImages = ref(outlineData.images || []) // 用户粘贴的图片数据
const style = ref('通用')
const selectedTemplate = ref<string>(templates.value?.[0]?.id || 'template_1')
const loading = ref(false)

// 素材列表（已移除素材管理功能，改为剪贴板图片粘贴）
const materials = ref([])

// 处理内容变化
const handleContentChange = (sections: any[]) => {
  // 这里可以处理内容变化的逻辑
  console.log('内容已更新:', sections)
}

const createPPT = async () => {
  if (!selectedTemplate.value) return
  mainStore.setGenerating(true)
  loading.value = true
  
  // 添加进度提示
  const progressToast = {
    show: true,
    message: '正在生成PPT内容，这可能需要几分钟时间...',
    type: 'info'
  }
  // 这里可以调用一个toast或通知组件来显示进度
  
  slideStore.resetSlides()

  try {
    // 获取用户填充的内容
    const sections = contentEditor.value ? contentEditor.value.getSections() : []
    
    // 构建包含用户内容的完整大纲
    let enrichedOutline = outline.value
    
    // 整合用户填充的内容到大纲中
    if (contentEditor.value) {
      const userSections = contentEditor.value.getSections()
      userSections.forEach(section => {
        // 将用户填写的内容整合到大纲中
        section.fields.forEach(field => {
          if (field.content.trim()) {
            // 在相应章节中添加用户填写的内容
            const sectionPattern = new RegExp(`## ${section.title}[\\s\\S]*?(?=##|$)`, 'i')
            const match = enrichedOutline.match(sectionPattern)
            if (match) {
              // 在章节内容中添加用户填写的内容
              enrichedOutline = enrichedOutline.replace(
                sectionPattern,
                match[0] + `\n\n${field.content.trim()}\n`
              )
            }
          }
        })
      })
    }
    
    console.log('开始调用AIPPT API，内容长度:', enrichedOutline.length)
    const startTime = Date.now()
    
    // 设置API调用超时
    const apiTimeout = setTimeout(() => {
      console.warn('API调用超时，可能需要检查后端服务状态')
    }, 10000) // 10秒超时
    
    const stream = await api.AIPPT({
      content: enrichedOutline,
      language: language.value,
      style: style.value,
      model: model.value,
    }).catch(err => {
      clearTimeout(apiTimeout)
      console.error('API调用失败:', err)
      loading.value = false
      mainStore.setGenerating(false)
      throw new Error('PPT生成服务暂时不可用，请稍后重试')
    })
    
    clearTimeout(apiTimeout)
    console.log('API连接建立耗时:', Date.now() - startTime, 'ms')
    
    // 设置流读取超时
    const streamTimeout = setTimeout(() => {
      console.error('流读取超时，可能后端处理时间过长')
      loading.value = false
      mainStore.setGenerating(false)
      // 可以在这里给用户提示
    }, 300000) // 5分钟超时

    // 初始化图片池，使用mock数据作为备用（已禁用图片功能）
    // const mockImgs = await api.getMockData('imgs')
    // presetImgPool(mockImgs)

    const templateData = await api.getFileData(selectedTemplate.value)
    const templateSlides: Slide[] = templateData.slides
    const templateTheme: SlideTheme = templateData.theme
    slideStore.setTheme(templateTheme)

    const reader: ReadableStreamDefaultReader = stream.body.getReader()
    const decoder = new TextDecoder('utf-8')

    let slideCount = 0
    let totalProcessingTime = 0
    
    const readStream = () => {
      reader.read().then(({ done, value }) => {
        if (done) {
          clearTimeout(streamTimeout)
          const endTime = Date.now()
          console.log(`PPT生成完成，总共生成 ${slideCount} 张幻灯片，总耗时: ${endTime - startTime}ms`)
          loading.value = false
          mainStore.setAIPPTDialogState(false)
          mainStore.setGenerating(false)
          
          // 保存PPT数据到sessionStorage
          const pptData = {
            slides: slideStore.slides,
            theme: slideStore.theme
          }
          SessionManager.storePPTData(pptData, sessionIdFromQuery)
          
          // 在PPT生成完成后再跳转到编辑器页面，使用正确的session_id
          router.push(`/editor?session_id=${sessionIdFromQuery}`)
          return
        }

        const chunk = decoder.decode(value, { stream: true })
        const processStartTime = Date.now()
        
        try {
          console.log('收到数据块，长度:', chunk.length)
          
          // 检查是否为错误消息
          if (chunk.includes('"status":"error"') || chunk.includes('"error":')) {
            try {
              const errorData = JSON.parse(chunk)
              throw new Error(errorData.message || errorData.error || 'PPT生成失败')
            } catch {
              throw new Error('生成过程中出现错误')
            }
          }
          
          const text = chunk.replace(/```json|```/g, '').trim()
          if (text) {
            const slide: AIPPTSlide = JSON.parse(text)
            slideCount++
            
            // 处理从后端返回的图片数据
            if (slide.images && slide.images.length > 0) {
              console.log(`幻灯片 ${slideCount} 包含 ${slide.images.length} 张图片`)
              // 将后端返回的图片添加到图片池
              const backendImages = slide.images.map((img: any) => ({
                id: img.id || Math.random().toString(),
                src: img.src,
                width: img.width || 1920,
                height: img.height || 1080
              }))
              presetImgPool(backendImages)
            }
            
            // 将用户粘贴的图片转换为ImgPoolItem格式
            const userImgPoolItems = userImages.value.map(img => ({
              id: Math.random().toString(),
              src: img.data,
              width: 800, // 默认宽度
              height: 600  // 默认高度
            }))
            
            const slideGenerator = AIPPTGenerator(templateSlides, [slide], userImgPoolItems)
            for (const generatedSlide of slideGenerator) {
              slideStore.addSlide(generatedSlide)
            }
            
            // 更新进度提示
            console.log(`成功处理第 ${slideCount} 张幻灯片`)
          }
        } catch (err) {
          console.error('处理数据块时出错:', err)
          console.error('原始数据块内容:', chunk)
          // 如果是严重错误，停止流式读取
          if (err instanceof Error && err.message.includes('生成失败')) {
            throw err // 向上抛出错误，让外层catch处理
          }
        }
        
        const processTime = Date.now() - processStartTime
        totalProcessingTime += processTime
        console.log(`处理耗时: ${processTime}ms，累计处理时间: ${totalProcessingTime}ms`)
        
        readStream()
      }).catch(err => {
        console.error('读取流时发生错误:', err)
        loading.value = false
        mainStore.setGenerating(false)
      })
    }
    readStream()
  } catch (e) {
    loading.value = false
    mainStore.setGenerating(false)
    // eslint-disable-next-line no-console
    console.error(e)
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

/* 头部区块：居中布局 */
.header {
  position: relative;
  text-align: center;
  margin-bottom: 28px;
  .title {
    font-weight: 900;
    font-size: 36px;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.5px;
    line-height: 1.15;
  }
  .subtitle {
    color: #475569;
    font-size: 16px;
    margin: 0 auto;
    font-weight: 500;
    line-height: 1.6;
    max-width: 680px;
  }
  .header-decoration {
    margin: 14px auto 0;
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    .decoration-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      opacity: 0.7; animation: pulse 2s ease-in-out infinite;
      &:nth-child(2) { animation-delay: 0.25s; }
      &:nth-child(3) { animation-delay: 0.5s; }
    }
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.2); opacity: 1; }
}

/* 模板区域 */
.select-template {
  .templates-container {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: saturate(120%) blur(2px);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
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

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 26px -4px rgba(0, 0, 0, 0.12);
      border-color: #cbd5e1;
    }

    &.selected {
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15), 0 12px 28px -6px rgba(59, 130, 246, 0.25);
      .overlay { opacity: 1; visibility: visible; }
      .template-info { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: #fff; }
    }

    .template-image {
      position: relative; aspect-ratio: 16/9; overflow: hidden;
      img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease; }
      .overlay {
        position: absolute; inset: 0; background: rgba(59, 130, 246, 0.18);
        display: flex; align-items: center; justify-content: center;
        opacity: 0; visibility: hidden; transition: all 0.25s ease;
        .check-icon {
          width: 32px; height: 32px; color: #fff; background: #3b82f6; border-radius: 50%;
          display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
          svg { width: 16px; height: 16px; }
        }
      }
    }

    .template-info {
      padding: 12px 14px; background: #f8fafc; transition: all 0.25s ease;
      .template-name { font-size: 14px; font-weight: 700; color: inherit; }
    }

    &:hover .template-image img { transform: scale(1.045); }
  }

  .actions {
    display: flex; justify-content: center; gap: 14px; align-items: center; margin-top: 18px;
    .btn {
      min-width: 148px; height: 48px; display: flex; align-items: center; justify-content: center; gap: 8px;
      font-weight: 700; font-size: 14px; border-radius: 12px; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative; overflow: hidden;
      &:disabled { opacity: 0.6; cursor: not-allowed; filter: grayscale(10%); }
      .btn-icon { width: 18px; height: 18px; transition: transform 0.25s ease; }
      &.btn-primary {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border: none; color: #fff;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.38);
        &:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 10px 24px rgba(59, 130, 246, 0.5); .btn-icon { transform: rotate(90deg); } }
        &:active:not(:disabled) { transform: translateY(0); }
      }
      &.btn-secondary {
        background: #fff; border: 2px solid #e2e8f0; color: #64748b;
        &:hover:not(:disabled) {
          border-color: #cbd5e1; background: #f8fafc; color: #475569; transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08); .btn-icon { transform: translateX(-2px); }
        }
        &:active:not(:disabled) { transform: translateY(0); }
      }
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .aippt-dialog { padding: 24px 16px; }
  .header { .title { font-size: 28px; } .subtitle { font-size: 14px; } }
  .select-template {
    .templates-container { padding: 16px; }
    .templates { grid-template-columns: 1fr; gap: 14px; }
    .actions { flex-direction: column; gap: 12px; .btn { width: 100%; max-width: 320px; } }
  }
}
@media (max-width: 480px) {
  .header .title { font-size: 24px; }
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 开发者工具样式 */
.developer-tools {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.dev-link {
  display: inline-block;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.dev-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>