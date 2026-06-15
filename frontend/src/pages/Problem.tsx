import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'
import { useSubmissionWS } from '../hooks/useSubmissionWS'
import { Problem, TestResult, Hint } from '../types'

type RunStatus = 'idle' | 'running' | 'passed' | 'failed' | 'error'

export default function ProblemPage() {
  const { slug } = useParams<{ slug: string }>()
  const [problem, setProblem] = useState<Problem | null>(null)
  const [code, setCode] = useState('')
  const [status, setStatus] = useState<RunStatus>('idle')
  const [results, setResults] = useState<TestResult[]>([])
  const [summary, setSummary] = useState<{ passed: number; total: number } | null>(null)
  const [submissionId, setSubmissionId] = useState<string | null>(null)
  const [hints, setHints] = useState<Hint[]>([])
  const [hintLoading, setHintLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'results' | 'hints'>('results')

  useEffect(() => {
    api.get(`/problems/${slug}`).then((res) => {
      setProblem(res.data)
      setCode(res.data.starter_code)
    })
  }, [slug])

  const onResult = useCallback((result: TestResult) => {
    setResults((prev) => [...prev, result])
  }, [])

  const onComplete = useCallback((passed: number, total: number, s: string) => {
    setSummary({ passed, total })
    setStatus(s === 'passed' ? 'passed' : 'failed')
  }, [])

  const onError = useCallback((msg: string) => {
    setStatus('error')
    console.error('WS error:', msg)
  }, [])

  const { connect } = useSubmissionWS({ onResult, onComplete, onError })

  const runCode = async () => {
    if (!problem) return
    setStatus('running')
    setResults([])
    setSummary(null)
    setHints([])

    const res = await api.post('/submissions/', {
      problem_id: problem.id,
      code,
    })
    const id = res.data.id
    setSubmissionId(id)
    connect(id)
  }

  const requestHint = async (level: 1 | 2 | 3) => {
    if (!submissionId) return
    setHintLoading(true)
    setActiveTab('hints')
    try {
      const res = await api.post(`/submissions/${submissionId}/hint`, {
        submission_id: submissionId,
        level,
      })
      setHints((prev) => [...prev, res.data])
    } catch (e) {
      console.error('Hint error:', e)
    } finally {
      setHintLoading(false)
    }
  }

  const markHint = async (hintId: string, helpful: boolean) => {
    if (!submissionId) return
    await api.put(`/submissions/${submissionId}/hint/${hintId}/feedback`, {
      was_helpful: helpful,
    })
  }

  if (!problem) {
    return <div style={{ padding: '2rem', color: 'var(--text2)' }}>Loading…</div>
  }

  const canHint = status === 'failed' || status === 'error'
  const passRate = summary ? `${summary.passed}/${summary.total}` : null

  return (
    <div style={styles.wrap}>
      {/* Top nav */}
      <nav style={styles.nav}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Link to="/" style={{ color: 'var(--text2)', fontSize: 13 }}>← Problems</Link>
          <span style={{ color: 'var(--border)' }}>|</span>
          <span style={{ fontWeight: 500 }}>{problem.title}</span>
          <span className={`badge ${problem.difficulty}`}>{problem.difficulty}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {passRate && (
            <span style={{ fontSize: 13, color: status === 'passed' ? 'var(--green)' : 'var(--red)' }}>
              {passRate} passed
            </span>
          )}
          <button
            className="btn-primary"
            onClick={runCode}
            disabled={status === 'running'}
            style={{ padding: '8px 20px' }}
          >
            {status === 'running' ? 'Running…' : '▶ Run'}
          </button>
        </div>
      </nav>

      <div style={styles.body}>
        {/* Left: problem description */}
        <div style={styles.left}>
          <div style={styles.prose}>
            <ReactMarkdown>{problem.description}</ReactMarkdown>
          </div>
        </div>

        {/* Center: Monaco editor */}
        <div style={styles.center}>
          <Editor
            height="100%"
            language="python"
            theme="vs-dark"
            value={code}
            onChange={(v) => setCode(v ?? '')}
            options={{
              fontSize: 14,
              fontFamily: 'JetBrains Mono, monospace',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              wordWrap: 'on',
              tabSize: 4,
            }}
          />
        </div>

        {/* Right: results + hints */}
        <div style={styles.right}>
          {/* Tabs */}
          <div style={styles.tabs}>
            <button
              style={{ ...styles.tab, ...(activeTab === 'results' ? styles.tabActive : {}) }}
              onClick={() => setActiveTab('results')}
            >
              Test results {results.length > 0 && `(${results.length})`}
            </button>
            <button
              style={{ ...styles.tab, ...(activeTab === 'hints' ? styles.tabActive : {}) }}
              onClick={() => setActiveTab('hints')}
            >
              Hints {hints.length > 0 && `(${hints.length})`}
            </button>
          </div>

          {activeTab === 'results' && (
            <div style={styles.panel}>
              {status === 'idle' && (
                <p style={{ color: 'var(--text3)', padding: '20px 0', fontSize: 13 }}>
                  Run your code to see test results here.
                </p>
              )}
              {status === 'running' && results.length === 0 && (
                <p style={{ color: 'var(--text2)', padding: '20px 0', fontSize: 13 }}>
                  Running tests…
                </p>
              )}
              {results.map((r) => (
                <TestResultRow key={r.index} result={r} />
              ))}
            </div>
          )}

          {activeTab === 'hints' && (
            <div style={styles.panel}>
              {/* Hint buttons */}
              {canHint && (
                <div style={styles.hintButtons}>
                  <p style={{ color: 'var(--text2)', fontSize: 12, marginBottom: 10 }}>
                    Get a hint grounded in your specific failure:
                  </p>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn-ghost" onClick={() => requestHint(1)} disabled={hintLoading} style={{ flex: 1, fontSize: 12, padding: '6px 0' }}>
                      Nudge
                    </button>
                    <button className="btn-ghost" onClick={() => requestHint(2)} disabled={hintLoading} style={{ flex: 1, fontSize: 12, padding: '6px 0' }}>
                      Specific
                    </button>
                    <button className="btn-ghost" onClick={() => requestHint(3)} disabled={hintLoading} style={{ flex: 1, fontSize: 12, padding: '6px 0' }}>
                      Near-solution
                    </button>
                  </div>
                </div>
              )}

              {!canHint && hints.length === 0 && (
                <p style={{ color: 'var(--text3)', fontSize: 13, padding: '20px 0' }}>
                  {status === 'idle' ? 'Run your code first, then request a hint.' : 'All tests passed — no hint needed!'}
                </p>
              )}

              {hintLoading && (
                <div style={styles.hintCard}>
                  <p style={{ color: 'var(--text2)', fontSize: 13 }}>Analysing your code…</p>
                </div>
              )}

              {hints.map((hint) => (
                <HintCard key={hint.id} hint={hint} onFeedback={markHint} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function TestResultRow({ result }: { result: TestResult }) {
  const [open, setOpen] = useState(result.status !== 'passed')

  const statusColor = {
    passed:  'var(--green)',
    failed:  'var(--red)',
    error:   'var(--red)',
    timeout: 'var(--amber)',
  }[result.status] || 'var(--text2)'

  const icon = { passed: '✓', failed: '✗', error: '!', timeout: '⏱' }[result.status] || '?'

  return (
    <div style={styles.resultRow}>
      <button
        onClick={() => setOpen(!open)}
        style={{ ...styles.resultHeader, borderColor: open ? 'var(--border)' : 'transparent' }}
      >
        <span style={{ color: statusColor, fontFamily: 'var(--mono)', fontSize: 12 }}>{icon}</span>
        <span style={{ flex: 1, fontSize: 13 }}>
          {result.is_hidden ? `Hidden test ${result.index + 1}` : `Test ${result.index + 1}`}
        </span>
        {result.elapsed_ms != null && (
          <span style={{ color: 'var(--text3)', fontSize: 11, fontFamily: 'var(--mono)' }}>
            {result.elapsed_ms}ms
          </span>
        )}
        <span style={{ color: 'var(--text3)', fontSize: 12 }}>{open ? '▲' : '▼'}</span>
      </button>

      {open && !result.is_hidden && (
        <div style={styles.resultBody}>
          <Detail label="Input" value={result.input} />
          <Detail label="Expected" value={result.expected} />
          {result.actual && <Detail label="Actual" value={result.actual} />}
          {result.error && <Detail label="Error" value={result.error} isError />}
        </div>
      )}
    </div>
  )
}

function Detail({ label, value, isError }: { label: string; value: string; isError?: boolean }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <span style={{ color: 'var(--text3)', fontSize: 11, display: 'block', marginBottom: 2 }}>{label}</span>
      <code style={{ color: isError ? 'var(--red)' : 'var(--text)', fontSize: 12, fontFamily: 'var(--mono)', wordBreak: 'break-all' }}>
        {value}
      </code>
    </div>
  )
}

function HintCard({ hint, onFeedback }: { hint: Hint; onFeedback: (id: string, h: boolean) => void }) {
  const [voted, setVoted] = useState<boolean | null>(null)
  const levelLabel = { 1: 'Nudge', 2: 'Specific hint', 3: 'Near-solution' }[hint.level] || 'Hint'

  const vote = (v: boolean) => {
    setVoted(v)
    onFeedback(hint.id, v)
  }

  return (
    <div style={styles.hintCard}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 500 }}>{levelLabel}</span>
      </div>
      <p style={{ fontSize: 13, lineHeight: 1.7, color: 'var(--text)' }}>{hint.content}</p>
      {voted === null && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button className="btn-ghost" onClick={() => vote(true)} style={{ fontSize: 11, padding: '4px 10px' }}>👍 Helpful</button>
          <button className="btn-ghost" onClick={() => vote(false)} style={{ fontSize: 11, padding: '4px 10px' }}>👎 Not helpful</button>
        </div>
      )}
      {voted !== null && (
        <p style={{ fontSize: 11, color: 'var(--text3)', marginTop: 8 }}>Thanks for the feedback.</p>
      )}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrap: { display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg)', overflow: 'hidden' },
  nav: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 20px', height: 52,
    background: 'var(--bg2)', borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  body: { display: 'flex', flex: 1, overflow: 'hidden' },
  left: { width: 340, overflowY: 'auto', padding: '20px', borderRight: '1px solid var(--border)', flexShrink: 0 },
  prose: { fontSize: 13, lineHeight: 1.8, color: 'var(--text)' },
  center: { flex: 1, overflow: 'hidden' },
  right: { width: 320, display: 'flex', flexDirection: 'column', borderLeft: '1px solid var(--border)', flexShrink: 0 },
  tabs: { display: 'flex', borderBottom: '1px solid var(--border)', flexShrink: 0 },
  tab: {
    flex: 1, padding: '12px 0', background: 'transparent', border: 'none',
    color: 'var(--text2)', fontSize: 13, cursor: 'pointer', borderBottom: '2px solid transparent',
  },
  tabActive: { color: 'var(--accent)', borderBottom: '2px solid var(--accent)' },
  panel: { flex: 1, overflowY: 'auto', padding: '12px' },
  resultRow: { marginBottom: 4, border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' },
  resultHeader: {
    display: 'flex', alignItems: 'center', gap: 10, width: '100%',
    background: 'var(--bg2)', padding: '10px 12px',
    border: 'none', cursor: 'pointer', color: 'var(--text)',
  },
  resultBody: { padding: '12px', background: 'var(--bg3)', borderTop: '1px solid var(--border)' },
  hintButtons: {
    background: 'var(--bg3)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '12px', marginBottom: 12,
  },
  hintCard: {
    background: 'var(--bg3)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '14px', marginBottom: 10,
  },
}
