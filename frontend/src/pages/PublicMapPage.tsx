import { useState } from 'react'
import { useDashboardData } from '../hooks/useDashboardData'
import { RiskMap } from '../maps/RiskMap'
import { ZoneDetail } from '../components/ZoneDetail'
import type { Zone } from '../types'
export function PublicMapPage() { const data = useDashboardData(); const [selected, setSelected] = useState<Zone>(); return <div className="map-page"><div className="page-intro"><span className="eyebrow">PUBLIC EARLY WARNING MAP</span><h2>Know the risk before you travel.</h2><p>Risk layers are demo predictions. Always follow official district advisories.</p></div><div className="command-grid"><div className="map-panel"><RiskMap zones={data.zones} roads={data.roads} selectedZone={selected} onSelect={setSelected}/></div><ZoneDetail zone={selected}/></div></div> }
