-- create_user_and_tenant_tables
-- depends: 

BEGIN;

CREATE TABLE IF NOT EXISTS transactions_tables (
    table_id UUID PRIMARY KEY DEFAULT uuidv7(),
    name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id UUID PRIMARY KEY,
    status VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tenants_versions (
    tenant_version_id UUID PRIMARY KEY DEFAULT uuidv7(),
    tenant_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL,
    event VARCHAR(30) NOT NULL,
    editor_id UUID REFERENCES tenants ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),

    UNIQUE(tenant_id, version)
);

CREATE TABLE IF NOT EXISTS tenants_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuidv7(),
    tenant_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    table_id UUID NOT NULL REFERENCES transactions_tables ON DELETE CASCADE,
    source_id UUID NOT NULL,
    status VARCHAR(30) NOT NULL,
    start_version INTEGER NOT NULL,
    last_processed_version INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_active_subscription
ON tenants_subscriptions (tenant_id, table_id, source_id)
WHERE status = 'active';

INSERT INTO transactions_tables (name)
VALUES ('users'), ('tenants'), ('tenants_versions'), ('tenants_subscriptions');

COMMIT;
