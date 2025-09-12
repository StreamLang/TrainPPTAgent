<template>
  <div class="content-editor">
    <div class="editor-header">
      <h3 class="section-title">📝 内容填充</h3>
      <p class="section-subtitle">为每个章节填充详细内容</p>
    </div>
    
    <div class="sections-editor" v-if="sections.length > 0">
      <div 
        class="section-item" 
        v-for="(section, index) in sections" 
        :key="section.id"
        :class="{ 'active': activeSection === index }"
      >
        <div class="section-header" @click="toggleSection(index)">
          <div class="section-title-wrapper">
            <span class="section-number">{{ index + 1 }}</span>
            <h4 class="section-name">{{ section.title }}</h4>
          </div>
          <div class="section-actions">
            <button 
              class="toggle-btn"
              :class="{ 'expanded': section.expanded }"
            >
              ▼
            </button>
          </div>
        </div>
        
        <div class="section-content" v-show="section.expanded">
          <div class="content-fields">
            <div class="field-group" v-for="(field, fieldIndex) in section.fields" :key="fieldIndex">
              <label class="field-label">{{ field.title }}</label>
              <textarea
                v-model="field.content"
                class="content-textarea"
                rows="4"
                placeholder="请输入详细内容..."
                @blur="saveSectionContent(index, fieldIndex)"
              ></textarea>
              <div class="field-meta">
                <span class="char-count">{{ field.content.length }} 字符</span>
                <button 
                  class="add-material-btn" 
                  @click="openMaterialSelector(index, fieldIndex)"
                  v-if="materials.length > 0"
                >
                  📎 关联素材
                </button>
              </div>
              
              <!-- 关联的素材预览 -->
              <div class="linked-materials" v-if="field.materials && field.materials.length > 0">
                <div class="materials-preview">
                  <div 
                    class="material-preview-item" 
                    v-for="materialId in field.materials" 
                    :key="materialId"
                  >
                    <img 
                      :src="getMaterialUrl(materialId)" 
                      :alt="getMaterialName(materialId)"
                      class="preview-image"
                    >
                    <span class="material-name">{{ getMaterialName(materialId) }}</span>
                    <button 
                      class="remove-material-btn" 
                      @click="removeMaterialFromField(index, fieldIndex, materialId)"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else>
      <div class="empty-icon">📝</div>
      <p class="empty-text">暂无章节内容，请先提供大纲</p>
    </div>
    
    <!-- 素材选择器模态框 -->
    <div class="modal-overlay" v-if="showMaterialSelector" @click="closeMaterialSelector">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">选择关联素材</h3>
          <button class="close-btn" @click="closeMaterialSelector">×</button>
        </div>
        <div class="modal-body">
          <div class="materials-selector-grid">
            <div 
              class="material-selector-item" 
              v-for="material in materials" 
              :key="material.id"
              :class="{ 'selected': isMaterialSelected(material.id) }"
              @click="toggleMaterialSelection(material.id)"
            >
              <div class="selector-preview">
                <img :src="material.url" :alt="material.name" class="selector-image">
              </div>
              <div class="selector-info">
                <span class="selector-name">{{ material.name }}</span>
                <span class="selector-desc">{{ material.description || '无描述' }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeMaterialSelector">取消</button>
          <button class="confirm-btn" @click="confirmMaterialSelection">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, watch, onUnmounted } from 'vue'

interface SectionField {
  title: string
  content: string
  materials: string[] // 关联的素材ID列表
}

interface Section {
  id: string
  title: string
  expanded: boolean
  fields: SectionField[]
}

interface Material {
  id: string
  name: string
  url: string
  size: number
  description: string
  file: File
}

const props = defineProps<{
  outline: string
  materials: Material[]
}>()

const emit = defineEmits<{
  (e: 'contentChange', sections: Section[]): void
}>()

const sections = ref<Section[]>([])
const activeSection = ref(0)
const showMaterialSelector = ref(false)
const currentField = ref<{ sectionIndex: number; fieldIndex: number } | null>(null)
const selectedMaterials = ref<string[]>([])
let debounceTimer: number | null = null

// 解析大纲内容
const parseOutline = (outline: string) => {
  const lines = outline.split('\n').map(line => line.trim()).filter(line => line)
  const newSections: Section[] = []
  
  let currentSection: Section | null = null
  let sectionCounter = 1
  
  lines.forEach(line => {
    if (line.startsWith('# ') && !line.startsWith('## ')) {
      // 主标题，跳过
      return
    }
    
    if (line.startsWith('## ')) {
      // 章节标题
      if (currentSection) {
        newSections.push(currentSection)
      }
      
      const title = line.substring(3)
      currentSection = {
        id: `section_${sectionCounter++}`,
        title,
        expanded: false,
        fields: []
      }
    } else if (line.startsWith('### ') && currentSection) {
      // 小节标题
      const title = line.substring(4)
      currentSection.fields.push({
        title,
        content: '',
        materials: []
      })
    } else if (line.startsWith('- ') && currentSection && currentSection.fields.length > 0) {
      // 列表项，作为内容的一部分
      const item = line.substring(2)
      const lastField = currentSection.fields[currentSection.fields.length - 1]
      if (lastField.content) {
        lastField.content += '\n' + item
      } else {
        lastField.content = item
      }
    }
  })
  
  // 添加最后一个章节
  if (currentSection) {
    newSections.push(currentSection)
  }
  
  sections.value = newSections
  // 初始解析时不触发contentChange事件，避免循环更新
}

// 监听大纲变化，使用防抖避免频繁触发
watch(() => props.outline, (newOutline) => {
  if (newOutline) {
    // 清除之前的计时器
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    // 设置防抖计时器
    debounceTimer = setTimeout(() => {
      parseOutline(newOutline)
    }, 300) as unknown as number
  }
}, { immediate: true })

// 组件卸载时清理计时器
onUnmounted(() => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
})

const toggleSection = (index: number) => {
  activeSection.value = index
  sections.value[index].expanded = !sections.value[index].expanded
}

const saveSectionContent = (sectionIndex: number, fieldIndex: number) => {
  // 这里可以添加保存内容到后端的逻辑
  console.log(`保存章节 ${sectionIndex} 字段 ${fieldIndex} 的内容`)
  emitContentChange()
}

const emitContentChange = () => {
  emit('contentChange', sections.value)
}

const openMaterialSelector = (sectionIndex: number, fieldIndex: number) => {
  currentField.value = { sectionIndex, fieldIndex }
  const field = sections.value[sectionIndex].fields[fieldIndex]
  selectedMaterials.value = [...field.materials]
  showMaterialSelector.value = true
}

const closeMaterialSelector = () => {
  showMaterialSelector.value = false
  currentField.value = null
  selectedMaterials.value = []
}

const toggleMaterialSelection = (materialId: string) => {
  const index = selectedMaterials.value.indexOf(materialId)
  if (index > -1) {
    selectedMaterials.value.splice(index, 1)
  } else {
    selectedMaterials.value.push(materialId)
  }
}

const isMaterialSelected = (materialId: string) => {
  return selectedMaterials.value.includes(materialId)
}

const confirmMaterialSelection = () => {
  if (currentField.value) {
    const { sectionIndex, fieldIndex } = currentField.value
    sections.value[sectionIndex].fields[fieldIndex].materials = [...selectedMaterials.value]
    emitContentChange()
  }
  closeMaterialSelector()
}

const removeMaterialFromField = (sectionIndex: number, fieldIndex: number, materialId: string) => {
  const field = sections.value[sectionIndex].fields[fieldIndex]
  const index = field.materials.indexOf(materialId)
  if (index > -1) {
    field.materials.splice(index, 1)
    emitContentChange()
  }
}

const getMaterialUrl = (materialId: string) => {
  const material = props.materials.find(m => m.id === materialId)
  return material ? material.url : ''
}

const getMaterialName = (materialId: string) => {
  const material = props.materials.find(m => m.id === materialId)
  return material ? material.name : ''
}

// 暴露方法给父组件
defineExpose({
  getSections: () => sections.value
})
</script>

<style lang="scss" scoped>
.content-editor {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.editor-header {
  margin-bottom: 1.5rem;
  
  .section-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .section-subtitle {
    font-size: 0.9rem;
    color: #64748b;
    margin: 0;
  }
}

.section-item {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  margin-bottom: 1rem;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &.active {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  cursor: pointer;
  transition: background 0.3s ease;
  
  &:hover {
    background: #f1f5f9;
  }
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #667eea;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.section-name {
  font-size: 1rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.section-actions {
  .toggle-btn {
    background: none;
    border: none;
    font-size: 0.9rem;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      background: #e2e8f0;
      color: #64748b;
    }
    
    &.expanded {
      transform: rotate(180deg);
    }
  }
}

.section-content {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #e2e8f0;
}

.content-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  font-weight: 500;
  color: #475569;
  font-size: 0.9rem;
}

.content-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
}

.field-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.25rem;
}

.char-count {
  font-size: 0.8rem;
  color: #94a3b8;
}

.add-material-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  &:hover {
    background: #e2e8f0;
  }
}

.linked-materials {
  margin-top: 0.75rem;
}

.materials-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.material-preview-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.preview-image {
  width: 24px;
  height: 24px;
  object-fit: cover;
  border-radius: 0.25rem;
}

.material-name {
  color: #475569;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-material-btn {
  background: none;
  border: none;
  color: #ef4444;
  font-weight: bold;
  cursor: pointer;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  
  &:hover {
    background: #fee2e2;
  }
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1rem;
  margin: 0;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 1rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #334155;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  
  &:hover {
    background: #f1f5f9;
    color: #64748b;
  }
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.materials-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.material-selector-item {
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &.selected {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
  }
  
  &:hover {
    border-color: #cbd5e1;
    transform: translateY(-2px);
  }
}

.selector-preview {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.selector-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.selector-info {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.selector-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selector-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.cancel-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e2e8f0;
  }
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
}

@media (max-width: 768px) {
  .content-editor {
    padding: 1rem;
  }
  
  .section-header {
    padding: 0.75rem 1rem;
  }
  
  .section-content {
    padding: 0 1rem 1rem;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .materials-selector-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>