-- create_m2m_between_transaction_categories_and_personal_transactions
-- depends: 20260415_01_eLJGT-create-transaction-category-and-personal-transaction-tables

BEGIN;

CREATE TABLE IF NOT EXISTS personal_transaction_categories (
    id UUID PRIMARY KEY DEFAULT uuid7(),
    transaction_id UUID NOT NULL REFERENCES personal_tansactions ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES transaction_categories ON DELETE CASCADE,

    UNIQUE(transaction_id, category_id)
);

COMMIT;
