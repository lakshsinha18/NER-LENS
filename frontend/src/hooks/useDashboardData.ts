import { useCallback, useEffect, useState } from 'react'
import { getAlerts, getForecast, getReports, getRoads, getStats, getZones } from '../services/api'
import type { Alert, DashboardStats, HazardReport, Road, Zone } from '../types'

export function useDashboardData() {
  const [zones, setZones] = useState<Zone[]>([]); const [roads, setRoads] = useState<Road[]>([]); const [reports, setReports] = useState<HazardReport[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([]); const [forecast, setForecast] = useState<{horizon: string; rainfall_mm: number; condition: string}[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null); const [trend, setTrend] = useState<{hour: string; risk: number}[]>([])
  const [error, setError] = useState(''); const [loading, setLoading] = useState(true)
  const refresh = useCallback(async () => { try { setError(''); const [z, r, rep, a, s, f] = await Promise.all([getZones(), getRoads(), getReports(), getAlerts(), getStats(), getForecast()]); setZones(z); setRoads(r); setReports(rep); setAlerts(a); setStats(s.stats); setTrend(s.trend); setForecast(f) } catch { setError('The live demo service is unavailable. Start the backend and try again.') } finally { setLoading(false) } }, [])
  useEffect(() => { refresh(); const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/dashboard`); socket.onmessage = () => refresh(); const ping = window.setInterval(() => socket.readyState === WebSocket.OPEN && socket.send('heartbeat'), 20000); return () => { window.clearInterval(ping); socket.close() } }, [refresh])
  return { zones, roads, reports, alerts, stats, trend, forecast, error, loading, refresh }
}
