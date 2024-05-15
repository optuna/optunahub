from __future__ import annotations

import os
import platform
from typing import Any

import toml


def config_file() -> str:
    """Return the path to the configuration file.

    Returns:
        The path to the configuration file.
    """
    if platform.system() == "Windows":  # NOTE: unverified
        return os.path.join(
            os.getenv(
                "APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
            ),
            "optunahub",
            "config.toml",
        )
    else:  # UNIX-like
        return os.path.join(
            os.getenv(
                "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
            ),
            "optunahub",
            "config.toml",
        )


def get_config_value(key: str) -> Any:
    """Return the value of a configuration key.

    Args:
        key:
            The configuration key.

    Returns:
        The value of the configuration key.
    """
    cf = config_file()
    if os.path.isfile(cf):
        with open(cf, "r") as f:
            conf = toml.load(f)
            if key in conf:
                return conf[key]
    return None


def set_config_value(key: str, value: Any) -> bool:
    """Set the value of a configuration key.

    Args:
        key:
            The configuration key.
        value:
            The value of the configuration key.

    Returns:
        `True` if the value was set or updated, `False` if the value was not updated.
    """

    conf = {}
    cf = config_file()
    if os.path.isfile(cf):
        with open(cf, "r") as f:
            conf = toml.load(f)

    if key in conf and conf[key] == value:
        return False

    conf[key] = value
    os.makedirs(os.path.dirname(cf), exist_ok=True)
    with open(cf, "w") as f:
        toml.dump(conf, f)
    return True


def cache_home() -> str:
    """Return the path to the cache directory.

    Returns:
        The path to the cache directory.
    """

    optunahub_cache_home_env = os.getenv("OPTUNAHUB_CACHE_HOME")
    if optunahub_cache_home_env is not None:
        return optunahub_cache_home_env

    conf_value = get_config_value("cache_home")
    if conf_value is not None:
        return conf_value

    if platform.system() == "Windows":  # NOTE: unverified
        return os.path.join(
            os.getenv(
                "LOCALAPPDATA",
                os.path.join(os.path.expanduser("~"), "AppData", "Local"),
            ),
            "optunahub",
            "cache",
        )
    else:  # UNIX-like
        return os.path.join(
            os.getenv(
                "XDG_CACHE_HOME", os.path.join(os.path.expanduser("~"), ".cache")
            ),
            "optunahub",
        )


def no_analytics() -> bool | None:
    """Return whether the analytics is disabled.

    Returns:
        `True` if the analytics is disabled, `False` if the analytics is enabled, or `None` if the configuration is not set.
    """

    no_analytics_env = os.getenv("OPTUNAHUB_NO_ANALYTICS")
    if no_analytics_env is not None:
        return no_analytics_env == "1"

    return get_config_value("no_analytics")
