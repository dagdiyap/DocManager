
import { useState, useRef } from 'react'
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi, documentApi } from '../../api'
import toast from 'react-hot-toast'

export default function DocumentUpload() {
    const [selectedClient, setSelectedClient] = useState('')
    const [year, setYear] = useState(new Date().getFullYear().toString())
    const [files, setFiles] = useState<File[]>([])
    const [dragActive, setDragActive] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const folderInputRef = useRef<HTMLInputElement>(null)
    const queryClient = useQueryClient()

    const { data: clients, isLoading: clientsLoading } = useQuery({
        queryKey: ['admin-clients'],
        queryFn: () => authApi.listClients().then(res => res.data),
    })

    const uploadMutation = useMutation({
        mutationFn: async (formDataArray: FormData[]) => {
            const results = []
            for (const formData of formDataArray) {
                const result = await documentApi.upload(formData)
                results.push(result)
            }
            return results
        },
        onSuccess: (results) => {
            toast.success(`${results.length} document(s) uploaded successfully!`)
            setFiles([])
            queryClient.invalidateQueries({ queryKey: ['documents'] })
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Upload failed')
        }
    })

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true)
        } else if (e.type === 'dragleave') {
            setDragActive(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFiles(Array.from(e.dataTransfer.files))
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files))
        }
    }
    
    const handleFolderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files))
        }
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (files.length === 0 || !selectedClient || !year) {
            toast.error('Please fill all fields and select at least one file')
            return
        }

        const formDataArray = files.map(file => {
            const formData = new FormData()
            formData.append('file', file)
            formData.append('client_phone', selectedClient)
            formData.append('year', year)
            return formData
        })

        uploadMutation.mutate(formDataArray)
    }

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                <Upload className="text-blue-600" size={20} />
                Upload Document
            </h3>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Client</label>
                        <select
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                            value={selectedClient}
                            onChange={(e) => setSelectedClient(e.target.value)}
                            required
                        >
                            <option value="">Select Client</option>
                            {clientsLoading ? (
                                <option disabled>Loading...</option>
                            ) : (
                                clients?.map((client: any) => (
                                    <option key={client.id} value={client.phone_number}>
                                        {client.name} ({client.phone_number})
                                    </option>
                                ))
                            )}
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Year</label>
                        <input
                            type="text"
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                            value={year}
                            onChange={(e) => setYear(e.target.value)}
                            placeholder="YYYY"
                            required
                        />
                    </div>
                </div>

                {/* Drag & Drop Area */}
                <div
                    className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all cursor-pointer ${
                        dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:bg-slate-50'
                    } ${files.length > 0 ? 'bg-green-50 border-green-200' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleChange}
                        accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.doc,.docx,.zip,.txt"
                        multiple
                    />
                    <input
                        ref={folderInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleFolderChange}
                        {...({ webkitdirectory: "", directory: "" } as any)}
                        multiple
                    />

                    {files.length > 0 ? (
                        <div className="w-full max-h-64 overflow-y-auto space-y-2">
                            <div className="flex items-center justify-between mb-3">
                                <p className="text-sm font-bold text-slate-900">{files.length} file(s) selected</p>
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        setFiles([])
                                    }}
                                    className="text-xs font-bold text-red-500 hover:text-red-700 flex items-center gap-1"
                                >
                                    <X size={12} /> Clear All
                                </button>
                            </div>
                            {files.map((file, idx) => (
                                <div key={idx} className="flex items-center gap-3 p-2 bg-white rounded-lg border border-slate-200">
                                    <FileText size={20} className="text-blue-600" />
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold text-slate-900 truncate">{file.name}</p>
                                        <p className="text-[10px] text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            setFiles(files.filter((_, i) => i !== idx))
                                        }}
                                        className="text-red-500 hover:text-red-700"
                                    >
                                        <X size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center text-center">
                            <div className="h-12 w-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-3">
                                <Upload size={24} />
                            </div>
                            <p className="text-sm font-bold text-slate-700">Click to upload or drag and drop</p>
                            <p className="text-xs text-slate-400 mt-1 font-medium">Multiple files or folders supported</p>
                            <div className="flex gap-2 mt-4">
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        folderInputRef.current?.click()
                                    }}
                                    className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-bold hover:bg-blue-200 transition-colors"
                                >
                                    Upload Folder
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={uploadMutation.isPending || files.length === 0 || !selectedClient}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {uploadMutation.isPending ? `Uploading ${files.length} file(s)...` : `Upload ${files.length > 0 ? files.length + ' Document(s)' : 'Documents'}`}
                </button>
            </form>
        </div>
    )
}
