create_venv:
	python -m venv .venv

install_tooling_dependencies:
	python -m pip install -r tooling/requirements.txt

install_posts_dependencies:
	find . -type f -name requirements.txt -not -path "./tooling/*" -exec pip install -r {} \;

init: create_venv install_tooling_dependencies install_posts_dependencies

clean:
	rm -rf .venv

build_posts:
	python tooling/cli.py build-posts ./.local/built_posts

build_requirements:
	python tooling/build_requirements.py

test_posts:
	pytest posts -vv

test_tooling:
	pytest tooling -vv

fix:
	git diff --name-only | grep "*.py" | xargs ruff check --fix
	git diff --name-only | grep "*.py" | xargs ruff format

fix_all:
	ruff check --fix .
	xargs ruff format .

type:
	ty check .
