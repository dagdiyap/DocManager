# User Guide: Local E2E Workflow Testing (UI Mode)

This guide provides step-by-step instructions for running the CA Document Manager ecosystem on your local machine and performing an end-to-end workflow test using the real User Interfaces.

## 1. Prerequisites & Dependencies

Ensure you have the following installed:
- **Python 3.9+**
- **Node.js 18+** & **npm**

### Backend Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
pip install -r license_server/requirements.txt
pip install -r ca_desktop/backend/requirements.txt
pip install pytest httpx requests  # For test suite
```

### Frontend Setup
```bash
# Install UI dependencies for both frontends from the project root
npm install --prefix license_server/ui
npm install --prefix ca_desktop/frontend
```

---

## 2. Bootstrapping & Launch

Before starting, create a default administrator for the CA Desktop.

```bash
# Run the bootstrap script
python3 scripts/bootstrap_local.py
```

### Start the Ecosystem
Run the master orchestration script to launch all 4 services (2 Backends, 2 UIs):
```bash
./start_local.sh
```

**Services will be available at:**
- **License Admin UI**: [http://localhost:5173](http://localhost:5173)
- **CA Desktop UI**: [http://localhost:5174](http://localhost:5174)
- **License API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **CA Desktop API Docs**: [http://localhost:8443/docs](http://localhost:8443/docs)

---

## 3. End-to-End Workflow Walkthrough

Follow these steps to verify the full system logic:

### Step A: Register the CA (License Authority)
1. Go to the **License Admin UI** (5173).
2. Look for the **"Register New CA"** section.
3. Enter details:
   - **ID**: `CA-LOCAL-01`
   - **Name**: `Local Test Accountant`
   - **Email**: `ca@test.com`
4. Click **Register**. You should see the CA appearing in the list.

### Step B: Activate CA Desktop
1. Go to the **CA Desktop UI** (5174).
2. Since no license is installed, you will see a **"License Required"** overlay or prompt.
3. Switch back to **License Admin UI** (5173).
4. Find `CA-LOCAL-01` and look for the **"Issue License"** button.
5. In the pop-up, you'll need the **Device ID**. 
   *   You can find your Device ID on the CA Desktop UI prompt, or generate it via API: `curl http://localhost:8443/api/v1/license/status`
6. Click **Issue Token**. Copy the long signed token string.
7. Go back to **CA Desktop UI** (5174).
8. Paste the token into the **Activate** field and click **Install**. 
9. The UI should unlock and redirect you to the **CA Login**.

### Step C: CA Workstation Management
1. **Login** with the bootstrapped credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
2. Go to **Clients** tab and click **Add New Client**.
   - **Name**: `Client Rajesh`
   - **Phone**: `9876543210`
   - **Password**: `client123`
3. Click **Save**.
4. Go to **Documents** tab.
5. In your local filesystem, create a folder named `9876543210` inside the `documents/` folder.
6. Drop some dummy PDFs into that folder.
7. Click **"Scan Folder"** on the UI.
8. The PDFs should now appear in the Document list, indexed for the client.

### Step D: Client Side Verification
1. Open a new Incognito/Private window.
2. Go to **CA Desktop UI** (5174) - it will show the Unified Login.
3. Login as the **Client**:
   - **Phone Number**: `9876543210`
   - **Password**: `client123`
4. You will be redirected to the **Client Portal**.
5. You should see the documents indexed in Step C.
6. Click **Download** on a file to verify the secure HMAC token generation and download flow.

---

## 4. Troubleshooting

- **Port Conflicts**: Ensure ports 8000, 8443, 5173, and 5174 are free. Use `lsof -i :PORT` to check.
- **SQLite Locking**: If the UI hangs on "Save", it's likely a database lock. Restart the servers using `CTRL+C` and `./start_local.sh`.
- **CORS Issues**: Both backend servers are configured to allow `localhost:5173` and `localhost:5174`. Ensure you are using these exact URLs.
