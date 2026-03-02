# DocManager CA Desktop — Installation Guide

## For CAs (Non-Technical Users)

### Quick Start (Windows)

1. **Extract** the DocManager zip file to a folder (e.g., `C:\DocManager`)
2. **Double-click** `StartDocManager.bat`
3. On first run, it will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Set up the database
   - Open the application in your browser
4. **Keep the black window open** while using the application
5. To stop, close the black window or press `Ctrl+C`

### Requirements

- **Windows 10/11** (64-bit)
- **Python 3.10+** — Download from [python.org](https://www.python.org/downloads/)
  - **Important**: Check ✅ "Add Python to PATH" during installation
- **Node.js 18+** (optional, for WhatsApp bot) — Download from [nodejs.org](https://nodejs.org/)

### WhatsApp Bot Setup (Optional)

If Node.js is installed, the WhatsApp bot starts automatically.
On first run, scan the QR code shown in the console with your WhatsApp app.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python is not installed" | Install Python, check "Add to PATH" |
| "Port 8443 already in use" | Close the other DocManager window first |
| Application won't open | Check if antivirus is blocking it |
| WhatsApp not connecting | Ensure Node.js is installed, check internet |

### Data Location

All your data is stored in the `backend/` folder:
- `ca_desktop.db` — Database (clients, documents)
- `documents/` — Client document files
- `shared_files/` — Manually shared files
- `logs/` — Application logs

**Backup**: Copy the entire DocManager folder to keep a backup.

---

## For Developers

### Building the Windows Executable

1. On a Windows machine with Python 3.10+:
   ```
   cd ca_desktop\installer
   build_windows.bat
   ```
2. The executable will be in `ca_desktop\backend\dist\DocManager\`
3. Zip that folder and distribute to CAs

### Portable Distribution (No Build Required)

1. Zip the entire `DocManager/` project folder
2. Include: `ca_desktop/`, `shared/`, and the `.bat` launcher
3. CA extracts and runs `StartDocManager.bat`
4. Python + dependencies install automatically on first run
