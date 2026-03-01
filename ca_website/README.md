# CA Lokesh Dagdiya - Professional Website

Standalone website for CA Lokesh Dagdiya showcasing 47 years of excellence in chartered accountancy services.

## Features

- ✅ Moving banner carousel with professional CA images
- ✅ DAGDIYA ASSOCIATES branding
- ✅ 47-year legacy content
- ✅ 6 professional services
- ✅ 3 personalized client testimonials
- ✅ Industries served section with background images
- ✅ Contact information and call-to-action
- ✅ Fully responsive design
- ✅ No login/portal dependencies

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment to Vercel

1. Push this directory to GitHub
2. Import to Vercel
3. Set environment variable: `VITE_API_URL=https://your-backend-url.com/api/v1`
4. Deploy

## Project Structure

```
ca_website/
├── src/
│   ├── components/
│   │   └── CAWebsite.tsx    # Main website component
│   ├── App.tsx               # App wrapper
│   ├── main.tsx              # Entry point
│   └── index.css             # Tailwind styles
├── public/                   # Static assets
├── index.html                # HTML template
└── vite.config.ts            # Vite configuration
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8443/api/v1
```

For production, set this in Vercel dashboard.

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Lucide React (icons)
- React Hot Toast

## License

Private - Dagdiya Associates
