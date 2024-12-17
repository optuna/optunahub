from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import optuna


class ConstrainedMixin:
    """Mixin class for constrained optimization problems.

    Example:
        You can define a constrained optimization problem by inheriting this class and implementing
        the :meth:`evaluate_constraints` method as follows.

        ::

            import optuna
            import optunahub

            class BinAndKorn(optunahub.benchmarks.ConstrainedMixin, optunahub.benchmarks.BaseProblem):
                def evaluate(self, params: dict[str, float]) -> tuple[float]:
                    x = params["x"]
                    y = params["y"]

                    v0 = 4 * x**2 + 4 * y**2
                    v1 = (x - 5)**2 + (y - 5)**2

                    return v0, v1

                def evaluate_constraints(self, params: dict[str, float]) -> tuple[float]:
                    x = params["x"]
                    y = params["y"]

                    # Constraints which are considered feasible if less than or equal to zero.
                    # The feasible region is basically the intersection of a circle centered at (x=5, y=0)
                    # and the complement to a circle centered at (x=8, y=-3).
                    c0 = (x - 5)**2 + y**2 - 25
                    c1 = -((x - 8)**2) - (y + 3)**2 + 7.7

                    return c0, c1

                @property
                def search_space(self) -> dict[str, optuna.distributions.BaseDistribution]:
                    return {
                        "x": optuna.distributions.FloatDistribution(low=-15, high=30),
                        "y": optuna.distributions.FloatDistribution(low=-15, high=30)
                    }

                @property
                def directions(self) -> list[optuna.study.StudyDirection]:
                    return [optuna.study.StudyDirection.MINIMIZE, optuna.study.StudyDirection.MINIMIZE]

            problem = BinAndKorn()
            sampler = optuna.samplers.TPESampler(constraints_func=problem.constraints_func)
            study = optuna.create_study(sampler=sampler, directions=problem.directions)
            study.optimize(problem, n_trials=20)
    """

    def constraints_func(self, trial: optuna.trial.FrozenTrial) -> Sequence[float]:
        """Evaluate the constraint functions.

        Args:
            trial: Optuna trial object.
        Returns:
            List of the constraint values.
        """
        return self.evaluate_constraints(trial.params.copy())

    def evaluate_constraints(self, params: dict[str, Any]) -> Sequence[float]:
        """Evaluate the constraint functions.

        Args:
            params: Dictionary of input parameters.
        Returns:
            List of the constraint values.
        """
        raise NotImplementedError
