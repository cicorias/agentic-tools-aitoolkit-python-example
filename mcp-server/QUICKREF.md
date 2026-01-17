# MCP Server Quick Reference

## Available Tools

| Tool | Purpose | Required Parameters | Optional Parameters |
|------|---------|-------------------|-------------------|
| `lookup_vendor` | Find vendor info | - | `vendor_id`, `name` |
| `lookup_invoice` | Get invoice details | `invoice_numbers` (array) | - |
| `lookup_purchase_order` | Get PO details | `po_numbers` (array) | - |
| `query_amounts` | Query financial data | - | `vendor_id`, `min_amount`, `max_amount`, `status` |
| `get_vendor_summary` | Vendor financial summary | `vendor_id` | - |

## Quick Examples

### Vendors
```
"Look up vendor with ID 1"
"Find vendor by name Tech Hardware"
```

### Invoices
```
"Get invoice INV-TH-2024-001"
"Look up invoices INV-TH-2024-001 and INV-OS-2024-001"
```

### Purchase Orders
```
"Show purchase order PO-2024-001"
"Look up POs PO-2024-001, PO-2024-002, and PO-2024-003"
```

### Financial Queries
```
"Show all paid invoices"
"Find invoices over $10000"
"Show invoices for vendor ID 1"
"Find invoices between $5000 and $20000 with status APPROVED"
```

### Summaries
```
"Get summary for vendor ID 1"
```

## Invoice Statuses
- `DRAFT` - Not yet validated
- `VALIDATED` - Validated but not approved
- `APPROVED` - Approved for payment
- `PAID` - Payment completed
- `VOID` - Cancelled/voided

## PO Statuses
- `DRAFT` - Being created
- `SUBMITTED` - Submitted for approval
- `APPROVED` - Approved but not received
- `RECEIVED` - Goods/services received
- `CANCELLED` - Cancelled

## Sample Data Quick Reference

**Vendor IDs:**
1. Tech Hardware Inc
2. Office Supplies Pro
3. Cloud Services Ltd
4. Global Logistics
5. Software Licensing Corp

**Sample Invoices:**
- INV-TH-2024-001 (Paid, $16,350)
- INV-OS-2024-001 (Approved, $3,815)
- INV-CS-2024-001 (Validated, $25,000)
- INV-GL-2024-001 (Paid, £14,400)
- INV-TH-2024-002 (Draft, $2,725)

**Sample POs:**
- PO-2024-001 (Received, $15,000)
- PO-2024-002 (Received, $3,500)
- PO-2024-003 (Approved, $25,000)
- PO-2024-004 (Submitted, $8,500)
- PO-2024-005 (Received, £12,000)
- PO-2024-006 (Approved, $50,000)
