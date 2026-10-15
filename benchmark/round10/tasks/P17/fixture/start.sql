-- Database state after 0001 and 0002 were applied.
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT
);
INSERT INTO customers (id, full_name, email) VALUES (1, 'Ines Varga', 'ines@larkspur.test');
INSERT INTO customers (id, full_name, email) VALUES (2, 'Tomasz Elbe', NULL);
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
);
INSERT INTO schema_migrations VALUES ('0001', '0001_create_customers.sql',
    '0e90e4f7b68c570f5c11df728f3ded1562199d76df10de2be10945de941cae49', '2026-09-01T08:00:00+00:00');
INSERT INTO schema_migrations VALUES ('0002', '0002_add_email.sql',
    'f2eb7be4ea1c0dc6d7c64ed66ed6e6bc61bf18787f6db7571eb5afaef0fd565f', '2026-09-08T08:00:00+00:00');
