![OptunaHub](https://github.com/user-attachments/assets/c5a53304-8f62-4c26-8464-9b338dd3ad97)
OptunaHub: Feature-sharing platform for Optuna
==================

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/optunahub.svg)](https://pypi.python.org/pypi/optunahub)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/optuna/optunahub)
[![Codecov](https://codecov.io/gh/optuna/optunahub/branch/main/graph/badge.svg)](https://codecov.io/gh/optuna/optunahub)


:link: [**Website**](https://hub.optuna.org/)
| :page_with_curl: [**Docs**](https://optuna.github.io/optunahub/)
| [**Twitter**](https://twitter.com/OptunaAutoML)
| [**LinkedIn**](https://www.linkedin.com/showcase/optuna/)
| [**Medium**](https://medium.com/optuna)


[*OptunaHub*](https://hub.optuna.org/) is a platform for sharing algorithms in [Optuna](https://optuna.org/), a powerful and flexible hyperparameter optimization framework. OptunaHub provides implementations of state-of-the-art optimization algorithms and visualization of optimization results for analysis. You can also publish your algorithm implementation on the platform and make it available to Optuna users around the world.


This is the repository of the optunahub Python Library to use packages published in [OptunaHub](https://hub.optuna.org/). If you would like to register your package in OptunaHub, please contribute by creating a pull request to [the optunahub-registry repository](https://github.com/optuna/optunahub-registry).


## :loudspeaker: News

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
    x = trial.suggest_float("x", 0, 1)

    return x


mod = optunahub.load_module("samplers/simulated_annealing")
study = optuna.create_study(sampler=mod.SimulatedAnnealingSampler())
study.optimize(objective, n_trials=20)

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
