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
}

interface PPTData {
  slides: any[] // 根据实际的slides类型定义
  theme: any // 根据实际的theme类型定义
}

class SessionManager {
  /**
   * 存储大纲数据
   * @param data 大纲数据
   * @param sessionId 可选的sessionId，如果提供则使用该ID，否则生成新ID
   * @returns sessionId
   */
  static storeOutlineData(data: OutlineData, sessionId?: string): string {
    const finalSessionId = sessionId || Date.now().toString()
    sessionStorage.setItem(`outline_${finalSessionId}`, JSON.stringify(data))
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
      return JSON.parse(data)
    }
    return null
  }

  /**
   * 存储PPT数据
   * @param data PPT数据
   * @param sessionId 可选的sessionId，如果提供则使用该ID，否则生成新ID
   * @returns sessionId
   */
  static storePPTData(data: PPTData, sessionId?: string): string {
    const finalSessionId = sessionId || Date.now().toString()
    sessionStorage.setItem(`ppt_${finalSessionId}`, JSON.stringify(data))
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
      return JSON.parse(data)
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
}

export default SessionManager