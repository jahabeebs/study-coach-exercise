/**
 * QuizView — renders a practice quiz and reports the student's answers.
 *
 * This component is complete and ready to use; it is not yet wired to any
 * data source (see TASKS.md).
 *
 * Props:
 *   quiz: {
 *     topic: string,
 *     questions: Array<{
 *       question: string,
 *       options: string[],          // exactly the choices to display, in order
 *       citation: string,           // section id supporting the question
 *     }>,
 *   }
 *   onSubmit(selections: number[]): void
 *       Called with the selected option index per question when the student
 *       submits. The parent owns grading and any result display.
 *   result: null | { score: number, total: number, feedback: string[] }
 *       When provided, shown instead of the submit button.
 */

import { useState } from 'react'

export default function QuizView({ quiz, onSubmit, result }) {
  const [selections, setSelections] = useState(
    () => new Array(quiz.questions.length).fill(null),
  )

  const complete = selections.every((s) => s !== null)

  return (
    <div className="quiz">
      <h2>Practice quiz: {quiz.topic}</h2>
      {quiz.questions.map((q, qi) => (
        <fieldset key={qi}>
          <legend>
            {qi + 1}. {q.question}
          </legend>
          {q.options.map((option, oi) => (
            <label key={oi}>
              <input
                type="radio"
                name={`q${qi}`}
                checked={selections[qi] === oi}
                onChange={() =>
                  setSelections((prior) =>
                    prior.map((s, i) => (i === qi ? oi : s)),
                  )
                }
                disabled={Boolean(result)}
              />
              {option}
            </label>
          ))}
          <span className="chip" title={q.citation}>
            source: {q.citation}
          </span>
        </fieldset>
      ))}

      {result ? (
        <div className="quiz-result">
          <h3>
            Score: {result.score} / {result.total}
          </h3>
          {result.feedback.map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      ) : (
        <button onClick={() => onSubmit(selections)} disabled={!complete}>
          Submit answers
        </button>
      )}
    </div>
  )
}
