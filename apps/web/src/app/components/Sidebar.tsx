import React from 'react'
import { Link } from 'react-router-dom'

export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-white">
      <div className="p-4 text-lg font-semibold">RequirementIQ</div>
      <nav className="space-y-2 p-4">
        <Link className="block rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-100" to="/dashboard">Dashboard</Link>
        <Link className="block rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-100" to="/profile">Profile</Link>
      </nav>
    </aside>
  )
}
