import type { RiskLevel } from '../types'
import { riskClass } from '../utils/risk'
export function RiskBadge({ level }: { level: RiskLevel | string }) { return <span className={`risk-badge ${riskClass(level)}`}>{level}</span> }
