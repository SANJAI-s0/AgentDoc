# Document Management Guide

## API Endpoints

### 1. Upload Document
**POST** `/api/documents/upload/`

Upload a new document for processing.

**Request (Multipart Form Data):**
```
file: <file>
title: "Invoice for March 2024"
source_channel: "web"
document_type_hint: "invoice"  (optional)
```

**Response:**
```json
{
  "document": {
    "document_id": "doc_abc123",
    "status": "processing",
    "title": "Invoice for March 2024",
    "file_name": "invoice.pdf",
    "document_type": "invoice"
  },
  "workflow": { ... }
}
```

### 2. List Documents
**GET** `/api/documents/`

Get all documents for the current user.

**Response:**
```json
[
  {
    "document_id": "doc_abc123",
    "title": "Invoice for March 2024",
    "status": "completed",
    "document_type": "invoice",
    "created_at": "2024-03-18T10:30:00Z"
  }
]
```

### 3. Get Document Details
**GET** `/api/documents/{document_id}/`

Get full details of a specific document.

**Response:**
```json
{
  "document": { ... },
  "pages": [ ... ],
  "extraction": { ... },
  "validation": { ... },
  "reviews": [ ... ],
  "audit_logs": [ ... ]
}
```

### 4. Update Document (NEW!)
**PATCH** `/api/documents/{document_id}/`

Update document metadata.

**Request:**
```json
{
  "title": "Updated Invoice Title",
  "document_type_hint": "receipt",
  "force_review": true
}
```

**Allowed Fields:**
- `title` - Document title
- `document_type_hint` - Hint for document classification
- `force_review` - Force human review

**Response:**
```json
{
  "document_id": "doc_abc123",
  "title": "Updated Invoice Title",
  "document_type_hint": "receipt",
  "force_review": true,
  "updated_at": "2024-03-18T11:00:00Z"
}
```

### 5. Delete Document (NEW!)
**DELETE** `/api/documents/{document_id}/`

Delete a document and all related data.

**Response:**
```json
{
  "detail": "Document deleted successfully.",
  "document_id": "doc_abc123"
}
```

**What Gets Deleted:**
- Document record
- All pages
- Extraction results
- Validation results
- Review records
- File from storage (if possible)

**Note:** Audit logs are preserved for compliance.

## Document Types

### Supported Document Types

1. **invoice** - Invoices and bills
2. **receipt** - Purchase receipts
3. **kyc_form** - KYC/identity documents
4. **loan_application** - Loan applications
5. **insurance_claim** - Insurance claims
6. **shipping_document** - Shipping/logistics documents
7. **contract** - Legal contracts
8. **handwritten_form** - Handwritten forms

### Document Status

- **processing** - Being processed by AI agents
- **completed** - Successfully processed
- **pending_review** - Needs human review
- **rejected** - Rejected by reviewer
- **failed** - Processing failed

## Valid vs Invalid Documents

### ✅ Valid Documents

#### 1. PDF Invoice
```
File: invoice_march_2024.pdf
Type: application/pdf
Size: 250 KB
Pages: 2
Content: Clear text, good quality scan
```

**Why Valid:**
- Supported file type (PDF)
- Reasonable file size
- Clear, readable content
- Standard invoice format

#### 2. Image Receipt
```
File: receipt_20240318.jpg
Type: image/jpeg
Size: 1.5 MB
Resolution: 1920x1080
Content: Clear photo of receipt
```

**Why Valid:**
- Supported image format
- Good resolution
- Clear, readable text
- Proper lighting

#### 3. Scanned KYC Form
```
File: kyc_form_john_doe.pdf
Type: application/pdf
Size: 500 KB
Pages: 3
Content: Government ID, address proof
```

**Why Valid:**
- PDF format
- Multiple pages supported
- Contains required KYC fields
- Good scan quality

### ❌ Invalid Documents

#### 1. Corrupted PDF
```
File: corrupted_invoice.pdf
Type: application/pdf
Size: 0 KB
Error: "Unable to read PDF"
```

**Why Invalid:**
- File is corrupted or empty
- Cannot extract pages
- No readable content

#### 2. Unsupported Format
```
File: document.docx
Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Error: "Unsupported file type"
```

**Why Invalid:**
- DOCX not supported
- Only PDF, images, and text files supported
- Convert to PDF first

#### 3. Low Quality Image
```
File: blurry_receipt.jpg
Type: image/jpeg
Size: 50 KB
Resolution: 320x240
Content: Blurry, unreadable
```

**Why Invalid:**
- Too low resolution
- Blurry or out of focus
- OCR cannot extract text
- Will be routed to manual review

#### 4. Duplicate Document
```
File: invoice_march_2024.pdf
Checksum: abc123def456
Error: "Duplicate document detected"
Status: 409 Conflict
```

**Why Invalid:**
- Same file already uploaded
- Duplicate detection by checksum
- Prevents duplicate processing

#### 5. Too Large File
```
File: huge_document.pdf
Type: application/pdf
Size: 50 MB
Error: "File too large"
```

**Why Invalid:**
- Exceeds size limit
- May cause processing timeout
- Compress or split the file

#### 6. Password Protected
```
File: protected_invoice.pdf
Type: application/pdf
Error: "Cannot extract pages"
```

**Why Invalid:**
- Password protected
- Cannot extract content
- Remove password first

## Best Practices

### For Uploading

1. **Use Clear Scans**
   - 300 DPI or higher
   - Good lighting
   - Straight alignment
   - No shadows

2. **Optimize File Size**
   - Compress large PDFs
   - Use JPEG for photos
   - Keep under 10 MB

3. **Provide Hints**
   - Use `document_type_hint` for better classification
   - Add descriptive titles
   - Include metadata

4. **Check Quality**
   - Preview before upload
   - Ensure text is readable
   - Verify all pages included

### For Managing

1. **Update Metadata**
   - Fix incorrect titles
   - Add document type hints
   - Force review if needed

2. **Delete Unused**
   - Remove test documents
   - Clean up rejected documents
   - Keep only necessary files

3. **Monitor Status**
   - Check processing status
   - Review validation results
   - Act on review requests

## Error Handling

### Common Errors

#### 409 Conflict - Duplicate Document
```json
{
  "detail": "Duplicate document detected.",
  "duplicate_document_id": "doc_xyz789"
}
```

**Solution:** Document already exists. Use the existing document ID or delete the old one first.

#### 503 Service Unavailable - Storage Error
```json
{
  "detail": "Document storage unavailable. Check MinIO connection."
}
```

**Solution:** MongoDB or storage service is down. Check connection and try again.

#### 500 Internal Server Error - Workflow Failed
```json
{
  "detail": "Workflow failed for this document. [Error details]"
}
```

**Solution:** AI processing failed. Document will be marked as failed. Check audit logs for details.

#### 400 Bad Request - Unsupported File
```json
{
  "detail": "Unsupported file type. Supported: PDF, image, and text."
}
```

**Solution:** Convert file to PDF, JPEG, PNG, or TXT format.

## Examples

### Upload with cURL

```bash
# Upload a PDF invoice
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@invoice.pdf" \
  -F "title=March 2024 Invoice" \
  -F "source_channel=web" \
  -F "document_type_hint=invoice"
```

### Update with cURL

```bash
# Update document title
curl -X PATCH http://localhost:8000/api/documents/doc_abc123/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Invoice Title"}'
```

### Delete with cURL

```bash
# Delete a document
curl -X DELETE http://localhost:8000/api/documents/doc_abc123/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### JavaScript Example

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'My Invoice');
formData.append('source_channel', 'web');

const response = await fetch('/api/documents/upload/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
console.log('Document ID:', result.document.document_id);

// Update document
await fetch(`/api/documents/${documentId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Updated Title',
    force_review: true
  })
});

// Delete document
await fetch(`/api/documents/${documentId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## MongoDB Connection Issue

If you see this error:
```
[WinError 10061] No connection could be made because the target machine actively refused it
```

**Solution:**

1. **Start MongoDB**
   ```bash
   # Windows
   net start MongoDB
   
   # Or start MongoDB service from Services app
   # Or run: mongod --dbpath C:\data\db
   ```

2. **Check MongoDB is Running**
   ```bash
   mongo --eval "db.version()"
   ```

3. **Update .env File**
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=agentdoc
   ```

4. **Restart Django Server**
   ```bash
   python manage.py runserver
   ```

## Testing

### Test Valid Document
```bash
# Create a test PDF
echo "Test Invoice\nAmount: $100\nDate: 2024-03-18" > test.txt
# Convert to PDF or use existing PDF

# Upload
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf" \
  -F "title=Test Invoice" \
  -F "source_channel=web"
```

### Test Invalid Document
```bash
# Try uploading unsupported format
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.docx" \
  -F "title=Test Document" \
  -F "source_channel=web"

# Expected: 400 Bad Request - Unsupported file type
```

## Summary

- ✅ **Upload**: POST `/api/documents/upload/`
- ✅ **List**: GET `/api/documents/`
- ✅ **Get**: GET `/api/documents/{id}/`
- ✅ **Update**: PATCH `/api/documents/{id}/` (NEW!)
- ✅ **Delete**: DELETE `/api/documents/{id}/` (NEW!)

**Supported Formats:** PDF, JPEG, PNG, TXT
**Max Size:** ~10 MB recommended
**Document Types:** 8 types supported
**Status:** 5 states (processing, completed, pending_review, rejected, failed)
