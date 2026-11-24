
import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

const initialQuests = [
  { id: 1, title: 'Workout for 30 minutes', reward: 50, done: false },
  { id: 2, title: 'Eat 100 grams of protein', reward: 30, done: false },
  { id: 3, title: 'Read for 20 minutes', reward: 30, done: false },
  { id: 4, title: 'Walk 8000 steps today', reward: 50, done: false }
]

const navigation = [
  { id: 'dashboard', label: 'Dashboard', icon: '⌂' },
  { id: 'quests', label: 'Quests', icon: '✓' },
  { id: 'wallet', label: 'Wallet', icon: '◈' },
  { id: 'achievements', label: 'Achievements', icon: '★' },
  { id: 'city', label: 'My City', icon: '▦' }
]

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }

  return data
}

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [authLoading, setAuthLoading] = useState(true)
  const [authMode, setAuthMode] = useState('login')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [token, setToken] = useState(
    () => localStorage.getItem('access_token')
  )

  const [user, setUser] = useState(null)
  const [coins, setCoins] = useState(0)
  const [walletLoading, setWalletLoading] = useState(false)
  const [transactions, setTransactions] = useState([])
  const [transactionsLoading, setTransactionsLoading] = useState(false)
  const [transactionError, setTransactionError] = useState('')

  const [quests, setQuests] = useState(initialQuests)
  const [activePage, setActivePage] = useState('dashboard')

  const completed = quests.filter((quest) => quest.done).length
  const progress = Math.round((completed / quests.length) * 100)

  async function loadUserData(accessToken) {
    const headers = {
      Authorization: `Bearer ${accessToken}`
    }

    const profile = await apiRequest('/api/auth/me', { headers })

    setUser(profile)
    setLoggedIn(true)

    setWalletLoading(true)
    setTransactionsLoading(true)
    setTransactionError('')

    try {
      const [wallet, transactionData] = await Promise.all([
        apiRequest('/api/wallet', { headers }),
        apiRequest('/api/wallet/transactions', { headers })
      ])

      setCoins(Number(wallet.balance))
      setTransactions(transactionData)
    } catch (err) {
      setTransactionError(err.message)
    } finally {
      setWalletLoading(false)
      setTransactionsLoading(false)
    }
  }

  // Restore the user's session when the page is refreshed.
  useEffect(() => {
    async function restoreSession() {
      const savedToken = localStorage.getItem('access_token')

      if (!savedToken) {
        setAuthLoading(false)
        return
      }

      try {
        setToken(savedToken)
        await loadUserData(savedToken)
      } catch {
        localStorage.removeItem('access_token')
        setToken(null)
        setUser(null)
        setLoggedIn(false)
      } finally {
        setAuthLoading(false)
      }
    }

    restoreSession()
  }, [])

  async function handleAuth(event) {
    event.preventDefault()

    setError('')
    setSuccess('')

    try {
      if (authMode === 'register') {
        await apiRequest('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            username,
            email,
            password
          })
        })
      }

      // Log in after registration, or directly when signing in.
      const loginData = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      const accessToken = loginData.access_token

      localStorage.setItem('access_token', accessToken)
      setToken(accessToken)

      await loadUserData(accessToken)

      setActivePage('dashboard')
      setSuccess('')
      setPassword('')
    } catch (err) {
      localStorage.removeItem('access_token')
      setToken(null)
      setUser(null)
      setLoggedIn(false)
      setError(err.message || 'Something went wrong. Please try again.')
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token')
    setToken(null)
    setUser(null)
    setLoggedIn(false)
    setEmail('')
    setPassword('')
    setUsername('')
    setError('')
    setSuccess('')
    setCoins(0)
    setActivePage('dashboard')
  }

  // Quest completion is still demo-only until a backend quest endpoint exists.
  function completeQuest(id) {
    const quest = quests.find((item) => item.id === id)
    if (!quest || quest.done) return

    setQuests((current) =>
      current.map((item) =>
        item.id === id ? { ...item, done: true } : item
      )
    )
  }

  function renderQuests() {
    return (
      <div className="quest-list">
        {quests.map((quest) => (
          <div className="quest" key={quest.id}>
            <div className={`quest-check ${quest.done ? 'completed-check' : ''}`}>
              {quest.done ? '✓' : '○'}
            </div>

            <div className="quest-info">
              <strong>{quest.title}</strong>
              <p>Reward: {quest.reward} coins</p>
            </div>

            <button
              className="quest-button"
              disabled={quest.done}
              onClick={() => completeQuest(quest.id)}
            >
              {quest.done ? 'Completed' : 'Complete'}
            </button>
          </div>
        ))}
      </div>
    )
  }

  function renderPage() {
    switch (activePage) {
      case 'dashboard':
        return (
          <>
            <section className="dashboard-card">
              <h2>Welcome back, {user?.username || 'User'}!</h2>
              <p>Here's an overview of your Lifestyle OS account.</p>
              <p>{user?.email}</p>
            </section>

            <section className="stats">
              <div className="stat-card">
                <p>Your wallet balance</p>
                <h2>◈ {walletLoading ? '...' : coins}</h2>
              </div>

              <div className="stat-card">
                <p>Demo quests completed</p>
                <h2>{completed}/{quests.length}</h2>
              </div>

              <div className="stat-card">
                <p>Demo daily progress</p>
                <h2>{progress}%</h2>
              </div>
            </section>

            <section className="dashboard-card">
              <div className="section-title">
                <div>
                  <h2>Recent Transactions</h2>
                  <p>Your latest wallet activity</p>
                </div>
              </div>

              {transactionsLoading ? (
                <p>Loading transactions...</p>
              ) : transactionError ? (
                <p role="alert">{transactionError}</p>
              ) : transactions.length === 0 ? (
                <p>No wallet activity yet.</p>
              ) : (
                <div className="transaction-list">
                  {transactions.slice(0, 3).map((transaction) => (
                    <div
                      className="transaction-item"
                      key={transaction.transaction_id}
                    >
                      <div>
                        <strong>{transaction.event_type}</strong>
                        <p>
                          {new Date(transaction.created_at).toLocaleString()}
                        </p>
                      </div>

                      <strong>
                        {Number(transaction.amount).toFixed(2)} coins
                      </strong>
                    </div>
                  ))}
                </div>
              )}

              <button
                className="quest-button"
                onClick={() => setActivePage('wallet')}
              >
                View Wallet
              </button>
            </section>

            <section className="dashboard-card">
              <div className="section-title">
                <div>
                  <h2>Daily quests</h2>
                  <p>Complete tasks and track your progress</p>
                </div>
                <span className="today-tag">DEMO</span>
              </div>

              {renderQuests()}
            </section>

            <section className="dashboard-card progress-card">
              <h2>Your journey</h2>
              <p>Every completed quest moves you forward</p>

              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <p className="progress-caption">
                {completed} of {quests.length} demo quests completed
              </p>
            </section>
          </>
        )

      case 'quests':
        return (
          <section className="dashboard-card">
            <div className="section-title">
              <div>
                <h2>All daily quests</h2>
                <p>Complete your daily objectives to earn rewards</p>
              </div>
              <span className="today-tag">{progress}% DONE</span>
            </div>

            {renderQuests()}

            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>

            <p className="progress-caption">
              {completed} of {quests.length} quests completed
            </p>
          </section>
        )

      case 'wallet':
        return (
          <section className="dashboard-card placeholder-card">
            <div className="placeholder-icon">◈</div>

            <h2>Your Wallet</h2>

            <p className="wallet-balance">
              {walletLoading ? 'Loading...' : `${coins} coins`}
            </p>

            <p>Your current balance from your Lifestyle OS account.</p>

            <div className="transaction-section">
              <h2>Transaction History</h2>

              {transactionsLoading ? (
                <p>Loading transactions...</p>
              ) : transactionError ? (
                <p role="alert">{transactionError}</p>
              ) : transactions.length === 0 ? (
                <p>No transactions yet. Your wallet activity will appear here.</p>
              ) : (
                <div className="transaction-list">
                  {transactions.map((transaction) => (
                    <div
                      className="transaction-item"
                      key={transaction.transaction_id}
                    >
                      <div>
                        <strong>{transaction.event_type}</strong>
                        <p>
                          {new Date(transaction.created_at).toLocaleString()}
                        </p>
                      </div>

                      <strong>
                        {Number(transaction.amount).toFixed(2)} coins
                      </strong>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )

      case 'achievements':
        return (
          <section className="dashboard-card placeholder-card">
            <div className="placeholder-icon">★</div>
            <h2>Achievements</h2>
            <p>Track milestones and celebrate your progress.</p>
            <p>Achievement tracking is coming next.</p>
          </section>
        )

      case 'city':
        return (
          <section className="dashboard-card placeholder-card">
            <div className="placeholder-icon">▦</div>
            <h2>Your City</h2>
            <p>Build and upgrade your city using coins earned from quests.</p>
            <p>Your city shop is coming next.</p>
          </section>
        )

      default:
        return null
    }
  }

  if (authLoading) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>Lifestyle OS</h1>
          <p className="subtitle">Restoring your session...</p>
        </section>
      </main>
    )
  }

  if (!loggedIn) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>Lifestyle OS</h1>
          <p className="subtitle">Helping you build better habits</p>

          <form onSubmit={handleAuth}>
            {authMode === 'register' && (
              <>
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  placeholder="Choose a username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  minLength={3}
                  maxLength={50}
                  pattern="[A-Za-z0-9_]+"
                  required
                />
              </>
            )}

            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />

            {error && <p role="alert" className="login-note">{error}</p>}
            {success && <p className="login-note">{success}</p>}

            <button className="primary-button" type="submit">
              {authMode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="login-note">
            {authMode === 'login'
              ? "Don't have an account?"
              : 'Already have an account?'}
          </p>

          <button
            type="button"
            className="logout-button"
            onClick={() => {
              setAuthMode(authMode === 'login' ? 'register' : 'login')
              setError('')
              setSuccess('')
            }}
          >
            {authMode === 'login' ? 'Create an account' : 'Sign in instead'}
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">L</div>
          <div>
            <strong>Lifestyle OS</strong>
            <p>Your life, leveled up.</p>
          </div>
        </div>

        <p className="nav-heading">MENU</p>

        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-coins">
            <span>◈</span>
            <div>
              <p>Your balance</p>
              <strong>{walletLoading ? 'Loading...' : `${coins} coins`}</strong>
            </div>
          </div>

          <button
            className="logout-button sidebar-logout"
            onClick={handleLogout}
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="main-content">
        <header className="dashboard-header">
          <div>
            <div className="small-brand">
              LIFESTYLE OS / {activePage.toUpperCase()}
            </div>
            <h1>
              {activePage === 'dashboard'
                ? 'Your Dashboard'
                : navigation.find((item) => item.id === activePage)?.label}
            </h1>
            <p>
              Welcome back, {user?.username || user?.email || 'User'}.
            </p>
          </div>
        </header>

        {renderPage()}
      </div>
    </main>
  )
}
