import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import type { Road, Zone } from '../types'
import { riskColor } from '../utils/risk'
import { Navigation, Route } from 'lucide-react'

function MapFlyer({ focus }: { focus?: Zone }) { const map = useMap(); useEffect(() => { if (focus) map.flyTo([focus.latitude, focus.longitude], 9, { duration: .7 }) }, [focus, map]); return null }

export function RiskMap({ zones, roads, selectedZone, onSelect }: { zones: Zone[]; roads: Road[]; selectedZone?: Zone; onSelect: (zone: Zone) => void }) {
  const [showRoads, setShowRoads] = useState(true)
  return <div className="map-frame">
    <div className="map-toolbar"><span><Navigation size={14}/> GIS risk intelligence</span><button className={showRoads ? 'map-toggle is-active' : 'map-toggle'} onClick={() => setShowRoads(!showRoads)}><Route size={13}/> Roads</button></div>
    <MapContainer center={[25.6, 92.3]} zoom={6} scrollWheelZoom className="leaflet-map">
      <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <MapFlyer focus={selectedZone} />
      {zones.map(zone => <CircleMarker key={zone.id} center={[zone.latitude, zone.longitude]} radius={Math.max(9, zone.risk_score / 4.2)} pathOptions={{ color: riskColor(zone.risk_level), fillColor: riskColor(zone.risk_level), fillOpacity: .54, weight: selectedZone?.id === zone.id ? 3 : 1.5 }} eventHandlers={{ click: () => onSelect(zone) }}><Popup><strong>{zone.zone_name}</strong><br/>{zone.risk_level} · {zone.risk_score}/100<br/><small>DEMO / SIMULATED DATA</small></Popup></CircleMarker>)}
      {showRoads && roads.map(road => <CircleMarker key={`road-${road.id}`} center={[road.latitude, road.longitude]} radius={5} pathOptions={{ color: road.status === 'OPEN' ? '#4fbd94' : '#f2a24e', fillColor: '#07131d', fillOpacity: 1, weight: 2 }}><Popup><strong>{road.road_name}</strong><br/>{road.status}</Popup></CircleMarker>)}
    </MapContainer>
    <div className="map-legend"><span><i className="dot low"/>Low</span><span><i className="dot moderate"/>Moderate</span><span><i className="dot high"/>High</span><span><i className="dot critical"/>Critical</span></div>
  </div>
}
