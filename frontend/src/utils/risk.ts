import type { RiskLevel } from '../types'
export const riskColor = (level: RiskLevel | string) => ({ LOW: '#42b58b', MODERATE: '#eebd4d', HIGH: '#ed8b4d', CRITICAL: '#e25050' }[level] || '#93a4b1')
export const riskClass = (level: RiskLevel | string) => `risk-${level.toLowerCase()}`
