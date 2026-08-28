import axios from 'axios'
import type { Alert, DashboardStats, HazardReport, Road, Zone } from '../types'

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '' })
api.interceptors.request.use((config) => { const token = localStorage.getItem('nerlens_token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config })

export const getZones = async () => (await api.get<{zones: Zone[]}>('/api/risk/zones')).data.zones
export const getRoads = async () => (await api.get<{roads: Road[]}>('/api/roads')).data.roads
export const getReports = async () => (await api.get<{reports: HazardReport[]}>('/api/reports')).data.reports
export const getAlerts = async () => (await api.get<{alerts: Alert[]}>('/api/alerts')).data.alerts
export const getStats = async () => (await api.get<{stats: DashboardStats; trend: {hour: string; risk: number}[]}>('/api/dashboard/stats')).data
export const getForecast = async () => (await api.get<{forecast: {horizon: string; rainfall_mm: number; condition: string}[]}>('/api/weather/forecast')).data.forecast
