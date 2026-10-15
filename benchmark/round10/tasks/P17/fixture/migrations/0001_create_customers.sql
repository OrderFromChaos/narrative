-- customers of the Larkspur Garden Supply shop
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL
);
INSERT INTO customers (id, full_name) VALUES (1, 'Ines Varga');
INSERT INTO customers (id, full_name) VALUES (2, 'Tomasz Elbe');
