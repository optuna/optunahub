"""
.. _debugging:

How to Debug Your Algorithm Before Registering in OptunaHub
===========================================================

This recipe shows how to debug your package before registering it in OptunaHub.


Load Your Package from Local Directory
-----------------------------------------------------------

First, you can use the `optunahub.load_local_module <https://optuna.github.io/optunahub/reference.html#optunahub.load_local_module>`__ function to load your package from your local directory and check if it works correctly.

.. code-block:: python

    import optunahub

    module = optunahub.load_local_module(
        package="category/your_package_name",
        registry_root="/path/to/optunahub-registry/package",
    )


Load Your Package from Your Fork of The optunahub-registry Repository
---------------------------------------------------------------------

Second, you can use the `optunahub.load_module <https://optuna.github.io/optunahub/reference.html#optunahub.load_module>`__ function with ``repo_owner={YOUR_GITHUB_ID}`` and ``ref={YOUR_BRANCH_NAME}`` to load your package from your fork of the optunahub-registry repository and check if it works correctly.

.. code-block:: python

    import optunahub

    module = optunahub.load_module(
        package="category/your_package_name",
        repo_owner="your_github_id",
        ref="your_branch_name",
    )

"""
