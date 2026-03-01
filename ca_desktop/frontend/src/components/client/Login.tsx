import { Phone, Lock, ArrowRight, ShieldCheck, HelpCircle } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import toast from 'react-hot-toast'
import { authApi } from '../../api'

export default function PortalLogin() {
    const [phone, setPhone] = useState('')
    const [password, setPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { login } = useAuth()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)

        try {
            const formData = new FormData()
            formData.append('username', phone)
            formData.append('password', password)

            const response = await authApi.login(formData)
            const { access_token, user_type } = response.data

            login(access_token, user_type as 'ca' | 'client', { name: 'Client User', phone: phone })
            toast.success('Welcome back!')
            
            // Redirect to portal after successful login
            if (user_type === 'client') {
                window.location.href = '/portal'
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Invalid phone number or password.')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="h-screen w-screen bg-slate-900 flex flex-col md:flex-row items-center justify-center p-6 relative overflow-hidden font-sans">
            {/* Decorative Elements */}
            <div className="absolute top-0 left-0 w-full h-full opacity-20 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-600 rounded-full mix-blend-screen filter blur-[150px] animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-600 rounded-full mix-blend-screen filter blur-[150px] animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>

            {/* Main Login Card */}
            <div className="bg-slate-800/50 backdrop-blur-xl w-full max-w-5xl rounded-[2.5rem] shadow-2xl border border-white/10 flex flex-col md:flex-row overflow-hidden z-10 animate-in zoom-in-95 duration-700">

                {/* Left Section: Branding & Info */}
                <div className="flex-1 p-12 bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex flex-col justify-between relative group">
                    <div className="absolute bottom-0 right-0 p-4 opacity-5 pointer-events-none group-hover:scale-110 transition-transform duration-1000">
                        <ShieldCheck size={300} strokeWidth={1} />
                    </div>

                    <div>
                        <div className="flex items-center gap-3 mb-10">
                            <div className="h-12 w-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 shadow-lg">
                                <ShieldCheck size={28} />
                            </div>
                            <h1 className="text-2xl font-black tracking-tighter uppercase">DocManager</h1>
                        </div>
                        <h2 className="text-4xl font-black leading-tight mb-6">Access your<br />documents securely.</h2>
                        <p className="text-blue-100 text-lg font-medium leading-relaxed max-w-sm">
                            Your sensitive fiscal files remain protected on your CA's secure encrypted storage.
                        </p>
                    </div>

                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center"><ArrowRight size={14} className="text-blue-200" /></div>
                            <p className="text-sm font-bold text-blue-200 uppercase tracking-widest">End-to-End Encrypted</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center"><ArrowRight size={14} className="text-blue-200" /></div>
                            <p className="text-sm font-bold text-blue-200 uppercase tracking-widest">Zero Cloud Persistence</p>
                        </div>
                    </div>
                </div>

                {/* Right Section: Form */}
                <div className="flex-1 p-12 md:p-16 flex flex-col justify-center">
                    <div className="mb-10 text-center md:text-left">
                        <h3 className="text-3xl font-black text-white mb-2">Client Portal</h3>
                        <p className="text-slate-400 font-medium">Log in using your registered phone number.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Phone Number</label>
                            <div className="relative group">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors">
                                    <Phone size={20} />
                                </div>
                                <input
                                    type="tel"
                                    placeholder="9876543210"
                                    required
                                    className="w-full bg-slate-900 border border-slate-700/50 rounded-2xl pl-12 pr-4 py-4 text-white font-bold placeholder:text-slate-600 focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-lg"
                                    value={phone}
                                    onChange={(e) => setPhone(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Secret Password</label>
                            <div className="relative group">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors">
                                    <Lock size={20} />
                                </div>
                                <input
                                    type="password"
                                    placeholder="••••••••"
                                    required
                                    className="w-full bg-slate-900 border border-slate-700/50 rounded-2xl pl-12 pr-4 py-4 text-white font-bold placeholder:text-slate-600 focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-lg"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="text-right">
                            <button type="button" className="text-xs font-bold text-blue-400 hover:text-blue-300 transition-colors">Forgot Password?</button>
                        </div>

                        <button
                            disabled={isSubmitting}
                            className={`w-full py-5 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-black text-lg shadow-2xl shadow-blue-500/30 transition-all active:scale-95 flex items-center justify-center gap-3 ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
                        >
                            {isSubmitting ? 'Authenticating...' : (
                                <>
                                    Connect Securely <ArrowRight size={20} />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-12 flex items-center justify-center gap-8 pt-10 border-t border-slate-700/30 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 transition-all duration-500">
                        <div className="flex items-center gap-2">
                            <HelpCircle size={16} className="text-slate-400" />
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Support</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <ShieldCheck size={16} className="text-slate-400" />
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Encrypted</span>
                        </div>
                    </div>
                </div>
            </div>

            <p className="mt-8 text-slate-500 text-[10px] font-black uppercase tracking-[0.3em] z-10">
                © 2026 CA Document Manager • Version 0.1.0-MVP
            </p>
        </div>
    )
}
