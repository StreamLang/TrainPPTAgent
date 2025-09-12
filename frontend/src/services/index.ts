import axios from './config'

// export const SERVER_URL = 'http://localhost:5000'
export const SERVER_URL = '/api'

interface AIPPTOutlinePayload {
  content: string
  language: string
  model: string
}

interface AIPPTPayload {
  content: string
  language: string
  style: string
  model: string
}

interface AIPPTContentPayload {
  content: string
  materials?: Array<{
    id: string
    name: string
    description: string
  }>
  sections?: Array<{
    id: string
    title: string
    fields: Array<{
      title: string
      content: string
      materials: string[]
    }>
  }>
}

interface AIWritingPayload {
  content: string
  command: string
}

export default {
  getMockData(filename: string): Promise<any> {
    return axios.get(`./mocks/${filename}.json`)
  },

  getFileData(filename: string): Promise<any> {
    return axios.get(`${SERVER_URL}/data/${filename}.json`)
  },

  AIPPT_Outline({
    content,
    language,
    model,
  }: AIPPTOutlinePayload): Promise<any> {
    return fetch(`${SERVER_URL}/tools/aippt_outline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        language,
        model,
        stream: true,
      }),
    })
  },

  AIPPT({
    content,
    language,
    style,
    model,
    materials,
    sections
  }: AIPPTContentPayload & { language: string; style: string; model: string }): Promise<any> {
    return fetch(`${SERVER_URL}/tools/aippt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        language,
        model,
        style,
        stream: true,
        materials: materials || [],
        sections: sections || []
      }),
    })
  },

  async uploadMaterial(file: File, description: string = ''): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('description', description)
    
    const response = await fetch(`${SERVER_URL}/upload_material`, {
      method: 'POST',
      body: formData
    })
    
    return response.json()
  },

  AI_Writing({
    content,
    command,
  }: AIWritingPayload): Promise<any> {
    return fetch(`${SERVER_URL}/tools/ai_writing`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        command,
        stream: true,
      }),
    })
  },
}