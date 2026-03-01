import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/common/Layout'
import Dashboard from './components/ca/Dashboard'
import ClientList from './components/ca/ClientList'
import DocumentBrowser from './components/ca/DocumentBrowser'
import DocumentUpload from './components/ca/DocumentUpload'
import MessagingInterface from './components/ca/MessagingInterface'
import ActivityLogs from './components/ca/ActivityLogs'
import ComplianceStatus from './components/ca/ComplianceStatus'
import ReminderManagement from './components/ca/ReminderManagement'
import ProfileManagement from './components/ca/ProfileManagement'
import CALogin from './components/ca/Login'
import PortalLogin from './components/client/Login'
import PortalDashboard from './components/client/Dashboard'
import PublicWebsite from './components/public/PublicWebsite'
import { ProfessionalCAWebsite } from './components/public/ProfessionalCAWebsite'
import { CAClientLogin } from './components/client/CAClientLogin'
import { PasswordReset } from './components/client/PasswordReset'
import { AuthProvider, useAuth } from './contexts/AuthContext'

function AppRoutes() {
    const { user, userType, isLoading } = useAuth()

    if (isLoading) {
        return <div className="h-screen w-screen flex items-center justify-center">Loading...</div>
    }

    return (
        <Routes>
            {/* Multi-tenant Public Routes */}
            <Route path="/:caSlug" element={<ProfessionalCAWebsite />} />
            <Route path="/:caSlug/login" element={<CAClientLogin />} />
            <Route path="/:caSlug/reset-password" element={<PasswordReset />} />
            <Route path="/:caSlug/home" element={userType === 'client' ? <PortalDashboard /> : <Navigate to="/:caSlug/login" />} />

            {/* CA Login */}
            <Route path="/ca/login" element={<CALogin />} />

            {/* Client Portal Login */}
            <Route path="/portal/login" element={userType === 'client' ? <Navigate to="/portal" /> : <PortalLogin />} />

            {/* CA Routes */}
            <Route path="/ca" element={userType === 'ca' ? <Layout /> : <Navigate to="/ca/login" />}>
                <Route index element={<Dashboard />} />
                <Route path="clients" element={<ClientList />} />
                <Route path="documents" element={<DocumentBrowser />} />
                <Route path="documents/upload" element={<DocumentUpload />} />
                <Route path="compliance" element={<ComplianceStatus />} />
                <Route path="reminders" element={<ReminderManagement />} />
                <Route path="profile" element={<ProfileManagement />} />
                <Route path="messaging" element={<MessagingInterface />} />
                <Route path="logs" element={<ActivityLogs />} />
            </Route>

            {/* Client Portal Routes */}
            <Route path="/portal" element={userType === 'client' ? <PortalDashboard /> : <Navigate to="/portal/login" />}>
                <Route index element={<Navigate to="/portal/documents" />} />
                <Route path="documents" element={<div>Client Documents View (TBD)</div>} />
                <Route path="messages" element={<div>Client Messages View (TBD)</div>} />
            </Route>

            {/* Legacy Public Routes */}
            <Route path="/site/:username" element={<PublicWebsite />} />

            {/* Fallback */}
            <Route path="/" element={<Navigate to="/portal/login" />} />
        </Routes>
    )
}

function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    )
}

export default App
