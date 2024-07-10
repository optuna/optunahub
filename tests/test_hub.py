import os
import sys

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
    ref: str,
    force_reload: bool,
    expected_ref: str,
    expected_force_reload: bool,
    capsys: pytest.CaptureFixture,
) -> None:
    m = optunahub.load_local_module(
        "package_for_test_hub",
        registry_root=os.path.dirname(__file__),
        ref=ref,
        force_reload=force_reload,
    )
    assert m.ref == expected_ref
    assert m.force_reload == expected_force_reload
    assert m.implementation.ref == expected_ref
    assert m.implementation.force_reload == expected_force_reload

    del sys.modules["package_for_test_hub"]
    del sys.modules["package_for_test_hub.implementation"]
