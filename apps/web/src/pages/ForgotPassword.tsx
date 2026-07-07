import React from 'react'
import { Link } from 'react-router-dom'

export default function ForgotPassword() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Forgot password</h1>
        <p className="mt-2 text-sm text-slate-600">This flow is currently a placeholder for the reset experience.</p>
        <div className="mt-6">
          <Link className="text-sm text-slate-600 hover:text-slate-900" to="/login">Back to sign in</Link>
        </div>
      </div>
    </div>
  )
}
