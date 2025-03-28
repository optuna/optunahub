"""
.. _benchmarks_advanced:

How to Implement Your Benchmark Problems with OptunaHub (Advanced)
==================================================================

OptunaHub provides the ``optunahub.benchmarks`` module for implementing benchmark problems.
In this tutorial, we will explain how to implement complex benchmark problems such as a problem with dynamic search space using ``optunahub.benchmarks``.

For the implementation of simple benchmark problems, please refer to :ref:`benchmarks_basic`.
"""

###################################################################################################
# Implementing a Problem with Dynamic Search Space
# -------------------------------------------------
#
# Here, let's implement a problem with a dynamic search space.
#
# First of all, import `optuna` and other required modules.
from __future__ import annotations

import optuna
from optunahub.benchmarks import BaseProblem
from optunahub.benchmarks import ConstrainedMixin


###################################################################################################
# Next, define your own problem class by inheriting ``BaseProblem`` class.
# To implement a problem with a dynamic search space, ``__call__(self, trial: optuna.Trial)`` method must be overridden so that we can define a dynamic search space in the define-by-run manner.
# Please note that ``direcitons`` property must also be implemented.
class DynamicProblem(BaseProblem):
    def __call__(self, trial: optuna.Trial) -> float:
        x = trial.suggest_float("x", -5, 5)
        if x < 0:
            # Parameter `y` exists only when `x` is negative.
            y = trial.suggest_float("y", -5, 5)
            return x**2 + y
        else:
            return x**2

    @property
    def directions(self) -> list[optuna.study.StudyDirection]:
        return [optuna.study.StudyDirection.MINIMIZE]

    @property
    def search_space(self) -> dict[str, optuna.distributions.BaseDistribution]:
        # You can implement this property as you like, or leave it unimplemented (``BaseProblem`` provides this default behavior).
        raise NotImplementedError

    def evaluate(self, params: dict[str, float]) -> float:
        # You can implement this method as you like, or leave it unimplemented (``BaseProblem`` provides this default behavior).
        raise NotImplementedError


###################################################################################################
# The implementations of the ``search_space`` and ``evaluate`` are non-trivial when the search space is dynamic.
# However, since ``__call__(self, trial: optuna.Trial)`` does not have to depend on both the ``evaluate`` method and the ``search_space`` attribute internally, their implementations are up to users.
# If possible, you could provide their implementations, but this is not necessary to make your benchmark problem work.
# Please note that calling them will result in ``NotImplementedError`` if you leave them unimplemented.

###################################################################################################
# Then, you can optimize the problem with Optuna as usual.
dynamic_problem = DynamicProblem()
study = optuna.create_study(directions=dynamic_problem.directions)
study.optimize(dynamic_problem, n_trials=20)


###################################################################################################
# Implementing a problem with constraints
# -------------------------------------------------
# Here, let's implement a problem with constraints.
# To implement a problem with constraints, you need to inherit ``ConstrainedMixin`` class in addition to ``BaseProblem`` and implement the ``evaluate_constraints`` method.
# The ``evaluate_constraints`` method evaluates the constraint functions given a dictionary of input parameters and returns a list of constraint values.
# Then, ``ConstrainedMixin`` internally defines the ``constraints_func`` method for Optuna samplers.
class ConstrainedProblem(ConstrainedMixin, DynamicProblem):
    def evaluate_constraints(self, params: dict[str, float]) -> tuple[float, float]:
        x = params["x"]
        c0 = x - 2
        if "y" not in params:
            c1 = 0.0  # c1 <= 0, so c1 is satisfied in this case.
            return c0, c1
        else:
            y = params["y"]
            c1 = x + y - 3
            return c0, c1


###################################################################################################
# Then, you can optimize the problem with Optuna as usual.
# Don't forget to set the `constraints_func` argument to the sampler to use.
problem = ConstrainedProblem()
sampler = optuna.samplers.TPESampler(
    constraints_func=problem.constraints_func
)  # Pass the constraints_func to the sampler.
study = optuna.create_study(sampler=sampler, directions=problem.directions)
study.optimize(problem, n_trials=20)

###################################################################################################
# After implementing your own benchmark problem, you can register it with OptunaHub.
# See :doc:`002_registration` for how to register your benchmark problem with OptunaHub.
