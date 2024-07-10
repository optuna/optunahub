import optunahub


ref = optunahub.hub._get_from_outer_globals("OPTUNAHUB_REF", "main")
force_reload = optunahub.hub._get_from_outer_globals("OPTUNAHUB_FORCE_RELOAD", False)
