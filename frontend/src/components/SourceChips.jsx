export default function SourceChips({ citations }) {
  return (
    <div className="sources" aria-label="Sources">
      {citations.map((id) => {
        const [file, section] = id.split('#')
        return (
          <span key={id} className="chip" title={id}>
            {file?.replace(/^lesson-\d+-/, '')} › {section?.replaceAll('-', ' ')}
          </span>
        )
      })}
    </div>
  )
}
