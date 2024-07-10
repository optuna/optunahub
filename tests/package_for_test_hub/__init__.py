import optunahub
from package_for_test_hub import implementation


ref = optunahub.hub._get_from_outer_globals("OPTUNAHUB_REF", "main")
force_reload = optunahub.hub._get_from_outer_globals("OPTUNAHUB_FORCE_RELOAD", False)


__all__ = ["implementation", "ref", "force_reload"]
