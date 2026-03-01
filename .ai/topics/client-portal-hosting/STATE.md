# Client Portal Hosting - Architecture Analysis

## Current Architecture

### What Works Today (Local Only)
- Backend binds to `127.0.0.1:8443` (localhost only)
- Frontend runs on `localhost:5174`
- CORS allows only localhost origins
- Client logs in via phone number + password
- Documents served via `FileStreamer` from local disk
- Rate limiting: 60 req/min per IP (in-memory)
- Single uvicorn worker (low resource usage)

### What DOES NOT Work for External Client Access

#### 1. CRITICAL: Backend binds to 127.0.0.1
- `config.py` line 91: `host: str = Field(default="127.0.0.1")`
- This means ONLY the CA's own machine can reach the API
- External clients on the internet CANNOT connect
- **Fix needed:** Bind to `0.0.0.0` for external access

#### 2. CRITICAL: No way for internet clients to reach CA's laptop
- CA's laptop is behind NAT/router (no public IP)
- ISP typically assigns dynamic IP
- No DNS entry points to CA's machine
- **Options:**
  - a) Tunneling service (ngrok, Cloudflare Tunnel, bore)
  - b) Reverse proxy on cloud VPS
  - c) Deploy backend to cloud (Railway, Render)

#### 3. CRITICAL: CORS blocks external origins
- Only allows `localhost:3000/5173/5174` and `127.0.0.1` variants
- Vercel website at `ca-lokesh-dagdiya.vercel.app` would be blocked
- **Fix needed:** Add deployed website origin to CORS

#### 4. CRITICAL: No HTTPS for production
- `enable_https: bool = True` is configured but no SSL cert
- Browsers block mixed content (HTTPS website → HTTP API)
- **Fix needed:** SSL termination via tunnel or reverse proxy

#### 5. HIGH: Rate limiting is in-memory only
- Resets on restart
- No per-user throttling (only per-IP)
- Could be bypassed via different IPs
- **Acceptable for MVP** but needs improvement

#### 6. HIGH: Single worker, no async file streaming
- `workers=1` in production config
- FileResponse is synchronous - blocks event loop for large files
- **Acceptable for <10 clients** but could cause lag

#### 7. MEDIUM: No connection pooling or caching
- SQLite with single connection
- No Redis/caching layer
- Every page load = multiple DB queries
- **Acceptable for <10 clients**

#### 8. MEDIUM: No health monitoring
- If CA closes laptop, clients see connection error
- No "CA is offline" graceful handling
- No automatic reconnection

## Architecture Options

### Option A: Cloudflare Tunnel (RECOMMENDED for MVP)
```
Client Browser → Vercel (website) → Cloudflare Tunnel → CA Laptop (backend)
```
- **Free tier:** Unlimited tunnels
- **How:** Install `cloudflared` on CA's laptop, create tunnel
- **Pros:** Free, secure (no port opening), auto-HTTPS, works behind NAT
- **Cons:** Requires CA to keep laptop on, tunnel running
- **Setup time:** 10 minutes
- **Resource impact:** Minimal (<50MB RAM, <1% CPU)

### Option B: Deploy Backend to Cloud (BEST for 24/7)
```
Client Browser → Vercel (website) → Railway/Render (backend + DB)
```
- **Free tier:** Railway 500hrs/month, Render 750hrs/month
- **How:** Deploy FastAPI to cloud, migrate SQLite → PostgreSQL
- **Pros:** 24/7 uptime, no laptop dependency, scalable
- **Cons:** Requires DB migration, costs after free tier
- **Setup time:** 1-2 hours
- **Resource impact:** Zero on CA's laptop

### Option C: ngrok Tunnel (Quick Demo)
```
Client Browser → Vercel (website) → ngrok → CA Laptop (backend)
```
- **Free tier:** 1 tunnel, random URL, 40 conn/min
- **Pros:** Fastest setup (2 minutes)
- **Cons:** Random URL changes, rate limited, not production-ready
- **Setup time:** 2 minutes

### Option D: VPS Reverse Proxy (Most Control)
```
Client Browser → VPS (nginx + domain) → WireGuard → CA Laptop
```
- **Cost:** $5-10/month VPS
- **Pros:** Custom domain, full control, persistent
- **Cons:** Complex setup, VPS maintenance
- **Setup time:** 2-4 hours

## Recommendation

### For TODAY (Demo with Lokesh): Option C (ngrok)
- Install ngrok, expose backend, update Vercel env var
- 5 minutes to working demo

### For PRODUCTION (Week 1): Option A (Cloudflare Tunnel)
- Free, secure, reliable
- CA installs `cloudflared` alongside DocManager
- Auto-starts with the application

### For SCALE (Month 1+): Option B (Cloud Backend)
- Migrate to Railway/Render
- SQLite → PostgreSQL
- 24/7 uptime, no laptop dependency

## Changes Required for External Access

### Backend Changes
1. Config: Allow `0.0.0.0` binding when `EXTERNAL_ACCESS=true`
2. CORS: Dynamic origins from env var
3. HTTPS: Let tunnel handle SSL termination
4. Rate limit: Increase for legitimate external traffic

### Frontend Changes (Vercel Website)
1. `VITE_API_URL` must point to tunnel/cloud URL
2. Error handling for "CA is offline" scenario

### Testing Needed
1. End-to-end: Client login → Document fetch via tunnel
2. File download performance over internet
3. Concurrent users (at least 5 simultaneous)
4. Memory/CPU usage on CA laptop under load
5. Reconnection after tunnel restart

## Resource Impact Assessment

### CA Laptop Running Backend (Current)
- **RAM:** ~80MB (Python + uvicorn + SQLite)
- **CPU:** <1% idle, 5-10% under API call
- **Disk I/O:** Minimal (SQLite reads)

### With Cloudflare Tunnel Added
- **RAM:** +30MB for cloudflared
- **CPU:** +<1% (just proxying)
- **Network:** Proportional to client traffic

### Under Load (10 concurrent clients)
- **RAM:** ~120MB total
- **CPU:** 10-20% during document downloads
- **Acceptable** for modern laptop/desktop

## NOT Tested Yet
- Docker networking setup
- DNS resolution through tunnel
- SSL/HTTPS end-to-end
- File download performance over internet
- Concurrent client access
- CA laptop sleep/hibernate behavior
- Firewall traversal on Windows
