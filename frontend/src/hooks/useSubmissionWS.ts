import { useRef, useCallback } from 'react'
import { WSMessage, TestResult } from '../types'
import { WS_URL } from '../api'

interface UseSubmissionWSOptions {
  onResult: (result: TestResult) => void
  onComplete: (passed: number, total: number, status: string) => void
  onError: (msg: string) => void
}

export function useSubmissionWS({
  onResult,
  onComplete,
  onError,
}: UseSubmissionWSOptions) {
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(
    (submissionId: string) => {
      // Close any existing connection
      wsRef.current?.close()

      const ws = new WebSocket(`${WS_URL}/submissions/ws/${submissionId}`)
      wsRef.current = ws

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data)

          switch (msg.type) {
            case 'result':
              onResult(msg.data)
              break
            case 'complete':
              onComplete(msg.passed, msg.total, msg.status)
              break
            case 'error':
              onError(msg.message)
              break
          }
        } catch {
          // Ignore parse errors
        }
      }

      ws.onerror = () => {
        onError('WebSocket connection failed.')
      }
    },
    [onResult, onComplete, onError]
  )

  const disconnect = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
  }, [])

  return { connect, disconnect }
}
