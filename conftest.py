from typing import List

from _pytest.config import Config
from _pytest.config import Perser
from _pytest.nodes import Item
import pytest


def pytest_addoption(parser: Perser) -> None:
    parser.addoption(
        "--github-api",
        action="store_true",
        default=False,
        help="Run tests that require GitHub API access. Default is False.",
    )


def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    use_github_api = config.getoption("--github-api")

    for item in items:
        if "use_github_api" in item.keywords:
            if not use_github_api:
                item.add_marker(
                    pytest.mark.skip(reason="You need to specify --github-api to run this test.")
                )
