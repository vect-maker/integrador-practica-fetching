import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

_ = load_dotenv()

PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT", "5432")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGSSLMODE = os.getenv("PGSSLMODE", "require")

# Admin/maintenance database used to manage other databases
ADMIN_DB = os.getenv("PGADMIN_DATABASE", "postgres")
# Target database to reset and apply schema migrations
TARGET_DB = os.getenv("RAW_DB_NAME", "raw")


def get_conninfo(dbname: str) -> str:
    """Build a PostgreSQL connection string for a specific database."""
    return (
        f"host={PGHOST} "
        f"port={PGPORT} "
        f"user={PGUSER} "
        f"password={PGPASSWORD} "
        f"dbname={dbname} "
        f"sslmode={PGSSLMODE}"
    )


def reset_database(target_db: str = TARGET_DB, admin_db: str = ADMIN_DB) -> None:
    """Drop target database if it exists, then create a clean one."""
    print(f"Connecting to admin database '{admin_db}' on {PGHOST}...")
    with (
        psycopg.connect(get_conninfo(admin_db), autocommit=True) as conn,
        conn.cursor() as cur,
    ):
        # Terminate any remaining active connections to the target database
        _ = cur.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid();
            """,
            (target_db,),
        )

        print(f"Dropping database '{target_db}' if it exists...")
        _ = cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE);").format(
                sql.Identifier(target_db)
            )
        )

        print(f"Creating fresh database '{target_db}'...")
        _ = cur.execute(
            sql.SQL("CREATE DATABASE {};").format(sql.Identifier(target_db))
        )

    print(f"Database '{target_db}' created successfully.\n")


def apply_migrations(
    target_db: str = TARGET_DB, migration_file: Path | None = None
) -> None:
    """Connect to the target database and execute the schema migration directly."""
    target_file = (
        migration_file
        if migration_file is not None
        else Path("migrations/01_schema.sql")
    )
    print(f"Connecting to target database '{target_db}'...")
    sql_content = target_file.read_bytes()
    with (
        psycopg.connect(get_conninfo(target_db)) as conn,
        conn.cursor() as cur,
    ):
        print(f"Applying schema migration from '{target_file}'...")
        _ = cur.execute(sql_content)
        conn.commit()
    print(f"Schema migration '{target_file}' applied successfully.")


if __name__ == "__main__":
    reset_database(TARGET_DB)
    apply_migrations(TARGET_DB, Path("migrations/01_schema.sql"))
