import { useState, useEffect } from 'react'
import axios from 'axios'

const NAV = [
  { id: 'dashboard',  label: 'Score Dashboard',  icon: '◈' },
  { id: 'simulation', label: 'Agent Simulation',  icon: '⟁' },
  { id: 'actions',    label: 'Action Plan',        icon: '◎' },
  { id: 'benchmark',  label: 'Competitor Index',   icon: '⊞' },
]

export default function Sidebar({ active, onNavigate }) {
  const [score, setScore] = useState(null)

  useEffect(() => {
    axios.get('/api/score').then(r => setScore(r.data.scores?.overall))
  }, [])

  const scoreColor = score == null ? '#4A6080' : score < 60 ? '#F0365A' : score < 75 ? '#F59E0B' : '#10D9A0'
  const barWidth   = score ? `${score}%` : '0%'

  return (
    <div style={{
      width: 224, minWidth: 224, background: '#080D18',
      borderRight: '1px solid #1A2438', display: 'flex',
      flexDirection: 'column', height: '100vh'
    }}>
      {/* Logo */}
      <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid #1A2438' }}>
        <div style={{ fontSize: 10, letterSpacing: 3, color: '#3B82F6', fontFamily: 'monospace', marginBottom: 4 }}>
          PLATFORM v2.1
        </div>
        <div style={{ fontSize: 22, fontWeight: 900, letterSpacing: -0.5 }}>
          Agent<span style={{ color: '#3B82F6' }}>Ready</span>
        </div>
      </div>

      {/* Client tag */}
      <div style={{ padding: '10px 20px', borderBottom: '1px solid #1A2438', background: '#0A1020' }}>
        <div style={{ fontSize: 9, letterSpacing: 2, color: '#4A6080', fontFamily: 'monospace', marginBottom: 3 }}>ANALYZING</div>
        <div style={{ fontSize: 13, fontWeight: 600 }}>Nexus Fashion Retail</div>
        <div style={{ fontSize: 11, color: '#8496B4', marginTop: 2 }}>SAP Commerce Cloud</div>
      </div>

      {/* Nav */}
      <nav style={{ padding: '12px 12px', flex: 1 }}>
        <div style={{ fontSize: 9, letterSpacing: 2, color: '#2A3F5F', fontFamily: 'monospace', padding: '8px 8px 6px', textTransform: 'uppercase' }}>
          Analytics
        </div>
        {NAV.map(item => {
          const isActive = active === item.id
          return (
            <button key={item.id} onClick={() => onNavigate(item.id)} style={{
              display: 'flex', alignItems: 'center', gap: 10, width: '100%',
              padding: '9px 12px', borderRadius: 8, marginBottom: 2,
              background: isActive ? 'rgba(59,130,246,0.08)' : 'transparent',
              border: isActive ? '1px solid rgba(59,130,246,0.2)' : '1px solid transparent',
              color: isActive ? '#60A5FA' : '#8496B4',
              fontSize: 13, fontWeight: 500, cursor: 'pointer',
              transition: 'all 0.15s',
            }}
              onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = '#111828'; e.currentTarget.style.color = '#EEF2FA' }}}
              onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#8496B4' }}}
            >
              <span style={{ fontSize: 14, width: 16, textAlign: 'center' }}>{item.icon}</span>
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Score mini */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid #1A2438', background: '#0A1020' }}>
        <div style={{ fontSize: 9, letterSpacing: 2, color: '#4A6080', fontFamily: 'monospace', marginBottom: 6 }}>CURRENT SCORE</div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 8 }}>
          <span style={{ fontFamily: 'monospace', fontSize: 32, fontWeight: 700, color: scoreColor }}>
            {score ?? '—'}
          </span>
          <span style={{ fontFamily: 'monospace', fontSize: 11, color: '#4A6080' }}>/100</span>
        </div>
        <div style={{ height: 4, background: '#1F2D45', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 2,
            width: barWidth,
            background: `linear-gradient(90deg, ${scoreColor}, ${scoreColor}CC)`,
            transition: 'width 1.2s ease'
          }} />
        </div>
        <div style={{ fontSize: 9, fontFamily: 'monospace', color: scoreColor, marginTop: 5 }}>
          {score == null ? 'LOADING...' : score < 60 ? '⚠ AGENT-INVISIBLE' : score < 75 ? '⚡ BELOW THRESHOLD' : '✓ AGENT-PREFERRED'}
        </div>
      </div>
    </div>
  )
}
