# Plan: Add HTTP Transport with Entra ID Authentication

## Problem
Add HTTP/SSE transport to the MCP server with Entra ID (Azure AD) authentication, including:
1. HTTP endpoint alongside existing stdio transport
2. JWT Bearer token validation using Entra ID
3. Custom scopes: `Mcp.Read`, `Mcp.Update`
4. Azure CLI setup scripts for Entra ID app registration

## Current State
- `mcp-server/server.py` - MCP server using stdio transport only
- `mcp-server/pyproject.toml` - Dependencies: `mcp`, `psycopg2-binary`
- `scripts/init-db.sh` - Existing setup script

## Approach
- Add HTTP/SSE transport using `mcp.server.sse.SseServerTransport` + Starlette/uvicorn
- Add JWT validation middleware using `msal` + `azure-identity` for Entra ID token verification
- Create Azure CLI script to register Entra ID app with custom scopes
- Use environment variables for configuration (tenant ID, client ID, audience)

---

## Tasks

### Phase 1: Entra ID Setup Scripts

- [ ] **1.1 Create `scripts/entra-setup.sh`**
  - Register API app with `az ad app create`
  - Set Application ID URI (`api://<client-id>`)
  - Add custom scopes: `Mcp.Read`, `Mcp.Update`
  - Create service principal
  - Output client ID and tenant ID for configuration

- [ ] **1.2 Create `scripts/entra-client-setup.sh`** (optional)
  - Register client app for testing
  - Grant API permissions to the client app
  - Admin consent

- [ ] **1.3 Create `mcp-server/.env.example.http`**
  - Template for HTTP-specific environment variables

### Phase 2: HTTP Transport Implementation

- [ ] **2.1 Update `mcp-server/pyproject.toml`**
  - Add dependencies: `starlette`, `uvicorn`, `msal`, `azure-identity`

- [ ] **2.2 Create `mcp-server/auth.py`**
  - Use `msal` for token validation
  - Use `azure-identity` for credential handling
  - Token claims extraction (scope validation)
  - Helper: `require_scope("Mcp.Read")` decorator

- [ ] **2.3 Create `mcp-server/http_server.py`**
  - Starlette app with SSE endpoint
  - Auth middleware integration
  - Health check endpoint (unauthenticated)

- [ ] **2.4 Update `mcp-server/server.py`**
  - Add `--mode` CLI argument: `stdio` (default) or `http`
  - Add `--port` argument for HTTP mode
  - Refactor `main()` to support both transports

- [ ] **2.5 Update entry points in `pyproject.toml`**
  - `mcp-server` (stdio, default)
  - `mcp-server-http` (HTTP mode shortcut)

### Phase 3: Testing & Documentation

- [ ] **3.1 Create `scripts/test-entra-auth.sh`**
  - Get test token using client credentials flow
  - Call MCP HTTP endpoint with token

- [ ] **3.2 Update `.vscode/mcp.json`**
  - Add HTTP configuration example with auth

- [ ] **3.3 Update `mcp-server/README.md`**
  - Document HTTP mode usage
  - Document Entra ID setup steps

---

## File Structure (New/Modified)

```
mcp-server/
├── server.py          # Modified: add --mode, --port args
├── http_server.py     # NEW: Starlette app with SSE
├── auth.py            # NEW: JWT validation for Entra ID
├── pyproject.toml     # Modified: add dependencies
├── .env.example       # Modified: add HTTP/Entra vars
└── README.md          # Modified: document HTTP mode

scripts/
├── entra-setup.sh         # NEW: Create Entra ID API app
├── entra-client-setup.sh  # NEW: Create test client app
└── test-entra-auth.sh     # NEW: Test auth flow
```

---

## Entra ID App Registration Details

### API App (mcp-server)
```
Display Name: MCP Server API
Application ID URI: api://<client-id>
Scopes:
  - Mcp.Read  (User consent: "Read MCP data")
  - Mcp.Update (Admin consent: "Modify MCP data")
```

### Environment Variables
```bash
# Entra ID Configuration
ENTRA_TENANT_ID=<your-tenant-id>
ENTRA_CLIENT_ID=<api-app-client-id>
ENTRA_AUDIENCE=api://<api-app-client-id>

# HTTP Server
MCP_HTTP_PORT=8000
MCP_HTTP_HOST=0.0.0.0
```

---

## Example Usage

### Start in HTTP mode
```bash
uv run mcp-server --mode http --port 8000
```

### Azure CLI Setup
```bash
./scripts/entra-setup.sh --app-name "MCP Server API"
# Outputs: CLIENT_ID, TENANT_ID to configure in .env
```

### mcp.json for HTTP
```json
{
  "servers": {
    "postgres-lookup-http": {
      "type": "sse",
      "url": "http://localhost:8000/sse",
      "headers": {
        "Authorization": "Bearer ${MCP_AUTH_TOKEN}"
      }
    }
  }
}
```

---

## Notes
- Use `msal` for token acquisition and validation (official Microsoft library)
- Use `azure-identity` for DefaultAzureCredential support
- Token issuer: `https://login.microsoftonline.com/{tenant}/v2.0`
- Scopes in token appear as `scp` claim (delegated) or `roles` claim (application)
- MSAL handles JWKS caching and key rotation automatically
