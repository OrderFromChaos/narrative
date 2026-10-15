-- Database state after 0001 to 0004 were applied on another machine; 0004_drop_legacy.sql has
-- since been deleted from the migrations directory.
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT
);
INSERT INTO customers (id, full_name, email) VALUES (1, 'Ines Varga', 'ines@larkspur.test');
INSERT INTO customers (id, full_name, email) VALUES (2, 'Tomasz Elbe', NULL);
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO settings (key, value) VALUES ('banner', 'Welcome; please sign in');
INSERT INTO settings (key, value) VALUES ('footer', 'Open 9-17; closed Sundays');
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
INSERT INTO schema_migrations VALUES ('0003', '0003_settings.sql',
    'aec9339fa1cba9ecc23d4a62b7e32ae4dbe4aa3cba40ad0dba9646e8a1dc23a4', '2026-09-15T08:00:00+00:00');
INSERT INTO schema_migrations VALUES ('0004', '0004_drop_legacy.sql',
    '3b1f0c9e2d7a4b8c6e5f1a0d9c8b7a6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a', '2026-09-22T08:00:00+00:00');
