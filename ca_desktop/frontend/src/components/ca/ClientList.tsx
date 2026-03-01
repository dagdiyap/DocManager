import {
    Search,
    UserPlus,
    MoreVertical,
    MessageSquare,
    Eye,
    Trash2,
    Mail,
    Phone,
    Briefcase,
    Upload
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { authApi } from '../../api'
import { toast } from 'react-hot-toast'
import ClientForm from './ClientForm'
import { BulkClientUpload } from './BulkClientUpload'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export default function ClientList() {
    const [searchTerm, setSearchTerm] = useState('')
    const [isFormOpen, setIsFormOpen] = useState(false)
    const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false)
    const [editingClient, setEditingClient] = useState<any>(null)
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: clients, isLoading } = useQuery({
        queryKey: ['admin-clients'],
        queryFn: () => authApi.listClients().then(res => res.data),
    })

    const deleteMutation = useMutation({
        mutationFn: (phone: string) => authApi.deleteClient(phone),
        onSuccess: () => {
            toast.success('Client deactivated')
            queryClient.invalidateQueries({ queryKey: ['admin-clients'] })
        },
        onError: () => toast.error('Failed to deactivate client')
    })

    const filteredClients = (clients || []).filter((c: any) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.phone_number.includes(searchTerm) ||
        (c.email && c.email.toLowerCase().includes(searchTerm.toLowerCase()))
    )

    const handleAdd = () => {
        setEditingClient(null)
        setIsFormOpen(true)
    }

    const handleEdit = (client: any) => {
        setEditingClient(client)
        setIsFormOpen(true)
    }

    const handleDelete = (phone: string) => {
        if (confirm('Are you sure you want to deactivate this client?')) {
            deleteMutation.mutate(phone)
        }
    }

    return (
        <div className="space-y-6 animate-slide-in-up">
            {/* Enhanced Header */}
            <div className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 rounded-3xl p-8 overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-black/20"></div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"></div>
                
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-4xl font-bold text-white tracking-tight mb-2">Client Management</h1>
                        <p className="text-blue-200 text-lg font-medium">Manage your client database and folders</p>
                    </div>
                    <div className="flex gap-3">
                        <button 
                            onClick={() => setIsBulkUploadOpen(true)}
                            className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-xl font-bold shadow-xl hover:bg-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                        >
                            <Upload size={20} />
                            <span>Bulk Upload</span>
                        </button>
                        <button 
                            onClick={handleAdd}
                            className="flex items-center justify-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-xl font-bold shadow-xl hover:bg-blue-50 transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                        >
                            <UserPlus size={20} />
                            <span>Add New Client</span>
                        </button>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-100 overflow-hidden">
                {/* Enhanced Search */}
                <div className="p-6 bg-gradient-to-r from-gray-50 to-blue-50 border-b-2 border-gray-200 flex items-center gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-blue-500" size={20} />
                        <input
                            type="text"
                            placeholder="Search by name, phone or email..."
                            className="w-full pl-12 pr-4 py-3.5 bg-white border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-base shadow-sm"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button className="px-4 py-2.5 bg-white border border-slate-200 text-slate-600 rounded-xl text-sm font-bold hover:bg-slate-100 transition-colors">
                        Filters
                    </button>
                </div>

                {/* Table */}
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50/50 text-[10px] uppercase tracking-widest font-black text-slate-400">
                                <th className="px-6 py-4">Client Detail</th>
                                <th className="px-6 py-4">Contact Info</th>
                                <th className="px-6 py-4">Type</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {isLoading ? (
                                <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-400">Loading clients...</td></tr>
                            ) : filteredClients.length === 0 ? (
                                <tr><td colSpan={5} className="px-6 py-12 text-center text-gray-400">No clients found</td></tr>
                            ) : filteredClients.map((client: any) => (
                                <tr key={client.id} className="hover:bg-blue-50/30 transition-colors group">
                                    <td className="px-6 py-4 cursor-pointer" onClick={() => handleEdit(client)}>
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-500 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                                {client.name.charAt(0)}
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-slate-900">{client.name}</p>
                                                <p className="text-[10px] font-black text-slate-400 uppercase">ID: CLI-{1000 + client.id}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 space-y-1">
                                        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                                            <Phone size={12} className="text-slate-400" />
                                            {client.phone_number}
                                        </div>
                                        <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
                                            <Mail size={12} />
                                            {client.email || 'No email provided'}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <Briefcase size={14} className="text-slate-400" />
                                            <span className="text-xs font-bold text-slate-700">{client.client_type || 'Unspecified'}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${client.is_active ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-400'
                                            }`}>
                                            {client.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center justify-center gap-2">
                                            <button 
                                                onClick={() => navigate('/ca/documents')}
                                                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" 
                                                title="View Documents"
                                            >
                                                <Eye size={18} />
                                            </button>
                                            <button 
                                                onClick={() => navigate('/ca/messaging')}
                                                className="p-2 text-slate-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-all" 
                                                title="Send Message"
                                            >
                                                <MessageSquare size={18} />
                                            </button>
                                            <button 
                                                onClick={() => handleDelete(client.phone_number)}
                                                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" 
                                                title="Deactivate"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <ClientForm 
                isOpen={isFormOpen} 
                onClose={() => setIsFormOpen(false)} 
                initialData={editingClient}
            />

            <BulkClientUpload
                isOpen={isBulkUploadOpen}
                onClose={() => setIsBulkUploadOpen(false)}
            />
        </div>
    )
}
