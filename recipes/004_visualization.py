"""
.. _visualization:

How to Implement Your Own Visualization Function
===========================================================

In this section, we show how to implement your own visualization function.
Here, we implement a visualization function that plots the optimization history.

"""
###################################################################################################
# First of all, import `optuna` and other required modules.

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import optuna
import plotly.graph_objects as go


###################################################################################################
# If you use `plotly <https://plotly.com/python/>`__ for visualization, the function should return a ``plotly.graph_objects.Figure`` object.


def plot_optimizaiton_history(study: optuna.study.Study) -> go.Figure:
    trials = study.trials
    values = [trial.value for trial in trials]
    best_values = [min(values[: i + 1]) for i in range(len(values))]  # type: ignore
    iterations = list(range(len(trials)))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=best_values,
            mode="lines+markers",
        )
    )
    fig.update_layout(title="Optimization history")
    return fig


###################################################################################################
# If you use `matplotlib <https://matplotlib.org/>`__ for visualization, the function should return a ``matplotlib.figure.Figure`` object.


def plot_optimizaiton_history_matplotlib(study: optuna.study.Study) -> matplotlib.figure.Figure:
    trials = study.trials
    values = [trial.value for trial in trials]
    best_values = [min(values[: i + 1]) for i in range(len(values))]  # type: ignore

    fig, ax = plt.subplots()
    ax.set_title("Optimization history")
    ax.plot(best_values, marker="o")
    return fig


###################################################################################################
# Plot the optimization history using the implemented visualization function.
# Here, we use the simple quadratic function as objective function.


def objective(trial: optuna.trial.Trial) -> float:
    x = trial.suggest_float("x", -10, 10)
    return x**2


study = optuna.create_study()
study.optimize(objective, n_trials=100)

fig = plot_optimizaiton_history(study)
fig.show()  # plt.show() for matplotlib


###################################################################################################
# After implementing your own visualization function, you can register it with OptunaHub.
# See :doc:`002_registration` for how to register your visualization function with OptunaHub.
