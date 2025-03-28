"""
.. _first:

How to Implement Your Sampler with OptunaHub
===========================================================

OptunaHub is an Optuna package registry, which is a platform to share algorithms developed by contributors.
This recipe shows how to implement your own algorithm with OptunaHub.

Here, we show how to implement your own sampler, i.e., optimizaiton algorithm.
If you want to implement algorithms other than a sampler, please refer to the other recipes.

- :doc:`003_pruner`
- :doc:`004_visualization`

Usually, Optuna provides ``BaseSampler`` class to implement your own sampler.
However, it is a bit complicated to implement a sampler from scratch.
Instead, in OptunaHub, you can use `optunahub.samplers.SimpleBaseSampler <https://optuna.github.io/optunahub/generated/optunahub.samplers.SimpleBaseSampler.html>`__ class, which is a sampler template that can be easily extended.

You need to install ``optuna`` to implement your own sampler, and ``optunahub`` to use the template ``SimpleBaseSampler``.

.. code-block:: bash

    $ pip install optuna optunahub

"""

###################################################################################################
# First of all, import ``optuna``, ``optunahub``, and other required modules.
from __future__ import annotations

from typing import Any

import numpy as np
import optuna
import optunahub


###################################################################################################
# Next, define your own sampler class by inheriting ``SimpleBaseSampler`` class.
# In this example, we implement a sampler that returns a random value.


class MySampler(optunahub.samplers.SimpleBaseSampler):
    # By default, search space will be estimated automatically like Optuna's built-in samplers.
    # You can fix the search spacd by `search_space` argument of `SimpleSampler` class.
    def __init__(
        self, search_space: dict[str, optuna.distributions.BaseDistribution] | None = None
    ) -> None:
        super().__init__(search_space)
        self._rng = np.random.RandomState()

    # You need to implement sample_relative method.
    # This method returns a dictionary of hyperparameters.
    # The keys of the dictionary are the names of the hyperparameters, which must be the same as the keys of the search_space argument.
    # The values of the dictionary are the values of the hyperparameters.
    # In this example, sample_relative method returns a dictionary of randomly sampled hyperparameters.
    def sample_relative(
        self,
        study: optuna.study.Study,
        trial: optuna.trial.FrozenTrial,
        search_space: dict[str, optuna.distributions.BaseDistribution],
    ) -> dict[str, Any]:
        # search_space argument must be identical to search_space argument input to __init__ method.
        # This method is automatically invoked by Optuna and SimpleBaseSampler.

        # If search space is empty, all parameter values are sampled randomly by SimpleBaseSampler.
        if search_space == {}:
            return {}

        params = {}  # type: dict[str, Any]
        for n, d in search_space.items():
            if isinstance(d, optuna.distributions.FloatDistribution):
                params[n] = self._rng.uniform(d.low, d.high)
            elif isinstance(d, optuna.distributions.IntDistribution):
                params[n] = self._rng.randint(d.low, d.high)
            elif isinstance(d, optuna.distributions.CategoricalDistribution):
                params[n] = d.choices[self._rng.randint(len(d.choices))]
            else:
                raise NotImplementedError
        return params


###################################################################################################
# Here, as an example, the objective function is defined as follows.


def objective(trial: optuna.trial.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", -10, 10)
    z = trial.suggest_categorical("z", ["a", "b", "c"])
    return x**2 + y**2 + {"a": -10, "b": 0, "c": 10}[z] ** 2


###################################################################################################
# This sampler can be used in the same way as other Optuna samplers.
# In the following example, we create a study and optimize it using ``MySampler`` class.
sampler = MySampler()
study = optuna.create_study(sampler=sampler)
study.optimize(objective, n_trials=100)

###################################################################################################
# The best parameters can be fetched as follows.

best_params = study.best_params
best_value = study.best_value
print(f"Best params: {best_params}, Best value: {best_value}")

###################################################################################################
# We can see that ``best_params`` value found by Optuna is close to the optimal value ``{"x":0, "y": 0, "z": "b"}``.

###################################################################################################
# In the above examples, search space is estimated at the first trial and updated dynamically through optimization.
# If your sampler requires the search space to be fixed before optimization, you can pass the search space to the sampler at initialization.
# Passing the search space also allows the sampler to avoid the overhead of estimating the search space.
# See `the documentation <https://optuna.readthedocs.io/en/stable/reference/distributions.html>`__ for more information about the ``optuna.distributions`` to define search space.
sampler = MySampler(
    search_space={
        "x": optuna.distributions.FloatDistribution(-10, 10),
        "y": optuna.distributions.IntDistribution(-10, 10),
        "z": optuna.distributions.CategoricalDistribution(["a", "b", "c"]),
    }
)
study = optuna.create_study(sampler=sampler)
study.optimize(objective, n_trials=100)

###################################################################################################
# In the next recipe, we will show how to register your sampler to OptunaHub.
# Let's move on to :doc:`002_registration`.
# See `the User-Defined Sampler documentation <https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/005_user_defined_sampler.html>`_ for more information to implement a sampler.
