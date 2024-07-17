# ![RealWorld Example App](logo.png)

> ### Django Ninja + Postgres codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)

This codebase was created to demonstrate a fully fledged fullstack application built with Django Ninja including CRUD operations, authentication, routing, pagination, and more.

It is using the [realWorld-DjangoRestFramework](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) repository from [Sean-Miningah](https://github.com/Sean-Miningah/) as a base, as porting an app from [Django REST framework](https://www.django-rest-framework.org) to [Django Ninja](https://django-ninja.dev) is an interesting process, and helps you realize that you may do it on your own codebase without having to change anything related to your Django models.

So credit is due to [Sean-Miningah](https://github.com/Sean-Miningah/) for any initial code.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


# Usage

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

## Using Docker and Docker Compose 

Run:
> docker compose up

## Testing
- Django Ninja tests: `./manage.py test`
- E2E Cypress tests: in `e2e-testing/cypress`, `npm test`

## Deploying
A [Django Ninja](https://django-ninja.dev/) project can be deployed just as any [https://www.djangoproject.com/](Django) project.
[The documentation is near perfect.](https://docs.djangoproject.com/en/5.0/howto/deployment/)

# API Documentation 
An auto-generated API documentation using [Swagger](https://swagger.io/) is available at the `/docs` route.


# Contributing
If you would like to contribute to the project, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.

2. Make the necessary changes and commit them.

3. Push your changes to your forked repository.

4. Submit a pull request to the main repository, explaining the changes you made and any additional information that might be helpful for review.

# Improvements / still TODO
*Not creating specific issues for those, but still currently considered:*
- Even better tests
- Update Django-Ninja / Django
- Better explain what has been done
  - Explain why https://github.com/gothinkster/realworld/blob/main/api/openapi.yml error management hasn't been followed
    - including 404 for everything
    - including error messages
  - not really adding test before migration, should add some after but not doing it
- Real checks with frontend apps, probably picking one of those for a demo
- Better debug env variable and settings in general
- Also port Playwright
- Explain a bit commit history, which ones are good to see a simple migration, before some of the whole lint + full modifications
- Explain better what is realworld and how to run the full project, maybe including a frontend as a git submodule to run fully e2e tests
- Help about CORS?

# License
- The [original code](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework) is a [Django REST framework](https://www.django-rest-framework.org/) project made by [Sean-Miningah](https://github.com/Sean-Miningah/) and released under the [MIT License](https://github.com/Sean-Miningah/realWorld-DjangoRestFramework/blob/master/LICENSE).
- This project is now also released for the most part under the [MIT License](https://github.com/c4ffein/realworld-django-ninja/blob/master/LICENSE) by [c4ffein](https://github.com/c4ffein/).
- `image_server` includes code from a public domain image, and a [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.en) image by [Toytoy](https://en.wikipedia.org/wiki/User:Toytoy).
