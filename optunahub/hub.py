import importlib.util
import inspect
import os
import shutil
import sys
import types
from urllib.parse import urlparse

from ga4mp import GtagMP  # type: ignore
from github import Auth
from github import Github
from github.ContentFile import ContentFile
import optuna.version

import optunahub
from optunahub import _conf


def _import_github_dir(
    repo_owner: str,
    repo_name: str,
    ref: str | None,
    dir_path: str,
    base_url: str,
    force_reload: bool,
    auth: Auth.Auth | None,
) -> tuple[types.ModuleType, bool]:
    """Import a package in a GitHub repository.

    Args:
        repo_owner:
            The owner of the repository.
        repo_name:
            The name of the repository.
        ref:
            The Git reference (branch, tag, or commit SHA) for the package.
            If None, the default branch of the repository is used.
        dir_path:
            The directory path to load in the repository.
        base_url:
            The base URL for the GitHub API.
        force_reload:
            If `True`, the package will be downloaded from the repository.
            Otherwise, the package cached in the local directory will be loaded
            if available.
        auth:
            The authentication object for the GitHub API.

    Returns:
        The module object of the package and a boolean value indicating whether
        the cached package is imported.
    """

    # If `ref` is `None`, we need to access the repository to identify the
    # default branch regardless of the cache availability.
    g: Github | None = None
    if ref is None:
        g = Github(auth=auth, base_url=base_url)
        repo = g.get_repo(f"{repo_owner}/{repo_name}")
        ref = ref if ref is not None else repo.default_branch

    hostname = urlparse(base_url).hostname
    if hostname is None:
        raise ValueError(f"Invalid base URL: {base_url}")
    cache_dir_prefix = os.path.join(_conf.cache_home(), hostname, repo_owner, repo_name, ref)
    package_cache_dir = os.path.join(cache_dir_prefix, dir_path)
    use_cache = not force_reload and os.path.exists(package_cache_dir)

    if not use_cache:
        if g is None:
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
                    f.write(m.decoded_content)

    module_path = os.path.join(cache_dir_prefix, dir_path)
    module_name = os.path.basename(module_path)
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(module_path, "__init__.py")
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    sys.modules[module_name] = module
    setattr(sys.modules[module_name], "OPTUNAHUB_FORCE_RELOAD", force_reload)
    spec.loader.exec_module(module)

    return module, use_cache


def _check_analytics_optout() -> bool:
    """Check if the user has opted out of analytics.

    The analytics can be disabled in the following ways:
        1. setting the environment variable `OPTUNAHUB_NO_ANALYTICS` to "1",
        2. setting the value of `no_analytics` to `true` in the config file.

    Returns:
        `True` if the user has opted out of analytics.
    """

    optunahub_no_analytics_env = os.getenv("OPTUNAHUB_NO_ANALYTICS")
    if optunahub_no_analytics_env is not None:
        return optunahub_no_analytics_env == "1"

    is_no_analytics = _conf.get_config_value("no_analytics")
    if is_no_analytics is not None:
        return is_no_analytics

    print(
        "Would you allow OptunaHub to collect anonymous usage statistics?\n"
        "This information helps the Optuna team improve OptunaHub. [Yes/No]"
    )
    while is_no_analytics is None:
        ans = input()
        if ans.lower() in ["yes", "y"]:
            is_no_analytics = False
        elif ans.lower() in ["no", "n"]:
            is_no_analytics = True
        else:
            print("Please answer Yes (Y/yes/y) or No (N/no/n).")

    _conf.set_config_value("no_analytics", is_no_analytics)
    _conf.set_config_value("no_analytics_version", optunahub.__version__)
    print(
        f'Your preference is saved to "{_conf.config_file()}".\n'
        'You can change the setting later by editing the "no_analytics" value '
        "in the config file."
    )

    return is_no_analytics


def _report_stats(
    package: str,
    repo_owner: str,
    repo_name: str,
    registry_root: str,
    ref: str | None,
    base_url: str,
) -> None:
    """Report statistics to Google Analytics.

    Args:
        package:
            The package name loaded.
        repo_owner:
            The owner of the repository.
        repo_name:
            The name of the repository.
        registry_root:
            The root directory of the registry.
            The default is "package".
        ref:
            The Git reference (branch, tag, or commit SHA) for the package.
        base_url:
            The base URL for the GitHub API.
    """

    # Statistics are collected only for the official registries.
    TARGET_REPO_OWNERS = ["optuna"]
    TARGET_REPO_NAMES = ["optunahub-registry"]
    if (
        repo_owner not in TARGET_REPO_OWNERS
        or repo_name not in TARGET_REPO_NAMES
        or base_url != "https://api.github.com"
    ):
        return

    if _check_analytics_optout():
        return

    ga = GtagMP(
        measurement_id="xxx",
        api_secret="xxx",
        client_id="xxx",
    )
    event = ga.create_new_event("load_package")
    event.set_event_param(name="CI", value=os.getenv("CI", False))
    event.set_event_param(name="optuna_version", value=optuna.version.__version__)
    event.set_event_param(name="optunahub_version", value=optunahub.__version__)
    event.set_event_param(name="package", value=package)
    event.set_event_param(name="repo_owner", value=repo_owner)
    event.set_event_param(name="repo_name", value=repo_name)
    event.set_event_param(name="registry_root", value=registry_root)
    event.set_event_param(name="ref", value=ref)
    ga.send([event])


def load_module(
    package: str,
    *,
    repo_owner: str = "optuna",
    repo_name: str = "optunahub-registry",
    registry_root: str = "package",
    ref: str | None = "main",
    base_url: str = "https://api.github.com",
    force_reload: bool | None = None,
    auth: Auth.Auth | None = None,
) -> types.ModuleType:
    """Import a package from the OptunaHub registry.
    A third-party registry is also available by setting the `repo_owner` and
    `repo_name`.

    Args:
        package_name:
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
        base_url:
            The base URL for the GitHub API.
        force_reload:
            If `True`, the package will be downloaded from the repository.
            If `False`, the package cached in the local directory will be
            loaded if available.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `False`.
        auth:
            The authentication object for the GitHub API.
            It is required to access private/internal repositories.

    Returns:
        The module object of the package.
    """
    if force_reload is None:
        outer_globals = inspect.stack()[1][0].f_globals
        if "OPTUNAHUB_FORCE_RELOAD" in outer_globals:
            force_reload = outer_globals["OPTUNAHUB_FORCE_RELOAD"]
        else:
            force_reload = False

    if registry_root:
        dir_path = f"{registry_root}/{package}"
    else:
        dir_path = package

    module, is_cache = _import_github_dir(
        repo_owner=repo_owner,
        repo_name=repo_name,
        ref=ref,
        dir_path=dir_path,
        base_url=base_url,
        force_reload=force_reload,
        auth=auth,
    )

    if not is_cache:
        _report_stats(package, repo_owner, repo_name, registry_root, ref, base_url)

    return module


def load_module_local(
    package: str,
    *,
    registry_root: str = os.sep,
    force_reload: bool | None = None,
) -> types.ModuleType:
    """Import a package from the local registry.

    Args:
        package_name:
            The package name to load.
        registry_root:
            The root directory of the registry.
            The default is the root directory of the file system,
            e.g., "/" for UNIX-like systems.
        force_reload:
            This setting will be inherited to the inner `load`-like function.
            If `None`, the setting is inherited from the outer `load`-like function.
            For the outermost call, the default is `False`.

    Returns:
        The module object of the package.
    """
    if force_reload is None:
        outer_globals = inspect.stack()[1][0].f_globals
        if "OPTUNAHUB_FORCE_RELOAD" in outer_globals:
            force_reload = outer_globals["OPTUNAHUB_FORCE_RELOAD"]
        else:
            force_reload = False

    module_path = os.path.join(registry_root, package)
    module_name = os.path.basename(package)
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(module_path, "__init__.py")
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    module = importlib.util.module_from_spec(spec)
    if module is None:
        raise ImportError(f"Module {module_name} not found in {module_path}")
    sys.modules[module_name] = module
    setattr(sys.modules[module_name], "OPTUNAHUB_FORCE_RELOAD", force_reload)
    spec.loader.exec_module(module)

    return module
