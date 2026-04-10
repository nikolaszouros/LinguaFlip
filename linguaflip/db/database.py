import psycopg
from psycopg.rows import dict_row
import os
from flask import g


def _database_url():
    return os.environ.get('DATABASE_URL', 'postgresql://localhost/linguaflip')


class _DBWrapper:
    """
    Wraps a psycopg connection so models can call db.execute() / db.commit()
    exactly as they did with sqlite3 — no changes needed at call sites except
    using %s placeholders instead of ?.
    """

    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, params=None):
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def executescript(self, sql):
        """Run multiple semicolon-separated DDL statements (used by init_db)."""
        cur = self._conn.cursor()
        for stmt in (s.strip() for s in sql.split(';')):
            if stmt:
                cur.execute(stmt)


def get_db():
    """Return the per-request DB wrapper, creating the connection if needed."""
    if 'db' not in g:
        conn = psycopg.connect(_database_url(), row_factory=dict_row)
        g.db = _DBWrapper(conn)
    return g.db


def close_db(e=None):
    """Close the connection at the end of each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Run schema.sql to create tables if they don't already exist."""
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        sql = f.read()
    db.executescript(sql)
    db.commit()
