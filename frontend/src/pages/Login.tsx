import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const submit = async () => {
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/auth/login', { email, password })
      await login(res.data.access_token)
      navigate('/')
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <h1 style={styles.logo}>CodeLens</h1>
        <p style={styles.sub}>Sign in to your account</p>

        {error && <p style={styles.error}>{error}</p>}

        <div style={styles.field}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            placeholder="you@example.com"
          />
        </div>
        <div style={styles.field}>
          <label style={styles.label}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            placeholder="••••••••"
          />
        </div>

        <button className="btn-primary" onClick={submit} disabled={loading} style={{ width: '100%', marginTop: 8 }}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>

        <p style={{ textAlign: 'center', marginTop: 20, color: 'var(--text2)', fontSize: 13 }}>
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'var(--bg)',
  },
  card: {
    width: 380,
    background: 'var(--bg2)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: '36px 32px',
  },
  logo: {
    fontSize: 24,
    fontWeight: 600,
    color: 'var(--accent)',
    textAlign: 'center',
    marginBottom: 4,
  },
  sub: {
    color: 'var(--text2)',
    textAlign: 'center',
    marginBottom: 28,
    fontSize: 13,
  },
  field: { marginBottom: 16 },
  label: { display: 'block', marginBottom: 6, color: 'var(--text2)', fontSize: 13 },
  error: {
    background: 'var(--red-dim)',
    color: 'var(--red)',
    padding: '10px 14px',
    borderRadius: 8,
    marginBottom: 16,
    fontSize: 13,
  },
}
