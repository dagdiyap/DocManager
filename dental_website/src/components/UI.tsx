import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { Star } from 'lucide-react';
import { WA } from '../data';

/* ─── Floating particles ─── */
export function Particles() {
  const ps = Array.from({ length: 12 }, (_, i) => ({
    id: i, x: Math.random() * 100, s: Math.random() * 3 + 2,
    d: Math.random() * 15 + 10, dl: Math.random() * 8, o: Math.random() * 0.25 + 0.1,
  }));
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {ps.map(p => (
        <motion.div key={p.id} className="absolute rounded-full"
          style={{ left: `${p.x}%`, bottom: -10, width: p.s, height: p.s,
            background: `radial-gradient(circle,rgba(20,184,166,${p.o}),transparent)` }}
          animate={{ y: [0, -1200], opacity: [0, p.o, p.o, 0] }}
          transition={{ duration: p.d, repeat: Infinity, delay: p.dl, ease: 'linear' }} />
      ))}
    </div>
  );
}

/* ─── Floating tooth SVG ─── */
export function FTooth({ className = '', delay = 0 }: { className?: string; delay?: number }) {
  return (
    <motion.svg className={className} viewBox="0 0 64 64" fill="none"
      animate={{ y: [0, -12, 0], rotate: [0, 4, -4, 0] }}
      transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay }}>
      <path d="M32 6C24 6 18 8 16 14C14 20 15 26 17 30C18 32 19 33 20 34L22 50C23 55 25 58 28 58C29.5 58 30.5 54 32 50C33.5 54 34.5 58 36 58C39 58 41 55 42 50L44 34C45 33 46 32 47 30C49 26 50 20 48 14C46 8 40 6 32 6Z"
        fill="rgba(20,184,166,0.08)" stroke="rgba(20,184,166,0.2)" strokeWidth="1" />
    </motion.svg>
  );
}

/* ─── Laser beam ─── */
export function Laser({ top, delay = 0 }: { top: string; delay?: number }) {
  return (
    <motion.div className="absolute h-[2px] bg-gradient-to-r from-transparent via-teal-400 to-transparent pointer-events-none"
      style={{ width: 250, top }}
      animate={{ x: [-250, 2000], opacity: [0, 0.8, 0.8, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: 'linear', repeatDelay: 3, delay }} />
  );
}

/* ─── Spinning drill decoration ─── */
export function Drill({ className = '' }: { className?: string }) {
  return (
    <motion.svg className={className} viewBox="0 0 80 80" fill="none"
      animate={{ rotate: [0, 360] }} transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}>
      <circle cx="40" cy="40" r="18" stroke="#14b8a6" strokeWidth="1.5" strokeDasharray="6 4" opacity="0.2" />
      <circle cx="40" cy="40" r="3" fill="#14b8a6" opacity="0.25" />
    </motion.svg>
  );
}

/* ─── Section title ─── */
export function STitle({ badge, title, sub, light = false }: { badge: string; title: string; sub: string; light?: boolean }) {
  const r = useRef(null);
  const iv = useInView(r, { once: true, margin: '-80px' });
  return (
    <motion.div ref={r} className="text-center mb-16"
      initial={{ opacity: 0, y: 40 }} animate={iv ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.7 }}>
      <motion.span
        className={`inline-block px-4 py-1.5 rounded-full text-sm font-medium mb-4 ${light ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30' : 'bg-teal-50 text-teal-700 border border-teal-200'}`}
        initial={{ scale: 0.8 }} animate={iv ? { scale: 1 } : {}} transition={{ delay: 0.2, type: 'spring' }}>
        {badge}
      </motion.span>
      <h2 className={`text-4xl md:text-5xl lg:text-6xl font-display font-bold mb-4 ${light ? 'text-white' : 'text-gray-900'}`}>{title}</h2>
      <p className={`text-lg max-w-2xl mx-auto ${light ? 'text-gray-300' : 'text-gray-600'}`}>{sub}</p>
      <motion.div className="w-24 h-1 bg-gradient-to-r from-teal-500 to-pink-500 mx-auto mt-6 rounded-full"
        initial={{ scaleX: 0 }} animate={iv ? { scaleX: 1 } : {}} transition={{ delay: 0.4, duration: 0.6 }} />
    </motion.div>
  );
}

/* ─── Count-up number ─── */
export function CUp({ end, suffix = '' }: { end: number; suffix?: string }) {
  const r = useRef(null);
  const iv = useInView(r, { once: true });
  const [c, setC] = useState(0);
  useEffect(() => {
    if (!iv) return;
    let v = 0;
    const s = end / 83; // 1.5x faster than original
    const t = setInterval(() => { v += s; if (v >= end) { setC(end); clearInterval(t); } else setC(Math.floor(v)); }, 16);
    return () => clearInterval(t);
  }, [iv, end]);
  return <span ref={r} className="counter-glow">{c.toLocaleString()}{suffix}</span>;
}

/* ─── WhatsApp button ─── */
export function WABtn({ text = 'Book Appointment', className = '', large = false }: { text?: string; className?: string; large?: boolean }) {
  return (
    <motion.a href={WA} target="_blank" rel="noopener noreferrer"
      className={`inline-flex items-center gap-1.5 sm:gap-2 bg-[#25D366] text-white font-semibold rounded-full shadow-lg hover:shadow-xl hover:bg-[#20BD5A] transition-all btn-shimmer ${large ? 'px-5 py-2.5 sm:px-8 sm:py-4 text-sm sm:text-lg' : 'px-4 py-2.5 sm:px-6 sm:py-3 text-xs sm:text-sm'} ${className}`}
      whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
      <svg viewBox="0 0 24 24" className={large ? 'w-4 h-4 sm:w-6 sm:h-6' : 'w-4 h-4 sm:w-5 sm:h-5'} fill="currentColor">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
      </svg>
      {text}
    </motion.a>
  );
}

/* ─── Phenomenon-style accordion item ─── */
export function Accordion({ icon, title, desc, idx }: { icon: React.ReactNode; title: string; desc: string; idx: number }) {
  const [open, setOpen] = useState(false);
  const r = useRef(null);
  const iv = useInView(r, { once: true });
  return (
    <motion.div ref={r} className="border-b border-white/10"
      initial={{ opacity: 0, x: -30 }} animate={iv ? { opacity: 1, x: 0 } : {}} transition={{ delay: idx * 0.08 }}>
      <motion.button className="w-full flex items-center justify-between py-6 md:py-8 text-left group"
        onClick={() => setOpen(!open)} whileHover={{ x: 10 }}>
        <div className="flex items-center gap-4 md:gap-6">
          <motion.div className="w-12 h-12 md:w-14 md:h-14 rounded-xl bg-teal-500/15 flex items-center justify-center text-teal-400"
            animate={open ? { rotate: 90 } : { rotate: 0 }}>{icon}</motion.div>
          <span className="text-xl md:text-3xl font-display font-bold text-white group-hover:text-teal-300 transition-colors">{title}</span>
        </div>
        <motion.span animate={{ rotate: open ? 45 : 0 }} className="text-teal-400 text-2xl flex-shrink-0">+</motion.span>
      </motion.button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }} className="overflow-hidden">
            <p className="text-gray-400 text-base md:text-lg pb-6 pl-16 md:pl-20 max-w-2xl leading-relaxed">{desc}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ─── Testimonial card ─── */
export function TestimonialCard({ name, text, rating }: { name: string; text: string; rating: number }) {
  return (
    <div className="bg-white rounded-3xl shadow-xl shadow-black/5 p-8 md:p-12 text-center relative">
      <span className="absolute top-4 left-6 text-8xl text-teal-100 font-serif leading-none">"</span>
      <div className="flex justify-center gap-1 mb-6">
        {[...Array(rating)].map((_, i) => <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />)}
      </div>
      <p className="text-lg md:text-xl text-gray-700 leading-relaxed mb-6 relative z-10 italic">"{text}"</p>
      <p className="text-teal-600 font-bold text-lg">{name}</p>
    </div>
  );
}
