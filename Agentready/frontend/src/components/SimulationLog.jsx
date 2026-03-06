import { useEffect, useRef, useState } from 'react'

const RED = '#F0365A', GRN = '#10D9A0', YLW = '#F59E0B', BLU = '#3B82F6'

const AGENT_COLORS = {
  'chatgpt-5':          BLU,
  'gemini-shop':        YLW,
  'perplexity-buy':     GRN,
  'alexa-plus':         '#A78BFA',
  'apple-intelligence': '#FF8C7A',
}

export default function SimulationLog() {
  const [rows, setRows]       = useState([])
  const [lost, setLost]       = useState(0)
  const [fails, setFails]     = useState(0)
  const [oks, setOks]         = useState(0)
  const [running, setRunning] = useState(false)
  const esRef = useRef(null)

  function start() {
    if (esRef.current) return
    setRunning(true)
    const es = new EventSource('/api/simulate/stream')
    esRef.current = es

    es.onmessage = (e) => {
      const ix = JSON.parse(e.data)
      setRows(prev => [ix, ...prev].slice(0, 120))
      if (ix.result === 'FAIL') {
        setFails(f => f + 1)
        setLost(l => l + ix.revenue_at_risk)
      } else {
        setOks(o => o + 1)
      }
    }
    es.onerror = () => { es.close(); esRef.current = null; setRunning(false) }
  }

  function stop() {
    if (esRef.current) { esRef.current.close(); esRef.current = null }
    setRunning(false)
  }

  function clear() {
    stop()
    setRows([]); setLost(0); setFails(0); setOks(0)
  }

  // Auto-start on mount
  useEffect(() => { start(); return () => stop() }, [])

  const total = fails + oks
  const rate  = total > 0 ? Math.round((oks / total) * 100) : 0

  return (
    <div>
      {/* Topbar */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(5,8,15,0.92)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid #1A2438', padding: '14px 28px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700 }}>Agent Simulation Log</div>
          <div style={{ fontSize: 11, color: '#8496B4', fontFamily: 'monospace', marginTop: 2 }}>
            Live SSE stream · Rule-based AI agents · Isolation Forest fraud detection
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={clear} style={{ padding: '7px 14px', fontSize: 12, fontWeight: 600, color: '#8496B4', background: 'transparent', border: '1px solid #1F2D45', borderRadius: 8, cursor: 'pointer' }}>
            Clear
          </button>
          <button onClick={running ? stop : start} style={{
            padding: '7px 16px', fontSize: 12, fontWeight: 600, borderRadius: 8, cursor: 'pointer',
            background: running ? '#1F2D45' : BLU, color: '#fff', border: 'none'
          }}>
            {running ? '■ Stop' : '▶ Start'}
          </button>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 20, background: 'rgba(16,217,160,0.08)', border: '1px solid rgba(16,217,160,0.2)', color: GRN, fontFamily: 'monospace', fontSize: 10, fontWeight: 700 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: running ? GRN : '#4A6080', transition: 'background 0.3s' }} />
            {running ? 'LIVE SSE' : 'PAUSED'}
          </span>
        </div>
      </div>

      <div style={{ padding: 28 }}>
        {/* Revenue hero */}
        <div style={{
          background: 'linear-gradient(135deg, #0C1220, #080D18)',
          border: '1px solid #1A2438', borderRadius: 20, padding: 24,
          display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 24,
          alignItems: 'center', marginBottom: 20
        }}>
          <div>
            <div style={{ fontSize: 9, letterSpacing: 2, color: 'rgba(240,54,90,0.7)', fontFamily: 'monospace', marginBottom: 6 }}>ESTIMATED REVENUE LOST</div>
            <div style={{ fontFamily: 'monospace', fontSize: 40, fontWeight: 700, color: RED, letterSpacing: -1 }}>
              ${lost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 11, color: '#8496B4', marginTop: 6 }}>
              Every FAIL row = revenue the retailer never knew they lost
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '0 24px', borderLeft: '1px solid #1A2438' }}>
            <div style={{ fontFamily: 'monospace', fontSize: 32, fontWeight: 700, color: RED }}>{fails}</div>
            <div style={{ fontSize: 11, color: '#8496B4', marginTop: 4 }}>Failed</div>
          </div>
          <div style={{ textAlign: 'center', padding: '0 24px', borderLeft: '1px solid #1A2438' }}>
            <div style={{ fontFamily: 'monospace', fontSize: 32, fontWeight: 700, color: GRN }}>{oks}</div>
            <div style={{ fontSize: 11, color: '#8496B4', marginTop: 4 }}>Succeeded</div>
          </div>
        </div>

        {/* Status bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
          <span style={{ fontSize: 11, color: '#8496B4', fontFamily: 'monospace', flex: 1 }}>
            {total} interactions · {fails} failed · {rate}% success rate
          </span>
          <span style={{
            padding: '4px 12px', borderRadius: 20, fontFamily: 'monospace', fontSize: 10, fontWeight: 700,
            background: rate < 50 ? 'rgba(240,54,90,0.1)' : 'rgba(16,217,160,0.1)',
            color: rate < 50 ? RED : GRN,
            border: `1px solid ${rate < 50 ? 'rgba(240,54,90,0.3)' : 'rgba(16,217,160,0.3)'}`
          }}>
            {rate}% SUCCESS RATE
          </span>
        </div>

        {/* Table */}
        <div style={{ background: '#080D18', border: '1px solid #1A2438', borderRadius: 12, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#0C1220' }}>
                {['Time', 'Agent', 'Action', 'Result', 'At Risk', 'Root Cause / Fraud'].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontFamily: 'monospace', fontSize: 9, letterSpacing: 2, color: '#4A6080', textTransform: 'uppercase', borderBottom: '1px solid #1A2438' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '48px', textAlign: 'center', color: '#4A6080', fontSize: 13 }}>
                    {running ? 'Waiting for first agent interaction...' : 'Press Start to begin simulation'}
                  </td>
                </tr>
              )}
              {rows.map((row, i) => (
                <tr key={i} className="fade-in" style={{ borderBottom: '1px solid #1A2438' }}>
                  <td style={{ padding: '10px 16px', fontFamily: 'monospace', fontSize: 10, color: '#4A6080', whiteSpace: 'nowrap' }}>
                    {new Date(row.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ padding: '10px 16px' }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 6,
                      background: '#111828', border: '1px solid #1F2D45',
                      borderRadius: 6, padding: '4px 8px', fontSize: 11, fontWeight: 600
                    }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: AGENT_COLORS[row.agent_id] || BLU }} />
                      {row.agent_name}
                    </span>
                  </td>
                  <td style={{ padding: '10px 16px', fontSize: 12, color: '#EEF2FA', maxWidth: 200 }}>
                    {row.action}
                  </td>
                  <td style={{ padding: '10px 16px' }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 5,
                      padding: '4px 10px', borderRadius: 6, fontFamily: 'monospace', fontSize: 10, fontWeight: 700,
                      background: row.result === 'FAIL' ? 'rgba(240,54,90,0.1)' : 'rgba(16,217,160,0.1)',
                      color: row.result === 'FAIL' ? RED : GRN,
                      border: `1px solid ${row.result === 'FAIL' ? 'rgba(240,54,90,0.3)' : 'rgba(16,217,160,0.3)'}`
                    }}>
                      {row.result === 'FAIL' ? '✕ FAILED' : '✓ OK'}
                    </span>
                  </td>
                  <td style={{ padding: '10px 16px', fontFamily: 'monospace', fontSize: 12, fontWeight: 700, color: row.result === 'FAIL' ? RED : GRN }}>
                    {row.result === 'FAIL' ? `$${row.revenue_at_risk.toFixed(0)}` : '—'}
                  </td>
                  <td style={{ padding: '10px 16px', fontSize: 11, maxWidth: 240 }}>
                    <span style={{ color: row.result === 'FAIL' ? 'rgba(240,54,90,0.8)' : '#4A6080' }}>
                      {row.root_cause}
                    </span>
                    {row.is_fraud_risk && (
                      <span style={{
                        marginLeft: 8, display: 'inline-flex', alignItems: 'center',
                        padding: '2px 6px', borderRadius: 4, fontSize: 9, fontWeight: 700, fontFamily: 'monospace',
                        background: 'rgba(245,158,11,0.1)', color: YLW, border: '1px solid rgba(245,158,11,0.3)'
                      }}>
                        ⚠ FRAUD {Math.round(row.fraud_score * 100)}%
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
