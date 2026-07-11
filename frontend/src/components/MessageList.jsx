import SourceChips from './SourceChips.jsx'

export default function MessageList({ messages, busy }) {
  if (messages.length === 0 && !busy) {
    return (
      <div className="empty">
        Try: “Why does binary search need a sorted list?”
      </div>
    )
  }

  return (
    <div className="messages">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          <p>{message.text}</p>
          {message.citations?.length > 0 && (
            <SourceChips citations={message.citations} />
          )}
        </div>
      ))}
      {busy && <div className="message assistant thinking">Thinking…</div>}
    </div>
  )
}
