import { useState } from 'react'
import ChatPanel from './components/ChatPanel.jsx'

export default function App() {
  const [tab, setTab] = useState('chat')

  return (
    <div className="app">
      <header>
        <h1>Study Coach</h1>
        <span className="course">CS-1010: Foundations of Computing</span>
        <nav>
          <button
            className={tab === 'chat' ? 'active' : ''}
            onClick={() => setTab('chat')}
          >
            Ask a question
          </button>
          <button
            className={tab === 'quiz' ? 'active' : ''}
            onClick={() => setTab('quiz')}
          >
            Practice quiz
          </button>
        </nav>
      </header>

      {tab === 'chat' ? (
        <ChatPanel />
      ) : (
        <div className="quiz-placeholder">
          <h2>Practice quizzes are coming soon</h2>
          <p>
            This tab is not wired up yet. A ready-made <code>QuizView</code>{' '}
            component lives in <code>src/components/QuizView.jsx</code> — see
            its header comment for the props it expects.
          </p>
        </div>
      )}
    </div>
  )
}
