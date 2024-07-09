import os
import tempfile

import pytest

import optunahub
import optunahub.hub


@pytest.mark.parametrize(
    ("ref", "force_reload", "expected_ref", "expected_force_reload"),
    [
        (None, None, "main", False),
        ("main", False, "main", False),
        ("test", True, "test", True),
    ],
)
def test_load_settings_propagation(
    ref: str, force_reload: bool, expected_ref: str, expected_force_reload: bool
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "__init__.py"), "w") as f:
            f.write(f"""from .implementation import *
import optunahub
assert(optunahub.hub._get_from_outer_globals('OPTUNAHUB_REF', 'main') == '{expected_ref}')
assert(optunahub.hub._get_from_outer_globals('OPTUNAHUB_FORCE_RELOAD', False) == {expected_force_reload})""")
        with open(os.path.join(tmpdir, "implementation.py"), "w") as f:
            f.write(f"""import optunahub
assert(optunahub.hub._get_from_outer_globals('OPTUNAHUB_REF', 'main')== '{expected_ref}')
assert(optunahub.hub._get_from_outer_globals('OPTUNAHUB_FORCE_RELOAD', False) == {expected_force_reload})""")
        _ = optunahub.load_local_module(
            os.path.basename(tmpdir),
            registry_root=os.path.dirname(tmpdir),
            ref=ref,
            force_reload=force_reload,
        )
