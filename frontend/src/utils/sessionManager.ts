/**
 * Session数据管理工具
 * 用于在页面跳转时存储和获取数据，避免URL参数过长的问题
 */

interface OutlineImage {
  data: string
  type: string
  name: string
}

interface OutlineData {
  outline: string
  language: string
  model: string
  images?: OutlineImage[]
  progress?: string
  updatedAt?: number
  createdAt?: number
}

interface PPTData {
  slides: any[] // 根据实际的slides类型定义
  theme: any // 根据实际的theme类型定义
  userSections?: any[] // 用户填写的内容
  progress?: string
  updatedAt?: number
  createdAt?: number
}

interface EditorData {
  // 根据实际的Editor数据类型定义
  progress?: string
  updatedAt?: number
  createdAt?: number
}

interface SessionState {
  sessionId: string
  title?: string
  outline?: string
  progress: string
  updatedAt: number
  createdAt: number
  language?: string
  model?: string
}

class SessionManager {
  /**
   * 存储大纲数据
   * @param data 大纲数据
   * @param sessionId 可选的sessionId，如果提供则使用该ID，否则生成新ID
   * @param progress 进度状态
   * @returns sessionId
   */
  static storeOutlineData(data: OutlineData, sessionId?: string, progress: string = 'outline'): string {
    const finalSessionId = sessionId || Date.now().toString()
    const sessionData: OutlineData = {
      ...data,
      progress: progress,
      updatedAt: Date.now(),
      createdAt: sessionId ? this.getOutlineData(sessionId)?.createdAt || Date.now() : Date.now()
    }
    sessionStorage.setItem(`outline_${finalSessionId}`, JSON.stringify(sessionData))
    return finalSessionId
  }

  /**
   * 获取大纲数据
   * @param sessionId 会话ID
   * @returns 大纲数据
   */
  static getOutlineData(sessionId: string): OutlineData | null {
    const data = sessionStorage.getItem(`outline_${sessionId}`)
    if (data) {
      const parsedData = JSON.parse(data)
      return {
        ...parsedData,
        progress: parsedData.progress || 'outline',
        updatedAt: parsedData.updatedAt || parseInt(sessionId),
        createdAt: parsedData.createdAt || parseInt(sessionId)
      }
    }
    return null
  }

  /**
   * 存储PPT数据
   * @param data PPT数据
   * @param sessionId 可选的sessionId，如果提供则使用该ID，否则生成新ID
   * @param progress 进度状态
   * @returns sessionId
   */
  static storePPTData(data: PPTData, sessionId?: string, progress: string = 'ppt'): string {
    const finalSessionId = sessionId || Date.now().toString()
    const sessionData: PPTData = {
      ...data,
      progress: progress,
      updatedAt: Date.now(),
      createdAt: sessionId ? this.getPPTData(sessionId)?.createdAt || Date.now() : Date.now()
    }
    sessionStorage.setItem(`ppt_${finalSessionId}`, JSON.stringify(sessionData))
    return finalSessionId
  }

  /**
   * 获取PPT数据
   * @param sessionId 会话ID
   * @returns PPT数据
   */
  static getPPTData(sessionId: string): PPTData | null {
    const data = sessionStorage.getItem(`ppt_${sessionId}`)
    if (data) {
      const parsedData = JSON.parse(data)
      return {
        ...parsedData,
        progress: parsedData.progress || 'ppt',
        updatedAt: parsedData.updatedAt || parseInt(sessionId),
        createdAt: parsedData.createdAt || parseInt(sessionId)
      }
    }
    return null
  }

  /**
   * 存储Editor数据
   * @param data Editor数据
   * @param sessionId 可选的sessionId，如果提供则使用该ID，否则生成新ID
   * @param progress 进度状态
   * @returns sessionId
   */
  static storeEditorData(data: EditorData, sessionId?: string, progress: string = 'editor'): string {
    const finalSessionId = sessionId || Date.now().toString()
    const sessionData: EditorData = {
      ...data,
      progress: progress,
      updatedAt: Date.now(),
      createdAt: sessionId ? this.getEditorData(sessionId)?.createdAt || Date.now() : Date.now()
    }
    sessionStorage.setItem(`editor_${finalSessionId}`, JSON.stringify(sessionData))
    return finalSessionId
  }

  /**
   * 获取Editor数据
   * @param sessionId 会话ID
   * @returns Editor数据
   */
  static getEditorData(sessionId: string): EditorData | null {
    const data = sessionStorage.getItem(`editor_${sessionId}`)
    if (data) {
      const parsedData = JSON.parse(data)
      return {
        ...parsedData,
        progress: parsedData.progress || 'editor',
        updatedAt: parsedData.updatedAt || parseInt(sessionId),
        createdAt: parsedData.createdAt || parseInt(sessionId)
      }
    }
    return null
  }

  /**
   * 清除指定的session数据
   * @param sessionId 会话ID
   * @param type 数据类型
   */
  static clearSessionData(sessionId: string, type: 'outline' | 'ppt'): void {
    sessionStorage.removeItem(`${type}_${sessionId}`)
  }

  /**
   * 获取所有session数据（包括outline、ppt、editor）
   * @returns 包含session_id和数据的数组
   */
  static getAllSessions(): Array<{sessionId: string, data: any}> {
    const sessions: Array<{sessionId: string, data: any}> = []
    
    // 首先收集所有session数据
    const allSessions: Map<string, {type: string, data: any}> = new Map()
    
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i)
      if (key && (key.startsWith('outline_') || key.startsWith('ppt_') || key.startsWith('editor_'))) {
        const sessionId = key.replace(/^(outline_|ppt_|editor_)/, '')
        const type = key.startsWith('outline_') ? 'outline' : 
                    key.startsWith('ppt_') ? 'ppt' : 'editor'
        const data = sessionStorage.getItem(key)
        if (data) {
          try {
            const parsedData = JSON.parse(data)
            allSessions.set(sessionId, {
              type,
              data: {
                ...parsedData,
                progress: parsedData.progress || type,
                updatedAt: parsedData.updatedAt || parseInt(sessionId),
                createdAt: parsedData.createdAt || parseInt(sessionId)
              }
            })
          } catch (e) {
            console.warn('解析session数据失败:', key, e)
          }
        }
      }
    }
    
    // 为每个session选择最新的数据
    for (const [sessionId, sessionInfo] of allSessions) {
      sessions.push({
        sessionId,
        data: sessionInfo.data
      })
    }
    
    // 按更新时间倒序排列
    return sessions.sort((a, b) => (b.data.updatedAt || parseInt(b.sessionId)) - (a.data.updatedAt || parseInt(a.sessionId)))
  }

  /**
   * 获取所有outline session数据（向后兼容）
   * @returns 包含session_id和数据的数组
   */
  static getAllOutlineSessions(): Array<{sessionId: string, data: OutlineData}> {
    return this.getAllSessions() as Array<{sessionId: string, data: OutlineData}>
  }

  /**
   * 获取session的当前进度
   * @param sessionId 会话ID
   * @returns 进度状态（'outline' | 'ppt' | 'editor'）
   */
  static getSessionProgress(sessionId: string): string {
    // 检查所有类型的数据，返回最新的进度状态
    const pptData = this.getPPTData(sessionId)
    const outlineData = this.getOutlineData(sessionId)
    const editorData = this.getEditorData(sessionId)
    
    // 优先返回最新更新的数据
    const allData = [
      { data: pptData, type: 'ppt' },
      { data: outlineData, type: 'outline' },
      { data: editorData, type: 'editor' }
    ].filter(item => item.data !== null)
    
    if (allData.length === 0) {
      return 'outline' // 默认
    }
    
    // 按更新时间排序，返回最新的进度状态
    const latestData = allData.sort((a, b) => 
      ((b.data?.updatedAt) || 0) - ((a.data?.updatedAt) || 0)
    )[0]
    
    return latestData.data.progress || latestData.type
  }

  /**
   * 清除所有过期的session数据（可选功能）
   * @param maxAge 最大保留时间（毫秒），默认24小时
   */
  static clearExpiredData(maxAge: number = 24 * 60 * 60 * 1000): void {
    const now = Date.now()
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i)
      if (key && (key.startsWith('outline_') || key.startsWith('ppt_'))) {
        // 这里可以实现更复杂的过期逻辑，比如在key中包含时间戳
        // 简单起见，我们只提供手动清理的方法
      }
    }
  }

  /**
   * 获取统一的session状态信息
   * @param sessionId 会话ID
   * @returns 统一的session状态
   */
  static getSessionState(sessionId: string): SessionState {
    const progress = this.getSessionProgress(sessionId)
    const outlineData = this.getOutlineData(sessionId)
    const pptData = this.getPPTData(sessionId)
    
    // 从大纲数据中提取标题
    let title = '未命名PPT'
    if (outlineData?.outline) {
      const firstLine = outlineData.outline.split('\
')[0]?.trim()
      if (firstLine && firstLine.length > 0 && firstLine.length < 50) {
        title = firstLine
      }
    }

    // 获取最新的更新时间
    let latestUpdatedAt = parseInt(sessionId)
    if (outlineData?.updatedAt) latestUpdatedAt = Math.max(latestUpdatedAt, outlineData.updatedAt)
    if (pptData?.updatedAt) latestUpdatedAt = Math.max(latestUpdatedAt, pptData.updatedAt)

    return {
      sessionId,
      title,
      outline: outlineData?.outline,
      progress,
      updatedAt: latestUpdatedAt,
      createdAt: parseInt(sessionId),
      language: outlineData?.language || '中文',
      model: outlineData?.model || 'qwen3-235b'
    }
  }

  /**
   * 获取所有session的统一状态信息
   * @returns 包含统一session状态的数组
   */
  static getAllSessionStates(): SessionState[] {
    const sessions = this.getAllSessions()
    const sessionStates: SessionState[] = []
    const processedIds = new Set<string>()

    for (const session of sessions) {
      if (!processedIds.has(session.sessionId)) {
        sessionStates.push(this.getSessionState(session.sessionId))
        processedIds.add(session.sessionId)
      }
    }

    // 按更新时间倒序排列
    return sessionStates.sort((a, b) => b.updatedAt - a.updatedAt)
  }
}

export default SessionManager