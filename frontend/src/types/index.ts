export interface User {
  id: string
  email: string
  username: string
  created_at: string
}

export interface Problem {
  id: string
  title: string
  slug: string
  description: string
  difficulty: 'easy' | 'medium' | 'hard'
  test_cases: TestCase[]
  starter_code: string
}

export interface ProblemListItem {
  id: string
  title: string
  slug: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface TestCase {
  input: string
  expected: string
  is_hidden: boolean
}

export interface TestResult {
  index: number
  status: 'passed' | 'failed' | 'error' | 'timeout'
  input: string
  expected: string
  actual: string | null
  error: string | null
  elapsed_ms: number | null
  is_hidden: boolean
}

export interface Submission {
  id: string
  status: 'pending' | 'running' | 'passed' | 'failed' | 'error' | 'timeout'
  test_results: TestResult[] | null
  passed_count: number
  total_count: number
  created_at: string
}

export interface Hint {
  id: string
  level: 1 | 2 | 3
  content: string
  created_at: string
}

// WebSocket message types
export type WSMessage =
  | { type: 'start'; total: number }
  | { type: 'result'; data: TestResult }
  | { type: 'complete'; status: string; passed: number; total: number }
  | { type: 'error'; message: string }
