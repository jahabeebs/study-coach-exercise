import { useState } from 'react'
import ChatPanel from './components/ChatPanel.jsx'
import QuizPanel from './components/QuizPanel.jsx'

/** Render the Study Coach shell and its mutually exclusive chat/quiz views. */
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
            aria-pressed={tab === 'chat'}
          >
            Ask a question
          </button>
          <button
            className={tab === 'quiz' ? 'active' : ''}
            onClick={() => setTab('quiz')}
            aria-pressed={tab === 'quiz'}
          >
            Practice quiz
          </button>
        </nav>
      </header>

      {tab === 'chat' ? (
        <ChatPanel />
      ) : (
        <QuizPanel />
      )}
    </div>
  )
}
