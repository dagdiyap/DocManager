import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion';
import { Phone, MapPin, Clock, Mail, ChevronDown, Star, Shield, Heart, Sparkles, Menu, X, ArrowRight, Zap, Smile } from 'lucide-react';
import Logo from './components/Logo';
import { Particles, FTooth, Laser, Drill, STitle, CUp, WABtn, Accordion, TestimonialCard } from './components/UI';
import { WA, MAPS, INAUG, HERO_IMGS, SERVICES, STATS, TESTIMONIALS, NAV_ITEMS, CLINIC_DESC } from './data';

/* Pre-computed confetti positions (avoids Math.random() in render) */
const CONFETTI_TYPES = ['tooth', 'brush', 'sparkle', 'mirror', 'star'] as const;
const CONFETTI = Array.from({ length: 30 }, (_, i) => {
  const seed = (i * 7 + 13) % 100;
  const seed2 = (i * 11 + 7) % 100;
  const seed3 = (i * 3 + 29) % 360;
  return { id: i, type: CONFETTI_TYPES[i % 5], size: 20 + (seed % 40), left: seed, top: seed2, rotate: seed3, opacity: 0.15 + (seed % 20) / 100 };
});

/* ═══════════════════════════════════════════
              MAIN APP COMPONENT
   ═══════════════════════════════════════════ */
export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [heroIdx, setHeroIdx] = useState(0);
  const [aTesti, setATesti] = useState(0);
  const [scrolled, setScrolled] = useState(false);
  const { scrollYProgress } = useScroll();

  // Cursor glow
  const gx = useMotionValue(0);
  const gy = useMotionValue(0);
  const onMove = useCallback((e: MouseEvent) => { gx.set(e.clientX); gy.set(e.clientY); }, [gx, gy]);
  useEffect(() => { window.addEventListener('mousemove', onMove); return () => window.removeEventListener('mousemove', onMove); }, [onMove]);
  const sx = useSpring(gx, { stiffness: 150, damping: 15 });
  const sy = useSpring(gy, { stiffness: 150, damping: 15 });

  // Hero parallax
  const heroY = useTransform(scrollYProgress, [0, 0.15], [0, -60]);

  // SMILE text reveal — scroll-driven
  const smileRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress: smileProg } = useScroll({ target: smileRef, offset: ['start end', 'end start'] });
  const smileClip = useTransform(smileProg, [0.15, 0.55], [0, 100]);
  const smileScale = useTransform(smileProg, [0.15, 0.55], [1.2, 1]);
  const smileTextOp = useTransform(smileProg, [0.05, 0.2], [0, 1]);
  // Moving text strips - left-to-right and right-to-left scroll-driven
  const stripLTR = useTransform(smileProg, [0, 1], [-300, 300]);
  const stripRTL = useTransform(smileProg, [0, 1], [300, -300]);


  const [expandedSvc, setExpandedSvc] = useState<number | null>(null);

  useEffect(() => { const h = () => setScrolled(window.scrollY > 50); window.addEventListener('scroll', h); return () => window.removeEventListener('scroll', h); }, []);
  useEffect(() => { const t = setInterval(() => setHeroIdx(p => (p + 1) % HERO_IMGS.length), 4000); return () => clearInterval(t); }, []);
  useEffect(() => { const t = setInterval(() => setATesti(p => (p + 1) % TESTIMONIALS.length), 5000); return () => clearInterval(t); }, []);

  return (
    <div className="relative overflow-x-hidden bg-white">
      {/* Cursor glow (desktop) */}
      <motion.div className="hidden lg:block fixed w-[500px] h-[500px] rounded-full pointer-events-none z-[9998]"
        style={{ x: sx, y: sy, translateX: '-50%', translateY: '-50%', background: 'radial-gradient(circle,rgba(20,184,166,0.06) 0%,transparent 70%)' }} />

      {/* Scroll progress bar */}
      <motion.div className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-teal-500 via-pink-500 to-teal-500 z-[100] origin-left" style={{ scaleX: scrollYProgress }} />

      {/* ════════════════ NAVIGATION ════════════════ */}
      <motion.nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? 'bg-white/90 backdrop-blur-xl shadow-lg shadow-black/5' : 'bg-transparent'}`}
        initial={{ y: -100 }} animate={{ y: 0 }} transition={{ duration: 0.6, type: 'spring' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            <Logo size={40} showText light={!scrolled} />
            <div className="hidden md:flex items-center gap-1">
              {NAV_ITEMS.map(n => (
                <motion.a key={n} href={`#${n.toLowerCase()}`}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${scrolled ? 'text-gray-700 hover:text-teal-600 hover:bg-teal-50' : 'text-white/80 hover:text-white hover:bg-white/10'}`}
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>{n}</motion.a>
              ))}
              <WABtn text="Book Now" className="ml-3" />
            </div>
            <button className={`md:hidden p-2 rounded-lg ${scrolled ? 'text-gray-800' : 'text-white'}`} onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
        <AnimatePresence>
          {menuOpen && (
            <motion.div className="md:hidden absolute top-full left-0 right-0 bg-white/95 backdrop-blur-xl shadow-2xl border-t border-gray-100"
              initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
              <div className="px-4 py-6 space-y-2">
                {NAV_ITEMS.map((n, i) => (
                  <motion.a key={n} href={`#${n.toLowerCase()}`}
                    className="block px-4 py-3 text-gray-800 font-medium rounded-xl hover:bg-teal-50"
                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                    onClick={() => setMenuOpen(false)}>{n}</motion.a>
                ))}
                <div className="pt-3"><WABtn text="Book Appointment" className="w-full justify-center" /></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* ════════════════ HERO ════════════════ */}
      <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-teal-950 to-slate-900" />
        <AnimatePresence mode="wait">
          <motion.div key={heroIdx} className="absolute inset-0"
            initial={{ opacity: 0, scale: 1.1 }} animate={{ opacity: 0.2, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: 1.5 }}>
            <img src={HERO_IMGS[heroIdx]} alt="Best dentist in Nanded - Dagdiya Laser Dental Clinic" className="w-full h-full object-cover" />
          </motion.div>
        </AnimatePresence>
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/70 via-transparent to-slate-900/80" />
        <Particles />
        <Laser top="25%" />
        <Laser top="65%" delay={2} />
        <FTooth className="absolute top-24 right-12 w-16 h-16 opacity-20 hidden lg:block" />
        <FTooth className="absolute bottom-36 left-20 w-12 h-12 opacity-15 hidden lg:block" delay={2} />
        <Drill className="absolute top-1/3 right-[15%] w-20 h-20 opacity-15 hidden lg:block" />

        <motion.div className="relative z-10 w-full" style={{ y: heroY }}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-20 md:pt-0 md:pb-0 md:min-h-screen md:flex md:items-center">
            <div className="w-full text-center">
              {/* Badge removed — cleaner hero on mobile */}

              <motion.h2 className="text-lg sm:text-2xl md:text-3xl font-display font-bold text-teal-300 mb-2 tracking-wide"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.1 }}>
                Dagdiya Laser Dental Clinic
              </motion.h2>

              <motion.h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-display font-bold text-white leading-[0.9] mb-3"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
                <motion.span className="inline-block" initial={{ opacity: 0, y: 60, rotateX: -90 }} animate={{ opacity: 1, y: 0, rotateX: 0 }} transition={{ duration: 0.9, delay: 0.3, type: 'spring', stiffness: 100 }}>
                  Your{' '}
                </motion.span>
                <motion.span className="inline-block gradient-text" initial={{ opacity: 0, scale: 0.3 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, delay: 0.6, type: 'spring', stiffness: 120 }}>
                  Smile
                </motion.span>
                <br />
                <motion.span className="inline-block" initial={{ opacity: 0, y: 60, rotateX: -90 }} animate={{ opacity: 1, y: 0, rotateX: 0 }} transition={{ duration: 0.9, delay: 0.8, type: 'spring', stiffness: 100 }}>
                  Our{' '}
                </motion.span>
                <motion.span className="inline-block gradient-text-pink" initial={{ opacity: 0, scale: 0.3 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, delay: 1.0, type: 'spring', stiffness: 120 }}>
                  Passion
                </motion.span>
              </motion.h1>

              <motion.p className="text-sm sm:text-base md:text-lg text-gray-300 max-w-xl mx-auto mb-6"
                initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 1.2 }}>
                Dental excellence by{' '}
                <span className="whitespace-nowrap"><span className="text-teal-400 font-semibold">Dr. Rajesh Dagdiya</span> & <span className="text-pink-400 font-semibold">Dr. Rekha Dagdiya</span></span>
              </motion.p>

              <motion.div className="flex flex-row gap-3 justify-center"
                initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.6 }}>
                <WABtn text="Book Appointment" />
                <motion.a href="#services"
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 sm:px-8 sm:py-4 text-sm sm:text-lg font-semibold text-white border-2 border-white/20 rounded-full hover:bg-white/10 transition-all"
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  Our Services <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
                </motion.a>
              </motion.div>

              <motion.div className="flex gap-6 md:gap-12 mt-8 justify-center flex-wrap"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }}>
                {[
                  { icon: <Heart className="w-5 h-5" />, label: '25+ Yrs', sub: 'Experience' },
                  { icon: <Smile className="w-5 h-5" />, label: '20K+', sub: 'Happy Smiles' },
                  { icon: <Zap className="w-5 h-5" />, label: 'Painless', sub: 'Laser Care' },
                ].map((item, i) => (
                  <motion.div key={i} className="text-center" whileHover={{ scale: 1.1 }}>
                    <div className="flex items-center justify-center gap-2 text-teal-400 mb-1">{item.icon}<span className="text-lg font-bold text-white">{item.label}</span></div>
                    <span className="text-xs text-gray-400">{item.sub}</span>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </motion.div>
        <motion.div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10" animate={{ y: [0, 10, 0] }} transition={{ duration: 2, repeat: Infinity }}>
          <ChevronDown className="w-8 h-8 text-teal-400" />
        </motion.div>
      </section>

      {/* ════════════════ LANDO-STYLE TEXT REVEAL WITH TEETH BACKGROUND ════════════════ */}
      <div ref={smileRef} className="relative h-[50vh] sm:h-[60vh] overflow-hidden bg-slate-950 flex items-center justify-center">
        {/* Animated teeth SVG background — revealed by scroll clip */}
        <motion.div className="absolute inset-0" style={{ scale: smileScale }}>
          <motion.div className="absolute inset-0"
            style={{ clipPath: useTransform(smileClip, v => `inset(${50 - v / 2}% 0 ${50 - v / 2}% 0)`) }}>
            <div className="w-full h-full bg-gradient-to-br from-teal-950 via-teal-900 to-slate-950 relative">
              {/* Giant central tooth */}
              <svg className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[60vw] h-[60vw] max-w-[600px] max-h-[600px] opacity-[0.07]" viewBox="0 0 64 64" fill="none">
                <path d="M32 6C24 6 18 8 16 14C14 20 15 26 17 30C18 32 19 33 20 34L22 50C23 55 25 58 28 58C29.5 58 30.5 54 32 50C33.5 54 34.5 58 36 58C39 58 41 55 42 50L44 34C45 33 46 32 47 30C49 26 50 20 48 14C46 8 40 6 32 6Z" fill="#5eead4" stroke="#5eead4" strokeWidth="0.5" />
              </svg>
              {/* Ring of teeth around center */}
              {[0, 45, 90, 135, 180, 225, 270, 315].map((deg, i) => (
                <svg key={i} className="absolute left-1/2 top-1/2 w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20 opacity-[0.12]" viewBox="0 0 64 64" fill="none"
                  style={{ transform: `translate(-50%,-50%) rotate(${deg}deg) translateY(-min(25vw, 200px)) rotate(-${deg}deg)` }}>
                  <path d="M32 6C24 6 18 8 16 14C14 20 15 26 17 30C18 32 19 33 20 34L22 50C23 55 25 58 28 58C29.5 58 30.5 54 32 50C33.5 54 34.5 58 36 58C39 58 41 55 42 50L44 34C45 33 46 32 47 30C49 26 50 20 48 14C46 8 40 6 32 6Z" fill="#2dd4bf" stroke="#2dd4bf" strokeWidth="0.5" />
                </svg>
              ))}
              {/* Scattered small teeth */}
              {CONFETTI.filter(c => c.type === 'tooth').map((c) => (
                <svg key={c.id} className="absolute opacity-[0.08]" style={{ left: `${c.left}%`, top: `${c.top}%`, width: c.size * 1.5, height: c.size * 1.5, transform: `rotate(${c.rotate}deg)` }} viewBox="0 0 64 64" fill="none">
                  <path d="M32 6C24 6 18 8 16 14C14 20 15 26 17 30C18 32 19 33 20 34L22 50C23 55 25 58 28 58C29.5 58 30.5 54 32 50C33.5 54 34.5 58 36 58C39 58 41 55 42 50L44 34C45 33 46 32 47 30C49 26 50 20 48 14C46 8 40 6 32 6Z" fill="#14b8a6" />
                </svg>
              ))}
              {/* Glowing circles */}
              <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl" />
              <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl" />
            </div>
          </motion.div>
        </motion.div>

        {/* Moving text strips — Lando-style */}
        <motion.div className="absolute top-[18%] whitespace-nowrap text-[6rem] md:text-[10rem] font-display font-black text-white/[0.03] pointer-events-none select-none"
          style={{ x: stripLTR }}>
          IMPLANTS · COSMETIC · ORTHODONTICS · ROOT CANAL · PEDIATRIC · ORAL SURGERY · IMPLANTS · COSMETIC ·
        </motion.div>
        <motion.div className="absolute top-[55%] whitespace-nowrap text-[6rem] md:text-[10rem] font-display font-black text-white/[0.03] pointer-events-none select-none"
          style={{ x: stripRTL }}>
          PAINLESS · LASER · DIGITAL · PRECISION · PAINLESS · LASER · DIGITAL · PRECISION · PAINLESS ·
        </motion.div>

        {/* Main text — "Ready for Your Best Smile?" */}
        <motion.div className="relative z-10 text-center px-4" style={{ opacity: smileTextOp }}>
          <h2 className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-display font-black leading-[1.1] text-white mix-blend-difference select-none">
            Ready for Your<br />
            <span className="gradient-text">Best Smile?</span>
          </h2>
          <motion.div className="mt-6 flex items-center justify-center gap-3"
            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.5 }}>
            <div className="h-[1px] w-12 bg-teal-400" />
            <span className="text-teal-400 text-sm tracking-[0.3em] uppercase font-medium">Let's Perfect It</span>
            <div className="h-[1px] w-12 bg-teal-400" />
          </motion.div>
        </motion.div>

        <FTooth className="absolute top-8 left-[10%] w-10 h-10 opacity-30" />
        <FTooth className="absolute bottom-12 right-[15%] w-8 h-8 opacity-20" delay={2} />
      </div>

      {/* ════════════════ MARQUEE STRIP ════════════════ */}
      <div className="bg-gradient-to-r from-teal-600 via-teal-500 to-teal-600 py-3 overflow-hidden">
        <div className="animate-marquee flex whitespace-nowrap">
          {[...Array(2)].map((_, si) => (
            <div key={si} className="flex items-center gap-8 mx-4">
              {['Dental Implants', 'Cosmetic Dentistry', 'Orthodontics', 'Root Canal', 'Pediatric Care', 'Oral Surgery', 'Emergency Care', 'Painless Laser Treatment'].map((s, i) => (
                <span key={i} className="flex items-center gap-3 text-white font-medium text-sm"><span className="text-teal-200">✦</span> {s}</span>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* ════════════════ SERVICES — DYNAMIC EXPANDABLE GRID ════════════════ */}
      <section id="services" className="py-16 sm:py-24 md:py-32 relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Particles />
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.3) 1px, transparent 0)', backgroundSize: '48px 48px' }} />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <STitle badge="What We Offer" title="Our Specializations" sub="Tap any service to learn more" light />

          {/* Expanded card overlay for mobile — full-width, not cramped in column */}
          <AnimatePresence>
            {expandedSvc !== null && (
              <motion.div
                key="svc-overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
                onClick={() => setExpandedSvc(null)}>
                <motion.div
                  initial={{ scale: 0.9, opacity: 0, y: 30 }}
                  animate={{ scale: 1, opacity: 1, y: 0 }}
                  exit={{ scale: 0.9, opacity: 0, y: 30 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                  className="w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-2xl overflow-hidden"
                  style={{ borderColor: SERVICES[expandedSvc].color + '50', borderWidth: 2, borderStyle: 'solid' }}
                  onClick={e => e.stopPropagation()}>
                  <div className="relative h-[180px] sm:h-[220px] overflow-hidden">
                    <img src={SERVICES[expandedSvc].image} alt={SERVICES[expandedSvc].title}
                      className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-black/40 to-transparent" />
                    <button onClick={() => setExpandedSvc(null)}
                      className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white/80 hover:text-white transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 p-4 sm:p-5">
                      <h3 className="text-xl sm:text-2xl font-display font-bold text-white">{SERVICES[expandedSvc].title}</h3>
                      <p className="text-sm text-gray-300 mt-1">{SERVICES[expandedSvc].desc}</p>
                    </div>
                  </div>
                  <div className="p-4 sm:p-5 bg-slate-950">
                    <div className="w-12 h-[2px] rounded-full mb-4" style={{ backgroundColor: SERVICES[expandedSvc].color }} />
                    <p className="text-sm sm:text-base text-gray-300 leading-relaxed">{SERVICES[expandedSvc].detail}</p>
                    <div className="mt-4 pt-4 border-t border-white/[0.08]">
                      <WABtn text="Book Consultation" />
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-5">
            {SERVICES.map((svc, i) => {
              const floatY = [6, -8, 7, -6, 8, -7, 5, -9][i % 8];
              const floatDur = [5, 6.5, 5.5, 7, 4.5, 6, 5.2, 7.2][i % 8];
              const floatDelay = [0, 0.8, 1.6, 0.4, 1.2, 2, 0.6, 1.4][i % 8];
              const h = 180; // uniform height for all cards
              return (
                <motion.div key={i}
                  className="relative cursor-pointer group"
                  initial={{ opacity: 0, y: 60, scale: 0.9 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true, margin: '-30px' }}
                  transition={{ duration: 0.7, delay: i * 0.07, type: 'spring', stiffness: 100 }}>
                  <motion.div
                    animate={{ y: [0, floatY, 0] }}
                    transition={{ duration: floatDur, repeat: Infinity, ease: 'easeInOut', delay: floatDelay }}
                    className="relative">
                    <motion.div
                      whileHover={{ scale: 1.05, y: -10 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => setExpandedSvc(i)}
                      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                      className="relative rounded-2xl overflow-hidden select-none shadow-lg shadow-black/20 group-hover:shadow-xl group-hover:shadow-black/40"
                      style={{ borderColor: 'rgba(255,255,255,0.06)', borderWidth: 1, borderStyle: 'solid' }}>
                      <div className="relative overflow-hidden" style={{ height: `${h}px` }}>
                        <motion.img src={svc.image} alt={svc.title}
                          className="w-full h-full object-cover"
                          whileHover={{ scale: 1.12 }}
                          transition={{ duration: 0.6 }}
                          loading="lazy" />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />

                        <span className="absolute top-2 right-3 text-3xl sm:text-4xl font-display font-black text-white/[0.05] select-none">
                          {String(i + 1).padStart(2, '0')}
                        </span>

                        <div className="absolute bottom-0 left-0 right-0 p-2.5 sm:p-3">
                          <div className="flex items-end justify-between gap-2">
                            <div>
                              <h3 className="text-[13px] sm:text-sm lg:text-base font-display font-bold text-white leading-tight group-hover:text-teal-300 transition-colors duration-300">
                                {svc.title}
                              </h3>
                              <p className="text-[10px] sm:text-[11px] text-gray-400 mt-0.5 leading-snug line-clamp-2">{svc.desc}</p>
                            </div>
                            <motion.div
                              className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                              style={{ backgroundColor: svc.color + '40' }}
                              whileHover={{ scale: 1.2 }}>
                              <ArrowRight className="w-3.5 h-3.5 text-white" />
                            </motion.div>
                          </div>
                        </div>

                        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                          style={{ boxShadow: `inset 0 0 60px ${svc.color}15` }} />
                      </div>

                      <motion.div className="absolute bottom-0 left-0 right-0 h-[2px] origin-left"
                        style={{ backgroundColor: svc.color }}
                        initial={{ scaleX: 0 }}
                        whileHover={{ scaleX: 1 }}
                        transition={{ duration: 0.4 }} />
                    </motion.div>
                  </motion.div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ════════════════ STATS ════════════════ */}
      <section className="py-20 relative overflow-hidden bg-gradient-to-br from-slate-900 via-teal-950 to-slate-900">
        <Particles />
        <Drill className="absolute top-10 left-10 w-32 h-32 opacity-10" />
        <FTooth className="absolute bottom-10 right-10 w-24 h-24 opacity-10" />
        <div className="absolute inset-0 opacity-20" style={{ background: 'radial-gradient(ellipse at center, rgba(20,184,166,0.3) 0%, transparent 70%)' }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map((s, i) => (
              <motion.div key={i} className="text-center" initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}>
                <motion.div className="text-4xl md:text-5xl lg:text-6xl font-display font-bold text-white mb-2" whileHover={{ scale: 1.1 }}>
                  <CUp end={s.value} suffix={s.suffix} />
                </motion.div>
                <p className="text-teal-300 text-sm md:text-base font-medium">{s.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════════════ ABOUT / DOCTORS ════════════════ */}
      <section id="about" className="py-24 md:py-32 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <STitle badge="👨‍⚕️ Meet Your Doctors" title="Trusted Dental Experts" sub="Dedication to your dental health and beautiful smile" />
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div className="relative" initial={{ opacity: 0, x: -50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
              <div className="relative rounded-3xl overflow-hidden shadow-2xl">
                <img src={INAUG} alt="Dagdiya Laser Dental Clinic Nanded inauguration by Ex Chief Minister - Dr Rajesh Dagdiya" className="w-full h-[400px] md:h-[500px] object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-6 md:p-8">
                  <motion.div className="bg-gradient-to-r from-teal-600/90 to-teal-500/90 backdrop-blur-sm rounded-xl p-4 md:p-5 border border-teal-400/30"
                    initial={{ y: 20, opacity: 0 }} whileInView={{ y: 0, opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.5 }}>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center"><Star className="w-5 h-5 text-yellow-300 fill-yellow-300" /></div>
                      <div>
                        <p className="text-white font-bold text-base md:text-lg">Inaugurated by Ex Chief Minister</p>
                        <p className="text-teal-100 text-sm">A proud moment for Dagdiya Laser Dental Clinic</p>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
              <motion.div className="absolute -top-4 -right-4 md:right-4 bg-gradient-to-br from-teal-500 to-teal-600 rounded-2xl p-5 shadow-xl shadow-teal-500/30"
                animate={{ y: [0, -6, 0] }} transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}>
                <p className="text-4xl font-display font-bold text-white">25+</p>
                <p className="text-teal-100 text-sm">Years of<br />Excellence</p>
              </motion.div>
            </motion.div>

            <motion.div initial={{ opacity: 0, x: 50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}>
              <div className="space-y-8">
                {[
                  { initials: 'RD', name: 'Dr. Rajesh Dagdiya', role: 'Prosthodontist & Implantologist', desc: 'Pioneer of laser dentistry in Nanded. Renowned for dental implants, orthodontics, and prosthodontics.', gradient: 'from-teal-500 to-teal-600', shadow: 'shadow-teal-500/30' },
                  { initials: 'RD', name: 'Dr. Rekha Dagdiya', role: 'General & Cosmetic Dentistry', desc: 'Expert in root canals, cosmetic dentistry, and pediatric care.', gradient: 'from-pink-500 to-pink-600', shadow: 'shadow-pink-500/30' },
                ].map((doc, i) => (
                  <div key={i} className="flex gap-5">
                    <div className={`flex-shrink-0 w-14 h-14 rounded-2xl bg-gradient-to-br ${doc.gradient} flex items-center justify-center text-white text-xl font-bold shadow-lg ${doc.shadow}`}>{doc.initials}</div>
                    <div>
                      <h3 className="text-xl font-display font-bold text-gray-900">{doc.name}</h3>
                      <p className={`${i === 0 ? 'text-teal-600' : 'text-pink-600'} font-medium text-sm mb-2`}>{doc.role}</p>
                      <p className="text-gray-600 text-sm leading-relaxed">{doc.desc}</p>
                    </div>
                  </div>
                ))}
                <p className="text-gray-600 text-sm leading-relaxed">{CLINIC_DESC}</p>
                <div className="grid grid-cols-2 gap-4 pt-4">
                  {[
                    { icon: <Shield className="w-5 h-5" />, text: 'Certified Implantologist' },
                    { icon: <Zap className="w-5 h-5" />, text: 'Painless Laser Care' },
                    { icon: <Sparkles className="w-5 h-5" />, text: 'Digital Smile Design' },
                    { icon: <Heart className="w-5 h-5" />, text: 'Family Dentistry' },
                  ].map((h, i) => (
                    <motion.div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-teal-50 transition-colors" whileHover={{ scale: 1.03 }}>
                      <div className="text-teal-600">{h.icon}</div>
                      <span className="text-sm font-medium text-gray-700">{h.text}</span>
                    </motion.div>
                  ))}
                </div>
                <WABtn text="Consult Now" large />
              </div>
            </motion.div>
          </div>
        </div>
      </section>


      {/* ════════════════ WHY CHOOSE US — PHENOMENON ACCORDION ════════════════ */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-teal-950 to-slate-900 relative overflow-hidden">
        <Particles />
        <FTooth className="absolute top-20 right-20 w-28 h-28 opacity-10" />
        <Drill className="absolute bottom-20 left-20 w-24 h-24 opacity-10" />
        <Laser top="30%" />
        <Laser top="70%" delay={2} />
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <STitle badge="🏆 Why Us" title="What Sets Us Apart" sub="Experience dental care that's different" light />
          <div className="mt-8">
            {[
              { icon: <Zap className="w-6 h-6" />, title: 'Painless Laser Treatments', desc: 'Advanced laser technology for virtually painless procedures. No drills, no fear — just precise, comfortable treatments with faster healing.' },
              { icon: <Shield className="w-6 h-6" />, title: 'Hospital-Grade Sterilization', desc: 'Every instrument is autoclaved and sealed. Our sterilization protocols meet international standards — your safety is non-negotiable.' },
              { icon: <Heart className="w-6 h-6" />, title: 'Patient-First Philosophy', desc: 'We listen first, diagnose carefully, then treat. Every plan is customized to your needs, comfort, and budget. No unnecessary procedures.' },
              { icon: <Sparkles className="w-6 h-6" />, title: 'Latest Digital Technology', desc: 'Digital X-rays, 3D treatment planning, and state-of-the-art tech for precise diagnosis and predictable outcomes every time.' },
              { icon: <Smile className="w-6 h-6" />, title: 'Comfortable & Welcoming', desc: "Our clinic is designed to put you at ease — from the modern lounge to treatment rooms. We make dental visits something you won't dread." },
            ].map((item, i) => <Accordion key={i} icon={item.icon} title={item.title} desc={item.desc} idx={i} />)}
          </div>
        </div>
      </section>

      {/* ════════════════ TESTIMONIALS ════════════════ */}
      <section id="testimonials" className="py-24 md:py-32 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <STitle badge="💬 Patient Stories" title="What Patients Say" sub="Hear from the thousands who trust us with their smiles" />
          <div className="relative max-w-4xl mx-auto">
            <AnimatePresence mode="wait">
              <motion.div key={aTesti}
                initial={{ opacity: 0, y: 20, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -20, scale: 0.95 }} transition={{ duration: 0.5 }}>
                <TestimonialCard {...TESTIMONIALS[aTesti]} />
              </motion.div>
            </AnimatePresence>
            <div className="flex justify-center gap-3 mt-8">
              {TESTIMONIALS.map((_, i) => (
                <button key={i} onClick={() => setATesti(i)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${i === aTesti ? 'bg-teal-500 w-8' : 'bg-gray-300 hover:bg-gray-400'}`} />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════ CTA ════════════════ */}
      <section className="py-12 sm:py-16 relative overflow-hidden bg-gradient-to-r from-teal-600 via-teal-500 to-cyan-500">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '30px 30px' }} />
        <FTooth className="absolute top-10 left-10 w-20 h-20 opacity-20" />
        <FTooth className="absolute bottom-10 right-10 w-16 h-16 opacity-15" delay={3} />
        <motion.div className="max-w-4xl mx-auto px-4 text-center relative z-10"
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <motion.div className="inline-block mb-4" animate={{ rotate: [0, 10, -10, 0] }} transition={{ duration: 4, repeat: Infinity }}>
            <span className="text-5xl">😊</span>
          </motion.div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-white mb-4">Ready for Your<br /><span className="text-teal-100">Best Smile?</span></h2>
          <p className="text-base sm:text-lg text-teal-100 mb-8 max-w-2xl mx-auto">Book your consultation today. Walk-ins welcome!</p>
          <div className="flex flex-row gap-3 justify-center">
            <WABtn text="WhatsApp Us Now" className="bg-white !text-teal-700 hover:!bg-gray-100" />
            <motion.a href="tel:+919422185785"
              className="inline-flex items-center gap-1.5 px-5 py-2.5 sm:px-8 sm:py-4 text-sm sm:text-lg font-semibold text-white border-2 border-white/40 rounded-full hover:bg-white/10 transition-all"
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Phone className="w-4 h-4 sm:w-5 sm:h-5" /> Call: 94221 85785
            </motion.a>
          </div>
        </motion.div>
      </section>

      {/* ════════════════ CONTACT / MAP ════════════════ */}
      <section id="contact" className="py-24 md:py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <STitle badge="📍 Visit Us" title="Get In Touch" sub="Conveniently located in the heart of Nanded city" />
          <div className="grid lg:grid-cols-2 gap-12">
            <motion.div className="space-y-6" initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
              <div className="bg-white rounded-2xl p-8 shadow-lg shadow-black/5">
                <h3 className="text-2xl font-display font-bold text-gray-900 mb-6">Dagdiya Laser Dental Clinic</h3>
                <div className="space-y-5">
                  {[
                    { icon: <MapPin className="w-6 h-6" />, label: 'Location', lines: ['1st Floor, Centre Point Complex,', 'Near Over Bridge, Shivaji Nagar,', 'Nanded, Maharashtra 431602'] },
                    { icon: <Phone className="w-6 h-6" />, label: 'Phone', lines: ['+91 94221 85785 (Dr. Rajesh)', '+91 88558 71716', '02462-255663 (Landline)'] },
                    { icon: <Mail className="w-6 h-6" />, label: 'Email', lines: ['rdagdiya@gmail.com'] },
                    { icon: <Clock className="w-6 h-6" />, label: 'Working Hours', lines: ['Monday – Saturday: 10:00 AM – 8:00 PM', 'Sunday: By Appointment Only'] },
                  ].map((c, i) => (
                    <div key={i} className="flex gap-4">
                      <div className="w-12 h-12 rounded-xl bg-teal-50 flex items-center justify-center flex-shrink-0 text-teal-600">{c.icon}</div>
                      <div><p className="font-semibold text-gray-900">{c.label}</p>{c.lines.map((l, j) => <p key={j} className="text-gray-600 text-sm">{l}</p>)}</div>
                    </div>
                  ))}
                </div>
                <div className="mt-8"><WABtn text="Send Inquiry on WhatsApp" large className="w-full justify-center" /></div>
              </div>
            </motion.div>
            <motion.div className="rounded-2xl overflow-hidden shadow-lg shadow-black/5 h-[400px] lg:h-full min-h-[400px]"
              initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
              <iframe src={MAPS} width="100%" height="100%" style={{ border: 0 }} allowFullScreen loading="lazy" referrerPolicy="no-referrer-when-downgrade" title="Clinic Location" />
            </motion.div>
          </div>
        </div>
      </section>

      {/* ════════════════ FOOTER ════════════════ */}
      <footer className="bg-slate-950 text-white py-16 relative overflow-hidden">
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '40px 40px' }} />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid md:grid-cols-3 gap-12 mb-12">
            <div>
              <Logo size={50} showText light />
              <p className="text-gray-400 mt-4 text-sm leading-relaxed">Dagdiya Laser Dental Clinic — Nanded's premier destination for dental implants, laser dentistry, orthodontics, root canal treatment, cosmetic dentistry, and pediatric dental care.</p>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Our Services</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                {SERVICES.map((s, i) => <li key={i} className="hover:text-teal-400 transition-colors cursor-pointer flex items-center gap-2"><span className="text-teal-500 text-xs">▸</span> {s.title}</li>)}
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-lg mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                {NAV_ITEMS.map((n, i) => <li key={i}><a href={`#${n.toLowerCase()}`} className="hover:text-teal-400 transition-colors flex items-center gap-2"><span className="text-teal-500 text-xs">▸</span> {n}</a></li>)}
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-500 text-sm">© {new Date().getFullYear()} Dagdiya Laser Dental Clinic. All rights reserved.</p>
            <p className="text-gray-500 text-sm"><span className="font-script text-teal-400 text-base">Caring For Your Smile</span> since 2001</p>
          </div>
        </div>
      </footer>

      {/* Floating WhatsApp */}
      <motion.a href={WA} target="_blank" rel="noopener noreferrer"
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-[#25D366] rounded-full flex items-center justify-center shadow-2xl shadow-green-500/30 whatsapp-pulse"
        whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
        initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 2, type: 'spring' }}>
        <svg viewBox="0 0 24 24" className="w-8 h-8" fill="white">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
      </motion.a>
    </div>
  );
}
