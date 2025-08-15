FAQ
===

.. contents::
    :local:

How to opt-out of the anonymous analytics?
------------------------------------------

`OptunaHub collects anonymous usage data <https://hub.optuna.org/static/anonymous_analytics/>`__ to improve the service.
The data is used to understand how users interact with the service and to identify areas for improvement.

Youn can opt-out of the anonymous analytics by setting the environment variable ``OPTUNAHUB_NO_ANALYTICS`` to ``1``.

.. code-block:: shell

      export OPTUNAHUB_NO_ANALYTICS=1


How to configure the package cache?
-----------------------------------

OptunaHub caches the downloaded packages in the following locations.

- The directory defined by ``OPTUNAHUB_CACHE_HOME`` environment variable
- (UNIX-like) ``XDG_CACHE_HOME/optunahub``
- (Windows) ``%LOCALAPPDATA%/optunahub``

The settings are prioritized in the order listed above.
``XDG_CACHE_HOME`` is usually ``~/.cache`` on UNIX-like systems.

If you have any trouble with the cache, you can remove the cache directory to reset the cache.


How can I update an OptunaHub package already cached?
-----------------------------------------------------

You can set the environment variable ``OPTUNAHUB_CACHE_EXPIRATION_SECONDS`` to define the cache expiration time in seconds.
The default value is 2,592,000 seconds (30 days).
When the cache expires, the package will be re-downloaded from the package registry.

If you want to force update the package every time you call it, you can use ``optunahub.load_module()`` with ``force_reload=True``.


I got the "403: rate limit exceeded" error when loading a package. How can I fix it?
------------------------------------------------------------------------------------

Based on `the GitHub API documentation <https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28>`__, the primary rate limit for unauthenticated requests is 60 requests per hour.

You can increase the rate limit by authenticating with GitHub using `a personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`__.
`optunahub.load_module <https://optuna.github.io/optunahub/reference.html#optunahub.load_module>`_ receives `an Auth object <https://pygithub.readthedocs.io/en/latest/examples/Authentication.html>`__ for authentication.

Another option is cloning the `optunahub-registry <https://github.com/optuna/optunahub-registry>`__ repository and loading the desired package from the local directory by using `optunahub.load_local_module <https://optuna.github.io/optunahub/reference.html#optunahub.load_local_module>`__.
