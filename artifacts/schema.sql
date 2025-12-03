-- Suppliers master
CREATE TABLE suppliers (
    supplier_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name                 TEXT        NOT NULL,
    contact_email        TEXT        UNIQUE,
    phone                TEXT,
    billing_address      JSONB,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Purchase orders
CREATE TABLE purchase_orders (
    po_id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id          BIGINT      NOT NULL REFERENCES suppliers(supplier_id),
    po_number            TEXT        NOT NULL UNIQUE,
    order_date           DATE        NOT NULL,
    currency_code        CHAR(3)     NOT NULL DEFAULT 'USD',
    status               TEXT        NOT NULL CHECK (status IN ('DRAFT','SUBMITTED','APPROVED','RECEIVED','CANCELLED')),
    total_amount         NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE purchase_order_lines (
    po_line_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    po_id                BIGINT      NOT NULL REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    line_number          INTEGER     NOT NULL,
    description          TEXT        NOT NULL,
    quantity_ordered     NUMERIC(12,2) NOT NULL CHECK (quantity_ordered > 0),
    unit_price           NUMERIC(12,4) NOT NULL CHECK (unit_price >= 0),
    expected_receipt_date DATE,
    UNIQUE (po_id, line_number)
);

-- Invoices received from suppliers
CREATE TABLE invoices (
    invoice_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id          BIGINT      NOT NULL REFERENCES suppliers(supplier_id),
    po_id                BIGINT      REFERENCES purchase_orders(po_id),
    invoice_number       TEXT        NOT NULL,
    invoice_date         DATE        NOT NULL,
    due_date             DATE        NOT NULL,
    currency_code        CHAR(3)     NOT NULL DEFAULT 'USD',
    status               TEXT        NOT NULL CHECK (status IN ('DRAFT','VALIDATED','APPROVED','PAID','VOID')),
    subtotal_amount      NUMERIC(12,2) NOT NULL DEFAULT 0,
    tax_amount           NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_amount         NUMERIC(12,2) NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (supplier_id, invoice_number)
);

CREATE TABLE invoice_lines (
    invoice_line_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id           BIGINT      NOT NULL REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    po_line_id           BIGINT      REFERENCES purchase_order_lines(po_line_id),
    line_number          INTEGER     NOT NULL,
    description          TEXT        NOT NULL,
    quantity_invoiced    NUMERIC(12,2) NOT NULL CHECK (quantity_invoiced > 0),
    unit_price           NUMERIC(12,4) NOT NULL CHECK (unit_price >= 0),
    tax_rate             NUMERIC(5,4)  NOT NULL DEFAULT 0 CHECK (tax_rate >= 0),
    line_total           NUMERIC(12,2) NOT NULL,
    UNIQUE (invoice_id, line_number)
);

-- Payments to suppliers
CREATE TABLE payments (
    payment_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supplier_id          BIGINT      NOT NULL REFERENCES suppliers(supplier_id),
    payment_reference    TEXT        NOT NULL UNIQUE,
    payment_date         DATE        NOT NULL,
    currency_code        CHAR(3)     NOT NULL DEFAULT 'USD',
    payment_method       TEXT        NOT NULL CHECK (payment_method IN ('ACH','WIRE','CHECK','CARD')),
    amount_paid          NUMERIC(12,2) NOT NULL CHECK (amount_paid > 0),
    status               TEXT        NOT NULL CHECK (status IN ('INITIATED','SETTLED','VOID')),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Allocation of payments to invoices
CREATE TABLE payment_allocations (
    payment_allocation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_id            BIGINT     NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
    invoice_id            BIGINT     NOT NULL REFERENCES invoices(invoice_id),
    allocated_amount      NUMERIC(12,2) NOT NULL CHECK (allocated_amount > 0),
    applied_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (payment_id, invoice_id)
);

-- Helpful views
CREATE VIEW invoice_balances AS
SELECT
    i.invoice_id,
    i.total_amount,
    COALESCE(SUM(pa.allocated_amount), 0) AS amount_paid,
    i.total_amount - COALESCE(SUM(pa.allocated_amount), 0) AS balance_due
FROM invoices i
LEFT JOIN payment_allocations pa ON pa.invoice_id = i.invoice_id
GROUP BY i.invoice_id;

CREATE VIEW supplier_open_balances AS
SELECT
    s.supplier_id,
    s.name,
    SUM(v.balance_due) AS open_balance
FROM suppliers s
JOIN invoice_balances v ON v.invoice_id IN (
    SELECT invoice_id FROM invoices WHERE supplier_id = s.supplier_id AND status <> 'PAID'
)
GROUP BY s.supplier_id, s.name;