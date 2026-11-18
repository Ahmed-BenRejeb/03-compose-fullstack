import os
import socket

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)

# "db" is the SERVICE NAME in docker-compose.yml – Docker's internal DNS resolves it
DB_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.getenv('DB_HOST', 'db')}:5432/{os.environ['POSTGRES_DB']}"
)


def query(sql, params=(), fetch=True):
    with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        if fetch:
            cols = [c.name for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


@app.get("/api/health")
def health():
    query("SELECT 1")
    return jsonify(status="ok", backend=socket.gethostname())


@app.get("/api/todos")
def list_todos():
    return jsonify(query("SELECT id, title, done FROM todos ORDER BY id"))


@app.post("/api/todos")
def add_todo():
    title = (request.json or {}).get("title", "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    row = query("INSERT INTO todos (title) VALUES (%s) RETURNING id, title, done", (title,))
    return jsonify(row[0]), 201


@app.patch("/api/todos/<int:todo_id>")
def toggle_todo(todo_id):
    row = query("UPDATE todos SET done = NOT done WHERE id = %s RETURNING id, title, done", (todo_id,))
    return (jsonify(row[0]), 200) if row else (jsonify(error="not found"), 404)


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id):
    query("DELETE FROM todos WHERE id = %s", (todo_id,), fetch=False)
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
