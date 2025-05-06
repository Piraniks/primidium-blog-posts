create_venv:
	python3.12 -m venv .venv


install_tooling_dependencies:
	. .venv/bin/activate
	python -m pip install -r tooling/requirements.txt
	deactivate

# TODO:
# install_posts_dependencies:


init: create_venv install_tooling_dependencies


clean:
	rm -rf .venv


build_posts:
	python tooling/cli.py build-posts ./.local/built_posts


build_requirements:
	python tooling/build_requirements.py


test_posts:
	pytest posts


test_tooling:
	pytest tooling -vv
