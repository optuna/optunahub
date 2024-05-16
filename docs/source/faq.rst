FAQ
===

.. contents::
    :local:

How to opt-out of the anonymous analytics?
------------------------------------------

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


How to configure the package cache?
-----------------------------------

OptunaHub caches the downloaded packages in the following locations.

- The directory defined by `OPTUNAHUB_CACHE_HOME` environment variable
- The `cache_home` value in `config.toml`
- (UNIX-like) `XDG_CACHE_HOME/optunahub`
- (Windows) `%LOCALAPPDATA%/optunahub`

The settings are prioritized in the order listed above.
`XDG_CACHE_HOME` is usually `~/.cache` on UNIX-like systems.


How can I update an OptunaHub package already cached?
-----------------------------------------------------

Calling `optunahub.load_module()` with `force_reload=True` ensures the selected package is re-download from the package registry.
