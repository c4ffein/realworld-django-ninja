########################
# Variables

DEFAULT_API_URL := "http://localhost:8000"

########################
# Django Project

run-debug:
	DEBUG=True ./manage.py runserver 0.0.0.0:8000

run:
	./manage.py runserver 0.0.0.0:8000

test-django:
	DEBUG=True ./manage.py test apps

test-postman:
	cd e2e-testing/postman/; APIURL=http://localhost:8000/api ./run-api-tests.sh

test-cypress-api:
	cd e2e-testing/cypress/; npm test -- --spec src/api

lint:
	ruff check --fix; ruff format

lint-check:
	ruff check --no-fix && ruff format --check

type-check:
	ty check

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

########################
# Dummy

dummy-test:
	cd e2e-testing/postman/; APIURL=http://localhost:8000 ./run-api-tests.sh
