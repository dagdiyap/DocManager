
import { useState, useEffect } from 'react'
import { X, User, Phone, Mail, Briefcase } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../../api'
import toast from 'react-hot-toast'
import { InviteModal } from './InviteModal'

interface ClientFormProps {
    isOpen: boolean
    onClose: () => void
    initialData?: any
}

export default function ClientForm({ isOpen, onClose, initialData }: ClientFormProps) {
    const [formData, setFormData] = useState({
        name: '',
        phone_number: '',
        email: '',
        client_type: 'Salaried'
    })
    const [inviteData, setInviteData] = useState<any>(null)
    const [showInviteModal, setShowInviteModal] = useState(false)
    const queryClient = useQueryClient()

    useEffect(() => {
        if (initialData) {
            setFormData({
                name: initialData.name,
                phone_number: initialData.phone_number,
                email: initialData.email || '',
                client_type: initialData.client_type || 'Salaried'
            })
        } else {
            setFormData({
                name: '',
                phone_number: '',
                email: '',
                client_type: 'Salaried'
            })
        }
    }, [initialData, isOpen])

    const createMutation = useMutation({
        mutationFn: (data: any) => authApi.createClient(data),
        onSuccess: (response: any) => {
            toast.success('Client added successfully')
            queryClient.invalidateQueries({ queryKey: ['admin-clients'] })
            
            // Show invite modal with credentials
            if (response.data.invite) {
                setInviteData({
                    ...response.data.invite,
                    clientName: formData.name
                })
                setShowInviteModal(true)
                onClose() // Close the form
            }
        },
        onError: (err: any) => {
            toast.error(err.response?.data?.detail || 'Failed to add client')
        }
    })

    const updateMutation = useMutation({
        mutationFn: (data: any) => authApi.updateClient(initialData.phone_number, data),
        onSuccess: () => {
            toast.success('Client updated successfully')
            queryClient.invalidateQueries({ queryKey: ['admin-clients'] })
            onClose()
        },
        onError: (err: any) => {
            toast.error(err.response?.data?.detail || 'Failed to update client')
        }
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (initialData) {
            const updateData: any = {
                name: formData.name,
                email: formData.email,
                client_type: formData.client_type
            }
            // Only send fields that are allowed to be updated
            // Assuming phone number is primary key/immutable via this form for now
            updateMutation.mutate(updateData)
        } else {
            createMutation.mutate(formData)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <h3 className="text-lg font-bold text-slate-900">
                        {initialData ? 'Edit Client' : 'Add New Client'}
                    </h3>
                    <button 
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Full Name</label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <input 
                                type="text"
                                required
                                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium"
                                placeholder="Amit Sharma"
                                value={formData.name}
                                onChange={e => setFormData({...formData, name: e.target.value})}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Phone Number</label>
                        <div className="relative">
                            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <input 
                                type="tel"
                                required
                                disabled={!!initialData}
                                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed"
                                placeholder="9876543210"
                                value={formData.phone_number}
                                onChange={e => setFormData({...formData, phone_number: e.target.value})}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Email (Optional)</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <input 
                                type="email"
                                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium"
                                placeholder="client@example.com"
                                value={formData.email}
                                onChange={e => setFormData({...formData, email: e.target.value})}
                            />
                        </div>
                    </div>

                    {!initialData && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <p className="text-xs text-blue-800">
                                <strong>🔐 Auto-Generated Password:</strong> A secure password will be automatically generated for this client. You'll receive it in the invite card after creation.
                            </p>
                        </div>
                    )}

                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Client Type</label>
                        <div className="relative">
                            <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <select
                                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium appearance-none"
                                value={formData.client_type}
                                onChange={e => setFormData({...formData, client_type: e.target.value})}
                            >
                                <option value="Salaried">Salaried</option>
                                <option value="Business">Business</option>
                                <option value="Partnership">Partnership</option>
                            </select>
                        </div>
                    </div>

                    <div className="pt-4">
                        <button 
                            type="submit"
                            disabled={createMutation.isPending || updateMutation.isPending}
                            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {createMutation.isPending || updateMutation.isPending ? 'Saving...' : (initialData ? 'Update Client' : 'Create Client')}
                        </button>
                    </div>
                </form>
            </div>

            {/* Invite Modal */}
            <InviteModal
                isOpen={showInviteModal}
                onClose={() => setShowInviteModal(false)}
                inviteData={inviteData}
                clientName={inviteData?.clientName || ''}
            />
        </div>
    )
}
