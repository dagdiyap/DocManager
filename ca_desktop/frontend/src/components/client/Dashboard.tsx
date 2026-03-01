import {
    FolderOpen,
    MessageCircle,
    Download,
    LogOut,
    ShieldCheck,
    User,
    ChevronRight,
    Clock,
    Bell
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Outlet, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { documentApi, messageApi } from '../../api'
import toast from 'react-hot-toast'

import ClientDocuments from './ClientDocuments'

export default function PortalDashboard() {
    const { user, logout } = useAuth()
    const [activeTab, setActiveTab] = useState('documents')

    const { data: messages, isLoading: msgsLoading } = useQuery({
        queryKey: ['messages'],
        queryFn: () => messageApi.list().then(res => res.data),
    })

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 flex flex-col font-sans">
            {/* Enhanced Client Header with gradient */}
            <header className="bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 text-white shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
                
                <div className="relative z-10 max-w-6xl mx-auto px-6 h-24 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/30 animate-float">
                            <ShieldCheck size={28} strokeWidth={2.5} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black tracking-tight leading-none">DocManager</h1>
                            <p className="text-xs font-bold text-blue-300 tracking-wider mt-1">Client Portal</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <button className="relative text-blue-200 hover:text-white transition-all duration-300 hover:scale-110">
                            <Bell size={22} />
                            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-blue-400 rounded-full animate-pulse"></span>
                        </button>
                        <div className="h-10 w-[1px] bg-white/20"></div>
                        <div className="flex items-center gap-3">
                            <div className="text-right hidden md:block">
                                <p className="text-base font-bold text-white">{user?.name}</p>
                                <p className="text-xs font-medium text-blue-300">{user?.phone}</p>
                            </div>
                            <button
                                onClick={logout}
                                className="h-11 w-11 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center text-blue-200 hover:text-red-400 hover:bg-red-500/20 transition-all duration-300 border border-white/20 hover:scale-110"
                            >
                                <LogOut size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Container */}
            <main className="flex-1 max-w-6xl mx-auto w-full p-6 md:p-8 space-y-8 animate-slide-in-up">
                {/* Enhanced Navigation Tabs */}
                <div className="bg-white p-3 rounded-2xl shadow-xl border-2 border-gray-100 flex gap-3">
                    <button
                        onClick={() => setActiveTab('documents')}
                        className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-xl font-bold transition-all duration-300 ${activeTab === 'documents' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl shadow-blue-500/30 scale-105' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:scale-105'
                            }`}
                    >
                        <FolderOpen size={22} strokeWidth={2.5} />
                        <span className="text-base">My Documents</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('messages')}
                        className={`flex-1 flex items-center justify-center gap-3 py-4 rounded-xl font-bold transition-all duration-300 ${activeTab === 'messages' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl shadow-blue-500/30 scale-105' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:scale-105'
                            }`}
                    >
                        <MessageCircle size={22} strokeWidth={2.5} />
                        <span className="text-base">Messages</span>
                    </button>
                </div>

                {/* Content Section */}
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-700">
                    {activeTab === 'documents' ? (
                        <ClientDocuments />
                    ) : (
                        <ClientMessagesView messages={messages || []} isLoading={msgsLoading} />
                    )}
                </div>
            </main>

            <footer className="p-8 text-center text-[10px] font-black uppercase text-slate-400 tracking-[0.3em]">
                Proprietary & Encrypted Connection • DocManager MVP
            </footer>
        </div>
    )
}

function ClientDocumentsView({ documents, isLoading, onDownload }: { documents: any[], isLoading: boolean, onDownload: (id: number) => void }) {
    if (isLoading) return <div className="text-center p-12 text-slate-400 font-bold uppercase tracking-widest animate-pulse">Loading documents...</div>

    if (documents.length === 0) {
        return (
            <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden min-h-[400px] flex flex-col items-center justify-center text-slate-300">
                <FolderOpen size={100} strokeWidth={1} />
                <p className="font-black uppercase tracking-widest text-sm mt-4">No documents available</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {documents.map((doc: any) => (
                    <div key={doc.id} className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-xl hover:scale-[1.02] transition-all cursor-default group">
                        <div className="flex justify-between items-start mb-6">
                            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                <FolderOpen size={24} />
                            </div>
                            <button
                                onClick={() => onDownload(doc.id)}
                                className="p-2 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-blue-50 transition-all shadow-sm active:scale-95 transition-transform"
                                title="Download Securely"
                            >
                                <Download size={20} />
                            </button>
                        </div>
                        <h4 className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors uppercase text-sm tracking-tight">{doc.document_type} ({doc.year})</h4>
                        <p className="text-[10px] text-slate-400 font-bold truncate mt-1">{doc.file_name}</p>
                        <div className="flex items-center gap-6 mt-4">
                            <div>
                                <p className="text-[10px] font-black text-slate-400 uppercase">Size</p>
                                <p className="text-xs font-bold text-slate-600">{(doc.file_size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                            <div className="h-6 w-[1px] bg-slate-100"></div>
                            <div>
                                <p className="text-[10px] font-black text-slate-400 uppercase">Released</p>
                                <p className="text-xs font-bold text-slate-600">{new Date(doc.uploaded_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

function ClientMessagesView({ messages, isLoading }: { messages: any[], isLoading: boolean }) {
    if (isLoading) return <div className="text-center p-12 text-slate-400 font-bold uppercase tracking-widest animate-pulse">Loading messages...</div>

    if (messages.length === 0) {
        return (
            <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden min-h-[400px] flex flex-col items-center justify-center text-slate-300">
                <MessageCircle size={100} strokeWidth={1} />
                <p className="font-black uppercase tracking-widest text-sm mt-4">No new messages from your CA</p>
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 gap-4">
            {messages.map((msg: any) => (
                <div key={msg.id} className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 hover:border-blue-100 transition-colors">
                    <div className="flex justify-between items-start mb-3">
                        <h4 className="font-bold text-slate-900">{msg.subject}</h4>
                        <span className="text-[10px] font-black text-slate-400 uppercase bg-slate-50 px-2 py-1 rounded">{new Date(msg.sent_at).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-slate-600 font-medium leading-relaxed">{msg.body}</p>
                </div>
            ))}
        </div>
    )
}
