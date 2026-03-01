import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
    LayoutDashboard,
    Users,
    FolderOpen,
    MessageSquare,
    History,
    ShieldCheck,
    LogOut,
    CheckCircle,
    User,
    Bell
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

export default function Layout() {
    const { logout, user } = useAuth()
    const navigate = useNavigate()

    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/ca' },
        { icon: Users, label: 'Clients', path: '/ca/clients' },
        { icon: FolderOpen, label: 'Documents', path: '/ca/documents' },
        { icon: CheckCircle, label: 'Compliance', path: '/ca/compliance' },
        { icon: Bell, label: 'Reminders', path: '/ca/reminders' },
        { icon: User, label: 'Profile', path: '/ca/profile' },
        { icon: MessageSquare, label: 'Messaging', path: '/ca/messaging' },
        { icon: History, label: 'Activity Logs', path: '/ca/logs' },
    ]

    return (
        <div className="flex h-screen bg-slate-50 font-sans">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-xl">
                <div className="p-6 flex items-center gap-3 border-b border-slate-800">
                    <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-900/40">
                        <ShieldCheck size={24} />
                    </div>
                    <div>
                        <h1 className="text-white font-bold text-lg tracking-tight">DocManager</h1>
                        <p className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">CA Edition</p>
                    </div>
                </div>

                <nav className="flex-1 py-6 px-3 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            end={item.path === '/ca'}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${isActive
                                    ? 'bg-blue-600/10 text-blue-400 font-medium'
                                    : 'hover:bg-slate-800/50 hover:text-white'
                                }`
                            }
                        >
                            <item.icon className="group-hover:scale-110 transition-transform" size={20} />
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <button
                        onClick={logout}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-colors text-slate-400"
                    >
                        <LogOut size={20} />
                        <span className="font-medium">Sign Out</span>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-10 shadow-sm">
                    <div className="flex items-center gap-4">
                        <h2 className="text-slate-500 text-sm font-medium">Welcome back, <span className="text-slate-900 font-bold">{user?.name || 'Admin'}</span></h2>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="h-8 w-8 bg-slate-200 rounded-full flex items-center justify-center text-xs font-bold text-slate-600 border border-slate-300">
                            {user?.name?.charAt(0) || 'A'}
                        </div>
                    </div>
                </header>

                {/* Dynamic Content */}
                <main className="flex-1 overflow-auto p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}
