import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts'

const RED = '#F0365A', GRN = '#10D9A0', BLU = '#3B82F6'

export default function BenchmarkIndex() {
  const [data, setData] = useState(null)

  useEffect(() => { axios.get('/api/benchmark').then(r => setData(r.data)) }, [])

  if (!data) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#4A6080' }}>Loading benchmark data...</div>

  const { competitors, vertical_stats: vs, projection } = data

  const gapData = ['delivery', 'returns', 'api', 'transparency'].map(k => {
    const demo = competitors.find(c => c.is_demo)
    return {
      name: k.charAt(0).toUpperCase() + k.slice(1),
      you:  demo?.[k]          ?? 0,
      top5: vs.top5_avg_sub?.[k] ?? 0,
    }
  })

  return (
    <div>
      <div style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(5,8,15,0.92)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid #1A2438', padding: '14px 28px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700 }}>Competitor Index</div>
          <div style={{ fontSize: 11, color: '#8496B4', fontFamily: 'monospace', marginTop: 2 }}>
            Real Olist seller clusters · ML-scored · {vs.total_count} retailers
          </div>
        </div>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 20, background: 'rgba(16,217,160,0.08)', border: '1px solid rgba(16,217,160,0.2)', color: GRN, fontFamily: 'monospace', fontSize: 10, fontWeight: 700 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: GRN }} /> UPDATED TODAY
        </span>
      </div>

      <div style={{ padding: 28 }}>
        {/* KPI strip */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, marginBottom: 20 }}>
          {[
            { label: 'Vertical Avg Score',  value: vs.average_score,           sub: `Fashion Retail (n=${vs.total_count})`, color: BLU },
            { label: 'Your Current Rank',   value: `${vs.demo_rank} / ${vs.total_count}`, sub: 'Bottom quartile',           color: RED },
            { label: 'Score to Top 5',      value: `+${vs.score_to_top5} pts`,  sub: 'Achievable in 90 days',              color: GRN },
          ].map(k => (
            <div key={k.label} style={{ background: '#080D18', border: '1px solid #1A2438', borderRadius: 16, padding: 20, position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: k.color }} />
              <div style={{ fontSize: 9, letterSpacing: 2, color: '#4A6080', fontFamily: 'monospace', textTransform: 'uppercase', marginBottom: 6 }}>{k.label}</div>
              <div style={{ fontFamily: 'monospace', fontSize: 26, fontWeight: 700, color: k.color, marginBottom: 4 }}>{k.value}</div>
              <div style={{ fontSize: 11, color: '#8496B4' }}>{k.sub}</div>
            </div>
          ))}
        </div>

        {/* Full landscape */}
        <div style={{ background: '#080D18', border: '1px solid #1A2438', borderRadius: 16, padding: 20, marginBottom: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Competitive Landscape — All {vs.total_count} Retailers</div>
          <div style={{ fontSize: 10, color: '#8496B4', fontFamily: 'monospace', marginBottom: 16 }}>Real Olist seller clusters · ML-scored · You in red</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={competitors} margin={{ left: -20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A2438" />
              <XAxis dataKey="name" tick={{ fill: '#4A6080', fontSize: 8 }} interval={0} angle={-40} textAnchor="end" />
              <YAxis domain={[30, 100]} tick={{ fill: '#4A6080', fontSize: 9 }} />
              <Tooltip contentStyle={{ background: '#0C1220', border: '1px solid #1A2438', borderRadius: 8, fontSize: 11 }} />
              <Bar dataKey="score" radius={[3, 3, 0, 0]}>
                {competitors.map((c, i) => (
                  <Cell key={i} fill={c.is_demo ? RED : 'rgba(59,130,246,0.5)'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Bottom 2 charts */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div style={{ background: '#080D18', border: '1px solid #1A2438', borderRadius: 16, padding: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Top 5 vs You — Sub-Score Gap</div>
            <div style={{ fontSize: 10, color: '#8496B4', fontFamily: 'monospace', marginBottom: 16 }}>Where you're losing ground</div>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={gapData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1A2438" />
                <XAxis dataKey="name" tick={{ fill: '#4A6080', fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#4A6080', fontSize: 9 }} />
                <Tooltip contentStyle={{ background: '#0C1220', border: '1px solid #1A2438', borderRadius: 8, fontSize: 11 }} />
                <Legend wrapperStyle={{ fontSize: 10, color: '#8496B4' }} />
                <Bar dataKey="top5" fill="rgba(16,217,160,0.65)" radius={[3, 3, 0, 0]} name="Top 5 Avg" />
                <Bar dataKey="you"  fill="rgba(240,54,90,0.65)"  radius={[3, 3, 0, 0]} name="You" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ background: '#080D18', border: '1px solid #1A2438', borderRadius: 16, padding: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Score Projection — With All 4 Fixes</div>
            <div style={{ fontSize: 10, color: '#8496B4', fontFamily: 'monospace', marginBottom: 16 }}>ML-estimated 90-day trajectory</div>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={projection}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1A2438" />
                <XAxis dataKey="week" tick={{ fill: '#4A6080', fontSize: 10 }} />
                <YAxis domain={[30, 100]} tick={{ fill: '#4A6080', fontSize: 9 }} />
                <Tooltip contentStyle={{ background: '#0C1220', border: '1px solid #1A2438', borderRadius: 8, fontSize: 11 }} />
                <Line type="monotone" dataKey="score" stroke={GRN} strokeWidth={2.5} dot={{ fill: GRN, r: 4 }} name="Projected Score" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
