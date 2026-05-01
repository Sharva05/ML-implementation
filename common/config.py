from common.env_handler import get_required_env

env = get_required_env(
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_PORT",
    "ELASTIC_URL"
)

POSTGRES_DB = env["POSTGRES_DB"]
POSTGRES_USER = env["POSTGRES_USER"]
POSTGRES_PASSWORD = env["POSTGRES_PASSWORD"]
POSTGRES_PORT = env["POSTGRES_PORT"]
ELASTIC_URL = env["ELASTIC_URL"]

DB_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
)