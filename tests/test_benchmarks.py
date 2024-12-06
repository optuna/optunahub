from __future__ import annotations

import optuna

import optunahub


def test_base_problem() -> None:
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

    problem = TestProblem()
    study = optuna.create_study()
    study.optimize(problem, n_trials=20)  # verify no error occurs
