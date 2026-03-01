
import { useState } from 'react'
import { FolderOpen, Download, FileText, ChevronRight, ChevronDown, Clock } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { documentApi, messageApi } from '../../api'
import toast from 'react-hot-toast'

interface Document {
    id: number
    file_name: string
    year: string
    document_type: string
    file_size: number
    uploaded_at: string
}

interface SharedFile {
    id: number
    file_name: string
    description: string
    file_size: number
    sent_at: string
    is_downloaded: boolean
}

export default function ClientDocuments() {
    const [expandedYears, setExpandedYears] = useState<string[]>([])

    const { data: documents, isLoading: docsLoading } = useQuery({
        queryKey: ['documents'],
        queryFn: () => documentApi.list().then(res => res.data),
    })

    const { data: sharedFiles, isLoading: sharedLoading } = useQuery({
        queryKey: ['shared-files'],
        queryFn: () => messageApi.listSharedFiles().then(res => res.data),
    })

    const handleDownload = async (docId: number) => {
        try {
            const response = await documentApi.getDownloadToken(docId)
            const { token } = response.data
            window.open(documentApi.download(token), '_blank')
        } catch (error) {
            toast.error('Failed to generate download link.')
        }
    }

    const handleSharedDownload = async (fileId: number) => {
        try {
            // Assuming messageApi has getSharedFileDownloadToken or similar
            // Wait, we implemented getSharedFileDownloadToken in backend but didn't update frontend API module fully?
            // Let's check api/index.ts. 
            // We need to update api/index.ts to include this method. 
            // Assuming it exists for now, we will fix it in next step.
            const response = await messageApi.getSharedFileDownloadToken(fileId)
            const { token } = response.data
            window.open(messageApi.downloadSharedFile(token), '_blank')
        } catch (error) {
            toast.error('Failed to download file.')
        }
    }

    const toggleYear = (year: string) => {
        setExpandedYears(prev => 
            prev.includes(year) ? prev.filter(y => y !== year) : [...prev, year]
        )
    }

    // Group documents by year
    const docsByYear = (documents || []).reduce((acc: any, doc: Document) => {
        if (!acc[doc.year]) acc[doc.year] = []
        acc[doc.year].push(doc)
        return acc
    }, {})

    const years = Object.keys(docsByYear).sort((a, b) => b.localeCompare(a))

    if (docsLoading || sharedLoading) {
        return <div className="p-12 text-center text-slate-400 font-bold uppercase tracking-widest animate-pulse">Loading documents...</div>
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Shared Files Section */}
            {sharedFiles && sharedFiles.length > 0 && (
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-blue-50/50">
                        <h3 className="font-bold text-slate-900 flex items-center gap-2">
                            <FolderOpen className="text-blue-600" size={20} />
                            Files Shared by CA
                        </h3>
                        <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded-lg">
                            {sharedFiles.length} New
                        </span>
                    </div>
                    <div className="divide-y divide-slate-50">
                        {sharedFiles.map((file: SharedFile) => (
                            <div key={file.id} className="p-4 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center">
                                        <FileText size={20} />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-slate-900">{file.file_name}</p>
                                        <p className="text-xs text-slate-500">{file.description || 'No description'} • {new Date(file.sent_at).toLocaleDateString()}</p>
                                    </div>
                                </div>
                                <button 
                                    onClick={() => handleSharedDownload(file.id)}
                                    className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                                >
                                    <Download size={20} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Yearly Documents */}
            <div className="space-y-4">
                {years.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">
                        <FolderOpen size={48} className="mx-auto mb-4 opacity-50" />
                        <p className="font-bold uppercase tracking-widest text-sm">No documents found</p>
                    </div>
                ) : (
                    years.map(year => (
                        <div key={year} className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                            <button 
                                onClick={() => toggleYear(year)}
                                className="w-full p-6 flex items-center justify-between hover:bg-slate-50 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg transition-transform duration-300 ${expandedYears.includes(year) ? 'rotate-90 bg-slate-100 text-slate-600' : 'text-slate-400'}`}>
                                        <ChevronRight size={20} />
                                    </div>
                                    <h3 className="text-lg font-bold text-slate-900">Financial Year {year}</h3>
                                </div>
                                <span className="text-xs font-bold text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full">
                                    {docsByYear[year].length} Documents
                                </span>
                            </button>
                            
                            {expandedYears.includes(year) && (
                                <div className="border-t border-slate-100 divide-y divide-slate-50 animate-in slide-in-from-top-2 duration-300">
                                    {docsByYear[year].map((doc: Document) => (
                                        <div key={doc.id} className="p-4 pl-16 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                            <div className="flex items-center gap-4">
                                                <FileText className="text-slate-300 group-hover:text-blue-500 transition-colors" size={20} />
                                                <div>
                                                    <p className="text-sm font-bold text-slate-900">{doc.document_type || doc.file_name}</p>
                                                    <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                                                        <span>{doc.file_name}</span>
                                                        <span>•</span>
                                                        <span>{(doc.file_size / 1024 / 1024).toFixed(2)} MB</span>
                                                        <span>•</span>
                                                        <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <button 
                                                onClick={() => handleDownload(doc.id)}
                                                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                            >
                                                <Download size={18} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}
