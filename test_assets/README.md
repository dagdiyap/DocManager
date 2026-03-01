# Test Assets for DocManager Browser Testing

This directory contains sample files and data for comprehensive browser testing of the DocManager CA Desktop application.

## Directory Structure

```
test_assets/
├── bulk_upload/
│   └── clients_import.xlsx      # Excel file with 3 client records for bulk import
└── documents/
    ├── sample_itr.txt           # Income Tax Return document
    ├── sample_gst_return.txt    # GST Return (GSTR-3B)
    ├── sample_audit_report.txt  # Independent Auditor's Report
    ├── sample_pan_card.txt      # PAN Card details
    └── sample_aadhar.txt        # Aadhaar Card details
```

## Test Data Details

### Bulk Upload Clients (clients_import.xlsx)

| Name | Phone | Email | PAN | Aadhaar |
|------|-------|-------|-----|---------|
| Piyush Dagdiya | 9876543210 | piyushdagdiya@gmail.com | ABCDE1234F | 123456789012 |
| Rahul Sharma | 9876543211 | rahul.sharma@example.com | BCDEF2345G | 234567890123 |
| Priya Patel | 9876543212 | priya.patel@example.com | CDEFG3456H | 345678901234 |

**Note**: The first client (Piyush Dagdiya) should receive an email verification at piyushdagdiya@gmail.com after registration.

### Sample Documents

1. **sample_itr.txt** - Income Tax Return for Piyush Dagdiya (AY 2025-26)
2. **sample_gst_return.txt** - GST GSTR-3B return for Rahul Sharma's business
3. **sample_audit_report.txt** - Audit report for Priya Patel's company
4. **sample_pan_card.txt** - PAN card details for identity verification
5. **sample_aadhar.txt** - Aadhaar card for address verification

## Usage Instructions

These files are designed to be used with the browser automation testing workflow. Refer to `BROWSER_TESTING_WORKFLOW.md` for detailed testing instructions.

## File Types to Test

The documents provided are in `.txt` format for simplicity. During testing, you should:

1. Upload these files as-is to test .txt file handling
2. Create PDF versions (if possible) to test PDF handling
3. Test image uploads by taking screenshots or using sample images
4. Test Excel file upload via the bulk import feature

## Expected Outcomes

- ✅ All documents should upload successfully
- ✅ Documents should be categorized correctly (ITR, GST, Audit, Identity)
- ✅ Email verification should be sent to piyushdagdiya@gmail.com
- ✅ Bulk upload should import all 3 clients
- ✅ File metadata should be preserved (filename, size, upload date)
- ✅ Documents should be downloadable after upload
