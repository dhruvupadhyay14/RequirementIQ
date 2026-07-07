import React from 'react'
import { useAuthStore } from '../store/authStore'

export default function Profile() {
  const user = useAuthStore((state) => state.user)

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">Profile</h1>
      <p className="mt-2 text-sm text-slate-600">Manage your account details and workspace membership.</p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border p-4">
          <p className="text-sm text-slate-500">Name</p>
          <p className="mt-1 font-medium">{user?.first_name} {user?.last_name}</p>
        </div>
        <div className="rounded-xl border p-4">
          <p className="text-sm text-slate-500">Email</p>
          <p className="mt-1 font-medium">{user?.email}</p>
        </div>
      </div>
    </div>
  )
}
