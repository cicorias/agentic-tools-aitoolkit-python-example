# Adding MCP Prompts Interface to PostgreSQL Lookup Server

This document provides the implementation plan and suggested prompts for adding the `prompts/list` and `prompts/get` MCP interface commands to the existing PostgreSQL Lookup MCP Server.

## Overview

The MCP Prompts capability allows servers to expose reusable, parameterized message templates that clients can discover and invoke. This enhances user experience by providing structured starting points for common database lookup workflows.

## Current Server Capabilities

The existing server provides 5 tools:
1. **lookup_vendor** - Find vendor/supplier information by name or ID
2. **lookup_invoice** - Get invoice details by invoice number(s)
3. **lookup_purchase_order** - Get PO details by PO number(s)
4. **query_amounts** - Query financial data with filters
5. **get_vendor_summary** - Get comprehensive vendor financial summary

---

## Suggested Prompts

Based on the server's capabilities and common accounts payable workflows, here are the recommended prompts:

### 1. `vendor_lookup`
**Purpose:** Quick vendor search by name or ID  
**Arguments:**
- `search_term` (required): Vendor name (partial match) or ID number

**Template:**
```
Search for vendor information matching '{search_term}'. Show contact details, billing address, and supplier ID.
```

---

### 2. `invoice_status_check`
**Purpose:** Check status and details of specific invoices  
**Arguments:**
- `invoice_numbers` (required): Comma-separated list of invoice numbers

**Template:**
```
Look up the following invoices and show their current status, amounts, and payment details: {invoice_numbers}
```

---

### 3. `purchase_order_review`
**Purpose:** Review purchase order details  
**Arguments:**
- `po_numbers` (required): Comma-separated list of PO numbers

**Template:**
```
Retrieve and display details for these purchase orders: {po_numbers}. Include supplier info, amounts, and current status.
```

---

### 4. `vendor_spend_analysis`
**Purpose:** Analyze spending with a specific vendor  
**Arguments:**
- `vendor_id` (required): Vendor ID number

**Template:**
```
Provide a comprehensive spending analysis for vendor ID {vendor_id}. Include:
- Total invoiced amount
- Total paid amount
- Outstanding balance
- Number of invoices and purchase orders
- Recent transactions
```

---

### 5. `outstanding_invoices`
**Purpose:** Find invoices pending payment  
**Arguments:**
- `status` (optional, default: "APPROVED"): Invoice status filter
- `min_amount` (optional): Minimum amount threshold

**Template:**
```
List all {status} invoices{min_amount_clause} that are awaiting payment. Show supplier name, invoice number, amount, and due date.
```

---

### 6. `high_value_transactions`
**Purpose:** Identify high-value invoices for approval workflow  
**Arguments:**
- `threshold` (required): Minimum amount in USD

**Template:**
```
Find all invoices with total amount greater than ${threshold}. Include supplier information, PO reference, and current status.
```

---

### 7. `month_end_summary`
**Purpose:** Generate month-end accounts payable summary  
**Arguments:**
- `vendor_id` (optional): Filter to specific vendor

**Template:**
```
Generate a month-end summary{vendor_clause}:
1. Show all PAID invoices
2. Show all APPROVED invoices pending payment
3. Calculate total amounts by status
4. Highlight any overdue items
```

---

### 8. `three_way_match_check`
**Purpose:** Verify invoice-PO-vendor matching  
**Arguments:**
- `invoice_number` (required): Invoice number to verify

**Template:**
```
Perform a three-way match verification for invoice {invoice_number}:
1. Look up the invoice details
2. Retrieve the associated purchase order
3. Get the vendor information
4. Compare amounts and verify the supplier matches across all documents
```

---

## Implementation Plan

### Phase 1: Add Prompt Types and Decorators

**Task 1.1:** Import required types in `server.py`
```python
from mcp.types import (
    Tool, TextContent,
    Prompt, PromptArgument, PromptMessage, GetPromptResult
)
```

**Task 1.2:** Add `prompts` capability to server initialization
```python
capabilities=server.get_capabilities(
    notification_options=NotificationOptions(),
    experimental_capabilities={},
),
```
Note: The MCP SDK should auto-register prompts capability when handlers are defined.

---

### Phase 2: Implement `list_prompts` Handler

**Task 2.1:** Define the `@server.list_prompts()` handler

```python
@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """List available prompts for common database lookup workflows."""
    return [
        Prompt(
            name="vendor_lookup",
            title="Vendor Lookup",
            description="Search for vendor information by name or ID",
            arguments=[
                PromptArgument(
                    name="search_term",
                    description="Vendor name (partial match supported) or vendor ID",
                    required=True
                )
            ]
        ),
        Prompt(
            name="invoice_status_check",
            title="Invoice Status Check",
            description="Check status and details of specific invoices",
            arguments=[
                PromptArgument(
                    name="invoice_numbers",
                    description="Comma-separated list of invoice numbers (e.g., INV-TH-2024-001, INV-OS-2024-001)",
                    required=True
                )
            ]
        ),
        Prompt(
            name="purchase_order_review",
            title="Purchase Order Review",
            description="Review purchase order details and status",
            arguments=[
                PromptArgument(
                    name="po_numbers",
                    description="Comma-separated list of PO numbers (e.g., PO-2024-001, PO-2024-002)",
                    required=True
                )
            ]
        ),
        Prompt(
            name="vendor_spend_analysis",
            title="Vendor Spend Analysis",
            description="Comprehensive spending analysis for a specific vendor",
            arguments=[
                PromptArgument(
                    name="vendor_id",
                    description="Vendor/Supplier ID number",
                    required=True
                )
            ]
        ),
        Prompt(
            name="outstanding_invoices",
            title="Outstanding Invoices",
            description="Find invoices pending payment with optional filters",
            arguments=[
                PromptArgument(
                    name="status",
                    description="Invoice status filter (APPROVED, VALIDATED, DRAFT). Default: APPROVED",
                    required=False
                ),
                PromptArgument(
                    name="min_amount",
                    description="Minimum invoice amount threshold",
                    required=False
                )
            ]
        ),
        Prompt(
            name="high_value_transactions",
            title="High-Value Transactions",
            description="Find invoices above a specified amount threshold",
            arguments=[
                PromptArgument(
                    name="threshold",
                    description="Minimum amount in USD (e.g., 10000)",
                    required=True
                )
            ]
        ),
        Prompt(
            name="month_end_summary",
            title="Month-End Summary",
            description="Generate accounts payable summary for month-end review",
            arguments=[
                PromptArgument(
                    name="vendor_id",
                    description="Optional: Filter to specific vendor ID",
                    required=False
                )
            ]
        ),
        Prompt(
            name="three_way_match_check",
            title="Three-Way Match Verification",
            description="Verify invoice-PO-vendor matching for an invoice",
            arguments=[
                PromptArgument(
                    name="invoice_number",
                    description="Invoice number to verify (e.g., INV-TH-2024-001)",
                    required=True
                )
            ]
        ),
    ]
```

---

### Phase 3: Implement `get_prompt` Handler

**Task 3.1:** Define the `@server.get_prompt()` handler

```python
@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
    """Get a specific prompt with filled-in arguments."""
    if arguments is None:
        arguments = {}

    if name == "vendor_lookup":
        search_term = arguments.get("search_term", "")
        return GetPromptResult(
            description="Search for vendor information",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Search for vendor information matching '{search_term}'. "
                             f"Show contact details, billing address, and supplier ID."
                    )
                )
            ]
        )

    elif name == "invoice_status_check":
        invoice_numbers = arguments.get("invoice_numbers", "")
        return GetPromptResult(
            description="Check invoice status and details",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Look up the following invoices and show their current status, "
                             f"amounts, and payment details: {invoice_numbers}"
                    )
                )
            ]
        )

    elif name == "purchase_order_review":
        po_numbers = arguments.get("po_numbers", "")
        return GetPromptResult(
            description="Review purchase order details",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Retrieve and display details for these purchase orders: {po_numbers}. "
                             f"Include supplier info, amounts, and current status."
                    )
                )
            ]
        )

    elif name == "vendor_spend_analysis":
        vendor_id = arguments.get("vendor_id", "")
        return GetPromptResult(
            description="Vendor spending analysis",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Provide a comprehensive spending analysis for vendor ID {vendor_id}. Include:\n"
                             f"- Total invoiced amount\n"
                             f"- Total paid amount\n"
                             f"- Outstanding balance\n"
                             f"- Number of invoices and purchase orders\n"
                             f"- Recent transactions"
                    )
                )
            ]
        )

    elif name == "outstanding_invoices":
        status = arguments.get("status", "APPROVED")
        min_amount = arguments.get("min_amount")
        min_amount_clause = f" with amounts over ${min_amount}" if min_amount else ""
        return GetPromptResult(
            description="Find outstanding invoices",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"List all {status} invoices{min_amount_clause} that are awaiting payment. "
                             f"Show supplier name, invoice number, amount, and due date."
                    )
                )
            ]
        )

    elif name == "high_value_transactions":
        threshold = arguments.get("threshold", "10000")
        return GetPromptResult(
            description="Find high-value invoices",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Find all invoices with total amount greater than ${threshold}. "
                             f"Include supplier information, PO reference, and current status."
                    )
                )
            ]
        )

    elif name == "month_end_summary":
        vendor_id = arguments.get("vendor_id")
        vendor_clause = f" for vendor ID {vendor_id}" if vendor_id else ""
        return GetPromptResult(
            description="Month-end AP summary",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Generate a month-end accounts payable summary{vendor_clause}:\n"
                             f"1. Show all PAID invoices\n"
                             f"2. Show all APPROVED invoices pending payment\n"
                             f"3. Calculate total amounts by status\n"
                             f"4. Highlight any overdue items"
                    )
                )
            ]
        )

    elif name == "three_way_match_check":
        invoice_number = arguments.get("invoice_number", "")
        return GetPromptResult(
            description="Three-way match verification",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Perform a three-way match verification for invoice {invoice_number}:\n"
                             f"1. Look up the invoice details\n"
                             f"2. Retrieve the associated purchase order\n"
                             f"3. Get the vendor information\n"
                             f"4. Compare amounts and verify the supplier matches across all documents"
                    )
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")
```

---

### Phase 4: Testing

**Task 4.1:** Create test file `test_prompts.py`
```python
"""Tests for MCP prompts functionality."""

import pytest
import asyncio
from server import server, handle_list_prompts, handle_get_prompt


class TestListPrompts:
    """Tests for list_prompts handler."""

    @pytest.mark.asyncio
    async def test_list_prompts_returns_all_prompts(self):
        """Verify all expected prompts are returned."""
        prompts = await handle_list_prompts()
        prompt_names = [p.name for p in prompts]
        
        expected = [
            "vendor_lookup",
            "invoice_status_check",
            "purchase_order_review",
            "vendor_spend_analysis",
            "outstanding_invoices",
            "high_value_transactions",
            "month_end_summary",
            "three_way_match_check",
        ]
        assert set(prompt_names) == set(expected)

    @pytest.mark.asyncio
    async def test_all_prompts_have_descriptions(self):
        """Verify all prompts have descriptions."""
        prompts = await handle_list_prompts()
        for prompt in prompts:
            assert prompt.description is not None
            assert len(prompt.description) > 0


class TestGetPrompt:
    """Tests for get_prompt handler."""

    @pytest.mark.asyncio
    async def test_vendor_lookup_prompt(self):
        """Test vendor_lookup prompt generation."""
        result = await handle_get_prompt(
            "vendor_lookup",
            {"search_term": "Tech Hardware"}
        )
        assert "Tech Hardware" in result.messages[0].content.text
        assert len(result.messages) == 1
        assert result.messages[0].role == "user"

    @pytest.mark.asyncio
    async def test_unknown_prompt_raises_error(self):
        """Test that unknown prompt name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await handle_get_prompt("nonexistent_prompt", {})
```

**Task 4.2:** Run tests
```bash
cd mcp-server
pytest test_prompts.py -v
```

---

### Phase 5: Documentation Updates

**Task 5.1:** Update `README.md` to include Prompts section

**Task 5.2:** Update `USAGE.md` with prompt usage examples

**Task 5.3:** Update `QUICKREF.md` with prompts quick reference table

---

## Checklist

- [ ] Import required types (`Prompt`, `PromptArgument`, `PromptMessage`, `GetPromptResult`)
- [ ] Implement `@server.list_prompts()` handler with 8 prompts
- [ ] Implement `@server.get_prompt()` handler with message generation
- [ ] Add error handling for unknown prompt names
- [ ] Create `test_prompts.py` with unit tests
- [ ] Run tests and verify all pass
- [ ] Update `README.md` documentation
- [ ] Update `USAGE.md` with prompt examples
- [ ] Update `QUICKREF.md` reference table
- [ ] Test end-to-end with MCP client (e.g., Claude Desktop)

---

## Expected Client Behavior

Once implemented, MCP clients will be able to:

1. **Discover prompts** via `prompts/list` - see all 8 available prompts with descriptions
2. **Use prompts** via `prompts/get` - get structured messages to send to the LLM
3. **Provide arguments** - customize prompts with specific invoice numbers, vendor IDs, etc.

### Example Client Interaction

```
User: /vendor_lookup Tech Hardware
→ Client calls prompts/get with name="vendor_lookup", arguments={"search_term": "Tech Hardware"}
→ Server returns PromptMessage: "Search for vendor information matching 'Tech Hardware'..."
→ Client sends message to LLM
→ LLM uses lookup_vendor tool to retrieve results
```

---

## References

- [MCP Prompts Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
