
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { publicApi } from '../../api'
import {
    Phone,
    Mail,
    MapPin,
    Globe,
    Linkedin,
    ArrowRight,
    Star,
    Menu,
    X,
    ShieldCheck,
    ChevronRight,
    CheckCircle,
    Users,
    Briefcase,
    FileText,
    Calculator,
    TrendingUp,
    Award,
    Building2,
    PieChart
} from 'lucide-react'
import axios from 'axios';

export default function PublicWebsite() {
    const { username } = useParams<{ username: string }>()
    const navigate = useNavigate()
    const [isMenuOpen, setIsMenuOpen] = useState(false)

    const { data: profile, isLoading: profileLoading, error } = useQuery({
        queryKey: ['public-profile', username],
        queryFn: () => publicApi.getProfile(username!).then(res => res.data),
        enabled: !!username,
        retry: false
    })

    const { data: media } = useQuery({
        queryKey: ['public-media', username],
        queryFn: () => publicApi.getMedia(username!).then(res => res.data),
        enabled: !!username
    })

    const { data: services } = useQuery({
        queryKey: ['public-services', username],
        queryFn: () => publicApi.getServices(username!).then(res => res.data),
        enabled: !!username
    })

    const { data: testimonials } = useQuery({
        queryKey: ['public-testimonials', username],
        queryFn: () => publicApi.getTestimonials(username!).then(res => res.data),
        enabled: !!username
    })

    if (profileLoading) return <div className="min-h-screen flex items-center justify-center text-slate-400">Loading website...</div>
    if (error || !profile) return <div className="min-h-screen flex items-center justify-center text-red-400">CA not found or error loading profile.</div>

    const carouselImages = media?.filter((m: any) => m.item_type === 'carousel') || []

    return (
        <div className="font-sans text-slate-800 bg-white min-h-screen flex flex-col">
            {/* Header */}
            <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-blue-100 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="h-12 w-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
                            <ShieldCheck size={28} strokeWidth={2.5} />
                        </div>
                        <div>
                            <h1 className="text-xl font-black text-slate-900 leading-none tracking-tight">Dagdiya Associates</h1>
                            <p className="text-[10px] text-blue-600 font-bold tracking-widest uppercase">Chartered Accountants</p>
                        </div>
                    </div>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-8">
                        {['Home', 'Services', 'Testimonials', 'Contact'].map(item => (
                            <a key={item} href={`#${item.toLowerCase()}`} className="text-sm font-bold text-slate-700 hover:text-blue-600 transition-colors relative group">
                                {item}
                                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all"></span>
                            </a>
                        ))}
                        <button
                            onClick={() => navigate('/portal/login')}
                            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2.5 rounded-xl font-bold text-sm hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg shadow-blue-500/30"
                        >
                            Client Login
                        </button>
                    </nav>

                    {/* Mobile Menu Toggle */}
                    <button className="md:hidden p-2 text-slate-600" onClick={() => setIsMenuOpen(!isMenuOpen)}>
                        {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>

                {/* Mobile Nav */}
                {isMenuOpen && (
                    <div className="md:hidden absolute top-20 left-0 w-full bg-white border-b border-slate-100 p-6 flex flex-col gap-4 shadow-xl">
                        {['Home', 'Services', 'Testimonials', 'Contact'].map(item => (
                            <a key={item} href={`#${item.toLowerCase()}`} onClick={() => setIsMenuOpen(false)} className="text-lg font-bold text-slate-800">
                                {item}
                            </a>
                        ))}
                        <button
                            onClick={() => navigate('/portal/login')}
                            className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold w-full"
                        >
                            Client Portal Login
                        </button>
                    </div>
                )}
            </header>

            <main className="flex-1">
                {/* Hero Section */}
                <section id="home" className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white overflow-hidden min-h-[650px] flex items-center">
                    {/* Background Pattern */}
                    <div className="absolute inset-0 z-0">
                        {carouselImages.length > 0 ? (
                            <img
                                src={`http://localhost:8443/${carouselImages[0].file_path}`}
                                alt="Office"
                                className="w-full h-full object-cover opacity-20"
                            />
                        ) : (
                            <div className="w-full h-full opacity-10">
                                <div className="absolute inset-0" style={{backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '40px 40px'}}></div>
                            </div>
                        )}
                        <div className="absolute inset-0 bg-gradient-to-t from-blue-900 via-transparent to-transparent"></div>
                    </div>

                    <div className="max-w-7xl mx-auto px-6 relative z-10 w-full py-24">
                        <div className="max-w-4xl space-y-8 animate-in slide-in-from-left duration-700">
                            <div>
                                <span className="inline-block px-5 py-2 rounded-full bg-white/10 text-blue-200 border border-white/20 text-xs font-black uppercase tracking-widest mb-8 backdrop-blur-sm">
                                    ✓ Trusted & Certified CA Firm
                                </span>
                                <h2 className="text-5xl md:text-7xl font-black tracking-tight leading-[1.1] mb-6">
                                    Welcome to <br />
                                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-white to-blue-200">Dagdiya Associates</span>
                                </h2>
                                <p className="text-2xl font-bold text-blue-100 mb-4">Your Partner in Financial Excellence</p>
                            </div>
                            <p className="text-lg text-blue-100 leading-relaxed max-w-2xl">
                                {profile.professional_bio || "Professional accounting, auditing, taxation, and compliance services delivered with integrity and precision. We help businesses and individuals achieve financial clarity and growth."}
                            </p>
                            <div className="flex flex-wrap gap-4 pt-4">
                                <button onClick={() => document.getElementById('contact')?.scrollIntoView()} className="bg-white text-blue-900 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition-all flex items-center gap-2 shadow-xl">
                                    Get Started <ArrowRight size={18} />
                                </button>
                                <button onClick={() => document.getElementById('services')?.scrollIntoView()} className="bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white px-8 py-4 rounded-xl font-bold hover:bg-white/20 transition-all">
                                    Our Services
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Services Section */}
                <section id="services" className="py-24 bg-gradient-to-b from-white to-blue-50">
                    <div className="max-w-7xl mx-auto px-6">
                        <div className="text-center max-w-3xl mx-auto mb-16">
                            <h3 className="text-blue-600 font-black uppercase tracking-widest text-sm mb-3">Our Expertise</h3>
                            <h2 className="text-4xl md:text-5xl font-black text-slate-900 mb-4">Comprehensive CA Services</h2>
                            <p className="text-slate-600 text-lg">Professional solutions tailored to your financial needs</p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8">
                            {services?.length > 0 ? services.map((svc: any, idx: number) => {
                                const icons = [FileText, Calculator, TrendingUp, Award, Building2, PieChart]
                                const Icon = icons[idx % icons.length]
                                return (
                                    <div key={svc.id} className="bg-white p-8 rounded-2xl shadow-lg border border-blue-100 hover:shadow-2xl hover:border-blue-300 transition-all group hover:-translate-y-1">
                                        <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-blue-700 text-white rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-blue-500/30">
                                            <Icon size={32} strokeWidth={2} />
                                        </div>
                                        <h4 className="text-xl font-bold text-slate-900 mb-3">{svc.name}</h4>
                                        <p className="text-slate-600 leading-relaxed">{svc.description}</p>
                                        <div className="mt-6 flex items-center text-blue-600 font-bold text-sm group-hover:gap-2 transition-all">
                                            Learn More <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                                        </div>
                                    </div>
                                )
                            }) : (
                                // Default services if none configured
                                [
                                    { name: 'Tax Planning & Filing', desc: 'Expert tax consultation and filing services for individuals and businesses', icon: Calculator },
                                    { name: 'Audit & Assurance', desc: 'Comprehensive audit services ensuring compliance and accuracy', icon: CheckCircle },
                                    { name: 'GST Compliance', desc: 'Complete GST registration, filing, and compliance management', icon: FileText },
                                    { name: 'Financial Advisory', desc: 'Strategic financial planning and business advisory services', icon: TrendingUp },
                                    { name: 'Company Formation', desc: 'End-to-end support for company registration and incorporation', icon: Building2 },
                                    { name: 'Accounting Services', desc: 'Professional bookkeeping and accounting management', icon: PieChart }
                                ].map((svc, idx) => {
                                    const Icon = svc.icon
                                    return (
                                        <div key={idx} className="bg-white p-8 rounded-2xl shadow-lg border border-blue-100 hover:shadow-2xl hover:border-blue-300 transition-all group hover:-translate-y-1">
                                            <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-blue-700 text-white rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-blue-500/30">
                                                <Icon size={32} strokeWidth={2} />
                                            </div>
                                            <h4 className="text-xl font-bold text-slate-900 mb-3">{svc.name}</h4>
                                            <p className="text-slate-600 leading-relaxed">{svc.desc}</p>
                                            <div className="mt-6 flex items-center text-blue-600 font-bold text-sm group-hover:gap-2 transition-all">
                                                Learn More <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                                            </div>
                                        </div>
                                    )
                                })
                            )}
                        </div>
                    </div>
                </section>

                {/* Testimonials Section */}
                <section id="testimonials" className="py-24 bg-white">
                    <div className="max-w-7xl mx-auto px-6">
                        <div className="text-center max-w-3xl mx-auto mb-16">
                            <h3 className="text-blue-600 font-black uppercase tracking-widest text-sm mb-3">Testimonials</h3>
                            <h2 className="text-4xl font-bold text-slate-900">What Our Clients Say</h2>
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {testimonials?.length > 0 ? testimonials.map((t: any) => (
                                <div key={t.id} className="bg-slate-50 p-8 rounded-3xl relative">
                                    <div className="flex gap-1 mb-4 text-amber-400">
                                        {[...Array(t.rating || 5)].map((_, i) => <Star key={i} size={16} fill="currentColor" />)}
                                    </div>
                                    <p className="text-slate-700 italic mb-6">"{t.text}"</p>
                                    <div>
                                        <p className="font-bold text-slate-900">{t.client_name}</p>
                                        <p className="text-xs text-slate-500 uppercase tracking-wide font-bold">Verified Client</p>
                                    </div>
                                </div>
                            )) : (
                                <p className="col-span-full text-center text-slate-400">No testimonials yet.</p>
                            )}
                        </div>
                    </div>
                </section>

                {/* Contact Section */}
                <section id="contact" className="py-24 bg-slate-900 text-white">
                    <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16">
                        <div>
                            <h2 className="text-4xl font-bold mb-6">Get in Touch</h2>
                            <p className="text-slate-400 mb-12 text-lg">
                                Ready to optimize your finances? Contact us today for a consultation.
                            </p>

                            <div className="space-y-6">
                                {profile.address && (
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 bg-white/10 rounded-xl"><MapPin size={24} className="text-blue-400" /></div>
                                        <div>
                                            <h4 className="font-bold text-lg">Visit Us</h4>
                                            <p className="text-slate-400">{profile.address}</p>
                                        </div>
                                    </div>
                                )}
                                {profile.phone_number && (
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 bg-white/10 rounded-xl"><Phone size={24} className="text-blue-400" /></div>
                                        <div>
                                            <h4 className="font-bold text-lg">Call Us</h4>
                                            <p className="text-slate-400">{profile.phone_number}</p>
                                        </div>
                                    </div>
                                )}
                                {profile.email && (
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 bg-white/10 rounded-xl"><Mail size={24} className="text-blue-400" /></div>
                                        <div>
                                            <h4 className="font-bold text-lg">Email Us</h4>
                                            <p className="text-slate-400">{profile.email}</p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-4 mt-12">
                                {profile.website_url && (
                                    <a href={profile.website_url} target="_blank" rel="noreferrer" className="p-3 bg-white/5 hover:bg-white/20 rounded-xl transition-colors">
                                        <Globe size={24} />
                                    </a>
                                )}
                                {profile.linkedin_url && (
                                    <a href={profile.linkedin_url} target="_blank" rel="noreferrer" className="p-3 bg-white/5 hover:bg-white/20 rounded-xl transition-colors">
                                        <Linkedin size={24} />
                                    </a>
                                )}
                            </div>
                        </div>

                        <div className="bg-white text-slate-900 p-8 rounded-3xl">
                            <h3 className="text-2xl font-bold mb-6">Send a Message</h3>
                            <form className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <input type="text" placeholder="Name" className="w-full p-4 bg-slate-50 border-none rounded-xl" />
                                    <input type="tel" placeholder="Phone" className="w-full p-4 bg-slate-50 border-none rounded-xl" />
                                </div>
                                <input type="email" placeholder="Email" className="w-full p-4 bg-slate-50 border-none rounded-xl" />
                                <textarea placeholder="How can we help?" className="w-full p-4 bg-slate-50 border-none rounded-xl h-32"></textarea>
                                <button type="button" className="w-full py-4 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors">
                                    Send Message
                                </button>
                            </form>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="bg-gradient-to-br from-blue-950 to-slate-950 text-slate-400 py-12 text-center text-sm font-bold uppercase tracking-widest border-t border-blue-900">
                <p>&copy; {new Date().getFullYear()} Dagdiya Associates. All rights reserved.</p>
                <p className="mt-2 text-xs opacity-50">Professional Chartered Accountants</p>
            </footer>
        </div>
    )
}
