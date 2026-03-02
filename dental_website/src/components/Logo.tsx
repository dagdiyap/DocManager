import { motion } from 'framer-motion';

interface LogoProps {
  size?: number;
  showText?: boolean;
  light?: boolean;
}

const Logo = ({ size = 40, showText = true, light = false }: LogoProps) => {
  return (
    <motion.div
      className="flex items-center gap-2.5 cursor-pointer"
      whileHover={{ scale: 1.03 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      {/* Realistic molar tooth SVG */}
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        animate={{ rotate: [0, 3, -3, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <defs>
          <linearGradient id="toothMain" x1="12" y1="4" x2="52" y2="60">
            <stop offset="0%" stopColor="#e0f2fe" />
            <stop offset="40%" stopColor="#f0fdfa" />
            <stop offset="100%" stopColor="#ccfbf1" />
          </linearGradient>
          <linearGradient id="toothShine" x1="20" y1="8" x2="44" y2="28">
            <stop offset="0%" stopColor="white" stopOpacity="0.8" />
            <stop offset="100%" stopColor="white" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="toothStroke" x1="12" y1="4" x2="52" y2="60">
            <stop offset="0%" stopColor="#14b8a6" />
            <stop offset="100%" stopColor="#0d9488" />
          </linearGradient>
          <filter id="toothShadow">
            <feDropShadow dx="0" dy="1" stdDeviation="1.5" floodColor="#14b8a6" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Tooth body — realistic molar shape with crown, two roots */}
        <g filter="url(#toothShadow)">
          {/* Main crown */}
          <path
            d="M32 6C24 6 18 8 16 14C14 20 15 26 17 30C18 32 19 33 20 34L22 50C23 55 25 58 28 58C29.5 58 30.5 54 32 50C33.5 54 34.5 58 36 58C39 58 41 55 42 50L44 34C45 33 46 32 47 30C49 26 50 20 48 14C46 8 40 6 32 6Z"
            fill="url(#toothMain)"
            stroke="url(#toothStroke)"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Left root */}
          <path
            d="M22 34C21 40 20 48 22 54C23 57 24.5 58 26 56C27 54 27.5 50 28 46"
            fill="none"
            stroke="url(#toothStroke)"
            strokeWidth="0"
          />

          {/* Right root */}
          <path
            d="M42 34C43 40 44 48 42 54C41 57 39.5 58 38 56C37 54 36.5 50 36 46"
            fill="none"
            stroke="url(#toothStroke)"
            strokeWidth="0"
          />

          {/* Crown detail — cusps/ridges on top */}
          <path
            d="M22 16C24 12 28 10 32 10C36 10 40 12 42 16"
            fill="none"
            stroke="#99f6e4"
            strokeWidth="1"
            strokeLinecap="round"
            opacity="0.6"
          />

          {/* Shine highlight */}
          <ellipse cx="27" cy="18" rx="5" ry="8" fill="url(#toothShine)" />
        </g>

        {/* Small sparkle dots */}
        <motion.circle
          cx="14" cy="10" r="1.5" fill="#14b8a6"
          animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 2, repeat: Infinity, delay: 0 }}
        />
        <motion.circle
          cx="50" cy="14" r="1" fill="#2dd4bf"
          animate={{ opacity: [0.2, 1, 0.2], scale: [0.8, 1.3, 0.8] }}
          transition={{ duration: 2, repeat: Infinity, delay: 0.7 }}
        />
        <motion.circle
          cx="48" cy="6" r="1.2" fill="#5eead4"
          animate={{ opacity: [0.4, 1, 0.4], scale: [0.9, 1.2, 0.9] }}
          transition={{ duration: 2, repeat: Infinity, delay: 1.3 }}
        />
      </motion.svg>

      {showText && (
        <div className="flex flex-col leading-tight">
          <span className={`text-xs tracking-widest uppercase font-semibold ${light ? 'text-teal-300' : 'text-teal-600'}`}>
            Dagdiya Dental
          </span>
          <span className={`text-[10px] font-script ${light ? 'text-gray-300' : 'text-gray-500'}`}>
            Caring For Your Smile
          </span>
        </div>
      )}
    </motion.div>
  );
};

export default Logo;
