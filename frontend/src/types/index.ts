/**
 * 类型定义文件
 */

// 优化级别
export enum OptimizationLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

// 任务类型
export enum TaskType {
  GENERATION = 'generation',
  ANALYSIS = 'analysis',
  CONVERSATION = 'conversation',
  EXTRACTION = 'extraction',
  TRANSFORMATION = 'transformation',
  REASONING = 'reasoning',
  OTHER = 'other'
}

// 意图结果
export interface IntentResult {
  task_type: TaskType
  domain: string
  objective: string
  constraints: string[]
  keywords: string[]
  context: Record<string, any>
  confidence: number
}

// Prompt 模板
export interface PromptTemplate {
  template_id: string
  name: string
  description?: string
  role: string
  objective: string
  constraints: string[]
  output_format: string
  context_vars: Record<string, string>
  task_types: TaskType[]
  domains: string[]
  tags: string[]
  created_at: string
  updated_at: string
  usage_count: number
  avg_quality_score: number
}

// 编译后的 Prompt
export interface CompiledPrompt {
  version_id: string
  original_input: string
  intent: IntentResult
  template_id?: string
  role: string
  objective: string
  constraints: string[]
  output_format: string
  context: Record<string, any>
  full_prompt: string
  optimization_level: OptimizationLevel
  optimized: boolean
  created_at: string
}

// 质量指标
export interface QualityMetrics {
  structure_score: number
  consistency_score: number
  completeness_score: number
  clarity_score: number
  overall_score: number
}

// 评估结果
export interface EvaluationResult {
  evaluation_id: string
  prompt_version_id: string
  metrics: QualityMetrics
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  ai_analysis?: string
  evaluated_at: string
  evaluator: string
}

// API 请求和响应

export interface CompileRequest {
  user_input: string
  template_id?: string
  optimization_level: OptimizationLevel
  auto_evaluate: boolean
}

export interface CompileResponse {
  success: boolean
  compiled_prompt: CompiledPrompt
  metrics?: QualityMetrics
  suggestions: string[]
  formatted_output: any
}

export interface OptimizeRequest {
  prompt_text: string
  optimization_level: OptimizationLevel
  focus_areas?: string[]
}

export interface OptimizeResponse {
  success: boolean
  original_prompt: string
  optimized_prompt: string
  improvements: string[]
  metrics_before: QualityMetrics
  metrics_after: QualityMetrics
}

export interface EvaluateRequest {
  prompt_text: string
  intent?: IntentResult
}

export interface EvaluateResponse {
  success: boolean
  evaluation: EvaluationResult
}

