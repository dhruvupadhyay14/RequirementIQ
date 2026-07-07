import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuthStore } from '../store/authStore'

export default function Register() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [form, setForm] = useState({
    company_name: '',
    industry: '',
    workspace_name: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    try {
      const response = await api.post('/auth/register', form)
      const { access_token, refresh_token, user } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      setAuth({ user, accessToken: access_token, refreshToken: refresh_token })
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to create account')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4">
      <div className="mx-auto w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-slate-900">Create your company workspace</h1>
          <p className="mt-2 text-sm text-slate-600">Set up your company, workspace, and admin account in minutes.</p>
        </div>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium">Company Name</label>
            <input className="w-full rounded-lg border px-3 py-2" name="company_name" value={form.company_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Industry</label>
            <input className="w-full rounded-lg border px-3 py-2" name="industry" value={form.industry} onChange={handleChange} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Workspace Name</label>
            <input className="w-full rounded-lg border px-3 py-2" name="workspace_name" value={form.workspace_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">First Name</label>
            <input className="w-full rounded-lg border px-3 py-2" name="first_name" value={form.first_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Last Name</label>
            <input className="w-full rounded-lg border px-3 py-2" name="last_name" value={form.last_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <input className="w-full rounded-lg border px-3 py-2" name="email" type="email" value={form.email} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Phone</label>
            <input className="w-full rounded-lg border px-3 py-2" name="phone" value={form.phone} onChange={handleChange} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <input className="w-full rounded-lg border px-3 py-2" name="password" type="password" value={form.password} onChange={handleChange} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Confirm Password</label>
            <input className="w-full rounded-lg border px-3 py-2" name="confirm_password" type="password" value={form.confirm_password} onChange={handleChange} required />
          </div>
          {error ? <p className="md:col-span-2 text-sm text-red-600">{error}</p> : null}
          <div className="md:col-span-2 flex items-center justify-between">
            <Link className="text-sm text-slate-600 hover:text-slate-900" to="/login">Already have an account?</Link>
            <button className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white" type="submit">Create account</button>
          </div>
        </form>
      </div>
    </div>
  )
}
