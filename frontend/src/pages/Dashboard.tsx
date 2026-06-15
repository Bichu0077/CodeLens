import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../AuthContext'
import { ProblemListItem } from '../types'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [problems, setProblems] = useState<ProblemListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/problems/').then((res) => {
      setProblems(res.data)
      setLoading(false)
    })
  }, [])

  return (
    <div style={styles.wrap}>
      <nav style={styles.nav}>
        <span style={styles.navLogo}>CodeLens</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ color: 'var(--text2)', fontSize: 13 }}>@{user?.username}</span>
          <button className="btn-ghost" onClick={logout} style={{ padding: '6px 14px', fontSize: 13 }}>
            Sign out
          </button>
        </div>
      </nav>

      <main style={styles.main}>
        <div style={styles.header}>
          <h2 style={{ fontSize: 20, fontWeight: 600 }}>Problems</h2>
          <p style={{ color: 'var(--text2)', fontSize: 13, marginTop: 4 }}>
            Solve a problem and get real-time hints when you're stuck.
          </p>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text2)' }}>Loading…</p>
        ) : (
          <div style={styles.list}>
            {problems.map((p, i) => (
              <Link to={`/problem/${p.slug}`} key={p.id} style={{ textDecoration: 'none' }}>
                <div style={styles.row}>
                  <span style={{ color: 'var(--text3)', width: 32, flexShrink: 0, fontSize: 13 }}>
                    {i + 1}
                  </span>
                  <span style={{ flex: 1, color: 'var(--text)', fontWeight: 500 }}>{p.title}</span>
                  <span className={`badge ${p.difficulty}`}>{p.difficulty}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrap: { minHeight: '100vh', background: 'var(--bg)' },
  nav: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    height: 56,
    background: 'var(--bg2)',
    borderBottom: '1px solid var(--border)',
  },
  navLogo: { fontSize: 18, fontWeight: 600, color: 'var(--accent)' },
  main: { maxWidth: 720, margin: '0 auto', padding: '40px 24px' },
  header: { marginBottom: 28 },
  list: { display: 'flex', flexDirection: 'column', gap: 2 },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: 16,
    padding: '14px 16px',
    background: 'var(--bg2)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    transition: 'border-color 0.15s, background 0.15s',
    cursor: 'pointer',
  },
}
