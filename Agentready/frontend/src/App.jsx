import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ScoreDashboard from './components/ScoreDashboard'
import SimulationLog from './components/SimulationLog'
import ActionPlan from './components/ActionPlan'
import BenchmarkIndex from './components/BenchmarkIndex'

export default function App() {
  const [screen, setScreen] = useState('dashboard')

  const screens = {
    dashboard:  <ScoreDashboard />,
    simulation: <SimulationLog />,
    actions:    <ActionPlan />,
    benchmark:  <BenchmarkIndex />,
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: '#05080F' }}>
      <Sidebar active={screen} onNavigate={setScreen} />
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {screens[screen]}
      </div>
    </div>
  )
}
