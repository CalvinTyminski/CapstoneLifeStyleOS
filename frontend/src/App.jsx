import { useState } from 'react'
import './App.css'

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

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [coins, setCoins] = useState(100)
  const [quests, setQuests] = useState(initialQuests)
  const [activePage, setActivePage] = useState('dashboard')

  const completed = quests.filter((quest) => quest.done).length
  const progress = Math.round((completed / quests.length) * 100)

  function completeQuest(id) {
    const quest = quests.find((item) => item.id === id)
    if (!quest || quest.done) return

    setQuests((current) =>
      current.map((item) =>
        item.id === id ? { ...item, done: true } : item
      )
    )
    setCoins((current) => current + quest.reward)
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
            <section className="stats">
              <div className="stat-card">
                <p>Your coins</p>
                <h2>◈ {coins}</h2>
              </div>

              <div className="stat-card">
                <p>Quests completed</p>
                <h2>{completed}/{quests.length}</h2>
              </div>

              <div className="stat-card">
                <p>Daily progress</p>
                <h2>{progress}%</h2>
              </div>
            </section>

            <section className="dashboard-card">
              <div className="section-title">
                <div>
                  <h2>Daily quests</h2>
                  <p>Complete tasks and earn coins</p>
                </div>
                <span className="today-tag">TODAY</span>
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
                {completed} of {quests.length} daily quests completed
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
            <p className="wallet-balance">{coins} coins</p>
            <p>Your earned coins will be available to spend on city upgrades.</p>
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

  if (!loggedIn) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>Lifestyle OS</h1>
          <p className="subtitle">Helping you build better habits</p>

          <form
            onSubmit={(event) => {
              event.preventDefault()
              if (email.trim() && password.trim()) setLoggedIn(true)
            }}
          >
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
              required
            />

            <button className="primary-button" type="submit">
              Sign in
            </button>
          </form>

          <p className="login-note">Enter email and password</p>
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
              <strong>{coins} coins</strong>
            </div>
          </div>

          <button
            className="logout-button sidebar-logout"
            onClick={() => setLoggedIn(false)}
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="main-content">
        <header className="dashboard-header">
          <div>
            <div className="small-brand">LIFESTYLE OS / {activePage.toUpperCase()}</div>
            <h1>
              {activePage === 'dashboard'
                ? 'Your Dashboard'
                : navigation.find((item) => item.id === activePage)?.label}
            </h1>
            <p>Build better habits. Build your life.</p>
          </div>
        </header>

        {renderPage()}
      </div>
    </main>
  )
}
