-- create_user_and_tenant_tables
-- depends: 

BEGIN;

DROP INDEX IF EXISTS idx_active_subscription;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tenants;
DROP TABLE IF EXISTS tenants_versions;
DROP TABLE IF EXISTS tenants_subscriptions;

COMMIT;
