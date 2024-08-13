Welcome to OptunaHub's documentation!
=====================================

`OptunaHub <https://hub.optuna.org/>`__ is a registry of third-party packages designed for `Optuna <https://optuna.org>`__.
It allows users to share and discover Optuna packages that are not included in the official Optuna distribution.
The `optunahub <https://github.com/optuna/optunahub/>`_ library provides Python APIs to load and use packages from the OptunaHub registry.


Usage
=====

Install the `optunahub`_ package.

.. code-block:: shell

      pip install optunahub

Load the package you want from the OptunaHub registry. In the next example code, you will load the ``SimulatedAnnealingSampler`` from the `samplers/simulated_annealing <https://hub.optuna.org/samplers/simulated_annealing/>`__ package.

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


Now that you've successfully loaded a package from the OptunaHub registry, you can start using `optunahub`_ in your optimization!
Get ready to explore the most suitable packages for your problems in the `OptunaHub registry <https://hub.optuna.org/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference
   faq
