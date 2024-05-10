OptunaHub-Proto
==================

Python Library to use packages published in [OptunaHub Registry](https://github.com/optuna/optunahub-registry).

# Install

Install `optunahub` package.
```sh
pip install optunahub
```

# Documentation

- [OptunaHub documentation](https://optuna.github.io/optunahub/)


# Example

```python
import optunahub
import optuna


def objective(trial: optuna.Trial) -> float:
    x = trial.suggest_float("x", 0, 1)

    return x


if __name__ == "__main__":
    mod = optunahub.load("samplers/simulated_annealing")

    sampler = mod.SimulatedAnnealingSampler()
    study = optuna.create_study(sampler=sampler)
    study.optimize(objective, n_trials=20)

    print(study.best_trial.value, study.best_trial.params)

```
