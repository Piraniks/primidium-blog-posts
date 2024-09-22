create_venv:
	python3.12 -m venv .venv


install_tooling_dependencies:
	. .venv/bin/activate
	python -m pip install -r tooling/requirements.txt
	deactivate


init: create_venv install_tooling_dependencies


clean:
	rm -rf .venv


compile_posts:
	python tooling/compile_all_templates.py


test:
	pytest .