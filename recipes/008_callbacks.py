"""
.. _callbacks:

How to Implement Your Callback with OptunaHub
=============================================

This recipe shows how to implement and register your own callback with OptunaHub.

Callbacks are used when you want to insert custom processing **after each trial completes**.
Typical use cases include:

- Uploading the current best result to an external server (e.g., W&B, MLflow).
- Sending a notification when a new best value is found.
- Stopping the study early based on custom criteria by calling :meth:`~optuna.Study.stop`.

A callback is simply a callable with the following signature:

.. code-block:: python

    def callback(study: optuna.Study, trial: optuna.trial.FrozenTrial) -> None:
        ...

Optuna calls each registered callback once per trial, after the objective function
returns and the trial state has been recorded.
At that point :class:`~optuna.Study` already reflects the updated best value / best params,
and ``trial`` is a :class:`~optuna.trial.FrozenTrial` (immutable).

The simplest way to implement a callback is to define a plain function:
"""

from __future__ import annotations

import optuna


def my_callback(study: optuna.Study, trial: optuna.trial.FrozenTrial) -> None:
    print(f"Trial {trial.number} finished.")
    print(f"  params     : {trial.params}")
    print(f"  value      : {trial.value}")
    if trial.state == optuna.trial.TrialState.COMPLETE:
        print(f"  best_value : {study.best_value}")


###################################################################################################
# If your callback needs to hold internal state (e.g., a connection to an external service),
# you can implement it as a class with a ``__call__`` method instead.


class MyCallback:
    """A callback that prints trial information after each completed trial.

    Args:
        verbose: If ``True``, also print the full ``params`` dict.
    """

    def __init__(self, verbose: bool = True) -> None:
        self._verbose = verbose

    def __call__(self, study: optuna.Study, trial: optuna.trial.FrozenTrial) -> None:
        # This method is called after every trial regardless of its state.
        if trial.state != optuna.trial.TrialState.COMPLETE:
            return

        print(f"Trial {trial.number} finished.")
        if self._verbose:
            print(f"  params     : {trial.params}")
        print(f"  value      : {trial.value}")
        print(f"  best_value : {study.best_value}")


###################################################################################################
# The callback is passed to :meth:`~optuna.Study.optimize` via the ``callbacks`` argument.
# Multiple callbacks can be specified as a list; they are called in order after each trial.


def objective(trial: optuna.trial.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_int("y", -5, 5)
    return x**2 + y**2


###################################################################################################
# Run the study with a plain function callback.
study = optuna.create_study()
study.optimize(objective, n_trials=5, callbacks=[my_callback])

###################################################################################################
# Run another study with the class-based callback.
study = optuna.create_study()
study.optimize(objective, n_trials=5, callbacks=[MyCallback(verbose=True)])

###################################################################################################
# After implementing your own callback, you can register it with OptunaHub.
# See :doc:`002_registration` for how to register your callback with OptunaHub.
# The category name to use when placing your package in the registry is ``callbacks``:
