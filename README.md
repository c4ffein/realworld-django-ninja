# ![RealWorld Example App](logo.png)

> ### Django Ninja + Postgres codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)

This codebase was created to demonstrate a fully fledged fullstack application built with [Django Ninja](https://django-ninja.dev) including CRUD operations, authentication, routing, pagination, and more.

It is using the [realWorld-DjangoRestFramework](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) repository from [Sean-Miningah](https://github.com/Sean-Miningah/) as a base, as porting an app from [Django REST framework](https://www.django-rest-framework.org) to [Django Ninja](https://django-ninja.dev) is an interesting process, and helps you realize that you may do it on your own codebase without having to change anything related to your Django models.

So credit is due to [Sean-Miningah](https://github.com/Sean-Miningah/) for any initial code.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.

#### About [RealWorld](https://codebase.show/projects/realworld)
The [RealWorld Demo App](https://codebase.show/projects/realworld?category=backend&language=python) includes many implementations of the same project ([a Medium clone](https://demo.realworld.io/#/)), for which all [frontends](https://codebase.show/projects/realworld?category=frontend) and [backends](https://codebase.show/projects/realworld?category=backend) are supposed to be switchable from one another [as they all follow the same API](https://github.com/gothinkster/realworld/tree/main/api).

It is supposed to [`reflect something similar to an early-stage startup's MVP`](https://realworld-docs.netlify.app/docs/implementation-creation/expectations), contrarily to some demo apps that are either too little or too much complex, and provide a good way to assert differences between frameworks.

This repository has been accepted as the reference implementation for [Django Ninja](https://django-ninja.dev), see [the Python category for the RealWorld Demo App](https://codebase.show/projects/realworld?category=backend&language=python).

#### About [Django Ninja](https://django-ninja.dev/)
[Django Ninja](https://django-ninja.dev/) is an overlay to [Django](https://www.djangoproject.com) which lets you create APIs while being heavily inspired by [FastAPI](https://fastapi.tiangolo.com). It means it tries to stay as simple as possible for the API creation, while letting you benefit from the whole [Django](https://www.djangoproject.com) ecosystem, including [its ORM](https://docs.djangoproject.com/en/5.0/topics/db/), [its auth system](https://docs.djangoproject.com/en/5.0/topics/auth/), even [its HTML templates](https://docs.djangoproject.com/en/5.0/topics/templates/) if you still need those...

[Django Ninja](https://django-ninja.dev/) is a very good alternative to [Django REST framework](https://www.django-rest-framework.org), as it tries to be less unnecessarily complex and more performant.

As [Django Ninja](https://django-ninja.dev/) (and by extension this repository) only covers the API part, you may then [connect a frontend to it](#connect-a-frontend) after [deploying](#deploying).


## Usage

1. Clone the Git repository:

```shell
  git clone https://github.com/c4ffein/realworld-django-ninja.git

```
2. Create `uv` Virtual Environment
```shell
  cd project_directory
  pip install uv  # Install the `extremely fast Python package installer and resolver`
  uv venv venv  # Create a venv
  . venv/bin/activate  # Activate it
  uv pip install .[dev]  # Install all dependencies for dev
```

make sure you a postgres database configured for connection

3. Run Application
> make run-debug

### Using Docker and Docker Compose

Run:
> docker compose up

### Testing
- Django Ninja tests: `make test-django`
- E2E Cypress tests: `make test-cypress` (needs the application running)

### Deploying
A [Django Ninja](https://django-ninja.dev/) project can be deployed just as any [https://www.djangoproject.com/](Django) project.
[The documentation is near perfect.](https://docs.djangoproject.com/en/5.0/howto/deployment/)

### Connect a frontend
Choose a frontend from [codebase.show](https://codebase.show/projects/realworld) and configure it as required.

## API Documentation
An auto-generated API documentation using [Swagger](https://swagger.io/) is available at the `/docs` route.


## Divergence with the existing, and porting process
### Divergence with [realWorld-DjangoRestFramework](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework)
- Contrarily to the [RealWorld API spec](https://github.com/gothinkster/realworld/blob/main/api/openapi.yml), [realWorld-DjangoRestFramework](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) returns [HTTP 404](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/404) for nearly anything that goes wrong. This was replaced by [the default Django Ninja handlers and some custom behavior](https://django-ninja.dev/guides/errors/).

### Divergence with the [RealWorld API spec](https://github.com/gothinkster/realworld/blob/main/api/openapi.yml)
- While the [RealWorld API spec](https://github.com/gothinkster/realworld/blob/main/api/openapi.yml) uses the [HTTP 422](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/422) for most errors, we are not just using an array but the output from [the default ValidationError handler](https://django-ninja.dev/guides/errors/#ninjaerrorsvalidationerror).
- This project handles some HTTP error codes differently:
  - Makes a difference between [401](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/401) and [403](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/403).
  - Uses [409](https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409) sometimes.
- Some additional checks for data consistency (example: now verifies that email addresses are indeed email addresses and not just random strings, that change made some e2e tests failed).

### Commits that are a good illustration of the migration from [Django REST framework](https://www.django-rest-framework.org) to [Django Ninja](https://django-ninja.dev)
Before the heaviest modifications, some small commits have been made with the intention to well present the migration process.  
*Please note that many tests were added after and not before the migration, as, even if in a real world scenario you would try to add as-much tests before (to ensure that you don't break anything), the goal here was mainly to provide a [Django Ninja](https://django-ninja.dev) of the [RealWorld demo app](https://github.com/gothinkster/realworld). See [`Divergence with the existing`](#divergence-with-the-existing).*
- [`df3f024a`](https://github.com/c4ffein/realworld-django-ninja/commit/df3f024a0fcbb5694de7d29d9a3cc3d50cde111c): Good example of migrating just one route.
  - Focused on the quick fix of the `/api/articles/tag` route in `articles/api.py`, and the modification of `articles/urls.py` that lets that route be handled by the [Django Ninja router](https://django-ninja.dev/guides/routers/).
  - UT is adapted, the existing [Django REST framework](https://www.django-rest-framework.org) `ViewSet` deleted.
- [`e5efe9c3`](https://github.com/c4ffein/realworld-django-ninja/commit/e5efe9c309b9fd46e5978ed09ce4e5fd119844e4): Migrating the `comments` app, (tests pass but the route is broken as the [router](https://django-ninja.dev/guides/routers/) is only registered in [`069cb7a7`](https://github.com/c4ffein/realworld-django-ninja/commit/069cb7a7c607457b8275ff9db2bf542c1b85b9de)).
- [`45e472e0`](https://github.com/c4ffein/realworld-django-ninja/commit/45e472e0bd8fc72b4458dc55901dc37c0ff205fa): Most modifications of the `accounts` app.
- [`069cb7a7`](https://github.com/c4ffein/realworld-django-ninja/commit/069cb7a7c607457b8275ff9db2bf542c1b85b9de): Preparing the migration of `articles`.
- [`e7285493`](https://github.com/c4ffein/realworld-django-ninja/commit/e7285493d28abeff453c03003a6e8075cd106e21): Biggest chunk of modification towards the migration of the `articles` app.


## Contributing
If you would like to contribute to the project, please follow these guidelines:
- Fork the repository and create a new branch for your feature or bug fix.
- Make the necessary changes and commit them.
  - `ruff format` and `ruff check` as I still haven't set-up a CI...
- Push your changes to your forked repository.
- Submit a pull request to the main repository, explaining the changes you made and any additional information that might be helpful for review.

### Should I create an issue?
Seriously, yes, for anything that crosses your mind. This is early-stage, I'll consider any opinion.


## Improvements / still TODO
*I'm not creating specific issues for those as I just hope to finish all that soon enough (I wish), but you may do it if you want:*
- Real checks with frontend apps, probably picking one of those for a demo
- Maybe include a frontend as a git submodule to run fully e2e tests
- Better debug env variable and settings in general
- Also port Playwright
- Also port [Postman](https://github.com/gothinkster/realworld/tree/main/api)
- Even better tests
- Help about CORS?
- CI with ruff + tests
- parameters for most routes, check API


## License
- The [original code](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) is a [Django REST framework](https://www.django-rest-framework.org/) project made by [Sean-Miningah](https://github.com/Sean-Miningah/) and released under the [MIT License](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework/blob/master/LICENSE).
- This project is now also released for the most part under the [MIT License](https://github.com/c4ffein/realworld-django-ninja/blob/master/LICENSE) by [c4ffein](https://github.com/c4ffein/).
- `image_server` includes code from a public domain image, and a [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.en) image by [Toytoy](https://en.wikipedia.org/wiki/User:Toytoy).
