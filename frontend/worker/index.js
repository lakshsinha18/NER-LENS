// Deployment-preview adapter. It makes the public demo functional without
// exposing the FastAPI/PostGIS operational stack on this static Worker host.
// Every response is explicitly identified as simulated data.
const state = {
  zones: [
    ['Aizawl Ridge', 'Aizawl', 'Mizoram', 23.727, 92.717, 87, 78, 38, 134],
    ['East Khasi Hills', 'Shillong', 'Meghalaya', 25.578, 91.893, 72, 71, 34, 104],
    ['Sikkim Corridor', 'Gangtok', 'Sikkim', 27.338, 88.606, 65, 63, 31, 89],
    ['Papum Pare Hills', 'Itanagar', 'Arunachal Pradesh', 27.103, 93.618, 58, 60, 29, 69],
    ['Dima Hasao', 'Haflong', 'Assam', 25.171, 93.017, 49, 55, 27, 58],
    ['Chandel Escarpment', 'Chandel', 'Manipur', 24.333, 94.052, 43, 50, 26, 47],
    ['Kohima South', 'Kohima', 'Nagaland', 25.658, 94.11, 37, 47, 22, 38],
    ['Jampui Hills', 'North Tripura', 'Tripura', 24.001, 92.273, 25, 42, 17, 27],
  ].map((row, i) => zone(i + 1, row)),
  roads: [
    road(1, 'NH-306 Aizawl Corridor', 'National Highway', 23.735, 92.729, 'MONITORING', 1.45),
    road(2, 'Shillong Bypass', 'State Highway', 25.588, 91.882, 'OPEN', 1.18),
    road(3, 'Gangtok–Rangpo Road', 'National Highway', 27.315, 88.598, 'PARTIALLY_BLOCKED', 1.39),
    road(4, 'Haflong Hill Road', 'District Road', 25.177, 93.03, 'OPEN', 1.12),
  ],
  reports: [report(1, 'Slope movement', 'Fresh soil displacement observed beside the hill road. Demo report for workflow testing.', 23.732, 92.725, 'possible_landslide', .58, 'HIGH', 'UNDER_REVIEW'), report(2, 'Blocked road', 'Small debris fall affecting one lane; demo report, not a verified incident.', 27.318, 88.601, 'blocked_road', .63, 'MODERATE', 'VERIFIED')],
  alerts: [alert(1, 'CRITICAL', 'Critical landslide watch — Aizawl Ridge', 'DEMO / SIMULATED DATA: Avoid exposed slopes and follow district authority guidance. This is a prediction, not a confirmed event.', 'Aizawl'), alert(2, 'HIGH', 'Monitoring: Gangtok–Rangpo Road', 'DEMO / SIMULATED DATA: partial obstruction workflow active.', 'Gangtok')],
}

function level(score) { return score >= 81 ? 'CRITICAL' : score >= 61 ? 'HIGH' : score >= 31 ? 'MODERATE' : 'LOW' }
function zone(id, row) { const [zone_name, district, state, latitude, longitude, risk_score, soil_moisture, slope, rainfall_24h] = row; return { id, zone_name, district, state, latitude, longitude, risk_score, risk_level: level(risk_score), probability: risk_score / 100, rainfall_24h, soil_moisture, slope, forecast_rainfall: Math.max(9, Math.round(rainfall_24h * .31)), updated_at: new Date().toISOString(), is_demo: true, explainability: { reasons: [rainfall_24h >= 70 && 'Heavy 24-hour rainfall', soil_moisture >= 68 && 'High soil moisture', slope >= 28 && 'Steep terrain', risk_score >= 61 && 'Accumulated terrain and rainfall risk'].filter(Boolean), notice: 'Predictions indicate relative risk, not a guaranteed event.' } } }
function road(id, road_name, road_type, latitude, longitude, status, criticality) { return { id, road_name, road_type, latitude, longitude, status, criticality, last_updated: new Date().toISOString(), is_demo: true } }
function report(id, report_type, description, latitude, longitude, ai_classification, ai_confidence, severity, status) { return { id, report_type, description, latitude, longitude, ai_classification, ai_confidence, human_verification_required: true, severity, status, created_at: new Date().toISOString(), is_demo: true } }
function alert(id, severity, title, message, target_area) { return { id, alert_type: 'EARLY_WARNING', severity, title, message, target_area, status: 'ACTIVE', created_at: new Date().toISOString() } }
function json(body, status = 200) { return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } }) }
function authorised(request) { return request.headers.get('authorization') === 'Bearer sites-demo-token' }

async function api(request, path) {
  const url = new URL(request.url)
  if (path === '/api/auth/login' && request.method === 'POST') return json({ access_token: 'sites-demo-token', token_type: 'bearer', user: { id: 1, name: 'Demo Administrator', role: 'ADMIN', district: 'Aizawl', language: 'en' } })
  if (path === '/api/auth/me') return authorised(request) ? json({ id: 1, name: 'Demo Administrator', email: 'admin@nerlens.demo', role: 'ADMIN', language: 'en' }) : json({ detail: 'Authentication required' }, 401)
  if (path === '/api/risk/zones') return json({ mode: 'DEMO / SIMULATED DATA', zones: state.zones })
  if (/^\/api\/risk\/zones\/\d+$/.test(path)) { const item = state.zones.find(zone => zone.id === Number(path.split('/').pop())); return item ? json({ ...item, nearby_villages: [`${item.district} demo community`, `${item.zone_name} cluster`], nearby_roads: state.roads, critical_infrastructure: ['Demo hospital / school records available'], recommended_action: item.risk_score >= 61 ? 'Stage response resources and issue targeted monitoring alerts.' : 'Maintain routine monitoring.' }) : json({ detail: 'Risk zone not found' }, 404) }
  if (path === '/api/weather/current') return json({ mode: 'DEMO / SIMULATED DATA', location: 'Northeast India', temperature: 24.6, condition: 'Overcast', observed_at: new Date().toISOString() })
  if (path === '/api/weather/forecast') return json({ mode: 'DEMO / SIMULATED DATA', forecast: [['Now',7,'Overcast'],['+6h',21,'Rain showers'],['+12h',33,'Heavy rain'],['+24h',28,'Rain showers'],['+48h',16,'Cloudy']].map(([horizon,rainfall_mm,condition]) => ({horizon,rainfall_mm,condition})) })
  if (path === '/api/roads' && request.method === 'GET') return json({ mode: 'DEMO / SIMULATED DATA', roads: state.roads })
  if (/^\/api\/roads\/\d+$/.test(path) && request.method === 'PATCH') { if (!authorised(request)) return json({ detail: 'Authentication required' }, 401); const update = await request.json(); const item = state.roads.find(road => road.id === Number(path.split('/').pop())); if (!item) return json({ detail: 'Road not found' }, 404); item.status = update.status; item.last_updated = new Date().toISOString(); return json(item) }
  if (path === '/api/reports' && request.method === 'GET') return json({ mode: 'DEMO / SIMULATED DATA', reports: state.reports })
  if (path === '/api/reports' && request.method === 'POST') { const item = await request.json(); const created = report(state.reports.length + 1, item.report_type, item.description, item.latitude, item.longitude, item.image_url ? 'possible_landslide' : 'uncertain', item.image_url ? .58 : 0, ['Landslide','Blocked road','Slope movement'].includes(item.report_type) ? 'HIGH' : 'MODERATE', 'PENDING_REVIEW'); state.reports.unshift(created); return json({ ...created, workflow: ['Stored report', 'AI triage completed', 'Human verification required', 'Authority dashboard notified'] }, 201) }
  if (path === '/api/reports/upload' && request.method === 'POST') return json({ url: null, content_type: 'demo', ai_triage: { classification: 'uncertain', confidence: 0, human_verification_required: true }, human_verification_required: true })
  if (path === '/api/alerts') return json({ mode: 'DEMO / SIMULATED DATA', alerts: state.alerts })
  if (path === '/api/dashboard/stats') { const zones = state.zones; return json({ mode: 'DEMO / SIMULATED DATA', stats: { critical_zones: zones.filter(z => z.risk_level === 'CRITICAL').length, high_risk_zones: zones.filter(z => z.risk_level === 'HIGH').length, open_alerts: state.alerts.length, roads_at_risk: state.roads.filter(r => r.status !== 'OPEN').length, active_field_reports: state.reports.length }, trend: [['-24h',43],['-18h',48],['-12h',55],['-6h',62],['Now',Math.round(zones.reduce((total,z)=>total+z.risk_score,0)/zones.length)]].map(([hour,risk])=>({hour,risk})) }) }
  if (path === '/api/dashboard/priorities') return json({ mode: 'DEMO / SIMULATED DATA', priorities: state.zones.slice(0,4).map((zone, index) => ({ id:index + 1, priority: zone.risk_level, priority_score: Math.min(100, zone.risk_score + 7), assigned_team: zone.risk_score >= 70 ? 'NER Response Cell' : null, status: zone.risk_score >= 70 ? 'ASSIGNED' : 'UNASSIGNED', explanation: `${zone.zone_name}: Risk ${zone.risk_score} × exposure 1.28 × infrastructure 1.35 × connectivity 1.30 × response difficulty 1.14` })) })
  if (path === '/api/satellite/observations') return json({ mode: 'Satellite analysis: Demo mode', architecture: ['satellite image','preprocessing','image comparison','change detection','risk engine'], observations: state.zones.map(zone => ({ id:zone.id, location_id:zone.id, observation_date:new Date().toISOString(), change_score:Math.round(zone.risk_score*.61), deformation_score:Math.round(zone.risk_score*.52), landslide_indicator:zone.risk_score > 60 ? 'elevated_change' : 'stable', image_url:null })) })
  if (path === '/api/sensors/data' && request.method === 'POST') { const reading = await request.json(); const closest = state.zones.reduce((best, zone) => ((zone.latitude-reading.latitude)**2 + (zone.longitude-reading.longitude)**2) < ((best.latitude-reading.latitude)**2 + (best.longitude-reading.longitude)**2) ? zone : best); closest.soil_moisture = reading.soil_moisture; closest.risk_score = Math.min(98, Math.round(closest.risk_score + Math.max(0, reading.soil_moisture - 65) * .25)); closest.risk_level = level(closest.risk_score); closest.probability = closest.risk_score / 100; return json({ accepted:true, mode:'DEMO / SIMULATED DATA', sensor_id:reading.sensor_id, nearest_zone:closest.zone_name, soil_moisture:reading.soil_moisture }, 201) }
  if (path === '/api/simulation/start' && request.method === 'POST') { if (!authorised(request)) return json({ detail: 'Authentication required' }, 401); const factor = url.searchParams.get('scenario') === 'normal' ? .55 : url.searchParams.get('scenario') === 'heavy_rainfall' ? 1.15 : url.searchParams.get('scenario') === 'extreme_rainfall' ? 1.45 : 1.72; state.zones.forEach((zone, index) => { zone.rainfall_24h = Math.min(260, Math.round(zone.rainfall_24h * factor + 12)); zone.soil_moisture = Math.min(96, Math.round(zone.soil_moisture * (.92 + factor*.18))); zone.risk_score = Math.min(98, Math.round(zone.risk_score * factor + (index < 2 ? 8 : 0))); zone.risk_level = level(zone.risk_score); zone.probability = zone.risk_score / 100 }); const target = state.zones[0]; state.alerts.unshift(alert(state.alerts.length + 1, 'CRITICAL', `Simulation alert — ${target.zone_name}`, 'DEMO / SIMULATED DATA: Disaster simulation elevated risk. No real notification was sent.', target.district)); return json({ scenario:url.searchParams.get('scenario') || 'critical_warning', message:'DEMO / SIMULATED DATA: disaster simulation running', zones:state.zones }) }
  if (path === '/api/simulation/stop' && request.method === 'POST') return json({ message: 'Deployment preview retains scenario state only for the active Worker isolate.' })
  if (path.startsWith('/ws/')) return new Response('WebSocket live events are available in the Docker backend.', { status: 426 })
  return json({ detail: 'Endpoint not available in the deployment preview' }, 404)
}

export default { async fetch(request, env) { const path = new URL(request.url).pathname; if (path.startsWith('/api/') || path.startsWith('/ws/')) return api(request, path); return env.ASSETS.fetch(request) } }
