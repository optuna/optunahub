from typing import Any
from typing import Dict
from typing import Optional

import numpy as np
from optuna import Study
from optuna.distributions import BaseDistribution
from optuna.trial import FrozenTrial

import optunahub


class TestSampler(optunahub.samplers.SimpleBaseSampler):
    def __init__(self, search_space: Optional[Dict[str, BaseDistribution]] = None) -> None:
        super().__init__(search_space)
        self._rng = np.random.RandomState()

    def sample_relative(
        self,
        study: Study,
        trial: FrozenTrial,
        search_space: Dict[str, BaseDistribution],
    ) -> Dict[str, Any]:
        params = {}
        for n, d in search_space.items():
            params[n] = self._rng.uniform(d.low, d.high)
        return params
