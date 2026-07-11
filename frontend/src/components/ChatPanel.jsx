import { useState } from 'react'
import MessageList from './MessageList.jsx'

export default function ChatPanel() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)

  async function send(event) {
    event.preventDefault()
    const question = input.trim()
    if (!question || busy) return

    setInput('')
    setMessages((prior) => [...prior, { role: 'user', text: question }])
    setBusy(true)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question }),
      })
      if (!response.ok) throw new Error(`Request failed (${response.status})`)
      const data = await response.json()
      setMessages((prior) => [
        ...prior,
        { role: 'assistant', text: data.answer, citations: data.citations },
      ])
    } catch (error) {
      setMessages((prior) => [
        ...prior,
        { role: 'error', text: `Something went wrong: ${error.message}` },
      ])
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="chat">
      <MessageList messages={messages} busy={busy} />
      <form onSubmit={send}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about anything in the course materials…"
          aria-label="Your question"
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </main>
  )
}
