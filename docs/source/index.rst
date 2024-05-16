Welcome to OptunaHub's documentation!
=====================================

OptunaHub is a registry of third-party Optuna packages.
It allows users to share and discover Optuna packages that are not included in the official Optuna distribution.
The `optunahub <https://github.com/optuna/optunahub/>`_ library provides Python APIs to load and use packages from the OptunaHub registry.


Usage
=====

Install the `optunahub` package.

.. code-block:: shell

      pip install optunahub

Load the package you want from the OptunaHub registry as follows.

.. code-block:: python

   import optunahub
   import optuna


   def objective(trial: optuna.Trial) -> float:
      x = trial.suggest_float("x", 0, 1)

      return x


   if __name__ == "__main__":
      mod = optunahub.load_module("samplers/simulated_annealing")

      sampler = mod.SimulatedAnnealingSampler()
      study = optuna.create_study(sampler=sampler)
      study.optimize(objective, n_trials=20)

      print(study.best_trial.value, study.best_trial.params)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   faq
