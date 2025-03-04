OptunaHub: Feature-sharing platform for Optuna
==================

![OptunaHub](https://github.com/user-attachments/assets/ee24b6eb-a431-4e02-ae52-c2538ffe01ee)

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/optunahub.svg)](https://pypi.python.org/pypi/optunahub)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/optuna/optunahub)
[![Codecov](https://codecov.io/gh/optuna/optunahub/branch/main/graph/badge.svg)](https://codecov.io/gh/optuna/optunahub)


:link: [**OptunaHub**](https://hub.optuna.org/)
| :page_with_curl: [**Docs**](https://optuna.github.io/optunahub/)
| :book: [**Tutorials**](https://optuna.org/)
| :question: [**FAQ**](https://optuna.org/)
| [**Optuna.org**](https://optuna.org/)

[*OptunaHub*](https://hub.optuna.org/) is a platform for sharing algorithms in [Optuna](https://optuna.org/), a powerful and flexible hyperparameter optimization framework. OptunaHub provides implementations of state-of-the-art optimization algorithms and visualization of optimization results for analysis. You can also publish your algorithm implementation on the platform and make it available to Optuna users around the world.


This is the repository of the optunahub Python Library to use packages published in [OptunaHub](https://hub.optuna.org/). If you would like to register your package in OptunaHub, please contribute by creating a pull request to [the optunahub-registry repository](https://github.com/optuna/optunahub-registry).

## :loudspeaker: News

* **Nov 6, 2024**: A new article [AutoSampler: Automatic Selection of Optimization Algorithms in Optuna](https://medium.com/optuna/autosampler-automatic-selection-of-optimization-algorithms-in-optuna-1443875fd8f9) has been published.
* **Oct 21, 2024**: We posted [an article](https://medium.com/optuna/an-introduction-to-moea-d-and-examples-of-multi-objective-optimization-comparisons-8630565a4e89) introducing [MOEA/D](https://hub.optuna.org/samplers/moead/) and an example comparison with other optimization methods.
* **Aug 30, 2024**: New Medium article "[OptunaHub, a Feature-Sharing Platform for Optuna, Now Available in Official Release!](https://medium.com/optuna/optunahub-a-feature-sharing-platform-for-optuna-now-available-in-official-release-4b99efe9934d)" was published!
* **Jul 16, 2024**: We posted an article [Announcing OptunaHub 0.1.0-β](https://medium.com/optuna/announcing-optunahub-0-1-0-%CE%B2-69b35bb3e95e) that describes what is, how to use, and how to contribute to OptunaHub.

## Installation

Optuna is available at [the Python Package Index](https://pypi.org/project/optunahub/).

```sh
pip install optunahub
```

## Example

You only need to search for the desired function on [the OptunaHub website](https://hub.optuna.org/) and call the [optunahub.load_module](https://optuna.github.io/optunahub/) function in your code to incorporate it.

```python
import optuna
import optunahub


def objective(trial: optuna.Trial) -> float:
  x = trial.suggest_float("x", -5, 5)
  y = trial.suggest_float("y", -5, 5)
  return x**2 + y**2


module = optunahub.load_module(package="samplers/auto_sampler")
study = optuna.create_study(sampler=module.AutoSampler())
study.optimize(objective, n_trials=10)

print(study.best_trial.value, study.best_trial.params)
```

## Contribution

Any contributions to OptunaHub are more than welcome!

OptunaHub is composed of the following three related repositories. Please contribute to the appropriate repository for your purposes.
- [optunahub](https://github.com/optuna/optunahub) (*this repository*)
    - The python library to use OptunaHub. If you find issues and/or bugs in the optunahub library, please report it here via [Github issues](https://github.com/optuna/optunahub/issues).
- [optunahub-registry](https://github.com/optuna/optunahub-registry/)
    - The registry of the OptunaHub packages. If you are interested in registering your package with OptunaHub, please contribute to this repository. For general guidelines on how to contribute to the repository, take a look at [CONTRIBUTING.md](https://github.com/optuna/optunahub-registry/blob/main/CONTRIBUTING.md).
- [optunahub-web](https://github.com/optuna/optunahub-web/)
    - The web frontend for OptunaHub. If you find issues and/or bugs on the website, please report it here via [GitHub issues](https://github.com/optuna/optunahub-web/issues).

## License

MIT License (see [LICENSE](https://github.com/optuna/optunahub/blob/main/LICENSE)).
