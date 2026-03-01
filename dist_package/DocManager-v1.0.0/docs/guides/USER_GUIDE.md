# DocManager CA Desktop - User Guide

**For Chartered Accountants**  
**Version**: 1.0  
**Last Updated**: March 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Client Management](#client-management)
4. [Document Management](#document-management)
5. [Reminder System](#reminder-system)
6. [Public Website](#public-website)
7. [Compliance Tracking](#compliance-tracking)
8. [Client Portal](#client-portal)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

DocManager CA Desktop is a comprehensive document management and client portal system designed specifically for Chartered Accountants. It helps you:

- **Manage clients** efficiently with organized profiles
- **Store and share documents** securely
- **Send reminders** for document submissions and deadlines
- **Maintain a professional public website**
- **Track compliance** requirements
- **Provide client portal access** for document viewing

---

## Getting Started

### First Time Login

1. **Open your browser** and navigate to: `http://localhost:5174/ca/login`
2. **Enter credentials**:
   - Username: `lokesh`
   - Password: `lokesh`
3. **Click "Sign In"**

### Dashboard Overview

After login, you'll see the main dashboard with:
- **Client count** and quick stats
- **Recent documents**
- **Pending reminders**
- **Quick action buttons**

### Navigation Menu

- **Dashboard** - Overview and statistics
- **Clients** - Manage client profiles
- **Documents** - Upload and organize documents
- **Reminders** - Create and manage reminders
- **Profile** - Your CA firm profile
- **Compliance** - Track compliance status

---

## Client Management

### Adding a New Client

1. Navigate to **Clients** section
2. Click **"Invite Client"** or **"+ New Client"**
3. Fill in client information:
   - **Full Name** (required)
   - **Phone Number** (required) - Used for login
   - **Email** (optional but recommended)
   - **Client Type**: Individual, Business, or Unspecified
   - **Password** - For client portal access
4. Click **"Create Client"**

**Note**: A directory will be automatically created for the client at:  
`data/uploads/{client_phone}/`

### Viewing Client List

- **Search** - Use the search bar to find clients
- **Filter** - Filter by client type (Individual/Business)
- **Client Card** displays:
  - Name and phone number
  - Client type
  - Number of documents
  - Quick actions (Edit, View Documents)

### Editing Client Information

1. Click the **Edit** icon on client card
2. Update information as needed
3. Click **"Save Changes"**

### Client Details View

Click on a client name to see:
- Full profile information
- All documents for this client
- Pending reminders
- Compliance status

---

## Document Management

### Uploading Documents

#### Single Document Upload

1. Go to **Documents** section
2. Click **"Upload Document"**
3. Select:
   - **Client** (from dropdown)
   - **Year** (e.g., 2025)
4. **Drag and drop** file or **click to browse**
5. Click **"Upload Document"**

#### Multiple Documents Upload

1. Click **"Upload Multiple Documents"** or select multiple files
2. All selected files will be shown in a list
3. You can **remove** individual files before uploading
4. Click **"Upload X Document(s)"**

#### Folder Upload

1. Click **"Upload Folder"**
2. Select entire folder with documents
3. All files will be uploaded together
4. Maintains folder structure

**Supported Formats**: PDF, Excel (.xlsx, .xls), Word (.doc, .docx), Images (.jpg, .png), Text (.txt), ZIP archives

**Maximum Size**: 100 MB per file

### Browsing Documents

#### View by Client

1. Documents are **grouped by client name**
2. Click on a client folder to view their documents
3. Use **back button** to return to client list

#### Document Display

- **Year** is shown prominently
- **Filename** - hover to see full name
- **File icon** indicates file type
- **Download** button for each document

### Document Preview

- Click on a document to **preview** (uses system default application)
- Download documents for offline access

### Organizing Documents

Documents are automatically organized by:
- **Client name**
- **Year**
- **Upload date**

---

## Reminder System

The reminder system helps you notify clients about pending document submissions and deadlines.

### Creating Single Reminder

1. Navigate to **Reminders** section
2. Click **"Create Reminder"**
3. Fill in:
   - **Select Client** (single client)
   - **Document name** (e.g., "ITR Filing AY 2025-26")
   - **Document type** (ITR, GST, PAN, etc.)
   - **Year** (e.g., "2025-26")
   - **Reminder date**
   - **Delivery method**: Email, WhatsApp, or both
4. Click **"Create Reminder"**

### Creating Multi-Client Reminders

**Use Case**: Send same reminder to multiple clients

1. Click **"Create Reminder"**
2. **Select multiple clients** using checkboxes
   - Count shows: "3 clients selected"
3. **Add documents** (can add multiple):
   - Document name
   - Document type (dropdown)
   - Year (optional)
4. Click **"+ Add Document"** for multiple documents
5. Set **reminder date**
6. Choose **delivery method**:
   - ☑ Email - Sends professional email
   - ☑ WhatsApp - Generates WhatsApp link
7. Add **general instructions** (optional)
8. Click **"Create X Reminder(s)"**
   - Example: 3 clients × 2 documents = 6 reminders

### Document Types Available

- **ITR** - Income Tax Return
- **GST_GSTR1** - GST Return GSTR-1
- **GST_GSTR3B** - GST Return GSTR-3B
- **PAN_CARD** - PAN Card
- **TDS_RETURN** - TDS Return
- **AUDIT_REPORT** - Audit Report
- **FINANCIAL_STATEMENTS** - Financial Statements
- **OTHER** - Other documents

### Viewing Reminders

- **All Reminders** - Shows complete list
- **Filter by client** - See specific client's reminders
- **Status indicators**:
  - 🟡 Pending
  - 🟢 Sent
  - ✉️ Email sent
  - 💬 WhatsApp sent

### Reminder Actions

- **Mark as Sent** - Manually mark reminder as completed
- **Delete** - Remove reminder
- **View Details** - See full reminder information

---

## Public Website

Your professional website accessible to public.

### Setting Up Your Profile

1. Go to **Profile** section
2. Fill in **CA Profile Information**:
   - **Firm Name** (e.g., "Dagdiya Associates")
   - **Professional Bio**
   - **Contact Information**:
     - Phone number
     - Email
     - Office address
   - **Website URL** (optional)
   - **LinkedIn URL** (optional)

3. Click **"Update Profile"**

### Adding Services

1. In Profile section, scroll to **Services**
2. Click **"Add Service"**
3. Enter:
   - **Service name** (e.g., "Tax Planning & Filing")
   - **Description**
   - **Category** (tax, audit, gst, etc.)
4. Click **"Save Service"**

**Common Services**:
- Tax Planning & Filing
- GST Compliance
- Audit & Assurance
- Financial Advisory
- Company Formation
- Accounting Services

### Adding Testimonials

1. Go to **Testimonials** section
2. Click **"Add Testimonial"**
3. Enter:
   - **Client name**
   - **Testimonial text**
   - **Rating** (1-5 stars)
4. Click **"Save"**

### Upload Media

- **Logo** - Your CA firm logo
- **Carousel Images** - Background images for hero section
- **Service Icons** - Custom icons for services

### Accessing Your Public Website

Your website is available at:  
`http://localhost:5174/ca-lokesh-dagdiya`

Share this URL with potential clients!

---

## Compliance Tracking

### Viewing Compliance Status

1. Navigate to **Compliance** section
2. View **compliance rules** applicable to your clients
3. Check **client compliance status**:
   - Green ✓ - Compliant
   - Red ✗ - Non-compliant
   - Yellow ⚠ - Partial compliance

### Setting Compliance Requirements

1. Define what documents are required
2. Track submission deadlines
3. Monitor client compliance in real-time

### Compliance Reports

Generate reports showing:
- Clients missing documents
- Upcoming deadlines
- Compliance rate statistics

---

## Client Portal

Your clients can access their documents through the client portal.

### Client Portal URL

`http://localhost:5174/portal/login`

### Client Login Credentials

- **Username**: Client's phone number
- **Password**: Set during client creation

### What Clients Can Do

✓ View all their documents  
✓ Download documents  
✓ See pending reminders  
✓ Check compliance status

### Sharing Portal Access

1. Create client account in your system
2. Share portal URL with client
3. Provide login credentials (phone + password)
4. Client can access anytime

---

## Best Practices

### Document Organization

1. **Consistent Naming**: Use clear document names
   - Good: "ITR_AY2025-26_JohnDoe.pdf"
   - Avoid: "doc1.pdf"

2. **Upload Regularly**: Don't wait to batch upload

3. **Use Years**: Always specify the correct year

4. **File Formats**: Prefer PDF for final documents

### Client Management

1. **Complete Profiles**: Fill all client information
2. **Update Regularly**: Keep contact information current
3. **Set Client Types**: Helps with filtering and compliance
4. **Portal Access**: Enable portal for all clients

### Reminder Management

1. **Plan Ahead**: Set reminders 30-45 days before deadline
2. **Use Templates**: Create standard reminders for common documents
3. **Multi-Client Reminders**: Batch process for efficiency
4. **Follow Up**: Check reminder status regularly

### Security

1. **Strong Passwords**: Use complex passwords
2. **Regular Backups**: Backup database regularly
3. **Client Privacy**: Never share client documents
4. **Logout**: Always logout when done

---

## Troubleshooting

### Cannot Login

**Problem**: Login fails  
**Solution**:
- Check username and password
- Ensure backend is running (`./start.sh`)
- Clear browser cache
- Check console for errors

### Document Upload Fails

**Problem**: Document won't upload  
**Solution**:
- Check file size (max 100 MB)
- Verify file format is supported
- Ensure client is selected
- Check disk space

### Client Portal Not Working

**Problem**: Client cannot login  
**Solution**:
- Verify password is set for client
- Check phone number is correct (no spaces/dashes)
- Ensure backend is running
- Test with demo credentials first

### Reminders Not Sending

**Problem**: Email reminders not delivered  
**Solution**:
- Check `.env` file has `RESEND_API_KEY`
- Verify client email is valid
- Check backend logs for errors
- Test with "Email" option enabled

### Public Website Not Loading

**Problem**: Public website shows error  
**Solution**:
- Ensure CA profile is complete
- Check firm name is set
- Verify frontend is running
- Check URL is correct

### Performance Issues

**Problem**: System is slow  
**Solution**:
- Close unnecessary browser tabs
- Clear old documents
- Archive old reminders
- Restart application

---

## Support & Updates

### Getting Help

- Check this user guide first
- Review the troubleshooting section
- Contact your system administrator

### System Information

- **Backend**: FastAPI + SQLite
- **Frontend**: React + TypeScript
- **Database**: `ca_desktop.db`
- **Logs**: `logs/` directory

### Version Information

Check current version in **Profile > About**

---

## Quick Reference

### Common Tasks

| Task | Steps |
|------|-------|
| Add Client | Clients → Invite Client → Fill form → Create |
| Upload Document | Documents → Upload → Select client → Choose file |
| Send Reminder | Reminders → Create → Select clients → Add documents → Create |
| Update Profile | Profile → Edit fields → Update Profile |
| Client Portal | Share portal URL + credentials |

### Keyboard Shortcuts

- `Ctrl/Cmd + K` - Quick search
- `Ctrl/Cmd + U` - Upload document
- `Esc` - Close modal

### Important URLs

- **CA Dashboard**: http://localhost:5174/ca
- **Client Portal**: http://localhost:5174/portal
- **Public Website**: http://localhost:5174/ca-lokesh-dagdiya
- **API Docs**: http://localhost:8443/docs

---

**DocManager CA Desktop** - Professional Document Management for Chartered Accountants

*For technical support or feature requests, contact your system administrator.*
