import {
    Folder,
    Search,
    FileText,
    ChevronRight,
    Download,
    Filter,
    Calendar,
    MoreVertical,
    Upload,
    ArrowLeft,
    Eye
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { documentApi, authApi } from '../../api'
import { toast } from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

export default function DocumentBrowser() {
    const [currentFolder, setCurrentFolder] = useState<string | null>(null)
    const [currentClientName, setCurrentClientName] = useState<string | null>(null)
    const [documents, setDocuments] = useState([])
    const [clients, setClients] = useState([])
    const [isLoading, setIsLoading] = useState(true)
    const navigate = useNavigate()

    const fetchDocs = async () => {
        setIsLoading(true)
        try {
            const [docsRes, clientsRes] = await Promise.all([
                documentApi.list(),
                authApi.listClients()
            ])
            setDocuments(docsRes.data)
            setClients(clientsRes.data)
        } catch (err) {
            console.error(err)
            toast.error("Failed to load documents")
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchDocs()
    }, [])

    const handleScan = async () => {
        try {
            await documentApi.list() // Triggering list also scans in current PoC logic
            toast.success("Folder scan triggered")
            fetchDocs()
        } catch (err) {
            toast.error("Scan failed")
        }
    }

    // Grouping logic for folder view - by client full name
    const clientFolders = Array.from(new Set(documents.map((d: any) => d.client_phone))).map(phone => {
        const docs = documents.filter((d: any) => d.client_phone === phone)
        const client: any = clients.find((c: any) => c.phone_number === phone)
        return {
            name: client?.name || `Client ${phone.slice(-4)}`,
            phone: phone,
            count: docs.length,
            years: Array.from(new Set(docs.map((d: any) => d.year)))
        }
    })

    const currentFiles = documents.filter((d: any) => d.client_phone === currentFolder)

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Documents</h1>
                    <nav className="flex items-center gap-2 mt-1 text-sm font-medium text-slate-400">
                        {currentFolder ? (
                            <>
                                <button onClick={() => { setCurrentFolder(null); setCurrentClientName(null); }} className="hover:text-blue-600 transition-colors">All Clients</button>
                                <ChevronRight size={14} />
                                <span className="text-slate-900 font-semibold">{currentClientName || currentFolder}</span>
                            </>
                        ) : (
                            <span>All Clients</span>
                        )}
                    </nav>
                </div>
                <div className="flex gap-2">
                    {currentFolder && (
                        <button 
                            onClick={() => { setCurrentFolder(null); setCurrentClientName(null); }}
                            className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl font-bold text-sm shadow-sm hover:bg-slate-200 transition-all"
                        >
                            <ArrowLeft size={16} /> Back
                        </button>
                    )}
                    <button 
                        onClick={() => navigate('/ca/documents/upload')}
                        className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all"
                    >
                        <Upload size={16} /> Upload
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl font-bold text-sm shadow-sm hover:bg-slate-50 transition-all">
                        <Filter size={16} /> Filter
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 min-h-[500px] flex flex-col">
                {/* Browser Top Bar */}
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                    <div className="relative w-80">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                        <input
                            type="text"
                            placeholder="Search files..."
                            className="w-full pl-10 pr-4 py-2 bg-slate-50 border-none rounded-lg focus:ring-2 focus:ring-blue-500/10 text-sm font-medium"
                        />
                    </div>
                    <div className="flex items-center gap-4 text-slate-400">
                        <button className="hover:text-slate-600"><Calendar size={18} /></button>
                        <div className="h-4 w-[1px] bg-slate-200"></div>
                        <p className="text-xs font-bold uppercase tracking-widest">{clientFolders.length} Folders / {documents.length} Files</p>
                    </div>
                </div>

                {/* Browser Grid */}
                <div className="flex-1 p-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
                        {!currentFolder ? (
                            // Folder View
                            clientFolders.map((folder) => (
                                <div
                                    key={folder.phone}
                                    onClick={() => { setCurrentFolder(folder.phone); setCurrentClientName(folder.name); }}
                                    className="group flex flex-col items-center gap-3 cursor-pointer p-4 rounded-xl hover:bg-blue-50/50 transition-all border border-transparent hover:border-blue-100 hover:shadow-sm"
                                    title={folder.name}
                                >
                                    <div className="relative">
                                        <Folder size={64} className="text-blue-500 fill-blue-500/10 transition-transform group-hover:scale-110 duration-300" />
                                    </div>
                                    <div className="text-center w-full">
                                        <p className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors truncate px-2" title={folder.name}>{folder.name}</p>
                                        <p className="text-[10px] font-bold text-slate-400 uppercase leading-none mt-1">{folder.count} Documents</p>
                                    </div>
                                </div>
                            ))
                        ) : (
                            // File View (Simplified for Demo)
                            currentFiles.map((file: any) => (
                                <div
                                    key={file.id}
                                    className="group flex flex-col items-center gap-3 cursor-pointer p-4 rounded-xl hover:bg-slate-50 transition-all border border-transparent hover:border-slate-100 relative shadow-sm hover:shadow-md"
                                    title={file.file_name}
                                >
                                    <div className="flex flex-col items-center">
                                        <FileText size={48} className="text-slate-300 transition-transform group-hover:scale-105" />
                                        <span className="text-[8px] font-black uppercase tracking-tighter bg-red-500 text-white px-1 rounded-sm -mt-2 z-10">
                                            {file.document_type || 'PDF'}
                                        </span>
                                    </div>
                                    <div className="text-center w-full">
                                        <p className="text-[11px] font-bold text-slate-800 truncate px-2" title={file.file_name}>{file.file_name}</p>
                                        <p className="text-base font-black text-blue-600 mt-1">{file.year}</p>
                                    </div>

                                    {/* Hover Actions */}
                                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col gap-1">
                                        <button 
                                            onClick={(e) => { e.stopPropagation(); /* Preview logic */ }}
                                            className="p-1.5 bg-white shadow-md rounded-lg text-green-600 hover:bg-green-600 hover:text-white transition-colors"
                                            title="Preview"
                                        >
                                            <Eye size={12} />
                                        </button>
                                        <button 
                                            className="p-1.5 bg-white shadow-md rounded-lg text-blue-600 hover:bg-blue-600 hover:text-white transition-colors"
                                            title="Download"
                                        >
                                            <Download size={12} />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {(!currentFolder && clientFolders.length === 0 && !isLoading) && (
                        <div className="h-full py-24 flex flex-col items-center justify-center text-slate-400 opacity-50 space-y-4">
                            <Folder size={80} strokeWidth={1} />
                            <p className="font-bold uppercase tracking-widest text-sm text-center">No client folders detected.<br />Ensure phone-based folder structure is followed.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
