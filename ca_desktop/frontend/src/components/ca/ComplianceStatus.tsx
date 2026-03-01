
import { CheckCircle, AlertTriangle, XCircle, Search } from 'lucide-react'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { authApi, complianceApi } from '../../api'

export default function ComplianceStatus() {
    const [selectedClient, setSelectedClient] = useState('')
    
    const { data: clients } = useQuery({
        queryKey: ['admin-clients'],
        queryFn: () => authApi.listClients().then(res => res.data),
    })

    const { data: compliance, isLoading } = useQuery({
        queryKey: ['compliance', selectedClient],
        queryFn: () => complianceApi.getClientStatus(selectedClient).then(res => res.data),
        enabled: !!selectedClient
    })

    if (!clients) return <div>Loading...</div>

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                <CheckCircle className="text-green-600" size={20} />
                Compliance Status
            </h3>

            <div className="mb-6">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Select Client</label>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <select
                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all appearance-none"
                        value={selectedClient}
                        onChange={(e) => setSelectedClient(e.target.value)}
                    >
                        <option value="">Choose a client...</option>
                        {clients.map((c: any) => (
                            <option key={c.id} value={c.phone_number}>{c.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {selectedClient && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    {isLoading ? (
                        <div className="text-center py-8 text-slate-400 font-bold uppercase tracking-widest text-xs">Checking compliance...</div>
                    ) : compliance ? (
                        <div className="space-y-6">
                            <div className={`p-4 rounded-xl border ${compliance.is_compliant ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'} flex items-start gap-4`}>
                                <div className={`p-2 rounded-lg ${compliance.is_compliant ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                    {compliance.is_compliant ? <CheckCircle size={24} /> : <AlertTriangle size={24} />}
                                </div>
                                <div>
                                    <h4 className={`font-bold ${compliance.is_compliant ? 'text-green-700' : 'text-red-700'}`}>
                                        {compliance.is_compliant ? 'Fully Compliant' : 'Attention Required'}
                                    </h4>
                                    <p className={`text-sm mt-1 ${compliance.is_compliant ? 'text-green-600' : 'text-red-600'}`}>
                                        {compliance.is_compliant 
                                            ? 'All required documents have been submitted.' 
                                            : `${compliance.missing_count} document(s) missing based on ${compliance.client_type} rules.`}
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {compliance.applicable_rules.map((rule: any) => (
                                    <div key={rule.rule_id} className="border border-slate-100 rounded-xl overflow-hidden">
                                        <div className="bg-slate-50 px-4 py-3 border-b border-slate-100">
                                            <h5 className="font-bold text-slate-700 text-sm">{rule.rule_name}</h5>
                                        </div>
                                        <div className="divide-y divide-slate-50">
                                            {rule.required_documents.map((doc: any) => (
                                                <div key={doc.tag_name} className="px-4 py-3 flex items-center justify-between">
                                                    <div className="flex items-center gap-3">
                                                        {doc.has_document ? (
                                                            <CheckCircle size={16} className="text-green-500" />
                                                        ) : (
                                                            <XCircle size={16} className="text-red-400" />
                                                        )}
                                                        <span className={`text-sm font-medium ${doc.has_document ? 'text-slate-700' : 'text-slate-400'}`}>
                                                            {doc.tag_name}
                                                        </span>
                                                    </div>
                                                    {doc.has_document && (
                                                        <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded">
                                                            {new Date(doc.latest_upload_date).toLocaleDateString()}
                                                        </span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-slate-400">Could not load compliance data.</div>
                    )}
                </div>
            )}
        </div>
    )
}
