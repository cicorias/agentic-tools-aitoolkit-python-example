-- Sample Data for Accounts Payable System
-- Insert order respects foreign key constraints

-- ============================================
-- 1. Insert Suppliers (no dependencies)
-- ============================================
INSERT INTO suppliers (name, contact_email, phone, billing_address, created_at, updated_at) VALUES
('Tech Hardware Inc', 'ap@techhardware.com', '+1-555-0100', '{"street": "123 Tech Blvd", "city": "San Jose", "state": "CA", "zip": "95110", "country": "USA"}'::jsonb, NOW(), NOW()),
('Office Supplies Pro', 'billing@officesupplies.com', '+1-555-0200', '{"street": "456 Commerce Ave", "city": "Chicago", "state": "IL", "zip": "60601", "country": "USA"}'::jsonb, NOW(), NOW()),
('Cloud Services Ltd', 'invoicing@cloudservices.io', '+1-555-0300', '{"street": "789 Innovation Dr", "city": "Seattle", "state": "WA", "zip": "98101", "country": "USA"}'::jsonb, NOW(), NOW()),
('Global Logistics', 'accounts@globallogistics.com', '+44-20-5550400', '{"street": "10 Business Park", "city": "London", "postcode": "EC1A 1BB", "country": "UK"}'::jsonb, NOW(), NOW()),
('Software Licensing Corp', 'payments@softwarelicensing.com', '+1-555-0500', '{"street": "321 Silicon Way", "city": "Austin", "state": "TX", "zip": "78701", "country": "USA"}'::jsonb, NOW(), NOW());

-- ============================================
-- 2. Insert Purchase Orders (depends on suppliers)
-- ============================================
INSERT INTO purchase_orders (supplier_id, po_number, order_date, currency_code, status, total_amount, created_at, updated_at) VALUES
(1, 'PO-2024-001', '2024-01-10', 'USD', 'RECEIVED', 15000.00, NOW(), NOW()),
(2, 'PO-2024-002', '2024-01-15', 'USD', 'RECEIVED', 3500.00, NOW(), NOW()),
(3, 'PO-2024-003', '2024-02-01', 'USD', 'APPROVED', 25000.00, NOW(), NOW()),
(1, 'PO-2024-004', '2024-02-15', 'USD', 'SUBMITTED', 8500.00, NOW(), NOW()),
(4, 'PO-2024-005', '2024-03-01', 'GBP', 'RECEIVED', 12000.00, NOW(), NOW()),
(5, 'PO-2024-006', '2024-03-10', 'USD', 'APPROVED', 50000.00, NOW(), NOW());

-- ============================================
-- 3. Insert Purchase Order Lines (depends on purchase_orders)
-- ============================================
-- PO-2024-001 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(1, 1, 'Dell Latitude Laptops', 10, 1200.00, '2024-02-01'),
(1, 2, 'USB-C Docking Stations', 10, 300.00, '2024-02-01');

-- PO-2024-002 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(2, 1, 'Office Chairs - Ergonomic', 20, 150.00, '2024-02-10'),
(2, 2, 'Standing Desks', 5, 200.00, '2024-02-10');

-- PO-2024-003 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(3, 1, 'Cloud Infrastructure - Annual', 1, 25000.00, '2024-02-15');

-- PO-2024-004 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(4, 1, 'Network Switches', 5, 1500.00, '2024-03-15'),
(4, 2, 'CAT6 Cables - 100 pack', 10, 100.00, '2024-03-15');

-- PO-2024-005 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(5, 1, 'International Shipping Services', 1, 12000.00, '2024-03-31');

-- PO-2024-006 lines
INSERT INTO purchase_order_lines (po_id, line_number, description, quantity_ordered, unit_price, expected_receipt_date) VALUES
(6, 1, 'Enterprise Software Licenses', 100, 500.00, '2024-04-01');

-- ============================================
-- 4. Insert Invoices (depends on suppliers, optionally on purchase_orders)
-- ============================================
INSERT INTO invoices (supplier_id, po_id, invoice_number, invoice_date, due_date, currency_code, status, subtotal_amount, tax_amount, total_amount, created_at, updated_at) VALUES
(1, 1, 'INV-TH-2024-001', '2024-02-05', '2024-03-07', 'USD', 'PAID', 15000.00, 1350.00, 16350.00, NOW(), NOW()),
(2, 2, 'INV-OS-2024-001', '2024-02-12', '2024-03-14', 'USD', 'APPROVED', 3500.00, 315.00, 3815.00, NOW(), NOW()),
(3, 3, 'INV-CS-2024-001', '2024-02-20', '2024-03-22', 'USD', 'VALIDATED', 25000.00, 0.00, 25000.00, NOW(), NOW()),
(4, 5, 'INV-GL-2024-001', '2024-03-05', '2024-04-04', 'GBP', 'PAID', 12000.00, 2400.00, 14400.00, NOW(), NOW()),
(1, NULL, 'INV-TH-2024-002', '2024-03-15', '2024-04-14', 'USD', 'DRAFT', 2500.00, 225.00, 2725.00, NOW(), NOW());

-- ============================================
-- 5. Insert Invoice Lines (depends on invoices, optionally on po_lines)
-- ============================================
-- Invoice 1 lines (matched to PO)
INSERT INTO invoice_lines (invoice_id, po_line_id, line_number, description, quantity_invoiced, unit_price, tax_rate, line_total) VALUES
(1, 1, 1, 'Dell Latitude Laptops', 10, 1200.00, 0.09, 13080.00),
(1, 2, 2, 'USB-C Docking Stations', 10, 300.00, 0.09, 3270.00);

-- Invoice 2 lines (matched to PO)
INSERT INTO invoice_lines (invoice_id, po_line_id, line_number, description, quantity_invoiced, unit_price, tax_rate, line_total) VALUES
(2, 3, 1, 'Office Chairs - Ergonomic', 20, 150.00, 0.09, 3270.00),
(2, 4, 2, 'Standing Desks', 5, 200.00, 0.09, 1090.00);

-- Invoice 3 lines (matched to PO)
INSERT INTO invoice_lines (invoice_id, po_line_id, line_number, description, quantity_invoiced, unit_price, tax_rate, line_total) VALUES
(3, 5, 1, 'Cloud Infrastructure - Annual', 1, 25000.00, 0.00, 25000.00);

-- Invoice 4 lines (matched to PO)
INSERT INTO invoice_lines (invoice_id, po_line_id, line_number, description, quantity_invoiced, unit_price, tax_rate, line_total) VALUES
(4, 9, 1, 'International Shipping Services', 1, 12000.00, 0.20, 14400.00);

-- Invoice 5 lines (no PO match - direct invoice)
INSERT INTO invoice_lines (invoice_id, po_line_id, line_number, description, quantity_invoiced, unit_price, tax_rate, line_total) VALUES
(5, NULL, 1, 'Emergency Hardware Repair', 1, 2500.00, 0.09, 2725.00);

-- ============================================
-- 6. Insert Payments (depends on suppliers)
-- ============================================
INSERT INTO payments (supplier_id, payment_reference, payment_date, currency_code, payment_method, amount_paid, status, created_at) VALUES
(1, 'PAY-2024-001', '2024-03-01', 'USD', 'ACH', 16350.00, 'SETTLED', NOW()),
(4, 'PAY-2024-002', '2024-03-25', 'GBP', 'WIRE', 14400.00, 'SETTLED', NOW());

-- ============================================
-- 7. Insert Payment Allocations (depends on payments and invoices)
-- ============================================
INSERT INTO payment_allocations (payment_id, invoice_id, allocated_amount, applied_at) VALUES
(1, 1, 16350.00, NOW()),
(2, 4, 14400.00, NOW());

-- ============================================
-- Summary Statistics
-- ============================================
-- 5 suppliers
-- 6 purchase orders
-- 11 purchase order lines
-- 5 invoices (2 paid, 1 approved, 1 validated, 1 draft)
-- 8 invoice lines
-- 2 payments
-- 2 payment allocations
