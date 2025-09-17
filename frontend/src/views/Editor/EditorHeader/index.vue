<template>
  <div class="editor-header">
    <div class="left">
      <Popover trigger="click" placement="bottom-start" v-model:value="mainMenuVisible">
        <template #content>
          <div class="main-menu">
            <div class="ai-menu" @click="router.push('/'); mainMenuVisible = false">
              <div class="icon"><IconClick theme="two-tone" :fill="['#ffc158', '#fff']" /></div>
              <div class="aippt-content">
                <div class="aippt"><span>PPTAgent</span></div>
                <div class="aippt-subtitle">输入一句话，智能生成演示文稿</div>
              </div>
            </div>
          </div>
          <Divider :margin="10" />
          <div class="import-section">
            <div class="import-label">导入文件</div>
            <div class="import-grid">
              <FileInput class="import-block" accept="application/vnd.openxmlformats-officedocument.presentationml.presentation" @change="files => {
                importPPTXFile(files)
                mainMenuVisible = false
              }">
                <span class="icon"><IconFilePdf theme="multi-color" :fill="['#333', '#d14424', '#fff']" /></span>
                <span class="label">PPTX</span>
                <span class="sub-label">（测试）</span>
              </FileInput>
              <FileInput class="import-block" accept=".json" @change="files => {
                importJSON(files)
                mainMenuVisible = false
              }">
                <span class="icon"><IconFileJpg theme="multi-color" :fill="['#333', '#d14424', '#fff']" /></span>
                <span class="label">JSON</span>
                <span class="sub-label">（测试）</span>
              </FileInput>
              <FileInput class="import-block" accept=".pptist" @change="files => {
                importSpecificFile(files)
                mainMenuVisible = false
              }">
                <span class="icon"><IconNotes theme="multi-color" :fill="['#333', '#d14424', '#fff']" /></span>
                <span class="label">PPTIST</span>
                <span class="sub-label">（专属格式）</span>
              </FileInput>
            </div>
          </div>
          <Divider :margin="10" />
          <PopoverMenuItem class="popover-menu-item" @click="setDialogForExport('pptx')"><IconDownload class="icon" /> 导出文件</PopoverMenuItem>
          <Divider :margin="10" />
          <PopoverMenuItem class="popover-menu-item" @click="resetSlides(); mainMenuVisible = false"><IconRefresh class="icon" /> 重置幻灯片</PopoverMenuItem>
          <PopoverMenuItem class="popover-menu-item" @click="openMarkupPanel(); mainMenuVisible = false"><IconMark class="icon" /> 幻灯片类型标注</PopoverMenuItem>
          <PopoverMenuItem class="popover-menu-item" @click="mainMenuVisible = false; hotkeyDrawerVisible = true"><IconCommand class="icon" /> 快捷操作</PopoverMenuItem>
        </template>
        <div class="menu-item"><IconHamburgerButton class="icon" /></div>
      </Popover>

      <div class="title">
        <Input 
          class="title-input" 
          ref="titleInputRef"
          v-model:value="titleValue" 
          @blur="handleUpdateTitle()" 
          v-if="editingTitle" 
        ></Input>
        <div 
          class="title-text"
          @click="startEditTitle()"
          :title="title"
          v-else
        >{{ title }}</div>
      </div>
    </div>

    <div class="right">
        <div class="menu-item" v-tooltip="'添加幻灯片'" @click="createSlide()">
          <IconAddText class="icon" /> 添加幻灯片
        </div>
        <div class="menu-item" v-tooltip="'插入base64图片'" @click="createImgElementBase64()">
          <IconPicture class="icon" /> 插入base64图片
        </div>
        <div class="menu-item" v-tooltip="'插入饼状图'" @click="">
          <IconChartProportion class="icon" /> 插入饼状图
        </div>
        <div class="menu-item" v-tooltip="'插入柱状图'" @click="">
          <IconHamburgerButton class="icon" /> 插入柱状图
        </div>
        <div class="menu-item" v-tooltip="'插入折线图'" @click="">
          <IconConnection class="icon" /> 插入折线图
        </div>
        <div class="menu-item" v-tooltip="'插入数据表格'" @click="importTableData()">
          <IconPicture class="icon" /> 插入表格数据
        </div>
      <div class="group-menu-item">
        <div class="menu-item" v-tooltip="'幻灯片放映（F5）'" @click="enterScreening()">
          <IconPpt class="icon" />
        </div>
        <Popover trigger="click" center>
          <template #content>
            <PopoverMenuItem class="popover-menu-item" @click="enterScreeningFromStart()"><IconSlideTwo class="icon" /> 从头开始</PopoverMenuItem>
            <PopoverMenuItem class="popover-menu-item" @click="enterScreening()"><IconPpt class="icon" /> 从当前页开始</PopoverMenuItem>
          </template>
          <div class="arrow-btn"><IconDown class="arrow" /></div>
        </Popover>
      </div>
      <div class="menu-item" v-tooltip="'导出'" @click="setDialogForExport('pptx')">
        <IconDownload class="icon" />
      </div>
    </div>

    <Drawer
      :width="320"
      v-model:visible="hotkeyDrawerVisible"
      placement="right"
    >
      <HotkeyDoc />
      <template v-slot:title>快捷操作</template>
    </Drawer>

    <FullscreenSpin :loading="exporting" tip="正在导入..." />
  </div>
</template>

<script lang="ts" setup>
import { nextTick, ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useMainStore, useSlidesStore } from '@/store'
import useScreening from '@/hooks/useScreening'
import useImport from '@/hooks/useImport'
import useSlideHandler from '@/hooks/useSlideHandler'
import useCreateTableFromData from '@/hooks/useCreateTableFromData'
import type { DialogForExportTypes } from '@/types/export'

import HotkeyDoc from './HotkeyDoc.vue'
import FileInput from '@/components/FileInput.vue'
import FullscreenSpin from '@/components/FullscreenSpin.vue'
import Drawer from '@/components/Drawer.vue'
import Input from '@/components/Input.vue'
import Popover from '@/components/Popover.vue'
import PopoverMenuItem from '@/components/PopoverMenuItem.vue'
import Divider from '@/components/Divider.vue'
import useCreateElement from '@/hooks/useCreateElement'

const router = useRouter()
const mainStore = useMainStore()
const slidesStore = useSlidesStore()
const { title } = storeToRefs(slidesStore)
const { enterScreening, enterScreeningFromStart } = useScreening()
const {
  createSlide,
} = useSlideHandler()
const { importSpecificFile, importPPTXFile, importJSON, exporting } = useImport()
const { resetSlides } = useSlideHandler()
const { parseCSVData, createTableFromData } = useCreateTableFromData()
const { createImageElementFromBase64,createChartElement } = useCreateElement()
const mainMenuVisible = ref(false)
const hotkeyDrawerVisible = ref(false)
const editingTitle = ref(false)
const titleValue = ref('')
const titleInputRef = useTemplateRef<InstanceType<typeof Input>>('titleInputRef')

const startEditTitle = () => {
  titleValue.value = title.value
  editingTitle.value = true
  nextTick(() => titleInputRef.value?.focus())
}

const handleUpdateTitle = () => {
  slidesStore.setTitle(titleValue.value)
  editingTitle.value = false
}

const goLink = (url: string) => {
  window.open(url)
  mainMenuVisible.value = false
}

const setDialogForExport = (type: DialogForExportTypes) => {
  mainStore.setDialogForExport(type)
  mainMenuVisible.value = false
}

const openMarkupPanel = () => {
  mainStore.setMarkupPanelState(true)
}
const createImgElementBase64 = () => {
  const base65Str = 'data:image/png;base64,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'
  createImageElementFromBase64(base65Str)
}
// 导入表格数据功能
const importTableData = () => {
  // 模拟CSV数据（可以替换为实际的接口数据）
  const csvData = `姓名,年龄,城市,职业
张三,25,北京,工程师
李四,30,上海,设计师
王五,28,广州,产品经理
赵六,35,深圳,项目经理
钱七,22,杭州,实习生`

  const parsedData = parseCSVData(csvData)
  createTableFromData(parsedData)
}
</script>

<style lang="scss" scoped>
.editor-header {
  background-color: #fff;
  user-select: none;
  border-bottom: 1px solid $borderColor;
  display: flex;
  justify-content: space-between;
  padding: 0 5px;
}
.left, .right {
  display: flex;
  justify-content: center;
  align-items: center;
}
.menu-item {
  height: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  padding: 0 10px;
  border-radius: $borderRadius;
  cursor: pointer;

  .icon {
    font-size: 18px;
    color: #666;
  }
  .text {
    width: 18px;
    text-align: center;
    font-size: 17px;
  }
  .ai {
    background: linear-gradient(270deg, #d897fd, #33bcfc);
    background-clip: text;
    color: transparent;
    font-weight: 700;
  }

  &:hover {
    background-color: #f1f1f1;
  }
}
.popover-menu-item {
  display: flex;
  padding: 8px 10px;

  .icon {
    font-size: 18px;
    margin-right: 12px;
  }
}
.main-menu {
  width: 300px;
}
.ai-menu {
  background: linear-gradient(270deg, #f8edff, #d4f1ff);
  color: $themeColor;
  border-radius: $borderRadius;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  cursor: pointer;

  .icon {
    font-size: 22px;
    margin-right: 16px;
  }
  .aippt-content {
    display: flex;
    flex-direction: column;
  }
  .aippt {
    font-weight: 700;
    font-size: 16px;

    span {
      background: linear-gradient(270deg, #d897fd, #33bcfc);
      background-clip: text;
      color: transparent;
    }
  }
  .aippt-subtitle {
    font-size: 12px;
    color: #777;
    margin-top: 5px;
  }
}

.import-section {
  padding: 5px 0;

  .import-label {
    font-size: 12px;
    color: #999;
    margin-bottom: 6px;
  }
  .import-grid {
    display: flex;
    gap: 8px;
    justify-content: space-between;
  }
  .import-block {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px 8px;
    border-radius: $borderRadius;
    border: 1px solid $borderColor;
    transition: background-color .2s;
    cursor: pointer;
  
    &:hover {
      background-color: #f1f1f1;
    }
    .icon {
      font-size: 24px;
      margin-bottom: 2px;
    }
    .label {
      font-size: 12px;
      text-align: center;
    }
    .sub-label {
      font-size: 10px;
      color: #999;
    }
  }
}

.group-menu-item {
  height: 30px;
  display: flex;
  margin: 0 8px;
  padding: 0 2px;
  border-radius: $borderRadius;

  &:hover {
    background-color: #f1f1f1;
  }

  .menu-item {
    padding: 0 3px;
  }
  .arrow-btn {
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }
}
.title {
  height: 30px;
  margin-left: 2px;
  font-size: 13px;

  .title-input {
    width: 200px;
    height: 100%;
    padding-left: 0;
    padding-right: 0;

    ::v-deep(input) {
      height: 28px;
      line-height: 28px;
    }
  }
  .title-text {
    min-width: 20px;
    max-width: 400px;
    line-height: 30px;
    padding: 0 6px;
    border-radius: $borderRadius;
    cursor: pointer;

    @include ellipsis-oneline();

    &:hover {
      background-color: #f1f1f1;
    }
  }
}
.github-link {
  display: inline-block;
  height: 30px;
}
</style>