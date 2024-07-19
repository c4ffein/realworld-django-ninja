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
2. Create Virtual Environment
```shell
  cd project_directory
  python3 -m venv venv 
  pip3 install -r requirements.txt
```

make sure you a postgres database configured for connection

3. Run Application
> python manage.py runserver 

### Using Docker and Docker Compose

Run:
> docker compose up

### Testing
- Django Ninja tests: `./manage.py test`
- E2E Cypress tests: in `e2e-testing/cypress`, `npm test`

### Deploying
A [Django Ninja](https://django-ninja.dev/) project can be deployed just as any [https://www.djangoproject.com/](Django) project.
[The documentation is near perfect.](https://docs.djangoproject.com/en/5.0/howto/deployment/)

### Connect a frontend
Choose a frontend from [codebase.show](https://codebase.show/projects/realworld) and configure it as required.

## API Documentation
An auto-generated API documentation using [Swagger](https://swagger.io/) is available at the `/docs` route.


## Contributing
If you would like to contribute to the project, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.

2. Make the necessary changes and commit them.
  b. `ruff format` and `ruff check` as I still haven't set-up a CI...

3. Push your changes to your forked repository.

4. Submit a pull request to the main repository, explaining the changes you made and any additional information that might be helpful for review.

### Should I create an issue?
Seriously, yes, for anything that crosses your mind. This is early-stage, I'll consider any opinion.

## Improvements / still TODO
*Not creating specific issues for those, but still currently considered:*
- Even better tests
- Update Django-Ninja / Django
- Better explain what has been done
  - Explain why https://github.com/gothinkster/realworld/blob/main/api/openapi.yml error management hasn't been followed
    - including 404 for everything
    - including error messages
  - Explain why many tests have been added after and not before the migration
- Real checks with frontend apps, probably picking one of those for a demo
- Better debug env variable and settings in general
- Also port Playwright
- Also port [Postman](https://github.com/gothinkster/realworld/tree/main/api)
- Explain a bit commit history, which ones are good to see a simple migration, before some of the whole lint + full modifications
- Maybe include a frontend as a git submodule to run fully e2e tests
- Help about CORS?
- CI with ruff + tests

## License
- The [original code](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) is a [Django REST framework](https://www.django-rest-framework.org/) project made by [Sean-Miningah](https://github.com/Sean-Miningah/) and released under the [MIT License](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework/blob/master/LICENSE).
- This project is now also released for the most part under the [MIT License](https://github.com/c4ffein/realworld-django-ninja/blob/master/LICENSE) by [c4ffein](https://github.com/c4ffein/).
- `image_server` includes code from a public domain image, and a [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.en) image by [Toytoy](https://en.wikipedia.org/wiki/User:Toytoy).
