#!/usr/bin/env python3
"""
Simple test script to verify database connectivity and basic queries.
This is not a full MCP test but validates the database functions work correctly.
"""

import os
import sys

# Set up environment variables for testing BEFORE any imports
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "15432")
os.environ.setdefault("POSTGRES_DATABASE", "invoices")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "P@ssw0rd!")


def test_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        conn = get_db_connection()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_vendor_lookup():
    """Test vendor lookup."""
    print("\nTesting vendor lookup...")
    try:
        query = "SELECT COUNT(*) as count FROM suppliers"
        result = query_db(query)
        count = result[0]['count']
        print(f"✅ Found {count} vendors in database")
        
        # Get one vendor
        query = "SELECT supplier_id, name FROM suppliers LIMIT 1"
        vendors = query_db(query)
        if vendors:
            print(f"   Sample vendor: {vendors[0]['name']} (ID: {vendors[0]['supplier_id']})")
        return True
    except Exception as e:
        print(f"❌ Vendor lookup failed: {e}")
        return False


def test_invoice_lookup():
    """Test invoice lookup."""
    print("\nTesting invoice lookup...")
    try:
        query = "SELECT COUNT(*) as count FROM invoices"
        result = query_db(query)
        count = result[0]['count']
        print(f"✅ Found {count} invoices in database")
        
        # Get one invoice
        query = """
            SELECT i.invoice_number, i.total_amount, i.currency_code, s.name as supplier_name
            FROM invoices i
            JOIN suppliers s ON i.supplier_id = s.supplier_id
            LIMIT 1
        """
        invoices = query_db(query)
        if invoices:
            inv = invoices[0]
            print(f"   Sample invoice: {inv['invoice_number']} - {inv['currency_code']} {inv['total_amount']} ({inv['supplier_name']})")
        return True
    except Exception as e:
        print(f"❌ Invoice lookup failed: {e}")
        return False


def test_po_lookup():
    """Test purchase order lookup."""
    print("\nTesting purchase order lookup...")
    try:
        query = "SELECT COUNT(*) as count FROM purchase_orders"
        result = query_db(query)
        count = result[0]['count']
        print(f"✅ Found {count} purchase orders in database")
        
        # Get one PO
        query = """
            SELECT po.po_number, po.total_amount, po.currency_code, s.name as supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.supplier_id
            LIMIT 1
        """
        pos = query_db(query)
        if pos:
            po = pos[0]
            print(f"   Sample PO: {po['po_number']} - {po['currency_code']} {po['total_amount']} ({po['supplier_name']})")
        return True
    except Exception as e:
        print(f"❌ Purchase order lookup failed: {e}")
        return False


def test_views():
    """Test database views."""
    print("\nTesting database views...")
    try:
        query = "SELECT COUNT(*) as count FROM invoice_balances"
        result = query_db(query)
        count = result[0]['count']
        print(f"✅ invoice_balances view has {count} records")
        
        query = "SELECT COUNT(*) as count FROM supplier_open_balances"
        result = query_db(query)
        count = result[0]['count']
        print(f"✅ supplier_open_balances view has {count} records")
        return True
    except Exception as e:
        print(f"❌ View query failed: {e}")
        return False


def main():
    """Run all tests."""
    # Import server module after environment variables are set
    from server import get_db_connection, query_db
    
    # Make functions available globally for test functions
    globals()['get_db_connection'] = get_db_connection
    globals()['query_db'] = query_db
    
    print("=" * 60)
    print("MCP Server Database Connectivity Test")
    print("=" * 60)
    
    tests = [
        test_connection,
        test_vendor_lookup,
        test_invoice_lookup,
        test_po_lookup,
        test_views,
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
        print("\n⚠️  Some tests failed. Please check:")
        print("   1. PostgreSQL is running (docker-compose up -d)")
        print("   2. Database initialization is complete")
        print("   3. Connection parameters are correct")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! MCP server is ready to use.")
        sys.exit(0)


if __name__ == "__main__":
    main()
