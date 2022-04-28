# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

from pathlib import Path

import pytest

from pylint.constants import PYLINT_HOME
from pylint.lint.caching import _get_pdata_path, load_results, save_results
from pylint.utils import LinterStats
from pylint.utils.linterstats import BadNames

PYLINT_HOME_PATH = Path(PYLINT_HOME)


@pytest.mark.parametrize(
    "path,recur,expected",
    [
        ["", 1, PYLINT_HOME_PATH / "1.stats"],
        ["", 2, PYLINT_HOME_PATH / "2.stats"],
        ["a/path/", 42, PYLINT_HOME_PATH / "a_path_42.stats"],
    ],
)
def test__get_pdata_path(path: str, recur: int, expected: Path) -> None:
    assert _get_pdata_path(Path(path), recur) == expected


# Pytest fixtures works like this by design
# pylint: disable=redefined-outer-name


@pytest.fixture
def linter_stats() -> LinterStats:
    return LinterStats(
        bad_names=BadNames(
            argument=1,
            attr=2,
            klass=3,
            class_attribute=4,
            class_const=5,
            const=6,
            inlinevar=7,
            function=8,
            method=9,
            module=10,
            variable=11,
            typevar=12,
        )
    )


@pytest.mark.parametrize("path", ["", "a/path/"])
def test_save_and_load_result(path: str, linter_stats: LinterStats) -> None:
    save_results(linter_stats, path)
    loaded = load_results(path)
    assert loaded is not None
    assert loaded.bad_names == linter_stats.bad_names


@pytest.mark.parametrize("path", ["", "a/path/"])
def test_save_and_load_not_a_linter_stats(path: str) -> None:
    # TODO: 3.0: Remove tests # pylint: disable=fixme
    # type ignore because this is what we're testing
    with pytest.warns(DeprecationWarning):
        save_results(1, path)  # type: ignore[arg-type]
        loaded = load_results(path)
        assert loaded is None


def test_load_save_results_deprecation(linter_stats) -> None:
    """TODO: 3.0: Remove tests and deprecated import # pylint: disable=fixme"""
    # pylint: disable=redefined-outer-name, import-outside-toplevel, reimported
    with pytest.warns(DeprecationWarning):
        from pylint.config import save_results

        save_results(linter_stats, "")
    with pytest.warns(DeprecationWarning):
        from pylint.config import load_results

        load_results("", "")
