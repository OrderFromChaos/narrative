CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    total_cents INTEGER NOT NULL,
    updated_at TEXT
);
CREATE INDEX orders_by_customer ON orders (customer_id);
CREATE TRIGGER orders_touch AFTER UPDATE OF total_cents ON orders
BEGIN
    UPDATE orders SET updated_at = 'changed' WHERE id = NEW.id;
END;
INSERT INTO orders (id, customer_id, total_cents) VALUES (1, 1, 4250);
UPDATE orders SET total_cents = 4300 WHERE id = 1;
