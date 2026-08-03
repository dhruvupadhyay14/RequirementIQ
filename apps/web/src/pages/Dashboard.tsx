import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, LineChart, Line } from 'recharts'
import api from '../lib/api'

type Overview = Record<string, number>
type AIData = { requirement_categories: { name: string; value: number }[]; confidence_score_average: number; suggestion_acceptance_rate: number; charts: { project_status: { name: string; value: number }[]; meetings_per_month: { month: string; value: number }[]; project_completion: { name: string; value: number }[] } }
type FilterState = { project: string; meeting: string; dateFrom: string; dateTo: string; status: string; workspace: string; domain: string }

const colors = ['#0f172a', '#2563eb', '#0891b2', '#16a34a', '#f59e0b']
const labels: Record<string, string> = { total_projects: 'Total Projects', total_meetings: 'Total Meetings', total_requirements: 'Requirements', documents_generated: 'Documents', ai_suggestions_generated: 'AI Suggestions', ai_suggestions_accepted: 'Suggestions Accepted', ai_suggestions_rejected: 'Suggestions Rejected', requirement_completion_score: 'Completion Score', active_projects: 'Active Projects', completed_projects: 'Completed Projects' }

export default function Dashboard() {
  const [filters, setFilters] = useState<FilterState>({ project: '', meeting: '', dateFrom: '', dateTo: '', status: '', workspace: '', domain: '' })
  const params = useMemo(() => {
    const entries = Object.entries(filters).filter(([, value]) => value)
    return Object.fromEntries(entries)
  }, [filters])

  const overview = useQuery({
    queryKey: ['dashboard-overview', params],
    queryFn: async () => {
      const response = await api.get<Overview>('/api/v1/dashboard/overview', { params })
      return response.data
    },
  })
  const ai = useQuery({
    queryKey: ['dashboard-ai', params],
    queryFn: async () => {
      const response = await api.get<AIData>('/api/v1/dashboard/ai', { params })
      return response.data
    },
  })
  const activity = useQuery({
    queryKey: ['dashboard-activity', params],
    queryFn: async () => {
      const response = await api.get<{ type: string; title: string; at: string }[]>('/api/v1/dashboard/activity', { params })
      return response.data
    },
  })

  const exportReport = async (format: string) => {
    const response = await api.get('/api/v1/dashboard/export', { params: { ...params, format }, responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const link = Object.assign(document.createElement('a'), { href: url, download: `analytics.${format === 'excel' ? 'xlsx' : format}` })
    link.click()
    URL.revokeObjectURL(url)
  }

  if (overview.isLoading || ai.isLoading) {
    return <div className="grid gap-4 md:grid-cols-4">{Array.from({ length: 8 }, (_, index) => <div key={index} className="h-28 animate-pulse rounded-lg bg-slate-200" />)}</div>
  }

  const data = overview.data || {}
  const charts = ai.data?.charts
  return <div className="space-y-6"><div className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="text-2xl font-semibold">Analytics Dashboard</h1><p className="mt-1 text-sm text-slate-600">Projects, meetings, requirements, and AI performance for your workspace.</p></div><div className="flex gap-2">{['csv', 'excel', 'pdf'].map((format) => <button key={format} onClick={() => exportReport(format)} className="rounded border px-3 py-2 text-sm">Export {format.toUpperCase()}</button>)}</div></div><section className="rounded-lg border bg-white p-4 shadow-sm"><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">{[['project', 'Project'], ['meeting', 'Meeting'], ['status', 'Status'], ['domain', 'Domain']].map(([key, label]) => <label key={key} className="text-sm"><span className="mb-1 block text-slate-600">{label}</span><input className="w-full rounded border px-3 py-2" value={filters[key as keyof FilterState]} onChange={(event) => setFilters((current) => ({ ...current, [key]: event.target.value }))} /></label>)}<label className="text-sm"><span className="mb-1 block text-slate-600">Date from</span><input type="date" className="w-full rounded border px-3 py-2" value={filters.dateFrom} onChange={(event) => setFilters((current) => ({ ...current, dateFrom: event.target.value }))} /></label><label className="text-sm"><span className="mb-1 block text-slate-600">Date to</span><input type="date" className="w-full rounded border px-3 py-2" value={filters.dateTo} onChange={(event) => setFilters((current) => ({ ...current, dateTo: event.target.value }))} /></label></div></section><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">{Object.entries(data).map(([key, value]) => <article key={key} className="rounded-lg border bg-white p-4 shadow-sm"><p className="text-sm text-slate-500">{labels[key] || key}</p><p className="mt-2 text-2xl font-semibold">{key.includes('score') ? `${value}%` : value}</p></article>)}</section><section className="grid gap-6 lg:grid-cols-2"><Chart title="Project status"><PieChart><Pie data={charts?.project_status || []} dataKey="value" nameKey="name" outerRadius={90}>{(charts?.project_status || []).map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}</Pie><Tooltip /></PieChart></Chart><Chart title="Requirement categories"><BarChart data={ai.data?.requirement_categories || []}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#2563eb" /></BarChart></Chart><Chart title="Meetings per month"><LineChart data={charts?.meetings_per_month || []}><XAxis dataKey="month" /><YAxis /><Tooltip /><Line type="monotone" dataKey="value" stroke="#0891b2" strokeWidth={3} /></LineChart></Chart><Chart title="Project completion"><BarChart data={charts?.project_completion || []}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#16a34a" /></BarChart></Chart></section><section className="grid gap-6 lg:grid-cols-[1fr_2fr]"><div className="rounded-lg border bg-white p-4"><h2 className="font-semibold">AI quality</h2><p className="mt-4 text-sm text-slate-600">Average confidence <strong>{Math.round((ai.data?.confidence_score_average || 0) * 100)}%</strong></p><p className="mt-2 text-sm text-slate-600">Question acceptance <strong>{ai.data?.suggestion_acceptance_rate || 0}%</strong></p></div><div className="rounded-lg border bg-white p-4"><h2 className="font-semibold">Recent activity</h2><div className="mt-3 space-y-2">{activity.data?.map((item, index) => <div key={index} className="flex justify-between gap-3 rounded border p-2 text-sm"><span><strong className="capitalize">{item.type}</strong> · {item.title}</span><span className="text-slate-500">{new Date(item.at).toLocaleDateString()}</span></div>) || <p className="text-sm text-slate-500">No recent activity.</p>}</div></div></section></div>
}

function Chart({ title, children }: { title: string; children: React.ReactElement }) {
  return <section className="h-80 rounded-lg border bg-white p-4"><h2 className="font-semibold">{title}</h2><div className="mt-3 h-64"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div></section>
}
