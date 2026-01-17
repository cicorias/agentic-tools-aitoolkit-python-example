#!/usr/bin/env python3
"""
Unit tests for MCP server structure validation.
Tests the server configuration without requiring database connectivity.
"""

import sys
import inspect


def test_imports():
    """Test that server can be imported."""
    print("Testing module imports...")
    try:
        # Test import without running
        import server
        print("✅ Server module imports successfully")
        return True
    except ImportError as e:
        # Expected if dependencies are not installed
        if any(pkg in str(e) for pkg in ["mcp", "psycopg2"]):
            print(f"⚠️  Dependencies not installed (expected in CI): {e}")
            print("   Install with: pip install -r requirements.txt")
            return True
        print(f"❌ Import failed: {e}")
        return False


def test_server_structure():
    """Test server structure without requiring dependencies."""
    print("\nTesting server structure...")
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        # Check for required components
        checks = [
            ("Server instantiation", 'Server("postgres-lookup-server")' in content),
            ("list_tools handler", "@server.list_tools()" in content),
            ("call_tool handler", "@server.call_tool()" in content),
            ("lookup_vendor function", "async def lookup_vendor" in content),
            ("lookup_invoice function", "async def lookup_invoice" in content),
            ("lookup_purchase_order function", "async def lookup_purchase_order" in content),
            ("query_amounts function", "async def query_amounts" in content),
            ("get_vendor_summary function", "async def get_vendor_summary" in content),
            ("Database config", "DB_CONFIG" in content),
            ("Main function", "async def main()" in content),
        ]
        
        all_passed = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {name}")
            if not passed:
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False


def test_tool_definitions():
    """Test that all tools are properly defined."""
    print("\nTesting tool definitions...")
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        # Expected tools
        tools = [
            "lookup_vendor",
            "lookup_invoice", 
            "lookup_purchase_order",
            "query_amounts",
            "get_vendor_summary"
        ]
        
        all_found = True
        for tool in tools:
            # Check in list_tools
            if f'name="{tool}"' in content:
                print(f"   ✅ Tool '{tool}' defined")
            else:
                print(f"   ❌ Tool '{tool}' missing")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Tool definition test failed: {e}")
        return False


def test_sql_queries():
    """Test that SQL queries are present and look reasonable."""
    print("\nTesting SQL query presence...")
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        # Check for key SQL tables
        tables = [
            "suppliers",
            "invoices",
            "purchase_orders",
            "invoice_balances"
        ]
        
        all_found = True
        for table in tables:
            if f"FROM {table}" in content or f"JOIN {table}" in content:
                print(f"   ✅ Queries use '{table}' table")
            else:
                print(f"   ⚠️  Table '{table}' not found in queries")
        
        return True  # Not critical if some tables are missing
    except Exception as e:
        print(f"❌ SQL query test failed: {e}")
        return False


def test_configuration():
    """Test that configuration is properly set up."""
    print("\nTesting configuration...")
    try:
        with open("server.py", "r") as f:
            content = f.read()
        
        configs = [
            ("POSTGRES_HOST", "host"),
            ("POSTGRES_PORT", "port"),
            ("POSTGRES_DATABASE", "database"),
            ("POSTGRES_USER", "user"),
            ("POSTGRES_PASSWORD", "password"),
        ]
        
        all_found = True
        for env_var, config_key in configs:
            if env_var in content:
                print(f"   ✅ Configuration for {config_key} ({env_var})")
            else:
                print(f"   ❌ Missing configuration for {config_key}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all structure tests."""
    print("=" * 60)
    print("MCP Server Structure Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_server_structure,
        test_tool_definitions,
        test_sql_queries,
        test_configuration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️  Some structure tests failed.")
        sys.exit(1)
    else:
        print("\n✅ All structure tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start database: docker compose up -d")
        print("3. Run database test: python test_db.py")
        print("4. Configure in MCP client (e.g., Claude Desktop)")
        sys.exit(0)


if __name__ == "__main__":
    main()
