import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, LogOut, Plus, Send, Loader2, AlertCircle, CheckCircle2, XCircle,
         TrendingUp, TrendingDown, ShoppingCart, Zap, Activity, User, ChevronDown,
         X, Terminal, Sparkles } from 'lucide-react'

// ─── KPI Bar ─────────────────────────────────────────────────────────────────
function KpiBar({ stats }) {
  const cards = [
    {
      label: 'Unmet Demand',
      value: stats.unmet_demand_count,
      sub: stats.unmet_demand_revenue_inr > 0
        ? `₹${stats.unmet_demand_revenue_inr.toLocaleString('en-IN')} pipeline`
        : 'signals',
      icon: TrendingDown,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-200',
    },
    {
      label: 'Sales Recovered',
      value: stats.recovered_sales_count,
      sub: stats.recovered_sales_revenue_inr > 0
        ? `₹${stats.recovered_sales_revenue_inr.toLocaleString('en-IN')} recovered`
        : 'transactions',
      icon: TrendingUp,
      color: 'text-emerald-700',
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
    },
    {
      label: 'Upsells Accepted',
      value: stats.upsells_accepted,
      sub: `${stats.upsells_rejected} rejected`,
      icon: Zap,
      color: 'text-amber-700',
      bg: 'bg-amber-50',
      border: 'border-amber-200',
    },
  ]

  return (
    <div className="grid grid-cols-3 gap-3 mb-4">
      {cards.map(c => {
        const Icon = c.icon
        return (
          <div key={c.label} className={`rounded-xl p-3 ${c.bg} border ${c.border} flex items-center gap-3`}>
            <div className="w-8 h-8 rounded-lg bg-white border border-[#e8ddd0] flex items-center justify-center shrink-0 shadow-sm">
              <Icon className={`w-4 h-4 ${c.color}`} />
            </div>
            <div className="min-w-0">
              <div className={`text-xl font-bold ${c.color}`}>{c.value}</div>
              <div className="text-xs text-[#7a5540] truncate">{c.label}</div>
              <div className="text-xs text-[#b08070] truncate">{c.sub}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ─── Audit Event Card ─────────────────────────────────────────────────────────
function EventCard({ event }) {
  const config = {
    POLICY_APPROVED:    { icon: CheckCircle2, color: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200',  label: 'Policy Approved' },
    POLICY_REJECTED:    { icon: XCircle,      color: 'text-red-600',     bg: 'bg-red-50 border-red-200',          label: 'Policy Rejected' },
    PURCHASE_INITIATED: { icon: ShoppingCart, color: 'text-[#c4622d]',   bg: 'bg-orange-50 border-orange-200',    label: 'Purchase Initiated' },
    PURCHASE_SUCCESS:   { icon: CheckCircle2, color: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200',  label: 'Purchase Success' },
    PURCHASE_FAILED:    { icon: XCircle,      color: 'text-red-600',     bg: 'bg-red-50 border-red-200',          label: 'Purchase Failed' },
    DEMAND_SIGNAL:      { icon: TrendingDown, color: 'text-amber-700',   bg: 'bg-amber-50 border-amber-200',      label: 'Demand Signal' },
    SALE_RECOVERED:     { icon: TrendingUp,   color: 'text-teal-700',    bg: 'bg-teal-50 border-teal-200',        label: 'Sale Recovered' },
    UPSELL_OFFERED:     { icon: Zap,          color: 'text-orange-700',  bg: 'bg-orange-50 border-orange-200',    label: 'Upsell Offered' },
    UPSELL_ACCEPTED:    { icon: Zap,          color: 'text-orange-700',  bg: 'bg-orange-50 border-orange-200',    label: 'Upsell Accepted' },
    UPSELL_REJECTED:    { icon: Zap,          color: 'text-[#9a7060]',   bg: 'bg-stone-50 border-stone-200',      label: 'Upsell Rejected' },
  }

  const c = config[event.event_type] || { icon: Activity, color: 'text-[#9a7060]', bg: 'bg-stone-50 border-stone-200', label: event.event_type }
  const Icon = c.icon
  const ts = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''

  return (
    <div className={`event-card-enter rounded-lg border p-3 ${c.bg} mb-2`}>
      <div className="flex items-start gap-2.5">
        <Icon className={`w-4 h-4 mt-0.5 shrink-0 ${c.color}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className={`text-xs font-semibold ${c.color}`}>{c.label}</span>
            <span className="text-xs text-[#b08070] shrink-0">{ts}</span>
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-0.5">
            {event.agent_id && (
              <span className="text-xs text-[#9a7060]">
                Agent: <span className="text-[#5c3d28]">{event.agent_id}</span>
              </span>
            )}
            {event.product_id && (
              <span className="text-xs text-[#9a7060]">
                Product: <span className="text-[#5c3d28]">{event.product_id}</span>
              </span>
            )}
            {event.amount_inr && (
              <span className="text-xs text-[#9a7060]">
                Amount: <span className="text-[#5c3d28]">₹{Number(event.amount_inr).toLocaleString('en-IN')}</span>
              </span>
            )}
          </div>
          {event.policy_decision && (
            <p className="text-xs text-[#b08070] mt-1 truncate">{event.policy_decision}</p>
          )}
          {event.details && typeof event.details === 'string' && (
            <p className="text-xs text-[#b08070] mt-1 truncate">{event.details}</p>
          )}
          {event.razorpay_order_id && (
            <p className="text-xs text-[#c4a882] mt-0.5 font-mono">{event.razorpay_order_id}</p>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── New Agent Modal ──────────────────────────────────────────────────────────
function NewAgentModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    agent_id: '',
    max_single_txn_inr: 5000,
    max_daily_spend_inr: 15000,
    allowed_categories: [],
    requires_approval_above_inr: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const categories = [
    'chargers', 'cables', 'power_banks', 'earbuds', 'headphones',
    'speakers', 'smartwatches', 'keyboards', 'mice', 'storage',
    'cases', 'screen_protectors'
  ]

  const toggleCategory = (cat) => {
    setForm(f => ({
      ...f,
      allowed_categories: f.allowed_categories.includes(cat)
        ? f.allowed_categories.filter(c => c !== cat)
        : [...f.allowed_categories, cat]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    if (!form.agent_id.trim()) return setError('Agent ID is required.')
    if (form.allowed_categories.length === 0) return setError('Select at least one category.')
    setLoading(true)
    try {
      const res = await fetch('/api/mandates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          agent_id: form.agent_id,
          max_single_txn_inr: Number(form.max_single_txn_inr),
          max_daily_spend_inr: Number(form.max_daily_spend_inr),
          allowed_categories: form.allowed_categories,
          requires_approval_above_inr: form.requires_approval_above_inr ? Number(form.requires_approval_above_inr) : null,
        }),
      })
      const data = await res.json()
      if (res.ok) { onCreated(data); onClose() }
      else setError(data.detail || 'Failed to create agent.')
    } catch { setError('Network error.') }
    finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[#1c1008]/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md rounded-2xl border border-[#e8ddd0] bg-white shadow-2xl shadow-[#c4622d]/10">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#e8ddd0]">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-[#c4622d]" />
            <h2 className="font-semibold text-[#1c1008]">Create New Agent</h2>
          </div>
          <button onClick={onClose} className="text-[#9a7060] hover:text-[#1c1008] transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />{error}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Agent ID</label>
            <input
              type="text" required value={form.agent_id}
              onChange={e => setForm(f => ({ ...f, agent_id: e.target.value }))}
              placeholder="e.g. agent-procurement-01"
              className="w-full px-3 py-2 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Max Single Txn (₹)</label>
              <input
                type="number" required min="100" value={form.max_single_txn_inr}
                onChange={e => setForm(f => ({ ...f, max_single_txn_inr: e.target.value }))}
                className="w-full px-3 py-2 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[#7a5540] mb-1.5">Max Daily Spend (₹)</label>
              <input
                type="number" required min="100" value={form.max_daily_spend_inr}
                onChange={e => setForm(f => ({ ...f, max_daily_spend_inr: e.target.value }))}
                className="w-full px-3 py-2 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#7a5540] mb-2">Allowed Categories</label>
            <div className="flex flex-wrap gap-2">
              {categories.map(cat => (
                <button
                  key={cat} type="button" onClick={() => toggleCategory(cat)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                    form.allowed_categories.includes(cat)
                      ? 'bg-[#c4622d]/10 border border-[#c4622d]/40 text-[#c4622d]'
                      : 'bg-[#f5f0e8] border border-[#e8ddd0] text-[#7a5540] hover:text-[#1c1008]'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#7a5540] mb-1.5">
              Approval Required Above (₹) <span className="text-[#b08070]">optional</span>
            </label>
            <input
              type="number" min="0" value={form.requires_approval_above_inr}
              onChange={e => setForm(f => ({ ...f, requires_approval_above_inr: e.target.value }))}
              placeholder="Leave blank to disable"
              className="w-full px-3 py-2 rounded-lg bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all"
            />
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-[#c4622d] hover:bg-[#a8521f] disabled:opacity-50 text-white font-semibold text-sm transition-all shadow-md shadow-[#c4622d]/20"
          >
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating...</> : '+ Create Agent'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ─── Chat Item with Live Thinking Terminal & Collapsible Trace ──────────────
function ChatItem({ msg, onResolveUpsell }) {
  const [expanded, setExpanded] = useState(false)

  if (msg.role === 'user') {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-[80%] rounded-2xl rounded-br-md px-4 py-2.5 text-sm leading-relaxed bg-gradient-to-br from-[#c4622d] to-[#a8521f] text-white shadow-sm">
          {msg.content}
        </div>
      </div>
    )
  }

  const thoughts = msg.thoughts || []
  const hasThoughts = thoughts.length > 0
  const isThinking = msg.isThinking

  // Format message text with markdown styling (bold, code, links, headers, dividers)
  const renderFormattedContent = (content) => {
    if (!content) return null

    const lines = content.split('\n')
    return lines.map((line, lineIdx) => {
      const trimmed = line.trim()

      // Horizontal divider
      if (trimmed === '---') {
        return <hr key={lineIdx} className="my-3 border-[#e8ddd0]" />
      }

      // Header (### ...)
      if (trimmed.startsWith('### ')) {
        return (
          <h4 key={lineIdx} className="font-bold text-sm text-[#1c1008] mt-3 mb-1.5 flex items-center gap-1.5">
            {trimmed.replace(/^###\s+/, '')}
          </h4>
        )
      }

      // Bullet points (• ...)
      const isBullet = trimmed.startsWith('•') || trimmed.startsWith('-')
      const bulletText = isBullet ? trimmed.replace(/^[•\-]\s*/, '') : line

      // Render inline elements (bold, code, links)
      const renderInline = (text) => {
        const tokenRegex = /(https?:\/\/[^\s]+|\*\*[^*]+\*\*|`[^`]+`)/g
        const parts = text.split(tokenRegex)
        return parts.map((part, pIdx) => {
          if (!part) return null
          if (part.startsWith('http://') || part.startsWith('https://')) {
            return (
              <a
                key={pIdx}
                href={part}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#c4622d] underline hover:text-[#a8521f] font-medium break-all"
              >
                {part}
              </a>
            )
          }
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <strong key={pIdx} className="font-semibold text-[#1c1008]">
                {part.slice(2, -2)}
              </strong>
            )
          }
          if (part.startsWith('`') && part.endsWith('`')) {
            return (
              <code key={pIdx} className="px-1.5 py-0.5 rounded bg-[#f5f0e8] text-[#c4622d] font-mono text-xs">
                {part.slice(1, -1)}
              </code>
            )
          }
          return part
        })
      }

      if (isBullet) {
        return (
          <div key={lineIdx} className="flex items-start gap-2 py-0.5 text-xs text-[#5c3d28] leading-relaxed">
            <span className="text-[#c4622d] mt-0.5 shrink-0 select-none">•</span>
            <span>{renderInline(bulletText)}</span>
          </div>
        )
      }

      if (!trimmed) {
        return <div key={lineIdx} className="h-1.5" />
      }

      return (
        <p key={lineIdx} className="text-sm leading-relaxed text-[#3d2010]">
          {renderInline(line)}
        </p>
      )
    })
  }

  // Vertical Rope & Node Thought Process Renderer (Light Theme)
  const renderThoughtRope = (isLive = false) => (
    <div className="rounded-2xl border border-[#e8ddd0] bg-[#fdfbf9] overflow-hidden shadow-xs my-2.5">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-[#ebdcd0] bg-[#f7f1e9]/80">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-[#f0e4d6] flex items-center justify-center text-[#c4622d]">
            <Sparkles className="w-3 h-3" />
          </div>
          <span className="text-xs font-semibold text-[#543621]">Agent Reasoning Trail</span>
        </div>
        {isLive ? (
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#fcedde] border border-[#f5cbab] text-[10px] font-semibold text-[#c4622d]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#c4622d] animate-ping" />
            <span>Executing...</span>
          </div>
        ) : (
          <span className="text-[11px] font-medium text-[#8a6854]">
            {thoughts.length} {thoughts.length === 1 ? 'step' : 'steps'} executed
          </span>
        )}
      </div>

      {/* Rope & Nodes Timeline */}
      <div className="p-4 max-h-80 overflow-y-auto">
        <div className="relative pl-1">
          {thoughts.map((step, idx) => {
            const isLast = idx === thoughts.length - 1 && !isLive

            // Node colors based on step activity
            let nodeColor = 'border-[#c4622d] bg-white'
            let dotColor = 'bg-[#c4622d]'
            const text = step.text || ''

            if (text.includes('Searching') || text.includes('🔍')) {
              nodeColor = 'border-amber-500 bg-amber-50/70'
              dotColor = 'bg-amber-500'
            } else if (text.includes('Selected') || text.includes('🎯')) {
              nodeColor = 'border-[#c4622d] bg-[#fbf0ea]'
              dotColor = 'bg-[#c4622d]'
            } else if (text.includes('Recover') || text.includes('🔄')) {
              nodeColor = 'border-purple-500 bg-purple-50'
              dotColor = 'bg-purple-500'
            } else if (text.includes('Upsell') || text.includes('🎁')) {
              nodeColor = 'border-rose-500 bg-rose-50'
              dotColor = 'bg-rose-500'
            } else if (text.includes('complete') || text.includes('✅') || text.includes('Within limits')) {
              nodeColor = 'border-emerald-600 bg-emerald-50'
              dotColor = 'bg-emerald-600'
            } else if (text.includes('Rejected') || text.includes('failed') || text.includes('❌')) {
              nodeColor = 'border-red-500 bg-red-50'
              dotColor = 'bg-red-500'
            }

            return (
              <div key={idx} className="relative flex items-start gap-3.5 pb-4 group">
                {/* Continuous Vertical Rope Line */}
                {!isLast && (
                  <div className="absolute left-[11px] top-6 bottom-0 w-[2px] bg-[#dfd2c4] group-hover:bg-[#c4622d]/40 transition-colors" />
                )}

                {/* Circular Node `o` */}
                <div className={`relative z-10 w-6 h-6 rounded-full border-2 ${nodeColor} flex items-center justify-center shrink-0 shadow-2xs mt-0.5 transition-transform group-hover:scale-105`}>
                  <div className={`w-2 h-2 rounded-full ${dotColor}`} />
                </div>

                {/* Event Description */}
                <div className="flex-1 min-w-0 pt-0.5">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-[10px] font-mono font-medium text-[#8a6854] bg-[#ede3d5] px-1.5 py-0.5 rounded">
                      {step.time}
                    </span>
                  </div>
                  <div className="text-xs text-[#2c180b] font-medium leading-relaxed break-words">
                    {step.text}
                  </div>
                </div>
              </div>
            )
          })}

          {/* Pending Node (when live) */}
          {isLive && (
            <div className="relative flex items-start gap-3.5">
              <div className="relative z-10 w-6 h-6 rounded-full border-2 border-dashed border-[#c4622d] bg-[#fdf5ee] flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                <span className="w-2 h-2 rounded-full bg-[#c4622d] animate-ping" />
              </div>
              <div className="flex-1 pt-1">
                <div className="flex items-center gap-2 text-xs font-medium text-[#c4622d]">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-[#c4622d]" />
                  <span>
                    {thoughts.length === 0
                      ? 'Connecting to buyer agent & initializing tools...'
                      : 'Executing next pipeline step...'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex items-start gap-2.5 mb-4">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center mt-0.5 shrink-0 shadow-xs">
        <Bot className="w-3.5 h-3.5 text-white" />
      </div>

      <div className="flex-1 max-w-[85%] space-y-2">
        {/* Active thinking process (while running in backend) */}
        {isThinking && renderThoughtRope(true)}

        {/* Collapsed toggle button when completed */}
        {!isThinking && hasThoughts && (
          <div>
            <button
              onClick={() => setExpanded(!expanded)}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#f5f0e8] hover:bg-[#ede3d5] border border-[#e8ddd0] text-xs font-medium text-[#7a5540] hover:text-[#1c1008] transition-all shadow-2xs group cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#c4622d]" />
              <span>Thought process ({thoughts.length} steps)</span>
              <ChevronDown className={`w-3.5 h-3.5 text-[#b08070] transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
            </button>

            {/* Expanded rope & node timeline */}
            {expanded && renderThoughtRope(false)}
          </div>
        )}

        {/* Human Feedback / Upsell Approval Card */}
        {msg.pendingUpsell && (
          <div className="rounded-2xl border-2 border-[#c4622d]/40 bg-gradient-to-b from-[#fffcf8] to-[#faf5ee] p-4 shadow-sm space-y-3 event-card-enter">
            <div className="flex items-center justify-between border-b border-[#ebdcd0] pb-2">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-[#c4622d]/10 flex items-center justify-center text-[#c4622d]">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-[#1c1008]">Human Feedback Required</h4>
                  <p className="text-[10px] text-[#7a5540]">Merchant proposed an add-on bundle</p>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded-full bg-[#fde8d7] border border-[#f3c29f] text-[10px] font-bold text-[#c4622d]">
                Action Required
              </span>
            </div>

            {/* Product breakdown */}
            <div className="grid grid-cols-1 gap-1.5 text-xs bg-white p-3 rounded-xl border border-[#e8ddd0]">
              <div className="flex items-center justify-between text-[#5c3a21]">
                <span className="font-medium flex items-center gap-1.5">
                  <span>📦</span> Primary Product:
                </span>
                <span className="font-bold text-[#1c1008]">
                  {msg.pendingUpsell.primary_product?.name || 'Selected Product'} · ₹{(msg.pendingUpsell.primary_price || 0).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="flex items-center justify-between text-[#c4622d] border-t border-[#f5ece2] pt-1.5">
                <span className="font-medium flex items-center gap-1.5">
                  <span>🎁</span> Add-on Bundle:
                </span>
                <span className="font-bold">
                  {msg.pendingUpsell.addon_product?.name || 'Add-on Item'} · +₹{(msg.pendingUpsell.addon_price || 0).toLocaleString('en-IN')}
                </span>
              </div>
              <div className="flex items-center justify-between text-[#1c1008] border-t border-[#ebdcd0] pt-1.5 font-bold">
                <span>💰 Total with Bundle:</span>
                <span className="text-sm text-[#c4622d]">
                  ₹{(msg.pendingUpsell.total_with_addon || 0).toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            {/* Agent Pitch / Narration */}
            {msg.pendingUpsell.agent_narration && (
              <div className="p-2.5 rounded-lg bg-[#f7f0e6] text-[11px] text-[#6b4730] italic leading-relaxed border border-[#ebdcd0]/60">
                “{msg.pendingUpsell.agent_narration}”
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                onClick={() => onResolveUpsell?.(msg.pendingUpsell.action_id, true)}
                className="flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-[#c4622d] to-[#b35220] hover:brightness-105 text-white text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Accept Bundle (+₹{(msg.pendingUpsell.addon_price || 0).toLocaleString('en-IN')})</span>
              </button>

              <button
                type="button"
                onClick={() => onResolveUpsell?.(msg.pendingUpsell.action_id, false)}
                className="py-2 px-3 rounded-xl bg-white hover:bg-[#f5ece1] border border-[#e8ddd0] text-[#7a5540] hover:text-[#1c1008] text-xs font-semibold shadow-2xs flex items-center justify-center gap-1.5 transition-all cursor-pointer"
              >
                <XCircle className="w-3.5 h-3.5 text-red-500" />
                <span>Decline Add-on</span>
              </button>
            </div>
          </div>
        )}

        {/* Resolved choice indicator */}
        {msg.resolvedChoice && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#f5f0e8] border border-[#e8ddd0] text-[#7a5540]">
            {msg.resolvedChoice === 'accepted' ? (
              <>
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>You approved the upsell bundle</span>
              </>
            ) : (
              <>
                <XCircle className="w-3 h-3 text-amber-600" />
                <span>You declined the add-on · bought primary product only</span>
              </>
            )}
          </div>
        )}

        {/* Agent final response bubble */}
        {msg.content && (
          <div className="rounded-2xl rounded-bl-md bg-white border border-[#e8ddd0] px-4 py-3 text-sm leading-relaxed text-[#1c1008] shadow-sm whitespace-pre-line">
            {renderFormattedContent(msg.content)}
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Main Demo Page ───────────────────────────────────────────────────────────
export default function DemoPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [showAgentDropdown, setShowAgentDropdown] = useState(false)
  const [showNewAgentModal, setShowNewAgentModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState({
    unmet_demand_count: 0, unmet_demand_revenue_inr: 0,
    recovered_sales_count: 0, recovered_sales_revenue_inr: 0,
    upsells_accepted: 0, upsells_rejected: 0,
  })
  const [sseConnected, setSseConnected] = useState(false)
  const chatEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(r => r.json())
      .then(data => { if (!data.user) navigate('/login', { replace: true }); else setUser(data.user) })
      .catch(() => navigate('/login', { replace: true }))
  }, [navigate])

  useEffect(() => {
    if (!user) return
    fetch('/api/mandates', { credentials: 'include' })
      .then(r => r.json())
      .then(data => {
        const list = Array.isArray(data) ? data : []
        setAgents(list)
        if (list.length > 0) setSelectedAgent(list[0].agent_id)
      })
      .catch(() => {})
  }, [user])

  const loadStats = () => {
    fetch('/api/stats', { credentials: 'include' }).then(r => r.json()).then(setStats).catch(() => {})
  }

  useEffect(() => { if (user) loadStats() }, [user])

  useEffect(() => {
    if (!user) return
    const es = new EventSource('/api/audit/stream')
    es.onopen = () => setSseConnected(true)
    es.onerror = () => setSseConnected(false)
    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'connected' || data.type === 'heartbeat') return
        setEvents(prev => [data, ...prev].slice(0, 100))
        loadStats()
      } catch {}
    }
    return () => { es.close(); setSseConnected(false) }
  }, [user])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !selectedAgent || chatLoading) return
    const userMsg = input.trim()

    // If there is an active pending upsell approval, allow natural language text resolution
    const lastMsg = messages[messages.length - 1]
    if (lastMsg && lastMsg.pendingUpsell) {
      const lower = userMsg.toLowerCase()
      if (['yes', 'y', 'accept', 'ok', 'approve', 'sure', 'bundle', 'confirm'].some(w => lower.includes(w))) {
        setInput('')
        handleResolveUpsell(lastMsg.pendingUpsell.action_id, true)
        return
      } else if (['no', 'n', 'reject', 'decline', 'pass', 'skip', 'cancel', 'dont'].some(w => lower.includes(w))) {
        setInput('')
        handleResolveUpsell(lastMsg.pendingUpsell.action_id, false)
        return
      }
    }

    setInput('')

    // Append user message and an active agent message with empty thoughts
    setMessages(prev => [
      ...prev,
      { role: 'user', content: userMsg },
      { role: 'agent', content: '', thoughts: [], isThinking: true }
    ])
    setChatLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ agent_id: selectedAgent, message: userMsg, stream: true }),
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const data = JSON.parse(line)
            if (data.type === 'step') {
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last && last.role === 'agent') {
                  copy[copy.length - 1] = {
                    ...last,
                    thoughts: [...(last.thoughts || []), { time: data.time, text: data.text }]
                  }
                }
                return copy
              })
            } else if (data.type === 'upsell_approval_required') {
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last && last.role === 'agent') {
                  copy[copy.length - 1] = {
                    ...last,
                    isThinking: false,
                    pendingUpsell: data
                  }
                }
                return copy
              })
            } else if (data.type === 'done') {
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last && last.role === 'agent') {
                  copy[copy.length - 1] = {
                    ...last,
                    content: data.response || 'Task completed.',
                    isThinking: false
                  }
                }
                return copy
              })
            }
          } catch (e) {
            console.error('Error parsing line:', line, e)
          }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const copy = [...prev]
        const last = copy[copy.length - 1]
        if (last && last.role === 'agent') {
          copy[copy.length - 1] = {
            ...last,
            content: `❌ Error connecting to agent: ${err.message}`,
            isThinking: false
          }
        }
        return copy
      })
    } finally {
      setChatLoading(false)
      inputRef.current?.focus()
    }
  }

  // Handle Human-in-the-Loop decision on merchant upsell bundles
  const handleResolveUpsell = async (actionId, approved) => {
    if (!actionId || chatLoading) return
    setChatLoading(true)

    // Mark active agent message as resumed execution
    setMessages(prev => {
      const copy = [...prev]
      const last = copy[copy.length - 1]
      if (last && last.role === 'agent') {
        copy[copy.length - 1] = {
          ...last,
          isThinking: true,
          pendingUpsell: null,
          resolvedChoice: approved ? 'accepted' : 'declined'
        }
      }
      return copy
    })

    try {
      const res = await fetch('/api/chat/resolve-upsell', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ action_id: actionId, approved: approved }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const data = JSON.parse(line)
            if (data.type === 'step') {
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last && last.role === 'agent') {
                  copy[copy.length - 1] = {
                    ...last,
                    thoughts: [...(last.thoughts || []), { time: data.time, text: data.text }]
                  }
                }
                return copy
              })
            } else if (data.type === 'done') {
              setMessages(prev => {
                const copy = [...prev]
                const last = copy[copy.length - 1]
                if (last && last.role === 'agent') {
                  copy[copy.length - 1] = {
                    ...last,
                    content: data.response || 'Task completed.',
                    isThinking: false
                  }
                }
                return copy
              })
            }
          } catch (e) {
            console.error('Error parsing resolve line:', line, e)
          }
        }
      }
    } catch (err) {
      setMessages(prev => {
        const copy = [...prev]
        const last = copy[copy.length - 1]
        if (last && last.role === 'agent') {
          copy[copy.length - 1] = {
            ...last,
            content: `❌ Error processing upsell response: ${err.message}`,
            isThinking: false
          }
        }
        return copy
      })
    } finally {
      setChatLoading(false)
      loadStats()
      inputRef.current?.focus()
    }
  }

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    navigate('/login', { replace: true })
  }

  if (!user) return null
  const selectedAgentObj = agents.find(a => a.agent_id === selectedAgent)

  return (
    <div className="h-screen bg-[#faf8f5] flex flex-col overflow-hidden">
      {/* Top Nav — warm light */}
      <header className="flex items-center justify-between px-4 h-14 border-b border-[#e8ddd0] bg-white shadow-sm shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/demo')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-sm text-[#1c1008] hidden sm:block">VendIQ</span>
          </button>
          <div className="h-4 w-px bg-[#e8ddd0] hidden sm:block" />
          <span className="text-xs text-[#b08070] hidden sm:block">Live Demo Console</span>
          <button
            onClick={() => navigate('/landing')}
            className="text-xs text-[#7a5540] hover:text-[#c4622d] font-medium transition-colors ml-2 hidden md:block"
          >
            Overview
          </button>
        </div>

        <div className="flex items-center gap-1.5">
          {sseConnected ? (
            <><span className="w-1.5 h-1.5 rounded-full bg-emerald-500 live-dot" /><span className="text-xs text-emerald-600 hidden sm:block">Live</span></>
          ) : (
            <><span className="w-1.5 h-1.5 rounded-full bg-red-400" /><span className="text-xs text-red-500 hidden sm:block">Disconnected</span></>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-[#f5f0e8] transition-colors"
          >
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.name} className="w-7 h-7 rounded-full ring-1 ring-[#e8ddd0]" />
            ) : (
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#c4622d] to-[#e59440] flex items-center justify-center">
                <User className="w-3.5 h-3.5 text-white" />
              </div>
            )}
            <span className="text-sm text-[#5c3d28] hidden sm:block">{user.name}</span>
            <ChevronDown className="w-3.5 h-3.5 text-[#b08070] hidden sm:block" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 top-full mt-1 w-48 rounded-xl border border-[#e8ddd0] bg-white shadow-lg z-50">
              <div className="p-3 border-b border-[#e8ddd0]">
                <p className="text-sm font-medium text-[#1c1008] truncate">{user.name}</p>
                <p className="text-xs text-[#b08070] truncate">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors rounded-b-xl"
              >
                <LogOut className="w-4 h-4" />Sign Out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* KPI Bar */}
      <div className="px-4 pt-4 shrink-0">
        <KpiBar stats={stats} />
      </div>

      {/* Main split panel */}
      <div className="flex-1 flex gap-4 px-4 pb-4 overflow-hidden min-h-0">

        {/* Left: Buyer Console */}
        <div className="flex-1 flex flex-col rounded-xl border border-[#e8ddd0] bg-white shadow-sm overflow-hidden min-w-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#e8ddd0] bg-[#faf8f5] shrink-0">
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-4 h-4 text-[#c4622d]" />
              <span className="text-sm font-semibold text-[#1c1008]">Buyer Console</span>
            </div>

            <div className="flex items-center gap-2">
              <div className="relative">
                <button
                  onClick={() => setShowAgentDropdown(!showAgentDropdown)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-[#e8ddd0] hover:border-[#c4622d]/40 text-xs font-medium text-[#5c3d28] transition-colors shadow-sm"
                >
                  <Bot className="w-3.5 h-3.5 text-[#c4622d]" />
                  <span className="max-w-[140px] truncate">{selectedAgent || 'Select agent'}</span>
                  <ChevronDown className="w-3 h-3 text-[#b08070]" />
                </button>

                {showAgentDropdown && (
                  <div className="absolute right-0 top-full mt-1 w-56 rounded-xl border border-[#e8ddd0] bg-white shadow-lg z-40">
                    {agents.length === 0 ? (
                      <p className="px-3 py-3 text-xs text-[#b08070]">No agents yet. Create one!</p>
                    ) : (
                      agents.map(a => (
                        <button
                          key={a.agent_id}
                          onClick={() => { setSelectedAgent(a.agent_id); setShowAgentDropdown(false) }}
                          className={`w-full text-left px-3 py-2.5 text-xs hover:bg-[#faf8f5] transition-colors first:rounded-t-xl last:rounded-b-xl ${
                            selectedAgent === a.agent_id ? 'text-[#c4622d]' : 'text-[#5c3d28]'
                          }`}
                        >
                          <div className="font-medium">{a.agent_id}</div>
                          <div className="text-[#b08070] mt-0.5">₹{a.max_single_txn_inr.toLocaleString('en-IN')} / txn</div>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>

              <button
                onClick={() => setShowNewAgentModal(true)}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#c4622d]/10 hover:bg-[#c4622d]/20 border border-[#c4622d]/30 text-[#c4622d] text-xs font-medium transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />New
              </button>
            </div>
          </div>

          {selectedAgentObj && (
            <div className="flex items-center gap-3 px-4 py-2 bg-[#f5f0e8]/60 border-b border-[#e8ddd0] text-xs text-[#b08070] shrink-0">
              <span>Limit: <span className="text-[#7a5540]">₹{selectedAgentObj.max_single_txn_inr.toLocaleString('en-IN')}</span></span>
              <span className="text-[#e8ddd0]">·</span>
              <span>Daily: <span className="text-[#7a5540]">₹{selectedAgentObj.max_daily_spend_inr.toLocaleString('en-IN')}</span></span>
              <span className="text-[#e8ddd0]">·</span>
              <span>Categories: <span className="text-[#7a5540]">{selectedAgentObj.allowed_categories?.join(', ')}</span></span>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 bg-[#faf8f5]/40">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-14 h-14 rounded-2xl bg-[#c4622d]/10 border border-[#c4622d]/20 flex items-center justify-center mb-4">
                  <Bot className="w-7 h-7 text-[#c4622d]" />
                </div>
                <h3 className="font-semibold text-[#3d2010] mb-2">Buyer Agent Ready</h3>
                <p className="text-sm text-[#9a7060] max-w-xs leading-relaxed">
                  Tell your agent what to buy. It will search the catalog, validate against your mandate, and execute the purchase.
                </p>
                <div className="mt-6 space-y-2">
                  {[
                    '"Buy me Sony earbuds under ₹3000"',
                    '"Get me a 45W fast charger"',
                    '"I need a USB-C cable"',
                  ].map(s => (
                    <button
                      key={s}
                      onClick={() => setInput(s.replace(/"/g, ''))}
                      className="block w-full text-left px-3 py-2 rounded-lg bg-white hover:bg-[#fdf8f0] border border-[#e8ddd0] hover:border-[#c4622d]/30 text-xs text-[#7a5540] hover:text-[#3d2010] transition-all shadow-sm"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((m, i) => (
                  <ChatItem
                    key={i}
                    msg={m}
                    onResolveUpsell={handleResolveUpsell}
                  />
                ))}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-[#e8ddd0] bg-white shrink-0">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) handleSend() }}
                placeholder={selectedAgent ? `Ask ${selectedAgent} to buy something...` : 'Select an agent first'}
                disabled={!selectedAgent || chatLoading}
                className="flex-1 px-4 py-2.5 rounded-xl bg-[#faf8f5] border border-[#e8ddd0] focus:border-[#c4622d] focus:ring-1 focus:ring-[#c4622d]/20 text-sm text-[#1c1008] placeholder-[#b08070] outline-none transition-all disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || !selectedAgent || chatLoading}
                className="px-3 py-2.5 rounded-xl bg-[#c4622d] hover:bg-[#a8521f] disabled:bg-[#c4622d]/30 disabled:cursor-not-allowed text-white transition-all shadow-sm"
              >
                {chatLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        {/* Right: Policy Engine Feed */}
        <div className="w-80 xl:w-96 flex flex-col rounded-xl border border-[#e8ddd0] bg-white shadow-sm overflow-hidden shrink-0">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#e8ddd0] bg-[#faf8f5] shrink-0">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#c4622d]" />
              <span className="text-sm font-semibold text-[#1c1008]">Policy Engine Feed</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${sseConnected ? 'bg-emerald-500 live-dot' : 'bg-red-400'}`} />
              <span className="text-xs text-[#b08070]">{sseConnected ? 'Live' : 'Offline'}</span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 bg-[#faf8f5]/40">
            {events.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center px-4">
                <Activity className="w-8 h-8 text-[#e8ddd0] mb-3" />
                <p className="text-sm text-[#b08070]">Policy engine events will appear here in real-time.</p>
              </div>
            ) : (
              events.map((event, i) => <EventCard key={event.id || i} event={event} />)
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showNewAgentModal && (
        <NewAgentModal
          onClose={() => setShowNewAgentModal(false)}
          onCreated={(data) => {
            fetch('/api/mandates', { credentials: 'include' })
              .then(r => r.json())
              .then(list => {
                const arr = Array.isArray(list) ? list : []
                setAgents(arr)
                setSelectedAgent(data.agent_id)
              })
              .catch(() => {})
          }}
        />
      )}

      {(showAgentDropdown || showUserMenu) && (
        <div className="fixed inset-0 z-30" onClick={() => { setShowAgentDropdown(false); setShowUserMenu(false) }} />
      )}
    </div>
  )
}
