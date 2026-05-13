import { useKnowledge } from '../hooks/useKnowledge'
import { KnowledgeTable } from '../components/KnowledgeTable'

export function KnowledgePage() {
  const { entries, total, isLoading, mutate } = useKnowledge()

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700 }}>Learned Answers</h1>
        <span style={{ fontSize: 13, color: '#6b7280' }}>{total} entries in knowledge base</span>
      </div>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 16 }}>
        These answers are served automatically when callers ask matching questions.
        <strong> Served</strong> count shows how many times each entry has been used.
      </p>
      {isLoading ? (
        <p>Loading…</p>
      ) : (
        <KnowledgeTable entries={entries} onChanged={mutate} />
      )}
    </div>
  )
}
