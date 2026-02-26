import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple

DB_PATH = "infrasight.db"

# Ensure media directory exists
MEDIA_ROOT = os.path.join("data", "media")
os.makedirs(MEDIA_ROOT, exist_ok=True)


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

        # Leaders
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

        # Emergency assets
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

        # Development projects (now with lat/lon)
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
                description TEXT,
                lat REAL,
                lon REAL
            );
            """
        )

        # Citizen media/evidence linked to projects
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS project_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                media_type TEXT NOT NULL, -- 'image' or 'video'
                file_path TEXT NOT NULL,
                caption TEXT,
                uploader_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )

        conn.commit()

    seed_default_leader()


# ---------- LEADERS ----------

def ensure_leader(username: str, password: str, constituency: str):
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
        cur.execute("SELECT * FROM constituencies WHERE name = ?", (name,))
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
    lat: Optional[float] = None,
    lon: Optional[float] = None,
):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO projects (
                constituency_name, name, status, budget,
                implementer, timeline, verification_status,
                location, description, lat, lon
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                lat,
                lon,
            ),
        )
        conn.commit()


def get_projects_by_constituency(constituency_name: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, status, budget, implementer, timeline,
                   verification_status, location, description, lat, lon
            FROM projects
            WHERE constituency_name = ?
            """,
            (constituency_name,),
        )
        return cur.fetchall()


def get_project_by_id(project_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, constituency_name, name, status, budget, implementer,
                   timeline, verification_status, location, description, lat, lon
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        )
        return cur.fetchone()


# ---------- MEDIA / EVIDENCE ----------

def save_media_file(project_id: int, filename: str, content: bytes, media_type: str, caption: str, uploader_name: str) -> str:
    """Save file under data/media and record in DB. Returns file_path."""
    # simple safe basename
    base = os.path.basename(filename)
    stored_name = f"p{project_id}_{base}"
    full_path = os.path.join(MEDIA_ROOT, stored_name)

    # write file
    with open(full_path, "wb") as f:
        f.write(content)

    rel_path = os.path.join("data", "media", stored_name)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO project_media (
                project_id, media_type, file_path, caption, uploader_name
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (project_id, media_type, rel_path, caption, uploader_name),
        )
        conn.commit()

    return rel_path


def get_media_for_project(project_id: int) -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, media_type, file_path, caption, uploader_name, created_at
            FROM project_media
            WHERE project_id = ?
            ORDER BY created_at DESC
            """,
            (project_id,),
        )
        return cur.fetchall()


if __name__ == "__main__":
    init_db()
    print("infrasight.db ready.")
