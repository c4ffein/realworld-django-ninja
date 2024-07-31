run-debug:
	DEBUG=True ./manage.py runserver 0.0.0.0:8000

test-django:
	DEBUG=True ./manage.py test

test-cypress-api:
	cd e2e-testing/cypress/; npm test -- --spec src/api

lint:
	ruff check --fix; ruff format

check-lint:
	ruff check --no-fix && ruff format --check
