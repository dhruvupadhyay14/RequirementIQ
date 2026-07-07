import React from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

export default function Navbar() {
  const user = useAuthStore((state) => state.user)
  const clearAuth = useAuthStore((state) => state.clearAuth)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    clearAuth()
  }

  return (
    <header className="w-full border-b bg-white px-6 py-4 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-slate-900">RequirementIQ</p>
        <p className="text-sm text-slate-500">{user?.email}</p>
      </div>
      <div className="flex items-center gap-4">
        <Link className="text-sm text-slate-600 hover:text-slate-900" to="/profile">Profile</Link>
        <button className="rounded-lg border px-3 py-2 text-sm" onClick={handleLogout} type="button">Logout</button>
      </div>
    </header>
  )
}
