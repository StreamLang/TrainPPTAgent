<template>
  <div class="pptist-editor">
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

  <SelectPanel v-if="showSelectPanel" />
  <SearchPanel v-if="showSearchPanel" />
  <NotesPanel v-if="showNotesPanel" />
  <MarkupPanel v-if="showMarkupPanel" />
  <SymbolPanel v-if="showSymbolPanel" />

  <Modal
    :visible="!!dialogForExport" 
    :width="680"
    @closed="closeExportDialog()"
  >
    <ExportDialog />
  </Modal>
  <div v-if="isGenerating" class="bottom-loading">
    <span>AI 生成中，请耐心等待…</span>
  </div>
  
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useMainStore, useSlidesStore } from '@/store'
import useGlobalHotkey from '@/hooks/useGlobalHotkey'
import usePasteEvent from '@/hooks/usePasteEvent'
import SessionManager from '@/utils/sessionManager'

import EditorHeader from './EditorHeader/index.vue'
import Canvas from './Canvas/index.vue'
import CanvasTool from './CanvasTool/index.vue'
import Thumbnails from './Thumbnails/index.vue'
import Toolbar from './Toolbar/index.vue'
import Remark from './Remark/index.vue'
import ExportDialog from './ExportDialog/index.vue'
import SelectPanel from './SelectPanel.vue'
import SearchPanel from './SearchPanel.vue'
import NotesPanel from './NotesPanel.vue'
import SymbolPanel from './SymbolPanel.vue'
import MarkupPanel from './MarkupPanel.vue'
import Modal from '@/components/Modal.vue'


const mainStore = useMainStore()
const slidesStore = useSlidesStore()
const route = useRoute()
const { dialogForExport, showSelectPanel, showSearchPanel, showNotesPanel, showSymbolPanel, showMarkupPanel, isGenerating } = storeToRefs(mainStore)

const closeExportDialog = () => mainStore.setDialogForExport('')

const remarkHeight = ref(40)

// 恢复session数据
const restoreSessionData = () => {
  const sessionId = route.query.session_id as string
  if (sessionId) {
    const pptData = SessionManager.getPPTData(sessionId)
    if (pptData) {
      // 恢复幻灯片数据
      slidesStore.setSlides(pptData.slides)
      if (pptData.theme) {
        slidesStore.setTheme(pptData.theme)
      }
      console.log('Session数据恢复成功，幻灯片数量:', pptData.slides.length)
    } else {
      console.warn('未找到对应的session数据，session_id:', sessionId)
    }
  }
}

onMounted(() => {
  restoreSessionData()
  setupAutoSave()
})

useGlobalHotkey()
usePasteEvent()

// 设置自动保存
const setupAutoSave = () => {
  const sessionId = route.query.session_id as string
  if (!sessionId) return
  
  // 监听幻灯片数据变化
  watch(() => slidesStore.slides, () => {
    saveSessionData(sessionId)
  }, { deep: true, immediate: true })
  
  // 监听主题变化
  watch(() => slidesStore.theme, () => {
    saveSessionData(sessionId)
  }, { deep: true, immediate: true })
  
  // 页面卸载前保存
  window.addEventListener('beforeunload', () => {
    saveSessionData(sessionId)
  })
}

// 保存session数据
const saveSessionData = (sessionId: string) => {
  const editorData = {
    slides: slidesStore.slides,
    theme: slidesStore.theme
  }
  // 在Editor页面保存数据时，强制设置进度为'editor'
  SessionManager.storeEditorData(editorData, sessionId, 'editor')
  console.log('Editor数据已保存，进度: editor')
}
</script>

<style lang="scss" scoped>
.pptist-editor {
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

  .center-top {
    height: 40px;
  }
}
.layout-content-right {
  width: 260px;
  height: 100%;
}

.bottom-loading {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 20px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 8px;
  z-index: 1000;
}
</style>