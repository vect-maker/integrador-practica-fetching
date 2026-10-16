set dotenv-load
export PATH := justfile_directory() + "/.venv/bin:" + env('PATH')
set shell := ["bash", "-c"]

# Default recipe: list available recipes
default:
    @just --list

# Run dbt commands (e.g. `just dbt debug`, `just dbt run`, `just dbt test`)
dbt *args="debug":
    exec dbt {{ args }} --project-dir dbt --profiles-dir dbt

# Run the complete database pipeline (reset DB, schema migration, and load data)
load:
    python loader.py

# Load only Parquet data into the existing raw database schema
load-data:
    python loader.py --data-only

# Reset database and apply schema migrations only
load-schema:
    python loader.py --schema-only

fetch:
    python fetcher.py

crear-entorno:
    python -m venv .venv
