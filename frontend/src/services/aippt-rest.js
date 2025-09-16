import axios from 'axios'

const API_BASE = '/api/tools'

export const generateAIPPT = async (markdown, model = 'qwen3-235b') => {
  const response = await axios.post(`${API_BASE}/aippt_rest`, {
    markdown,
    model
  })
  return {
    task_id: response.task_id,
    status: response.status
  }
}

export const getAIPPTResult = async (taskId) => {
  const response = await axios.get(`${API_BASE}/aippt_rest_result/${taskId}`)
  return response
}

// 添加请求拦截器处理错误
axios.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)