from __future__ import annotations

from pathlib import Path
import sys

import pytest

import optunahub


@pytest.mark.parametrize("package", ["root_switch", "samplers/root_switch"])
@pytest.mark.parametrize("different_root", [False, True])
def test_load_local_module_registry_root(
    tmp_path: Path, package: str, different_root: bool
) -> None:
    roots = [tmp_path / "first", tmp_path / "second"]
    for value, root in enumerate(roots, start=1):
        package_dir = root / package
        package_dir.mkdir(parents=True)
        (package_dir / "__init__.py").write_text("from .values import VALUE\n", encoding="utf-8")
        (package_dir / "values.py").write_text(f"VALUE = {value}\n", encoding="utf-8")

    module_name = f"optunahub_registry.package.{package.replace('/', '.')}"
    try:
        first = optunahub.load_local_module(package, registry_root=str(roots[0]))
        assert first.VALUE == 1
        root = roots[1] if different_root else roots[0]
        second = optunahub.load_local_module(package, registry_root=str(root))
        assert second.__file__ is not None
        assert Path(second.__file__) == root / package / "__init__.py"
        assert second.VALUE == (2 if different_root else 1)
        assert first.VALUE == 1
    finally:
        for name in list(sys.modules):
            if name == module_name or name.startswith(module_name + "."):
                del sys.modules[name]
