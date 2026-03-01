# CA User Guide

Welcome to the CA Document Manager Desktop Application. This guide will help you manage your clients, documents, compliance, and profile.

## 1. Getting Started

### Initial Setup
1.  Launch the application.
2.  **Activation**: Enter the license token provided by your administrator/vendor.
3.  **Login**: Use your credentials (default: `admin` / `admin123`).

### Dashboard Overview
The dashboard provides a quick snapshot of your practice:
- **Total Clients**: Number of active clients.
- **Documents**: Total documents managed.
- **Compliance**: Pending compliance actions.
- **Reminders**: Upcoming deadlines.

## 2. Client Management

### Adding a New Client
1.  Navigate to **Clients** tab.
2.  Click **"Add New Client"**.
3.  Fill in details:
    - **Name**: Client's full name or business name.
    - **Phone**: 10-digit mobile number (used for login).
    - **Email**: Optional email address.
    - **Client Type**: Select `Salaried`, `Business`, or `Partnership` (affects compliance rules).
4.  Click **"Create Client"**.

### Editing/Deactivating
- Click the **Edit** icon on a client card to update details.
- Click the **Trash** icon to deactivate a client (data is preserved).

## 3. Document Management

### Organizing Documents
Your documents are stored locally on your computer in the `documents/` folder.
Structure: `documents/{client_phone}/{year}/{filename}`

### Uploading Documents
1.  Navigate to **Documents** tab.
2.  Click **"Upload Document"**.
3.  Select Client and Year.
4.  Drag & drop files or browse.
5.  Select **Document Type** (ITR, Form 16, etc.) or let auto-tagging handle it.
6.  Click **"Upload"**.

### Scanning Folders
If you manually copy files to the `documents/` folder:
1.  Go to **Documents**.
2.  Click **"Scan Folder"**.
3.  The system will index new files and attempt to auto-tag them based on filenames.

### Searching
- Use the search bar to find documents by **filename**, **tag**, or **year**.
- Filter by specific clients.

## 4. Compliance Calendar

### Viewing Status
1.  Navigate to **Compliance** tab.
2.  View a matrix of Clients vs. Required Documents.
3.  **Green Check**: Document present.
4.  **Red X**: Document missing.

### Rules
- **Salaried**: Requires ITR, Form 16, Bank Statement.
- **Business**: Requires ITR, GST Return, Audit Report.
- **Partnership**: Requires ITR, GST Return, Partner ITR.

## 5. Reminders & Notifications

### Creating a Reminder
1.  Navigate to **Reminders**.
2.  Click **"Create Reminder"**.
3.  Select Client.
4.  Choose Type:
    - **Document**: Reminder for a specific missing document.
    - **Custom**: Any text message.
5.  Set Date and Recurrence (e.g., Monthly for GST).

### Group Reminders
1.  Click **"Group Reminder"**.
2.  Select Filter (e.g., "All Salaried Clients missing Form 16").
3.  Enter message.
4.  Click **"Send"**. This logs a reminder for all matching clients.

## 6. CA Profile & Website

### Updating Profile
1.  Navigate to **Profile**.
2.  **Basic Info**: Update Firm Name, Address, Contact Info.
3.  **Media**: Upload carousel images for your public page.
4.  **Services**: Add/Edit services you offer.
5.  **Testimonials**: Add client reviews.

### Public Website
- Your public profile is available at: `http://localhost:8443/site/{username}`
- Share this link with potential clients.

## 7. Client Communication

### Sharing Access
- Provide the client with the **Portal URL** (`http://localhost:5174/portal`).
- Their login is their **Phone Number**.
- Default password is set during creation (reset recommended).

### Messaging
- Use the **Messaging** tab to send secure messages or files to clients.
