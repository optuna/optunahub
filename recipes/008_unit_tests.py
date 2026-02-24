"""
.. _unit_tests:

How to Implement Unit Tests using Optuna's Testing Module
===========================================================

Optuna provides a testing module, ``optuna.testing``, which includes general test cases for Optuna's samplers and storages.
In this tutorial, we will explain how to implement unit tests for your OptunaHub package using ``optuna.testing``.
Note that ``Optuna >= 4.8`` is required to use the testing module.

"""
###################################################################################################
# We prepare ``MySampler`` class again as an example to show how to implement unit tests for your package.
# For the implementation details of ``MySampler``, please refer to :doc:`001_first`.

from __future__ import annotations

from typing import Any
from typing import Callable

import numpy as np
import optuna

import optunahub


class MySampler(optunahub.samplers.SimpleBaseSampler):
    def __init__(
        self, search_space: dict[str, optuna.distributions.BaseDistribution] | None = None
    ) -> None:
        super().__init__(search_space)
        self._rng = np.random.RandomState()

    def sample_relative(
        self,
        study: optuna.study.Study,
        trial: optuna.trial.FrozenTrial,
        search_space: dict[str, optuna.distributions.BaseDistribution],
    ) -> dict[str, Any]:
        if search_space == {}:
            return {}

        params = {}  # type: dict[str, Any]
        for n, d in search_space.items():
            if isinstance(d, optuna.distributions.FloatDistribution):
                params[n] = self._rng.uniform(d.low, d.high)
            elif isinstance(d, optuna.distributions.IntDistribution):
                params[n] = self._rng.randint(d.low, d.high + 1)  # sample from [d.low, d.high + 1)
            elif isinstance(d, optuna.distributions.CategoricalDistribution):
                params[n] = d.choices[self._rng.randint(len(d.choices))]
            else:
                raise NotImplementedError
        return params


###################################################################################################
# Although here we define ``MySampler`` class above, usually the sampler class is defined in a separate file, and the test code is implemented in another file.
# For example, ``MySampler`` class is defined in ``my_sampler.py``, and the test code is implemented in ``tests/test_my_sampler.py``.
# In such case, you can import ``MySampler`` class in your local environment using :func:`optunahub.load_local_module` function as below.
#
# .. code-block:: python
#
#     from optunahub import load_local_module
#     MySampler = load_local_module("samplers/my_sampler").MySampler


###################################################################################################
# To implement unit tests for ``MySampler``, you can use the test cases provided in ``optuna.testing.pytest_samplers`` module.
# At the moment, this module provides the following test cases for samplers.
#
# - ``BasicSamplerTestCase``: provides basic test cases for samplers, such as sample float, int, and categorical parameters.
# - ``RelativeSamplerTestCase``: provides test cases for samplers that support relative sampling.
# - ``MultiObjectiveSamplerTestCase``: provides test cases for samplers that support multi-objective optimization.
# - ``SingleOnlySamplerTestCase``: provides test cases for samplers that only support single-objective optimization.
#
# Note that MultiObjectiveSamplerTestCase and SingleOnlySamplerTestCase is exclusive, so you can use either of them depending on the type of your sampler.
#
# Here, since ``MySampler`` supports relative sampling and multi-objective optimization, we define a test class that inherits ``BasicSamplerTestCase``, ``RelativeSamplerTestCase``, and ``MultiObjectiveSamplerTestCase`` as below.
# By overriding the ``sampler`` fixture, which is provided by the test case classes, ``MySampler`` is tested with all the test cases provided in the three test case classes.
# You can also implement your own test cases in addition to the provided test cases by defining additional test methods in the test class.
# Also, by overriding the test cases in the provided test case classes, you can customize the test cases as you like, e.g., disable tests for intentionally unsupported features.
# You can find more details about the provided test cases in the source code of `optuna.testing.pytest_samplers <https://github.com/optuna/optuna/blob/master/optuna/testing/pytest_samplers.py>`__ module.

# Suppress the warning E402: Module level import not at top of file in tutorials
# ruff: noqa: E402

from optuna.samplers import BaseSampler
from optuna.testing.pytest_samplers import BasicSamplerTestCase
from optuna.testing.pytest_samplers import MultiObjectiveSamplerTestCase
from optuna.testing.pytest_samplers import RelativeSamplerTestCase
import pytest


class TestMySampler(BasicSamplerTestCase, RelativeSamplerTestCase, MultiObjectiveSamplerTestCase):
    @pytest.fixture
    def sampler(self) -> Callable[[], BaseSampler]:
        return MySampler  # Return the sampler class to be tested.

    def test_user_defined_case(self) -> None:
        # You can also implement your own test cases in addition to the provided test cases.
        # This is an example of a user-defined test case.
        pass

    def test_nan_objective_value(self) -> None:
        # This is an example of overriding the provided test case to customize it.
        # By default, the provided test cases check if the sampler can handle NaN objective values.
        # If your sampler does not support NaN objective values, you can disable the test by overriding it like this.
        pass


###################################################################################################
# You can run the test with pytest as usual.
#
# .. code-block:: shell
#
#    pytest tests/test_my_sampler.py
#    ==================================================== test session starts =====================================================
#    platform darwin -- Python 3.13.5, pytest-8.4.1, pluggy-1.6.0
#    rootdir: ...
#    configfile: pyproject.toml
#    plugins: xdist-3.8.0, anyio-4.10.0, langsmith-0.4.42
#    collected 127 items
#    tests/test_my_sampler.py ............................................................................................ [ 72%]
#    ...................................                                                                                   [100%]
#    ==================================================== 127 passed in 0.59s =====================================================

###################################################################################################
# Proper unit tests go a long way to ensuring the quality of your package, and we strongly encourage you to add unit tests to your package before registering it.
