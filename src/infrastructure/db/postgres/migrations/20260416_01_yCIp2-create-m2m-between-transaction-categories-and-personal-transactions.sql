-- create_m2m_between_transaction_categories_and_personal_transactions
-- depends: 20260415_01_eLJGT-create-transaction-category-and-personal-transaction-tables

BEGIN;

CREATE TABLE IF NOT EXISTS personal_transaction_categories (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    transaction_id UUID NOT NULL REFERENCES personal_transactions ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES transaction_categories ON DELETE CASCADE,

    UNIQUE(transaction_id, category_id)
);

CREATE TABLE IF NOT EXISTS personal_transaction_categories_versions (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    transaction_version_id UUID NOT NULL REFERENCES personal_transactions_versions ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES transaction_categories ON DELETE CASCADE,

    UNIQUE(transaction_version_id, category_id)
);

INSERT INTO transactions_tables (name)
VALUES ('personal_transaction_categories'), ('personal_transaction_categories_versions');

COMMIT;
