import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Zap, Shield, BarChart3, ArrowRight, ChevronRight, Store, ShoppingCart, Brain, Cpu, User, LogOut } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'LangGraph Buyer Agent',
    desc: 'Autonomous AI agent that searches products, validates against mandates, and executes purchases without human intervention.',
    color: 'from-amber-50 to-orange-50',
    border: 'border-amber-200',
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-700',
  },
  {
    icon: Shield,
    title: 'Merchant Policy Engine',
    desc: 'Real-time policy validation with spend limits, category controls, and automatic upsell suggestions on every transaction.',
    color: 'from-emerald-50 to-teal-50',
    border: 'border-emerald-200',
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-700',
  },
  {
    icon: Cpu,
    title: 'MCP Server Integration',
    desc: 'Model Context Protocol server exposing product search, purchase, and demand signal tools to AI agents over a standard protocol.',
    color: 'from-rose-50 to-pink-50',
    border: 'border-rose-200',
    iconBg: 'bg-rose-100',
    iconColor: 'text-rose-700',
  },
  {
    icon: BarChart3,
    title: 'Business Intelligence',
    desc: 'Live KPI dashboard tracking unmet demand signals, recovered sales, and upsell conversion rates in real-time.',
    color: 'from-orange-50 to-amber-50',
    border: 'border-orange-200',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-700',
  },
  {
    icon: Zap,
    title: 'Razorpay Payments',
    desc: 'Fully integrated headless payment execution. Agents create orders and initiate payments programmatically.',
    color: 'from-yellow-50 to-amber-50',
    border: 'border-yellow-200',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-700',
  },
  {
    icon: Store,
    title: 'Multi-Tenant Agents',
    desc: 'Each user creates and manages their own agents with custom mandates. Full isolation — your agents, your rules.',
    color: 'from-stone-50 to-orange-50',
    border: 'border-stone-200',
    iconBg: 'bg-stone-100',
    iconColor: 'text-stone-700',
  },
]

const steps = [
  { num: '01', title: 'Create an Agent', desc: 'Define your buyer agent with spending limits and allowed product categories.' },
  { num: '02', title: 'Set Mandates', desc: 'Configure per-transaction and daily budget caps with fine-grained category controls.' },
  { num: '03', title: 'Send a Request', desc: 'Tell your agent what to buy in plain language — it handles everything autonomously.' },
  { num: '04', title: 'Watch it Work', desc: 'Live audit feed shows every decision: search, validate, upsell, purchase.' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(r => r.json())
      .then(data => { if (data.user) setUser(data.user) })
      .catch(() => {})
  }, [])

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    setUser(null)
  }

  return (
    <div className="min-h-screen bg-[#faf8f5] text-[#1c1008] overflow-x-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-[#e8ddd0] bg-[#faf8f5]/90 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center shadow-sm">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight text-[#1c1008]">Agentic Commerce</span>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <div className="flex items-center gap-2 pr-1">
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.name} className="w-7 h-7 rounded-full ring-1 ring-[#e8ddd0]" />
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center text-white text-xs">
                      <User className="w-3.5 h-3.5" />
                    </div>
                  )}
                  <span className="text-sm font-medium text-[#5c3d28] hidden sm:block">{user.name}</span>
                </div>
                <button
                  onClick={() => navigate('/demo')}
                  className="px-4 py-2 text-sm font-semibold bg-[#c4622d] hover:bg-[#a8521f] text-white rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
                >
                  Launch Console
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={handleLogout}
                  className="p-2 text-[#7a5540] hover:text-red-600 transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 text-sm text-[#5c3d28] hover:text-[#1c1008] transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 text-sm font-medium bg-[#c4622d] hover:bg-[#a8521f] text-white rounded-lg transition-colors shadow-sm"
                >
                  Get Started
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6 overflow-hidden">
        {/* Warm background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-amber-200/30 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 left-1/4 w-[300px] h-[300px] bg-orange-200/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-10 right-1/4 w-[250px] h-[250px] bg-rose-200/15 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#c4622d]/30 bg-[#c4622d]/8 text-[#c4622d] text-xs font-medium mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-[#c4622d] live-dot" />
            AI-Native Commerce Platform
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-tight mb-6 text-[#1c1008]">
            Commerce that
            <br />
            <span className="gradient-text">runs itself</span>
          </h1>

          <p className="text-lg sm:text-xl text-[#7a5540] max-w-2xl mx-auto mb-10 leading-relaxed">
            Autonomous AI agents that search products, validate spending policies, and execute purchases —
            all while your merchant intelligence engine watches for upsell opportunities and demand signals.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => navigate(user ? '/demo' : '/login')}
              className="group flex items-center gap-2 px-8 py-3.5 bg-[#c4622d] hover:bg-[#a8521f] text-white font-semibold rounded-xl transition-all duration-200 shadow-md shadow-[#c4622d]/20"
            >
              {user ? 'Launch Demo Console' : 'Start Building'}
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/demo')}
              className="flex items-center gap-2 px-8 py-3.5 border border-[#e8ddd0] hover:border-[#c4622d]/40 text-[#5c3d28] hover:text-[#1c1008] font-semibold rounded-xl transition-all duration-200 bg-white hover:bg-[#fdf8f0]"
            >
              View Live Demo
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Hero visual — warm terminal */}
        <div className="mt-16 max-w-5xl mx-auto relative">
          <div className="rounded-2xl border border-[#e8ddd0] bg-[#1a120a] overflow-hidden shadow-xl shadow-[#c4622d]/10">
            {/* Terminal bar */}
            <div className="flex items-center gap-1.5 px-4 py-3 border-b border-[#3e2d1a] bg-[#251a10]">
              <div className="w-3 h-3 rounded-full bg-red-400/80" />
              <div className="w-3 h-3 rounded-full bg-amber-400/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-400/80" />
              <span className="ml-3 text-xs text-[#7d6050] font-mono">Agentic Commerce · Live Demo Console</span>
            </div>
            {/* Mock feed */}
            <div className="p-6 space-y-3 font-mono text-sm">
              <div className="flex items-start gap-3">
                <span className="text-[#5a4030] text-xs mt-0.5 shrink-0">09:14:02</span>
                <span className="text-[#c9a882]">Agent <span className="text-[#e59440]">agent-buyer-01</span> requested: <span className="text-emerald-400">"Buy me the best wireless earbuds under ₹3000"</span></span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#5a4030] text-xs mt-0.5 shrink-0">09:14:03</span>
                <span className="text-[#c9a882]">🔍 Searching catalog for <span className="text-amber-400">wireless earbuds</span> · 4 results found</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#5a4030] text-xs mt-0.5 shrink-0">09:14:04</span>
                <span className="text-[#c9a882]">📋 Policy check: <span className="text-[#e59440]">Sony WF-C700N ₹2,499</span> · ✅ Within limits</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#5a4030] text-xs mt-0.5 shrink-0">09:14:05</span>
                <span className="text-[#c9a882]">🎁 Upsell offered: <span className="text-rose-400">Anker cable ₹499</span> · Agent declined</span>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-[#5a4030] text-xs mt-0.5 shrink-0">09:14:06</span>
                <span className="text-emerald-400 font-semibold">✅ Purchase complete · Razorpay order ord_OKxRz9 created</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-6 bg-[#f5f0e8]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-[#1c1008]">Everything you need for agentic commerce</h2>
            <p className="text-[#7a5540] text-lg max-w-2xl mx-auto">
              A complete platform for AI-driven B2B procurement — from agent mandate creation to payment execution.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => {
              const Icon = f.icon
              return (
                <div
                  key={f.title}
                  className={`relative p-6 rounded-2xl bg-gradient-to-br ${f.color} border ${f.border} hover:scale-[1.02] transition-transform duration-200`}
                >
                  <div className={`w-10 h-10 rounded-xl ${f.iconBg} flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${f.iconColor}`} />
                  </div>
                  <h3 className="font-semibold text-[#1c1008] mb-2">{f.title}</h3>
                  <p className="text-sm text-[#7a5540] leading-relaxed">{f.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6 border-t border-[#e8ddd0]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-[#1c1008]">How it works</h2>
            <p className="text-[#7a5540] text-lg">From mandate to purchase in seconds</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <div key={step.num} className="relative text-center">
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-6 left-[calc(50%+24px)] w-[calc(100%-24px)] h-px border-t border-dashed border-[#e8ddd0]" />
                )}
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#c4622d]/10 to-[#e59440]/10 border border-[#c4622d]/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-[#c4622d] font-bold text-sm">{step.num}</span>
                </div>
                <h3 className="font-semibold text-[#1c1008] mb-2">{step.title}</h3>
                <p className="text-sm text-[#7a5540] leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-[#f5f0e8]">
        <div className="max-w-3xl mx-auto text-center">
          <div className="rounded-3xl border border-[#e8ddd0] bg-white p-12 shadow-sm">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 text-[#1c1008]">
              Ready to automate your commerce?
            </h2>
            <p className="text-[#7a5540] text-lg mb-8">
              Sign up free, create your first agent, and watch it shop for you.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={() => navigate(user ? '/demo' : '/login')}
                className="group flex items-center gap-2 px-8 py-3.5 bg-[#c4622d] hover:bg-[#a8521f] text-white font-semibold rounded-xl transition-all shadow-md shadow-[#c4622d]/20"
              >
                {user ? 'Launch Demo Console' : 'Create Your Account'}
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/demo')}
                className="px-8 py-3.5 border border-[#e8ddd0] hover:border-[#c4622d]/30 text-[#5c3d28] hover:text-[#1c1008] font-semibold rounded-xl transition-all bg-transparent"
              >
                {user ? 'Open Console' : 'Try Demo First'}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#e8ddd0] py-10 px-6 bg-[#faf8f5]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-[#5c3d28]">Agentic Commerce</span>
          </div>
          <p className="text-xs text-[#9a7060]">Built with LangGraph · FastAPI · MCP · Razorpay</p>
        </div>
      </footer>
    </div>
  )
}
