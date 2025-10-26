/**
 * API 服务基础配置
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 120000, // 增加超时到120秒，因为AI编译可能需要较长时间
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    // 统一错误处理
    console.error('API 请求错误:', error)
    
    // 如果是超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return Promise.reject({
        status: 0,
        message: '请求超时，请稍后重试',
      })
    }
    
    if (error.response) {
      // 服务器返回错误状态
      const status = error.response.status
      const message = error.response.data?.detail || error.response.data?.error_message || '请求失败'
      
      return Promise.reject({
        status,
        message,
        data: error.response.data
      })
    } else if (error.request) {
      // 请求发送失败
      return Promise.reject({
        status: 0,
        message: '网络错误，请检查您的网络连接',
      })
    } else {
      // 其他错误
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误',
      })
    }
  }
)

export default apiClient

