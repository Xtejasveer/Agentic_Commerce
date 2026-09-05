import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Lock, User, AlertCircle, Loader2 } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleClientId, setGoogleClientId] = useState('')
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(r => r.json())
      .then(data => { if (data.user) setCurrentUser(data.user) })
      .catch(() => {})

    fetch('/api/auth/google/config')
      .then(r => r.json())
      .then(data => {
        if (data.configured && data.client_id) {
          setGoogleClientId(data.client_id)
          if (!window.google) {
            const script = document.createElement('script')
            script.src = 'https://accounts.google.com/gsi/client'
            script.async = true
            script.defer = true
            script.onload = () => initGoogleGIS(data.client_id)
            document.head.appendChild(script)
          } else {
            initGoogleGIS(data.client_id)
          }
        }
      })
      .catch(() => {})

    const params = new URLSearchParams(window.location.search)
    const urlError = params.get('error')
    if (urlError) {
      setError(urlError === 'oauth_failed'
        ? 'Google sign-in failed. Please try again.'
        : urlError === 'cancelled'
        ? 'Sign-in was cancelled.'
        : 'Authentication error. Please try again.')
    }
  }, [navigate])

  const initGoogleGIS = (clientId) => {
    if (!window.google?.accounts?.id) return
    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleGoogleCallback,
      auto_select: false,
    })
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-btn'),
      { theme: 'outline', size: 'large', width: '100%', text: 'continue_with', logo_alignment: 'left' }
    )
  }

  const handleGoogleCallback = async (googleResp) => {
    setLoading(true); setError('')
    try {
      const res = await fetch('/api/auth/google/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ credential: googleResp.credential }),
      })
      const data = await res.json()
      if (res.ok) navigate('/landing', { replace: true })
      else setError(data.detail || 'Google sign-in failed.')
    } catch { setError('Network error. Please try again.') }
    finally { setLoading(false) }
  }

  const handleGoogleRedirect = () => { window.location.href = '/api/auth/google/login' }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true)
    const endpoint = tab === 'login' ? '/api/auth/login' : '/api/auth/register'
    const body = tab === 'login'
      ? { email: form.email, password: form.password }
      : { email: form.email, password: form.password, name: form.name }
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) navigate('/landing', { replace: true })
      else setError(data.detail || 'Something went wrong.')
    } catch { setError('Network error. Please check your connection.') }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-[#faf8f5] flex">
      {/* Left panel — warm dark branding */}
      <div className="hidden lg:flex flex-col w-1/2 bg-[#1a120a] p-12 relative overflow-hidden">
        {/* Warm background orbs */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-orange-700/10 rounded-full blur-3xl pointer-events-none" />

        {/* Logo */}
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center shadow-lg shadow-[#c4622d]/30">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight text-[#fdf4ec]">Agentic Commerce</span>
        </div>

        {/* Tagline */}
        <div className="flex-1 flex flex-col justify-center relative z-10">
          <h2 className="text-4xl font-extrabold leading-tight mb-6 text-[#fdf4ec]">
            Your AI agents,
            <br />
            <span className="gradient-text">buying for you</span>
          </h2>
          <p className="text-[#9a7060] text-lg leading-relaxed mb-10">
            Sign in to manage your autonomous buyer agents, set spending mandates, and watch the AI handle procurement end-to-end.
          </p>

          <div className="space-y-4">
            {[
              { icon: '🤖', text: 'Create agents with custom mandates' },
              { icon: '🛡️', text: 'Real-time policy engine protection' },
              { icon: '📊', text: 'Live audit feed & KPI dashboard' },
              { icon: '💳', text: 'Integrated Razorpay payments' },
            ].map(item => (
              <div key={item.text} className="flex items-center gap-3">
                <span className="text-lg">{item.icon}</span>
                <span className="text-[#c9a882] text-sm">{item.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Mock terminal */}
        <div className="relative z-10 rounded-xl border border-[#3e2d1a] bg-[#251a10] p-4 font-mono text-xs space-y-1.5">
          <p className="text-[#5a4030]">// Agent running...</p>
          <p className="text-[#e59440]">agent.buy(<span className="text-emerald-400">"Sony earbuds ₹2499"</span>)</p>
          <p className="text-[#c9a882]">→ Policy: <span className="text-emerald-400">APPROVED</span></p>
          <p className="text-[#c9a882]">→ Razorpay: <span className="text-amber-400">order_OKxRz9 created</span></p>
          <p className="text-emerald-400">✓ Purchase complete</p>
        </div>
      </div>

      {/* Right panel — warm light auth form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-[#faf8f5]">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg text-[#1c1008]">Agentic Commerce</span>
          </div>

          {/* Card */}
          <div className="rounded-2xl border border-[#e8ddd0] bg-white shadow-sm p-8">
            {/* Active session banner if user is already logged in */}
            {currentUser && (
              <div className="mb-6 p-4 rounded-xl bg-[#fdf8f0] border border-[#e8ddd0] shadow-xs">
                <div className="flex items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2.5 min-w-0">
                    {currentUser.avatar_url ? (
                      <img src={currentUser.avatar_url} alt={currentUser.name} className="w-8 h-8 rounded-full ring-1 ring-[#e8ddd0]" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center text-white">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="text-[11px] text-[#7a5540]">Active Session</p>
                      <p className="text-sm font-semibold text-[#1c1008] truncate">{currentUser.name}</p>
                    </div>
                  </div>
                  <button
                    onClick={async () => {
                      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
                      setCurrentUser(null)
                    }}
                    className="text-xs text-[#b08070] hover:text-red-600 font-medium transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
                <button
                  onClick={() => navigate('/landing')}
                  className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-[#c4622d] hover:bg-[#a8521f] text-white text-xs font-semibold transition-all shadow-sm"
                >
                  Continue to Landing Page →
                </button>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 mb-8 p-1 rounded-xl bg-[#f5f0e8] border border-[#e8ddd0]">
              {['login', 'register'].map(t => (
                <button
                  key={t}
                  onClick={() => { setTab(t); setError('') }}
                  className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                    tab === t
                      ? 'bg-[#c4622d] text-white shadow-sm'
                      : 'text-[#7a5540] hover:text-[#1c1008]'
                  }`}
                >
                  {t === 'login' ? 'Sign In' : 'Create Account'}
                </button>
              ))}
            </div>

            <h1 className="text-2xl font-bold mb-1 text-[#1c1008]">
              {tab === 'login' ? 'Welcome back' : 'Get started'}
            </h1>
            <p className="text-sm text-[#7a5540] mb-8">
              {tab === 'login'
                ? 'Sign in to access your agents and dashboard'
                : 'Create an account to start building AI agents'}
            </p>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm mb-6">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Google Sign-In */}
            <div className="mb-6">
              {googleClientId ? (
                <div id="google-signin-btn" className="w-full" />
              ) : (
                <button
                  onClick={handleGoogleRedirect}
                  className="w-full flex items-center justify-center gap-3 py-2.5 px-4 rounded-lg border border-[#e8ddd0] hover:border-[#c4622d]/30 bg-white hover:bg-[#fdf8f0] text-[#5c3d28] text-sm font-medium transition-all"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>
              )}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1 h-px bg-[#e8ddd0]" />
              <span className="text-xs text-[#b08070]">or</span>
              <div className="flex-1 h-px bg-[#e8ddd0]" />
            </div>

            {/* Email/Password Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {tab === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#b08070]" />
                    <input
                      type="text"
                      required
                      value={form.name}
                      onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                      placeholder="John Smith"
                      className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#b08070]" />
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    placeholder="you@example.com"
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#b08070]" />
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={form.password}
                    onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all"
                  />
                </div>
                {tab === 'register' && (
                  <p className="text-xs text-[#b08070] mt-1">Minimum 8 characters</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-[#c4622d] hover:bg-[#a8521f] disabled:bg-[#c4622d]/50 text-white font-semibold text-sm transition-all shadow-md shadow-[#c4622d]/20 mt-2"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
                ) : tab === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </form>
          </div>

          <p className="text-center text-xs text-[#b08070] mt-6">
            By continuing, you agree to the terms of service.
          </p>

          <div className="text-center mt-3">
            <button
              onClick={() => navigate('/landing')}
              className="text-xs text-[#7a5540] hover:text-[#c4622d] font-medium transition-colors"
            >
              ← View Platform Overview & Features
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
