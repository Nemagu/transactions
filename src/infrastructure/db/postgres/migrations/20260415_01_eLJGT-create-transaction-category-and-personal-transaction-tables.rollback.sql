-- create_transaction_category_and_personal_transaction_tables
-- depends: 20260414_01_HcEPU-create-user-and-tenant-tables

BEGIN;

DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS transaction_categories_versions;
DROP TABLE IF EXISTS personal_transactions;
DROP TABLE IF EXISTS personal_transactions_versions;

COMMIT;
