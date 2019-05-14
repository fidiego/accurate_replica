.DEFAULT_GOAL := help
OPEN=$(word 1, $(wildcard /usr/bin/xdg-open /usr/bin/open))

.PHONY: help
help: ## Print the help message
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST) | \
		sort | \
		column -s ':' -t

.PHONY: install
install: ## install python dependencies
	@pipenv install

.PHONY: devinstall
devinstall: ## install python dependencies with dev deps
	@pipenv install --dev

.PHONY: run
run:  # run in development mode: requires dev dependencies
	@pipenv run honcho start -f Procfile.dev

.PHONY: shell
shell:  # shell
	@pipenv run python manage.py shell

.PHONY: dbshell
dbshell:  # dbshell
	@pipenv run python manage.py dbshell

.PHONY: erd
erd:  # generate an ERD: requires dev dependendencies
	@pipenv run python manage.py graph_models -o schema.png

.PHONY: migrations
migrations:  # generate migrations
	@pipenv run python manage.py makemigrations

.PHONY: migrate
migrate:  # apply migrations
	@pipenv run python manage.py migrate

.PHONY: static
static:  # collect staticfiles
	@pipenv run python manage.py collectstatic --no-input

.PHONY: test
test: ## run the test suite
	@export PYTHONDONTWRITEBYTECODE=1 && pipenv run python -m pytest -p no:cacheprovider -v --color=yes --cov=apps/

.PHONY: test-no-coverage
test-no-coverage: ## run the test suite without generating a coverage report
	@export PYTHONDONTWRITEBYTECODE=1 && pipenv run python -m pytest -v --color=yes

.PHONY: lint
lint: ## lint the codebase
	@export PYTHONDONTWRITEBYTECODE=1 && pipenv run flake8 . --statistics --count

.PHONY: bandit
bandit: ## analyize for security vulnerabilities with bandit
	@export PYTHONDONTWRITEBYTECODE=1 && pipenv run bandit -x frontend/,tests/ -r .

.PHONY: coverage
coverage: ## generate coverage report
	@coverage report -m

.PHONY: coverage-html
coverage-html: ## generate html coverage report
	@coverage report -m && coverage html

.PHONY: redis
redis:  # connect to redis instances defined in env
	@redis-cli -u $(REDIS_URL)

.PHONY: ngrok
ngrok:  # run ngrok
	@ngrok http 9901 -subdomain=ac-dev

.PHONY: rmbytecode
rmbytecode:  # remove all bytecode
	@find . -name "*.pyc" -exec rm -f {} \; && rm -r .pytest_cache
