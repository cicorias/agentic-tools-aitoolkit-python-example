# Agentic Tools AI Toolkit Python Example

This repository demonstrates agentic AI workflows using the Azure AI Toolkit and includes a Model Context Protocol (MCP) server for database lookups.

## Repository Structure

```
.
├── agents/                  # AI agent implementations
│   ├── crud/agent2/        # Writer-Reviewer workflow agent
│   └── my-ai-agent/        # Sample AI agent
├── data/                    # Database schema and sample data
│   ├── schema.sql          # PostgreSQL database schema
│   └── sample_data.sql     # Sample invoice/PO data
├── mcp-server/             # MCP server for SQL lookups (NEW)
│   ├── server.py           # Main MCP server implementation
│   ├── README.md           # Setup and configuration guide
│   ├── USAGE.md            # Detailed usage examples
│   ├── QUICKREF.md         # Quick reference guide
│   └── test_*.py           # Test scripts
├── scripts/                # Database initialization scripts
│   └── init-db.sh          # PostgreSQL initialization script
└── compose.yml             # Docker Compose configuration
```

## Components

### 1. PostgreSQL Database

The repository includes a PostgreSQL database with a complete accounts payable schema including:
- Suppliers/Vendors
- Purchase Orders
- Invoices
- Payments and Payment Allocations

**To start the database:**

```bash
docker compose up -d
```

The database will be available on port `15432` with the database name `invoices`.

### 2. AI Agents

Sample agent implementations using Azure AI Agent Framework:
- **Writer-Reviewer Agent**: Demonstrates multi-agent workflow for content creation and review
- Located in `agents/` directory
- Requires Microsoft Foundry Project and model deployment

### 3. MCP Server for SQL Lookups (NEW)

A Python-based MCP server that provides tools to query the PostgreSQL database. This server enables AI assistants to look up invoice, purchase order, vendor, and payment information.

**Features:**
- 5 specialized lookup tools for different data queries
- Support for single and batch lookups (e.g., multiple invoice numbers)
- Parameterized queries for security
- Financial summaries and aggregations
- Environment-based configuration

**Quick Start:**

```bash
# Install dependencies
cd mcp-server
pip install -r requirements.txt

# Start the database (if not already running)
cd ..
docker compose up -d

# Test the server
cd mcp-server
python test_structure.py  # Validate server structure
python test_db.py         # Test database connectivity
```

**Documentation:**
- [Setup Guide](mcp-server/README.md) - Installation and configuration
- [Usage Examples](mcp-server/USAGE.md) - Detailed usage examples and workflows
- [Quick Reference](mcp-server/QUICKREF.md) - Quick reference card

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- (Optional) Microsoft Foundry Project for AI agents

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/cicorias/agentic-tools-aitoolkit-python-example.git
   cd agentic-tools-aitoolkit-python-example
   ```

2. **Start the PostgreSQL database**

   ```bash
   docker compose up -d
   ```

   Wait for initialization to complete (check with `docker compose logs -f db`)

3. **Set up the MCP server**

   ```bash
   cd mcp-server
   pip install -r requirements.txt
   python test_db.py  # Verify database connectivity
   ```

4. **Configure in your MCP client** (e.g., Claude Desktop)

   See [mcp-server/README.md](mcp-server/README.md) for detailed configuration instructions.

## Database Schema

The PostgreSQL database includes the following tables:

- **suppliers** - Vendor/supplier master data
- **purchase_orders** - Purchase order headers
- **purchase_order_lines** - PO line items
- **invoices** - Invoice headers
- **invoice_lines** - Invoice line items
- **payments** - Payment records
- **payment_allocations** - Links payments to invoices

Plus helpful views:
- **invoice_balances** - Shows paid amounts and outstanding balances
- **supplier_open_balances** - Aggregated open balances by supplier

## Sample Data

The database is pre-populated with sample data including:
- 5 suppliers
- 6 purchase orders
- 5 invoices (various statuses)
- 2 payments

This sample data is perfect for testing and demonstrating the MCP server capabilities.

## Use Cases

### MCP Server Use Cases

1. **Invoice Lookup**: Quickly retrieve invoice details by number
2. **Vendor Research**: Get vendor contact information and financial summaries
3. **Financial Queries**: Find invoices by amount, status, or vendor
4. **Purchase Order Tracking**: Check PO status and details
5. **Payment Reconciliation**: Review payment allocations and balances

### AI Agent Use Cases

1. **Content Creation**: Writer-Reviewer workflow for content generation
2. **Workflow Automation**: Multi-agent orchestration examples
3. **Azure AI Integration**: Examples of Microsoft Foundry integration

## MCP Server Tools

| Tool | Description |
|------|-------------|
| `lookup_vendor` | Look up vendor information by ID or name |
| `lookup_invoice` | Get invoice details (supports batch lookup) |
| `lookup_purchase_order` | Get PO details (supports batch lookup) |
| `query_amounts` | Query invoices by amount, status, or vendor |
| `get_vendor_summary` | Get comprehensive vendor financial summary |

## Configuration

### Database Configuration

Default database connection settings (can be overridden with environment variables):

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=15432
POSTGRES_DATABASE=invoices
POSTGRES_USER=postgres
POSTGRES_PASSWORD=P@ssw0rd!
```

### MCP Server Configuration

See [mcp-server/.env.example](mcp-server/.env.example) for environment variable template.

## Security

- All SQL queries use parameterized statements to prevent SQL injection
- CodeQL security scanning: 0 alerts
- Environment variables for sensitive configuration
- `.env` files are git-ignored

## Testing

### MCP Server Tests

```bash
cd mcp-server

# Structure validation (works without dependencies)
python test_structure.py

# Database connectivity test (requires running database)
python test_db.py
```

### Database Tests

```bash
# Connect to the database
docker exec -it postgresql psql -U postgres -d invoices

# Run sample queries
SELECT * FROM suppliers;
SELECT * FROM invoices;
SELECT * FROM invoice_balances;
```

## Contributing

This is an example repository demonstrating agentic AI workflows and MCP server implementation.

## License

See repository license file for details.

## Additional Resources

- [Microsoft Foundry Documentation](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)
- [Model Context Protocol (MCP) Specification](https://modelcontextprotocol.io/)
- [Azure AI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)
