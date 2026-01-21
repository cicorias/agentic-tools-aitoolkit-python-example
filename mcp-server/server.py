#!/usr/bin/env python3
"""
MCP Server for SQL Data Lookups
Provides tools to query invoice, purchase order, vendor, and payment data from PostgreSQL.
"""

import os
import asyncio
from typing import Any
import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Database connection parameters from environment variables
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "15432")),
    "database": os.getenv("POSTGRES_DATABASE", "invoices"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "P@ssw0rd!"),
}


def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def query_db(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Execute a query and return results as a list of dictionaries."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]


def build_in_clause_query(base_query: str, values: list) -> tuple[str, tuple]:
    """
    Build a SQL query with IN clause from a base query and list of values.
    
    Args:
        base_query: SQL query template with {placeholders} marker
        values: List of values to include in the IN clause
        
    Returns:
        Tuple of (formatted_query, values_tuple)
    """
    placeholders = ",".join(["%s"] * len(values))
    query = base_query.format(placeholders=placeholders)
    return query, tuple(values)


# Create MCP server instance
server = Server("postgres-lookup-server")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for querying the database."""
    return [
        Tool(
            name="lookup_vendor",
            description="Look up vendor/supplier information by name or ID. Returns vendor details including contact info and billing address.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "integer",
                        "description": "The vendor's ID number",
                    },
                    "name": {
                        "type": "string",
                        "description": "Search for vendor by name (partial match supported)",
                    },
                },
            },
        ),
        Tool(
            name="lookup_invoice",
            description="Look up invoice information by invoice number(s). Can handle single invoice or list of invoice numbers. Returns invoice details including amounts, dates, and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_numbers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of invoice numbers to look up",
                    },
                },
                "required": ["invoice_numbers"],
            },
        ),
        Tool(
            name="lookup_purchase_order",
            description="Look up purchase order information by PO number(s). Can handle single PO or list of PO numbers. Returns PO details including amounts, dates, and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "po_numbers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of purchase order numbers to look up",
                    },
                },
                "required": ["po_numbers"],
            },
        ),
        Tool(
            name="query_amounts",
            description="Query financial information including invoice amounts, payment amounts, and balances. Supports filtering by vendor, date range, and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "integer",
                        "description": "Filter by vendor ID",
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum amount to filter",
                    },
                    "max_amount": {
                        "type": "number",
                        "description": "Maximum amount to filter",
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status (e.g., PAID, APPROVED, DRAFT)",
                    },
                },
            },
        ),
        Tool(
            name="get_vendor_summary",
            description="Get summary information for a vendor including total invoices, total amounts, and payment status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "integer",
                        "description": "The vendor's ID number",
                    },
                },
                "required": ["vendor_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls for database lookups."""
    if arguments is None:
        arguments = {}

    try:
        if name == "lookup_vendor":
            return await lookup_vendor(arguments)
        elif name == "lookup_invoice":
            return await lookup_invoice(arguments)
        elif name == "lookup_purchase_order":
            return await lookup_purchase_order(arguments)
        elif name == "query_amounts":
            return await query_amounts(arguments)
        elif name == "get_vendor_summary":
            return await get_vendor_summary(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def lookup_vendor(args: dict) -> list[TextContent]:
    """Look up vendor information."""
    vendor_id = args.get("vendor_id")
    name = args.get("name")

    if vendor_id:
        query = """
            SELECT supplier_id, name, contact_email, phone, 
                   billing_address, created_at, updated_at
            FROM suppliers
            WHERE supplier_id = %s
        """
        results = query_db(query, (vendor_id,))
    elif name:
        query = """
            SELECT supplier_id, name, contact_email, phone, 
                   billing_address, created_at, updated_at
            FROM suppliers
            WHERE name ILIKE %s
        """
        results = query_db(query, (f"%{name}%",))
    else:
        # Return all vendors if no filter provided
        query = """
            SELECT supplier_id, name, contact_email, phone, 
                   billing_address, created_at, updated_at
            FROM suppliers
            ORDER BY name
        """
        results = query_db(query)

    if not results:
        return [TextContent(type="text", text="No vendors found.")]

    # Format results
    output = "Vendor Information:\n\n"
    for vendor in results:
        output += f"ID: {vendor['supplier_id']}\n"
        output += f"Name: {vendor['name']}\n"
        output += f"Email: {vendor['contact_email']}\n"
        output += f"Phone: {vendor['phone']}\n"
        output += f"Billing Address: {vendor['billing_address']}\n"
        output += "-" * 50 + "\n"

    return [TextContent(type="text", text=output)]


async def lookup_invoice(args: dict) -> list[TextContent]:
    """Look up invoice information by invoice number(s)."""
    invoice_numbers = args.get("invoice_numbers", [])

    if not invoice_numbers:
        return [TextContent(type="text", text="No invoice numbers provided.")]

    base_query = """
        SELECT i.invoice_id, i.invoice_number, i.invoice_date, i.due_date,
               i.currency_code, i.status, i.subtotal_amount, i.tax_amount, 
               i.total_amount, s.name as supplier_name, s.supplier_id,
               po.po_number
        FROM invoices i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        LEFT JOIN purchase_orders po ON i.po_id = po.po_id
        WHERE i.invoice_number IN ({placeholders})
        ORDER BY i.invoice_date DESC
    """
    query, params = build_in_clause_query(base_query, invoice_numbers)
    results = query_db(query, params)

    if not results:
        return [TextContent(type="text", text="No invoices found.")]

    # Format results
    output = "Invoice Information:\n\n"
    for inv in results:
        output += f"Invoice Number: {inv['invoice_number']}\n"
        output += f"Supplier: {inv['supplier_name']} (ID: {inv['supplier_id']})\n"
        output += f"PO Number: {inv['po_number'] or 'N/A'}\n"
        output += f"Invoice Date: {inv['invoice_date']}\n"
        output += f"Due Date: {inv['due_date']}\n"
        output += f"Status: {inv['status']}\n"
        output += f"Subtotal: {inv['currency_code']} {inv['subtotal_amount']}\n"
        output += f"Tax: {inv['currency_code']} {inv['tax_amount']}\n"
        output += f"Total Amount: {inv['currency_code']} {inv['total_amount']}\n"
        output += "-" * 50 + "\n"

    return [TextContent(type="text", text=output)]


async def lookup_purchase_order(args: dict) -> list[TextContent]:
    """Look up purchase order information by PO number(s)."""
    po_numbers = args.get("po_numbers", [])

    if not po_numbers:
        return [TextContent(type="text", text="No purchase order numbers provided.")]

    base_query = """
        SELECT po.po_id, po.po_number, po.order_date, po.currency_code,
               po.status, po.total_amount, s.name as supplier_name, s.supplier_id
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        WHERE po.po_number IN ({placeholders})
        ORDER BY po.order_date DESC
    """
    query, params = build_in_clause_query(base_query, po_numbers)
    results = query_db(query, params)

    if not results:
        return [TextContent(type="text", text="No purchase orders found.")]

    # Format results
    output = "Purchase Order Information:\n\n"
    for po in results:
        output += f"PO Number: {po['po_number']}\n"
        output += f"Supplier: {po['supplier_name']} (ID: {po['supplier_id']})\n"
        output += f"Order Date: {po['order_date']}\n"
        output += f"Status: {po['status']}\n"
        output += f"Total Amount: {po['currency_code']} {po['total_amount']}\n"
        output += "-" * 50 + "\n"

    return [TextContent(type="text", text=output)]


async def query_amounts(args: dict) -> list[TextContent]:
    """Query financial information with filters."""
    vendor_id = args.get("vendor_id")
    min_amount = args.get("min_amount")
    max_amount = args.get("max_amount")
    status = args.get("status")

    conditions = []
    params = []

    if vendor_id:
        conditions.append("i.supplier_id = %s")
        params.append(vendor_id)
    if min_amount is not None:
        conditions.append("i.total_amount >= %s")
        params.append(min_amount)
    if max_amount is not None:
        conditions.append("i.total_amount <= %s")
        params.append(max_amount)
    if status:
        conditions.append("i.status = %s")
        params.append(status)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT i.invoice_number, i.invoice_date, i.total_amount, 
               i.currency_code, i.status, s.name as supplier_name,
               ib.amount_paid, ib.balance_due
        FROM invoices i
        JOIN suppliers s ON i.supplier_id = s.supplier_id
        LEFT JOIN invoice_balances ib ON i.invoice_id = ib.invoice_id
        WHERE {where_clause}
        ORDER BY i.invoice_date DESC
    """
    results = query_db(query, tuple(params))

    if not results:
        return [TextContent(type="text", text="No invoices found matching criteria.")]

    # Format results
    output = "Financial Query Results:\n\n"
    total = 0
    for inv in results:
        output += f"Invoice: {inv['invoice_number']}\n"
        output += f"Supplier: {inv['supplier_name']}\n"
        output += f"Date: {inv['invoice_date']}\n"
        output += f"Total: {inv['currency_code']} {inv['total_amount']}\n"
        output += f"Paid: {inv['currency_code']} {inv['amount_paid'] or 0}\n"
        output += f"Balance Due: {inv['currency_code']} {inv['balance_due'] or inv['total_amount']}\n"
        output += f"Status: {inv['status']}\n"
        output += "-" * 50 + "\n"
        if inv['currency_code'] == 'USD':
            total += float(inv['total_amount'])

    output += f"\nTotal (USD only): ${total:.2f}\n"
    return [TextContent(type="text", text=output)]


async def get_vendor_summary(args: dict) -> list[TextContent]:
    """Get summary information for a vendor."""
    vendor_id = args.get("vendor_id")

    if not vendor_id:
        return [TextContent(type="text", text="Vendor ID is required.")]

    # Get vendor info
    vendor_query = """
        SELECT supplier_id, name, contact_email, phone
        FROM suppliers
        WHERE supplier_id = %s
    """
    vendor_results = query_db(vendor_query, (vendor_id,))

    if not vendor_results:
        return [TextContent(type="text", text="Vendor not found.")]

    vendor = vendor_results[0]

    # Get invoice summary
    invoice_query = """
        SELECT 
            COUNT(*) as invoice_count,
            SUM(total_amount) as total_invoiced,
            SUM(CASE WHEN status = 'PAID' THEN total_amount ELSE 0 END) as total_paid,
            currency_code
        FROM invoices
        WHERE supplier_id = %s
        GROUP BY currency_code
    """
    invoice_stats = query_db(invoice_query, (vendor_id,))

    # Get PO summary
    po_query = """
        SELECT 
            COUNT(*) as po_count,
            SUM(total_amount) as total_po_amount,
            currency_code
        FROM purchase_orders
        WHERE supplier_id = %s
        GROUP BY currency_code
    """
    po_stats = query_db(po_query, (vendor_id,))

    # Format results
    output = f"Vendor Summary for: {vendor['name']}\n"
    output += f"ID: {vendor['supplier_id']}\n"
    output += f"Email: {vendor['contact_email']}\n"
    output += f"Phone: {vendor['phone']}\n"
    output += "=" * 50 + "\n\n"

    output += "Invoice Summary:\n"
    if invoice_stats:
        for stat in invoice_stats:
            output += f"  Currency: {stat['currency_code']}\n"
            output += f"  Total Invoices: {stat['invoice_count']}\n"
            output += f"  Total Invoiced: {stat['currency_code']} {stat['total_invoiced']}\n"
            output += f"  Total Paid: {stat['currency_code']} {stat['total_paid']}\n"
            output += f"  Outstanding: {stat['currency_code']} {float(stat['total_invoiced']) - float(stat['total_paid'])}\n"
    else:
        output += "  No invoices found.\n"

    output += "\nPurchase Order Summary:\n"
    if po_stats:
        for stat in po_stats:
            output += f"  Currency: {stat['currency_code']}\n"
            output += f"  Total POs: {stat['po_count']}\n"
            output += f"  Total Amount: {stat['currency_code']} {stat['total_po_amount']}\n"
    else:
        output += "  No purchase orders found.\n"

    return [TextContent(type="text", text=output)]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="postgres-lookup-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main_cli():
    """Entry point for the mcp-server script."""
    asyncio.run(main())


if __name__ == "__main__":
    main_cli()
