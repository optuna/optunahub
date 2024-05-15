.. OptunaHub documentation master file, created by
   sphinx-quickstart on Tue Apr 16 12:13:49 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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


Reference
=========

.. automodule:: optunahub
   :members:
   :undoc-members:
   :show-inheritance:


Anonymous Analytics
===================

OptunaHub collects anonymous usage data to improve the service.
The data is used to understand how users interact with the service and to identify areas for improvement.

Youn can opt-out of the anonymous analytics in the following ways.

- By setting the environment variable `OPTUNAHUB_NO_ANALYTICS` to `1`
- By setting `no_analytics = false` in `config.toml`

.. code-block:: shell

      export OPTUNAHUB_NO_ANALYTICS=1


`config.toml`

.. code-block:: toml

      no_analytics = false

The settings are prioritized in the order listed above.

The configuration file (`config.toml`) of OptunaHub is placed in the following locations.

- (UNIX-like) `XDG_CONFIG_HOME/optunahub/config.toml`
- (Windows) `%APPDATA%/optunahub/config.toml`

`XDG_CONFIG_HOME` is usually `~/.config` on UNIX-like systems.


Package Cache
=============

OptunaHub caches the downloaded packages in the following locations.

- The directory defined by `OPTUNAHUB_CACHE_HOME` environment variable
- The `cache_home` value in `config.toml`
- (UNIX-like) `XDG_CACHE_HOME/optunahub`
- (Windows) `%LOCALAPPDATA%/optunahub`

The settings are prioritized in the order listed above.
`XDG_CACHE_HOME` is usually `~/.cache` on UNIX-like systems.


FAQ
===

- Q. How can I update an OptunaHub package already cached?

   - A. Calling `optunahub.load_module()` with `force_reload=True` ensures the selected package is re-download from the package registry.
