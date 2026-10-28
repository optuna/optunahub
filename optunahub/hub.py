from __future__ import annotations

import importlib.util
import os
import re
import shutil
import sys
import tempfile
import types
from urllib.parse import urlparse

from git import Repo
from github import Auth
from github import Github
from github.ContentFile import ContentFile

from optunahub import _conf


# Dummy optunahub_registry module is required to avoid ModuleNotFoundError.
sys.modules["optunahub_registry"] = types.ModuleType("optunahub_registry")


def load_module(
    package: str,
    *,
    repo_owner: str = "optuna",
    repo_name: str = "optunahub-registry",
    ref: str = "main",
    base_url: str | None = None,
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
            If ``auth`` is :obj:`None` and the ``git`` command is available, this should be the base URI for the remote repository.
            In this case, specifying SSH endpoints, such as ``git@github.com``, ``git@gitlab.example.com``, or other custom domains and similar
            services, allows access to private/internal repositories via SSH.
            Otherwise, this should be the base URL for the GitHub API, such as ``https://api.github.com``, ``https://gitlab.example.com/api/v4/``,
            or other custom domains and similar services, depending on your setup.
        force_reload:
            If :obj:`True`, the package will be downloaded from the repository.
            If :obj:`False`, the package cached in the local directory will be loaded if available.
        auth:
            `The authentication object <https://pygithub.readthedocs.io/en/latest/examples/Authentication.html>`__ for the GitHub API.
            It also allows access to access private/internal repositories via the GitHub API.

    Returns:
        The module object of the package.
    """
    registry_root = "package"
    dir_path = f"{registry_root}/{package}"
    hostname = _extract_hostname(base_url) if base_url else "github.com"
    if hostname is None:
        raise ValueError(f"Invalid base URI: {base_url}")
    cache_dir_prefix = os.path.join(_conf.cache_home(), hostname, repo_owner, repo_name, ref)
    package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
    use_cache = not force_reload and os.path.exists(package_cache_dir)

    if not use_cache:
        if auth is None and shutil.which("git") is not None:
            _download_via_git(
                base_url=base_url or "https://github.com",
                repo_owner=repo_owner,
                repo_name=repo_name,
                dir_path=dir_path,
                ref=ref,
                cache_dir_prefix=cache_dir_prefix,
            )
        else:
            _download_via_github_api(
                auth=auth,
                base_url=base_url or "https://api.github.com",
                repo_owner=repo_owner,
                repo_name=repo_name,
                dir_path=dir_path,
                ref=ref,
                cache_dir_prefix=cache_dir_prefix,
            )

    local_registry_root = os.path.join(cache_dir_prefix, registry_root)
    module = load_local_module(
        package=package,
        registry_root=local_registry_root,
    )

    return module


def _extract_hostname(url: str) -> str | None:
    if "://" in url:
        return urlparse(url).hostname
    else:
        # NOTE(kAIto47802) Extract hostname: skip optional user@, capture up to `:`, ignore the rest.
        match = re.match(r"(?:.+@)?([^:]+)(?::.*)?", url)
        return match and match.group(1)


def _download_via_git(
    base_url: str,
    repo_owner: str,
    repo_name: str,
    dir_path: str,
    ref: str,
    cache_dir_prefix: str,
) -> None:
    repo_url_separator = "/" if "://" in base_url else ":"
    repo_url = f"{base_url.rstrip('/')}{repo_url_separator}{repo_owner}/{repo_name}"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize a temporary Git repository to perform sparse checkout.
        repo = Repo.init(tmpdir)
        origin = (
            repo.remotes.origin
            if "origin" in repo.remotes
            else repo.create_remote("origin", repo_url)
        )
        if repo.remotes.origin.url != repo_url:
            repo.remotes.origin.set_url(repo_url)
        repo.git.sparse_checkout("init", "--cone")
        repo.git.sparse_checkout("set", dir_path)
        origin.fetch(refspec=ref, depth=1)
        repo.git.checkout("FETCH_HEAD")

        # Move the downloaded package to the cache directory.
        package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
        shutil.rmtree(package_cache_dir, ignore_errors=True)
        os.makedirs(os.path.dirname(package_cache_dir), exist_ok=True)
        shutil.move(os.path.join(tmpdir, dir_path), package_cache_dir)


def _download_via_github_api(  # pragma: no cover
    auth: Auth.Auth | None,
    base_url: str,
    repo_owner: str,
    repo_name: str,
    dir_path: str,
    ref: str,
    cache_dir_prefix: str,
) -> None:
    g = Github(auth=auth, base_url=base_url)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    package_contents = repo.get_contents(dir_path, ref)

    if isinstance(package_contents, ContentFile):
        package_contents = [package_contents]

    with tempfile.TemporaryDirectory() as tmpdir:
        for m in package_contents:
            file_path = os.path.join(tmpdir, m.path)
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

        # Move the downloaded package to the cache directory.
        package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
        shutil.rmtree(package_cache_dir, ignore_errors=True)
        os.makedirs(os.path.dirname(package_cache_dir), exist_ok=True)
        shutil.move(os.path.join(tmpdir, dir_path), package_cache_dir)


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
    previous_module = sys.modules.get(module_name)
    if previous_module is not None and previous_module.__file__ != module.__file__:
        # Relative imports must come from the newly selected registry root.
        for name in list(sys.modules):
            if name.startswith(module_name + "."):
                del sys.modules[name]
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module
