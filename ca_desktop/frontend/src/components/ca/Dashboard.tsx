import { useState, useEffect } from 'react'
import {
    Users,
    FileText,
    Download,
    CheckCircle2,
    Clock,
    AlertTriangle,
    ShieldCheck,
    Terminal,
    RefreshCw
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { authApi, documentApi } from '../../api'
import { toast } from 'react-hot-toast'

export default function Dashboard() {
    const { user } = useAuth()
    const [isLoading, setIsLoading] = useState(true)
    const [counts, setCounts] = useState({ clients: 0, documents: 0, downloads: 0 })
    const [supportEnabled, setSupportEnabled] = useState(false)

    const fetchData = async () => {
        setIsLoading(true)
        try {
            const [clientsRes, docsRes] = await Promise.all([
                authApi.listClients(),
                documentApi.list()
            ])
            setCounts({
                clients: clientsRes.data.length,
                documents: docsRes.data.length,
                downloads: 0 // Placeholder
            })
        } catch (err) {
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleSync = async () => {
        toast.promise(
            new Promise(resolve => setTimeout(resolve, 1500)), // Placeholder for real sync
            {
                loading: 'Contacting Authority...',
                success: 'License Verified Successfully!',
                error: 'Connection Lost',
            }
        )
    }

    const stats = [
        { label: 'Active Clients', value: isLoading ? '...' : counts.clients.toString(), icon: Users, color: 'text-blue-600', bg: 'bg-blue-100' },
        { label: 'Documents Shared', value: isLoading ? '...' : counts.documents.toString(), icon: FileText, color: 'text-green-600', bg: 'bg-green-100' },
        { label: 'Client Downloads', value: counts.downloads.toString(), icon: Download, color: 'text-purple-600', bg: 'bg-purple-100' },
        { label: 'Pending Messages', value: '0', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
    ]

    return (
        <div className="space-y-8 animate-slide-in-up">
            {/* Header with gradient background */}
            <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 rounded-3xl p-8 overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
                
                <div className="relative z-10 flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold text-white tracking-tight mb-2">
                            Welcome back, {user?.name || 'Admin'}! 👋
                        </h1>
                        <p className="text-blue-100 text-lg font-medium">
                            Here's what's happening with your practice today
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <button className="px-6 py-3 bg-white/20 backdrop-blur-sm border border-white/30 text-white rounded-xl font-semibold hover:bg-white/30 transition-all duration-300 hover:scale-105 shadow-lg">
                            Export Report
                        </button>
                        <button 
                            onClick={fetchData}
                            className="px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-all duration-300 hover:scale-105 shadow-xl flex items-center gap-2"
                        >
                            <RefreshCw size={18} />
                            Refresh
                        </button>
                    </div>
                </div>
            </div>

            {/* Stats Cards with enhanced design */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat, idx) => (
                    <div 
                        key={stat.label} 
                        className={`group relative bg-white p-6 rounded-2xl shadow-lg border-2 border-gray-100 hover:border-${stat.color.replace('text-', '')} transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 cursor-pointer overflow-hidden stagger-${idx + 1} animate-slide-in-up`}
                    >
                        {/* Gradient background on hover */}
                        <div className="absolute inset-0 bg-gradient-to-br from-transparent to-gray-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        
                        <div className="relative z-10 flex items-start justify-between">
                            <div className="flex-1">
                                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                                    {stat.label}
                                </p>
                                <p className="text-4xl font-black text-gray-900 mb-1 group-hover:scale-110 transition-transform duration-300">
                                    {stat.value}
                                </p>
                                <p className="text-sm text-gray-500 font-medium">
                                    {stat.label === 'Active Clients' && 'Total active'}
                                    {stat.label === 'Documents Shared' && 'This month'}
                                    {stat.label === 'Client Downloads' && 'All time'}
                                    {stat.label === 'Pending Messages' && 'Unread'}
                                </p>
                            </div>
                            <div className={`p-4 rounded-2xl ${stat.bg} ${stat.color} group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg`}>
                                <stat.icon size={28} strokeWidth={2.5} />
                            </div>
                        </div>
                        
                        {/* Progress bar */}
                        <div className="relative z-10 mt-4 h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div 
                                className={`h-full bg-gradient-to-r ${stat.bg.replace('bg-', 'from-')} ${stat.color.replace('text-', 'to-')} rounded-full transition-all duration-1000 group-hover:w-full`}
                                style={{ width: '70%' }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content Area */}
                <div className="lg:col-span-3 space-y-8">
                    {/* Recent Activity */}
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                            <h3 className="font-bold text-slate-900 flex items-center gap-2">
                                <Clock className="text-slate-400" size={18} />
                                Recent Activity
                            </h3>
                            <button className="text-xs font-bold text-blue-600 hover:text-blue-700 uppercase tracking-wider">View All</button>
                        </div>
                        <div className="divide-y divide-slate-50">
                            {[
                                { name: 'Rajesh Kumar', action: 'Downloaded GSTR-3B', time: '12 minutes ago', status: 'Success' },
                                { name: 'Anita Sharma', action: 'New Client Registered', time: '1 hour ago', status: 'New' },
                                { name: 'Vikram Mehta', action: 'Uploaded ITR Computation', time: '3 hours ago', status: 'Upload' },
                                { name: 'Sunil Gupta', action: 'Logged in to Portal', time: '5 hours ago', status: 'Login' },
                            ].map((item, i) => (
                                <div key={i} className="p-5 flex items-center justify-between hover:bg-slate-50 transition-colors group">
                                    <div className="flex items-center gap-4">
                                        <div className="h-10 w-10 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-500 group-hover:bg-white group-hover:shadow-md transition-all">
                                            {item.name.charAt(0)}
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold text-slate-900">{item.name}</p>
                                            <p className="text-xs text-slate-500 font-medium">{item.action}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-xs text-slate-400 font-bold">{item.time}</p>
                                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${item.status === 'Success' ? 'bg-green-100 text-green-600' :
                                            item.status === 'New' ? 'bg-blue-100 text-blue-600' :
                                                'bg-slate-100 text-slate-500'
                                            }`}>
                                            {item.status}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
