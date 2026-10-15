ALTER TABLE customers ADD COLUMN email TEXT;
UPDATE customers SET email = 'ines@larkspur.test' WHERE id = 1;
