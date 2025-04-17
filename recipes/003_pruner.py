"""
.. _pruner:

How to Implement Your Pruners with OptunaHub
=========================================================

OptunaHub supports Optuna's pruners as well as samplers and visualization functions.
This recipe shows how to implement and register your own pruner with OptunaHub.

Usually, Optuna provides ``BasePruner`` class to implement your own sampler.
You can implement your own pruner by inheriting this class.
You need to install ``optuna`` to implement your own pruner.

.. code-block:: bash

    $ pip install optuna

"""

###################################################################################################
# First of all, import `optuna` and other required modules.
from __future__ import annotations

import optuna
from optuna.pruners import BasePruner


###################################################################################################
# Next, define your own pruner class by inheriting ``BasePruner`` class.
# In this example, we implement a pruner that stops objective functions based on a given threshold.
class MyPruner(BasePruner):  # type: ignore
    def __init__(self, upper_threshold: float, n_warmup_steps: int) -> None:
        self._upper_threshold = upper_threshold
        self._n_warmup_steps = n_warmup_steps

    # You need to implement `prune` method.
    # This method returns true if it stops objective function, otherwise false.
    # It stops the objective function if the intermediate value exceeds the threshold.
    # Note that first `n_warmup_steps` steps are not pruned.
    def prune(
        self,
        study: optuna.study.Study,
        trial: optuna.trial.FrozenTrial,
    ) -> bool:
        step = trial.last_step
        if step is None:
            return False

        if step < self._n_warmup_steps:
            return False

        if trial.intermediate_values[step] > self._upper_threshold:
            return True

        return False


###################################################################################################
# In this example, the objective function is a simple quadratic function.
# It has 20 variables and the sum of the squares of these variables is returned.


def objective(trial: optuna.trial.Trial) -> float:
    s = 0.0
    for step in range(20):
        x = trial.suggest_float(f"x_{step}", -5, 5)
        s += x**2
        trial.report(s, step)
        if trial.should_prune():
            raise optuna.TrialPruned()
    return s


###################################################################################################
# This pruner can be used in the same way as other Optuna pruners.
# In the following example, we create a study and optimize it using ``MyPruner`` class.
pruner = MyPruner(upper_threshold=100, n_warmup_steps=5)
study = optuna.create_study(pruner=pruner)
study.optimize(objective, n_trials=100)

###################################################################################################
# After implementing your own pruner, you can register it with OptunaHub.
# See :doc:`002_registration` for how to register your pruner with OptunaHub.
# See `the User-Defined Pruner documentation <https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/006_user_defined_pruner.html>`_ for more information to implement an pruner.
