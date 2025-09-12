<template>
  <div class="material-uploader">
    <div class="uploader-header">
      <h3 class="section-title">📎 素材管理</h3>
      <p class="section-subtitle">上传图片素材并添加描述</p>
    </div>
    
    <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
      <div 
        class="drop-zone" 
        :class="{ 'drag-over': isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop="handleDrop"
      >
        <div class="upload-icon">📁</div>
        <p class="upload-text">拖拽文件到此处或点击上传</p>
        <p class="upload-hint">支持 JPG、PNG、GIF 格式，单个文件不超过 10MB</p>
        <input 
          type="file" 
          ref="fileInput" 
          class="file-input" 
          accept="image/*" 
          multiple 
          @change="handleFileSelect"
        >
        <button class="upload-btn" @click="triggerFileInput">选择文件</button>
      </div>
    </div>
    
    <div class="materials-list" v-if="materials.length > 0">
      <h4 class="list-title">已上传素材 ({{ materials.length }})</h4>
      <div class="materials-grid">
        <div 
          class="material-item" 
          v-for="(material, index) in materials" 
          :key="material.id"
        >
          <div class="material-preview">
            <img :src="material.url" :alt="material.name" class="material-image">
          </div>
          <div class="material-info">
            <input 
              type="text" 
              v-model="material.description" 
              class="material-description"
              placeholder="请输入素材描述"
              @blur="saveMaterialDescription(index)"
            >
            <div class="material-meta">
              <span class="material-name">{{ material.name }}</span>
              <span class="material-size">{{ formatFileSize(material.size) }}</span>
            </div>
            <button class="delete-btn" @click="removeMaterial(index)">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from 'vue'

interface Material {
  id: string
  name: string
  url: string
  size: number
  description: string
  file: File
}

const isDragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const materials = ref<Material[]>([])

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    processFiles(Array.from(input.files))
    // 清空input值以便重复选择相同文件
    input.value = ''
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer && event.dataTransfer.files.length > 0) {
    processFiles(Array.from(event.dataTransfer.files))
  }
}

const processFiles = (files: File[]) => {
  files.forEach(file => {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert(`文件 ${file.name} 不是图片格式，请上传 JPG、PNG 或 GIF 格式的图片`)
      return
    }
    
    // 检查文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert(`文件 ${file.name} 超过 10MB 限制`)
      return
    }
    
    // 创建预览URL
    const url = URL.createObjectURL(file)
    
    // 添加到素材列表
    materials.value.push({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      url: url,
      size: file.size,
      description: '',
      file: file
    })
  })
}

const saveMaterialDescription = (index: number) => {
  // 这里可以添加保存描述到后端的逻辑
  console.log(`保存素材 ${materials.value[index].name} 的描述: ${materials.value[index].description}`)
}

const removeMaterial = (index: number) => {
  // 释放预览URL
  URL.revokeObjectURL(materials.value[index].url)
  materials.value.splice(index, 1)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 暴露方法给父组件
defineExpose({
  getMaterials: () => materials.value
})
</script>

<style lang="scss" scoped>
.material-uploader {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.uploader-header {
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

.upload-area {
  margin-bottom: 1.5rem;
}

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  background: #f8fafc;
  
  &.drag-over {
    border-color: #667eea;
    background: #f0f4ff;
  }
  
  .upload-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }
  
  .upload-text {
    font-size: 1.1rem;
    font-weight: 500;
    color: #475569;
    margin: 0 0 0.5rem 0;
  }
  
  .upload-hint {
    font-size: 0.85rem;
    color: #94a3b8;
    margin: 0 0 1.5rem 0;
  }
  
  .file-input {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }
  
  .upload-btn {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
  }
}

.materials-list {
  .list-title {
    font-size: 1rem;
    font-weight: 600;
    color: #334155;
    margin: 0 0 1rem 0;
  }
}

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.material-item {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.material-preview {
  height: 120px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  
  .material-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
  }
}

.material-info {
  padding: 0.75rem;
}

.material-description {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
}

.material-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.material-name {
  font-size: 0.8rem;
  font-weight: 500;
  color: #475569;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-size {
  font-size: 0.75rem;
  color: #94a3b8;
}

.delete-btn {
  width: 100%;
  padding: 0.5rem;
  background: #fee2e2;
  color: #ef4444;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #fecaca;
  }
}

@media (max-width: 768px) {
  .materials-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .material-preview {
    height: 100px;
  }
}
</style>