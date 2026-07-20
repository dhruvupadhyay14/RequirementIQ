import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'

type RequirementItem = { id: string; title: string; description: string; priority: string; confidence_score: number; category: string; status: 'pending' | 'approved' | 'rejected' }
type QuestionItem = { id: string; question: string; reason: string; status: 'pending' | 'answered' | 'dismissed' }
type MissingItem = { field: string; reason: string; severity: string }
type Analysis = { functional_requirements: RequirementItem[]; non_functional_requirements: RequirementItem[]; business_requirements: RequirementItem[]; technical_requirements: RequirementItem[]; questions: QuestionItem[]; missing_information: MissingItem[] }

const requirementQueryKey = (meetingId: string) => ['ai-requirements', meetingId]
const questionQueryKey = (meetingId: string) => ['ai-questions', meetingId]

export default function AIAnalysis() {
  const queryClient = useQueryClient()
  const [meetingId, setMeetingId] = useState('')
  const [missingInformation, setMissingInformation] = useState<MissingItem[]>([])
  const [error, setError] = useState('')
  const [editing, setEditing] = useState<RequirementItem | null>(null)

  useEffect(() => setMeetingId(new URLSearchParams(window.location.search).get('meeting_id') || ''), [])

  const requirementsQuery = useQuery({ queryKey: requirementQueryKey(meetingId), queryFn: async () => (await api.get<RequirementItem[]>(`/api/v1/ai/requirements/${meetingId}`)).data, enabled: Boolean(meetingId), retry: false })
  const questionsQuery = useQuery({ queryKey: questionQueryKey(meetingId), queryFn: async () => (await api.get<QuestionItem[]>(`/api/v1/ai/questions/${meetingId}`)).data, enabled: Boolean(meetingId), retry: false })
  const requirements = requirementsQuery.data || []
  const questions = questionsQuery.data || []

  const analysisMutation = useMutation({
    mutationFn: async () => (await api.post<Analysis>(`/api/v1/ai/analyze/${meetingId}`)).data,
    onSuccess: (result) => {
      queryClient.setQueryData(requirementQueryKey(meetingId), [...result.functional_requirements, ...result.non_functional_requirements, ...result.business_requirements, ...result.technical_requirements])
      queryClient.setQueryData(questionQueryKey(meetingId), result.questions)
      setMissingInformation(result.missing_information)
      setError('')
    },
    onError: () => setError('Analysis could not run. Ensure the meeting has a synced transcript, agenda, or description.'),
  })
  const requirementMutation = useMutation({ mutationFn: async ({ id, payload }: { id: string; payload: Partial<RequirementItem> }) => (await api.patch<RequirementItem>(`/api/v1/ai/requirements/${id}`, payload)).data, onSuccess: () => queryClient.invalidateQueries({ queryKey: requirementQueryKey(meetingId) }) })
  const questionMutation = useMutation({ mutationFn: async ({ id, status }: { id: string; status: QuestionItem['status'] }) => (await api.patch<QuestionItem>(`/api/v1/ai/questions/${id}`, { status })).data, onSuccess: () => queryClient.invalidateQueries({ queryKey: questionQueryKey(meetingId) }) })

  const groupedRequirements = useMemo(() => ['functional', 'non_functional', 'business', 'technical'].map((category) => ({ category, items: requirements.filter((item) => item.category === category) })), [requirements])
  const runAnalysis = () => { if (meetingId) analysisMutation.mutate() }
  const saveEdit = () => { if (editing) { requirementMutation.mutate({ id: editing.id, payload: { title: editing.title, description: editing.description, priority: editing.priority } }); setEditing(null) } }

  return <div className="space-y-6">
    <div><h1 className="text-2xl font-semibold">AI Requirement Analysis</h1><p className="mt-2 text-sm text-slate-600">Extract and validate discovery requirements from a Google Meet transcript.</p></div>
    <div className="rounded-lg border bg-white p-4"><label className="mb-2 block text-sm font-medium">Meeting ID</label><div className="flex gap-3"><input aria-label="Meeting ID" className="w-full rounded border px-3 py-2" value={meetingId} onChange={(event) => setMeetingId(event.target.value)} /><button className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-50" onClick={runAnalysis} disabled={!meetingId || analysisMutation.isPending}>{analysisMutation.isPending ? 'Analyzing…' : 'Analyze'}</button></div>{error && <p className="mt-2 text-sm text-red-600">{error}</p>}</div>
    <div className="space-y-5">{groupedRequirements.map(({ category, items }) => <section key={category} className="rounded-lg border bg-white p-4"><h2 className="text-lg font-semibold capitalize">{category.replace('_', ' ')} requirements</h2>{items.length === 0 ? <p className="mt-3 text-sm text-slate-500">No requirements extracted yet.</p> : <div className="mt-4 grid gap-3 lg:grid-cols-2">{items.map((item) => <article key={item.id} className="rounded border p-3"><div className="flex items-start justify-between gap-3"><strong>{item.title}</strong><span className="rounded bg-slate-100 px-2 py-1 text-xs">{item.status}</span></div><p className="mt-2 text-sm text-slate-600">{item.description}</p><p className="mt-2 text-xs text-slate-500">{item.priority} priority · {Math.round(item.confidence_score * 100)}% confidence</p><div className="mt-3 flex flex-wrap gap-2"><button className="rounded border px-2 py-1 text-sm" onClick={() => requirementMutation.mutate({ id: item.id, payload: { status: 'approved' } })}>Approve</button><button className="rounded border px-2 py-1 text-sm" onClick={() => requirementMutation.mutate({ id: item.id, payload: { status: 'rejected' } })}>Reject</button><button className="rounded border px-2 py-1 text-sm" onClick={() => setEditing(item)}>Edit</button></div></article>)}</div>}</section>)}</div>
    <div className="grid gap-6 lg:grid-cols-2"><section className="rounded-lg border bg-white p-4"><h2 className="text-lg font-semibold">Suggested questions</h2><div className="mt-4 space-y-3">{questions.map((item) => <article key={item.id} className="rounded border p-3"><p className="font-medium">{item.question}</p><p className="mt-1 text-sm text-slate-600">{item.reason}</p><div className="mt-3 flex items-center justify-between"><span className="text-xs uppercase text-slate-500">{item.status}</span>{item.status === 'pending' && <button className="rounded border px-2 py-1 text-sm" onClick={() => questionMutation.mutate({ id: item.id, status: 'answered' })}>Mark answered</button>}</div></article>)}</div></section><section className="rounded-lg border bg-white p-4"><h2 className="text-lg font-semibold">Missing information</h2><div className="mt-4 space-y-2">{missingInformation.map((item) => <article key={item.field} className="rounded border p-3 text-sm"><p className="font-medium">{item.field.replaceAll('_', ' ')}</p><p className="text-slate-600">{item.reason}</p></article>)}</div></section></div>
    {editing && <div className="fixed inset-0 grid place-items-center bg-black/30 p-4"><div className="w-full max-w-lg rounded-lg bg-white p-5"><h2 className="text-lg font-semibold">Edit requirement</h2><input className="mt-4 w-full rounded border p-2" value={editing.title} onChange={(event) => setEditing({ ...editing, title: event.target.value })} /><textarea className="mt-3 min-h-28 w-full rounded border p-2" value={editing.description} onChange={(event) => setEditing({ ...editing, description: event.target.value })} /><div className="mt-4 flex justify-end gap-2"><button className="rounded border px-3 py-2" onClick={() => setEditing(null)}>Cancel</button><button className="rounded bg-slate-900 px-3 py-2 text-white" onClick={saveEdit}>Save</button></div></div></div>}
  </div>
}
