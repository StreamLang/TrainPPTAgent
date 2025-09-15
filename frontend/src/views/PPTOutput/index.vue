<template>
  <div class="ppt-output-container">
    <div class="header">
      <h1>PPT 生成结果</h1>
      <div class="header-actions">
        <button @click="goBack" class="back-button">返回编辑</button>
        <button @click="exportPPT" class="export-button" v-if="initialized">导出PPT</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在加载PPT数据...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="goBack" class="retry-button">重新编辑</button>
    </div>
    
    <div v-else class="ppt-container">
      <!-- PPTist 编辑器容器 -->
      <div v-if="initialized" class="pptist-editor-wrapper">
        <EditorHeader class="layout-header" />
        <div class="layout-content">
          <Thumbnails class="layout-content-left" />
          <div class="layout-content-center">
            <CanvasTool class="center-top" />
            <Canvas class="center-body" :style="{ height: `calc(100% - ${remarkHeight + 40}px)` }" />
            <Remark
              class="center-bottom" 
              v-model:height="remarkHeight" 
              :style="{ height: `${remarkHeight}px` }"
            />
          </div>
          <Toolbar class="layout-content-right" />
        </div>
      </div>
      <div v-else class="initializing">
        <div class="spinner"></div>
        <p>正在初始化编辑器...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useMainStore, useSlidesStore } from '@/store'
import api from '@/services'

// 导入 PPTist 组件
import EditorHeader from '@/views/Editor/EditorHeader/index.vue'
import Canvas from '@/views/Editor/Canvas/index.vue'
import CanvasTool from '@/views/Editor/CanvasTool/index.vue'
import Thumbnails from '@/views/Editor/Thumbnails/index.vue'
import Toolbar from '@/views/Editor/Toolbar/index.vue'
import Remark from '@/views/Editor/Remark/index.vue'

export default {
  name: 'PPTOutput',
  components: {
    EditorHeader,
    Canvas,
    CanvasTool,
    Thumbnails,
    Toolbar,
    Remark
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const mainStore = useMainStore()
    const slidesStore = useSlidesStore()
    const { dialogForExport } = storeToRefs(mainStore)
    
    const loading = ref(true)
    const error = ref(null)
    const initialized = ref(false)
    const remarkHeight = ref(40)
    const selectedTemplate = ref('template_1') // 默认模板
    
    const goBack = () => {
      router.push('/markdown')
    }
    
    const exportPPT = () => {
      // 触发导出对话框
      mainStore.setDialogForExport('pptx')
    }
    
    // 应用模板主题
    const applyTemplateTheme = async (templateId) => {
      try {
        const templateData = await api.getFileData(templateId)
        if (templateData && templateData.theme) {
          slidesStore.setTheme(templateData.theme)
        }
      } catch (err) {
        console.error('应用模板主题失败:', err)
      }
    }
    
    const loadPPTData = async () => {
      try {
        const sessionId = route.query.session_id
        if (!sessionId) {
          throw new Error('缺少session_id参数')
        }
        
        const data = localStorage.getItem(`pptResult_${sessionId}`)
        if (!data) {
          throw new Error('未找到PPT数据')
        }
        
        const pptResult = JSON.parse(data)
        console.log('PPT结果数据:', pptResult)
        
        // 获取模板信息
        const templateId = pptResult.template || 'template_1'
        selectedTemplate.value = templateId
        
        // 处理后端返回的数据格式
        let slidesData = []
        let themeData = null
        let titleData = '未命名演示文稿'
        
        // 根据实际返回的数据结构进行处理
        if (Array.isArray(pptResult)) {
          // 如果是数组格式，假定是幻灯片数据
          slidesData = pptResult
        } else if (pptResult.chunks) {
          // 如果有chunks字段，使用该字段作为幻灯片数据
          slidesData = pptResult.chunks
          // 从第一个chunk中提取主题信息（如果有的话）
          if (slidesData.length > 0 && slidesData[0].theme) {
            themeData = slidesData[0].theme
          }
        } else if (pptResult.slides) {
          // 如果有slides字段，使用该字段
          slidesData = pptResult.slides
          themeData = pptResult.theme
          titleData = pptResult.title || titleData
        } else {
          // 其他情况，假定整个对象就是幻灯片数据
          slidesData = [pptResult]
        }
        
        // 初始化 PPTist store
        if (slidesData && Array.isArray(slidesData) && slidesData.length > 0) {
          // 确保每个幻灯片都有ID
          const slidesWithId = slidesData.map(slide => {
            if (!slide.id) {
              // 生成唯一ID
              slide.id = 'slide_' + Math.random().toString(36).substr(2, 9)
            }
            return slide
          })
          
          slidesStore.setSlides(slidesWithId)
        } else {
          // 如果没有幻灯片数据，创建一个空的幻灯片
          slidesStore.resetSlides()
        }
        
        // 应用模板主题
        if (themeData) {
          slidesStore.setTheme(themeData)
        } else {
          // 如果没有主题数据，则根据模板ID应用主题
          await applyTemplateTheme(templateId)
        }
        
        slidesStore.setTitle(titleData)
        
      } catch (err) {
        error.value = err.message || '加载PPT数据失败'
        console.error('加载PPT数据失败:', err)
      } finally {
        loading.value = false
      }
    }
    
    // 监听导出对话框状态变化
    watch(dialogForExport, (newVal) => {
      if (!newVal) {
        // 导出对话框关闭时重置状态
        mainStore.setDialogForExport('')
      }
    })
    
    onMounted(() => {
      loadPPTData()
      nextTick(() => {
        if (!error.value) {
          // 延迟设置初始化状态，确保组件正确挂载
          setTimeout(() => {
            initialized.value = true
          }, 100)
        }
      })
    })
    
    return {
      loading,
      error,
      initialized,
      remarkHeight,
      goBack,
      exportPPT
    }
  }
}
</script>

<style scoped>
.ppt-output-container {
  padding: 20px;
  max-width: 100%;
  height: 100vh;
  margin: 0 auto;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h1 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.back-button,
.export-button,
.retry-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.back-button {
  background-color: #f0f0f0;
  color: #333;
}

.back-button:hover {
  background-color: #e0e0e0;
}

.export-button {
  background-color: #1890ff;
  color: white;
}

.export-button:hover {
  background-color: #40a9ff;
}

.retry-button {
  background-color: #ff4d4f;
  color: white;
}

.retry-button:hover {
  background-color: #ff7875;
}

.loading,
.error,
.initializing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 70vh;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error p {
  color: #ff4d4f;
  font-size: 16px;
  margin-bottom: 20px;
}

.ppt-container {
  height: calc(100vh - 120px);
}

.pptist-editor-wrapper {
  height: 100%;
}

.layout-header {
  height: 40px;
}

.layout-content {
  height: calc(100% - 40px);
  display: flex;
}

.layout-content-left {
  width: 160px;
  height: 100%;
  flex-shrink: 0;
}

.layout-content-center {
  width: calc(100% - 160px - 260px);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.center-top {
  height: 40px;
}

.center-body {
  flex: 1;
}

.center-bottom {
  height: 40px;
}

.layout-content-right {
  width: 260px;
  height: 100%;
}

@media (max-width: 768px) {
  .layout-content {
    flex-direction: column;
  }
  
  .layout-content-left,
  .layout-content-right {
    width: 100%;
    height: auto;
  }
  
  .layout-content-center {
    width: 100%;
    height: auto;
  }
}
</style>