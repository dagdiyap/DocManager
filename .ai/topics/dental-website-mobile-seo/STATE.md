# STATE — Dental Website Mobile UX + SEO

## Decisions
- All mobile button sizes reduced via responsive Tailwind classes (px-4/px-5 mobile, px-6/px-8 desktop)
- Hero buttons arranged in flex-row (side-by-side) instead of flex-col on mobile
- WABtn component made fully responsive with breakpoint-aware padding/text
- Service cards: uniform 180px height, removed Crown & Bridges (8 → 8 services)
- Stats updated to user-specified values (25 yrs, 20K+ patients)
- "Your Smile Our Passion" gets staggered spring animation: words fly in, "Smile"/"Passion" scale-pop
- SEO: targeting "dentist in Nanded", "dental clinic Nanded", "best dentist nanded", etc.
- Structured data: Dentist schema + FAQPage schema for rich results
- Footer year updated to "since 2001" (matching 25+ years from 2026)
- Marquee 3x faster (30s → 10s), counter 1.5x faster (125→83 divisor)

## Implementation Log
- App.tsx: Removed "Nanded's Most Trusted" badge, de-cluttered hero, added word-by-word stagger animation
- App.tsx: Reduced mobile button sizes throughout (hero, CTA sections)
- App.tsx: Reduced Lando section from 100vh to 50vh/60vh
- App.tsx: Reduced CTA section padding py-24 → py-12/py-16, smaller heading + emoji
- App.tsx: Updated stats to 25+ years, 20K+ patients, floating badge 25+
- App.tsx: Removed "advanced" from Dr. Rajesh description
- App.tsx: Added SEO alt tags to hero and inauguration images
- App.tsx: Added keyword-rich footer description
- App.tsx: Updated "since 2001" in footer
- data.ts: Updated STATS values, removed Crown & Bridges from SERVICES
- UI.tsx: Made WABtn responsive with sm: breakpoints, 1.5x counter speed
- index.css: Marquee speed 30s → 10s
- index.html: Complete SEO overhaul (title, meta, OG, Twitter, canonical, JSON-LD Dentist + FAQPage)
