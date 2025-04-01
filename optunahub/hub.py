from __future__ import annotations

import importlib.util
import logging
import os
import shutil
import sys
import types
from urllib.parse import urlparse
import re

from ga4mp import GtagMP  # type: ignore
from github import Auth
from github import Github
from github.ContentFile import ContentFile
import optuna.version
from git import Repo

import optunahub
from optunahub import _conf


# Dummy optunahub_registry module is required to avoid ModuleNotFoundError.
sys.modules["optunahub_registry"] = types.ModuleType("optunahub_registry")


# Revert the log level to Python's default (i.e., WARNING) for the `ga4mp` package.
logging.getLogger("ga4mp.ga4mp").setLevel(logging.WARNING)


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
    ref: str = "main",
    base_url: str = "https://github.com",
    force_reload: bool = False,
    auth: Auth.Auth | None = None,
) -> types.ModuleType:
    """Import a package from the OptunaHub registry.
    The imported package name is set to ``optunahub_registry.package.<package>``.
    A third-party registry is also available by setting the ``repo_owner`` and
    ``repo_name``.

    Args:
        package:
            The package name to load.
        repo_owner:
            The owner of the repository.
        repo_name:
            The name of the repository.
        ref:
            The Git reference (branch, tag, or commit SHA) for the package.
        base_url:
            If ``auth`` is :obj:`None`, the base URI for the remote repository.
            In this case, specifying ``git@github.com`` allows access to private repositories via SSH.
            If ``auth`` is not :obj:`None`, the base URL for the GitHub API.
        force_reload:
            If :obj:`True`, the package will be downloaded from the repository.
            If :obj:`False`, the package cached in the local directory will be
            loaded if available.
        auth:
            `The authentication object <https://pygithub.readthedocs.io/en/latest/examples/Authentication.html>`__ for the GitHub API.
            It is required to access private/internal repositories via the GitHub API.

    Returns:
        The module object of the package.
    """
    registry_root = "package"
    dir_path = f"{registry_root}/{package}"
    hostname = _extract_hostname(base_url)
    if hostname is None:
        raise ValueError(f"Invalid base URI: {base_url}")
    cache_dir_prefix = os.path.join(_conf.cache_home(), hostname, repo_owner, repo_name, ref)
    package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
    use_cache = not force_reload and os.path.exists(package_cache_dir)

    if not use_cache:
        if auth is None:
            _download_via_git(
                repo_owner=repo_owner,
                repo_name=repo_name,
                dir_path=dir_path,
                ref=ref,
                base_url=base_url,
                cache_dir_prefix=cache_dir_prefix,
            )
        else:
            _download_via_github_api(
                auth=auth,
                base_url=base_url,
                repo_owner=repo_owner,
                repo_name=repo_name,
                dir_path=dir_path,
                ref=ref,
                package_cache_dir=package_cache_dir,
                cache_dir_prefix=cache_dir_prefix,
            )


    local_registry_root = os.path.join(cache_dir_prefix, registry_root)
    module = load_local_module(
        package=package,
        registry_root=local_registry_root,
    )

    # Statistics are collected only for the official registry.
    is_official_registry = (
        repo_owner == "optuna"
        and repo_name == "optunahub-registry"
        and base_url == "https://github.com"
    )
    if not _conf.is_no_analytics() and not use_cache and is_official_registry:
        _report_stats(package, ref)

    return module

def _extract_hostname(url: str) -> str | None:
    if "://" in url:
        return urlparse(url).hostname
    else:
        match = re.match(r"(?:.+@)?([^:]+)(?::.*)?", url)
        return match and match.group(1)

def _download_via_git(
    repo_owner: str,
    repo_name: str,
    dir_path: str,
    ref: str,
    base_url: str,
    cache_dir_prefix: str,
) -> None:
    repo_url_separator = "/" if "://" in base_url else ":"
    repo_url = f"{base_url.rstrip('/')}{repo_url_separator}{repo_owner}/{repo_name}"
    repo = Repo.init(cache_dir_prefix)
    origin = repo.remotes.origin if "origin" in repo.remotes else repo.create_remote("origin", repo_url)
    if repo.remotes.origin.url != repo_url:
        repo.remotes.origin.set_url(repo_url)
    repo.git.sparse_checkout("init", "--cone")
    repo.git.sparse_checkout("set", dir_path)
    origin.fetch(refspec=ref, depth=1)
    repo.git.checkout("FETCH_HEAD")

def _download_via_github_api(
    auth: Auth.Auth | None,
    base_url: str,
    repo_owner: str,
    repo_name: str,
    dir_path: str,
    ref: str,
    package_cache_dir: str,
    cache_dir_prefix: str,
) -> None:
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

def load_local_module(
    package: str,
    *,
    registry_root: str = os.sep,
) -> types.ModuleType:
    """Import a package from the local registry.
       The imported package name is set to ``optunahub_registry.package.<package>``.

    Args:
        package:
            The package name to load.
        registry_root:
            The root directory of the registry.
            The default is the root directory of the file system,
            e.g., "/" for UNIX-like systems.

    Returns:
        The module object of the package.
    """

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
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module
