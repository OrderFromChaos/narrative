CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO settings (key, value) VALUES ('banner', 'Welcome; please sign in');
INSERT INTO settings (key, value) VALUES ('footer', 'Open 9-17; closed Sundays');
