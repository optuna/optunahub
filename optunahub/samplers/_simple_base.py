from __future__ import annotations

import abc
from typing import Any

from optuna import Study
from optuna.distributions import BaseDistribution
from optuna.samplers import BaseSampler
from optuna.samplers import RandomSampler
from optuna.search_space import IntersectionSearchSpace
from optuna.trial import FrozenTrial


class SimpleBaseSampler(BaseSampler, abc.ABC):
    """A simple base class to implement user-defined samplers."""

    def __init__(
        self, search_space: dict[str, BaseDistribution] | None = None, seed: int | None = None
    ) -> None:
        self.search_space = search_space
        self._seed = seed
        self._init_defaults()

    def infer_relative_search_space(
        self,
        study: Study,
        trial: FrozenTrial,
    ) -> dict[str, BaseDistribution]:
        # This method is optional.
        # If you want to optimize the function with the eager search space,
        # please implement this method.
        if self.search_space is not None:
            return self.search_space
        return self._default_infer_relative_search_space(study, trial)

    @abc.abstractmethod
    def sample_relative(
        self,
        study: Study,
        trial: FrozenTrial,
        search_space: dict[str, BaseDistribution],
    ) -> dict[str, Any]:
        # This method is required.
        # This method is called at the beginning of each trial in Optuna to sample parameters.
        raise NotImplementedError

    def sample_independent(
        self,
        study: Study,
        trial: FrozenTrial,
        param_name: str,
        param_distribution: BaseDistribution,
    ) -> Any:
        # This method is optional.
        # By default, parameter values are sampled by ``optuna.samplers.RandomSampler``.
        return self._default_sample_independent(study, trial, param_name, param_distribution)

    def reseed_rng(self) -> None:
        self._default_reseed_rng()

    def _init_defaults(self) -> None:
        self._intersection_search_space = IntersectionSearchSpace()
        self._random_sampler = RandomSampler(seed=self._seed)

    def _default_infer_relative_search_space(
        self, study: Study, trial: FrozenTrial
    ) -> dict[str, BaseDistribution]:
        search_space: dict[str, BaseDistribution] = {}
        for name, distribution in self._intersection_search_space.calculate(study).items():
            if distribution.single():
                # Single value objects are not sampled with the `sample_relative` method,
                # but with the `sample_independent` method.
                continue
            search_space[name] = distribution
        return search_space

    def _default_sample_independent(
        self,
        study: Study,
        trial: FrozenTrial,
        param_name: str,
        param_distribution: BaseDistribution,
    ) -> Any:
        # Following parameters are randomly sampled here.
        # 1. A parameter in the initial population/first generation.
        # 2. A parameter to mutate.
        # 3. A parameter excluded from the intersection search space.

        return self._random_sampler.sample_independent(
            study, trial, param_name, param_distribution
        )

    def _default_reseed_rng(self) -> None:
        self._random_sampler.reseed_rng()
