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


@pytest.mark.parametrize(
    "git_command",
    [
        pytest.param("/usr/bin/git"),
        pytest.param(None, marks=pytest.mark.github_api),
    ],
)
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
    monkeypatch.setattr("optunahub.hub._download_via_git", mock_do_nothing)
    monkeypatch.setattr("optunahub.hub._download_via_github_api", mock_do_nothing)
    monkeypatch.setattr("optunahub.hub.load_local_module", mock_do_nothing)
    # Analytics must be activated.
    monkeypatch.setattr("optunahub._conf.is_no_analytics", lambda: False)

    # Capture the call of _report_stats.
    calls: list[None] = []
    monkeypatch.setattr("optunahub.hub._report_stats", lambda *args, **kwargs: calls.append(None))
    optunahub.load_module(package="dummy/test")
    assert len(calls) > 0


@pytest.mark.parametrize(
    "package_name, cache_expiration_seconds, expected_result",
    [
        ("samplers/simulated_annealing", "1", False),
        ("samplers/simulated_annealing", "1000000", True),
        ("samplers/simulated_annealing", None, True),
    ],
)
def test_if_cache_is_valid(
    monkeypatch: MonkeyPatch,
    package_name: str,
    cache_expiration_seconds: str | None,
    expected_result: bool,
) -> None:
    if cache_expiration_seconds is not None:
        monkeypatch.setenv("OPTUNAHUB_CACHE_EXPIRATION_SECONDS", cache_expiration_seconds)
    else:
        monkeypatch.delenv("OPTUNAHUB_CACHE_EXPIRATION_SECONDS", raising=False)

    cache_dir_prefix = os.path.join(
        _conf.cache_home(), "github.com", "optuna", "optunahub-registry", "main"
    )
    package_cache_dir = os.path.join(cache_dir_prefix, "package", package_name)

    time.sleep(2)
    assert _is_cache_valid(package_cache_dir) == expected_result
