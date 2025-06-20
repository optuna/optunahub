from __future__ import annotations

import os
import shutil

import optuna
import pytest
from pytest import MonkeyPatch

import optunahub
from optunahub.hub import _extract_hostname


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
    def mock_do_nothing(*args, **kwargs) -> None:
        return

    # To make the environment look like git is available or unavailable.
    monkeypatch.setattr(shutil, "which", lambda cmd: git_command)
    monkeypatch.setattr("optunahub.hub._download_via_git", mock_do_nothing)
    monkeypatch.setattr("optunahub.hub._download_via_github_api", mock_do_nothing)
    monkeypatch.setattr("optunahub.hub.load_local_module", mock_do_nothing)
    # Analytics must be activated.
    monkeypatch.setattr("optunahub._conf.is_no_analytics", lambda: False)

    # Capture the call of _report_stats.
    calls = []
    monkeypatch.setattr(
        "optunahub.hub._report_stats", lambda *args, **kwargs: calls.append(None)
    )
    optunahub.load_module(package="dummy/test")
    assert len(calls) > 0
