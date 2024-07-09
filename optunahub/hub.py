from __future__ import annotations

import importlib.util
import inspect
import logging
import os
import shutil
import sys
import types
from typing import Any
from urllib.parse import urlparse

from ga4mp import GtagMP  # type: ignore
from github import Auth
from github import Github
from github.ContentFile import ContentFile
import optuna.version

import optunahub
from optunahub import _conf


# Revert the log level to Python's default (i.e., WARNING) for the `ga4mp` package.
logging.getLogger("ga4mp.ga4mp").setLevel(logging.WARNING)


def _get_from_outer_globals(key: str, default: Any) -> Any:
    """Get a value from the outer globals.

    Find the value of the specified key from the outer globals.
    If the key is found, return the value immediately.
    Otherwise, search for the key in the outer globals of the outer caller.
    If the key is not found after the search, return the default value.

    Args:
        key:
            The key to get.
        default:
            The default value.
    """

    for s in inspect.stack():
        outer_globals = s[0].f_globals
        if key in outer_globals:
            return outer_globals[key]
    return default


def _report_stats(
    package: str,
    ref: str | None,
) -> None:
    """Report anonymous statistics.

    Collecting statistics for the official registry.
    The following parameters are collected:
      - CI: Whether the environment is CI or not.
      - optuna_version: The version of Optuna.
      - optunahub_version: The version of OptunaHub.
      - package: The package name loaded.
      - ref: The Git reference (branch, tag, or commit SHA) for the package.
    WE NEVER COLLECT ANY PERSONAL INFORMATION.

    The statistics can be disabled by setting the environmental variable OPTUNAHUB_NO_ANALYTICS=1,

    Args:
        package:
            The package name loaded.
        ref:
            The Git reference (branch, tag, or commit SHA) for the package.
    """
    ga = GtagMP(
        measurement_id="G-8EZ4F4Z74E",  # OptunaHub
        api_secret="8tWYGaAEQJiYJSUJfqNMTw",
        client_id="optunahub",  # Anonymous (by always setting client_id to "optunahub")
    )
    event = ga.create_new_event("load_module")
    event.set_event_param(name="CI", value=os.getenv("CI", False))
    event.set_event_param(name="optuna_version", value=optuna.version.__version__)
    event.set_event_param(name="optunahub_version", value=optunahub.__version__)
    event.set_event_param(name="package", value=package)
    event.set_event_param(name="ref", value=ref)
    ga.send([event])


def load_module(
    package: str,
    *,
    repo_owner: str = "optuna",
    repo_name: str = "optunahub-registry",
    registry_root: str = "package",
    ref: str | None = None,
    base_url: str = "https://api.github.com",
    force_reload: bool | None = None,
    auth: Auth.Auth | None = None,
) -> types.ModuleType:
    """Import a package from the OptunaHub registry.
    A third-party registry is also available by setting the `repo_owner` and `repo_name`.
    The imported package name is set to `optunahub_registry.package.<package>`.

    Args:
        package:
            The package name to load.
        repo_owner:
            The owner of the repository.
        repo_name:
            The name of the repository.
        registry_root:
            The root directory of the registry.
            The default is "package".
        ref:
            The Git reference (branch, tag, or commit SHA) for the package.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `"main"`.
        base_url:
            The base URL for the GitHub API.
        force_reload:
            If `True`, the package will be downloaded from the repository.
            If `False`, the package cached in the local directory will be
            loaded if available.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `False`.
        auth:
            `The authentication object <https://pygithub.readthedocs.io/en/latest/examples/Authentication.html>`__ for the GitHub API.
            It is required to access private/internal repositories.

    Returns:
        The module object of the package.
    """
    if ref is None:
        ref = _get_from_outer_globals("OPTUNAHUB_REF", "main")
    if force_reload is None:
        force_reload = _get_from_outer_globals("OPTUNAHUB_FORCE_RELOAD", False)

    hostname = urlparse(base_url).hostname
    if hostname is None:
        raise ValueError(f"Invalid base URL: {base_url}")
    dir_path = f"{registry_root}/{package}" if registry_root else package
    cache_dir_prefix = os.path.join(_conf.cache_home(), hostname, repo_owner, repo_name, ref)
    package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
    use_cache = not force_reload and os.path.exists(package_cache_dir)

    # Download the package from the GitHub repository.
    if not use_cache:
        g = Github(auth=auth, base_url=base_url)
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
        package_contents = repo.get_contents(dir_path, ref)

        if isinstance(package_contents, ContentFile):
            package_contents = [package_contents]

        shutil.rmtree(package_cache_dir, ignore_errors=True)
        os.makedirs(cache_dir_prefix, exist_ok=True)
        for m in package_contents:
            file_path = os.path.join(cache_dir_prefix, m.path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if m.type == "dir":
                dir_contents = repo.get_contents(m.path, ref)
                if isinstance(dir_contents, ContentFile):
                    dir_contents = [dir_contents]
                package_contents.extend(dir_contents)
            else:
                with open(file_path, "wb") as f:
                    try:
                        decoded_content = m.decoded_content
                    except AssertionError:
                        continue
                    f.write(decoded_content)

    # Statistics are collected only for the official registry.
    is_official_registry = (
        repo_owner == "optuna"
        and repo_name == "optunahub-registry"
        and base_url == "https://api.github.com"
    )
    if not _conf.is_no_analytics() and not use_cache and is_official_registry:
        _report_stats(package, ref)

    return load_local_module(
        package,
        ref=ref,
        registry_root=os.path.join(cache_dir_prefix, registry_root),
        force_reload=force_reload,
    )


def load_local_module(
    package: str,
    *,
    ref: str | None = None,
    registry_root: str = os.sep,
    force_reload: bool | None = None,
) -> types.ModuleType:
    """Import a package from the local registry.
       The imported package name is set to `optunahub_registry.package.<package>`.

    Args:
        package:
            The package name to load.
        registry_root:
            The root directory of the registry.
            The default is the root directory of the file system,
            e.g., "/" for UNIX-like systems.
        ref:
            This setting will be inherited to the inner `load`-like function.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `"main"`.
        force_reload:
            This setting will be inherited to the inner `load`-like function.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `False`.

    Returns:
        The module object of the package.
    """

    if ref is None:
        ref = _get_from_outer_globals("OPTUNAHUB_REF", "main")
    if force_reload is None:
        force_reload = _get_from_outer_globals("OPTUNAHUB_FORCE_RELOAD", False)

    module_path = os.path.join(registry_root, package)
    module_name = f"optunahub_registry.package.{package.replace('/', '.')}"
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(module_path, "__init__.py")
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    setattr(module, "OPTUNAHUB_REF", ref)
    setattr(module, "OPTUNAHUB_FORCE_RELOAD", force_reload)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module
