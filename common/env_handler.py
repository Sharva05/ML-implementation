from dotenv import dotenv_values, find_dotenv


class EnvError(Exception):
    pass


# Load ONLY .env file (no Windows/system env)
_env = dotenv_values(find_dotenv())


def get_required_env(*keys: str) -> dict:
    missing = []
    values = {}

    for key in keys:
        value = _env.get(key)

        if value is None or value.strip() == "":
            missing.append(key)
        else:
            values[key] = value.strip()

    if missing:
        raise EnvError(
            f"[ENV ERROR] Missing required variables: {', '.join(missing)}"
        )

    return values