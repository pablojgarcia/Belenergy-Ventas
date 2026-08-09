-- Habilitar RLS en todas las tablas (bloquea acceso público por API REST)
-- El backend se conecta directo por DATABASE_URL (postgres role), bypassing RLS

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE taxes ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_statuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotation_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotation_draft_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE alembic_version ENABLE ROW LEVEL SECURITY;

-- Denegar todo acceso público (anon key) a todas las tablas
CREATE POLICY "deny_all" ON users AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON customers AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON contacts AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON taxes AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON products AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON refresh_tokens AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON orders AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON order_statuses AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON order_lines AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON quotation_drafts AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON quotation_draft_lines AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON quotations AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON leads AS PERMISSIVE FOR ALL TO public USING (false);
CREATE POLICY "deny_all" ON alembic_version AS PERMISSIVE FOR ALL TO public USING (false);
