OptunaHub
==================

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![pypi](https://img.shields.io/pypi/v/optunahub.svg)](https://pypi.python.org/pypi/optunahub)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/optuna/optunahub)
[![Codecov](https://codecov.io/gh/optuna/optunahub/branch/main/graph/badge.svg)](https://codecov.io/gh/optuna/optunahub)


Python Library to use packages published in [OptunaHub](https://hub.optuna.org/).
If you would like to register your package in OptunaHub, please contribute by creating a pull request to [the optunahub-registry repository](https://github.com/optuna/optunahub-registry).

# Install

Install `optunahub` package.
```sh
pip install optunahub
```

# Documentation

- [OptunaHub documentation](https://optuna.github.io/optunahub/)


# Example

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
