from typing import Optional
from decouple import config, Csv


class Env:
    """Centralized environment variables."""

    def __init__(self):
        pass

    @classmethod
    def get(cls, key: str, default=None, cast=None) -> Optional[str]:
        """Safe env getter with casting"""
        kwargs = {"default": default}
        if cast is not None:
            kwargs["cast"] = cast
        value = config(key, **kwargs)
        if value is None and default is None:
            raise ValueError(f"Missing required env var: {key}")
        return value

    # --- Database Settings ---
    @property
    def db_host(self):
        return self.get("DB_HOST", default="localhost")

    @property
    def db_name(self):
        return self.get("DB_NAME")

    @property
    def db_user(self):
        return self.get("DB_USER")

    @property
    def db_password(self):
        return self.get("DB_PASSWORD")

    @property
    def db_port(self):
        return self.get("DB_PORT", default=5432, cast=int)

    # --- Django Settings ---
    @property
    def secret_key(self):
        return self.get("SECRET_KEY")

    @property
    def debug(self):
        # Casts 'True'/'False' strings in .env to actual Python Booleans
        return self.get("DJANGO_DEBUG", default=False, cast=bool)

    @property
    def allowed_hosts(self):
        return self.get("DJANGO_ALLOWED_HOSTS", cast=Csv())

    @property
    def create_su_ips(self):
        return self.get("CREATE_SU_IPS", default=[], cast=Csv())


env = Env()
