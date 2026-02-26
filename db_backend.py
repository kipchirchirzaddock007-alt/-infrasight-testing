def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        # Drop old tables for testing phase (reset schema)
        cur.execute("DROP TABLE IF EXISTS project_media;")
        cur.execute("DROP TABLE IF EXISTS projects;")
        cur.execute("DROP TABLE IF EXISTS emergency_assets;")
        cur.execute("DROP TABLE IF EXISTS constituencies;")
        cur.execute("DROP TABLE IF EXISTS leaders;")

        # Leaders
        cur.execute(
            """
            CREATE TABLE leaders (
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
            CREATE TABLE constituencies (
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
            CREATE TABLE emergency_assets (
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

        # Development projects (with lat/lon)
        cur.execute(
            """
            CREATE TABLE projects (
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

        # Citizen media/evidence
        cur.execute(
            """
            CREATE TABLE project_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
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
