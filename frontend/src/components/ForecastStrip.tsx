import { CloudRain } from 'lucide-react'
export function ForecastStrip({ forecast }: { forecast: { horizon: string; rainfall_mm: number; condition: string }[] }) { return <section className="forecast-strip">{forecast.map(item => <div key={item.horizon}><span>{item.horizon}</span><CloudRain size={17}/><b>{item.rainfall_mm} mm</b><small>{item.condition}</small></div>)}</section> }
