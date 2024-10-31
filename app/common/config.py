"""

Configuration settings for the application.

# Precedence of settings:
# -----------------------
# environment variables
# .env file (if load_dotenv=True)
# settings_files (taking into consideration only settings for the correct env

"""

import os
from dynaconf import Dynaconf
from loguru import logger

_settings = Dynaconf(
    settings_files=[
        "app/config/settings.toml",
        "app/config/settings.dev-localhost.toml",
        "app/config/settings.dev-compose.toml",
        "app/config/settings.test.toml",
        "app/config/settings.kubernetes.toml",
        "app/config_prod/.secrets.toml",
        # this file comes from separate dir to make it
        # easier to mount setting file in kubernetes
        "app/config/.secrets.toml",
    ],
    load_dotenv=True,
    # useful for dev-localhost only, overridden when running in docker
    env_switcher="ENV_FOR_DYNACONF",
    environments=True,
)

# Debugging: Print environment variables
logger.debug(f"Environment Variables: {os.environ}")


class Settings:
    """
    This class is a WA for the fact that Dynaconf does not seem to let env variables
    override the settings files, even though it says it does.
    Probably a misconfiguration I need to fix.
    """

    def __init__(self, dynaconf_settings):
        self._dynaconf_settings = dynaconf_settings

    def get(self, name, default=None):
        # Check if the value is in the environment variables
        env_value = os.getenv(name)

        # If found in environment, return that value
        if env_value is not None:
            return env_value

        # Otherwise, return from Dynaconf settings or the default value
        return self._dynaconf_settings.get(name, default)

    def __getattr__(self, name):
        # Convert the attribute name to uppercase (Dynaconf convention)
        name = name.upper()

        # Use the same logic for attribute access as in the get() method
        return self.get(name)


def get_connection_url():

    user = _settings.database_user
    password = _settings.database_password
    name = _settings.database_name
    host = _settings.database_host
    port = _settings.database_port

    # Construct and return the connection URL
    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return connection_url


_settings.DATABASE_URL = get_connection_url()

settings = Settings(_settings)
