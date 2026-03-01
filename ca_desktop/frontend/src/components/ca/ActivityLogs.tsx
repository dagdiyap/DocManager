
import {
    History,
    Search,
    Download,
    LogIn,
    ShieldAlert,
    Filter,
    FileSearch,
    ChevronLeft,
    ChevronRight
} from 'lucide-react'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../../api'

export default function ActivityLogs() {
    const [page, setPage] = useState(0)
    const limit = 20
    const [filterType, setFilterType] = useState<string | null>(null)

    const { data: logs, isLoading } = useQuery({
        queryKey: ['audit-logs', page, filterType],
        queryFn: () => api.get('/auth/audit-logs', { params: { limit, offset: page * limit, event_type: filterType } }).then(res => res.data),
    })

    return (
        <div className="space-y-6 animate-in slide-in-from-right-4 duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Audit Logs</h1>
                    <p className="text-slate-500 font-medium">Security and access history for your practice.</p>
                </div>
                <div className="flex gap-2">
                    <select 
                        className="px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl font-bold text-sm shadow-sm hover:bg-slate-50 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                        onChange={(e) => setFilterType(e.target.value || null)}
                        value={filterType || ''}
                    >
                        <option value="">All Events</option>
                        <option value="LOGIN">Login</option>
                        <option value="DOWNLOAD">Download</option>
                        <option value="UPLOAD">Upload</option>
                        <option value="SECURITY">Security</option>
                    </select>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50 text-[10px] uppercase tracking-widest font-black text-slate-400">
                                <th className="px-6 py-4">Event Type</th>
                                <th className="px-6 py-4">User</th>
                                <th className="px-6 py-4">Details</th>
                                <th className="px-6 py-4">IP Address</th>
                                <th className="px-6 py-4">Timestamp</th>
                                <th className="px-6 py-4">Severity</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {isLoading ? (
                                <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400 font-bold uppercase tracking-widest">Loading logs...</td></tr>
                            ) : logs?.length === 0 ? (
                                <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-400 font-bold uppercase tracking-widest">No logs found</td></tr>
                            ) : logs?.map((log: any) => (
                                <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            {log.event_type.includes('DOWNLOAD') && <Download size={14} className="text-purple-500" />}
                                            {log.event_type.includes('LOGIN') && <LogIn size={14} className="text-blue-500" />}
                                            {log.severity === 'WARNING' && <ShieldAlert size={14} className="text-red-500" />}
                                            <span className="text-xs font-bold text-slate-700">{log.event_type}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded-md">{log.user_id || 'System'}</span>
                                        <span className="text-[10px] text-slate-400 ml-1 uppercase">{log.user_type}</span>
                                    </td>
                                    <td className="px-6 py-4 max-w-md truncate">
                                        <span className="text-xs font-medium text-slate-600" title={log.event_details}>{log.event_details || '-'}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-xs font-mono text-slate-400">{log.ip_address}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-xs font-medium text-slate-500">{new Date(log.created_at).toLocaleString()}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${
                                            log.severity === 'INFO' ? 'bg-blue-100 text-blue-600' :
                                            log.severity === 'WARNING' ? 'bg-amber-100 text-amber-600' :
                                            'bg-red-100 text-red-600'
                                        }`}>
                                            {log.severity}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                
                {/* Pagination */}
                <div className="p-4 border-t border-slate-100 flex items-center justify-between">
                    <button 
                        onClick={() => setPage(p => Math.max(0, p - 1))}
                        disabled={page === 0}
                        className="p-2 text-slate-400 hover:text-slate-600 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Page {page + 1}</span>
                    <button 
                        onClick={() => setPage(p => p + 1)}
                        disabled={logs?.length < limit}
                        className="p-2 text-slate-400 hover:text-slate-600 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>
        </div>
    )
}
