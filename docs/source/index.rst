Welcome to OptunaHub's documentation!
=====================================

`OptunaHub <https://hub.optuna.org/>`__ is a registry of third-party Optuna packages.
It allows users to share and discover Optuna packages that are not included in the official Optuna distribution.
The `optunahub <https://github.com/optuna/optunahub/>`_ library provides Python APIs to load and use packages from the OptunaHub registry.


Usage
=====

Install the `optunahub`_ package.

.. code-block:: shell

      pip install optunahub

Load the package you want from the OptunaHub registry as follows.

.. code-block:: python

   import optuna
   import optunahub


   def objective(trial: optuna.Trial) -> float:
      x = trial.suggest_float("x", 0, 1)

      return x


   mod = optunahub.load_module("samplers/simulated_annealing")

   study = optuna.create_study(sampler=mod.SimulatedAnnealingSampler())
   study.optimize(objective, n_trials=20)

   print(study.best_trial.value, study.best_trial.params)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference
   faq
