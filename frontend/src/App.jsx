import { useState } from 'react'
import './App.css'

const initialQuests = [
  {id: 1, title: 'Workout for 30 minutes', reward: 50, done: false},
  {id: 2, title: 'Eat 100 grams of protein', reward: 30, done: false},
  {id: 3, title: 'Read for 20 minutes', reward: 30, done: false},
  {id: 4, title: 'Walk 8000 steps today', reward: 50, done: false}
]

const products= [
  {id: 1, name: 'Noir city pack', price: 200, color: 'black'},
  {id: 2, name: 'Cyberpunk city pack', price: 250, color: 'red'}
]

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [coins, setCoins] = useState(100)
  const [quests, setQuests] = useState(initialQuests)

  const completed = quests.filter((quest) => quest.done).length

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

  if (!loggedIn) {
    return (
      <main className="login-page">
        <section className="login-card">
          <h1>Lifestyle OS</h1>
          <p className="subtitle">Helping you built better habits</p>

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
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <div className="small-brand">Lifestyle OS</div>
          <h1>Your Dashboard</h1>
          <p>Build Your City</p>
        </div>
        <button className="logout-button" onClick={() => setLoggedIn(false)}>
          Sign out
        </button>
      </header>

      <section className="stats">
        <div className="stat-card">
          <p>Your coins</p>
          <h2>{coins}</h2>
        </div>
        <div className="stat-card">
          <p>Quests completed</p>
          <h2>{completed}/{quests.length}</h2>
        </div>
        <div className="stat-card">
          <p>Daily progress</p>
          <h2>{Math.round((completed / quests.length) * 100)}%</h2>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="section-title">
          <div>
            <h2>Daily quests</h2>
            <p>Complete a task to earn coins</p>
          </div>
          <span className="today-tag">TODAY</span>
        </div>

        <div className="quest-list">
          {quests.map((quest) => (
            <div className="quest" key={quest.id}>
              <div className="quest-check">
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
                {quest.done ? 'Done' : 'Complete'}
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-card progress-card">
        <div>
          <h2>Your journey</h2>
          <p>Every completed quest moves you forward</p>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(completed / quests.length) * 100}%` }}
          />
        </div>
        <p className="progress-caption">
          {completed} of {quests.length} daily quests completed
        </p>
      </section>
    </main>
  )
}