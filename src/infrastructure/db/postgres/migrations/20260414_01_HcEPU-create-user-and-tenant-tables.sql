-- create_user_and_tenant_tables
-- depends: 

BEGIN;

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
    tenant_version_id UUID PRIMARY KEY DEFAULT uuid7(),
    tenant_id UUID NOT NULL REFERENCES tenants ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    state VARCHAR(30) NOT NULL,
    version INTEGER NOT NULL,
    editor UUID REFERENCES tenants ON DELETE SET NULL,
    created_at NOT NULL TIMESTAMP WITH TIME ZONE DEFAULT now()
);

COMMIT;
