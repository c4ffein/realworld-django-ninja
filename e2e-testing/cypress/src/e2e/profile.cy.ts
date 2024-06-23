import { registerUser } from '../support/user.util';
import { createArticle } from '../support/article.util';

describe('@GET profile', () => {
  it('OK @200', () => {
    // Given
    registerUser().then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user).as('user');
    });

    // When
    cy.then(function () {
      cy.getRequest(`/api/profiles/${this.user.username}`).then(
        (response: Cypress.Response<Profile>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.profile.username).to.equal(this.user.username);
          expect(response.body.profile.bio).to.equal(null);
          expect(response.body.profile.image).to.equal(
            'https://api.realworld.io/images/smiley-cyrus.jpeg',
          );
          expect(response.body.profile.following).to.equal(false);
        },
      );
    });
  });

  it('KO @404', () => {
    // Given
    const unknownUsername = `${new Date().getTime() * 3}`;

    // When
    cy.getRequest(`/api/profiles/${unknownUsername}`).then((response: Cypress.Response<never>) => {
      // Then
      expect(response.status).to.equal(404);
    });
  });
});

describe('@POST follow user', () => {
  it('OK @200', () => {
    // Given
    registerUser().then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user).as('user');
    });

    const article = {
      title: `${Cypress.env('prefix')}${Date.now()}`,
      description: `${Cypress.env('prefix')}${Date.now()}`,
      body: `${Cypress.env('prefix')}${Date.now()}`,
      tagList: [`${Cypress.env('prefix')}${Date.now()}`],
    };

    cy.then(function () {
      createArticle(article, this.user.token);
    });

    registerUser({
      username: `${Cypress.env('prefix')}${Date.now()}-2`,
      email: `${Cypress.env('prefix')}${Date.now()}-2`,
      password: `${Cypress.env('prefix')}${Date.now()}-2`,
    }).then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user.token).as('followerToken');
    });

    // When
    cy.then(function () {
      cy.postRequest(`/api/profiles/${this.user.username}/follow`, {}, this.followerToken).then(
        (response: Cypress.Response<Profile>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.profile.following).to.equal(true);
          expect(response.body.profile.username).to.equal(this.user.username);
        },
      );
    });

    cy.then(function () {
      cy.getRequest(`/api/articles/feed`, this.followerToken).then(
        (response: Cypress.Response<any>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.articlesCount).to.equal(1);
          expect(response.body.articles.length).to.equal(1);
          expect(response.body.articles[0].title).to.equal(article.title);
          expect(response.body.articles[0].description).to.equal(article.description);
          expect(response.body.articles[0].body).to.equal(article.body);
          expect(response.body.articles[0].tagList).to.deep.equal(article.tagList);
          expect(response.body.articles[0].author.username).to.equal(this.user.username);
        },
      );
    });
  });

  it('KO @401', () => {
    // Given
    registerUser().then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user).as('user');
    });

    // When
    cy.then(function () {
      cy.postRequest(`/api/profiles/${this.user.username}/follow`, {}, undefined).then(
        (response: Cypress.Response<any>) => {
          // Then
          expect(response.status).to.equal(401);
          expect(response.body.message).to.equal('missing authorization credentials');
        },
      );
    });
  });
});

describe('@DELETE unfollow user', () => {
  it('OK @200', () => {
    // Given
    registerUser().then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user).as('user');
    });

    registerUser({
      username: `${Cypress.env('prefix')}${Date.now()}-2`,
      email: `${Cypress.env('prefix')}${Date.now()}-2`,
      password: `${Cypress.env('prefix')}${Date.now()}-2`,
    }).then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user.token).as('followerToken');
    });

    cy.then(function () {
      cy.postRequest(`/api/profiles/${this.user.username}/follow`, {}, this.followerToken);
    });

    // When
    cy.then(function () {
      cy.deleteRequest(`/api/profiles/${this.user.username}/follow`, this.followerToken).then(
        (response: Cypress.Response<Profile>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.profile.following).to.equal(false);
          expect(response.body.profile.username).to.equal(this.user.username);
        },
      );

      cy.getRequest(`/api/profiles/${this.user.username}`, this.followerToken).then(
        (response: Cypress.Response<Profile>) => {
          // Then
          expect(response.status).to.equal(200);
          expect(response.body.profile.following).to.equal(false);
        },
      );
    });
  });

  it('KO @401', () => {
    // Given
    registerUser().then((response: Cypress.Response<User>) => {
      cy.wrap(response.body.user).as('user');
    });

    // When
    cy.then(function () {
      cy.deleteRequest(`/api/profiles/${this.user.username}/follow`, undefined).then(
        (response: Cypress.Response<any>) => {
          // Then
          expect(response.status).to.equal(401);
          expect(response.body.message).to.equal('missing authorization credentials');
        },
      );
    });
  });
});
