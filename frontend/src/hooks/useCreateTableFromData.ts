import { nanoid } from 'nanoid'
import { useSlidesStore } from '@/store'
import useCreateElement from './useCreateElement'
import useHistorySnapshot from './useHistorySnapshot'
import type { TableCell, TableCellStyle } from '@/types/slides'

export default () => {
  const slidesStore = useSlidesStore()
  const { createTableElement } = useCreateElement()
  const { addHistorySnapshot } = useHistorySnapshot()

  /**
   * 解析CSV数据
   * @param csvText CSV格式的文本数据
   * @returns 二维字符串数组
   */
  const parseCSVData = (csvText: string): string[][] => {
    const lines = csvText.trim().split('\n')
    const data: string[][] = []
    
    for (const line of lines) {
      // 简单的CSV解析，实际项目中可能需要更复杂的解析逻辑
      const row = line.split(',')
      data.push(row)
    }
    
    return data
  }

  /**
   * 根据数据创建表格
   * @param data 二维字符串数组形式的表格数据
   */
  const createTableFromData = async (data: string[][]) => {
    if (data.length === 0) return
    
    const rows = data.length
    const cols = data[0].length
    
    // 获取当前主题
    const theme = slidesStore.theme
    
    // 创建表格样式
    const style: TableCellStyle = {
      fontname: theme.fontName,
      color: theme.fontColor,
    }
    
    // 构造表格数据
    const tableData: TableCell[][] = []
    for (let i = 0; i < rows; i++) {
      const rowCells: TableCell[] = []
      for (let j = 0; j < cols; j++) {
        rowCells.push({ 
          id: nanoid(10), 
          colspan: 1, 
          rowspan: 1, 
          text: data[i][j] || '', 
          style 
        })
      }
      tableData.push(rowCells)
    }
    
    // 记录创建前的元素数量
    const currentSlide = slidesStore.currentSlide
    const initialTableCount = currentSlide.elements.filter(el => el.type === 'table').length
    
    // 使用现有的createTableElement创建基础表格
    createTableElement(rows, cols)
    
    // 等待元素创建完成
    await new Promise(resolve => {
      const checkInterval = setInterval(() => {
        const updatedSlide = slidesStore.currentSlide
        const currentTableCount = updatedSlide.elements.filter(el => el.type === 'table').length
        
        // 当表格数量增加时，说明新表格已创建完成
        if (currentTableCount > initialTableCount) {
          clearInterval(checkInterval)
          resolve(null)
        }
      }, 50)
      
      // 设置超时时间，避免无限等待
      setTimeout(() => {
        clearInterval(checkInterval)
        resolve(null)
      }, 2000)
    })
    
    // 获取最新创建的表格元素
    const updatedSlide = slidesStore.currentSlide
    const tableElements = updatedSlide.elements.filter(el => el.type === 'table')
    
    if (tableElements.length > 0) {
      const latestTableElement = tableElements[tableElements.length - 1]
      const elementId = latestTableElement.id
      
      // 更新表格元素的数据
      slidesStore.updateElement({
        id: elementId,
        props: {
          data: tableData
        }
      })
      
      addHistorySnapshot()
    }
  }

  return {
    parseCSVData,
    createTableFromData
  }
}