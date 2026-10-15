CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    actor TEXT NOT NULL
);
INSERT INTO audit_log (id, actor) VALUES (1, 'system');
INSERT INTO customers (id, full_name, nickname) VALUES (3, 'Ada Morrow', 'ada');
