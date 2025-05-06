import os
from pathlib import Path

import pytest

from tooling.build_posts import build_posts
from tooling.tests.test_build_posts import BUILD_POSTS_DIRECTORY_PATH


def compare_directories(*, expected_directory: Path, built_directory: Path) -> None:
    common_path = os.path.commonpath([expected_directory, built_directory])

    relative_expected_directory = BUILD_POSTS_DIRECTORY_PATH / expected_directory.relative_to(common_path)
    expected_file_paths = tuple(sorted(relative_expected_directory.iterdir()))
    expected_file_path_names = frozenset(expected_file_path.name for expected_file_path in expected_file_paths)

    relative_built_directory = BUILD_POSTS_DIRECTORY_PATH / built_directory.relative_to(common_path)
    built_file_paths = tuple(sorted(relative_built_directory.iterdir()))
    built_file_path_names = frozenset(built_file_path.name for built_file_path in built_file_paths)

    # Ensure all files in the expected directory are in the built directory,
    # as well as there are no extra files in the built directory.
    assert expected_file_path_names == built_file_path_names

    for expected_file_path, built_file_path in zip(expected_file_paths, built_file_paths):
        if expected_file_path.is_dir():
            # Check all nested directories, the same way we check the current one.
            compare_directories(
                expected_directory=expected_file_path,
                built_directory=built_file_path
            )

        else:
            with (
                open(expected_file_path, 'r') as expected_file,
                open(built_file_path, 'r') as built_file
            ):
                expected_file_contents = expected_file.read()
                built_file_contents = built_file.read()

                assert expected_file_contents == built_file_contents


def delete_built_directory_contents(*, directory_path: Path) -> None:
    for built_directory_path_child in directory_path.iterdir():
        _delete_built_directory(directory_path=built_directory_path_child)


def _delete_built_directory(*, directory_path: Path) -> None:
    if directory_path.is_dir():
        for built_directory_path_child in directory_path.iterdir():
            _delete_built_directory(directory_path=built_directory_path_child)
        directory_path.rmdir()

    else:
        directory_path.unlink()


@pytest.fixture
def posts_directory() -> Path:
    return BUILD_POSTS_DIRECTORY_PATH / 'posts'


@pytest.fixture
def built_posts_directory() -> Path:
    built_posts_directory_path = BUILD_POSTS_DIRECTORY_PATH / 'built_posts'

    if not built_posts_directory_path.exists():
        built_posts_directory_path.mkdir()

    # Clean-up done on creation, directly before the test just in case previous run crashed and left some files.
    delete_built_directory_contents(directory_path=built_posts_directory_path)

    return built_posts_directory_path


@pytest.fixture
def expected_built_directory() -> Path:
    return BUILD_POSTS_DIRECTORY_PATH / 'expected_built_posts'


def test_compiles_all_post_samples_successfully_to_match_expected_built_posts(
    posts_directory: Path,
    built_posts_directory: Path,
    expected_built_directory: Path
) -> None:
    build_posts(posts_directory=posts_directory, built_posts_directory=built_posts_directory)

    expected_built_directory.exists()
    compare_directories(
        expected_directory=expected_built_directory,
        built_directory=built_posts_directory
    )
