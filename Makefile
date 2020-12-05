setup.py: pyproject.toml
	@dephell deps convert

install-editable: setup.py
	@pip install -e .

build:
	@poetry build

install:
	@poetry install