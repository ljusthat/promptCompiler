/**
 * Prompt 相关 API 服务
 */
import apiClient from './api'
import type {
  CompileRequest,
  CompileResponse,
  OptimizeRequest,
  OptimizeResponse,
  EvaluateRequest,
  EvaluateResponse,
} from '../types'

export const promptService = {
  /**
   * 编译 Prompt
   */
  async compile(request: CompileRequest): Promise<CompileResponse> {
    console.log('发送编译请求:', request)
    const response = await apiClient.post('/compile', request)
    console.log('收到编译响应:', response)
    return response
  },

  /**
   * 优化 Prompt
   */
  async optimize(request: OptimizeRequest): Promise<OptimizeResponse> {
    return apiClient.post('/optimize', request)
  },

  /**
   * 评估 Prompt
   */
  async evaluate(request: EvaluateRequest): Promise<EvaluateResponse> {
    return apiClient.post('/evaluate', request)
  },
}

export default promptService

