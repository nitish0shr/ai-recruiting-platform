DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'uuid-ossp') THEN
    EXECUTE 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"';
  END IF;
END$$;
