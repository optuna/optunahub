from __future__ import annotations

from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Sequence

import optuna


class BaseProblem(metaclass=ABCMeta):
    """Base class for optimization problems."""

    def __call__(self, trial: optuna.Trial) -> float | Sequence[float]:
        """Objective function for Optuna. By default, this method calls :meth:`evaluate` with the parameters defined in :attr:`search_space`.

        Args:
            trial: Optuna trial object.
        Returns:
            The objective value or a sequence of the objective values for multi-objective optimization.
        """
        params = {}
        for name, dist in self.search_space.items():
            params[name] = trial._suggest(name, dist)
            trial._check_distribution(name, dist)
        return self.evaluate(params)

    def evaluate(self, params: dict[str, Any]) -> float | Sequence[float]:
        """Evaluate the objective function.

        Args:
            params: Dictionary of input parameters.

        Returns:
            The objective value or a sequence of the objective values for multi-objective optimization.

        Example:
            ::

                def evaluate(self, params: dict[str, Any]) -> float:
                    x = params["x"]
                    y = params["y"]
                    return x ** 2 + y
        """
        raise NotImplementedError

    @property
    def search_space(self) -> dict[str, optuna.distributions.BaseDistribution]:
        """Return the search space.

        Returns:
            Dictionary of search space. Each dictionary element consists of the parameter name and distribution (see `optuna.distributions <https://optuna.readthedocs.io/en/stable/reference/distributions.html>`__).

        Example:
            ::

                @property
                def search_space(self) -> dict[str, optuna.distributions.BaseDistribution]:
                    return {
                        "x": optuna.distributions.FloatDistribution(low=0, high=1),
                        "y": optuna.distributions.CategoricalDistribution(choices=[0, 1, 2]),
                    }
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def directions(self) -> list[optuna.study.StudyDirection]:
        """Return the optimization directions.

        Returns:
            List of `optuna.study.StudyDirection <https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.StudyDirection.html>`__.

        Example:
            ::

                @property
                def directions(self) -> list[optuna.study.StudyDirection]:
                    return [optuna.study.StudyDirection.MINIMIZE]
        """
        ...
