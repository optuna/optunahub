Welcome to OptunaHub's documentation!
=====================================

`OptunaHub <https://hub.optuna.org/>`__ is a platform for black-box optimization.
It hosts a registry of third-party packages designed for `Optuna <https://optuna.org>`__, allowing users to share and discover Optuna packages that are not included in the official Optuna distribution.
The `optunahub <https://github.com/optuna/optunahub/>`__ library provides Python APIs to load and use packages from the OptunaHub registry.
Please check out :doc:`Tutorials for Users </tutorials_for_users/index>`  as well.

**If you are interested in registering your own features in OptunaHub**, please visit `the optunahub-registry repository <https://github.com/optuna/optunahub-registry>`__ and submit a pull request there. More details are available in :doc:`Tutorials for Contributors </tutorials_for_contributors>`.


Getting Started
===============

Learn Optuna Fundamentals
-------------------------

Are you already familiar with Optuna? If so, you can skip this section.
If not, let's learn about the concept and basic usage of Optuna first, since OptunaHub is built on top of Optuna.

To get started with OptunaHub, you should at least know the concepts of ``Study``, ``Trial``, how to specify a sampler, how to define search space in a dynamic manner, and how to run optimization with Optuna.
The following resources are available to learn Optuna. Note that these are external links to :doc:`the official Optuna documentation <optuna:index>`.

- :doc:`Install Optuna <optuna:installation>`
- :doc:`optuna:tutorial/10_key_features/001_first`
- :doc:`optuna:tutorial/10_key_features/002_configurations`
- :doc:`optuna:tutorial/10_key_features/003_efficient_optimization_algorithms`


:doc:`The Optuna official tutorial <optuna:tutorial/index>` provides more detailed lectures for learning Optuna, so please check it out if you want to learn more about Optuna.


Basic Usage of OptunaHub
------------------------

Let's learn how to use the OptunaHub library.

First, please install the ``optunahub`` package.

From PyPI:

.. code-block:: shell

   pip install optunahub

From conda-forge:

.. code-block:: shell

   conda install -c conda-forge optunahub

Then, load the package you want from the OptunaHub registry. In the next example code, you will load the ``AutoSampler`` from the `samplers/auto_sampler <https://hub.optuna.org/samplers/auto_sampler/>`__ package.
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

Learn More about OptunaHub
==========================

Learn more about OptunaHub through the following contents.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference
   tutorials_for_users/index
   tutorials_for_contributors
   faq

Reference
=========


Please cite `the OptunaHub paper <https://doi.org/10.48550/arXiv.2510.02798>`__ with the following format when you use it in your project:

.. code-block:: bibtex

   @article{ozaki2025optunahub,
      title={{OptunaHub}: A Platform for Black-Box Optimization},
      author={Ozaki, Yoshihiko and Watanabe, Shuhei and Yanase, Toshihiko},
      journal={arXiv preprint arXiv:2510.02798},
      year={2025}
   }
