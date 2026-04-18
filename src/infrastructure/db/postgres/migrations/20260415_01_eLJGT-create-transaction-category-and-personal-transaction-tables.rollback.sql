-- create_transaction_category_and_personal_transaction_tables
-- depends: 20260414_01_HcEPU-create-user-and-tenant-tables

BEGIN;

DELETE
FROM transactions_tables
WHERE
    name IN ('transaction_categories', 'transaction_categories_versions', 'personal_transactions', 'personal_transactions_versions');

DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS transaction_categories_versions;
DROP TABLE IF EXISTS personal_transactions;
DROP TABLE IF EXISTS personal_transactions_versions;

COMMIT;
