import type { LucideIcon } from 'lucide-react'
export function KpiCard({ label, value, icon: Icon, accent }: {label: string; value: number | string; icon: LucideIcon; accent: string}) { return <div className="kpi-card"><div><span>{label}</span><strong>{value}</strong></div><div className="kpi-icon" style={{ color: accent, backgroundColor: `${accent}19` }}><Icon size={21}/></div></div> }
