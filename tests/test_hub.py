import os

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
    _ = optunahub.load_local_module(
        "package_for_test_hub",
        registry_root=os.path.dirname(__file__),
        ref=ref,
        force_reload=force_reload,
    )
    out = capsys.readouterr()[0].split("\n")
    assert out[0] == expected_ref
    assert {"True": True, "False": False}[out[1]] == expected_force_reload
