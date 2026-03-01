import {
    Send,
    Paperclip,
    Search,
    Plus,
    Smile,
    MoreHorizontal,
    Circle,
    MessageSquare
} from 'lucide-react'
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { messageApi, authApi } from '../../api'
import toast from 'react-hot-toast'

export default function MessagingInterface() {
    const [selectedClient, setSelectedClient] = useState<any | null>(null)
    const [messageText, setMessageText] = useState('')
    const queryClient = useQueryClient()

    // 1. Fetch Clients
    const { data: clients, isLoading: clientsLoading } = useQuery({
        queryKey: ['admin-clients'],
        queryFn: () => authApi.listClients ? authApi.listClients().then(res => res.data) : Promise.resolve([]),
    })

    // 2. Fetch Messages for selected client
    const { data: messages, isLoading: messagesLoading } = useQuery({
        queryKey: ['messages', selectedClient?.phone_number],
        queryFn: () => messageApi.list().then(res => res.data.filter((m: any) => m.client_phone === selectedClient?.phone_number)),
        enabled: !!selectedClient
    })

    // 3. Send Message Mutation
    const sendMessageMutation = useMutation({
        mutationFn: (msg: { client_phone: string, subject: string, body: string }) =>
            messageApi.send ? messageApi.send(msg) : Promise.resolve({}),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['messages', selectedClient?.phone_number] })
            setMessageText('')
            toast.success('Message sent!')
        },
        onError: () => toast.error('Failed to send message.')
    })

    const handleSend = () => {
        if (!selectedClient || !messageText.trim()) return
        sendMessageMutation.mutate({
            client_phone: selectedClient.phone_number,
            subject: `Update from CA`,
            body: messageText
        })
    }

    return (
        <div className="h-[calc(100vh-10rem)] flex bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100 animate-in zoom-in-95 duration-500">
            {/* Thread List */}
            <aside className="w-80 border-r border-slate-50 flex flex-col bg-slate-50/30">
                <div className="p-6 border-b border-slate-100">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-black text-slate-900 uppercase tracking-widest text-sm">Client Inbox</h3>
                        <button className="p-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-md shadow-blue-500/20">
                            <Plus size={16} />
                        </button>
                    </div>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                        <input
                            type="text"
                            placeholder="Search clients..."
                            className="w-full pl-9 pr-4 py-2 bg-white border border-slate-100 rounded-xl text-xs font-medium focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                    </div>
                </div>

                <div className="flex-1 overflow-auto divide-y divide-slate-50">
                    {clientsLoading ? (
                        <div className="p-8 text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest animate-pulse">Loading...</div>
                    ) : (clients || []).map((chat: any) => (
                        <button
                            key={chat.id}
                            onClick={() => setSelectedClient(chat)}
                            className={`w-full p-4 flex items-center gap-3 transition-all hover:bg-white text-left ${selectedClient?.id === chat.id ? 'bg-white border-l-4 border-blue-600 shadow-sm z-10' : ''}`}
                        >
                            <div className="relative flex-shrink-0">
                                <div className="h-10 w-10 bg-slate-200 rounded-2xl flex items-center justify-center font-bold text-slate-500">
                                    {chat.name.charAt(0)}
                                </div>
                                {chat.is_active && <Circle size={10} className="absolute -bottom-0.5 -right-0.5 text-green-500 fill-green-500 border-2 border-white rounded-full" />}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-baseline">
                                    <p className="text-sm font-bold text-slate-900 truncate">{chat.name}</p>
                                </div>
                                <p className="text-xs text-slate-500 truncate mt-0.5 font-medium">{chat.phone_number}</p>
                            </div>
                        </button>
                    ))}
                </div>
            </aside>

            {/* Chat Area */}
            <main className="flex-1 flex flex-col relative bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-fixed opacity-95">
                {!selectedClient ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-300 space-y-4">
                        <MessageSquare size={100} strokeWidth={1} />
                        <p className="font-black uppercase tracking-[0.2em] text-sm">Select a client to message</p>
                    </div>
                ) : (
                    <>
                        {/* Chat Header */}
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-white/80 backdrop-blur-md">
                            <div className="flex items-center gap-4">
                                <div className="h-10 w-10 bg-blue-600 rounded-2xl flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/30">
                                    {selectedClient.name.charAt(0)}
                                </div>
                                <div>
                                    <h4 className="font-bold text-slate-900">{selectedClient.name}</h4>
                                    <p className="text-[10px] text-green-500 font-bold uppercase tracking-wider flex items-center gap-1">
                                        <Circle size={8} fill="currentColor" /> {selectedClient.is_active ? 'Active' : 'Inactive'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 text-slate-400">
                                <button className="p-2 hover:bg-slate-100 rounded-xl transition-colors"><Paperclip size={20} /></button>
                                <button className="p-2 hover:bg-slate-100 rounded-xl transition-colors"><MoreHorizontal size={20} /></button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-auto p-8 space-y-6">
                            {messagesLoading ? (
                                <div className="text-center font-bold text-[10px] text-slate-300 uppercase tracking-widest">Fetching history...</div>
                            ) : (messages || []).map((msg: any) => (
                                <div key={msg.id} className="flex justify-end">
                                    <div className="max-w-[70%] group order-1">
                                        <div className="p-4 rounded-2xl text-sm font-medium shadow-sm transition-transform hover:scale-[1.01] bg-blue-600 text-white rounded-br-none">
                                            {msg.body}
                                        </div>
                                        <p className="text-[10px] font-bold text-slate-400 mt-2 px-1 text-right">
                                            {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Input Area */}
                        <div className="p-4 bg-white/80 backdrop-blur-md border-t border-slate-100">
                            <div className="flex items-center gap-3 p-2 bg-slate-50 border border-slate-200 rounded-2xl focus-within:ring-4 focus-within:ring-blue-100 focus-within:bg-white transition-all shadow-inner">
                                <button className="p-2 text-slate-400 hover:text-blue-600 transition-colors"><Smile size={20} /></button>
                                <input
                                    type="text"
                                    placeholder="Type your message here..."
                                    className="flex-1 bg-transparent border-none outline-none text-sm font-medium text-slate-700"
                                    value={messageText}
                                    onChange={(e) => setMessageText(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={sendMessageMutation.isPending || !messageText.trim()}
                                    className="bg-blue-600 text-white p-3 rounded-xl shadow-lg shadow-blue-500/40 hover:bg-blue-700 transition hover:scale-105 active:scale-95 disabled:opacity-50"
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    )
}
