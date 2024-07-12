import optunahub

from . import implementation


ref = optunahub.hub._get_global_variable_from_outer_scopes("OPTUNAHUB_REF", "main")
force_reload = optunahub.hub._get_global_variable_from_outer_scopes(
    "OPTUNAHUB_FORCE_RELOAD", False
)


__all__ = ["implementation", "ref", "force_reload"]
