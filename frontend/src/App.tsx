import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './layouts/AppShell'
import { DashboardPage } from './pages/DashboardPage'
import { PublicMapPage } from './pages/PublicMapPage'
import { ReportsPage } from './pages/ReportsPage'
import { AboutPage } from './pages/AboutPage'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { AlertsPage, AnalyticsPage, EmergencyPage, RoadsPage, SatellitePage, SensorsPage, SettingsPage, UsersPage, WeatherPage } from './pages/OperationsPages'
function Framed({ children }: {children: React.ReactNode}) { return <AppShell>{children}</AppShell> }
export default function App() { return <Routes><Route path="/" element={<LandingPage/>}/><Route path="/login" element={<LoginPage/>}/><Route path="/about" element={<AboutPage/>}/><Route path="/dashboard" element={<Framed><DashboardPage/></Framed>}/><Route path="/field-dashboard" element={<Framed><DashboardPage/></Framed>}/><Route path="/risk-map" element={<Framed><PublicMapPage/></Framed>}/><Route path="/reports" element={<Framed><ReportsPage/></Framed>}/><Route path="/my-reports" element={<Framed><ReportsPage/></Framed>}/><Route path="/submit-report" element={<Framed><ReportsPage/></Framed>}/><Route path="/alerts" element={<Framed><AlertsPage/></Framed>}/><Route path="/local-alerts" element={<Framed><AlertsPage/></Framed>}/><Route path="/roads" element={<Framed><RoadsPage/></Framed>}/><Route path="/road-status" element={<Framed><RoadsPage/></Framed>}/><Route path="/emergency" element={<Framed><EmergencyPage/></Framed>}/><Route path="/assigned-tasks" element={<Framed><EmergencyPage/></Framed>}/><Route path="/weather" element={<Framed><WeatherPage/></Framed>}/><Route path="/satellite" element={<Framed><SatellitePage/></Framed>}/><Route path="/sensors" element={<Framed><SensorsPage/></Framed>}/><Route path="/analytics" element={<Framed><AnalyticsPage/></Framed>}/><Route path="/settings" element={<Framed><SettingsPage/></Framed>}/><Route path="/users" element={<Framed><UsersPage/></Framed>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes> }
