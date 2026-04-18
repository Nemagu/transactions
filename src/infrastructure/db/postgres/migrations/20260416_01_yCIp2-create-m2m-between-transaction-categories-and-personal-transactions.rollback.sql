-- create_m2m_between_transaction_categories_and_personal_transactions
-- depends: 20260415_01_eLJGT-create-transaction-category-and-personal-transaction-tables

BEGIN;

DELETE FROM transactions_tables WHERE name IN ('personal_transaction_categories', 'personal_transaction_categories_versions');

DROP TABLE IF EXISTS personal_transaction_categories;
DROP TABLE IF EXISTS personal_transaction_categories_versions;

COMMIT;
