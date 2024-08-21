import os
import sys

import optuna
import pytest

import optunahub


def test_load_module() -> None:
    def objective(trial: optuna.Trial) -> float:
        x = trial.suggest_float("x", 0, 1)

        return x

    m = optunahub.load_module("samplers/simulated_annealing")
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
    sampler = m.RandomSampler()
    study = optuna.create_study(sampler=sampler)
    study.optimize(objective, n_trials=10)


@pytest.mark.parametrize(
    (
        "repo_owner",
        "ref",
        "force_reload",
        "expected_repo_owner",
        "expected_ref",
        "expected_force_reload",
    ),
    [
        (None, None, None, "optuna", "main", False),
        ("optuna", "main", False, "optuna", "main", False),
        ("test", "test", True, "test", "test", True),
    ],
)
def test_load_settings_propagation(
    repo_owner: str,
    ref: str,
    force_reload: bool,
    expected_repo_owner: str,
    expected_ref: str,
    expected_force_reload: bool,
) -> None:
    m = optunahub.load_local_module(
        "package_for_test_hub",
        registry_root=os.path.dirname(__file__),
        repo_owner=repo_owner,
        ref=ref,
        force_reload=force_reload,
    )
    assert m.repo_owner == expected_repo_owner
    assert m.ref == expected_ref
    assert m.force_reload == expected_force_reload
    assert m.implementation.repo_owner == expected_repo_owner
    assert m.implementation.ref == expected_ref
    assert m.implementation.force_reload == expected_force_reload

    del sys.modules["optunahub_registry.package.package_for_test_hub"]
    del sys.modules["optunahub_registry.package.package_for_test_hub.implementation"]
