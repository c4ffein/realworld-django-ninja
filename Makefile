########################
# Variables

DEFAULT_API_URL := "http://localhost:8000"


########################
# Django Project

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


########################
# Submodules

submodule:
	git submodule init; git submodule update


########################
# Frontend

front-setup-react:
	cd react-redux-realworld-example-app/; npm i

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
