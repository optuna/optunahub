from __future__ import annotations

import os
import shutil
import time

import optuna
import pytest
from pytest import MonkeyPatch

import optunahub
from optunahub import _conf
from optunahub.hub import _extract_hostname
from optunahub.hub import _is_cache_valid


@pytest.mark.parametrize("git_command", ["/usr/bin/git", None])
def test_load_module(monkeypatch: MonkeyPatch, git_command: str | None) -> None:
    def objective(trial: optuna.Trial) -> float:
        x = trial.suggest_float("x", 0, 1)

        return x

    monkeypatch.setattr(shutil, "which", lambda cmd: git_command)
    m = optunahub.load_module("samplers/simulated_annealing", force_reload=True)
    assert m.__name__ == "optunahub_registry.package.samplers.simulated_annealing"

    # Confirm no error occurs by running optimization
    sampler = m.SimulatedAnnealingSampler()
    study = optuna.create_study(sampler=sampler)
    study.optimize(objective, n_trials=10)


def test_load_local_module() -> None:
    def objective(trial: optuna.Trial) -> float:
        x = trial.suggest_float("x", 0, 1)

        return x

    m = optunahub.load_local_module(
        "package_for_test_hub",
        registry_root=os.path.dirname(__file__),
    )
    assert m.__name__ == "optunahub_registry.package.package_for_test_hub"

    # Confirm no error occurs by running optimization
    sampler = m.TestSampler()
    study = optuna.create_study(sampler=sampler)
    study.optimize(objective, n_trials=10)


@pytest.mark.parametrize(
    "uri, expected_hostname",
    [
        ("git@github.com", "github.com"),
        ("git@gitlab.example.com", "gitlab.example.com"),
        ("https://api.github.com", "api.github.com"),
        ("https://gitlab.example.com/api/v4/", "gitlab.example.com"),
    ],
)
def test_extract_hostname(uri: str, expected_hostname: str) -> None:
    assert _extract_hostname(uri) == expected_hostname


@pytest.mark.parametrize("git_command", ["/usr/bin/git", None])
def test_if_report_stats_is_called(monkeypatch: MonkeyPatch, git_command: str | None) -> None:
    def mock_do_nothing(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        return

    # To make the environment look like git is available or unavailable.
    monkeypatch.setattr(shutil, "which", lambda cmd: git_command)
    monkeypatch.setattr("optunahub.hub._load_remote_module", mock_do_nothing)
    monkeypatch.setattr("optunahub.hub.load_local_module", mock_do_nothing)
    # Analytics must be activated.
    monkeypatch.setattr("optunahub._conf.is_no_analytics", lambda: False)

    # Capture the call of _report_stats.
    calls: list[None] = []
    monkeypatch.setattr("optunahub.hub._report_stats", lambda *args, **kwargs: calls.append(None))
    optunahub.load_module(package="dummy/test")
    assert len(calls) > 0


@pytest.mark.parametrize(
    "mtime_offset, cache_expiration_seconds, expected",
    [
        (-10, 30, True),
        (-40, 30, False),
        (-30, 30, False),
    ],
)
def test_is_cache_valid(
    monkeypatch: MonkeyPatch, mtime_offset: int, cache_expiration_seconds: int, expected: bool
) -> None:
    registry_root = "package"
    package = "samplers/auto_sampler"
    repo_owner = "optuna"
    repo_name = "optunahub-registry"
    ref = "main"
    base_url = "git@github.com"
    hostname = _extract_hostname(base_url)
    assert hostname is not None
    cache_dir_prefix = os.path.join(_conf.cache_home(), hostname, repo_owner, repo_name, ref)
    package_cache_dir = os.path.join(cache_dir_prefix, registry_root, package)

    _ = optunahub.load_module(
        package,
        force_reload=True,
        repo_owner=repo_owner,
        repo_name=repo_name,
        ref=ref,
        base_url=base_url,
    )

    monkeypatch.setenv("OPTUNAHUB_CACHE_EXPIRATION_SECONDS", str(cache_expiration_seconds))

    fake_now = 1000000000
    monkeypatch.setattr(time, "time", lambda: fake_now)
    modified_time = fake_now + mtime_offset
    monkeypatch.setattr(
        "optunahub.hub._get_cache_latest_modified_time", lambda package_cache_dir: modified_time
    )
    assert _is_cache_valid(package_cache_dir) is expected
