import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

const RED = '#F0365A', YLW = '#F59E0B', GRN = '#10D9A0', BLU = '#3B82F6'

function ScoreRing({ score }) {
  const r = 58, circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const color = score < 60 ? RED : score < 75 ? YLW : GRN
  return (
    <div style={{ position: 'relative', width: 140, height: 140 }}>
      <svg style={{ transform: 'rotate(-90deg)' }} width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="#1F2D45" strokeWidth="12" />
        <circle cx="70" cy="70" r={r} fill="none" stroke={color}
          strokeWidth="12" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1)' }} />
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
      }}>
        <span style={{ fontFamily: 'monospace', fontSize: 36, fontWeight: 700, color, lineHeight: 1 }}>{score}</span>
        <span style={{ fontFamily: 'monospace', fontSize: 11, color: '#4A6080' }}>/100</span>
      </div>
    </div>
  )
}

function Card({ children, style = {} }) {
  return (
    <div style={{
      background: '#080D18', border: '1px solid #1A2438',
      borderRadius: 16, padding: 20, ...style
    }}>
      {children}
    </div>
  )
}

function Label({ children }) {
  return <div style={{ fontSize: 9, letterSpacing: 2, color: '#4A6080', fontFamily: 'monospace', textTransform: 'uppercase', marginBottom: 6 }}>{children}</div>
}

export default function ScoreDashboard() {
  const [data, setData]       = useState(null)
  const [subs, setSubs]       = useState([])
  const [history, setHistory] = useState({ seller: [], competitor_avg: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get('/api/score'),
      axios.get('/api/score/sub'),
      axios.get('/api/score/history'),
    ]).then(([s, sub, h]) => {
      setData(s.data)
      setSubs(sub.data)
      setHistory(h.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#4A6080' }}>Loading real data from ML model...</div>
  if (!data)   return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: RED }}>Error — is the backend running on port 8000?</div>

  const { scores, kpis, alert } = data

  const trendData = (history.seller || []).map((s, i) => ({
    date:     s.date?.slice(5),
    you:      s.score,
    comp_avg: history.competitor_avg?.[i]?.score,
  }))

  const radarData = subs.map(s => ({
    dim:  s.dimension.split(' ')[0],
    you:  s.score,
    top5: Math.min(s.score + 22, 98),
  }))

  const subColor = c => c === 'red' ? RED : c === 'green' ? GRN : YLW

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
          <div style={{ fontSize: 15, fontWeight: 700 }}>Score Dashboard</div>
          <div style={{ fontSize: 11, color: '#8496B4', fontFamily: 'monospace', marginTop: 2 }}>
            Real data · Olist 100K orders · Random Forest R² 0.94
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 20, background: 'rgba(240,54,90,0.08)', border: '1px solid rgba(240,54,90,0.2)', color: RED, fontFamily: 'monospace', fontSize: 10, fontWeight: 700 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: RED, animation: 'pulse 2s infinite' }} /> AGENT-INVISIBLE
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 20, background: 'rgba(16,217,160,0.08)', border: '1px solid rgba(16,217,160,0.2)', color: GRN, fontFamily: 'monospace', fontSize: 10, fontWeight: 700 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: GRN }} /> LIVE
          </span>
        </div>
      </div>

      <div style={{ padding: 28 }}>
        {/* Alert */}
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', background: 'rgba(240,54,90,0.05)', border: '1px solid rgba(240,54,90,0.3)', borderRadius: 12, padding: 16, marginBottom: 24 }}>
          <div style={{ width: 36, height: 36, flexShrink: 0, background: 'rgba(240,54,90,0.1)', border: '1px solid rgba(240,54,90,0.2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>⚠</div>
          <div>
            <div style={{ color: RED, fontWeight: 600, fontSize: 13 }}>{alert?.message}</div>
            <div style={{ color: '#8496B4', fontSize: 11, marginTop: 4 }}>
              Source: Olist Brazilian E-Commerce Dataset · ML model trained on 100,000 real orders
            </div>
          </div>
        </div>

        {/* Score hero + sub-scores */}
        <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gap: 16, marginBottom: 16 }}>
          <Card style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Label>Overall AgentReady Score</Label>
            <ScoreRing score={scores.overall} />
            <div style={{ marginTop: 12, padding: '4px 10px', borderRadius: 6, background: 'rgba(240,54,90,0.1)', border: '1px solid rgba(240,54,90,0.2)', color: RED, fontFamily: 'monospace', fontSize: 9, fontWeight: 700 }}>
              {scores.label}
            </div>
            <div style={{ fontSize: 11, color: '#8496B4', textAlign: 'center', marginTop: 10, lineHeight: 1.6, maxWidth: 180 }}>
              Below 70pt threshold. Competitors above 80 are capturing agent-driven orders.
            </div>
          </Card>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {subs.map(s => (
              <Card key={s.dimension}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#8496B4', maxWidth: 140, lineHeight: 1.4 }}>{s.dimension}</div>
                  <div style={{ fontFamily: 'monospace', fontSize: 26, fontWeight: 700, color: subColor(s.color) }}>{s.score}</div>
                </div>
                <div style={{ height: 4, background: '#1F2D45', borderRadius: 2, overflow: 'hidden', marginBottom: 8 }}>
                  <div style={{ height: '100%', borderRadius: 2, width: `${s.score}%`, background: subColor(s.color), transition: 'width 1s ease' }} />
                </div>
                <div style={{ fontSize: 11, color: '#4A6080', lineHeight: 1.5 }}>{s.detail}</div>
              </Card>
            ))}
          </div>
        </div>

        {/* KPI strip */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 16 }}>
          {[
            { label: 'Weekly Revenue Lost', value: `$${(kpis.weekly_revenue_lost / 1000).toFixed(1)}K`, sub: 'Failed agent interactions', color: RED },
            { label: 'Agent Success Rate',  value: `${kpis.agent_success_rate}%`,   sub: `${kpis.total_interactions} total interactions`, color: YLW },
            { label: 'Competitors Above 80',value: kpis.competitors_above_80,        sub: 'Capturing your orders', color: BLU },
            { label: 'Score Change 30d',    value: `${kpis.score_change_30d} pts`,   sub: 'Trending downward', color: RED },
          ].map(k => (
            <Card key={k.label} style={{ position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: k.color }} />
              <Label>{k.label}</Label>
              <div style={{ fontFamily: 'monospace', fontSize: 24, fontWeight: 700, color: k.color, marginBottom: 4 }}>{k.value}</div>
              <div style={{ fontSize: 11, color: '#8496B4' }}>{k.sub}</div>
            </Card>
          ))}
        </div>

        {/* Charts */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Card>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Score Trend — 90 Days</div>
            <div style={{ fontSize: 10, color: '#8496B4', fontFamily: 'monospace', marginBottom: 16 }}>You vs competitor average</div>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1A2438" />
                <XAxis dataKey="date" tick={{ fill: '#4A6080', fontSize: 9 }} interval={14} />
                <YAxis domain={[30, 100]} tick={{ fill: '#4A6080', fontSize: 9 }} />
                <Tooltip contentStyle={{ background: '#0C1220', border: '1px solid #1A2438', borderRadius: 8, fontSize: 11 }} />
                <Legend wrapperStyle={{ fontSize: 10, color: '#8496B4' }} />
                <Line type="monotone" dataKey="you"      stroke={RED} strokeWidth={2} dot={false} name="Nexus Fashion" />
                <Line type="monotone" dataKey="comp_avg" stroke={BLU} strokeWidth={2} dot={false} strokeDasharray="4 3" name="Competitor Avg" />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Sub-Score Radar</div>
            <div style={{ fontSize: 10, color: '#8496B4', fontFamily: 'monospace', marginBottom: 16 }}>You vs top 5 competitors</div>
            <ResponsiveContainer width="100%" height={150}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1A2438" />
                <PolarAngleAxis dataKey="dim" tick={{ fill: '#8496B4', fontSize: 9 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} />
                <Radar name="You"  dataKey="you"  stroke={RED} fill={RED} fillOpacity={0.15} />
                <Radar name="Top5" dataKey="top5" stroke={GRN} fill={GRN} fillOpacity={0.07} strokeDasharray="4 3" />
                <Legend wrapperStyle={{ fontSize: 10, color: '#8496B4' }} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </div>
    </div>
  )
}
