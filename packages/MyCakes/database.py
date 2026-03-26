import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "mycakes.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS layers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    description  TEXT,
    category     TEXT DEFAULT 'inne',
    default_height_cm   REAL DEFAULT 2.0,
    default_diameter_cm REAL DEFAULT 24.0,
    prep_time_min INTEGER DEFAULT 0,
    bake_time_min INTEGER DEFAULT 0,
    photo_path   TEXT,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS layer_ingredients (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    layer_id  INTEGER NOT NULL REFERENCES layers(id) ON DELETE CASCADE,
    name      TEXT NOT NULL,
    amount    REAL NOT NULL,
    unit      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS layer_steps (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    layer_id  INTEGER NOT NULL REFERENCES layers(id) ON DELETE CASCADE,
    position  INTEGER NOT NULL DEFAULT 0,
    title     TEXT,
    description TEXT,
    time_min  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS frostings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    description  TEXT,
    type         TEXT DEFAULT 'masło',
    g_per_100cm2 REAL DEFAULT 50.0,
    prep_time_min INTEGER DEFAULT 0,
    photo_path   TEXT,
    created_at   TEXT DEFAULT (datetime('now')),
    updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS frosting_ingredients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    frosting_id  INTEGER NOT NULL REFERENCES frostings(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,
    amount       REAL NOT NULL,
    unit         TEXT NOT NULL,
    per_area_cm2 REAL DEFAULT 100.0
);

CREATE TABLE IF NOT EXISTS frosting_steps (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    frosting_id INTEGER NOT NULL REFERENCES frostings(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL DEFAULT 0,
    title       TEXT,
    description TEXT,
    time_min    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS decorations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    type        TEXT DEFAULT 'inne',
    description TEXT,
    unit        TEXT DEFAULT 'szt',
    photo_path  TEXT
);

CREATE TABLE IF NOT EXISTS cakes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    diameter_cm REAL NOT NULL DEFAULT 24.0,
    photo_path  TEXT,
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cake_layers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cake_id     INTEGER NOT NULL REFERENCES cakes(id) ON DELETE CASCADE,
    layer_id    INTEGER NOT NULL REFERENCES layers(id),
    position    INTEGER NOT NULL DEFAULT 0,
    height_cm   REAL,
    diameter_cm REAL
);

CREATE TABLE IF NOT EXISTS cake_frostings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cake_id     INTEGER NOT NULL REFERENCES cakes(id) ON DELETE CASCADE,
    frosting_id INTEGER NOT NULL REFERENCES frostings(id),
    apply_top   INTEGER DEFAULT 1,
    apply_sides INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cake_decorations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cake_id        INTEGER NOT NULL REFERENCES cakes(id) ON DELETE CASCADE,
    decoration_id  INTEGER NOT NULL REFERENCES decorations(id),
    quantity       REAL DEFAULT 1,
    note           TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,
    target_id   INTEGER NOT NULL,
    author      TEXT DEFAULT 'Anonim',
    text        TEXT,
    rating      INTEGER CHECK(rating BETWEEN 1 AND 5),
    created_at  TEXT DEFAULT (datetime('now'))
);
"""


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


MIGRATIONS = [
    "ALTER TABLE layer_steps    ADD COLUMN stage TEXT DEFAULT 'Dzień 1'",
    "ALTER TABLE frosting_steps ADD COLUMN stage TEXT DEFAULT 'Dzień 1'",
    "ALTER TABLE frostings      ADD COLUMN ref_diameter_cm REAL DEFAULT 24.0",
    "ALTER TABLE frostings      ADD COLUMN ref_height_cm   REAL DEFAULT 10.0",
    "ALTER TABLE cakes          ADD COLUMN serves INTEGER DEFAULT 0",
]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        for migration in MIGRATIONS:
            try:
                await db.execute(migration)
            except Exception:
                pass  # kolumna już istnieje
        await db.commit()
