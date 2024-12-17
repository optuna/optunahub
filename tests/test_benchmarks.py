from __future__ import annotations

import optuna

from optuna.samplers._base import _CONSTRAINTS_KEY
import optunahub


class TestProblem(optunahub.benchmarks.BaseProblem):
    def evaluate(self, params: dict[str, float]) -> float:
        x = params["x"]
        return x**2

    @property
    def search_space(self) -> dict[str, optuna.distributions.BaseDistribution]:
        return {"x": optuna.distributions.FloatDistribution(low=-1, high=1)}

    @property
    def directions(self) -> list[optuna.study.StudyDirection]:
        return [optuna.study.StudyDirection.MINIMIZE]


def test_base_problem() -> None:
    problem = TestProblem()
    study = optuna.create_study(directions=problem.directions)
    study.optimize(problem, n_trials=20)  # verify no error occurs


def test_constrained_mixin() -> None:
    class ConstrainedTestProblem(optunahub.benchmarks.ConstrainedMixin, TestProblem):
        def evaluate_constraints(self, params: dict[str, float]) -> list[float]:
            return [params["x"]]

    problem = ConstrainedTestProblem()
    sampler = optuna.samplers.TPESampler(constraints_func=problem.constraints_func)
    study = optuna.create_study(sampler=sampler, directions=problem.directions)
    study.optimize(problem, n_trials=20)  # verify no error occurs

    # Check if constraints are stored in trials
    for t in study.trials:
        assert _CONSTRAINTS_KEY in study._storage.get_trial_system_attrs(t._trial_id)
