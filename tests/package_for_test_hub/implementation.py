import optunahub


repo_owner = optunahub.hub._get_global_variable_from_outer_scopes("OPTUNAHUB_REPO_OWNER", "optuna")
ref = optunahub.hub._get_global_variable_from_outer_scopes("OPTUNAHUB_REF", "main")
force_reload = optunahub.hub._get_global_variable_from_outer_scopes(
    "OPTUNAHUB_FORCE_RELOAD", False
)
