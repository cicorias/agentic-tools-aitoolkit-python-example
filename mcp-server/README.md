# PostgreSQL Lookup MCP Server

This is an MCP (Model Context Protocol) server that provides tools to query invoice, purchase order, vendor, and payment data from the PostgreSQL database.

## Features

The server provides the following tools:

1. **lookup_vendor** - Look up vendor/supplier information by name or ID
2. **lookup_invoice** - Look up invoice information by invoice number(s)
3. **lookup_purchase_order** - Look up purchase order information by PO number(s)
4. **query_amounts** - Query financial information with filters (vendor, amount range, status)
5. **get_vendor_summary** - Get comprehensive summary for a vendor

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database running (via docker-compose in the repository)
- Access to the `invoices` database

## Setup

1. **Install dependencies:**

   ```bash
   cd mcp-server
   pip install -r requirements.txt
   ```

2. **Start the PostgreSQL database** (if not already running):

   ```bash
   cd ..
   docker-compose up -d
   ```

   Wait for the database to initialize completely. You can check the status with:

   ```bash
   docker-compose logs db
   ```

3. **Configure environment variables** (optional):

   The server uses the following environment variables. If not set, it defaults to the values from the docker-compose setup:

   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=15432
   export POSTGRES_DATABASE=invoices
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD='P@ssw0rd!'
   ```

## Running the Server

The MCP server runs via stdio (standard input/output) and is designed to be used by MCP clients like Claude Desktop or other MCP-compatible tools.

### Direct execution:

```bash
python server.py
```

### Configuration for Claude Desktop

Add this to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "postgres-lookup": {
      "command": "python",
      "args": ["/path/to/mcp-server/server.py"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "15432",
        "POSTGRES_DATABASE": "invoices",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "P@ssw0rd!"
      }
    }
  }
}
```

Replace `/path/to/mcp-server/server.py` with the absolute path to the server.py file.

## Usage Examples

Once connected to an MCP client, you can use natural language to query the database:

- "Look up vendor with ID 1"
- "Find vendor by name 'Tech Hardware'"
- "Get invoice details for INV-TH-2024-001"
- "Look up invoices INV-TH-2024-001 and INV-OS-2024-001"
- "Show me purchase order PO-2024-001"
- "Query invoices with status PAID"
- "Show invoices between $1000 and $20000"
- "Get summary for vendor ID 1"

## Database Schema

The server queries the following main tables:

- `suppliers` - Vendor/supplier information
- `invoices` - Invoice records with amounts and dates
- `purchase_orders` - Purchase order records
- `payments` - Payment records
- `payment_allocations` - Links between payments and invoices

Views:
- `invoice_balances` - Shows paid and outstanding amounts for invoices
- `supplier_open_balances` - Shows open balances by supplier

## Development

To modify or extend the server:

1. Edit `server.py` to add new tools or modify existing ones
2. Each tool follows the MCP protocol:
   - Define the tool in `handle_list_tools()`
   - Implement the handler function
   - Add the handler to `handle_call_tool()`

## Troubleshooting

**Connection refused:**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check the port mapping: `docker-compose port db 5432`

**Database not found:**
- Wait for initialization to complete: `docker-compose logs -f db`
- Look for "Database initialization complete!" message

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This is a sample implementation for demonstration purposes.
