import optunahub


print(optunahub.hub._get_from_outer_globals("OPTUNAHUB_REF", "main"))
print(optunahub.hub._get_from_outer_globals("OPTUNAHUB_FORCE_RELOAD", False))
