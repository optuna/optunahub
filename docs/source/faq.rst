FAQ
===

.. contents::
    :local:

How to opt-out of the anonymous analytics?
------------------------------------------

OptunaHub collects anonymous usage data to improve the service.
The data is used to understand how users interact with the service and to identify areas for improvement.

Youn can opt-out of the anonymous analytics by setting the environment variable `OPTUNAHUB_NO_ANALYTICS` to `1`

.. code-block:: shell

      export OPTUNAHUB_NO_ANALYTICS=1


How to configure the package cache?
-----------------------------------

OptunaHub caches the downloaded packages in the following locations.

- The directory defined by `OPTUNAHUB_CACHE_HOME` environment variable
- (UNIX-like) `XDG_CACHE_HOME/optunahub`
- (Windows) `%LOCALAPPDATA%/optunahub`

The settings are prioritized in the order listed above.
`XDG_CACHE_HOME` is usually `~/.cache` on UNIX-like systems.


How can I update an OptunaHub package already cached?
-----------------------------------------------------

Calling `optunahub.load_module()` with `force_reload=True` ensures the selected package is re-download from the package registry.
