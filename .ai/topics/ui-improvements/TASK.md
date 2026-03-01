# UI/UX Improvements - Task List

## User Requirements

### 1. Remove from MVP
- [ ] Remove Notifications option
- [ ] Remove Settings option

### 2. Client Registration Improvements
- [ ] Show full name after registration (currently only first name)
- [ ] Create client directory if it doesn't exist
- [ ] Display directory location in UI after creation
- [ ] Fix client type display (shows "Unspecified" instead of selected type)

### 3. Documents Tab Redesign
- [ ] Group documents by client full name (not client ID/phone)
- [ ] Navigate into client folder to see all documents
- [ ] Add back button from client folder to documents list
- [ ] Add document preview (use system to open files)
- [ ] Show full filename on hover (tooltip)
- [ ] Make year display bigger in UI
- [ ] Support multiple document upload
- [ ] Support folder upload

## Implementation Plan

### Phase 1: Remove Unnecessary Features
1. Find and remove Notifications UI
2. Find and remove Settings UI

### Phase 2: Fix Client Registration
1. Update ClientList to show full name
2. Update backend to create directory on client creation
3. Add directory path to API response
4. Display directory location in InviteModal
5. Fix client_type persistence issue

### Phase 3: Documents Tab Overhaul
1. Update DocumentBrowser to group by client name
2. Fetch client data to map phone → name
3. Add back button navigation
4. Implement document preview
5. Add filename tooltip on hover
6. Increase year font size
7. Add multiple file upload support
8. Add folder upload support

## Files to Modify

### Frontend
- `ca_desktop/frontend/src/components/ca/Dashboard.tsx` - Remove notifications/settings
- `ca_desktop/frontend/src/components/ca/ClientList.tsx` - Show full name
- `ca_desktop/frontend/src/components/ca/InviteModal.tsx` - Show directory location
- `ca_desktop/frontend/src/components/ca/DocumentBrowser.tsx` - Major redesign
- `ca_desktop/frontend/src/components/ca/DocumentUpload.tsx` - Multiple/folder upload

### Backend
- `ca_desktop/backend/src/routers/clients.py` - Create directory, return path
- `ca_desktop/backend/src/routers/documents.py` - Support multiple uploads
