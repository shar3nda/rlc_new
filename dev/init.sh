#!/bin/bash

set -e
set -o pipefail
set -m

DEV_DIR=$(realpath "$(dirname "$0")")
REPO_DIR="$DEV_DIR/.."

DB_USER="rlc_new"
DB_PASSWORD="VerySecureUserPassword"
DB_NAME="rlc_new"

log_action() {
    local message=$1
    local level=${2:-INFO}
    echo "[$level] $message"
}

run_sql() {
    local query=$1
    sudo -u postgres psql -c "$query"
}

pushd_q() {
    command pushd "$@" >/dev/null
}

# shellcheck disable=SC2120
popd_q() {
    command popd "$@" >/dev/null
}

log_action "Installing spellcheck tools..."
sudo apt install -y enchant-2 hunspell-ru

if [ ! -d ".venv" ]; then
    log_action ".venv not found. Creating venv..."
    python3 -m venv .venv

    log_action "Activating venv..."
    source .venv/bin/activate

    if [ -f "requirements.txt" ]; then
        log_action "Installing requirements.txt..."
        pip install -r requirements.txt
    else
        log_action "requirements.txt not found. Exiting." "ERROR"
        exit 1
    fi
else
    log_action ".venv already exists. Skipping venv creation."
    log_action "Activating venv..."
    source .venv/bin/activate
fi

if ! pg_isready -h localhost -p 5432 -q; then
    log_action "Postgres is not running. Start the postgres service." "ERROR"
    exit 1
fi

log_action "Recreating database..."

log_action "Dropping database $DB_NAME if it exists..."
run_sql "DROP DATABASE IF EXISTS $DB_NAME"

log_action "Dropping user $DB_USER if it exists..."
run_sql "DROP USER IF EXISTS $DB_USER"

log_action "Creating user $DB_USER..."
run_sql "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'"

log_action "Creating database $DB_NAME..."
run_sql "CREATE DATABASE $DB_NAME"

log_action "Setting owner of database $DB_NAME to $DB_USER..."
run_sql "ALTER DATABASE $DB_NAME OWNER TO $DB_USER"

log_action "Applying migrations..."
pushd_q "$REPO_DIR"
python "$REPO_DIR/manage.py" makemigrations
python "$REPO_DIR/manage.py" migrate
popd_q

log_action "Seeding database..."
pushd_q "$REPO_DIR"
python "$REPO_DIR/dev/seed_db.py"
popd_q

log_action "Setup complete. Run 'source .venv/bin/activate' to activate the virtual environment."
