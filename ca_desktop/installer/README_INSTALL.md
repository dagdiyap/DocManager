# DocManager CA Desktop — Installation Guide

## For CAs (Non-Technical Users)

### Quick Start (Windows)

1. **Extract** the DocManager zip file to a folder (e.g., `C:\DocManager`)
2. **Double-click** `StartDocManager.bat`
3. **That's it!** On first run, the script will automatically:
   - Install Python (if not already installed)
   - Install Node.js (if not already installed)
   - Create a virtual environment and install all Python packages
   - Install WhatsApp bot dependencies
   - Set up the database and configuration
   - Start the backend server + WhatsApp bot
   - Open the application in your browser
4. **Keep the black window open** while using the application
5. To stop, close the black window or press `Ctrl+C`

### Requirements

- **Windows 10/11** (64-bit)
- **Internet connection** (for first-time setup only)
- Everything else is installed automatically by `StartDocManager.bat`

### WhatsApp Bot Setup

On first launch, a QR code will appear in the console window.
Scan it with your WhatsApp app to link the bot to your number.
The QR code only needs to be scanned once — the session persists.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port 8443 already in use" | Close the other DocManager window first |
| "Python was installed but not in PATH" | Close the window and run `StartDocManager.bat` again |
| "Node.js was installed but not in PATH" | Close the window and run `StartDocManager.bat` again |
| Application won't open in browser | Go to http://127.0.0.1:8443 manually |
| Antivirus blocks the installer | Add the DocManager folder to antivirus exceptions |
| "npm install failed" | Check internet connection, run `StartDocManager.bat` again |
| WhatsApp QR code not appearing | Wait 30 seconds — it may take time to initialize |

### Data Location

All your data is stored in the application folder:
- `ca_desktop.db` — Database (clients, documents, reminders)
- `documents/` — Client document files
- `shared_files/` — Manually shared files
- `logs/` — Application logs
- `keys/` — Security keys
- `.env` — Configuration (auto-generated on first run)

**Backup**: Copy the entire DocManager folder to keep a backup.

---

## For Developers

### Building the Windows Executable

1. On a Windows machine with Python 3.10+ and Node.js 18+:
   ```
   cd ca_desktop\installer
   build_windows.bat
   ```
2. The build script will:
   - Verify Python, Node.js, and npm are installed
   - Install all Python and Node.js dependencies
   - Build the frontend
   - Run PyInstaller to create the .exe
   - Copy WhatsApp server files and install npm deps in dist
   - Verify all required files are present
3. The executable will be in `ca_desktop\backend\dist\DocManager\`
4. Zip that folder and send to the CA

### Portable Distribution (No Build Required)

1. Zip the entire `DocManager/` project folder
2. Include: `ca_desktop/`, `shared/`, and `StartDocManager.bat`
3. CA extracts and runs `StartDocManager.bat`
4. **Everything installs automatically** — Python, Node.js, pip packages, npm packages
