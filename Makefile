install:
	poetry install

install-dev:
	poetry install --with "dev"

clean:
	rm -rf dist
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	make lint

build:
	python -m build

compile:
	make build

publish-test:
	make clean
	make build
	python -m twine upload --repository testpypi dist/* --verbose -p ${TEST_PYPI_TOKEN}

publish-prod:
	make clean
	make build
	python -m twine upload dist/* --verbose -p ${PYPI_TOKEN}

test:
	poetry run pytest tests/ -v

coverage:
	poetry run pytest tests/ --cov=anyparser_langchain --cov-report=html

lint:
	black ./

all: clean build 