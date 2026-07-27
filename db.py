# -*- coding: utf-8 -*-
import sqlite3
import os
from flask import g

DATA_DIR = os.environ.get("APP_DATA_DIR", "/app/data")
DB_PATH = os.path.join(DATA_DIR, "depouillement.db")


def get_db():
    if "db" not in g:
        os.makedirs(DATA_DIR, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        with open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8") as f:
            conn.executescript(f.read())
    app.teardown_appcontext(close_db)
