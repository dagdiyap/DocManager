import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, Lock, Mail, User, ArrowRight, AlertCircle } from 'lucide-react'
import { authApi } from '../../api'
import { useAuth } from '../../contexts/AuthContext'
import toast from 'react-hot-toast'

export default function CALogin() {
    const [isLogin, setIsLogin] = useState(true)
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: ''
    })
    const [isLoading, setIsLoading] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)

        try {
            if (isLogin) {
                const data = new FormData()
                data.append('username', formData.username)
                data.append('password', formData.password)
                
                const response = await authApi.login(data)
                const { access_token, user_type } = response.data
                
                // For CA, we might not get user details in login response payload directly in schema, 
                // but we can infer or fetch. For MVP, we'll store minimal.
                login(access_token, user_type as 'ca' | 'client', { name: formData.username })
                toast.success('Welcome back, Admin!')
            } else {
                // Register
                await authApi.register({
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                })
                toast.success('Registration successful! Please login.')
                setIsLogin(true)
            }
        } catch (error: any) {
            console.error(error)
            toast.error(error.response?.data?.detail || 'Authentication failed')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 relative overflow-hidden">
            {/* Animated background blobs */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
            <div className="absolute top-0 right-0 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
            <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
            
            <div className="max-w-5xl w-full bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row relative z-10 animate-slide-in-up">
                
                {/* Left Side - Brand with gradient */}
                <div className="md:w-1/2 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 p-12 text-white flex flex-col justify-between relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl"></div>
                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl"></div>
                    
                    <div className="relative z-10">
                        <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 shadow-2xl shadow-blue-900/50 animate-float">
                            <ShieldCheck size={32} strokeWidth={2.5} />
                        </div>
                        <h1 className="text-4xl font-bold tracking-tight mb-3">DocManager <span className="text-blue-400">CA</span></h1>
                        <p className="text-blue-200 text-lg font-medium">Secure Document Management System</p>
                    </div>

                    <div className="relative z-10 space-y-6">
                        <div className="space-y-3">
                            <h3 className="font-bold text-xl text-white">For Chartered Accountants</h3>
                            <p className="text-blue-200 text-base leading-relaxed">
                                Manage client documents, compliance calendars, and secure sharing from your local machine.
                            </p>
                        </div>
                        <div className="pt-6 border-t border-white/20">
                            <p className="text-xs uppercase tracking-widest text-blue-300 font-bold">Version 0.1.0-MVP</p>
                        </div>
                    </div>
                </div>

                {/* Right Side - Form with enhanced styling */}
                <div className="md:w-1/2 p-12 flex flex-col justify-center bg-gradient-to-br from-white to-blue-50">
                    <div className="mb-8">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">{isLogin ? 'Welcome Back! 👋' : 'Setup Admin Account'}</h2>
                        <p className="text-gray-600 text-base">
                            {isLogin ? 'Enter your credentials to access the dashboard.' : 'Create the main administrator account.'}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">Username</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                                    <input 
                                        type="text" 
                                        required
                                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium"
                                        placeholder="admin"
                                        value={formData.username}
                                        onChange={e => setFormData({...formData, username: e.target.value})}
                                    />
                                </div>
                            </div>

                            {!isLogin && (
                                <div className="animate-in slide-in-from-top-2 duration-300">
                                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">Email Address</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                                        <input 
                                            type="email" 
                                            required={!isLogin}
                                            className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium"
                                            placeholder="ca@firm.com"
                                            value={formData.email}
                                            onChange={e => setFormData({...formData, email: e.target.value})}
                                        />
                                    </div>
                                </div>
                            )}

                            <div>
                                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                                    <input 
                                        type="password" 
                                        required
                                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm font-medium"
                                        placeholder="••••••••"
                                        value={formData.password}
                                        onChange={e => setFormData({...formData, password: e.target.value})}
                                    />
                                </div>
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            disabled={isLoading}
                            className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl font-bold shadow-xl shadow-blue-500/30 hover:shadow-2xl hover:shadow-blue-500/40 transition-all duration-300 hover:scale-105 active:scale-95 flex items-center justify-center gap-2 text-base"
                        >
                            {isLoading ? 'Processing...' : (
                                <>
                                    {isLogin ? 'Sign In' : 'Create Account'} 
                                    <ArrowRight size={18} />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <button 
                            type="button"
                            onClick={() => setIsLogin(!isLogin)}
                            className="text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors"
                        >
                            {isLogin ? 'First time setup? Create Account' : 'Already have an account? Sign In'}
                        </button>
                    </div>
                    
                    {!isLogin && (
                        <div className="mt-4 p-3 bg-amber-50 border border-amber-100 rounded-lg flex items-start gap-3">
                            <AlertCircle className="text-amber-600 shrink-0" size={16} />
                            <p className="text-xs text-amber-700 font-medium">
                                <strong>Note:</strong> Registration is only available for the initial setup. Once an admin account exists, new registrations will be disabled.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
