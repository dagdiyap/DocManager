# Phase 2 API Reference - Quick Guide

## Base URL
```
http://localhost:8443/api/v1
```

---

## 🏷️ Tags Endpoints

### List All Tags
```bash
GET /tags
```
Response:
```json
[
  {
    "id": 1,
    "name": "ITR",
    "description": "Income Tax Return",
    "regex_pattern": "ITR|Income Tax Return",
    "created_at": "2026-02-22T10:00:00"
  }
]
```

### Auto-Tag Documents
```bash
POST /documents/auto-tag?client_phone=9876543210&year=2024
```
Response:
```json
{
  "assigned_count": 3,
  "total_documents": 3,
  "message": "Auto-tagged 3 documents"
}
```

### Get Document Tags
```bash
GET /documents/5/tags
```

### Add Tags to Document
```bash
POST /documents/5/tags
Body: {"tag_ids": [1, 2]}
```

### Remove Tag from Document
```bash
DELETE /documents/5/tags/1
```

---

## 📋 Compliance Endpoints

### List Compliance Rules
```bash
GET /compliance/rules?client_type=Salaried
```
Response:
```json
[
  {
    "id": 1,
    "name": "Salaried Employee Compliance",
    "client_type": "Salaried",
    "required_document_tags": ["ITR", "Form 16", "Bank Statement"],
    "created_at": "2026-02-22T10:00:00"
  }
]
```

### Get Client Compliance Status
```bash
GET /clients/9876543210/compliance
```
Response:
```json
{
  "client_phone": "9876543210",
  "client_type": "Salaried",
  "is_compliant": true,
  "missing_count": 0,
  "total_required": 3,
  "applicable_rules": [
    {
      "rule_id": 1,
      "rule_name": "Salaried Employee Compliance",
      "required_documents": [
        {
          "tag_name": "ITR",
          "has_document": true,
          "latest_upload_date": "2026-02-20T15:30:00"
        }
      ]
    }
  ]
}
```

### Update Client Type
```bash
PATCH /clients/9876543210
Body: {"client_type": "Business"}
```

---

## 🔔 Reminders Endpoints

### Create Reminder
```bash
POST /reminders
Body: {
  "client_phone": "9876543210",
  "reminder_type": "document_type",
  "tag_id": 1,
  "reminder_date": "2026-03-01T09:00:00",
  "message": "Please arrange ITR documents",
  "is_recurring": true,
  "recurrence_pattern": "yearly"
}
```

### List Reminders
```bash
GET /reminders?client_phone=9876543210&start_date=2026-02-01&end_date=2026-03-31
```

### Update Reminder
```bash
PATCH /reminders/5
Body: {
  "reminder_date": "2026-03-15T09:00:00",
  "message": "Updated reminder message"
}
```

### Delete Reminder
```bash
DELETE /reminders/5
```

### Send Group Reminders
```bash
POST /reminders/send-group
Body: {
  "filter_type": "missing_documents",
  "tag_id": 2,
  "message": "Please arrange Form 16 documents"
}
```
Response:
```json
{
  "sent_count": 5,
  "affected_clients": ["9876543210", "9876543211"],
  "message": "Sent reminders to 5 clients"
}
```

---

## 👤 CA Profile Endpoints

### Get CA Profile
```bash
GET /ca/profile
```

### Update CA Profile
```bash
PATCH /ca/profile
Body: {
  "firm_name": "Sharma Chartered Accountants",
  "professional_bio": "Expert in tax and GST",
  "address": "123 Main Street, Delhi",
  "gstin_pan": "ABCDE1234F",
  "phone_number": "+91-9999999999",
  "email": "contact@example.com"
}
```

### Upload Media
```bash
POST /ca/media
Body (multipart):
  - item_type: "carousel"
  - file: <binary image>
  - title: "Office Photo"
  - description: "Our office building"
  - order_index: 0
```

### List Media
```bash
GET /ca/media?item_type=carousel
```

### Reorder Media
```bash
PUT /ca/media/5/order
Body: {"order_index": 2}
```

### Create Service
```bash
POST /ca/services
Body: {
  "name": "ITR Filing",
  "description": "Complete ITR filing service for individuals and businesses",
  "order_index": 1
}
```

### List Services
```bash
GET /ca/services
```

### Update Service
```bash
PATCH /ca/services/5
Body: {
  "name": "GST Return Filing",
  "description": "Complete GST return filing"
}
```

### Delete Service
```bash
DELETE /ca/services/5
```

### Create Testimonial
```bash
POST /ca/testimonials
Body: {
  "client_name": "Amit Kumar",
  "text": "Excellent service and quick response!",
  "rating": 5
}
```

### List Testimonials
```bash
GET /ca/testimonials
```

---

## 🌐 Public Endpoints (No Auth Required)

### Get Public CA Profile
```bash
GET /public/ca/admin/profile
```

### Get Public Media
```bash
GET /public/ca/admin/media?item_type=carousel
```

### Get Public Services
```bash
GET /public/ca/admin/services
```

### Get Public Testimonials
```bash
GET /public/ca/admin/testimonials
```

### Get Client Portal Link
```bash
GET /public/ca/admin/clients/123
```

---

## 🔍 Document Search

### Search Documents with Filters
```bash
GET /documents/search?client_phone=9876543210&year=2024&tags=ITR,Form%2016&file_type=pdf&uploaded_after=2026-01-01
```
Query Parameters:
- `client_phone` (optional) - Filter by client
- `year` (optional) - Filter by year
- `tags` (optional) - Comma-separated tag names
- `file_type` (optional) - File extension (pdf, xlsx, etc.)
- `uploaded_after` (optional) - ISO datetime
- `uploaded_before` (optional) - ISO datetime

Response:
```json
[
  {
    "id": 1,
    "client_phone": "9876543210",
    "year": "2024",
    "file_name": "ITR_2024.pdf",
    "file_size": 250000,
    "uploaded_at": "2026-02-22T10:30:00",
    "tags": [
      {"id": 1, "name": "ITR"}
    ]
  }
]
```

---

## 🔐 Authentication

### For CA Endpoints
Include JWT token in headers:
```bash
Authorization: Bearer <ca_token>
```

### For Client Endpoints
Include JWT token in headers:
```bash
Authorization: Bearer <client_token>
```

### Public Endpoints
No authentication required.

---

## 📊 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 403 | Forbidden (permission denied) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |

---

## 🧪 Testing Examples

### Using cURL

**List all tags:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8443/api/v1/tags
```

**Get client compliance:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8443/api/v1/clients/9876543210/compliance"
```

**Search documents:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8443/api/v1/documents/search?year=2024&tags=ITR"
```

**Get public profile (no auth):**
```bash
curl http://localhost:8443/api/v1/public/ca/admin/profile
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8443/api/v1"
headers = {"Authorization": f"Bearer {token}"}

# Get compliance status
response = requests.get(
    f"{BASE_URL}/clients/9876543210/compliance",
    headers=headers
)
print(response.json())

# Search documents
response = requests.get(
    f"{BASE_URL}/documents/search",
    params={"year": "2024", "tags": "ITR"},
    headers=headers
)
print(response.json())

# Get public profile (no auth)
response = requests.get(f"{BASE_URL}/public/ca/admin/profile")
print(response.json())
```

---

## 📝 Notes

- All date-time fields are in ISO 8601 format
- Tag names are case-sensitive
- Client phone numbers must be 10-15 digits
- File uploads must include proper multipart form data
- Download tokens expire after 24 hours (configurable)

---

**Last Updated:** February 22, 2026  
**Version:** Phase 2 API v1.0


