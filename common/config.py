from common.env_handler import get_env

def __getattr__(name: str):
    """
    Dynamically fetch environment variables when they are accessed.
    This allows lazy evaluation: variables are only checked when actually imported/used.
    """
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    
    # Fetch the requested variable (e.g., DB_URL, ELASTIC_URL) directly from the .env file
    return get_env(name)