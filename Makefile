########################
# Variables

DEFAULT_API_URL := "http://localhost:8000"

########################
# Django Project

help:
	@echo "Available commands:"
	@echo "  lint-check"
	@echo "  run-debug"
	@echo "  run"
	@echo "  test-django"
	@echo "  test-postman"
	@echo "  test-cypress-api"
	@echo "  lint"
	@echo "  lint-check"
	@echo "  type-check"
	@echo "  verify"
	@echo "  submodule"
	@echo "  setup-cypress"
	@echo "  front-setup-react"
	@echo "  front-run-react"
	@echo "  front-clean-react"
	@echo "  front-setup-vue"
	@echo "  front-run-vue"
	@echo "  front-clean-vue"

########################
# Django Project

run-debug:
	DEBUG=True python3 -m uv run python manage.py runserver 0.0.0.0:8000

migrate:
	python3 -m uv run python manage.py migrate

run:
	python3 -m uv run python manage.py runserver 0.0.0.0:8000

test-django:
	DEBUG=True python3 -m uv run python manage.py test apps

test-postman:
	cd e2e-testing/postman/; APIURL=http://localhost:8000/api ./run-api-tests.sh

test-cypress-api:
	cd e2e-testing/cypress/; npm test -- --spec src/api

lint:
	python3 -m uv run ruff check --fix; python3 -m uv run ruff format

lint-check:
	python3 -m uv run ruff check --no-fix && python3 -m uv run ruff format --check

type-check:
	python3 -m uv run ty check

verify:
	make lint-check && make type-check && make test-django

########################
# Setup

submodule:
	git submodule init; git submodule update

setup-cypress:
	cd e2e-testing/cypress/; npm i

########################
# Frontend

front-setup-react:
	cd fronts/react-redux-realworld-example-app/; npm i

front-run-react:
	cd fronts/react-redux-realworld-example-app/;\
	REACT_APP_BACKEND_URL="$${API_URL:=$(DEFAULT_API_URL)}"/api npm start

front-clean-react:
	cd fronts/react-redux-realworld-example-app/; rm -r node_modules package-lock.json

front-setup-vue:
	cd fronts/vue3-realworld-example-app/; npm i

front-run-vue:
	cd fronts/vue3-realworld-example-app/;\
	VITE_API_HOST="$${API_URL:=$(DEFAULT_API_URL)}" npm run dev -- --host

front-clean-vue:
	cd fronts/vue3-realworld-example-app/; rm -r node_modules package-lock.json
