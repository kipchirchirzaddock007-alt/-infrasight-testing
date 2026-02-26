import sqlite3
from contextlib import contextmanager
from typing import Optional

DB_PATH = "infrasight.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        # Leaders (for login, simple for now)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS leaders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                constituency TEXT NOT NULL
            );
            """
        )

        # Constituency profile + metrics
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS constituencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ambulances_count INTEGER DEFAULT 0,
                hospitals_count INTEGER DEFAULT 0,
                equality_index REAL,
                need_factor REAL,
                road_density REAL,
                electricity_coverage REAL,
                water_access REAL,
                health_per_10k REAL,
                schools_per_10k REAL,
                emergency_units_index REAL
            );
            """
        )

        # Emergency assets (ambulances, etc.)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS emergency_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                constituency_name TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                name TEXT,
                number_plate TEXT,
                attached_hospital TEXT,
                location TEXT
            );
            """
        )

        # Development projects
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                constituency_name TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT,
                budget REAL,
                implementer TEXT,
                timeline TEXT,
                verification_status TEXT,
                location TEXT,
                description TEXT
            );
            """
        )

        conn.commit()

    # ensure at least one leader exists when the module is imported
    seed_default_leader()


# ---------- LEADERS ----------

def ensure_leader(username: str, password: str, constituency: str):
    """Create a leader if not exists."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO leaders (username, password, constituency) VALUES (?, ?, ?)",
            (username, password, constituency),
        )
        conn.commit()


def authenticate_leader(username: str, password: str) -> Optional[dict]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, constituency FROM leaders WHERE username = ? AND password = ?",
            (username, password),
        )
        row = cur.fetchone()
    if row:
        return {"id": row[0], "username": row[1], "constituency": row[2]}
    return None


def seed_default_leader():
    # simple seed for testing version
    ensure_leader("leader_ainabkoi", "test123", "AINABKOI")


# ---------- CONSTITUENCY ----------

def upsert_constituency(
    name: str,
    ambulances_count: int,
    hospitals_count: int,
    equality_index: Optional[float],
    need_factor: Optional[float],
    road_density: Optional[float],
    electricity_coverage: Optional[float],
    water_access: Optional[float],
    health_per_10k: Optional[float],
    schools_per_10k: Optional[float],
    emergency_units_index: Optional[float],
):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO constituencies (
                name, ambulances_count, hospitals_count,
                equality_index, need_factor, road_density,
                electricity_coverage, water_access,
                health_per_10k, schools_per_10k, emergency_units_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                ambulances_count = excluded.ambulances_count,
                hospitals_count = excluded.hospitals_count,
                equality_index = excluded.equality_index,
                need_factor = excluded.need_factor,
                road_density = excluded.road_density,
                electricity_coverage = excluded.electricity_coverage,
                water_access = excluded.water_access,
                health_per_10k = excluded.health_per_10k,
                schools_per_10k = excluded.schools_per_10k,
                emergency_units_index = excluded.emergency_units_index;
            """,
            (
                name,
                ambulances_count,
                hospitals_count,
                equality_index,
                need_factor,
                road_density,
                electricity_coverage,
                water_access,
                health_per_10k,
                schools_per_10k,
                emergency_units_index,
            ),
        )
        conn.commit()


def get_constituency(name: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM constituencies WHERE name = ?",
            (name,),
        )
        return cur.fetchone()


# ---------- EMERGENCY ASSETS ----------

def add_ambulance(
    constituency_name: str,
    name: str,
    number_plate: str,
    attached_hospital: str,
    location: str,
):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO emergency_assets (
                constituency_name, asset_type, name, number_plate, attached_hospital, location
            )
            VALUES (?, 'ambulance', ?, ?, ?, ?)
            """,
            (constituency_name, name, number_plate, attached_hospital, location),
        )
        conn.commit()


def get_ambulances(constituency_name: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, number_plate, attached_hospital, location
            FROM emergency_assets
            WHERE constituency_name = ? AND asset_type = 'ambulance'
            """,
            (constituency_name,),
        )
        return cur.fetchall()


# ---------- PROJECTS ----------

def add_project(
    constituency_name: str,
    name: str,
    status: str,
    budget: float,
    implementer: str,
    timeline: str,
    verification_status: str,
    location: str,
    description: str,
):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO projects (
                constituency_name, name, status, budget,
                implementer, timeline, verification_status,
                location, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                constituency_name,
                name,
                status,
                budget,
                implementer,
                timeline,
                verification_status,
                location,
                description,
            ),
        )
        conn.commit()


def get_projects_by_constituency(constituency_name: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, status, budget, implementer, timeline,
                   verification_status, location, description
            FROM projects
            WHERE constituency_name = ?
            """,
            (constituency_name,),
        )
        return cur.fetchall()


if __name__ == "__main__":
    init_db()
    print(
        "infrasight.db ready with leader + constituency + emergency + projects tables."
    )
