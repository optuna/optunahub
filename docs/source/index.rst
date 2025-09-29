Welcome to OptunaHub's documentation!
=====================================

`OptunaHub <https://hub.optuna.org/>`__ is a platform for black-box optimization.
It hosts a registry of third-party packages designed for `Optuna <https://optuna.org>`__ and allows users to share and discover Optuna packages that are not included in the official Optuna distribution.
The `optunahub <https://github.com/optuna/optunahub/>`__ library provides Python APIs to load and use packages from the OptunaHub registry.
Please check out `Tutorials for Users <./tutorials_for_users/index.html>`__  as well.

**If you are interested in registering your own features in OptunaHub**, please visit `the optunahub-registry repository <https://github.com/optuna/optunahub-registry>`__ and submit a pull request there. More details are available in `Tutorials for Contributors <./tutorials_for_contributors.html>`__.


Usage
=====

Install the ``optunahub`` package.

From PyPI:

.. code-block:: shell

   pip install optunahub

From conda-forge:

.. code-block:: shell

   conda install -c conda-forge optunahub

Load the package you want from the OptunaHub registry. In the next example code, you will load the ``AutoSampler`` from the `samplers/auto_sampler <https://hub.optuna.org/samplers/auto_sampler/>`__ package.
The details for ``AutoSampler`` can be found in `this article <https://medium.com/optuna/autosampler-automatic-selection-of-optimization-algorithms-in-optuna-1443875fd8f9>`__.

.. code-block:: python

   import optuna
   import optunahub


   def objective(trial: optuna.Trial) -> float:
      x = trial.suggest_float("x", -5, 5)
      y = trial.suggest_float("y", -5, 5)

      return x**2 + y**2


   mod = optunahub.load_module("samplers/auto_sampler")

   study = optuna.create_study(sampler=mod.AutoSampler())
   study.optimize(objective, n_trials=10)

   print(study.best_trial.value, study.best_trial.params)


Now that you've successfully loaded a package from the OptunaHub registry, you can start using ``optunahub`` in your optimization!
Get ready to explore the most suitable packages for your problems in the `OptunaHub registry <https://hub.optuna.org/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference
   tutorials_for_users/index
   tutorials_for_contributors
   faq
