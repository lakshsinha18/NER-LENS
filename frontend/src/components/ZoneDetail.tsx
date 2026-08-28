import { CloudRain, Droplets, Mountain, TriangleAlert } from 'lucide-react'
import type { Zone } from '../types'
import { RiskBadge } from './RiskBadge'

export function ZoneDetail({ zone }: { zone?: Zone }) {
  if (!zone) return <aside className="detail-panel empty-detail"><Mountain size={29}/><strong>Select a risk zone</strong><span>Click a zone on the map to inspect its drivers, forecast, and recommended response.</span></aside>
  return <aside className="detail-panel">
    <div className="panel-title"><div><span className="eyebrow">ZONE INTELLIGENCE</span><h2>{zone.zone_name}</h2><p>{zone.district}, {zone.state}</p></div><RiskBadge level={zone.risk_level}/></div>
    <div className="score-row"><div><span>Risk score</span><strong>{zone.risk_score}<small>/100</small></strong></div><div><span>Probability</span><strong>{Math.round(zone.probability * 100)}<small>%</small></strong></div></div>
    <div className="measure-grid"><div><CloudRain/><span>24h rain</span><b>{zone.rainfall_24h} mm</b></div><div><Droplets/><span>Soil moisture</span><b>{zone.soil_moisture}%</b></div><div><Mountain/><span>Slope</span><b>{zone.slope}°</b></div><div><CloudRain/><span>+24h forecast</span><b>{zone.forecast_rainfall} mm</b></div></div>
    <div className="why-box"><div><TriangleAlert size={16}/><b>Why this risk level?</b></div><ul>{zone.explainability.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul><small>{zone.explainability.notice}</small></div>
    <div className="response-box"><span>RECOMMENDED ACTION</span><p>{zone.risk_score >= 81 ? 'Activate district incident coordination and restrict exposed road segments.' : zone.risk_score >= 61 ? 'Stage response resources and issue targeted monitoring alerts.' : 'Continue rainfall and slope monitoring.'}</p></div>
  </aside>
}
