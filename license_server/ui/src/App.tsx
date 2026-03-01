import { useState, useEffect } from 'react'
import { Layout, Users, Shield, Terminal, Activity, LogOut, RefreshCw, PlusCircle, CheckCircle2, AlertCircle } from 'lucide-react'
import * as api from './api/client'
import { toast, Toaster } from 'react-hot-toast'

function App() {
    const [activeTab, setActiveTab] = useState('dashboard')

    return (
        <div className="flex h-screen w-full bg-gray-100 overflow-hidden font-sans">
            <Toaster position="top-right" />
            {/* Sidebar */}
            <aside className="w-64 bg-slate-900 text-white flex flex-col">
                <div className="p-6 text-xl font-bold flex items-center gap-2 border-b border-slate-700">
                    <Shield className="text-blue-400" />
                    <span>License Authority</span>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'dashboard' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
                    >
                        <Activity size={20} /> Dashboard
                    </button>
                    <button
                        onClick={() => setActiveTab('cas')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'cas' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
                    >
                        <Users size={20} /> CA Management
                    </button>
                    <button
                        onClick={() => setActiveTab('support')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'support' ? 'bg-blue-600' : 'hover:bg-slate-800'}`}
                    >
                        <Terminal size={20} /> Remote Support
                    </button>
                </nav>

                <div className="p-4 border-t border-slate-700">
                    <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 text-slate-400">
                        <LogOut size={20} /> Logout
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-auto">
                <header className="h-16 bg-white border-b flex items-center justify-between px-8 shadow-sm">
                    <h2 className="text-lg font-semibold text-gray-800 capitalize">{activeTab.replace('-', ' ')}</h2>
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-2 text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full font-medium">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            Server Online
                        </span>
                    </div>
                </header>

                <section className="p-8">
                    {activeTab === 'dashboard' && <DashboardView />}
                    {activeTab === 'cas' && <CAManagementView />}
                    {activeTab === 'support' && <RemoteSupportView />}
                </section>
            </main>
        </div>
    )
}

function DashboardView() {
    const [stats, setStats] = useState({ total_cas: 0, active_licenses: 0, online_devices: 0 })
    const [recentActivity, setRecentActivity] = useState([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // In a real app these might be specific endpoints
                const caRes = await api.getCAs()
                setStats({
                    total_cas: caRes.data.length,
                    active_licenses: caRes.data.filter((ca: any) => ca.is_active).length, // simplified
                    online_devices: 0 // TBD from socket
                })
                // setRecentActivity(...)
            } catch (err) {
                console.error(err)
            } finally {
                setIsLoading(false)
            }
        }
        fetchDashboardData()
    }, [])

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard title="Total CAs" value={isLoading ? "..." : stats.total_cas.toString()} sub="Verified accounts" />
                <StatCard title="Active Licenses" value={isLoading ? "..." : stats.active_licenses.toString()} sub="Valid tokens" />
                <StatCard title="Connected Devices" value={isLoading ? "..." : stats.online_devices.toString()} sub="Currently monitored" />
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">System Status</h3>
                    <span className="text-xs text-gray-400 font-mono underline cursor-help">Activity Log (TBD)</span>
                </div>
                <div className="space-y-4">
                    {stats.total_cas === 0 ? (
                        <div className="py-8 text-center text-gray-400 text-sm italic">No recent system events</div>
                    ) : (
                        <ActivityItem user="System" action="License server heartbeat stable" time="Just now" />
                    )}
                </div>
            </div>
        </div>
    )
}

function CAManagementView() {
    const [cas, setCas] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [formData, setFormData] = useState({ id: '', name: '', email: '', phone: '' })

    const fetchCAs = async () => {
        setIsLoading(true)
        try {
            const response = await api.getCAs()
            setCas(response.data)
        } catch (error) {
            toast.error("Failed to load CAs")
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchCAs()
    }, [])

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            await api.registerCA(formData)
            toast.success("CA Registered Successfully")
            setShowModal(false)
            fetchCAs()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || "Registration failed")
        }
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <h3 className="text-lg font-semibold">Registered CAs</h3>
                    <button onClick={fetchCAs} className="text-gray-400 hover:text-blue-600 transition">
                        <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
                    </button>
                </div>
                <button
                    onClick={() => setShowModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition flex items-center gap-2"
                >
                    <PlusCircle size={18} /> Register New CA
                </button>
            </div>

            {isLoading ? (
                <div className="p-12 text-center text-gray-500">Loading Chartered Accountants...</div>
            ) : (
                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 text-xs uppercase font-semibold">
                        <tr>
                            <th className="px-6 py-4">CA ID</th>
                            <th className="px-6 py-4">Name</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Created</th>
                            <th className="px-6 py-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y text-sm">
                        {cas.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-12 text-center text-gray-400">No CAs registered yet</td>
                            </tr>
                        ) : cas.map((ca: any) => (
                            <tr key={ca.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 font-medium font-mono">{ca.id}</td>
                                <td className="px-6 py-4">
                                    <div className="font-medium text-gray-900">{ca.name}</div>
                                    <div className="text-xs text-gray-500">{ca.email}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${ca.is_active ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'}`}>
                                        {ca.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-gray-500">{new Date(ca.created_at).toLocaleDateString()}</td>
                                <td className="px-6 py-4 text-blue-600 font-medium cursor-pointer hover:underline">Manage</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}

            {/* Simple Registration Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                        <div className="p-6 border-b">
                            <h3 className="text-lg font-bold">Register CA</h3>
                        </div>
                        <form onSubmit={handleRegister} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">CA Identifier (e.g. CA-JOHN)</label>
                                <input
                                    required
                                    className="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                                    value={formData.id}
                                    onChange={e => setFormData({ ...formData, id: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                                <input
                                    required
                                    className="w-full border rounded-lg px-3 py-2"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input
                                    required type="email"
                                    className="w-full border rounded-lg px-3 py-2"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button type="button" onClick={() => setShowModal(false)} className="flex-1 px-4 py-2 border rounded-lg font-medium hover:bg-gray-50">Cancel</button>
                                <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">Register</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

function RemoteSupportView() {
    const [sessions, setSessions] = useState([])
    const [isLoading, setIsLoading] = useState(true)

    const fetchSessions = async () => {
        setIsLoading(true)
        try {
            // Placeholder: currently returns array from registry
            const response = await api.getSupportSessions()
            setSessions(response.data)
        } catch (err) {
            console.error("Failed to fetch sessions", err)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchSessions()
        const interval = setInterval(fetchSessions, 10000) // Poll every 10s
        return () => clearInterval(interval)
    }, [])

    const handleAction = async (caId: string, action: string) => {
        try {
            await api.sendRemoteCommand(caId, action)
            toast.success(`Command [${action}] sent to ${caId}`)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || "Command failed")
        }
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Active Support Connections</h3>
                    <button onClick={fetchSessions} className="text-gray-400 hover:text-blue-600 transition">
                        <RefreshCw size={16} className={isLoading ? "animate-spin" : ""} />
                    </button>
                </div>

                <div className="space-y-4">
                    {sessions.length === 0 ? (
                        <div className="py-12 text-center text-gray-400 text-sm italic">
                            No CA desktops currently in support mode
                        </div>
                    ) : sessions.map((session: any) => (
                        <div key={session.ca_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
                            <div>
                                <p className="font-semibold">{session.ca_id} - {session.hostname || 'Remote PC'}</p>
                                <p className="text-xs text-gray-500">Connected since: {new Date(session.connected_at).toLocaleTimeString()}</p>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleAction(session.ca_id, 'diagnostics')}
                                    className="px-3 py-1 bg-white border rounded text-xs font-semibold hover:bg-gray-100"
                                >
                                    Diagnostics
                                </button>
                                <button
                                    onClick={() => handleAction(session.ca_id, 'update')}
                                    className="px-3 py-1 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700"
                                >
                                    Update
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
                <h3 className="text-lg font-semibold mb-4">System Health</h3>
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-blue-800 text-sm flex items-start gap-3">
                    <Shield className="mt-0.5 text-blue-600" size={18} />
                    <div>
                        <strong>Infrastructure Status:</strong> All systems are operational on local node. RSA Keys Loaded.
                    </div>
                </div>
            </div>
        </div>
    )
}

function StatCard({ title, value, sub }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border">
            <p className="text-sm text-gray-500 font-medium">{title}</p>
            <p className="text-3xl font-bold mt-2 text-slate-800">{value}</p>
            <p className="text-xs text-blue-600 mt-2 font-medium">{sub}</p>
        </div>
    )
}

function ActivityItem({ user, action, time }) {
    return (
        <div className="flex items-center justify-between hover:bg-gray-50 p-2 rounded transition">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                    <Users size={16} />
                </div>
                <div>
                    <p className="text-sm font-semibold">{user}</p>
                    <p className="text-xs text-gray-500">{action}</p>
                </div>
            </div>
            <span className="text-xs text-gray-400">{time}</span>
        </div>
    )
}

export default App
