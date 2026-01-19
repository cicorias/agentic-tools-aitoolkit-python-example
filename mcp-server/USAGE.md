# MCP Server Usage Examples

This document provides practical examples of using the PostgreSQL Lookup MCP Server.

## Prerequisites

1. PostgreSQL database is running with sample data
2. MCP server is configured in your MCP client (e.g., Claude Desktop)
3. Dependencies are installed

## Tool Descriptions

### 1. lookup_vendor

Look up vendor/supplier information by name or ID.

**Use Cases:**
- Find vendor contact information
- Verify vendor details before creating a purchase order
- Look up billing address for payment processing

**Examples:**

```
"Look up vendor with ID 1"
"Find vendor by name Tech Hardware"
"Show me all vendors"
```

**Response Format:**
```
Vendor Information:

ID: 1
Name: Tech Hardware Inc
Email: ap@techhardware.com
Phone: +1-555-0100
Billing Address: {"street": "123 Tech Blvd", "city": "San Jose", ...}
--------------------------------------------------
```

### 2. lookup_invoice

Look up invoice information by invoice number(s). Supports single or multiple invoices.

**Use Cases:**
- Check invoice status and amounts
- Verify invoice details for approval
- Look up multiple invoices for batch processing
- Find invoice payment due dates

**Examples:**

```
"Get invoice details for INV-TH-2024-001"
"Look up invoices INV-TH-2024-001, INV-OS-2024-001, and INV-CS-2024-001"
"Show me invoice INV-GL-2024-001"
```

**Response Format:**
```
Invoice Information:

Invoice Number: INV-TH-2024-001
Supplier: Tech Hardware Inc (ID: 1)
PO Number: PO-2024-001
Invoice Date: 2024-02-05
Due Date: 2024-03-07
Status: PAID
Subtotal: USD 15000.00
Tax: USD 1350.00
Total Amount: USD 16350.00
--------------------------------------------------
```

### 3. lookup_purchase_order

Look up purchase order information by PO number(s). Supports single or multiple POs.

**Use Cases:**
- Check PO status before creating an invoice
- Verify PO amounts and details
- Track PO approval workflow
- Look up multiple POs for reporting

**Examples:**

```
"Show me purchase order PO-2024-001"
"Look up PO-2024-003 and PO-2024-004"
"Get details for purchase order PO-2024-006"
```

**Response Format:**
```
Purchase Order Information:

PO Number: PO-2024-001
Supplier: Tech Hardware Inc (ID: 1)
Order Date: 2024-01-10
Status: RECEIVED
Total Amount: USD 15000.00
--------------------------------------------------
```

### 4. query_amounts

Query financial information with flexible filtering options.

**Use Cases:**
- Find all invoices over a certain amount
- Check invoices by status (PAID, APPROVED, DRAFT)
- Audit vendor spending
- Find invoices within a specific amount range
- Generate financial reports

**Examples:**

```
"Show me all paid invoices"
"Find invoices with amounts between $5000 and $20000"
"Show invoices for vendor ID 1"
"Get all approved invoices"
"Find invoices over $10000"
"Show draft invoices under $5000"
```

**Response Format:**
```
Financial Query Results:

Invoice: INV-TH-2024-001
Supplier: Tech Hardware Inc
Date: 2024-02-05
Total: USD 16350.00
Paid: USD 16350.00
Balance Due: USD 0.00
Status: PAID
--------------------------------------------------
[more invoices...]

Total (USD only): $45890.00
```

**Filter Parameters:**
- `vendor_id` - Filter by specific vendor
- `min_amount` - Minimum invoice amount
- `max_amount` - Maximum invoice amount
- `status` - Filter by status (PAID, APPROVED, VALIDATED, DRAFT, VOID)

### 5. get_vendor_summary

Get comprehensive summary for a vendor including invoice and PO totals.

**Use Cases:**
- Review vendor relationship at a glance
- Check total spending with a vendor
- Verify outstanding balances
- Prepare for vendor negotiations
- Audit vendor activity

**Examples:**

```
"Get summary for vendor ID 1"
"Show me vendor summary for vendor 3"
"What's the summary for vendor ID 5?"
```

**Response Format:**
```
Vendor Summary for: Tech Hardware Inc
ID: 1
Email: ap@techhardware.com
Phone: +1-555-0100
==================================================

Invoice Summary:
  Currency: USD
  Total Invoices: 2
  Total Invoiced: USD 19075.00
  Total Paid: USD 16350.00
  Outstanding: USD 2725.00

Purchase Order Summary:
  Currency: USD
  Total POs: 2
  Total Amount: USD 23500.00
```

## Common Workflow Examples

### Workflow 1: Process New Invoice

1. Look up the vendor: `"Find vendor by name Tech Hardware"`
2. Verify the PO: `"Show me purchase order PO-2024-004"`
3. Check invoice details: `"Get invoice details for INV-TH-2024-002"`

### Workflow 2: Month-End Review

1. Check all paid invoices: `"Show me all paid invoices"`
2. Review pending approvals: `"Show me all approved invoices"`
3. Get vendor summaries: `"Get summary for vendor ID 1"`

### Workflow 3: Vendor Analysis

1. Get vendor summary: `"Get summary for vendor ID 3"`
2. Check all invoices: `"Show invoices for vendor ID 3"`
3. Review POs: `"Query amounts for vendor ID 3"`

### Workflow 4: Audit Trail

1. Look up specific invoices: `"Look up invoices INV-TH-2024-001 and INV-TH-2024-002"`
2. Check amounts: `"Find invoices over $15000"`
3. Verify payments: `"Show me all paid invoices"`

## Sample Data Reference

The database includes the following sample data:

### Vendors
1. Tech Hardware Inc
2. Office Supplies Pro
3. Cloud Services Ltd
4. Global Logistics
5. Software Licensing Corp

### Invoice Numbers
- INV-TH-2024-001 (Tech Hardware, PAID)
- INV-OS-2024-001 (Office Supplies, APPROVED)
- INV-CS-2024-001 (Cloud Services, VALIDATED)
- INV-GL-2024-001 (Global Logistics, PAID)
- INV-TH-2024-002 (Tech Hardware, DRAFT)

### Purchase Order Numbers
- PO-2024-001 (Tech Hardware, RECEIVED)
- PO-2024-002 (Office Supplies, RECEIVED)
- PO-2024-003 (Cloud Services, APPROVED)
- PO-2024-004 (Tech Hardware, SUBMITTED)
- PO-2024-005 (Global Logistics, RECEIVED)
- PO-2024-006 (Software Licensing, APPROVED)

## Tips for Best Results

1. **Be specific with invoice/PO numbers**: Use exact numbers from the database
2. **Use lists for multiple lookups**: "Look up invoices A, B, and C"
3. **Combine filters for precise results**: "Show paid invoices for vendor ID 1 over $10000"
4. **Start with vendor summaries**: Get an overview before diving into details
5. **Check both POs and invoices**: Some invoices may not be linked to POs

## Troubleshooting

**"No vendors found"**
- Check the vendor ID or name spelling
- Try partial name matching: "Tech" instead of "Tech Hardware Inc"

**"No invoices found"**
- Verify the invoice number format (e.g., INV-TH-2024-001)
- Check if the invoice exists in the database

**"No purchase orders found"**
- Verify the PO number format (e.g., PO-2024-001)
- Check if the PO exists in the database

**Empty results for amount queries**
- Adjust your filter criteria
- Remove some filters to broaden the search
- Check the currency (queries work best with USD)
