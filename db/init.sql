-- Runs automatically the FIRST time the postgres volume is created
CREATE TABLE IF NOT EXISTS todos (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    done       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO todos (title) VALUES
    ('Install Docker'),
    ('Write my first Dockerfile'),
    ('Run a full stack with docker compose');
