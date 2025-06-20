from __future__ import annotations

import os
import platform


def cache_home() -> str:
    """Return the path to the cache directory.

    Returns:
        The path to the cache directory.
    """

    optunahub_cache_home_env = os.getenv("OPTUNAHUB_CACHE_HOME")
    if optunahub_cache_home_env is not None:
        return optunahub_cache_home_env

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
            os.getenv("XDG_CACHE_HOME", os.path.join(os.path.expanduser("~"), ".cache")),
            "optunahub",
        )


def is_no_analytics() -> bool:
    """Return whether the analytics is disabled.

    Returns:
        `True` if the analytics is disabled, `False` if the analytics is enabled.
    """

    return os.getenv("OPTUNAHUB_NO_ANALYTICS", "0") == "1"
