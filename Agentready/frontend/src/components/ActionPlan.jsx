import { useEffect, useState } from 'react'
import axios from 'axios'

const RED = '#F0365A', YLW = '#F59E0B', GRN = '#10D9A0', BLU = '#3B82F6'

const PRIORITY = {
  CRITICAL: { bg: 'rgba(240,54,90,0.08)',  color: RED, border: 'rgba(240,54,90,0.3)' },
  HIGH:     { bg: 'rgba(245,158,11,0.08)', color: YLW, border: 'rgba(245,158,11,0.3)' },
  MEDIUM:   { bg: 'rgba(59,130,246,0.08)', color: BLU, border: 'rgba(59,130,246,0.3)' },
}

export default function ActionPlan() {
  const [data, setData] = useState(null)

  useEffect(() => { axios.get('/api/actions').then(r => setData(r.data)) }, [])

  if (!data) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#4A6080' }}>Loading action plan...</div>

  const { actions, roi_summary } = data

  return (
    <div>
      <div style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(5,8,15,0.92)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid #1A2438', padding: '14px 28px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700 }}>Action Plan</div>
          <div style={{ fontSize: 11, color: '#8496B4', fontFamily: 'monospace', marginTop: 2 }}>
            Ranked by annual revenue recovery · Live failure counts from simulation
          </div>
        </div>
        <span style={{ padding: '6px 14px', borderRadius: 20, background: 'rgba(16,217,160,0.08)', border: '1px solid rgba(16,217,160,0.2)', color: GRN, fontFamily: 'monospace', fontSize: 10, fontWeight: 700 }}>
          Total Recovery: ${(roi_summary.total_annual_recovery / 1e6).toFixed(2)}M / yr
        </span>
      </div>

      <div style={{ padding: 28 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
          {actions.map(a => {
            const ps = PRIORITY[a.priority] || PRIORITY.MEDIUM
            return (
              <div key={a.rank} style={{
                background: '#080D18',
                border: `1px solid ${a.priority === 'CRITICAL' ? 'rgba(240,54,90,0.35)' : '#1A2438'}`,
                borderRadius: 20, padding: 20,
                display: 'flex', flexDirection: 'column',
                transition: 'transform 0.15s',
              }}>
                {/* Header badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span style={{ padding: '4px 10px', borderRadius: 6, fontFamily: 'monospace', fontSize: 9, fontWeight: 700, background: ps.bg, color: ps.color, border: `1px solid ${ps.border}` }}>
                    #{a.rank} {a.priority}
                  </span>
                  <span style={{ padding: '4px 10px', borderRadius: 6, fontFamily: 'monospace', fontSize: 9, background: 'rgba(255,255,255,0.04)', color: '#4A6080', border: '1px solid #1A2438' }}>
                    {a.effort} · {a.weeks}wk
                  </span>
                </div>

                <div style={{ fontSize: 14, fontWeight: 700, color: '#EEF2FA', marginBottom: 8, lineHeight: 1.4 }}>{a.title}</div>
                <div style={{ fontSize: 12, color: '#8496B4', lineHeight: 1.6, marginBottom: 12, flex: 1 }}>{a.description}</div>

                {/* Recovery */}
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 12 }}>
                  <span style={{ fontFamily: 'monospace', fontSize: 9, color: '#4A6080', textTransform: 'uppercase', letterSpacing: 1 }}>Recovers</span>
                  <span style={{ fontFamily: 'monospace', fontSize: 22, fontWeight: 700, color: GRN }}>${(a.annual_recovery / 1e6).toFixed(1)}M</span>
                  <span style={{ fontSize: 11, color: '#4A6080' }}>/year</span>
                  {a.live_failure_count > 0 && (
                    <span style={{ marginLeft: 'auto', padding: '2px 8px', borderRadius: 6, fontFamily: 'monospace', fontSize: 9, fontWeight: 700, background: 'rgba(240,54,90,0.1)', color: RED, border: '1px solid rgba(240,54,90,0.3)' }}>
                      {a.live_failure_count} live failures
                    </span>
                  )}
                </div>

                {/* Fix box */}
                <div style={{ padding: '10px 12px', background: '#0C1220', border: '1px solid #1A2438', borderRadius: 10, marginBottom: 10 }}>
                  <span style={{ color: BLU, fontWeight: 600, fontSize: 11 }}>Fix: </span>
                  <span style={{ color: '#4A6080', fontSize: 11 }}>{a.fix}</span>
                </div>

                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#4A6080', marginBottom: 14 }}>
                  SAP Component: <span style={{ color: '#60A5FA' }}>{a.sap_component}</span>
                </div>

                <button style={{
                  padding: '10px', background: '#0C1220', border: '1px solid #1F2D45',
                  borderRadius: 10, fontSize: 13, fontWeight: 600, color: '#EEF2FA',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}
                  onMouseEnter={e => { e.currentTarget.style.background = BLU; e.currentTarget.style.borderColor = BLU }}
                  onMouseLeave={e => { e.currentTarget.style.background = '#0C1220'; e.currentTarget.style.borderColor = '#1F2D45' }}
                >
                  ⚡ Initiate Fix
                </button>
              </div>
            )
          })}
        </div>

        {/* ROI summary */}
        <div style={{
          background: 'linear-gradient(135deg, #0A1628, #061020)',
          border: '1px solid rgba(59,130,246,0.25)',
          borderRadius: 20, padding: 28,
          display: 'grid', gridTemplateColumns: '1fr auto', gap: 24, alignItems: 'center'
        }}>
          <div>
            <div style={{ fontFamily: 'monospace', fontSize: 10, letterSpacing: 2, color: '#60A5FA', marginBottom: 10 }}>FULL RECOVERY PROJECTION</div>
            <div style={{ fontSize: 17, fontWeight: 700, lineHeight: 1.5, marginBottom: 20 }}>
              Fix all 4 issues → <span style={{ color: GRN }}>${(roi_summary.total_annual_recovery / 1e6).toFixed(2)}M</span> recovered annually.<br />
              AgentReady platform costs <span style={{ color: RED }}>${(roi_summary.platform_cost_annual / 1000).toFixed(0)}K</span>/year.
            </div>
            <div style={{ display: 'flex', gap: 32 }}>
              {[
                { label: 'Annual Recovery',  value: `$${(roi_summary.total_annual_recovery / 1e6).toFixed(2)}M`, color: GRN },
                { label: 'Platform Cost',    value: `$${(roi_summary.platform_cost_annual / 1000).toFixed(0)}K`,  color: RED },
                { label: 'Net Impact Yr 1',  value: `$${(roi_summary.net_impact_year1 / 1e6).toFixed(2)}M`,      color: '#EEF2FA' },
                { label: 'Payback Period',   value: `${roi_summary.payback_days} days`,                           color: BLU },
              ].map(item => (
                <div key={item.label}>
                  <div style={{ fontSize: 9, fontFamily: 'monospace', color: '#4A6080', marginBottom: 4 }}>{item.label}</div>
                  <div style={{ fontFamily: 'monospace', fontSize: 16, fontWeight: 700, color: item.color }}>{item.value}</div>
                </div>
              ))}
            </div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 16, padding: '24px 32px', minWidth: 140 }}>
            <div style={{ fontFamily: 'monospace', fontSize: 52, fontWeight: 700, color: '#60A5FA', lineHeight: 1 }}>{roi_summary.roi_multiplier}x</div>
            <div style={{ fontSize: 11, color: '#4A6080', fontFamily: 'monospace', marginTop: 6 }}>Return on Investment</div>
          </div>
        </div>
      </div>
    </div>
  )
}
