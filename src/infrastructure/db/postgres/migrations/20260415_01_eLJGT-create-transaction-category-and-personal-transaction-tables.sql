-- create_transaction_category_and_personal_transaction_tables
-- depends: 20260414_01_HcEPU-create-user-and-tenant-tables

BEGIN;

CREATE TABLE IF NOT EXISTS transaction_categories (
    category_id UUID PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL,

    UNIQUE (owner_id, name)
);

CREATE TABLE IF NOT EXISTS transaction_categories_versions (
    category_version_id UUID PRIMARY KEY DEFAULT uuidv7(),
    category_id UUID NOT NULL REFERENCES transaction_categories ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL,
    event VARCHAR(30) NOT NULL,
    editor_id UUID REFERENCES tenants ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),

    UNIQUE (category_id, version)
);

CREATE TABLE IF NOT EXISTS personal_transactions (
    transaction_id UUID PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    name VARCHAR(100),
    description TEXT,
    transaction_type VARCHAR(30) NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    currency VARCHAR(30) NOT NULL,
    transaction_time TIMESTAMP WITH TIME ZONE NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS personal_transactions_versions (
    transaction_version_id UUID PRIMARY KEY DEFAULT uuidv7(),
    transaction_id UUID NOT NULL REFERENCES personal_transactions ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    name VARCHAR(100),
    description TEXT,
    transaction_type VARCHAR(30) NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    currency VARCHAR(30) NOT NULL,
    transaction_time TIMESTAMP WITH TIME ZONE NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL,
    event VARCHAR(30) NOT NULL,
    editor_id UUID REFERENCES tenants ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

    UNIQUE (transaction_id, version)
);

INSERT INTO transactions_tables (name)
VALUES ('transaction_categories'), ('transaction_categories_versions'), ('personal_transactions'), ('personal_transactions_versions');

COMMIT;
