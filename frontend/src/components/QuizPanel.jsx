import { useEffect, useRef, useState } from 'react'
import QuizView from './QuizView.jsx'

const FALLBACK_ERROR = 'We could not generate a quiz. Please try again.'

/**
 * Normalize generated display text for client-side contract validation.
 * @param {string} value
 * @returns {string}
 */
function normalizeDisplayText(value) {
  return value
    .normalize('NFKC')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim()
}

/**
 * Read a safe user-facing message from a failed quiz response.
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function errorMessage(response) {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string' && body.detail.trim()) {
      return body.detail
    }
  } catch {
    // The API may return an empty or non-JSON response for an upstream failure.
  }
  return `${FALLBACK_ERROR} (status ${response.status})`
}

/**
 * Validate the API payload and separate display-safe quiz data from its key.
 * @param {unknown} data
 * @returns {{quiz: {topic: string, questions: Array<{question: string, options: string[], citation: string}>}, answerKey: number[]}}
 * @throws {Error} When the payload violates the five-question quiz contract.
 */
function splitQuizResponse(data) {
  if (
    !data ||
    typeof data.topic !== 'string' ||
    !data.topic.trim() ||
    !Array.isArray(data.questions) ||
    data.questions.length !== 5
  ) {
    throw new Error('The quiz response was incomplete. Please try again.')
  }

  const questions = data.questions.map((item) => {
    const normalizedOptions = Array.isArray(item?.options)
      ? item.options.map((option) =>
          typeof option === 'string' ? normalizeDisplayText(option) : '',
        )
      : []
    if (
      !item ||
      typeof item.question !== 'string' ||
      !normalizeDisplayText(item.question) ||
      !Array.isArray(item.options) ||
      item.options.length !== 4 ||
      normalizedOptions.some((option) => !option) ||
      new Set(normalizedOptions).size !== normalizedOptions.length ||
      typeof item.citation !== 'string' ||
      !item.citation.trim() ||
      !Number.isInteger(item.correct_index) ||
      item.correct_index < 0 ||
      item.correct_index >= item.options.length
    ) {
      throw new Error('The quiz response was incomplete. Please try again.')
    }

    return {
      question: item.question,
      options: item.options,
      citation: item.citation,
    }
  })

  return {
    quiz: { topic: data.topic, questions },
    answerKey: data.questions.map((item) => item.correct_index),
  }
}

/** Own quiz generation, request lifecycle, local grading, and reset state. */
export default function QuizPanel() {
  const [topic, setTopic] = useState('')
  const [quiz, setQuiz] = useState(null)
  const [answerKey, setAnswerKey] = useState([])
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [quizVersion, setQuizVersion] = useState(0)
  const [announcement, setAnnouncement] = useState('')
  const requestController = useRef(null)
  const quizRegion = useRef(null)

  useEffect(() => {
    return () => requestController.current?.abort()
  }, [])

  useEffect(() => {
    if (quiz) quizRegion.current?.focus()
  }, [quiz, result])

  async function generateQuiz(event) {
    event.preventDefault()
    const requestedTopic = topic.trim()
    if (!requestedTopic || busy) return

    setBusy(true)
    setError('')
    setResult(null)
    setAnnouncement('')
    const controller = new AbortController()
    requestController.current = controller

    try {
      const response = await fetch('/api/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: requestedTopic }),
        signal: controller.signal,
      })
      if (!response.ok) {
        throw new Error(await errorMessage(response))
      }

      const { quiz: nextQuiz, answerKey: nextAnswerKey } = splitQuizResponse(
        await response.json(),
      )
      if (controller.signal.aborted) return
      setQuiz(nextQuiz)
      setAnswerKey(nextAnswerKey)
      setQuizVersion((version) => version + 1)
      setAnnouncement(`Quiz ready: ${nextQuiz.questions.length} questions.`)
    } catch (requestError) {
      if (controller.signal.aborted) return
      const message =
        requestError instanceof Error && !(requestError instanceof TypeError)
          ? requestError.message
          : FALLBACK_ERROR
      setError(message || FALLBACK_ERROR)
    } finally {
      if (requestController.current === controller) {
        requestController.current = null
        if (!controller.signal.aborted) setBusy(false)
      }
    }
  }

  function gradeQuiz(selections) {
    const feedback = selections.map((selection, index) => {
      const correctIndex = answerKey[index]
      if (selection === correctIndex) {
        return `Question ${index + 1}: Correct.`
      }

      const correctAnswer = quiz.questions[index].options[correctIndex]
      const punctuatedAnswer = /[.!?]$/.test(correctAnswer.trim())
        ? correctAnswer.trim()
        : `${correctAnswer.trim()}.`
      return `Question ${index + 1}: Not quite. The correct answer is ${punctuatedAnswer}`
    })

    const score = selections.filter(
      (selection, index) => selection === answerKey[index],
    ).length
    setResult({
      score,
      total: answerKey.length,
      feedback,
    })
    setAnnouncement(`Score: ${score} out of ${answerKey.length}.`)
  }

  function startNewQuiz() {
    setTopic('')
    setQuiz(null)
    setAnswerKey([])
    setResult(null)
    setError('')
    setAnnouncement('')
  }

  return (
    <main className="quiz-panel" aria-busy={busy}>
      <p className="sr-only" role="status" aria-live="polite">
        {announcement}
      </p>
      {quiz ? (
        <section
          className="quiz-session"
          ref={quizRegion}
          tabIndex={-1}
          aria-label={`Practice quiz: ${quiz.topic}`}
        >
          <QuizView
            key={quizVersion}
            quiz={quiz}
            onSubmit={gradeQuiz}
            result={result}
          />
          <div className="quiz-actions">
            <button type="button" className="quiz-secondary" onClick={startNewQuiz}>
              New quiz
            </button>
            <p>
              Answer checking happens in this browser; practice scores are not
              saved.
            </p>
          </div>
        </section>
      ) : (
        <section className="quiz-setup">
          <h2>Create a practice quiz</h2>
          <p>Choose a topic from the course materials.</p>
          <form className="quiz-form" onSubmit={generateQuiz}>
            <label htmlFor="quiz-topic">
              Topic
              <input
                id="quiz-topic"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                placeholder="For example, binary search"
                maxLength={200}
                disabled={busy}
                autoFocus
              />
            </label>
            <button type="submit" disabled={busy || !topic.trim()}>
              {busy ? 'Generating…' : 'Generate quiz'}
            </button>
          </form>
          {busy ? (
            <p className="quiz-status" role="status" aria-live="polite">
              Building a quiz from the course materials…
            </p>
          ) : null}
          {error ? (
            <p className="quiz-error" role="alert">
              {error}
            </p>
          ) : null}
        </section>
      )}
    </main>
  )
}
