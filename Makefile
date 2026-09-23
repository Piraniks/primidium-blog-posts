install_tooling_dependencies:
	uv sync --all-packages --all-groups

install_posts_dependencies:
	find . -type f -name requirements.txt -not -path "./tooling/*" -exec sh -c 'uv run python -m pip install -r "{}" || true' \;

install: install_tooling_dependencies install_posts_dependencies

clean:
	rm -rf .venv

init: clean install

build_posts:
	uv run python tooling/cli.py build-posts ./.local/built_posts

test_posts:
	uv run pytest posts -vv

test_tooling:
	uv run pytest tooling -vv

test: # test_posts test_tooling
	uv run pytest . -vv

fix:
	git diff --name-only | grep "*.py" | xargs ruff check --fix
	git diff --name-only | grep "*.py" | xargs ruff format

fix_all:
	uv run ruff check --fix .
	uv run ruff format .

check:
	git diff --name-only | grep "*.py" | xargs ruff check
	git diff --name-only | grep "*.py" | xargs ruff format --check

check_all:
	uv run ruff check .
	uv run ruff format --check .

type:
	uv run ty check .

all: type fix_all test
